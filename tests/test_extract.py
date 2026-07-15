

import json
from pathlib import Path

import responses

from src.extract import BASE, REGION, RESOLUTION, get_latest_timestamp, get_series

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


@responses.activate
def test_get_latest_timestamp_returns_last_entry():
    filter_id = 4067
    fixture = load_fixture("index_hour.json")
    url = f"{BASE}/{filter_id}/{REGION}/index_{RESOLUTION}.json"
    responses.add(responses.GET, url, json=fixture, status=200)

    result = get_latest_timestamp(filter_id)

    assert result == fixture["timestamps"][-1]
    assert result == 1641769200000


@responses.activate
def test_get_series_generation():
    filter_id = 4067
    timestamp = 1641769200000
    fixture = load_fixture("generation_series_4067.json")
    url = f"{BASE}/{filter_id}/{REGION}/{filter_id}_{REGION}_{RESOLUTION}_{timestamp}.json"
    responses.add(responses.GET, url, json=fixture, status=200)

    series = get_series(filter_id, timestamp)

    assert series == fixture["series"]
    assert series[0] == [1641769200000, 4000.0]


@responses.activate
def test_get_series_price():
    """Price data (filter 4169) uses the same chart_data path as generation
    data — confirmed against the live API. (Older SMARD documentation
    suggested a separate /table_data/ path for prices; that's outdated.)
    """
    filter_id = 4169
    timestamp = 1641769200000
    fixture = load_fixture("price_series_4169.json")
    url = f"{BASE}/{filter_id}/{REGION}/{filter_id}_{REGION}_{RESOLUTION}_{timestamp}.json"
    responses.add(responses.GET, url, json=fixture, status=200)

    series = get_series(filter_id, timestamp)

    assert series == fixture["series"]
    assert any(price < 0 for _, price in series)