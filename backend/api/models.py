from django.db import models
from datetime import date

# Create your models here.

class AccountType(models.Model):
    account_type = models.CharField(max_length=254, unique=True)
    color = models.CharField(max_length=7, default='#059669')
    icon = models.CharField(max_length=25)
    
    def __str__(self):
        return self.account_type


class Bank(models.Model):
    bank_name = models.CharField(max_length=254, unique=True)
    
    def __str__(self):
        return self.bank_name


class Account(models.Model):
    account_name = models.CharField(max_length=254, unique=True)
    account_type = models.ForeignKey(AccountType, null=True, on_delete=models.SET_NULL)
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True)
    apy = models.DecimalField(max_digits=2, decimal_places=2, default=0.00, null=True)
    due_date = models.DateField(default=date.today, null=True)
    active = models.BooleanField(default=True)
    open_date = models.DateField(default=date.today, null=True)
    next_cycle_date = models.DateField(default=date.today, null=True)
    statement_cycle_length = models.IntegerField(default=0, null=True)
    statement_cycle_period = models.CharField(max_length=1, null=True, default='d')
    rewards_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    last_statement_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True)
    
    def __str__(self):
        return self.account_name

class TagType(models.Model):
    tag_type = models.CharField(max_length=254, unique=True)
    
    def __str__(self):
        return self.tag_type

class Tag(models.Model):
    tag_name = models.CharField(max_length=254, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    tag_type = models.ForeignKey(TagType, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    
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
    widget1_graph_name = models.CharField(max_length=254)
    widget1_tag_id = models.IntegerField(default=None, null=True, blank=True)
    widget1_expense = models.BooleanField(default=True)
    widget1_month = models.IntegerField(default=0)
    widget1_exclude = models.CharField(max_length=254)
    widget2_graph_name = models.CharField(max_length=254)
    widget2_tag_id = models.IntegerField(default=None, null=True, blank=True)
    widget2_expense = models.BooleanField(default=True)
    widget2_month = models.IntegerField(default=0)
    widget2_exclude = models.CharField(max_length=254)
    widget3_graph_name = models.CharField(max_length=254)
    widget3_tag_id = models.IntegerField(default=None, null=True, blank=True)
    widget3_expense = models.BooleanField(default=True)
    widget3_month = models.IntegerField(default=0)
    widget3_exclude = models.CharField(max_length=254)

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

class Paycheck(models.Model):
    gross = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    taxes = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    health = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pension = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fsa = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    dca = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    union_dues = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    four_fifty_seven_b = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payee = models.ForeignKey(Payee, on_delete=models.SET_NULL, null=True, blank=True, default=None)

class Transaction(models.Model):
    transaction_date = models.DateField(default=date.today)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.ForeignKey(TransactionStatus, on_delete=models.SET_NULL, null=True, blank=True)
    memo = models.CharField(max_length=254)
    description = models.CharField(max_length=254)
    edit_date = models.DateField(default=date.today)
    add_date = models.DateField(default=date.today)
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.SET_NULL, null=True, blank=True)
    reminder = models.ForeignKey(Reminder, on_delete=models.CASCADE, null=True, blank=True, default=None)
    paycheck = models.ForeignKey(Paycheck, on_delete=models.CASCADE, null=True, blank=True, default=None)
    
class TransactionDetail(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
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
    
    class Meta:
        verbose_name_plural = "Log entries"
    
    def __str__(self):
        return self.log_entry

class Message(models.Model):
    message_date = models.DateField(default=date.today)
    message = models.CharField(max_length=254)
    unread = models.BooleanField(default=True)
    
    def __str__(self):
        return self.message
