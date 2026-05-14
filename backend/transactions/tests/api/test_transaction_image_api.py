import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from transactions.models import TransactionImage

AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_transaction_list_attachment_count_zero(api_client, test_transaction):
    response = api_client.get(
        f"/transactions/get/{test_transaction.id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["attachment_count"] == 0


@pytest.mark.django_db
@pytest.mark.api
def test_transaction_list_attachment_count_reflects_uploads(
    api_client, settings, tmp_path, test_transaction
):
    settings.MEDIA_ROOT = tmp_path

    for name in ("receipt1.jpg", "receipt2.jpg"):
        TransactionImage.objects.create(
            image=SimpleUploadedFile(name, b"bytes", content_type="image/jpeg"),
            transaction=test_transaction,
        )

    response = api_client.get(
        f"/transactions/get/{test_transaction.id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["attachment_count"] == 2


@pytest.mark.django_db
@pytest.mark.api
def test_list_transaction_images_empty(api_client, test_transaction):
    response = api_client.get(
        f"/transactions/attachments/list/{test_transaction.id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
@pytest.mark.api
def test_list_transaction_images(api_client, settings, tmp_path, test_transaction):
    settings.MEDIA_ROOT = tmp_path

    file = SimpleUploadedFile("receipt.jpg", b"fake image bytes", content_type="image/jpeg")
    obj = TransactionImage.objects.create(image=file, transaction=test_transaction)

    response = api_client.get(
        f"/transactions/attachments/list/{test_transaction.id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == obj.id
    assert data[0]["url"].startswith("/media/tran_images/")
    assert data[0]["filename"].endswith("-receipt.jpg")


@pytest.mark.django_db
@pytest.mark.api
def test_upload_transaction_image(api_client, settings, tmp_path, test_transaction):
    settings.MEDIA_ROOT = tmp_path

    file = SimpleUploadedFile("receipt.jpg", b"fake image bytes", content_type="image/jpeg")

    response = api_client.post(
        f"/transactions/attachments/upload/{test_transaction.id}",
        FILES={"file": file},
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["url"].startswith("/media/tran_images/")
    assert data["filename"].endswith("-receipt.jpg")

    assert TransactionImage.objects.filter(id=data["id"]).exists()
    assert (tmp_path / TransactionImage.objects.get(id=data["id"]).image.name).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_upload_transaction_image_transaction_not_found(api_client):
    file = SimpleUploadedFile("receipt.jpg", b"fake image bytes", content_type="image/jpeg")

    response = api_client.post(
        "/transactions/attachments/upload/9999",
        FILES={"file": file},
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_delete_transaction_image(api_client, settings, tmp_path, test_transaction):
    settings.MEDIA_ROOT = tmp_path

    file = SimpleUploadedFile("receipt.jpg", b"fake image bytes", content_type="image/jpeg")
    obj = TransactionImage.objects.create(image=file, transaction=test_transaction)
    path = tmp_path / obj.image.name
    assert path.exists()

    response = api_client.delete(
        f"/transactions/attachments/delete/{obj.id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert not TransactionImage.objects.filter(id=obj.id).exists()
    assert not path.exists()


@pytest.mark.django_db
@pytest.mark.api
def test_delete_transaction_image_not_found(api_client):
    response = api_client.delete(
        "/transactions/attachments/delete/9999",
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_delete_transaction_removes_attachment_files(
    api_client, settings, tmp_path, test_transaction
):
    """Deleting a transaction via the API cleans up all its attachment files."""
    settings.MEDIA_ROOT = tmp_path

    file1 = SimpleUploadedFile("receipt1.jpg", b"bytes1", content_type="image/jpeg")
    file2 = SimpleUploadedFile("receipt2.jpg", b"bytes2", content_type="image/jpeg")
    obj1 = TransactionImage.objects.create(image=file1, transaction=test_transaction)
    obj2 = TransactionImage.objects.create(image=file2, transaction=test_transaction)

    path1 = tmp_path / obj1.image.name
    path2 = tmp_path / obj2.image.name
    assert path1.exists()
    assert path2.exists()

    api_client.patch(
        "/transactions/delete",
        json={"transactions": [test_transaction.id]},
        headers=AUTH,
    )

    assert not TransactionImage.objects.filter(
        transaction_id=test_transaction.id
    ).exists()
    assert not path1.exists()
    assert not path2.exists()
