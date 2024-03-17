
import json
import os
from datetime import datetime
from typing import Optional

import pandas as pd
import requests
from sqlalchemy import text, inspect
from util import create_snow_engine, send_mail


def get_gameweek(engine):
    week = pd.read_sql('select max(weeknum) as weeknum from gameweek2', engine)
    print(week)
    week = week.iloc[0].values - 1

    return week


def get_manager_team(api_url, manager_id):
    """
    Fetch manager's team data from an API and return it.

    Parameters:
    - api_url (str): The URL of the API endpoint.
    - manager_id (int): The manager's unique identifier.

    Returns:
    - dict : The manager's team data as a dict.
    """

    try:
        response = requests.get(api_url, timeout=120)

        if response.status_code == 200:
            manager_team = response.json()
            manager_team["manager_id"] = manager_id
            return manager_team
        else:
            send_mail({'ojofemijoseph@outlook.com':'Joseph Ojo'},
                      f"Request failed for ID {manager_id}",
                      'Failed')
            return None
    except Exception as e:
        send_mail(
            {'ojofemijoseph@outlook.com':'Joseph Ojo'},
            f"Request failed for ID {manager_id} with error: {str(e)}",
            'Failed')
        return None


def fetch_managers(engine):
        """
        Fetch distinct managers id from the db and saves it locally.

        Returns:
        - df (pd.DataFrame): A DataFrame containing the distinct Manager's id.
        """
        try:
            df = pd.read_sql(text("select distinct ENTRY from webinar_Standings"), engine)
            return df
        except Exception as e:
            send_mail(
                {'ojofemijoseph@outlook.com':'Joseph Ojo'},
                f"Failed to fetch managers: {str(e)}",
                "Failed"
                )
        return None
        
        
        
        
def fetch_gameweek_stat(df):
        """
        Fetch statistics for managers for the latest game week.

        Parameters:
        - retries (int): Number of retries in case of network errors.

        Returns:
        - list: A list of dictionaries containing manager statistics.
        """
        last_week = get_gameweek()
        
        managers_id = df[df.columns[0]].tolist()
        results = []

        for idx in managers_id:
            print(idx, last_week)
            api_url = f"https://fantasy.premierleague.com/api/entry/{idx}/event/{last_week[0]}/picks/"

            retry = 0
            while retry < 3:
                try:
                    Managers_team = get_manager_team(api_url, idx)
                    if Managers_team:
                        results.append(Managers_team)
                        retry = 5
                    else:
                        retry +=1
                except Exception as e:
                    retry += 1
                    print(e)
        return results


def load_warehouse(results, engine):
    YDP = pd.json_normalize(
        results,
        record_path="picks",
        meta=[
            "active_chip",
            ["entry_history", "event"],
            ["entry_history", "points_on_bench"],
            "manager_id",
        ],
        errors="ignore",
    )
    YDP['key'] = YDP['manager_id'].astype(str) + YDP['entry_history.event'].astype(str)
    Manager_keys = YDP['key'].to_list()
    
    with engine.connect() as conn:
        if inspect(engine).has_table("webinar_Managers_Team"):
            conn.execute(text('delete from `webinar_Managers_Team` where `key` in ' + f'{Manager_keys}'.replace('[','(').replace(']',')')))
            conn.commit()

    YDP.to_sql("webinar_Managers_Team", if_exists="append", con=engine,index=False)
    


def lambda_handler(event, context):
    uri = os.getenv('DB_URI')
    engine = create_snow_engine(uri)
    ydp_managers = fetch_managers(engine)
    if not ydp_managers:
        return
    managers_stats = fetch_gameweek_stat(ydp_managers)
    load_warehouse(managers_stats, engine)
    
    return True

