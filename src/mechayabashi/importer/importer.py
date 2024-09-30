from dataclasses import dataclass
from datetime import datetime


@dataclass
class Item:
    pubDate: datetime
    description: str
