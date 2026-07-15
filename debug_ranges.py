from src.extract import fetch_all_generation
from datetime import datetime, timezone

generation = fetch_all_generation()
for source, series in generation.items():
    first_ts = series[0][0]
    last_ts = series[-1][0]
    print(source,
        datetime.fromtimestamp(first_ts/1000, tz=timezone.utc),
        "->",
        datetime.fromtimestamp(last_ts/1000, tz=timezone.utc),
        f"({len(series)} points)")