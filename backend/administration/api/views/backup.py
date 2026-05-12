from ninja import Router, UploadedFile, File
from ninja.errors import HttpError
from administration.models import BackupConfig
from administration.api.schemas.backup import BackupConfigOut, BackupConfigIn, BackupFileOut
from administration.api.dependencies.auth import FullAccessAuth
from django.conf import settings
from django.core.management import call_command
from django.http import FileResponse
from typing import List
from datetime import datetime
import os
import logging
import tempfile

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")

backup_router = Router(tags=["Backup"])


def _backup_location():
    return settings.DBBACKUP_STORAGE_OPTIONS.get("location", "/backups/")


def _list_backup_files():
    location = _backup_location()
    if not os.path.exists(location):
        return []
    files = []
    for filename in os.listdir(location):
        filepath = os.path.join(location, filename)
        if not os.path.isfile(filepath):
            continue
        if not (filename.endswith(".json.gz") or filename.endswith(".json")):
            continue
        stat = os.stat(filepath)
        files.append(
            BackupFileOut(
                filename=filename,
                size=stat.st_size,
                created_at=datetime.fromtimestamp(stat.st_mtime),
                backup_type="database",
            )
        )
    files.sort(key=lambda f: f.created_at, reverse=True)
    return files


@backup_router.get("/config", response=BackupConfigOut)
def get_backup_config(request):
    try:
        config = BackupConfig.load()
        return config
    except Exception as e:
        error_logger.exception(f"Error retrieving backup config: {e}")
        raise HttpError(500, "Error retrieving backup config")


@backup_router.patch("/config", response=BackupConfigOut, auth=FullAccessAuth())
def update_backup_config(request, payload: BackupConfigIn):
    try:
        config = BackupConfig.load()
        for attr, value in payload.dict(exclude_none=True).items():
            setattr(config, attr, value)
        config.save()
        _reschedule_backup(config)
        return config
    except Exception as e:
        error_logger.exception(f"Error updating backup config: {e}")
        raise HttpError(500, "Error updating backup config")


@backup_router.get("/files", response=List[BackupFileOut])
def list_backups(request):
    try:
        return _list_backup_files()
    except Exception as e:
        error_logger.exception(f"Error listing backups: {e}")
        raise HttpError(500, "Error listing backups")


@backup_router.post("/run", auth=FullAccessAuth())
def run_backup(request):
    try:
        from django_q.tasks import async_task
        async_task("transactions.tasks.create_backup")
        api_logger.info("Manual backup triggered")
        return {"success": True}
    except Exception as e:
        error_logger.exception(f"Error triggering backup: {e}")
        raise HttpError(500, "Error triggering backup")


@backup_router.get("/files/{filename}/download")
def download_backup(request, filename: str):
    try:
        location = _backup_location()
        filepath = os.path.join(location, filename)
        if not os.path.exists(filepath):
            raise HttpError(404, "Backup file not found")
        # Prevent path traversal
        if not os.path.abspath(filepath).startswith(os.path.abspath(location)):
            raise HttpError(400, "Invalid filename")
        return FileResponse(open(filepath, "rb"), as_attachment=True, filename=filename)
    except HttpError:
        raise
    except Exception as e:
        error_logger.exception(f"Error downloading backup {filename}: {e}")
        raise HttpError(500, "Error downloading backup")


@backup_router.delete("/files/{filename}", auth=FullAccessAuth())
def delete_backup(request, filename: str):
    try:
        location = _backup_location()
        filepath = os.path.join(location, filename)
        if not os.path.exists(filepath):
            raise HttpError(404, "Backup file not found")
        if not os.path.abspath(filepath).startswith(os.path.abspath(location)):
            raise HttpError(400, "Invalid filename")
        os.remove(filepath)
        api_logger.info(f"Backup deleted: {filename}")
        return {"success": True}
    except HttpError:
        raise
    except Exception as e:
        error_logger.exception(f"Error deleting backup {filename}: {e}")
        raise HttpError(500, "Error deleting backup")


@backup_router.post("/restore/database", auth=FullAccessAuth())
def restore_database(request, filename: str):
    try:
        location = _backup_location()
        filepath = os.path.join(location, filename)
        if not os.path.exists(filepath):
            raise HttpError(404, "Backup file not found")
        if not os.path.abspath(filepath).startswith(os.path.abspath(location)):
            raise HttpError(400, "Invalid filename")
        call_command("import_user_data", filepath)
        api_logger.info(f"Database restored from: {filename}")
        return {"success": True}
    except HttpError:
        raise
    except Exception as e:
        error_logger.exception(f"Error restoring database from {filename}: {e}")
        raise HttpError(500, f"Restore failed: {str(e)}")


@backup_router.post("/restore/upload", auth=FullAccessAuth())
def restore_from_upload(request, file: UploadedFile = File(...)):
    try:
        name = file.name or "upload.json.gz"
        suffix = ".json.gz" if name.endswith(".json.gz") else os.path.splitext(name)[1] or ".json.gz"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
        try:
            call_command("import_user_data", tmp_path)
            api_logger.info(f"Database restored from uploaded file: {file.name}")
            return {"success": True}
        finally:
            os.unlink(tmp_path)
    except HttpError:
        raise
    except Exception as e:
        error_logger.exception(f"Error restoring from upload: {e}")
        raise HttpError(500, f"Restore failed: {str(e)}")


def _reschedule_backup(config):
    from django_q.models import Schedule
    from django.utils import timezone
    import pytz
    from datetime import timedelta

    tz = pytz.timezone(os.environ.get("TIMEZONE", "UTC"))
    today = timezone.now().astimezone(tz).date()
    tomorrow = today + timedelta(days=1)
    current_timezone = timezone.get_current_timezone()

    schedule_map = {
        "HOURLY": Schedule.HOURLY,
        "DAILY": Schedule.DAILY,
        "WEEKLY": Schedule.WEEKLY,
    }

    start_date = today if config.frequency == "HOURLY" else tomorrow
    next_run = datetime.combine(
        start_date, datetime.strptime(config.backup_time, "%H:%M").time()
    )
    next_run = tz.localize(next_run).astimezone(current_timezone)

    Schedule.objects.update_or_create(
        name="Backup Database",
        defaults={
            "func": "transactions.tasks.create_backup",
            "args": "",
            "schedule_type": schedule_map.get(config.frequency, Schedule.DAILY),
            "next_run": next_run,
        },
    )
