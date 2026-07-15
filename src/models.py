from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class KPIRecord(BaseModel):
    timestamp: datetime
    metric_name: str
    value: Optional[float]
    segment: str
    schema_version: str = "1.0"