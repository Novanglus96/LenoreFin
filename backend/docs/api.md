# API Reference

LenoreFin exposes a REST API built with [Django Ninja](https://django-ninja.dev/). All endpoints are under `/api/v1/` and require authentication.

## Interactive Docs

The full interactive API documentation (ReDoc) is available at:

```
http://<your-host>/api/v1/docs
```

Use this page to browse all endpoints, view request/response schemas, and try requests directly.

## Authentication

All API requests require an API key passed as a query parameter or header.

**Query parameter:**
```
GET /api/v1/accounts?api_key=<your-key>
```

**Header:**
```
Authorization: Bearer <your-key>
```

Generate API keys in **Django Admin → Authentication → API Keys**. The key used by the frontend is configured via `VITE_API_KEY` in your `.env` file.

## Endpoints

All routes are prefixed with `/api/v1/`.

### Accounts

| Method | Path | Description |
|--------|------|-------------|
| GET | `/accounts` | List all accounts |
| POST | `/accounts` | Create an account |
| GET | `/accounts/{id}` | Get account by ID |
| PUT | `/accounts/{id}` | Update account |
| DELETE | `/accounts/{id}` | Delete account |
| GET | `/accounts/account-types` | List account types |
| GET | `/accounts/banks` | List banks |
| POST | `/accounts/banks` | Create bank |
| PUT | `/accounts/banks/{id}` | Update bank |
| DELETE | `/accounts/banks/{id}` | Delete bank |
| GET | `/accounts/forecast` | Get forecast data for an account |
| GET | `/accounts/{id}/investment-return` | Get estimated annual return for an investment account |

### Transactions

| Method | Path | Description |
|--------|------|-------------|
| GET | `/transactions` | List transactions (supports filtering) |
| POST | `/transactions` | Create a transaction |
| GET | `/transactions/{id}` | Get transaction by ID |
| PUT | `/transactions/{id}` | Update transaction |
| DELETE | `/transactions/{id}` | Delete transaction |
| GET | `/transactions/transaction-types` | List transaction types |
| GET | `/transactions/transaction-statuses` | List transaction statuses |
| GET | `/transactions/transaction-details` | List transaction details (tag splits) |
| POST | `/transactions/transaction-details` | Create transaction detail |
| PUT | `/transactions/transaction-details/{id}` | Update transaction detail |
| DELETE | `/transactions/transaction-details/{id}` | Delete transaction detail |
| GET | `/transactions/attachments` | List attachments |
| POST | `/transactions/attachments` | Upload an attachment |
| DELETE | `/transactions/attachments/{id}` | Delete an attachment |
| GET | `/transactions/paychecks` | List paychecks |
| POST | `/transactions/paychecks` | Create paycheck |

### Tags

| Method | Path | Description |
|--------|------|-------------|
| GET | `/tags` | List tags |
| POST | `/tags` | Create tag |
| DELETE | `/tags/{id}` | Delete tag |
| GET | `/tags/tag-types` | List tag types |
| GET | `/tags/main-tags` | List main tags |
| POST | `/tags/main-tags` | Create main tag |
| GET | `/tags/sub-tags` | List sub-tags |
| POST | `/tags/sub-tags` | Create sub-tag |
| GET | `/tags/graph-by-tags` | Tag spending graph data |

### Reminders

| Method | Path | Description |
|--------|------|-------------|
| GET | `/reminders` | List reminders |
| POST | `/reminders` | Create reminder |
| GET | `/reminders/{id}` | Get reminder by ID |
| PUT | `/reminders/{id}` | Update reminder |
| DELETE | `/reminders/{id}` | Delete reminder |
| GET | `/reminders/repeat` | List repeat types |

### Planning

| Method | Path | Description |
|--------|------|-------------|
| GET | `/planning/budget` | List budgets |
| POST | `/planning/budget` | Create budget |
| PUT | `/planning/budget/{id}` | Update budget |
| DELETE | `/planning/budget/{id}` | Delete budget |
| GET | `/planning/graph` | Planning graph data |
| GET | `/planning/detected-recurring/` | List non-ignored detected recurring patterns |
| POST | `/planning/detected-recurring/{id}/ignore` | Mark a detection as ignored |
| DELETE | `/planning/detected-recurring/{id}` | Delete a detection |

### Reports

| Method | Path | Description |
|--------|------|-------------|
| GET | `/reports` | List saved reports |
| POST | `/reports` | Create/save a report |
| GET | `/reports/{id}` | Get report by ID |
| PUT | `/reports/{id}` | Update a saved report |
| DELETE | `/reports/{id}` | Delete a saved report |
| POST | `/reports/{id}/run` | Run a saved report and return results |
| GET | `/reports/{id}/results` | List historical run results for a report |

### Administration

| Method | Path | Description |
|--------|------|-------------|
| GET | `/administration/options` | Get application options |
| PUT | `/administration/options/{id}` | Update application options |
| GET | `/administration/version` | Get current version |
| GET | `/administration/health` | Health check |
| GET | `/administration/payees` | List payees |
| POST | `/administration/payees` | Create payee |
| GET | `/administration/messages` | List inbox messages |
| POST | `/administration/messages` | Create a system message |
| DELETE | `/administration/messages/{id}` | Delete a message |
| GET | `/administration/backups` | List backups |
| POST | `/administration/backups` | Create a backup |
| GET | `/administration/logs` | Retrieve application logs |
| GET | `/administration/push/vapid-public-key` | Get the VAPID public key |
| POST | `/administration/push/subscribe` | Register a push subscription for the current user |
| DELETE | `/administration/push/unsubscribe` | Remove the current user's push subscription |
| GET | `/administration/push/status` | Check if the current user has an active push subscription |

### Imports

| Method | Path | Description |
|--------|------|-------------|
| POST | `/file-imports` | Upload and process a CSV import |
| GET | `/file-imports` | List import records |

### Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/login` | Log in and obtain session |
| POST | `/auth/logout` | Log out |
| GET | `/auth/me` | Get current user info |

## Investment Return Response

`GET /accounts/{id}/investment-return` returns:

| Field | Type | Description |
|-------|------|-------------|
| `rate` | float \| null | Annualized return rate as a percentage (e.g. `7.42` = 7.42%). `null` when insufficient data. |
| `period_months` | int | Look-back window in months (always `12`) |
| `data_points` | int | Number of cleared transactions used in the calculation |
| `sufficient_data` | bool | `false` when the account is not an investment account, does not exist, or has no cleared transaction history |

## Transaction Filters

The `GET /transactions` endpoint supports the following query parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `account_id` | int | Filter by account |
| `search` | string | Search description field |
| `status_id` | int | Filter by status |
| `transaction_type_id` | int | Filter by transaction type |
| `tag_id` | int | Filter by tag |
| `date_from` | date | Start of date range (`YYYY-MM-DD`) |
| `date_to` | date | End of date range (`YYYY-MM-DD`) |
| `page` | int | Page number for pagination |
| `page_size` | int | Results per page |
