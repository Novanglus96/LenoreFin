import gzip
import json
import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


# ---------------------------------------------------------------------------
# Export smoke tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_export_creates_gz_file(tmp_path):
    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)

    with gzip.open(output, "rb") as f:
        data = json.loads(f.read())

    for key in ("payees", "banks", "accounts", "transactions", "reminders", "budgets"):
        assert key in data


@pytest.mark.django_db
def test_export_includes_user_data(tmp_path, test_payee, test_checking_account, test_tag):
    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)

    with gzip.open(output, "rb") as f:
        data = json.loads(f.read())

    assert any(p["payee_name"] == test_payee.payee_name for p in data["payees"])
    assert any(a["account_name"] == test_checking_account.account_name for a in data["accounts"])
    # User-created tag is present; slug is stored as a natural key
    assert any(t["slug"] == test_tag.slug for t in data["tags"])


@pytest.mark.django_db
def test_export_stores_system_fks_as_slugs(
    tmp_path, test_checking_account, test_transaction,
    test_pending_transaction_status, test_expense_transaction_type,
):
    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)

    with gzip.open(output, "rb") as f:
        data = json.loads(f.read())

    txn = next(t for t in data["transactions"] if t["description"] == test_transaction.description)
    assert txn["status_slug"] == test_pending_transaction_status.slug
    assert txn["transaction_type_slug"] == test_expense_transaction_type.slug

    account = next(a for a in data["accounts"] if a["account_name"] == test_checking_account.account_name)
    assert account["account_type_slug"] == test_checking_account.account_type.slug


# ---------------------------------------------------------------------------
# Round-trip: full export → import
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_roundtrip_restores_all_core_models(
    tmp_path,
    test_payee,
    test_checking_account,
    test_savings_account,
    test_tag,
    test_transaction,
    test_paycheck,
    test_reminder,
):
    from accounts.models import Account, Bank, Reward
    from administration.models import DescriptionHistory
    from planning.models import Contribution, ContribRule, Note
    from reminders.models import ReminderExclusion

    DescriptionHistory.objects.create(
        description_normalized="grocery store",
        description_pretty="Grocery Store",
        tag=test_tag,
    )
    Reward.objects.create(reward_amount="50.00", reward_account=test_checking_account)
    ContribRule.objects.create(rule="401k", cap="5000", order=1)
    Contribution.objects.create(
        contribution="HSA",
        per_paycheck="50.00",
        emergency_amt="0.00",
        emergency_diff="0.00",
        cap="3600.00",
        active=True,
    )
    Note.objects.create(note_text="Check budget monthly")
    ReminderExclusion.objects.create(reminder=test_reminder, exclude_date="2025-01-01")

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)
    call_command("import_user_data", output)

    from transactions.models import Transaction, Paycheck

    assert Account.objects.filter(account_name=test_checking_account.account_name).exists()
    assert Account.objects.filter(account_name=test_savings_account.account_name).exists()
    assert Bank.objects.filter(bank_name=test_checking_account.bank.bank_name).exists()
    assert DescriptionHistory.objects.filter(description_normalized="grocery store").exists()
    assert Reward.objects.filter(reward_amount="50.00").exists()
    assert Paycheck.objects.filter(gross=test_paycheck.gross).exists()
    assert Transaction.objects.filter(description=test_transaction.description).exists()
    assert ContribRule.objects.filter(rule="401k").exists()
    assert Contribution.objects.filter(contribution="HSA").exists()
    assert Note.objects.filter(note_text="Check budget monthly").exists()
    assert ReminderExclusion.objects.filter(exclude_date="2025-01-01").exists()


@pytest.mark.django_db
def test_roundtrip_remaps_transaction_detail_tag(
    tmp_path, test_checking_account, test_tag,
    test_pending_transaction_status, test_expense_transaction_type,
):
    """TransactionDetail.tag FK points to the re-created Tag after import."""
    from transactions.models import Transaction, TransactionDetail
    from tags.models import Tag

    txn = Transaction.objects.create(
        description="Tagged Expense",
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        total_amount="75.00",
    )
    TransactionDetail.objects.create(transaction=txn, detail_amt="75.00", tag=test_tag)

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)
    call_command("import_user_data", output)

    restored_tag = Tag.objects.get(slug=test_tag.slug)
    restored_txn = Transaction.objects.get(description="Tagged Expense")
    detail = TransactionDetail.objects.get(transaction=restored_txn)
    assert detail.tag_id == restored_tag.pk


