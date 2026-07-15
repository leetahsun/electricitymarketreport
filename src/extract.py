

import requests

BASE = "https://www.smard.de/app/chart_data"

REGION = "DE"
RESOLUTION = "hour"

GENERATION_FILTERS = {
    "wind_onshore": 4067,
    "wind_offshore": 1225,
    "solar": 4068,
    "lignite": 1223,
    "hard_coal": 4069,
    "gas": 4071,
    "hydro": 1226,      # corrected — was 3792, which pointed at the wrong (forecast) filter
    "biomass": 4066,
}

PRICE_FILTER = 4169  # DE/LU day-ahead price, EUR/MWh

RENEWABLE_SOURCES = {"wind_onshore", "wind_offshore", "solar", "hydro", "biomass"}


def get_latest_timestamp(filter_id: int) -> int:
    """Get the most recent available timestamp bucket for a given filter."""
    url = f"{BASE}/{filter_id}/{REGION}/index_{RESOLUTION}.json"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()["timestamps"][-1]


def get_series(filter_id: int, timestamp: int) -> list[tuple[int, float]]:
    """Fetch a time series (generation or price — both use chart_data)."""
    url = f"{BASE}/{filter_id}/{REGION}/{filter_id}_{REGION}_{RESOLUTION}_{timestamp}.json"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()["series"]


def fetch_all_generation() -> dict[str, list[tuple[int, float]]]:
    """Fetch generation series for all sources, aligned to one shared
    reference timestamp (rather than each source fetching its own
    'latest' timestamp independently, which can land in different weekly
    buckets per source and silently break KPI alignment downstream).
    """
    reference_ts = get_latest_timestamp(GENERATION_FILTERS["wind_onshore"])
    data = {}
    for name, fid in GENERATION_FILTERS.items():
        data[name] = get_series(fid, reference_ts)
    return data


def fetch_latest_price() -> list[tuple[int, float]]:
    """Fetch the latest DE/LU day-ahead price series."""
    ts = get_latest_timestamp(PRICE_FILTER)
    return get_series(PRICE_FILTER, ts)