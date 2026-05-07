def account_real_transactions(account_id: int) -> str:
    return f"account:{account_id}:transactions:real"


def account_reminder_transactions(account_id: int) -> str:
    return f"account:{account_id}:transactions:reminder"


def account_forecast_transactions(account_id: int) -> str:
    return f"account:{account_id}:transactions:forecast"


def account_combined_transactions(account_id: int) -> str:
    return f"account:{account_id}:transactions:combined"


def account_pending_balance(account_id: int) -> str:
    return f"account:{account_id}:balance:pending"


def account_cleared_balance(account_id: int) -> str:
    return f"account:{account_id}:balance:cleared"


def account_financials(account_id: int) -> str:
    return f"account:{account_id}:financials"


def account_all(account_id: int) -> str:
    return f"account:{account_id}:"


def account_all_balances(account_id: int) -> str:
    return f"account:{account_id}:balance"


def account_all_transactions(account_id: int) -> str:
    return f"account:{account_id}:transactions"