@pytest.mark.django_db
def test_roundtrip_remaps_paycheck_link(
    tmp_path, test_checking_account, test_payee,
    test_pending_transaction_status, test_expense_transaction_type,
):
    """Transaction.paycheck is remapped to the new Paycheck record after import."""
    from transactions.models import Paycheck, Transaction

    pc = Paycheck.objects.create(
        gross="3000.00", net="2500.00", taxes="500.00",
        health="0", pension="0", fsa="0", dca="0",
        union_dues="0", four_fifty_seven_b="0", payee=test_payee,
    )
    Transaction.objects.create(
        description="Paycheck Deposit",
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        paycheck=pc,
    )

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)
    call_command("import_user_data", output)

    restored = Transaction.objects.get(description="Paycheck Deposit")
    assert restored.paycheck is not None
    assert str(restored.paycheck.gross) == "3000.00"


@pytest.mark.django_db
def test_roundtrip_funding_account(tmp_path, bank, checking_account_type, credit_card_account_type):
    """Account.funding_account self-referential FK is correctly restored (two-pass import)."""
    from accounts.models import Account

    checking = Account.objects.create(
        account_name="My Checking",
        account_type=checking_account_type,
        bank=bank,
        opening_balance="1000.00",
    )
    Account.objects.create(
        account_name="My CC",
        account_type=credit_card_account_type,
        bank=bank,
        opening_balance="0.00",
        funding_account=checking,
    )

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)
    call_command("import_user_data", output)

    restored_cc = Account.objects.get(account_name="My CC")
    assert restored_cc.funding_account is not None
    assert restored_cc.funding_account.account_name == "My Checking"


@pytest.mark.django_db
def test_roundtrip_budget_tag_ids_converted(tmp_path, test_checking_account, test_tag):
    """Budget.tag_ids PK array is converted to slugs on export and back to new PKs on import."""
    from planning.models import Budget
    from tags.models import Tag

    Budget.objects.create(
        tag_ids=json.dumps([test_tag.pk]),
        name="Groceries Budget",
        amount="500.00",
        roll_over=True,
        start_day="2025-01-01",
        roll_over_amt="0.00",
        next_start="2025-02-01",
    )

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)

    # Verify the export stored slugs, not PKs
    with gzip.open(output, "rb") as f:
        exported = json.loads(f.read())
    budget_data = next(b for b in exported["budgets"] if b["name"] == "Groceries Budget")
    assert json.loads(budget_data["tag_ids"]) == [test_tag.slug]

    call_command("import_user_data", output)

    restored_tag = Tag.objects.get(slug=test_tag.slug)
    restored_budget = Budget.objects.get(name="Groceries Budget")
    assert json.loads(restored_budget.tag_ids) == [restored_tag.pk]


@pytest.mark.django_db
def test_roundtrip_reminder_maps(
    tmp_path, test_checking_account, test_savings_account,
    test_tag, test_repeat,
    test_expense_transaction_type,
):
    """Reminder FKs (tag, accounts, transaction_type, repeat) are all restored correctly."""
    from reminders.models import Reminder

    Reminder.objects.create(
        tag=test_tag,
        amount="100.00",
        reminder_source_account=test_checking_account,
        reminder_destination_account=test_savings_account,
        description="Monthly Transfer",
        transaction_type=test_expense_transaction_type,
        repeat=test_repeat,
        auto_add=False,
    )

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)
    call_command("import_user_data", output)


    restored = Reminder.objects.get(description="Monthly Transfer")
    assert restored.tag is not None
    assert restored.tag.slug == test_tag.slug
    assert restored.reminder_source_account.account_name == test_checking_account.account_name
    assert restored.reminder_destination_account.account_name == test_savings_account.account_name
    assert restored.repeat.slug == test_repeat.slug


# ---------------------------------------------------------------------------
# Atomic rollback
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_import_raises_for_missing_file():
    with pytest.raises(CommandError, match="File not found"):
        call_command("import_user_data", "/nonexistent/backup.json.gz")


@pytest.mark.django_db
def test_import_rollback_on_restore_failure(tmp_path, test_checking_account):
    """If restore fails mid-import, the clear is rolled back atomically."""
    from accounts.models import Account

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)

    # Corrupt the backup: account references a bank not in the banks list
    with gzip.open(output, "rb") as f:
        data = json.loads(f.read())
    data["accounts"][0]["bank_name"] = "__nonexistent_bank__"
    data["banks"] = [b for b in data["banks"] if b["bank_name"] != "__nonexistent_bank__"]

    corrupt = str(tmp_path / "corrupt.json.gz")
    with gzip.open(corrupt, "wb") as f:
        f.write(json.dumps(data).encode())

    original_count = Account.objects.count()

    with pytest.raises(Exception):
        call_command("import_user_data", corrupt)

    # Clear was rolled back — accounts are still present
    assert Account.objects.count() == original_count
