import pytest
import json
from django.core.files.uploadedfile import SimpleUploadedFile


AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_import_file_creates_file_import(
    api_client,
    test_checking_account,
    test_expense_transaction_type,
    test_pending_transaction_status,
    test_tag,
    tmp_path,
    settings,
):
    settings.MEDIA_ROOT = tmp_path

    csv_file = SimpleUploadedFile(
        "import.csv",
        b"id,amount,date\n1,100,2024-01-01\n",
        content_type="text/csv",
    )

    payload = {
        "transaction_types": [
            {
                "file_type": "Expense",
                "type_id": test_expense_transaction_type.id,
            }
        ],
        "transaction_statuses": [
            {
                "file_status": "Pending",
                "status_id": test_pending_transaction_status.id,
            }
        ],
        "accounts": [
            {
                "file_account": "Checking",
                "account_id": test_checking_account.id,
            }
        ],
        "tags": [
            {
                "file_tag": "Groceries",
                "tag_id": test_tag.id,
            }
        ],
        "transactions": [],
    }

    response = api_client.post(
        "/file-imports/create",
        data={"payload": json.dumps(payload)},
        FILES={"import_file": csv_file},
        headers=AUTH,
    )

    assert response.status_code == 200
    assert "id" in response.json()

    from imports.models import FileImport
    assert FileImport.objects.filter(id=response.json()["id"]).exists()
