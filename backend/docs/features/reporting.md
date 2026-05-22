# Reporting

LenoreFin includes a custom report builder that lets you analyze spending and income by tag, account, and time period.

## Report Types

| Type | Description |
|------|-------------|
| **Totals** | Aggregate income and spending by tag for a date range |
| **Year-over-Year Comparison** | Compare the same period across two calendar years side by side |

## Running a Report

Navigate to **Reports** and configure:

| Field | Description |
|-------|-------------|
| **Report Type** | Totals or Year-over-Year Comparison |
| **Date Range** | Start and end date for the report period |
| **Accounts** | Filter to one or more accounts (leave blank for all) |
| **Tags** | Filter to specific tags (leave blank for all) |
| **Status** | Include Pending, Cleared, Reconciled, or any combination |

Click **Run** to execute the report. Results appear immediately in a table below the filter form. No saving required — run as many variations as you like.

## Totals Report

The Totals report groups transactions by tag and shows:

- Total credits (income/deposits)
- Total debits (spending/withdrawals)
- Net amount

Rows are grouped by the top-level main tag, with sub-tags expanded in nested rows.

## Year-over-Year Comparison

The comparison report runs the same tag grouping for two separate years and displays them side by side with a delta column showing the change.

Useful for:

- Comparing annual spending in a category
- Identifying cost increases over time
- Reviewing income growth

## Filtering by Status

Use the status filter to control which transactions are included:

- **Pending only** — upcoming/unposted items
- **Cleared** — posted and verified transactions
- **Reconciled** — finalized transactions
- **All** — include every status

For accurate historical reporting, filter to Cleared + Reconciled and exclude Pending.

## Printing Reports

Use your browser's **Print** function (`Ctrl+P` / `Cmd+P`) to print or save a report as PDF. The report table is formatted for print with a clean layout.
