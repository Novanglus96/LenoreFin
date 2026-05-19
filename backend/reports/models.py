from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


REPORT_TYPE_CHOICES = [
    ("TOTALS", "Totals"),
    ("COMPARISON", "Comparison"),
]

DATE_RANGE_CHOICES = [
    ("THIS_YEAR", "This Year"),
    ("LAST_YEAR", "Last Year"),
    ("THIS_QUARTER", "This Quarter"),
    ("LAST_QUARTER", "Last Quarter"),
    ("TRAILING_12", "Trailing 12 Months"),
    ("CUSTOM", "Custom"),
]

GROUP_BY_CHOICES = [
    ("TAG", "Tag"),
    ("MONTH", "Month"),
]


class ReportConfig(models.Model):
    name = models.CharField(max_length=254)
    description = models.TextField(blank=True, default="")
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    date_range_type = models.CharField(max_length=20, choices=DATE_RANGE_CHOICES)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    period2_date_from = models.DateField(null=True, blank=True)
    period2_date_to = models.DateField(null=True, blank=True)
    accounts = models.ManyToManyField("accounts.Account", blank=True)
    group_by = models.CharField(max_length=10, choices=GROUP_BY_CHOICES)
    show_transactions = models.BooleanField(default=False)
    show_subtotal = models.BooleanField(default=True)
    include_pending = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name


class ReportConfigTag(models.Model):
    """Through-table: one row per tag selection attached to a ReportConfig.
    Exactly one of tag/sub_tag/main_tag must be set."""

    report = models.ForeignKey(
        ReportConfig, on_delete=models.CASCADE, related_name="tag_selections"
    )
    tag = models.ForeignKey(
        "tags.Tag", on_delete=models.CASCADE, null=True, blank=True
    )
    sub_tag = models.ForeignKey(
        "tags.SubTag", on_delete=models.CASCADE, null=True, blank=True
    )
    main_tag = models.ForeignKey(
        "tags.MainTag", on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(tag__isnull=False, sub_tag__isnull=True, main_tag__isnull=True)
                    | models.Q(tag__isnull=True, sub_tag__isnull=False, main_tag__isnull=True)
                    | models.Q(tag__isnull=True, sub_tag__isnull=True, main_tag__isnull=False)
                ),
                name="reports_reportconfigtag_exactly_one_set",
            )
        ]

    def clean(self):
        filled = sum([
            self.tag_id is not None,
            self.sub_tag_id is not None,
            self.main_tag_id is not None,
        ])
        if filled != 1:
            raise ValidationError("Exactly one of tag, sub_tag, or main_tag must be set.")

    def __str__(self):
        if self.tag_id:
            return f"Tag:{self.tag_id}"
        if self.sub_tag_id:
            return f"SubTag:{self.sub_tag_id}"
        return f"MainTag:{self.main_tag_id}"
