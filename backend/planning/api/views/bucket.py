import logging
from typing import List

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from administration.api.dependencies.auth import FullAccessAuth
from planning.api.schemas.bucket import BucketIn, BucketOut
from planning.models import Bucket
from reminders.models import Reminder

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")

bucket_router = Router(tags=["Buckets"])


def bucket_out(bucket: Bucket) -> BucketOut:
    reminder = bucket.reminder
    return BucketOut(
        id=bucket.id,
        name=bucket.name,
        contribution_per_paycheck=bucket.contribution_per_paycheck,
        goal_amount=bucket.goal_amount,
        goal_date=bucket.goal_date,
        active=bucket.active,
        account_id=bucket.account_id,
        account_name=bucket.account.account_name if bucket.account_id else None,
        reminder_id=bucket.reminder_id,
        reminder_description=reminder.description if reminder else None,
        reminder_amount=abs(reminder.amount) if reminder else None,
    )


def _validate(payload: BucketIn) -> dict:
    data = payload.dict()
    if data["goal_amount"] is not None and data["goal_amount"] < 0:
        raise HttpError(400, "A goal cannot be negative")
    if data["contribution_per_paycheck"] < 0:
        raise HttpError(400, "A contribution cannot be negative")
    if data["reminder_id"]:
        reminder = Reminder.objects.filter(pk=data["reminder_id"]).first()
        if reminder is None:
            raise HttpError(400, "That reminder does not exist")
        destination = reminder.reminder_destination_account_id
        # The reminder names the account; picking one is enough.
        if not data["account_id"]:
            data["account_id"] = destination
        elif destination and destination != data["account_id"]:
            raise HttpError(
                400, "That reminder does not pay into this bucket's account"
            )
    return data


@bucket_router.get("/list", response=List[BucketOut])
def list_buckets(request):
    return [
        bucket_out(b)
        for b in Bucket.objects.select_related("account", "reminder").all()
    ]


@bucket_router.get("/get/{bucket_id}", response=BucketOut)
def get_bucket(request, bucket_id: int):
    return bucket_out(get_object_or_404(Bucket, id=bucket_id))


@bucket_router.post("/create", auth=FullAccessAuth())
def create_bucket(request, payload: BucketIn):
    data = _validate(payload)
    try:
        bucket = Bucket.objects.create(**data)
    except IntegrityError:
        raise HttpError(400, "A bucket with that name already exists")
    api_logger.info(f"Bucket created : {bucket.name}")
    return {"id": bucket.id}


@bucket_router.put("/update/{bucket_id}", auth=FullAccessAuth())
def update_bucket(request, bucket_id: int, payload: BucketIn):
    bucket = get_object_or_404(Bucket, id=bucket_id)
    for field, value in _validate(payload).items():
        setattr(bucket, field, value)
    try:
        bucket.save()
    except IntegrityError:
        raise HttpError(400, "A bucket with that name already exists")
    api_logger.info(f"Bucket updated : #{bucket_id}")
    return {"success": True}


@bucket_router.delete("/delete/{bucket_id}", auth=FullAccessAuth())
def delete_bucket(request, bucket_id: int):
    bucket = get_object_or_404(Bucket, id=bucket_id)
    bucket.delete()
    api_logger.info(f"Bucket deleted : #{bucket_id}")
    return {"success": True}
