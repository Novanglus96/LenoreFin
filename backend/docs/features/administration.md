# Administration

The Administration section covers system management: users, authentication, application options, version info, backup/restore, and the log viewer.

## Accessing the Admin Panel

LenoreFin has two admin interfaces:

- **In-app admin** — accessible from the main navigation under **Admin**. Covers the most common administrative tasks.
- **Django admin** — available at `/django-admin/`. Full database-level access for advanced configuration.

## Users & Authentication

### Permission Groups

LenoreFin uses two built-in permission groups:

| Group | Permissions |
|-------|-------------|
| **Full Access** | Create, edit, and delete all data |
| **Readonly** | View-only access across the entire app |

Assign users to the appropriate group in **Django Admin → Authentication → Users**.

### API Keys

API key authentication is supported for programmatic access. Generate keys in **Django Admin → Authentication → API Keys** or via the in-app admin panel.

The frontend uses the API key set in `VITE_API_KEY`. Additional keys can be issued for scripts or integrations.

## Application Options

Navigate to **Admin → Options** to configure application-wide settings:

| Option | Description |
|--------|-------------|
| **Forecast Window** | Number of days to project in the balance forecast chart |
| **Currency** | Display currency (default: USD) |
| **Date Format** | Short date format used across the UI |

## Version

Navigate to **Admin → Version** to view the currently running version of LenoreFin. Use this to verify a successful upgrade.

## Backup & Restore

LenoreFin includes a built-in backup system accessible at **Admin → Backup & Restore**.

### Creating a Backup

Click **Export** to run a full data export. The export generates a JSON archive of all user data (accounts, transactions, tags, reminders, planning data, and options). The file is saved to the `/backups/` volume inside the container.

Click **Download** to retrieve the archive to your local machine.

### Restoring a Backup

Click **Import** and upload a previously exported archive. The restore operation replaces all existing data with the archive contents.

!!! warning
    Restore is destructive. All current data is replaced by the archive. Back up the current state before restoring.

### Automated Backups

The task worker runs a scheduled daily backup automatically. Backups accumulate in the `lenorefin_bkp` volume. Mount this volume to a persistent location and manage rotation externally (e.g. with a cron job or backup tool).

## Log Viewer

Navigate to **Admin → Logs** to view structured application logs.

| Control | Description |
|---------|-------------|
| **Level filter** | Show All, DEBUG, INFO, WARNING, ERROR, or CRITICAL |
| **Search** | Filter log lines by keyword |
| **Download bundle** | Download a zip archive of all log files for offline review |

The log viewer is useful for diagnosing errors, reviewing scheduled task output, and monitoring background job activity.

## Payees

Payees are reusable payee records linked to transactions. Navigate to **Admin → Payees** to add, edit, or remove payees.

Payees are optional — transactions can have a free-text description without a linked payee. Linking a payee enables paycheck splitting and payee-level filtering.

## System Messages

System messages are admin-authored notices displayed to all users on the dashboard. Use these to communicate maintenance windows, upgrade notices, or other system-wide alerts.

Manage system messages at **Admin → System Messages**.

## Banks

Banks are managed in **Django Admin → Accounts → Banks**. Each bank has:

- **Bank Name** — display name
- **Domain** — used to fetch the bank logo from [icon.horse](https://icon.horse)
- **Logo URL** — auto-populated from the domain; can be overridden manually

If a bank logo doesn't load correctly, verify the domain field and that `https://icon.horse/icon/{domain}` returns a valid image.
