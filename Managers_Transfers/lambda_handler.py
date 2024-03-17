import json
import os

import pandas as pd
import requests
from sqlalchemy import create_engine, text


def lambda_handler(event, context):
    
    url = f"https://fantasy.premierleague.com/api/leagues-classic/885844/standings?page_standings={page}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "cookie": "OptanonAlertBoxClosed=2023-08-14T07:21:20.502Z; _gid=GA1.2.853544306.1691997681; pl_profile=eyJzIjogIld6SXNOelV3T0RFM05EWmQ6MXFWVDlNOjhrOFRhUFBtMXpCRXhJQkZSM3hleGUtSklNZ2p1clp5RHRBcXNYRkZJdUUiLCAidSI6IHsiaWQiOiA3NTA4MTc0NiwgImZuIjogIkNoZWxzZWEiLCAibG4iOiAiTGFucmUtQmFkbXVzIiwgImZjIjogOH19; csrftoken=bAVmy1p0r3rYTfw3zbDuvojPmi808P3y; sessionid=.eJxVzUsLwjAQBOD_krOUvDbd9eZdUCieQ15LxFKKsSfxv5ve9Dh8M8xb-LC9qt9aefp7FkcxgkQ1WicOvxRDepRl93XmdR52Ga7nW7c2TZdTj_-DGlrt7QiEhWOw2ZSsmVSyWaecrWO2JBGS7GekE5IDh8GoqBEQyCgkRis-XxUjMp8:1qVT9N:kDH6Y8XCNHFa8jNbEWx34AaIi5d7qjp2qSRorCbxg1g; _ga=GA1.3.1920194934.1691997681; _gid=GA1.3.853544306.1691997681; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Aug+14+2023+19^%^3A37^%^3A28+GMT^%^2B0100+(West+Africa+Standard+Time)&version=202302.1.0&isIABGlobal=false&hosts=&consentId=95b26f06-35a4-486e-a999-f50f96d1d53f&interactionCount=1&landingPath=NotLandingPage&groups=C0001^%^3A1^%^2CC0002^%^3A1^%^2CC0003^%^3A1^%^2CC0004^%^3A1&geolocation=NG^%^3BOY&AwaitingReconsent=false; _ga=GA1.2.1920194934.1691997681; datadome=6-mDjA78VJorC~SbYPLvCi~OB9dYwbCMw06isde1p8vnZn8nPS4~HEKJvPsq1QORa6-VW3bjsthQpJ0RZyqAxsVHnzbVUEm5TTy8t_l5oU~lI3Zv1qlRnlh~iZtqEjot; _ga_844XQSF4K8=GS1.1.1692041085.5.1.1692041088.57.0.0",
    }
    engine = create_engine(os.getenv('DB_URI'))
    managers = pd.read_sql(text('select distinct entry from webinar_Standings'),engine.connect())
    results = []
    managers_id = managers['entry'].tolist()

    for idx in managers_id:
        api_url = f'https://fantasy.premierleague.com/api/entry/{idx}/transfers/'
        
        response = requests.get(api_url)
    
        if response.status_code == 200:
            Managers_team = response.json()
            Managers_team = pd.json_normalize(Managers_team)

            results.append(Managers_team)
           
        else:
            print(f"Request failed for ID {idx} with status code: {response.status_code}")
            
    df = pd.concat(results)
    df.to_sql('Webinar_Managers_Transfers',index=False, con=engine, if_exists='replace')

