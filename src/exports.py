import json
from pathlib import Path
from src.models import KPIRecord

def export_records(records: list[KPIRecord], out_dir: str):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    data = [r.model_dump(mode="json") for r in records]

    (Path(out_dir) / "kpis.json").write_text(json.dumps(data, indent=2))

    import pandas as pd
    pd.DataFrame(data).to_parquet(Path(out_dir) / "kpis.parquet", index=False)