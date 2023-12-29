from django.db import models
from datetime import date

# Create your models here.

class AccountType(models.Model):
    account_type = models.CharField(max_length=254, unique=True)
    color = models.CharField(max_length=7, default='#059669')
    icon = models.CharField(max_length=25)
    
    def __str__(self):
        return self.account_type

class Account(models.Model):
    account_name = models.CharField(max_length=254, unique=True)
    account_type = models.ForeignKey(AccountType, null=True, on_delete=models.SET_NULL)
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    apy = models.DecimalField(max_digits=2, decimal_places=2, default=0.00, null=True)
    due_date = models.DateField(default=date.today, null=True)
    active = models.BooleanField(default=True)
    open_date = models.DateField(default=date.today)
    next_cycle_date = models.DateField(default=date.today, null=True)
    statement_cycle_length = models.IntegerField(default=0, null=True)
    rewards_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True)
    
    def __str__(self):
        return self.account_name

class CalendarDate(models.Model):
    datefield = models.DateField(unique=True)
    
    def __str__(self):
        return str(self.datefield)

class Tag(models.Model):
    tag_name = models.CharField(max_length=254, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.tag_name

class ChristmasGift(models.Model):
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tag = models.ForeignKey(Tag, null=True, on_delete=models.SET_NULL)
   
class ContribRule(models.Model):
    rule = models.CharField(max_length=254)
    cap = models.CharField(max_length=254, null=True, blank=True, default=None)
    
    def __str__(self):
        return self.rule

class Contribution(models.Model):
    contribution = models.CharField(max_length=20, unique=True)
    per_paycheck = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    emergency_amt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    emergency_diff = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cap = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.contribution

class ErrorLevel(models.Model):
    error_level = models.CharField(max_length=25, unique=True)
    
    def __str__(self):
        return self.error_level

class TransactionType(models.Model):
    transaction_type = models.CharField(max_length=254, unique=True)
    
    def __str__(self):
        return self.transaction_type

class Repeat(models.Model):
    repeat_name = models.CharField(max_length=254, unique=True)
    days = models.IntegerField(default=0)
    weeks = models.IntegerField(default=0)
    months = models.IntegerField(default=0)
    years = models.IntegerField(default=0)
    
    def __str__(self):
        return self.repeat_name

class Reminder(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reminder_source_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='reminder_source_account')
    reminder_destination_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='reminder_destination_account')
    description = models.CharField(max_length=254)
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default=date.today)
    repeat = models.ForeignKey(Repeat, on_delete=models.SET_NULL, null=True, blank=True)
    auto_add = models.BooleanField(default=False)
    
    def __str__(self):
        return self.description

class Note(models.Model):
    note_text = models.CharField(max_length=254)
    note_date = models.DateField(default=date.today)
    
    def __str__(self):
        return self.note_date

class Option(models.Model):
    log_level = models.ForeignKey(ErrorLevel, on_delete=models.SET_NULL, null=True, blank=True)
    alert_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    alert_period = models.IntegerField(default=3)

class TransactionStatus(models.Model):
    transaction_status = models.CharField(max_length=254, unique=True)
    
    class Meta:
        verbose_name_plural = "Transaction statuses"
    
    def __str__(self):
        return self.transaction_status


class Payee(models.Model):
    payee_name = models.CharField(max_length=254, unique=True)
    
    def __str__(self):
        return self.payee_name

class Transaction(models.Model):
    transaction_date = models.DateField(default=date.today)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.ForeignKey(TransactionStatus, on_delete=models.SET_NULL, null=True, blank=True)
    memo = models.CharField(max_length=254)
    description = models.CharField(max_length=254)
    edit_date = models.DateField(default=date.today)
    add_date = models.DateField(default=date.today)
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_source_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='transaction_source_account')
    transaction_destination_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='transaction_destination_account')
    p_gross = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    p_taxes = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    p_health = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    p_pension = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    p_fsa = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    p_dca = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    p_union_dues = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    p_457b = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    p_payee = models.ForeignKey(Payee, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    reminder = models.ForeignKey(Reminder, on_delete=models.CASCADE, null=True, blank=True, default=None)
    
class TransactionDetail(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    detail_amt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, blank=True)

class LogEntry(models.Model):
    log_date = models.DateField(default=date.today)
    log_entry = models.CharField(max_length=254)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, default=None)
    reminder = models.ForeignKey(Reminder, on_delete=models.CASCADE, null=True, blank=True, default=None)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, blank=True, default=None)
    error_num = models.IntegerField(default=None, null=True, blank=True)
    error_level = models.ForeignKey(ErrorLevel, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.log_entry
