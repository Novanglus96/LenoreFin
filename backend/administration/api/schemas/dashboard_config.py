from ninja import Schema
from typing import List


class WidgetConfig(Schema):
    id: str
    visible: bool


class DashboardConfigOut(Schema):
    layout: List[WidgetConfig]


class DashboardConfigIn(Schema):
    layout: List[WidgetConfig]
