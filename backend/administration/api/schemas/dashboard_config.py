from ninja import Schema
from typing import List, Optional


class WidgetConfig(Schema):
    id: str
    visible: bool


class GraphWidgetConfig(Schema):
    widget_id: int
    graph_name: str
    type_id: int
    tag_id: Optional[int] = None
    month: int = 0
    exclude: str = "[0]"


class DashboardConfigOut(Schema):
    layout: List[WidgetConfig]
    graph_widgets: List[GraphWidgetConfig]


class DashboardConfigIn(Schema):
    layout: Optional[List[WidgetConfig]] = None
    graph_widgets: Optional[List[GraphWidgetConfig]] = None
