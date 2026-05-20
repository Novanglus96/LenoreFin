# Transactions

Transactions are the primary data entry point. Every movement of money — deposits, withdrawals, transfers, credit card charges — is recorded as a transaction.

## Transaction Fields

| Field | Description |
|-------|-------------|
| **Account** | The account this transaction belongs to |
| **Date** | Transaction date |
| **Description** | Free-text description or payee name |
| **Amount** | Dollar amount (positive = credit/deposit, negative = debit/charge) |
| **Transaction Type** | Debit, Credit, or Transfer |
| **Status** | Pending, Cleared, or Reconciled |
| **Tags** | One or more tags for categorization |
| **Notes** | Optional free-text notes |
| **Attachments** | One or more file attachments (receipts, statements) |

## Transaction List

The transaction list displays all transactions for the selected account. Use the filter bar to narrow results:

| Filter | Description |
|--------|-------------|
| **Search** | Full-text search on description |
| **Status** | Filter by Pending, Cleared, or Reconciled |
| **Type** | Filter by transaction type |
| **Tag** | Filter by one or more tags |
| **Date From / To** | Filter by date range |

Transactions are paginated. The list shows the running balance alongside each transaction.

## Adding Transactions

Click the **+** button to open the Add Transaction form. Fill in the required fields and save. The account balance updates immediately.

## Editing Transactions

Click any transaction row to open the Edit Transaction form. All fields are editable. Full Access users can edit any transaction; Readonly users can only view.

## Bulk Editing

Select multiple transactions using the checkboxes, then use the bulk action toolbar to:

- Change status on all selected
- Delete selected
- Apply tags to selected

## CSV Import

Upload a CSV file from your bank's export to import multiple transactions at once. The import pipeline:

1. Parses the CSV
2. Shows a preview table for review
3. Applies on save; duplicate detection prevents re-importing already-present transactions

Navigate to **Transactions → Import** to start an import.

## File Attachments

Each transaction can have one or more file attachments. Supported types include PDF, PNG, JPG, and other common document formats.

Attachments are stored in the `lenorefin_media` volume and linked to the transaction record. Click the paperclip icon on a transaction to view or add attachments.

## Tags

Tags are the primary categorization mechanism. The tag hierarchy is:

```
Main Tag  (e.g. "Housing")
  └── Sub Tag  (e.g. "Rent")
        └── Tag  (e.g. "Apartment 4B")
```

Assign one or more tags to each transaction. Tags drive budgeting and reporting.

## Paycheck Transactions

Paycheck transactions are a special transaction type that auto-splits a paycheck deposit into its component parts (gross pay, taxes, deductions). Configure paycheck rules in **Administration → Payees** and use the **Add Paycheck** shortcut to record a paycheck with all splits in one step.

## Reminders

Recurring bill reminders appear in the transaction list as upcoming items. Confirm a reminder to create the real transaction. See [Budgeting & Planning](planning.md) for reminder configuration.

## Statuses

| Status | Meaning |
|--------|---------|
| **Pending** | Transaction entered but not yet posted by the bank |
| **Cleared** | Posted and verified against the bank statement |
| **Reconciled** | Included in a completed reconciliation |

Use status filtering in reports to exclude pending transactions from cleared totals.
