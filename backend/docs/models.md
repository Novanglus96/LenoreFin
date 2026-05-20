# Models

This page is a reference for the core Django models in LenoreFin. Auto-generated fields (`id`, `created_at`, `updated_at`) are omitted unless notable.

## Accounts

### AccountType

Classifies an account (Checking, Savings, Credit Card, Investment, Loan).

| Field | Type | Notes |
|-------|------|-------|
| `account_type` | CharField | Display name, unique |
| `color` | CharField | Hex color for UI display |
| `icon` | CharField | MDI icon name |

### Bank

A financial institution linked to accounts.

| Field | Type | Notes |
|-------|------|-------|
| `bank_name` | CharField | Display name, unique |
| `logo_url` | CharField | Optional; populated from `icon.horse` |

### Account

The core account entity. Represents a real-world financial account.

| Field | Type | Notes |
|-------|------|-------|
| `account_name` | CharField | Unique |
| `account_type` | FK → AccountType | |
| `bank` | FK → Bank | |
| `opening_balance` | DecimalField | |
| `active` | BooleanField | Inactive accounts hidden from nav |
| `open_date` | DateField | |
| `credit_limit` | DecimalField | Credit cards only |
| `statement_balance` | DecimalField | Balance from last statement |
| `statement_day` | IntegerField | Day of month statement closes |
| `due_day` | IntegerField | Day of month payment is due |
| `statement_cycle_length` | IntegerField | Billing cycle length |
| `statement_cycle_period` | CharField | `D` (days), `M` (months) |
| `calculate_payments` | BooleanField | Auto-calculate minimum payment |
| `payment_strategy` | CharField | `F` (full balance) or `M` (minimum) |
| `calculate_interest` | BooleanField | Auto-post interest earned |
| `annual_rate` | DecimalField | Annual interest rate (%) |
| `parent_account` | FK → Account (self) | Optional parent for combined view |

### Reward

A credit card reward entry earned on a specific date.

| Field | Type | Notes |
|-------|------|-------|
| `reward_account` | FK → Account | |
| `reward_date` | DateField | |
| `reward_amount` | DecimalField | |

---

## Transactions

### TransactionType

Classification for a transaction's direction (Debit, Credit, Transfer).

| Field | Type | Notes |
|-------|------|-------|
| `transaction_type` | CharField | Unique |

### TransactionStatus

A transaction's posting status (Pending, Cleared, Reconciled).

| Field | Type | Notes |
|-------|------|-------|
| `transaction_status` | CharField | Unique |

### Transaction

A single financial transaction between two accounts.

| Field | Type | Notes |
|-------|------|-------|
| `transaction_date` | DateField | |
| `total_amount` | DecimalField | |
| `description` | CharField | Payee or free-text description |
| `memo` | TextField | Optional notes |
| `transaction_type` | FK → TransactionType | |
| `status` | FK → TransactionStatus | |
| `source_account` | FK → Account | Money leaves here |
| `destination_account` | FK → Account | Money arrives here |
| `paycheck` | FK → Paycheck | Optional; set for paycheck splits |
| `check_number` | IntegerField | Optional |

### TransactionDetail

A tagged line item within a transaction. A single transaction may have multiple details splitting the total across different tags.

| Field | Type | Notes |
|-------|------|-------|
| `transaction` | FK → Transaction | |
| `tag` | FK → Tag | |
| `detail_amt` | DecimalField | Amount for this line item |
| `full_toggle` | BooleanField | If true, detail represents the full transaction amount |

### TransactionImage

A file attachment linked to a transaction (receipt, statement, etc.).

| Field | Type | Notes |
|-------|------|-------|
| `transaction` | FK → Transaction | |
| `image` | FileField | Stored in `lenorefin_media` |

### Paycheck

Itemized paycheck deductions linked to a transaction.

| Field | Type | Notes |
|-------|------|-------|
| `gross` | DecimalField | |
| `net` | DecimalField | |
| `taxes` | DecimalField | |
| `health` | DecimalField | Health insurance |
| `pension` | DecimalField | |
| `fsa` | DecimalField | Flexible spending account |
| `dca` | DecimalField | Dependent care account |
| `union_dues` | DecimalField | |
| `four_fifty_seven_b` | DecimalField | 457(b) retirement contribution |
| `payee` | FK → Payee | |

---

## Tags

### TagType

Classifies tags by type (Expense, Income, Transfer).

| Field | Type | Notes |
|-------|------|-------|
| `tag_type` | CharField | Unique |

### MainTag

Top-level tag category (e.g. "Housing", "Food").

| Field | Type | Notes |
|-------|------|-------|
| `tag_name` | CharField | Unique |
| `tag_type` | FK → TagType | |

### SubTag

Second-level tag (e.g. "Rent" under "Housing").

| Field | Type | Notes |
|-------|------|-------|
| `tag_name` | CharField | Unique |
| `tag_type` | FK → TagType | |

### Tag

The composite tag entity combining a MainTag and optional SubTag. This is the tag you assign to transactions.

| Field | Type | Notes |
|-------|------|-------|
| `parent` | FK → MainTag | |
| `child` | FK → SubTag | Optional |
| `tag_type` | FK → TagType | |

---

## Planning

### Budget

A spending limit for transactions matching specific tags.

| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField | Unique |
| `tag_ids` | CharField | Comma-separated tag IDs |
| `amount` | DecimalField | Budget cap |
| `roll_over` | BooleanField | Carry unused balance to next period |
| `roll_over_amt` | DecimalField | Current rolled-over balance |
| `repeat` | FK → Repeat | How often the budget resets |
| `start_day` | DateField | Start of current budget period |
| `next_start` | DateField | Start of next budget period |
| `active` | BooleanField | |
| `widget` | BooleanField | Show on dashboard widget |

---

## Reminders

### Repeat

A recurrence interval combining days, weeks, months, and years.

| Field | Type | Notes |
|-------|------|-------|
| `repeat_name` | CharField | Unique display name |
| `days` | IntegerField | |
| `weeks` | IntegerField | |
| `months` | IntegerField | |
| `years` | IntegerField | |

### Reminder

A scheduled recurring transaction.

| Field | Type | Notes |
|-------|------|-------|
| `description` | CharField | |
| `amount` | DecimalField | |
| `transaction_type` | FK → TransactionType | |
| `reminder_source_account` | FK → Account | |
| `reminder_destination_account` | FK → Account | Optional |
| `tag` | FK → Tag | Applied to confirmed transaction |
| `repeat` | FK → Repeat | Recurrence interval |
| `start_date` | DateField | First occurrence |
| `next_date` | DateField | Next upcoming occurrence |
| `end_date` | DateField | Optional end date |
| `auto_add` | BooleanField | Auto-create transactions without manual confirmation |
| `memo` | TextField | Optional notes |

### ReminderExclusion

Marks a specific date as excluded from a reminder's recurrence.

| Field | Type | Notes |
|-------|------|-------|
| `reminder` | FK → Reminder | |
| `exclude_date` | DateField | |
