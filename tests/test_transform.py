import pytest
 
from src.transform import compute_renewable_share, compute_price_volatility
 
 
def test_compute_renewable_share_simple_split():
    # 1 timestamp, 2 sources: 300 renewable (solar), 700 non-renewable (gas)
    # -> renewable share = 300 / 1000 * 100 = 30.0%
    generation = {
        "solar": [(1000, 300.0)],
        "gas": [(1000, 700.0)],
    }
 
    records = compute_renewable_share(generation)
 
    assert len(records) == 1
    assert records[0].metric_name == "renewable_share_pct"
    assert records[0].value == pytest.approx(30.0)
 
 
def test_compute_renewable_share_handles_zero_total():
    # If total generation is 0 for a timestamp, share should be None,
    # not a division-by-zero error or a misleading 0.0.
    generation = {
        "solar": [(1000, 0.0)],
        "gas": [(1000, 0.0)],
    }
 
    records = compute_renewable_share(generation)
 
    assert records[0].value is None
 
 
def test_compute_renewable_share_aligns_multiple_timestamps():
    generation = {
        "solar": [(1000, 100.0), (2000, 200.0)],
        "gas": [(1000, 900.0), (2000, 800.0)],
    }
 
    records = compute_renewable_share(generation)
 
    assert len(records) == 2
    # ts=1000: 100 / 1000 = 10%
    # ts=2000: 200 / 1000 = 20%
    assert records[0].value == pytest.approx(10.0)
    assert records[1].value == pytest.approx(20.0)
 
 
def test_compute_price_volatility_spread_and_stdev():
    # Known values: 45.20, -8.50, 62.10, 30.00
    # spread = max - min = 62.10 - (-8.50) = 70.60
    price_series = [
        (1641769200000, 45.20),
        (1641772800000, -8.50),
        (1641776400000, 62.10),
        (1641780000000, 30.00),
    ]
 
    records = compute_price_volatility(price_series)
    by_name = {r.metric_name: r for r in records}
 
    assert by_name["price_spread_eur_mwh"].value == pytest.approx(70.60)
    # population stdev of [45.20, -8.50, 62.10, 30.00]
    assert by_name["price_stdev_eur_mwh"].value == pytest.approx(26.10, abs=0.1)
 
 
def test_compute_price_volatility_does_not_filter_negative_prices():
    """Regression test: negative day-ahead prices are real market events
    (high renewable output) and must be included in the calculation, not
    clipped to zero or dropped.
    """
    price_series = [
        (1000, -50.0),
        (2000, -50.0),
        (3000, -50.0),
    ]
 
    records = compute_price_volatility(price_series)
    by_name = {r.metric_name: r for r in records}
 
    # all values identical and negative -> spread and stdev both 0,
    # not an error, and not silently treating negatives as 0.0
    assert by_name["price_spread_eur_mwh"].value == pytest.approx(0.0)
    assert by_name["price_stdev_eur_mwh"].value == pytest.approx(0.0)