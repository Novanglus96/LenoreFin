import io
import math
import re
import zipfile
from typing import Optional

import logging
from django.conf import settings
from django.http import HttpResponse
from ninja import Router
from ninja.errors import HttpError

from administration.api.dependencies.auth import FullAccessAuth
from administration.api.schemas.logs import LogPageOut

error_logger = logging.getLogger("error")
api_logger = logging.getLogger("api")

logs_router = Router(tags=["Logs"])

VALID_LOG_TYPES = {"api", "error", "task"}
VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

# Matches the start of a new log entry: [timestamp] LEVEL ...
_LOG_LINE_RE = re.compile(r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)\] (\w+) (.*)")


def _parse_log_file(log_type: str) -> list:
    log_path = settings.LOG_DIR / f"{log_type}.log"
    if not log_path.exists():
        return []

    entries = []
    current = None

    with open(log_path, "r", errors="replace") as f:
        for line in f:
            m = _LOG_LINE_RE.match(line)
            if m:
                if current:
                    entries.append(current)
                current = {
                    "timestamp": m.group(1),
                    "level": m.group(2),
                    "message": m.group(3).rstrip(),
                }
            elif current:
                # Continuation line (e.g. traceback)
                current["message"] += "\n" + line.rstrip()

    if current:
        entries.append(current)

    return entries


@logs_router.get("", response=LogPageOut, auth=FullAccessAuth())
def get_logs(
    request,
    log_type: str = "error",
    page: int = 1,
    page_size: int = 100,
    level: Optional[str] = None,
    search: Optional[str] = None,
):
    if log_type not in VALID_LOG_TYPES:
        raise HttpError(400, f"Invalid log_type. Choose from: {', '.join(sorted(VALID_LOG_TYPES))}")

    selected_levels = set()
    if level:
        selected_levels = {lvl.strip().upper() for lvl in level.split(",")}
        invalid = selected_levels - VALID_LEVELS
        if invalid:
            raise HttpError(400, f"Invalid level(s): {', '.join(sorted(invalid))}. Choose from: {', '.join(sorted(VALID_LEVELS))}")

    try:
        entries = _parse_log_file(log_type)
        # Newest first
        entries = list(reversed(entries))

        if selected_levels:
            entries = [e for e in entries if e["level"] in selected_levels]
        if search:
            search_lower = search.lower()
            entries = [e for e in entries if search_lower in e["message"].lower()]

        total = len(entries)
        pages = max(1, math.ceil(total / page_size))
        page = max(1, min(page, pages))
        start = (page - 1) * page_size
        page_entries = entries[start : start + page_size]

        api_logger.info(f"Logs retrieved : type={log_type} page={page} total={total}")
        return {
            "entries": page_entries,
            "total": total,
            "page": page,
            "pages": pages,
            "log_type": log_type,
        }
    except Exception as e:
        error_logger.exception(f"Error reading logs: {e}")
        raise HttpError(500, "Error reading log file")


@logs_router.get("/bundle", auth=FullAccessAuth())
def download_log_bundle(request):
    try:
        log_dir = settings.LOG_DIR
        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for log_file in sorted(log_dir.glob("*.log*")):
                if log_file.is_file():
                    zf.write(log_file, log_file.name)

        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="lenorefin_logs.zip"'
        api_logger.info("Log bundle downloaded")
        return response
    except Exception as e:
        error_logger.exception(f"Error creating log bundle: {e}")
        raise HttpError(500, "Error creating log bundle")
