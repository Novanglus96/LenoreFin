from ninja import Router, File
from ninja.files import UploadedFile
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from django.http import Http404
from typing import List
import logging

from administration.api.dependencies.auth import FullAccessAuth
from transactions.models import Transaction, TransactionImage
from transactions.api.schemas.transaction_image import TransactionImageOut

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")

transaction_image_router = Router(tags=["Transaction Attachments"])


@transaction_image_router.get(
    "/list/{transaction_id}",
    response=List[TransactionImageOut],
)
def list_transaction_images(request, transaction_id: int):
    try:
        images = TransactionImage.objects.filter(transaction_id=transaction_id)
        api_logger.debug(f"Attachments listed for transaction #{transaction_id}")
        return images
    except Exception as e:
        error_logger.error(str(e))
        raise HttpError(500, "Record retrieval error")


@transaction_image_router.post(
    "/upload/{transaction_id}",
    response=TransactionImageOut,
    auth=FullAccessAuth(),
)
def upload_transaction_image(
    request,
    transaction_id: int,
    file: UploadedFile = File(...),
):
    try:
        transaction = get_object_or_404(Transaction, id=transaction_id)
        image = TransactionImage.objects.create(transaction=transaction, image=file)
        api_logger.info(f"Attachment uploaded for transaction #{transaction_id}")
        return image
    except Http404:
        raise HttpError(404, "Transaction not found")
    except Exception as e:
        error_logger.error(str(e))
        raise HttpError(500, "Upload error")


@transaction_image_router.delete(
    "/delete/{image_id}",
    auth=FullAccessAuth(),
)
def delete_transaction_image(request, image_id: int):
    try:
        image = get_object_or_404(TransactionImage, id=image_id)
        image.delete()
        api_logger.info(f"Attachment deleted #{image_id}")
        return {"success": True}
    except Http404:
        raise HttpError(404, "Attachment not found")
    except Exception as e:
        error_logger.error(str(e))
        raise HttpError(500, "Delete error")
