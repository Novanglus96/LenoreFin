import gzip
import json
from decimal import Decimal

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
    from planning.models import Bucket, WindfallRule, Note
    from reminders.models import ReminderExclusion

    DescriptionHistory.objects.create(
        description_normalized="grocery store",
        description_pretty="Grocery Store",
        tag=test_tag,
    )
    Reward.objects.create(reward_amount="50.00", reward_account=test_checking_account)
    WindfallRule.objects.create(rule="401k", cap="5000", order=1)
    Bucket.objects.create(
        name="HSA",
        contribution_per_paycheck="50.00",
        minimum_per_paycheck="0.00",
        target_balance="3600.00",
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
    assert WindfallRule.objects.filter(rule="401k").exists()
    assert Bucket.objects.filter(name="HSA").exists()
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


@pytest.mark.django_db
def test_roundtrip_bucket_planner_fields(
    tmp_path, test_checking_account, test_savings_account,
    test_tag, test_repeat, test_expense_transaction_type,
):
    """A bucket's account, reminder link and target all survive a round trip.

    The reminder link is the one that can silently break: it is exported as the
    source pk and has to come back through reminder_id_map, not as a raw id.
    """
    from planning.models import Bucket
    from reminders.models import Reminder

    reminder = Reminder.objects.create(
        tag=test_tag,
        amount="200.00",
        reminder_source_account=test_checking_account,
        reminder_destination_account=test_savings_account,
        description="House Transfer",
        transaction_type=test_expense_transaction_type,
        repeat=test_repeat,
        auto_add=False,
    )
    Bucket.objects.create(
        name="House",
        contribution_per_paycheck="200.00",
        minimum_per_paycheck="25.00",
        target_balance="5000.00",
        target_date="2027-06-01",
        priority=5,
        lendable=False,
        sweep_share=3,
        receives_rewards=True,
        active=True,
        account=test_savings_account,
        reminder=reminder,
    )

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)
    call_command("import_user_data", output)

    restored = Bucket.objects.get(name="House")
    assert restored.account is not None
    assert restored.account.account_name == test_savings_account.account_name
    assert restored.reminder is not None
    assert restored.reminder.description == "House Transfer"
    # The remapped reminder must be the restored one, not a dangling source pk.
    assert restored.reminder_id == Reminder.objects.get(
        description="House Transfer"
    ).id
    assert str(restored.target_balance) == "5000.00"
    assert str(restored.target_date) == "2027-06-01"
    assert str(restored.minimum_per_paycheck) == "25.00"
    assert restored.priority == 5
    # Losing this on restore would quietly re-open an account the user had
    # marked untouchable, and the planner would start borrowing from it again.
    assert restored.lendable is False
    assert restored.sweep_share == 3
    assert restored.receives_rewards is True


@pytest.mark.django_db
def test_roundtrip_budget_parent(tmp_path, test_checking_account, test_tag):
    """A budget hierarchy survives, linked by name.

    Restored the wrong way round, a parent would total nothing and its children
    would each start funding themselves again — the double count the hierarchy
    exists to prevent, reintroduced by a restore.
    """
    import json

    from planning.models import Budget

    parent = Budget.objects.create(
        name="Christmas", amount="0.00", tag_ids=json.dumps([test_tag.pk])
    )
    Budget.objects.create(
        name="Christmas - John",
        amount="100.00",
        tag_ids=json.dumps([test_tag.pk]),
        parent=parent,
    )

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)
    call_command("import_user_data", output)

    restored_parent = Budget.objects.get(name="Christmas")
    restored_child = Budget.objects.get(name="Christmas - John")
    assert restored_child.parent_id == restored_parent.pk
    assert restored_parent.parent_id is None


@pytest.mark.django_db
def test_roundtrip_bucket_tags(tmp_path, test_checking_account, test_tag):
    """Tags carry by slug, not by pk.

    Primary keys are not stable across an export/import cycle, and a
    bucket that came back linked to whatever tag happened to land on that
    pk would fund the wrong spending — silently, since the number would still
    look plausible.
    """
    from planning.models import Bucket
    from tags.models import Tag

    bucket = Bucket.objects.create(
        name="Gifts", contribution_per_paycheck="45.00", active=True
    )
    bucket.scope_tags.set([test_tag])

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)
    call_command("import_user_data", output)

    restored = Bucket.objects.get(name="Gifts")
    assert [t.slug for t in restored.scope_tags.all()] == [test_tag.slug]
    assert restored.scope_tags.first().pk == Tag.objects.get(slug=test_tag.slug).pk


