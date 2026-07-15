import argparse

from src.extract import fetch_all_generation, get_latest_timestamp, get_series, PRICE_FILTER
from src.transform import compute_renewable_share, compute_price_volatility
from src.exports import export_records
from src.report import build_report


def main(out_dir: str):
    generation = fetch_all_generation()

    price_ts = get_latest_timestamp(PRICE_FILTER)
    price_series = get_series(PRICE_FILTER, price_ts)

    records = compute_renewable_share(generation) + compute_price_volatility(price_series)
    export_records(records, out_dir)
    build_report(records, out_path=f"{out_dir}/report.html")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    main(**vars(parser.parse_args()))