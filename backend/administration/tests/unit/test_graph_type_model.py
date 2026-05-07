import pytest
from administration.models import GraphType
from django.db import IntegrityError


@pytest.mark.django_db
def test_graph_type_creation():
    graph_type = GraphType.objects.create(graph_type="Widget")

    assert graph_type.graph_type == "Widget"


@pytest.mark.django_db
def test_graph_type_must_be_unique():
    GraphType.objects.create(graph_type="Line")

    with pytest.raises(IntegrityError):
        GraphType.objects.create(graph_type="Line")


@pytest.mark.django_db
def test_graph_type_string_representation():
    """Ensure __str__ returns the expected formatted string."""
    graph_type = GraphType.objects.create(graph_type="Widget")

    expected = "Widget"
    assert str(graph_type) == expected