@pytest.mark.django_db
def test_import_reads_the_pre_bucket_spelling(tmp_path, test_tag):
    """Every backup written before the rename says `contributions`.

    Including the production snapshot this dev database was built from. The
    rename was vocabulary only, so a file written under the old names has to
    restore into buckets unchanged — otherwise renaming the model would have
    quietly destroyed every existing backup.
    """
    from planning.models import Bucket, WindfallRule

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)
    with gzip.open(output, "rb") as f:
        data = json.loads(f.read())

    # Rewrite the planner section the way the old exporter wrote it.
    data.pop("buckets", None)
    data.pop("windfall_rules", None)
    data["contributions"] = [
        {
            "contribution": "Gifts",
            "per_paycheck": "45.00",
            "active": True,
            "tag_slugs": [test_tag.slug],
        }
    ]
    data["contrib_rules"] = [
        {"rule": "Split anything over 500", "cap": "Until projects complete", "order": 1}
    ]
    legacy = str(tmp_path / "legacy.json.gz")
    with gzip.open(legacy, "wb") as f:
        f.write(json.dumps(data).encode())

    call_command("import_user_data", legacy)

    restored = Bucket.objects.get(name="Gifts")
    assert restored.contribution_per_paycheck == Decimal("45.00")
    assert [t.slug for t in restored.scope_tags.all()] == [test_tag.slug]
    assert WindfallRule.objects.get(rule="Split anything over 500").order == 1


@pytest.mark.django_db
def test_roundtrip_bucket_without_planner_fields(
    tmp_path, test_checking_account,
):
    """A bucket with no account, reminder or target still round trips.

    This is the shape every pre-planner backup has, so it must not raise.
    """
    from planning.models import Bucket

    Bucket.objects.create(
        name="HSA",
        contribution_per_paycheck="50.00",
        minimum_per_paycheck="0.00",
        target_balance="0.00",
        active=True,
    )

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)
    call_command("import_user_data", output)

    restored = Bucket.objects.get(name="HSA")
    assert restored.account is None
    assert restored.reminder is None
    assert restored.target_balance is None
    assert restored.sweep is False
    # A backup taken before bridging existed says nothing about lending, and
    # the safe reading of silence is the default.
    assert restored.lendable is True


# ---------------------------------------------------------------------------
# Version check
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_export_includes_app_version(tmp_path):
    """Exported backup includes the current app version."""
    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)

    with gzip.open(output, "rb") as f:
        data = json.loads(f.read())

    assert "app_version" in data
    assert data["app_version"]  # non-empty string


@pytest.mark.django_db
def test_import_no_version_warning_when_versions_match(tmp_path, test_checking_account):
    """No VERSION_WARNING is written when backup and app share the same major.minor."""
    from io import StringIO

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)

    out = StringIO()
    call_command("import_user_data", output, stdout=out)
    assert "VERSION_WARNING" not in out.getvalue()


@pytest.mark.django_db
def test_import_version_warning_on_minor_mismatch(tmp_path, test_checking_account):
    """VERSION_WARNING is written when the backup major.minor differs from the current app."""
    from io import StringIO

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)

    # Patch the backup version to a different minor
    with gzip.open(output, "rb") as f:
        data = json.loads(f.read())
    data["app_version"] = "0.9.0"
    patched = str(tmp_path / "old.json.gz")
    with gzip.open(patched, "wb") as f:
        f.write(json.dumps(data).encode())

    out = StringIO()
    call_command("import_user_data", patched, stdout=out)
    assert "VERSION_WARNING" in out.getvalue()
    assert "0.9.0" in out.getvalue()


@pytest.mark.django_db
def test_import_version_warning_on_missing_version(tmp_path, test_checking_account):
    """VERSION_WARNING is written when the backup has no app_version field (pre-v1.4.0-alpha.37)."""
    from io import StringIO

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)

    with gzip.open(output, "rb") as f:
        data = json.loads(f.read())
    del data["app_version"]
    patched = str(tmp_path / "no_version.json.gz")
    with gzip.open(patched, "wb") as f:
        f.write(json.dumps(data).encode())

    out = StringIO()
    call_command("import_user_data", patched, stdout=out)
    assert "VERSION_WARNING" in out.getvalue()


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


# ---------------------------------------------------------------------------
# Round-trip: fields added after initial backup/restore implementation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_roundtrip_bank_logo_url(tmp_path, bank):
    """Bank.logo_url is exported and restored."""
    bank.logo_url = "https://icon.horse/icon/example.com"
    bank.save()

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)
    call_command("import_user_data", output)

    from accounts.models import Bank
    restored = Bank.objects.get(bank_name=bank.bank_name)
    assert restored.logo_url == "https://icon.horse/icon/example.com"


