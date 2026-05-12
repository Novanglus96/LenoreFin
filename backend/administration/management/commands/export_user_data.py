import gzip
import json
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Export user data to a version-agnostic gzipped JSON backup"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help="Output file path. Defaults to <backup_location>/lenorefin-backup-YYYY-MM-DD-HHMMSS.json.gz",
        )

    def handle(self, *args, **options):
        output = options["output"]
        if output is None:
            location = settings.DBBACKUP_STORAGE_OPTIONS.get("location", "/backups/")
            os.makedirs(location, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
            output = os.path.join(location, f"lenorefin-backup-{timestamp}.json.gz")

        data = self._collect_data()

        json_bytes = json.dumps(data, indent=2, default=str).encode("utf-8")
        with gzip.open(output, "wb") as f:
            f.write(json_bytes)

        self.stdout.write(self.style.SUCCESS(f"Backup written to: {output}"))
        return output

    def _collect_data(self):
        from administration.models import Payee, DescriptionHistory, Option, BackupConfig
        from accounts.models import Bank, Account, Reward
        from tags.models import Tag, MainTag, SubTag
        from transactions.models import Transaction, Paycheck, TransactionDetail
        from reminders.models import Reminder, ReminderExclusion
        from planning.models import ContribRule, Contribution, Note, ChristmasGift, Budget, CalculationRule

        data = {}

        # Build helper maps for converting PKs to natural keys
        all_tags = list(Tag.objects.all().select_related("parent", "child", "tag_type"))
        tag_pk_to_slug = {t.pk: t.slug for t in all_tags}
        account_pk_to_name = {a.pk: a.account_name for a in Account.objects.all()}

        def convert_id_json_array(id_str, pk_to_key):
            """Convert a JSON array of PKs stored as a string to a JSON array of natural keys."""
            if not id_str:
                return id_str
            try:
                pk_list = json.loads(id_str)
                if not isinstance(pk_list, list):
                    return id_str
                return json.dumps([pk_to_key.get(pk, pk) for pk in pk_list])
            except (json.JSONDecodeError, TypeError):
                return id_str

        # 1. Payees
        data["payees"] = [
            {"payee_name": p.payee_name}
            for p in Payee.objects.all()
        ]

        # 2. Banks
        data["banks"] = [
            {"bank_name": b.bank_name}
            for b in Bank.objects.all()
        ]

        # 3. MainTags (user-created only)
        data["main_tags"] = [
            {
                "slug": mt.slug,
                "tag_name": mt.tag_name,
                "tag_type_slug": mt.tag_type.slug if mt.tag_type else None,
            }
            for mt in MainTag.objects.filter(is_system=False).select_related("tag_type")
        ]

        # 4. SubTags (user-created only)
        data["sub_tags"] = [
            {
                "slug": st.slug,
                "tag_name": st.tag_name,
                "tag_type_slug": st.tag_type.slug if st.tag_type else None,
            }
            for st in SubTag.objects.filter(is_system=False).select_related("tag_type")
        ]

        # 5. Tags (user-created only)
        data["tags"] = [
            {
                "slug": t.slug,
                "parent_slug": t.parent.slug if t.parent else None,
                "child_slug": t.child.slug if t.child else None,
                "tag_type_slug": t.tag_type.slug if t.tag_type else None,
            }
            for t in Tag.objects.filter(is_system=False).select_related("parent", "child", "tag_type")
        ]

        # 6. Accounts
        data["accounts"] = [
            {
                "account_name": a.account_name,
                "account_type_slug": a.account_type.slug if a.account_type else None,
                "opening_balance": str(a.opening_balance),
                "annual_rate": str(a.annual_rate) if a.annual_rate is not None else None,
                "active": a.active,
                "open_date": str(a.open_date) if a.open_date else None,
                "statement_cycle_length": a.statement_cycle_length,
                "statement_cycle_period": a.statement_cycle_period,
                "credit_limit": str(a.credit_limit) if a.credit_limit is not None else None,
                "bank_name": a.bank.bank_name,
                "statement_balance": str(a.statement_balance) if a.statement_balance is not None else None,
                "archive_balance": str(a.archive_balance) if a.archive_balance is not None else None,
                "funding_account_name": a.funding_account.account_name if a.funding_account else None,
                "calculate_payments": a.calculate_payments,
                "calculate_interest": a.calculate_interest,
                "payment_strategy": a.payment_strategy,
                "payment_amount": str(a.payment_amount) if a.payment_amount is not None else None,
                "minimum_payment_amount": str(a.minimum_payment_amount) if a.minimum_payment_amount is not None else None,
                "statement_day": a.statement_day,
                "due_day": a.due_day,
                "pay_day": a.pay_day,
                "interest_deposit_day": a.interest_deposit_day,
            }
            for a in Account.objects.all().select_related("account_type", "bank", "funding_account")
        ]

        # 7. DescriptionHistory
        data["description_history"] = [
            {
                "description_normalized": dh.description_normalized,
                "description_pretty": dh.description_pretty,
                "tag_slug": dh.tag.slug if dh.tag else None,
            }
            for dh in DescriptionHistory.objects.all().select_related("tag")
        ]

        # 8. Rewards
        data["rewards"] = [
            {
                "reward_date": str(r.reward_date),
                "reward_amount": str(r.reward_amount),
                "account_name": r.reward_account.account_name,
            }
            for r in Reward.objects.all().select_related("reward_account")
        ]

        # 9. Paychecks
        data["paychecks"] = [
            {
                "_id": p.id,
                "gross": str(p.gross),
                "net": str(p.net),
                "taxes": str(p.taxes),
                "health": str(p.health),
                "pension": str(p.pension),
                "fsa": str(p.fsa),
                "dca": str(p.dca),
                "union_dues": str(p.union_dues),
                "four_fifty_seven_b": str(p.four_fifty_seven_b),
                "payee_name": p.payee.payee_name if p.payee else None,
            }
            for p in Paycheck.objects.all().select_related("payee")
        ]

        # 10. Transactions
        data["transactions"] = [
            {
                "_id": t.id,
                "transaction_date": str(t.transaction_date),
                "total_amount": str(t.total_amount),
                "status_slug": t.status.slug if t.status else None,
                "memo": t.memo,
                "description": t.description,
                "edit_date": str(t.edit_date),
                "add_date": str(t.add_date),
                "transaction_type_slug": t.transaction_type.slug if t.transaction_type else None,
                "paycheck_id": t.paycheck_id,
                "checkNumber": t.checkNumber,
                "source_account_name": t.source_account.account_name if t.source_account else None,
                "destination_account_name": t.destination_account.account_name if t.destination_account else None,
            }
            for t in Transaction.objects.all().select_related(
                "status", "transaction_type", "paycheck",
                "source_account", "destination_account"
            )
        ]

        # 11. TransactionDetails
        data["transaction_details"] = [
            {
                "transaction_id": td.transaction_id,
                "detail_amt": str(td.detail_amt),
                "tag_slug": td.tag.slug if td.tag else None,
            }
            for td in TransactionDetail.objects.all().select_related("tag")
        ]

        # 12. Reminders
        data["reminders"] = [
            {
                "_id": r.id,
                "tag_slug": r.tag.slug if r.tag else None,
                "amount": str(r.amount),
                "source_account_name": r.reminder_source_account.account_name if r.reminder_source_account else None,
                "destination_account_name": r.reminder_destination_account.account_name if r.reminder_destination_account else None,
                "description": r.description,
                "transaction_type_slug": r.transaction_type.slug if r.transaction_type else None,
                "start_date": str(r.start_date),
                "next_date": str(r.next_date) if r.next_date else None,
                "end_date": str(r.end_date) if r.end_date else None,
                "repeat_slug": r.repeat.slug if r.repeat else None,
                "auto_add": r.auto_add,
                "memo": r.memo,
            }
            for r in Reminder.objects.all().select_related(
                "tag", "reminder_source_account", "reminder_destination_account",
                "transaction_type", "repeat"
            )
        ]

        # 13. ReminderExclusions
        data["reminder_exclusions"] = [
            {
                "reminder_id": re.reminder_id,
                "exclude_date": str(re.exclude_date),
            }
            for re in ReminderExclusion.objects.all()
        ]

        # 14. ContribRules
        data["contrib_rules"] = [
            {"rule": cr.rule, "cap": cr.cap, "order": cr.order}
            for cr in ContribRule.objects.all()
        ]

        # 15. Contributions
        data["contributions"] = [
            {
                "contribution": c.contribution,
                "per_paycheck": str(c.per_paycheck),
                "emergency_amt": str(c.emergency_amt),
                "emergency_diff": str(c.emergency_diff),
                "cap": str(c.cap),
                "active": c.active,
            }
            for c in Contribution.objects.all()
        ]

        # 16. Notes
        data["notes"] = [
            {"note_text": n.note_text, "note_date": str(n.note_date)}
            for n in Note.objects.all()
        ]

        # 17. ChristmasGifts
        data["christmas_gifts"] = [
            {
                "budget": str(cg.budget),
                "tag_slug": cg.tag.slug if cg.tag else None,
            }
            for cg in ChristmasGift.objects.all().select_related("tag")
        ]

        # 18. Budgets (convert tag_ids PK array to slug array)
        data["budgets"] = [
            {
                "tag_ids": convert_id_json_array(b.tag_ids, tag_pk_to_slug),
                "name": b.name,
                "amount": str(b.amount),
                "roll_over": b.roll_over,
                "repeat_slug": b.repeat.slug if b.repeat else None,
                "start_day": str(b.start_day),
                "roll_over_amt": str(b.roll_over_amt),
                "active": b.active,
                "widget": b.widget,
                "next_start": str(b.next_start),
            }
            for b in Budget.objects.all().select_related("repeat")
        ]

        # 19. CalculationRules (convert tag_ids and account IDs)
        data["calculation_rules"] = []
        for cr in CalculationRule.objects.all():
            data["calculation_rules"].append({
                "tag_ids": convert_id_json_array(cr.tag_ids, tag_pk_to_slug),
                "name": cr.name,
                "source_account_name": account_pk_to_name.get(cr.source_account_id),
                "destination_account_name": account_pk_to_name.get(cr.destination_account_id),
            })

        # 20. Option singleton
        option = Option.load()
        if option:
            data["option"] = {
                "alert_balance": str(option.alert_balance) if option.alert_balance is not None else None,
                "alert_period": option.alert_period,
                "widget1_graph_name": option.widget1_graph_name,
                "widget1_tag_slug": tag_pk_to_slug.get(option.widget1_tag_id) if option.widget1_tag_id else None,
                "widget1_type_slug": option.widget1_type.slug if option.widget1_type else None,
                "widget1_month": option.widget1_month,
                "widget1_exclude": convert_id_json_array(option.widget1_exclude, tag_pk_to_slug),
                "widget2_graph_name": option.widget2_graph_name,
                "widget2_tag_slug": tag_pk_to_slug.get(option.widget2_tag_id) if option.widget2_tag_id else None,
                "widget2_type_slug": option.widget2_type.slug if option.widget2_type else None,
                "widget2_month": option.widget2_month,
                "widget2_exclude": convert_id_json_array(option.widget2_exclude, tag_pk_to_slug),
                "widget3_graph_name": option.widget3_graph_name,
                "widget3_tag_slug": tag_pk_to_slug.get(option.widget3_tag_id) if option.widget3_tag_id else None,
                "widget3_type_slug": option.widget3_type.slug if option.widget3_type else None,
                "widget3_month": option.widget3_month,
                "widget3_exclude": convert_id_json_array(option.widget3_exclude, tag_pk_to_slug),
                "auto_archive": option.auto_archive,
                "archive_length": option.archive_length,
                "enable_cc_bill_calculation": option.enable_cc_bill_calculation,
                "report_main": option.report_main,
                "report_individual": option.report_individual,
                "retirement_accounts": convert_id_json_array(option.retirement_accounts, account_pk_to_name),
                "christmas_accounts": convert_id_json_array(option.christmas_accounts, account_pk_to_name),
                "christmas_rewards": convert_id_json_array(option.christmas_rewards, account_pk_to_name),
            }

        # 21. BackupConfig singleton
        config = BackupConfig.load()
        data["backup_config"] = {
            "backup_enabled": config.backup_enabled,
            "frequency": config.frequency,
            "backup_time": config.backup_time,
            "copies_to_keep": config.copies_to_keep,
        }

        return data
