from ninja import Schema
from pydantic import ConfigDict
from typing import Optional


class TransactionImageOut(Schema):
    id: int
    url: Optional[str] = None
    filename: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
