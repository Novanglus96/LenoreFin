# Budgeting & Planning

The Planning section covers everything forward-looking: balance forecasting, tag-based budgeting, savings goals, and bill reminders.

## Balance Forecasting

The **Forecast** view projects account balances into the future based on scheduled transactions and reminders.

- Select an account from the slide-group (desktop) or dropdown (mobile)
- The chart shows the projected balance over the configured time window
- The time window is adjustable via the forecast settings

The forecast engine walks forward day by day, applying:

1. Scheduled recurring transactions
2. Upcoming bill reminders

## Budget

The budget is tag-based. Each tag can have a monthly budget allocation.

Navigate to **Planning → Budget** to:

- View actual spending vs. budget by tag for the current period
- Add or adjust budget amounts per tag
- See a summary of over- and under-budget categories

Budget calculations use the date range you select and the cleared/pending status filter.

## Savings Goals

Savings goals track progress toward a target balance in a savings or investment account.

Set a goal amount and target date. The goal widget shows:

- Current balance vs. target
- Required monthly contribution to hit the target on time
- Progress bar

## Bill Reminders

Reminders track recurring bills so nothing gets missed.

Navigate to **Planning → Reminders** to manage reminders. Each reminder has:

| Field | Description |
|-------|-------------|
| **Name** | Bill name (e.g. "Electric Bill") |
| **Account** | Account to charge when confirmed |
| **Amount** | Expected bill amount |
| **Due Date** | Next due date |
| **Repeat Type** | Monthly, weekly, bi-weekly, quarterly, annual, etc. |
| **Payee** | Optional payee link |
| **Tag** | Tag applied to the created transaction |

### Confirming a Reminder

When a reminder is due, it appears in the transaction list as an upcoming item. Click **Confirm** to create the real transaction and advance the reminder to its next due date. The reminder stays active and continues repeating.

### Reminder Repeat Schedule

The repeat engine supports:

- **Fixed interval** — every N days, weeks, months
- **Day of month** — e.g. the 15th of every month
- **Last day of month** — handles months of different lengths correctly
