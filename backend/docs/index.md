# LenoreFin

<div align="center">
  <img src="images/logov2.png" alt="LenoreFin" height="60">
  <p><em>A self-hosted personal finance tracker built for privacy and control.</em></p>
</div>

---

LenoreFin began as a simple spreadsheet and grew into a full-featured finance tracker designed for self-hosting. Your data stays on your own infrastructure — no third-party syncing, no telemetry, no subscription fees.

## Features at a Glance

| Area | What you get |
|------|-------------|
| **Accounts** | Checking, savings, credit cards, investments, loans; parent accounts for combined views; bank logo display |
| **Transactions** | Full CRUD, bulk editing, CSV import, file attachments, tag-based categorization, filtering |
| **Credit Cards** | Statement cycle tracking, due dates, minimum payment calculation, rewards tracking |
| **Forecasting** | Balance forecast chart per account; configurable time window |
| **Budgeting** | Tag-based budget, savings goal tracking |
| **Reminders** | Recurring bill reminders with customizable repeat schedules |
| **Reporting** | Totals and year-over-year comparison reports; filterable by account, tag, and status |
| **Logging** | Structured log viewer with level filtering and downloadable log bundle |
| **Auth** | Full Access and Readonly permission groups; API key authentication |
| **PWA** | Installable as a Progressive Web App; offline read-only mode |
| **Self-hosted** | Single Docker image; PostgreSQL + Redis; no external dependencies |

## Stack

- **Backend**: Django 5.2 + Django Ninja (REST API) + PostgreSQL + Redis
- **Frontend**: Vue 3 + Vuetify 3 + Pinia + TanStack Query
- **Task Queue**: django-q2 (scheduled tasks and async jobs)
- **Deployment**: Single Docker image with nginx + gunicorn + supervisord + worker

## Quick Start

See the [Installation guide](getting-started.md) to get up and running with Docker Compose in minutes.

## Links

- [GitHub Repository](https://github.com/Novanglus96/LenoreFin)
- [Report a Bug](https://github.com/Novanglus96/LenoreFin/issues/new?template=bug_report.md)
- [Request a Feature](https://github.com/Novanglus96/LenoreFin/issues/new?template=feature_request.md)
- [Support on Patreon](https://www.patreon.com/novanglus)
