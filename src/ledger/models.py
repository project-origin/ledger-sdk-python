

from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
from marshmallow_dataclass import class_schema

from .requests import Direction

@dataclass
class Measurement():
    address: Optional[str] = field()
    amount: int = field()
    direction: Direction = field()
    begin: datetime = field()
    end: datetime = field()
    sector: str = field()
    key: str = field()



@dataclass
class GGO():
    address: Optional[str] = field()
    amount: int = field()
    begin: datetime = field()
    end: datetime = field()
    sector: str = field()
    tech_type: str = field()
    fuel_type: str = field()
    key: str = field()


measurement_schema = class_schema(Measurement)
ggo_schema = class_schema(GGO)