#! /usr/bin/env python3
"""
Timeular status widget for waybar.
Requires api-key and secret.

Can also generate the css-styles to render the activities nicely.
Suggested use: add a timeular.css file to your waybar config and import it from the styles.css

Add @import url("timeular.css"); to the top of your waybar style.css, then
python3 get_timeular_status.py  --api_key KET --api_secret SECRET --generate_styles > .config/waybar/timeular.css

"""


import json
import requests
from argparse import ArgumentParser
from typing import Dict
import datetime
SIGN_IN_URL = "https://api.timeular.com/api/v3/developer/sign-in"
CURRENT_TRACKING_URL = "https://api.timeular.com/api/v3/tracking"
GET_ACTIVITIES_URL = "https://api.timeular.com/api/v3/activities"


CSS_HEADER = """/* Activity Classes */"""
CSS_FOOTER = """
/* base classes */
#custom-timeular.ok {
        background: rgb( 42,161,152);
}
#custom-timeular.nothing {
    background: #f53c3c;
    animation-name: blink;
    animation-duration: 0.5s;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
    animation-direction: alternate;
}
"""

all_activities = dict()


def print_tracking(response: dict) -> Dict[str, str]:
    if (tracking := response.get("currentTracking")) is None:
        return {"text": "Nothing being tracked!",
                "class": "nothing"}

    if tracking['activityId'] in all_activities:
        name = all_activities[tracking['activityId']]['name']
    else:
        name = 'Tracking something!'
    if len(name) > 30:
        name = name[:30]+'...'
    if (started_at := tracking.get('startedAt')) is not None:
        start_time = datetime.datetime.fromisoformat(started_at)
        name = str(datetime.datetime.utcnow() -
                   start_time).rsplit(':', maxsplit=1)[0] + " | "+name
    return {"text": name.center(min(len(name)+6, 40)), "class": f"act_{tracking['activityId']}"}


def main(api_key: str, api_secret: str, should_generate_styles: bool = False):
    payload = json.dumps({
        "apiKey": f"{api_key}",
        "apiSecret": f"{api_secret}"
    })
    response = requests.request("POST", SIGN_IN_URL, headers={
                                'Content-Type': 'application/json'}, data=payload)
    token = response.json()["token"]
    update_activites(token)
    if should_generate_styles:
        generate_styles()
        return
    response = requests.request("GET", CURRENT_TRACKING_URL, headers={
                                'Authorization': f'Bearer {token}'}, data=payload)
    current_tracking = response.json()
    print(json.dumps(print_tracking(current_tracking)))


def update_activites(token: str) -> None:
    response = requests.request("GET", GET_ACTIVITIES_URL, headers={
                                'Authorization':  f'Bearer {token}'})
    all_activities.update(
        {act['id']: act for act in response.json().get('activities', [])})


def generate_styles():
    print(CSS_HEADER)
    for act in all_activities.values():
        print(
            """
/* {act_name} */
#custom-timeular.act_{act_id} {{
    background: {color};
}}""".format(act_id=act['id'], color=act['color'], act_name=act['name'])
        )
    print(CSS_FOOTER)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--api_key", required=True)
    parser.add_argument("--generate_styles", action="store_true")
    parser.add_argument("--api_secret", required=True)
    args = parser.parse_args()
    try:
        main(args.api_key, args.api_secret,
             should_generate_styles=args.generate_styles)
    except Exception as err:
        print('{{"text" : "Error occured: {}", "class" : "nothing"}}'.format(str(err)))
