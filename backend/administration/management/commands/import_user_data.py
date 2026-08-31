import gzip
import json
import os
import re
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import transaction as db_transaction


def _optional_amount(value):
    """`cap` used 0 to mean "no cap"; `target_balance` says that as None.

    Restored as 0 it would read as "accumulate to nothing", which stops the
    bucket being funded at all.
    """
    if value is None:
        return None
    from decimal import Decimal

    try:
        amount = Decimal(str(value))
    except Exception:
        return None
    return None if amount == 0 else amount


class Command(BaseCommand):
    help = "Restore user data from a version-agnostic JSON backup (.json.gz)"

    def add_arguments(self, parser):
        parser.add_argument("input", type=str, help="Path to backup file (.json.gz or .json)")

    def handle(self, *args, **options):
        filepath = options["input"]
        if not os.path.exists(filepath):
            raise CommandError(f"File not found: {filepath}")

        self.stdout.write(f"Reading backup from: {filepath}")
        if filepath.endswith(".gz"):
            with gzip.open(filepath, "rb") as f:
                data = json.loads(f.read().decode("utf-8"))
        else:
            with open(filepath, "r") as f:
                data = json.load(f)

        self._check_version(data)

        # Disconnect signals that queue async cache tasks — they race with
        # load_caches and produce double forecast/reminder entries.
        from django.db.models.signals import post_save, post_delete
        from reminders.models import Reminder as ReminderModel
        from reminders.signals import (
            update_and_invalidate_cache_on_save as reminder_on_save,
            update_and_invalidate_cache_on_delete as reminder_on_delete,
        )
        from transactions.models import Transaction as TransactionModel
        from transactions.signals import (
            update_forecast_cache_on_save as txn_on_save,
            update_forecast_cache_on_delete as txn_on_delete,
        )
        post_save.disconnect(reminder_on_save, sender=ReminderModel)
        post_delete.disconnect(reminder_on_delete, sender=ReminderModel)
        post_save.disconnect(txn_on_save, sender=TransactionModel)
        post_delete.disconnect(txn_on_delete, sender=TransactionModel)

        try:
            self.stdout.write("Starting restore (atomic)...")
            with db_transaction.atomic():
                self._clear_user_data()
                self._restore_data(data)
            call_command("load_caches")
        finally:
            post_save.connect(reminder_on_save, sender=ReminderModel)
            post_delete.connect(reminder_on_delete, sender=ReminderModel)
            post_save.connect(txn_on_save, sender=TransactionModel)
            post_delete.connect(txn_on_delete, sender=TransactionModel)

        self.stdout.write(self.style.SUCCESS("Restore completed successfully."))

    def _check_version(self, data):
        from administration.api.dependencies.version import get_version

        backup_version = data.get("app_version")
        current_version = get_version()

        if not backup_version:
            self.stdout.write(
                "VERSION_WARNING: Backup has no version information (created before v1.4.0-alpha.37). "
                "Verify all data restored correctly."
            )
            return

        def minor(v):
            m = re.match(r"(\d+\.\d+)", v)
            return m.group(1) if m else v

        if minor(backup_version) != minor(current_version):
            self.stdout.write(
                f"VERSION_WARNING: Backup was created on v{backup_version} but the app is "
                f"v{current_version}. Features added between versions may not be fully restored."
            )

    def _clear_user_data(self):
        from transactions.models import (
            TransactionDetail, Transaction, Paycheck,
            ReminderCacheTransaction, ForecastCacheTransaction,
        )
        from accounts.models import Account, Bank, Reward
        from administration.models import Payee, DescriptionHistory
        from reminders.models import Reminder, ReminderExclusion, Repeat
        from tags.models import Tag, MainTag, SubTag
        from planning.models import (
            WindfallRule, Bucket, Note, ChristmasGift,
            Budget, CalculationRule,
        )
        from reports.models import ReportConfig

        # Cache tables first (generated data, not user data)
        ForecastCacheTransaction.objects.all().delete()
        ReminderCacheTransaction.objects.all().delete()

        # Leaf records before parents
        TransactionDetail.objects.all().delete()
        Transaction.objects.all().delete()
        Paycheck.objects.all().delete()
        Reward.objects.all().delete()
        DescriptionHistory.objects.all().delete()
        ReminderExclusion.objects.all().delete()
        Reminder.objects.all().delete()
        Repeat.objects.filter(is_system=False).delete()

        ReportConfig.objects.all().delete()

        # Accounts: clear self-referential FKs before delete
        Account.objects.update(funding_account=None, parent_account=None, interest_child_account=None)
        Account.objects.all().delete()
        Bank.objects.all().delete()

        # User-created tags only; system tags remain (re-seeded by fixtures)
        Tag.objects.filter(is_system=False).delete()
        SubTag.objects.filter(is_system=False).delete()
        MainTag.objects.filter(is_system=False).delete()

        Payee.objects.all().delete()
        ChristmasGift.objects.all().delete()
        Budget.objects.all().delete()
        CalculationRule.objects.all().delete()
        Note.objects.all().delete()
        Bucket.objects.all().delete()
        WindfallRule.objects.all().delete()

        self.stdout.write("Cleared existing user data.")

    def _restore_data(self, data):
        from administration.models import Payee, DescriptionHistory, Option, BackupConfig, GraphType
        from accounts.models import AccountType, Bank, Account, AccountFavorite, Reward
        from django.contrib.auth import get_user_model
        User = get_user_model()
        from tags.models import TagType, MainTag, SubTag, Tag
        from transactions.models import (
            TransactionStatus, TransactionType,
            Transaction, Paycheck, TransactionDetail,
        )
        from reminders.models import Repeat, Reminder, ReminderExclusion
        from planning.models import WindfallRule, Bucket, Note, ChristmasGift, Budget, CalculationRule
        from reports.models import ReportConfig, ReportConfigTag

        # --- System lookup tables (slug → object) ---
        account_type_by_slug = {o.slug: o for o in AccountType.objects.all()}
        status_by_slug = {o.slug: o for o in TransactionStatus.objects.all()}
        ttype_by_slug = {o.slug: o for o in TransactionType.objects.all()}
        repeat_by_slug = {o.slug: o for o in Repeat.objects.all()}
        tag_type_by_slug = {o.slug: o for o in TagType.objects.all()}
        graph_type_by_slug = {o.slug: o for o in GraphType.objects.all()}

        def convert_slug_json_array(slug_str, slug_to_pk):
            """Convert JSON array of natural keys back to a JSON array of current PKs."""
            if not slug_str:
                return slug_str
            try:
                slug_list = json.loads(slug_str)
                if not isinstance(slug_list, list):
                    return slug_str
                return json.dumps([slug_to_pk.get(s, s) for s in slug_list])
            except (json.JSONDecodeError, TypeError):
                return slug_str

        # --- 1. Payees ---
        for item in data.get("payees", []):
            Payee.objects.create(payee_name=item["payee_name"])
        payee_by_name = {p.payee_name: p for p in Payee.objects.all()}

        # --- 2. Banks ---
        for item in data.get("banks", []):
            bank, created = Bank.objects.get_or_create(bank_name=item["bank_name"])
            if item.get("logo_url") and (created or not bank.logo_url):
                bank.logo_url = item["logo_url"]
                bank.save()
        bank_by_name = {b.bank_name: b for b in Bank.objects.all()}

        # --- 3. MainTags (user-created) ---
        # System tags loaded first; user tags added second so their old slugs
        # take precedence over system slugs when both share the same string.
        main_tag_by_slug = {mt.slug: mt for mt in MainTag.objects.filter(is_system=True)}
        for item in data.get("main_tags", []):
            mt = MainTag.objects.create(
                tag_name=item["tag_name"],
                tag_type=tag_type_by_slug.get(item["tag_type_slug"]) if item.get("tag_type_slug") else None,
            )
            main_tag_by_slug[item["slug"]] = mt

        # --- 4. SubTags (user-created) ---
        sub_tag_by_slug = {st.slug: st for st in SubTag.objects.filter(is_system=True)}
        for item in data.get("sub_tags", []):
            st = SubTag.objects.create(
                tag_name=item["tag_name"],
                tag_type=tag_type_by_slug.get(item["tag_type_slug"]) if item.get("tag_type_slug") else None,
            )
            sub_tag_by_slug[item["slug"]] = st

        # --- 5. Tags (user-created) ---
        tag_by_slug = {t.slug: t for t in Tag.objects.filter(is_system=True).select_related("parent", "child")}
        for item in data.get("tags", []):
            t = Tag.objects.create(
                parent=main_tag_by_slug.get(item["parent_slug"]) if item.get("parent_slug") else None,
                child=sub_tag_by_slug.get(item["child_slug"]) if item.get("child_slug") else None,
                tag_type=tag_type_by_slug.get(item["tag_type_slug"]) if item.get("tag_type_slug") else None,
            )
            tag_by_slug[item["slug"]] = t

        tag_slug_to_pk = {slug: t.pk for slug, t in tag_by_slug.items()}

        # --- 6. Accounts (first pass: no funding_account) ---
        account_by_name = {}
        for item in data.get("accounts", []):
            a = Account(
                account_name=item["account_name"],
                account_type=account_type_by_slug.get(item["account_type_slug"]) if item.get("account_type_slug") else None,
                opening_balance=item["opening_balance"],
                annual_rate=item.get("annual_rate"),
                active=item["active"],
                open_date=item.get("open_date"),
                statement_cycle_length=item.get("statement_cycle_length", 0),
                statement_cycle_period=item.get("statement_cycle_period", "d"),
                credit_limit=item.get("credit_limit"),
                bank=bank_by_name[item["bank_name"]],
                statement_balance=item.get("statement_balance"),
                archive_balance=item.get("archive_balance"),
                funding_account=None,
                calculate_payments=item.get("calculate_payments", False),
                calculate_interest=item.get("calculate_interest", False),
                payment_strategy=item.get("payment_strategy", "F"),
                payment_amount=item.get("payment_amount"),
                minimum_payment_amount=item.get("minimum_payment_amount"),
                statement_day=item.get("statement_day", 15),
                due_day=item.get("due_day", 15),
                pay_day=item.get("pay_day", 15),
                interest_deposit_day=item.get("interest_deposit_day"),
            )
            a.save()
            account_by_name[a.account_name] = a

        # Second pass: set self-referential FKs (funding_account, parent_account, interest_child_account)
        for item in data.get("accounts", []):
            acct = account_by_name[item["account_name"]]
            changed = False
            if item.get("funding_account_name"):
                funding = account_by_name.get(item["funding_account_name"])
                if funding:
                    acct.funding_account = funding
                    changed = True
            if item.get("parent_account_name"):
                parent = account_by_name.get(item["parent_account_name"])
                if parent:
                    acct.parent_account = parent
                    changed = True
            if item.get("interest_child_account_name"):
                child = account_by_name.get(item["interest_child_account_name"])
                if child:
                    acct.interest_child_account = child
                    changed = True
            if changed:
                acct.save()

        account_name_to_pk = {name: a.pk for name, a in account_by_name.items()}

        # --- 7. DescriptionHistory ---
        for item in data.get("description_history", []):
            DescriptionHistory.objects.create(
                description_normalized=item["description_normalized"],
                description_pretty=item.get("description_pretty"),
                tag=tag_by_slug.get(item["tag_slug"]) if item.get("tag_slug") else None,
            )

        # --- 8. Rewards ---
        for item in data.get("rewards", []):
            acct = account_by_name.get(item["account_name"])
            if acct:
                Reward.objects.create(
                    reward_date=item["reward_date"],
                    reward_amount=item["reward_amount"],
                    reward_account=acct,
                )

        # --- 9. Paychecks ---
        paycheck_id_map = {}
        for item in data.get("paychecks", []):
            p = Paycheck.objects.create(
                gross=item["gross"],
                net=item["net"],
                taxes=item["taxes"],
                health=item["health"],
                pension=item["pension"],
                fsa=item["fsa"],
                dca=item["dca"],
                union_dues=item["union_dues"],
                four_fifty_seven_b=item["four_fifty_seven_b"],
                payee=payee_by_name.get(item["payee_name"]) if item.get("payee_name") else None,
            )
            paycheck_id_map[item["_id"]] = p

        # --- 10. Transactions (bulk create for performance) ---
        transaction_id_map = {}
        transaction_rows = []
        for item in data.get("transactions", []):
            transaction_rows.append((
                item["_id"],
                Transaction(
                    transaction_date=item["transaction_date"],
                    total_amount=item["total_amount"],
                    status=status_by_slug.get(item["status_slug"]) if item.get("status_slug") else None,
                    memo=item.get("memo"),
                    description=item["description"],
                    edit_date=item["edit_date"],
                    add_date=item["add_date"],
                    transaction_type=ttype_by_slug.get(item["transaction_type_slug"]) if item.get("transaction_type_slug") else None,
                    paycheck=paycheck_id_map.get(item["paycheck_id"]) if item.get("paycheck_id") else None,
                    checkNumber=item.get("checkNumber"),
                    source_account=account_by_name.get(item["source_account_name"]) if item.get("source_account_name") else None,
                    destination_account=account_by_name.get(item["destination_account_name"]) if item.get("destination_account_name") else None,
                ),
            ))

        created_transactions = Transaction.objects.bulk_create([t for _, t in transaction_rows])
        for (old_id, _), new_obj in zip(transaction_rows, created_transactions):
            transaction_id_map[old_id] = new_obj

        # --- 11. TransactionDetails (bulk create) ---
        detail_batch = []
        for item in data.get("transaction_details", []):
            t = transaction_id_map.get(item["transaction_id"])
            if t:
                detail_batch.append(TransactionDetail(
                    transaction=t,
                    detail_amt=item["detail_amt"],
                    tag=tag_by_slug.get(item["tag_slug"]) if item.get("tag_slug") else None,
                    full_toggle=item.get("full_toggle", False),
                ))
        if detail_batch:
            TransactionDetail.objects.bulk_create(detail_batch)

        # --- 12. Custom Repeats (user-created only) ---
        for item in data.get("custom_repeats", []):
            repeat, _ = Repeat.objects.get_or_create(
                slug=item["slug"],
                defaults={
                    "repeat_name": item["repeat_name"],
                    "days": item.get("days", 0),
                    "weeks": item.get("weeks", 0),
                    "months": item.get("months", 0),
                    "years": item.get("years", 0),
                },
            )
            repeat_by_slug[item["slug"]] = repeat

        # --- 13. Reminders ---
        reminder_id_map = {}
        for item in data.get("reminders", []):
            r = Reminder.objects.create(
                tag=tag_by_slug.get(item["tag_slug"]) if item.get("tag_slug") else None,
                amount=item["amount"],
                reminder_source_account=account_by_name.get(item["source_account_name"]) if item.get("source_account_name") else None,
                reminder_destination_account=account_by_name.get(item["destination_account_name"]) if item.get("destination_account_name") else None,
                description=item["description"],
                transaction_type=ttype_by_slug.get(item["transaction_type_slug"]) if item.get("transaction_type_slug") else None,
                start_date=item["start_date"],
                next_date=item.get("next_date"),
                end_date=item.get("end_date"),
                repeat=repeat_by_slug.get(item["repeat_slug"]) if item.get("repeat_slug") else None,
                auto_add=item["auto_add"],
                memo=item.get("memo"),
            )
            reminder_id_map[item["_id"]] = r

        # --- 13. ReminderExclusions ---
        for item in data.get("reminder_exclusions", []):
            r = reminder_id_map.get(item["reminder_id"])
            if r:
                ReminderExclusion.objects.create(
                    reminder=r,
                    exclude_date=item["exclude_date"],
                )

        # --- 14. WindfallRules ---
        # `contrib_rules` is what backups called these before the rename.
        for item in data.get("windfall_rules", data.get("contrib_rules", [])):
            WindfallRule.objects.create(
                rule=item["rule"],
                cap=item.get("cap"),
                order=item.get("order", 0),
            )

        # --- 15. Buckets ---
        pending_bucket_budgets = []
        # Runs after Reminders (13) so reminder_id_map is populated; a backup
        # taken before the planner fields existed simply leaves them at default.
        #
        # Every existing backup file says `contributions`/`contribution`/
        # `per_paycheck`, including the production snapshot this dev database
        # was built from, so those spellings are read for as long as such files
        # exist. New exports write the bucket names.
        for item in data.get("buckets", data.get("contributions", [])):
            bucket_obj = Bucket.objects.create(
                name=item.get("name", item.get("contribution")),
                contribution_per_paycheck=item.get(
                    "contribution_per_paycheck", item.get("per_paycheck")
                ),
                # Backups predating the one-plan reshape carry `emergency_amt`
                # and `cap`; those are exactly what the new names mean, so an
                # old export restores without losing the emergency plan.
                minimum_per_paycheck=item.get(
                    "minimum_per_paycheck", item.get("emergency_amt")
                ),
                target_balance=_optional_amount(
                    item.get("target_balance", item.get("cap"))
                ),
                target_date=item.get("target_date") or item.get("goal_date"),
                sweep=item.get("sweep", item.get("goal_type") == "maximise"),
                active=item["active"],
                account=account_by_name.get(item["account_name"])
                if item.get("account_name")
                else None,
                reminder=reminder_id_map.get(item["reminder_id"])
                if item.get("reminder_id")
                else None,
                priority=item.get("priority", 100),
                # A backup taken before bridging existed has no opinion on
                # this, and the safe reading of no opinion is the default
                # every bucket starts with.
                lendable=item.get("lendable", True),
                sweep_share=item.get("sweep_share", 1),
                receives_rewards=item.get("receives_rewards", False),
            )
            # Budgets are imported at step 20, after this, so the link is made
            # by name once both sides exist rather than here.
            # Tags exist by now (imported before buckets), so they can be linked
            # straight away; budgets cannot, and wait until step 20.
            tag_pks = [
                tag_slug_to_pk[slug]
                for slug in item.get("scope_tag_slugs", item.get("tag_slugs", []))
                if slug in tag_slug_to_pk
            ]
            if tag_pks:
                bucket_obj.scope_tags.set(tag_pks)
            pending_bucket_budgets.append(
                (bucket_obj, item.get("budget_names", []))
            )

        # --- 16. Notes ---
        for item in data.get("notes", []):
            Note.objects.create(note_text=item["note_text"], note_date=item["note_date"])

        # --- 17. ChristmasGifts ---
        for item in data.get("christmas_gifts", []):
            ChristmasGift.objects.create(
                budget=item["budget"],
                tag=tag_by_slug.get(item["tag_slug"]) if item.get("tag_slug") else None,
            )

        # --- 18. Budgets (convert tag slug array back to PK array) ---
        # Parents are linked in a second pass: a child can name a parent that
        # has not been created yet, and the order in the file is not the order
        # of the hierarchy.
        pending_budget_parents = []
        for item in data.get("budgets", []):
            budget_obj = Budget.objects.create(
                tag_ids=convert_slug_json_array(item["tag_ids"], tag_slug_to_pk),
                name=item["name"],
                amount=item["amount"],
                roll_over=item["roll_over"],
                repeat=repeat_by_slug.get(item["repeat_slug"]) if item.get("repeat_slug") else None,
                start_day=item["start_day"],
                roll_over_amt=item["roll_over_amt"],
                active=item["active"],
                widget=item["widget"],
                next_start=item["next_start"],
            )
            if item.get("parent_name"):
                pending_budget_parents.append((budget_obj, item["parent_name"]))

        for budget_obj, parent_name in pending_budget_parents:
            parent = Budget.objects.filter(name=parent_name).first()
            if parent:
                budget_obj.parent = parent
                budget_obj.save(update_fields=["parent"])

        # Buckets were created at step 15, before the budgets they point at
        # existed, so the links are made here now both sides are present.
        budget_by_name = {b.name: b for b in Budget.objects.all()}
        for bucket_obj, budget_names in pending_bucket_budgets:
            linked = [
                budget_by_name[name]
                for name in budget_names
                if name in budget_by_name
            ]
            if linked:
                bucket_obj.budgets.set(linked)

        # --- 19. CalculationRules ---
        for item in data.get("calculation_rules", []):
            CalculationRule.objects.create(
                tag_ids=convert_slug_json_array(item["tag_ids"], tag_slug_to_pk),
                name=item["name"],
                source_account_id=account_name_to_pk.get(item.get("source_account_name"), 0),
                destination_account_id=account_name_to_pk.get(item.get("destination_account_name"), 0),
            )

        # --- 20. ReportConfigs ---
        for item in data.get("report_configs", []):
            rc = ReportConfig.objects.create(
                name=item["name"],
                description=item.get("description", ""),
                report_type=item["report_type"],
                date_range_type=item["date_range_type"],
                date_from=item.get("date_from"),
                date_to=item.get("date_to"),
                period2_date_from=item.get("period2_date_from"),
                period2_date_to=item.get("period2_date_to"),
                group_by=item["group_by"],
                show_transactions=item.get("show_transactions", False),
                show_subtotal=item.get("show_subtotal", True),
                include_pending=item.get("include_pending", False),
                is_shared=item.get("is_shared", False),
            )
            for account_name in item.get("account_names", []):
                acct = account_by_name.get(account_name)
                if acct:
                    rc.accounts.add(acct)
            for sel in item.get("tag_selections", []):
                ReportConfigTag.objects.create(
                    report=rc,
                    tag=tag_by_slug.get(sel["tag_slug"]) if sel.get("tag_slug") else None,
                    sub_tag=sub_tag_by_slug.get(sel["sub_tag_slug"]) if sel.get("sub_tag_slug") else None,
                    main_tag=main_tag_by_slug.get(sel["main_tag_slug"]) if sel.get("main_tag_slug") else None,
                )

        # --- 21. AccountFavorites ---
        AccountFavorite.objects.all().delete()
        for item in data.get("account_favorites", []):
            user = User.objects.filter(username=item["username"]).first()
            account = account_by_name.get(item["account_name"])
            if user and account:
                AccountFavorite.objects.get_or_create(user=user, account=account)

        # --- 22. Option singleton (update in place) ---
        if "option" in data:
            opt = data["option"]
            option = Option.load()
            if option is None:
                return  # Cannot create; load_options management command handles initial creation

            option.alert_balance = opt.get("alert_balance")
            option.alert_period = opt.get("alert_period", 3)
            option.widget1_graph_name = opt.get("widget1_graph_name", "")
            option.widget1_tag_id = tag_slug_to_pk.get(opt["widget1_tag_slug"]) if opt.get("widget1_tag_slug") else None
            option.widget1_type = graph_type_by_slug.get(opt["widget1_type_slug"]) if opt.get("widget1_type_slug") else None
            option.widget1_month = opt.get("widget1_month", 0)
            option.widget1_exclude = convert_slug_json_array(opt.get("widget1_exclude"), tag_slug_to_pk)
            option.widget2_graph_name = opt.get("widget2_graph_name", "")
            option.widget2_tag_id = tag_slug_to_pk.get(opt["widget2_tag_slug"]) if opt.get("widget2_tag_slug") else None
            option.widget2_type = graph_type_by_slug.get(opt["widget2_type_slug"]) if opt.get("widget2_type_slug") else None
            option.widget2_month = opt.get("widget2_month", 0)
            option.widget2_exclude = convert_slug_json_array(opt.get("widget2_exclude"), tag_slug_to_pk)
            option.widget3_graph_name = opt.get("widget3_graph_name", "")
            option.widget3_tag_id = tag_slug_to_pk.get(opt["widget3_tag_slug"]) if opt.get("widget3_tag_slug") else None
            option.widget3_type = graph_type_by_slug.get(opt["widget3_type_slug"]) if opt.get("widget3_type_slug") else None
            option.widget3_month = opt.get("widget3_month", 0)
            option.widget3_exclude = convert_slug_json_array(opt.get("widget3_exclude"), tag_slug_to_pk)
            option.auto_archive = opt.get("auto_archive", True)
            option.archive_length = opt.get("archive_length", 2)
            option.enable_cc_bill_calculation = opt.get("enable_cc_bill_calculation", True)
            main_tag_slug_to_pk = {slug: mt.pk for slug, mt in main_tag_by_slug.items()}
            option.report_main = convert_slug_json_array(opt.get("report_main"), main_tag_slug_to_pk)
            option.report_individual = convert_slug_json_array(opt.get("report_individual"), main_tag_slug_to_pk)
            option.retirement_accounts = convert_slug_json_array(opt.get("retirement_accounts"), account_name_to_pk)
            option.christmas_accounts = convert_slug_json_array(opt.get("christmas_accounts"), account_name_to_pk)
            option.christmas_rewards = convert_slug_json_array(opt.get("christmas_rewards"), account_name_to_pk)
            option.save()

        # --- 22. BackupConfig singleton (update in place) ---
        if "backup_config" in data:
            bc = data["backup_config"]
            config = BackupConfig.load()
            config.backup_enabled = bc.get("backup_enabled", True)
            config.frequency = bc.get("frequency", "DAILY")
            config.backup_time = bc.get("backup_time", "02:00")
            config.copies_to_keep = bc.get("copies_to_keep", 2)
            config.save()

        self.stdout.write("Data restored.")
