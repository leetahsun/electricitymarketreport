
import requests
from datatime import datetime, timezone

BASE =

FILTERS = {
    "wind_onshore": 4067,
    "wind_offshore": 1225,
    "solar": 4068,
    "lignite": 1223,
    "hard_coal": 4069,
    "nuclear": 1224,
    "gas": 4071,
    "hydro": 3792,
    "biomass": 4066,
    "price_de_lu": 4169,   # day-ahead price, EUR/MWh
}

RENEWABLE_SOURCES = {"wind_onshore", "wind_offshore", "solar", "hydro", "biomass"}

REIGON = "DE"
RESOLUTION = "hour"

#get the latest timestamp
def get_latest_timestamp(filter_id: int) -> int:
    url = f"{BASE}/{filter_id}/{REGION}/index_{RESOLUTION}.json"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()["timestamps"][-1]

def get_series(filter_id: int, timestamp: int) -> list[tuple[int, float]]:
    url = f"{BASE}/{filter_id}/{REGION}/{filter_id}_{REGION}_{RESOLUTION}_{timestamp}.json"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()["series"]

def fetch_all_generation() -> dict[str, list[tuple[int, float]]]:
    data = {}
    for name, fid in FILTERS.items():
        ts = get_latest_timestamp(fid)
        data[name] = get_series(fid, ts)
    return data