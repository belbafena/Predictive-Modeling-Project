import requests
import urllib3
import pandas as pd

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SAS_URL  = "https://vfl-061.engage.sas.com"
USERNAME = "belete_bafena.ageno@stud.fils.upb.ro"
PASSWORD = "ADAsaslab@123"                    # ← fill this in
FLOW_ID  = "cbcc2025-abe4-4c4d-9f58-bc4d7337a5ca"


def get_sas_token():
    try:
        response = requests.post(
            f"{SAS_URL}/SASLogon/oauth/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "password",
                "username": USERNAME,
                "password": PASSWORD,
            },
            auth=("sas.ec", ""),
            verify=False,
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    except Exception as e:
        print(f"Token error: {e}")
        return None


def call_sas_decision(row):
    token = get_sas_token()
    if not token:
        print("Could not get token — check credentials")
        return None

    lag_traffic = float(row["LagTraffic"]) if not pd.isna(row["LagTraffic"]) else 0.0
    rain_lag    = float(row["RainLag"])    if not pd.isna(row["RainLag"])    else 0.0

    payload = {
        "inputs": [
            {"name": "MovingAvg3hr", "value": float(row["MovingAvg3hr"])},
            {"name": "Hour",         "value": int(row["Hour"])},
            {"name": "LagTraffic",   "value": lag_traffic},
            {"name": "Month",        "value": int(row["Month"])},
            {"name": "Junction",     "value": int(row["Junction"])},
            {"name": "DayOfWeek",    "value": int(row["DayOfWeek"])},
            {"name": "TempC",        "value": float(row["TempC"])},
            {"name": "RAIN_MM",      "value": float(row["RAIN_MM"])},
            {"name": "RainLag",      "value": rain_lag},
            {"name": "RainFlag",     "value": int(row["RainFlag"])},
            {"name": "Weekend",      "value": int(row["Weekend"])},
        ]
    }

    try:
        response = requests.post(
            f"{SAS_URL}/decisions/flows/{FLOW_ID}/execute",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=payload,
            verify=False,
            timeout=15
        )
        print(f"SAS API status: {response.status_code}")
        if response.status_code == 200:
            outputs = {}
            for item in response.json().get("outputs", []):
                outputs[item["name"]] = item["value"]
            return outputs
        else:
            print(f"SAS API error: {response.text}")
            return None
    except Exception as e:
        print(f"API call error: {e}")
        return None