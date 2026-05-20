# Budgeting & Planning

The Planning section covers everything forward-looking: balance forecasting, tag-based budgeting, contribution rules, savings goals, retirement modeling, and bill reminders.

## Balance Forecasting

The **Forecast** view projects account balances into the future based on scheduled transactions, reminders, and contribution rules.

- Select an account from the slide-group (desktop) or dropdown (mobile)
- The chart shows the projected balance over the configured time window
- The time window is adjustable via the forecast settings

The forecast engine walks forward day by day, applying:

1. Scheduled recurring transactions
2. Upcoming bill reminders
3. Contribution rules (savings/investment transfers)

## Budget

The budget is tag-based. Each tag can have a monthly budget allocation.

Navigate to **Planning → Budget** to:

- View actual spending vs. budget by tag for the current period
- Add or adjust budget amounts per tag
- See a summary of over- and under-budget categories

Budget calculations use the date range you select and the cleared/pending status filter.

## Contributions

!!! note "Optional Feature"
    Contributions are an optional feature that can be enabled in the admin settings.

Contribution rules define automatic recurring transfers between accounts — typically a paycheck-driven savings or investment contribution.

Each rule specifies:

- Source account
- Destination account
- Amount or percentage
- Frequency (weekly, bi-weekly, monthly, etc.)

Contributions appear in the forecast chart and affect projected balances for both the source and destination accounts.

## Savings Goals

Savings goals track progress toward a target balance in a savings or investment account.

Set a goal amount and target date. The goal widget shows:

- Current balance vs. target
- Required monthly contribution to hit the target on time
- Progress bar

## Retirement Forecasting

!!! note "Optional Feature"
    Retirement forecasting is an optional feature that can be enabled in the admin settings.

The retirement calculator projects your investment portfolio value at retirement based on:

- Current balance
- Monthly contribution
- Expected annual return (%)
- Years to retirement

The chart shows a growth curve over time.

## Financial Calculator

!!! note "Optional Feature"
    The financial calculator is an optional feature that can be enabled in the admin settings.

A general-purpose financial calculator with common formulas:

- Loan payment (monthly payment for a given principal, rate, and term)
- Compound interest (future value of an investment)
- Savings goal (required monthly savings to reach a target)

## Notes

!!! note "Optional Feature"
    Notes are an optional feature that can be enabled in the admin settings.

Free-form notes attached to the Planning section. Use this for budget commentary, financial goals, or any reference text you want alongside your plan.

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
