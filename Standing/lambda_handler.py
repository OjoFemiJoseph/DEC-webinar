import os
from typing import Optional

import pandas as pd
import requests
from sqlalchemy import inspect, text
from util import create_snow_engine, send_mail


def fetch_fixture(week):
    """
    Fetch the status (finished or not) of the last game for a given week from the Fantasy Premier League API.

    Parameters:
    - week (int): The game week for which to retrieve fixture status.

    Returns:
    - str or None: The status of the last game ('Finished' or 'Not Finished') or None if no data is available.

    """
    url = "https://fantasy.premierleague.com/api/fixtures/"

    reponse = requests.get(url)
    if reponse.status_code != 200:
        return
    fixtures = reponse.json()

    data = pd.json_normalize(fixtures)
    last_game_status = data.loc[data["event"] == week, "finished"].iloc[-1]

    return last_game_status


def week_file(engine, week=4):
    """
    Read the last week number from a file or create the file with a default value if it doesn't exist.

    Parameters:
    - file (str): name of the file containing the week number.
    - default_week (int): Default week number to use when the file doesn't exist.

    Returns:
    - float: The last week number read from the file or the default week number.
    """
    try:
        week = pd.read_sql(text('select max(weeknum) as weeknum from gameweek2'), engine.connect())
        print(week)
        week = week.iloc[0].values
        
    except Exception as e:
        print(e)
        send_mail(
                {'ojofemijoseph@outlook.com':'Joseph Ojo'},
                f"Failed to get current Gameweek: {str(e)}",
                "Failed"
                )
        return
        

    return float(week)


def ge_result(response):
    """
    Extract and normalize data from a JSON response and return it as a Pandas DataFrame.

    Parameters:
    - response (requests.Response): The HTTP response containing JSON data.
    """

    df = pd.json_normalize(response.json()["standings"]["results"])

    return df


def is_last_game_played(engine, current_week: Optional[int] = None) -> Optional[bool]:
    """
    Check if the last game of the current week in the Fantasy Premier League has been played.

    Parameters:
    - current_week (int, optional): The current week number. If not provided, it will be fetched from week_file.

    Returns:
    - bool or None: True if the last game is played, False if it's not played, or None if data is unavailable.
    """

    current_week = week_file(engine)

    has_last_game_played = fetch_fixture(current_week)
    print(has_last_game_played)
    return has_last_game_played, current_week

def fetch_standing(page):
    """
    Fetch YDP FPL League standing.

    Parameters:
    - page (int): The page number.
    """
    url = f"https://fantasy.premierleague.com/api/leagues-classic/885844/standings?page_standings={page}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "cookie": "OptanonAlertBoxClosed=2023-08-14T07:21:20.502Z; _gid=GA1.2.853544306.1691997681; pl_profile=eyJzIjogIld6SXNOelV3T0RFM05EWmQ6MXFWVDlNOjhrOFRhUFBtMXpCRXhJQkZSM3hleGUtSklNZ2p1clp5RHRBcXNYRkZJdUUiLCAidSI6IHsiaWQiOiA3NTA4MTc0NiwgImZuIjogIkNoZWxzZWEiLCAibG4iOiAiTGFucmUtQmFkbXVzIiwgImZjIjogOH19; csrftoken=bAVmy1p0r3rYTfw3zbDuvojPmi808P3y; sessionid=.eJxVzUsLwjAQBOD_krOUvDbd9eZdUCieQ15LxFKKsSfxv5ve9Dh8M8xb-LC9qt9aefp7FkcxgkQ1WicOvxRDepRl93XmdR52Ga7nW7c2TZdTj_-DGlrt7QiEhWOw2ZSsmVSyWaecrWO2JBGS7GekE5IDh8GoqBEQyCgkRis-XxUjMp8:1qVT9N:kDH6Y8XCNHFa8jNbEWx34AaIi5d7qjp2qSRorCbxg1g; _ga=GA1.3.1920194934.1691997681; _gid=GA1.3.853544306.1691997681; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Aug+14+2023+19^%^3A37^%^3A28+GMT^%^2B0100+(West+Africa+Standard+Time)&version=202302.1.0&isIABGlobal=false&hosts=&consentId=95b26f06-35a4-486e-a999-f50f96d1d53f&interactionCount=1&landingPath=NotLandingPage&groups=C0001^%^3A1^%^2CC0002^%^3A1^%^2CC0003^%^3A1^%^2CC0004^%^3A1&geolocation=NG^%^3BOY&AwaitingReconsent=false; _ga=GA1.2.1920194934.1691997681; datadome=6-mDjA78VJorC~SbYPLvCi~OB9dYwbCMw06isde1p8vnZn8nPS4~HEKJvPsq1QORa6-VW3bjsthQpJ0RZyqAxsVHnzbVUEm5TTy8t_l5oU~lI3Zv1qlRnlh~iZtqEjot; _ga_844XQSF4K8=GS1.1.1692041085.5.1.1692041088.57.0.0",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Request successful!")
        return response

    print(f"Request failed with status code: {response.status_code}")
    return

    
def get_standing(resp):
    """
    Retrieve and concatenate multiple pages of standings data and return it as a JSON string.

    Returns:
    - str: A JSON containing the concatenated standings data.
    """
    try:
        standing_json = []
        start_page = 1
        has_next = True
        while has_next:
            print(f"{start_page} standing")
            response = fetch_standing(start_page)
            has_next = response.json()["standings"]["has_next"]
            standing_json.append(ge_result(response))

            start_page += 1

        standing_df_json = pd.concat(standing_json)
        print(standing_df_json)
        standing_df_json.reset_index(drop=True, inplace=True)
        return standing_df_json.to_json()
    except Exception as e:
        send_mail(
            {'ojofemijoseph@outlook.com':'Joseph Ojo'},
            f"Error Message: {e}",
            'Failed'
        )
    


    
def load_to_warehouse(engine, data,current_week):
    table_name = 'webinar_Standings'
    df = pd.read_json(data)
    df['gameweek'] = [int(current_week) for _ in range(df.shape[0])]
    df['key'] = df['entry'].astype(str) + df['gameweek'].astype(str) 
    
    standing_keys = df['key'].to_list()
    
    with engine.connect() as conn:
        if inspect(engine).has_table(table_name):
            conn.execute(text(f'delete from {table_name} where `key` in ' + f'{standing_keys}'.replace('[','(').replace(']',')')))
            conn.commit()

    df.to_sql(table_name, engine, if_exists='append', index = False)
    
    return True


def update_game_week(engine):
    week = pd.read_sql(text('select max(weeknum) as weeknum from gameweek2'), engine.connect())
    print(week)
    new_week = week.iloc[0].values + 1

    conn = engine.connect()
    conn.execute(text(f'insert into `gameweek2` (weeknum) VALUES ({new_week[0]})'))
    conn.commit()
    engine.dispose()
    
    
def lambda_handler(event, context):

    uri = os.getenv('DB_URI')
    
    engine = create_snow_engine(uri)
    resp,current_week = is_last_game_played(engine)
    print(resp)
    if resp:
        parsed_data = get_standing(resp)
        status2 = load_to_warehouse(engine, parsed_data,current_week)
    
        ugw = update_game_week(engine)
    
        return { 'IsLastGamePlayed': True}
    return { 'IsLastGamePlayed': False}

lambda_handler(None,None)