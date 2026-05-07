import pytest
from django.utils import timezone
from administration.models import Message


AUTH = {"Authorization": "Bearer test-api-key"}


def make_message(message="Test message", unread=True):
    return Message.objects.create(
        message_date=timezone.now(),
        message=message,
        unread=unread,
    )


@pytest.mark.django_db
@pytest.mark.api
def test_create_message(api_client):
    payload = {
        "message_date": timezone.now().isoformat(),
        "message": "New message",
        "unread": True,
    }
    response = api_client.post(
        "/administration/messages/create",
        json=payload,
        headers=AUTH,
    )

    assert response.status_code == 200
    assert "id" in response.json()
    assert Message.objects.filter(message="New message").exists()


@pytest.mark.django_db
@pytest.mark.api
def test_get_message(api_client):
    message = make_message("Get me")

    response = api_client.get(
        f"/administration/messages/get/{message.id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == message.id
    assert data["message"] == "Get me"
    assert data["unread"] is True


@pytest.mark.django_db
@pytest.mark.api
def test_get_message_not_found(api_client):
    response = api_client.get(
        "/administration/messages/get/99999",
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_list_messages_empty(api_client):
    response = api_client.get("/administration/messages/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert data["unread_count"] == 0
    assert data["total_count"] == 0
    assert data["messages"] == []


@pytest.mark.django_db
@pytest.mark.api
def test_list_messages_unread_count(api_client):
    make_message("Unread 1", unread=True)
    make_message("Unread 2", unread=True)
    make_message("Read 1", unread=False)

    response = api_client.get("/administration/messages/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert data["unread_count"] == 2
    assert data["total_count"] == 3
    assert len(data["messages"]) == 3


@pytest.mark.django_db
@pytest.mark.api
def test_list_messages_ordered_by_id_descending(api_client):
    msg1 = make_message("First")
    make_message("Second")
    msg3 = make_message("Third")

    response = api_client.get("/administration/messages/list", headers=AUTH)

    assert response.status_code == 200
    ids = [m["id"] for m in response.json()["messages"]]
    assert ids == sorted(ids, reverse=True)
    assert ids[0] == msg3.id
    assert ids[-1] == msg1.id


@pytest.mark.django_db
@pytest.mark.api
def test_update_message(api_client):
    message = make_message("Original", unread=True)

    payload = {
        "message_date": timezone.now().isoformat(),
        "message": "Updated message",
        "unread": False,
    }
    response = api_client.put(
        f"/administration/messages/update/{message.id}",
        json=payload,
        headers=AUTH,
    )

    assert response.status_code == 200
    message.refresh_from_db()
    assert message.message == "Updated message"
    assert message.unread is False


@pytest.mark.django_db
@pytest.mark.api
def test_update_message_not_found(api_client):
    payload = {
        "message_date": timezone.now().isoformat(),
        "message": "Does not matter",
        "unread": False,
    }
    response = api_client.put(
        "/administration/messages/update/99999",
        json=payload,
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_readall_marks_all_messages_read(api_client):
    make_message("Msg 1", unread=True)
    make_message("Msg 2", unread=True)

    response = api_client.patch(
        "/administration/messages/readall/0",
        json={"unread": False},
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert Message.objects.filter(unread=True).count() == 0


@pytest.mark.django_db
@pytest.mark.api
def test_delete_message(api_client):
    message = make_message("Delete me")

    response = api_client.delete(
        f"/administration/messages/delete/{message.id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert not Message.objects.filter(id=message.id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_delete_message_not_found(api_client):
    response = api_client.delete(
        "/administration/messages/delete/99999",
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_deleteall_removes_all_messages(api_client):
    make_message("Msg A")
    make_message("Msg B")
    make_message("Msg C")

    assert Message.objects.count() == 3

    response = api_client.delete(
        "/administration/messages/deleteall/0",
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert Message.objects.count() == 0
