# Accounts

The Accounts section is the core of LenoreFin. Each account tracks a real-world financial account and drives balances, forecasts, and reports across the app.

## Account Types

| Type | Description |
|------|-------------|
| **Checking** | Standard debit/checking account |
| **Savings** | Savings or money market account |
| **Credit Card** | Revolving credit with statement cycle tracking |
| **Investment** | Brokerage, retirement (401k, IRA), or other investment account |
| **Loan** | Mortgage, auto loan, personal loan |

## Account Header

Each account page shows a header card with key balances and metadata. The card adapts between desktop and mobile layouts.

**Desktop** displays all fields side by side:

- Current balance
- Statement end date *(credit cards only)*
- Statement balance or minimum due *(credit cards only)*
- Due date *(credit cards only)*
- Rewards amount *(credit cards only)*
- Available credit *(credit cards only)*

**Mobile** shows the current balance up front, with a **more / less** toggle to reveal credit card fields.

The account's bank logo appears as a watermark on desktop and inline before the account name on mobile.

## Adjusting the Balance

Full Access users can click the current balance to open the **Adjust Balance** dialog. This creates a correction transaction to bring the account to the entered amount.

## Parent Accounts

A parent account is a virtual account that aggregates the balances of its child accounts into a single combined view. It has no transactions of its own — it exists solely for the combined balance display.

**Use cases:**

- View your total checking balance across multiple checking accounts at one bank
- Group all credit cards under a single card portfolio account

To create a parent account, enable the **Is Parent Account** toggle in the Add/Edit Account form, then assign child accounts to it.

## Credit Card Features

Credit card accounts (account type = Credit Card) have additional fields:

| Field | Description |
|-------|-------------|
| **Statement Date** | The end date of the current billing cycle |
| **Statement Balance** | Balance carried from the last statement |
| **Due Date** | Payment due date |
| **Credit Limit** | Total credit limit |
| **Available Credit** | Credit limit minus current balance |
| **Rewards Amount** | Current rewards balance |
| **Payment Strategy** | `Full balance` or `Minimum payment` |
| **Calculate Payments** | If enabled, shows minimum due instead of statement balance |

### Rewards Tracking

Click the rewards amount (or the chart icon) to open the **Rewards Graph**, which shows monthly rewards earned for the current and prior year side by side.

## Banks

Each account is linked to a bank. Banks display with a logo fetched from [icon.horse](https://icon.horse) using the bank's domain. If no logo is found, a default bank icon is shown.

Banks are managed in the Django admin panel under **Administration → Banks**.

## Navigation

The left sidebar lists all active accounts. Each entry shows the bank logo, account name, and current balance. Inactive accounts are hidden from the sidebar but remain accessible for reporting and history.

## Investment Return Estimation

For investment accounts (account type = Investment), LenoreFin estimates the historical annual return rate from your transaction history using the **Modified Dietz method**.

### How It Works

The engine looks back 12 months of cleared transactions and calculates:

- **Beginning market value (BMV)** — account balance at the start of the period
- **Ending market value (EMV)** — current balance
- **Net cash flows** — external transfers in and out (contributions and withdrawals), weighted by the number of days remaining in the period
- **Intrinsic returns** — income and expense transactions (dividends, interest, fees) that are excluded from cash flow weighting

This approach isolates the account's investment performance from the effect of new contributions or withdrawals.

The period return is then annualized:

```
annualized_rate = (1 + period_return) ^ (365 / days) - 1
```

### Viewing the Estimated Rate

The estimated annual return appears in the account header widget next to the APY field (when `Calculate Interest` is enabled). A minimum of one cleared income transaction is required before a rate is displayed.

### Applying to Forecast

Click the chart icon next to the displayed rate to apply it as the account's APY. This updates `Annual Rate` and the forecast immediately uses the derived rate for future projections.

You can also apply it from the **Edit Account** form — a chip below the Annual Rate field shows the calculated rate and can be clicked to fill the field.

---

## Forecasting

Each account has a **Forecast** tab showing a balance projection chart over a configurable time window. See [Budgeting & Planning](planning.md) for details.
