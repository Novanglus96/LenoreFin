from ninja import Router
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from ninja.errors import HttpError
from planning.models import Budget, Bucket
from tags.models import MainTag, Tag
from planning.api.schemas.bucket import (
    BucketIn,
    BucketOut,
    BucketsWithTotals,
)
from django.shortcuts import get_object_or_404
from django.http import Http404
import logging
from administration.api.dependencies.auth import FullAccessAuth

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

bucket_router = Router(tags=["Buckets"])


@bucket_router.post("/create", auth=FullAccessAuth())
def create_bucket(request, payload: BucketIn):
    """
    The function `create_bucket` creates a bucket

    Args:
        request ():
        payload (BucketIn): An object using schema of BucketIn.

    Returns:
        id: returns the id of the created bucket
    """

    try:
        fields = payload.dict()
        # Many-to-many cannot be set before the row exists.
        budget_ids = fields.pop("budget_ids", [])
        tag_ids = fields.pop("scope_tag_ids", [])
        main_tag_ids = fields.pop("scope_main_tag_ids", [])
        bucket = Bucket(**fields)
        # Target/account coherence is enforced in Bucket.clean(); without
        # this the API would happily store a target pointing at no account.
        bucket.full_clean(exclude=["name"])
        bucket.save()
        if budget_ids:
            bucket.budgets.set(Budget.objects.filter(id__in=budget_ids))
        if tag_ids:
            bucket.scope_tags.set(Tag.objects.filter(id__in=tag_ids))
        if main_tag_ids:
            bucket.scope_main_tags.set(MainTag.objects.filter(id__in=main_tag_ids))
        api_logger.info(f"Bucket created : {payload.name}")
        return {"id": bucket.id}
    except ValidationError as validation_error:
        api_logger.error(
            f"Bucket not created : invalid ({validation_error.messages})"
        )
        raise HttpError(400, "; ".join(validation_error.messages))
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Bucket not created : bucket exists ({payload.name})"
            )
            error_logger.exception(
                f"Bucket not created : bucket exists ({payload.name})"
            )
            raise HttpError(400, "Bucket already exists")
        else:
            # Log other types of integry errors
            api_logger.error("Bucket not created : db integrity error")
            error_logger.exception("Bucket not created : db integrity error")
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Bucket not created")
        error_logger.exception(f"{str(e)}")
        raise HttpError(500, "Record creation error")


@bucket_router.put("/update/{bucket_id}", auth=FullAccessAuth())
def update_bucket(request, bucket_id: int, payload: BucketIn):
    """
    The function `update_bucket` updates the bucket specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        bucket_id (int): the id of the bucket to update
        payload (BucketIn): a bucket object

    Returns:
        success: True

    Raises:
        Http404: If the bucket with the specified ID does not exist.
    """

    try:
        bucket = get_object_or_404(Bucket, id=bucket_id)
        bucket.name = payload.name
        bucket.contribution_per_paycheck = payload.contribution_per_paycheck
        bucket.minimum_per_paycheck = payload.minimum_per_paycheck
        bucket.buffer = payload.buffer
        bucket.mode = payload.mode
        bucket.minimum_balance = payload.minimum_balance
        bucket.goal_amount = payload.goal_amount
        bucket.goal_date = payload.goal_date
        bucket.sweep_share = payload.sweep_share
        bucket.priority = payload.priority
        bucket.lendable = payload.lendable
        bucket.receives_rewards = payload.receives_rewards
        bucket.active = payload.active
        bucket.account_id = payload.account_id
        bucket.reminder_id = payload.reminder_id

        bucket.full_clean(exclude=["name"])
        bucket.save()
        bucket.budgets.set(Budget.objects.filter(id__in=payload.budget_ids))
        bucket.scope_tags.set(Tag.objects.filter(id__in=payload.scope_tag_ids))
        bucket.scope_main_tags.set(
            MainTag.objects.filter(id__in=payload.scope_main_tag_ids)
        )
        api_logger.info(f"Bucket updated : {bucket.name}")
        return {"success": True}
    except Http404:
        raise HttpError(404, "Bucket not found")
    except ValidationError as validation_error:
        api_logger.error(
            f"Bucket not updated : invalid ({validation_error.messages})"
        )
        raise HttpError(400, "; ".join(validation_error.messages))
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Bucket not updated : bucket exists ({payload.name})"
            )
            error_logger.exception(
                f"Bucket not updated : bucket exists ({payload.name})"
            )
            raise HttpError(400, "Bucket already exists")
        else:
            # Log other types of integry errors
            api_logger.error("Bucket not updated : db integrity error")
            error_logger.exception("Bucket not updated : db integrity error")
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Bucket not updated")
        error_logger.exception(f"{str(e)}")
        raise HttpError(500, "Record update error")