@pytest.mark.django_db
def test_roundtrip_parent_account(tmp_path, bank, checking_account_type, savings_account_type):
    """Account.parent_account self-referential FK is correctly restored."""
    from accounts.models import Account

    parent = Account.objects.create(
        account_name="Parent Savings",
        account_type=savings_account_type,
        bank=bank,
        opening_balance="1000.00",
    )
    Account.objects.create(
        account_name="Child Savings",
        account_type=savings_account_type,
        bank=bank,
        opening_balance="500.00",
        parent_account=parent,
    )

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)
    call_command("import_user_data", output)

    restored_child = Account.objects.get(account_name="Child Savings")
    assert restored_child.parent_account is not None
    assert restored_child.parent_account.account_name == "Parent Savings"


@pytest.mark.django_db
def test_roundtrip_interest_child_account(tmp_path, bank, checking_account_type, savings_account_type):
    """Account.interest_child_account FK is correctly restored."""
    from accounts.models import Account

    parent = Account.objects.create(
        account_name="Interest Parent",
        account_type=savings_account_type,
        bank=bank,
        opening_balance="5000.00",
    )
    child = Account.objects.create(
        account_name="Interest Child",
        account_type=savings_account_type,
        bank=bank,
        opening_balance="0.00",
        parent_account=parent,
    )
    parent.interest_child_account = child
    parent.save()

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)
    call_command("import_user_data", output)

    restored_parent = Account.objects.get(account_name="Interest Parent")
    assert restored_parent.interest_child_account is not None
    assert restored_parent.interest_child_account.account_name == "Interest Child"


@pytest.mark.django_db
def test_roundtrip_transaction_detail_full_toggle(
    tmp_path, test_checking_account, test_tag,
    test_pending_transaction_status, test_expense_transaction_type,
):
    """TransactionDetail.full_toggle is preserved through export/import."""
    from transactions.models import Transaction, TransactionDetail

    txn = Transaction.objects.create(
        description="Full Toggle Expense",
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        total_amount="200.00",
    )
    TransactionDetail.objects.create(
        transaction=txn, detail_amt="200.00", tag=test_tag, full_toggle=True
    )

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)
    call_command("import_user_data", output)

    restored_txn = Transaction.objects.get(description="Full Toggle Expense")
    detail = TransactionDetail.objects.get(transaction=restored_txn)
    assert detail.full_toggle is True


@pytest.mark.django_db
def test_roundtrip_report_config(
    tmp_path, test_checking_account, test_tag, test_main_tag, test_sub_tag,
):
    """ReportConfig with tag selections and account filters is fully restored."""
    from reports.models import ReportConfig, ReportConfigTag

    rc = ReportConfig.objects.create(
        name="My Annual Report",
        description="Year over year comparison",
        report_type="COMPARISON",
        date_range_type="THIS_YEAR",
        group_by="TAG",
        show_transactions=True,
        show_subtotal=True,
        include_pending=False,
    )
    rc.accounts.add(test_checking_account)
    ReportConfigTag.objects.create(report=rc, tag=test_tag)
    ReportConfigTag.objects.create(report=rc, main_tag=test_main_tag)

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)
    call_command("import_user_data", output)

    restored = ReportConfig.objects.get(name="My Annual Report")
    assert restored.report_type == "COMPARISON"
    assert restored.group_by == "TAG"
    assert restored.show_transactions is True
    assert restored.accounts.filter(account_name=test_checking_account.account_name).exists()

    selections = list(restored.tag_selections.all())
    assert len(selections) == 2
    tag_slugs = {s.tag.slug for s in selections if s.tag_id}
    main_slugs = {s.main_tag.slug for s in selections if s.main_tag_id}
    assert test_tag.slug in tag_slugs
    assert test_main_tag.slug in main_slugs


@pytest.mark.django_db
def test_roundtrip_custom_repeat(tmp_path):
    """User-created (non-system) Repeat is exported, cleared, and re-created on import."""
    from reminders.models import Repeat

    custom = Repeat.objects.create(
        repeat_name="Bi-weekly",
        days=0,
        weeks=2,
        months=0,
        years=0,
    )
    slug = custom.slug

    output = str(tmp_path / "backup.json.gz")
    call_command("export_user_data", output=output)

    # Verify the export contains the custom repeat
    with gzip.open(output, "rb") as f:
        exported = json.loads(f.read())
    assert any(r["slug"] == slug for r in exported.get("custom_repeats", []))

    call_command("import_user_data", output)

    restored = Repeat.objects.get(slug=slug)
    assert restored.repeat_name == "Bi-weekly"
    assert restored.weeks == 2
    assert restored.is_system is False
