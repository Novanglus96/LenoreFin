from ninja import Schema
from typing import Optional
from datetime import datetime


class BackupConfigOut(Schema):
    id: int
    backup_enabled: bool
    frequency: str
    backup_time: str
    copies_to_keep: int


class BackupConfigIn(Schema):
    backup_enabled: Optional[bool] = None
    frequency: Optional[str] = None
    backup_time: Optional[str] = None
    copies_to_keep: Optional[int] = None


class BackupFileOut(Schema):
    filename: str
    size: int
    created_at: datetime
    backup_type: str
