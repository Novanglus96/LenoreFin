from ninja import Router
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from django.http import Http404
from typing import List
import logging

from planning.models import DetectedRecurring
from planning.api.schemas.detected_recurring import DetectedRecurringOut

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")

detected_recurring_router = Router(tags=["Detected Recurring"])


def _serialize(d: DetectedRecurring) -> dict:
    return {
        "id": d.id,
        "description": d.description,
        "estimated_amount": d.estimated_amount,
        "repeat_id": d.repeat_id,
        "repeat_name": d.repeat.repeat_name if d.repeat else None,
        "next_estimated_date": d.next_estimated_date,
        "transaction_ids": d.transaction_ids,
        "created_at": d.created_at,
    }


@detected_recurring_router.get("", response=List[DetectedRecurringOut])
def list_detected(request):
    detections = DetectedRecurring.objects.filter(is_ignored=False).select_related("repeat")
    return [_serialize(d) for d in detections]


@detected_recurring_router.post("/{detection_id}/ignore")
def ignore_detected(request, detection_id: int):
    try:
        detection = get_object_or_404(DetectedRecurring, id=detection_id)
        detection.is_ignored = True
        detection.save(update_fields=["is_ignored"])
        api_logger.info(f"Detection ignored: {detection.description}")
        return {"success": True}
    except Http404:
        raise HttpError(404, "Detection not found")
    except Exception as e:
        error_logger.exception(str(e))
        raise HttpError(500, "Failed to ignore detection")


@detected_recurring_router.delete("/{detection_id}")
def delete_detected(request, detection_id: int):
    try:
        detection = get_object_or_404(DetectedRecurring, id=detection_id)
        detection.delete()
        api_logger.info(f"Detection deleted: {detection_id}")
        return {"success": True}
    except Http404:
        raise HttpError(404, "Detection not found")
    except Exception as e:
        error_logger.exception(str(e))
        raise HttpError(500, "Failed to delete detection")