@bucket_router.get("/get/{bucket_id}", response=BucketOut)
def get_bucket(request, bucket_id: int):
    """
    The function `get_bucket` retrieves the bucket by id

    Args:
        request (HttpRequest): The HTTP request object.
        bucket_id (int): The id of the bucket to retrieve.

    Returns:
        BucketOut: the bucket object

    Raises:
        Http404: If the bucket with the specified ID does not exist.
    """

    try:
        bucket = get_object_or_404(Bucket, id=bucket_id)
        api_logger.debug(
            f"Bucket retrieved : {bucket.name}"
        )
        return bucket
    except Http404:
        raise HttpError(404, "Bucket not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Bucket not retrieved")
        error_logger.exception(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error: {str(e)}")


@bucket_router.get("/list", response=BucketsWithTotals)
def list_buckets(request):
    """
    The function `list_buckets` retrieves a list of buckets,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        BucketOut: a list of bucket objects
    """

    try:
        qs = Bucket.objects.all().order_by("-active", "id")
        active_buckets = qs.filter(active=True)

        # Compute totals (this can be customized based on your business logic)
        per_paycheck_total = sum(
            [bucket.contribution_per_paycheck for bucket in active_buckets]
        )
        # The emergency plan, derived rather than stored. What each bucket
        # may not go below, and what that frees up to refill the emergency fund.
        emergency_paycheck_total = sum(
            [
                bucket.minimum_per_paycheck
                if bucket.minimum_per_paycheck is not None
                else bucket.contribution_per_paycheck
                for bucket in active_buckets
            ]
        )
        total_emergency = sum(
            [
                bucket.contribution_per_paycheck
                - (
                    bucket.minimum_per_paycheck
                    if bucket.minimum_per_paycheck is not None
                    else bucket.contribution_per_paycheck
                )
                for bucket in active_buckets
            ]
        )

        # Create the BucketsWithTotals object
        buckets_with_totals = BucketsWithTotals(
            buckets=list(qs),
            per_paycheck_total=per_paycheck_total,
            emergency_paycheck_total=emergency_paycheck_total,
            total_emergency=total_emergency,
        )
        api_logger.debug("Bucket list retrieved")
        return buckets_with_totals
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Bucket list not retrieved")
        error_logger.exception(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error: {str(e)}")


@bucket_router.delete("/delete/{bucket_id}", auth=FullAccessAuth())
def delete_bucket(request, bucket_id: int):
    """
    The function `delete_bucket` deletes the bucket specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        bucket_id (int): the id of the bucket to delete

    Returns:
        success: True

    Raises:
        Http404: If the bucket with the specified ID does not exist.
    """

    try:
        bucket = get_object_or_404(Bucket, id=bucket_id)
        bucket_name = bucket.name
        bucket.delete()
        api_logger.info(f"Bucket deleted : {bucket_name}")
        return {"success": True}
    except Http404:
        raise HttpError(404, "Bucket not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Bucket not deleted")
        error_logger.exception(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")
