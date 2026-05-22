import gzip
import json
import os
import pytest
from unittest.mock import patch
from django.test import override_settings


AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.fixture
def backup_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def backup_settings(backup_dir):
    return override_settings(DBBACKUP_STORAGE_OPTIONS={"location": backup_dir})


@pytest.fixture
def sample_backup_file(backup_dir):
    """Create a minimal valid .json.gz backup in the temp dir."""
    data = {
        "payees": [], "banks": [], "main_tags": [], "sub_tags": [], "tags": [],
        "accounts": [], "description_history": [], "rewards": [], "paychecks": [],
        "transactions": [], "transaction_details": [], "reminders": [],
        "reminder_exclusions": [], "contrib_rules": [], "contributions": [],
        "notes": [], "christmas_gifts": [], "budgets": [], "calculation_rules": [],
        "backup_config": {"backup_enabled": True, "frequency": "DAILY",
                          "backup_time": "02:00", "copies_to_keep": 2},
    }
    filename = "lenorefin-backup-2025-01-01-120000.json.gz"
    filepath = os.path.join(backup_dir, filename)
    with gzip.open(filepath, "wb") as f:
        f.write(json.dumps(data).encode())
    return filename


# ---------------------------------------------------------------------------
# Config endpoints
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.api
def test_get_backup_config(api_client):
    response = api_client.get("/administration/backups/config", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert "backup_enabled" in data
    assert "frequency" in data
    assert "backup_time" in data
    assert "copies_to_keep" in data


@pytest.mark.django_db
@pytest.mark.api
def test_update_backup_config(api_client):
    response = api_client.patch(
        "/administration/backups/config",
        json={"frequency": "WEEKLY", "copies_to_keep": 5},
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["frequency"] == "WEEKLY"
    assert data["copies_to_keep"] == 5

    from administration.models import BackupConfig
    config = BackupConfig.load()
    assert config.frequency == "WEEKLY"
    assert config.copies_to_keep == 5


# ---------------------------------------------------------------------------
# File listing
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.api
def test_list_backups_empty(api_client, backup_settings, backup_dir):
    with backup_settings:
        response = api_client.get("/administration/backups/files", headers=AUTH)

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
@pytest.mark.api
def test_list_backups_returns_json_gz_files(api_client, backup_settings, sample_backup_file):
    with backup_settings:
        response = api_client.get("/administration/backups/files", headers=AUTH)

    assert response.status_code == 200
    files = response.json()
    assert len(files) == 1
    assert files[0]["filename"] == sample_backup_file
    assert files[0]["backup_type"] == "database"
    assert files[0]["size"] > 0


@pytest.mark.django_db
@pytest.mark.api
def test_list_backups_ignores_non_json_gz(api_client, backup_settings, backup_dir):
    # Write a file that should be ignored
    open(os.path.join(backup_dir, "somefile.dump"), "w").close()
    with backup_settings:
        response = api_client.get("/administration/backups/files", headers=AUTH)

    assert response.status_code == 200
    assert response.json() == []


# ---------------------------------------------------------------------------
# Run backup
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.api
def test_run_backup_queues_async_task(api_client):
    with patch("django_q.tasks.async_task") as mock_task:
        response = api_client.post("/administration/backups/run", headers=AUTH)

    assert response.status_code == 200
    assert response.json()["success"] is True
    mock_task.assert_called_once_with("transactions.tasks.create_backup")


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.api
def test_download_backup(api_client, backup_settings, backup_dir, sample_backup_file):
    with backup_settings:
        response = api_client.get(
            f"/administration/backups/files/{sample_backup_file}/download",
            headers=AUTH,
        )

    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.api
def test_download_backup_not_found(api_client, backup_settings):
    with backup_settings:
        response = api_client.get(
            "/administration/backups/files/nonexistent.json.gz/download",
            headers=AUTH,
        )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_download_backup_path_traversal_rejected(api_client, backup_settings):
    with backup_settings:
        response = api_client.get(
            "/administration/backups/files/..%2F..%2Fetc%2Fpasswd/download",
            headers=AUTH,
        )

    assert response.status_code in (400, 404)


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.api
def test_delete_backup(api_client, backup_settings, backup_dir, sample_backup_file):
    filepath = os.path.join(backup_dir, sample_backup_file)
    assert os.path.exists(filepath)

    with backup_settings:
        response = api_client.delete(
            f"/administration/backups/files/{sample_backup_file}",
            headers=AUTH,
        )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert not os.path.exists(filepath)


@pytest.mark.django_db
@pytest.mark.api
def test_delete_backup_not_found(api_client, backup_settings):
    with backup_settings:
        response = api_client.delete(
            "/administration/backups/files/nonexistent.json.gz",
            headers=AUTH,
        )

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Restore from stored file
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.api
def test_restore_database(api_client, backup_settings, sample_backup_file):
    with backup_settings:
        with patch("administration.api.views.backup.call_command") as mock_cmd:
            response = api_client.post(
                f"/administration/backups/restore/database?filename={sample_backup_file}",
                headers=AUTH,
            )

    assert response.status_code == 200
    assert response.json()["success"] is True
    mock_cmd.assert_called_once()
    assert mock_cmd.call_args[0][0] == "import_user_data"


@pytest.mark.django_db
@pytest.mark.api
def test_restore_database_file_not_found(api_client, backup_settings):
    with backup_settings:
        response = api_client.post(
            "/administration/backups/restore/database?filename=missing.json.gz",
            headers=AUTH,
        )

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Restore from upload
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.api
def test_restore_upload(api_client):
    from django.core.files.uploadedfile import SimpleUploadedFile

    uploaded = SimpleUploadedFile("backup.json.gz", b"fake backup content", content_type="application/gzip")
    with patch("administration.api.views.backup.call_command") as mock_cmd:
        response = api_client.post(
            "/administration/backups/restore/upload",
            FILES={"file": uploaded},
            headers=AUTH,
        )

    assert response.status_code == 200
    assert response.json()["success"] is True
    mock_cmd.assert_called_once()
    assert mock_cmd.call_args[0][0] == "import_user_data"
