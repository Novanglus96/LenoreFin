import pytest
import re
from django.core.files.uploadedfile import SimpleUploadedFile
from transactions.models import TransactionImage


@pytest.mark.django_db
def test_transaction_image_upload(settings, tmp_path, test_transaction):
    settings.MEDIA_ROOT = tmp_path

    file = SimpleUploadedFile(
        "receipt.jpg",
        b"fake image bytes",
        content_type="image/jpeg",
    )

    obj = TransactionImage.objects.create(
        image=file,
        transaction=test_transaction,
    )

    assert obj.id is not None
    assert obj.transaction == test_transaction

    # Filename structure
    assert obj.image.name.startswith("tran_images/")
    assert obj.image.name.endswith("-receipt.jpg")

    # Regex for timestamp
    assert re.match(
        r"tran_images/\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-receipt\.jpg",
        obj.image.name,
    )

    # File exists
    assert (tmp_path / obj.image.name).exists()


@pytest.mark.django_db
def test_transaction_image_file_deleted(settings, tmp_path, test_transaction):
    settings.MEDIA_ROOT = tmp_path

    file = SimpleUploadedFile("receipt.jpg", b"fake image")

    obj = TransactionImage.objects.create(
        image=file,
        transaction=test_transaction,
    )

    path = tmp_path / obj.image.name
    assert path.exists()

    obj.delete()

    assert not path.exists()


@pytest.mark.django_db
def test_transaction_image_deleted_on_transaction_delete(
    settings, tmp_path, test_transaction
):
    settings.MEDIA_ROOT = tmp_path

    file = SimpleUploadedFile("receipt.jpg", b"fake image")

    TransactionImage.objects.create(
        image=file,
        transaction=test_transaction,
    )

    assert TransactionImage.objects.count() == 1
    test_transaction.delete()
    assert TransactionImage.objects.count() == 0


@pytest.mark.django_db
def test_transaction_image_file_deleted_on_transaction_delete(
    settings, tmp_path, test_transaction
):
    """File is removed from disk when parent transaction is cascade-deleted."""
    settings.MEDIA_ROOT = tmp_path

    file = SimpleUploadedFile("receipt.jpg", b"fake image")
    obj = TransactionImage.objects.create(
        image=file,
        transaction=test_transaction,
    )

    path = tmp_path / obj.image.name
    assert path.exists()

    test_transaction.delete()

    assert not path.exists()


@pytest.mark.django_db
def test_transaction_image_url_property(settings, tmp_path, test_transaction):
    settings.MEDIA_ROOT = tmp_path

    file = SimpleUploadedFile("receipt.jpg", b"fake image bytes")
    obj = TransactionImage.objects.create(
        image=file,
        transaction=test_transaction,
    )

    assert obj.url is not None
    assert obj.url.startswith("/media/tran_images/")
    assert obj.url.endswith("-receipt.jpg")


@pytest.mark.django_db
def test_transaction_image_filename_property(settings, tmp_path, test_transaction):
    settings.MEDIA_ROOT = tmp_path

    file = SimpleUploadedFile("my-receipt.jpg", b"fake image bytes")
    obj = TransactionImage.objects.create(
        image=file,
        transaction=test_transaction,
    )

    assert obj.filename is not None
    assert obj.filename.endswith("-my-receipt.jpg")
