import statistics
from datetime import datetime, timezone
from collections import defaultdict
from src.extract import RENEWABLE_SOURCES
from src.models import KPIRecord

def compute_renewable_share(generation: dict[str, list[tuple[int, float]]]) -> list[KPIRecord]:
    # Index each source's series by timestamp for alignment
    by_ts = {}
    for source, series in generation.items():
        for ts, value in series:
            by_ts.setdefault(ts, {})[source] = value or 0.0

    records = []
    for ts, values in sorted(by_ts.items()):
        total = sum(values.values())
        renewable = sum(v for k, v in values.items() if k in RENEWABLE_SOURCES)
        share = (renewable / total * 100) if total > 0 else None
        records.append(KPIRecord(
            timestamp=datetime.fromtimestamp(ts / 1000, tz=timezone.utc),
            metric_name="renewable_share_pct",
            value=share,
            segment="DE",
        ))
    return records


def compute_price_volatility(price_series: list[tuple[int, float]]) -> list[KPIRecord]:
  
    by_day = defaultdict(list)
    for ts, value in price_series:
        if value is None:
            continue
        day = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).date()
        by_day[day].append((ts, value))

    records = []
    for day, points in sorted(by_day.items()):
        values = [v for _, v in points]
        day_ts = datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc)
        records.append(KPIRecord(
            timestamp=day_ts, metric_name="price_spread_eur_mwh",
            value=max(values) - min(values), segment="DE_LU",
        ))
        records.append(KPIRecord(
            timestamp=day_ts, metric_name="price_stdev_eur_mwh",
            value=statistics.pstdev(values), segment="DE_LU",
        ))
    return records