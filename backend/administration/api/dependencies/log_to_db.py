from administration.models import LogEntry
from django.shortcuts import get_object_or_404
from administration.models import Option


def logToDB(message, account, reminder, trans, error, level):
    """
    The function `logToDB` creates log entries, but only if the current logging level
    set in options is lower than the specified error level.

    Args:
        message (str): The log entry message.
        account (Account): Optional, the account associated with this entry.
        reminder (Reminder): Optional, the reminder associated with this entry.
        trans (Transaction): Optional, the transactions associated with this entry.
        error (int): Optional, any error number associated with this entry.
        level (ErrorLevel): The error level of this entry.

    Returns:
        success (int): Returns the id of the created log entry.
    """

    options = get_object_or_404(Option, id=1)
    if options.log_level.id <= level:
        log_entry = LogEntry.objects.create(
            log_entry=message,
            account_id=account,
            reminder_id=reminder,
            transaction_id=trans,
            error_num=error,
            error_level_id=level,
        )
        return_id = log_entry.id
    else:
        return_id = 0
    return {"success": return_id}
