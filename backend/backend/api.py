from ninja import NinjaAPI
from administration.api.dependencies.auth import SessionAuth
from administration.api.dependencies.version import get_version
from administration.api.routers.auth import auth_router

# Import routers from apps
from accounts.api.routers.account_type import account_type_router
from accounts.api.routers.bank import bank_router
from accounts.api.routers.account import account_router
from tags.api.routers.tag_type import tag_type_router
from tags.api.routers.main_tag import main_tag_router
from tags.api.routers.sub_tag import sub_tag_router
from tags.api.routers.tag import tag_router
from planning.api.routers.contrib_rule import contrib_rule_router
from planning.api.routers.contribution import contribution_router
from transactions.api.routers.transaction_type import transaction_type_router
from reminders.api.routers.repeat import repeat_router
from accounts.api.routers.forecast import forecast_router
from reminders.api.routers.reminder import reminder_router
from planning.api.routers.note import note_router
from administration.api.routers.option import option_router
from transactions.api.routers.transaction_status import (
    transaction_status_router,
)
from administration.api.routers.payee import payee_router
from transactions.api.routers.paycheck import paycheck_router
from transactions.api.routers.transaction import transaction_router
from administration.api.routers.message import message_router
from transactions.api.routers.transaction_detail import (
    transaction_detail_router,
)
from tags.api.routers.tag_graph import tag_graph_router
from tags.api.routers.graph_by_tags import graph_by_tags_router
from imports.api.routers.import_file import import_file_router
from administration.api.routers.version import version_router
from administration.api.routers.decription_history import (
    description_history_router,
)
from planning.api.routers.calculator import calculator_router
from planning.api.routers.planning_graph import planning_graph_router
from planning.api.routers.budget import budget_router
from planning.api.routers.retirement import retirement_router
from administration.api.routers.health import health_router
from administration.api.routers.backup import backup_router

api = NinjaAPI(auth=SessionAuth())
api.title = "LenoreFin API"
api.version = get_version()
api.description = "API documentation for LenoreFin"

# Add routers to the API
api.add_router("/accounts", account_router)
api.add_router("/accounts/account-types", account_type_router)
api.add_router("/accounts/banks", bank_router)
api.add_router("/tags/tag-types", tag_type_router)
api.add_router("/tags/main-tags", main_tag_router)
api.add_router("/tags/sub-tags", sub_tag_router)
api.add_router("/tags", tag_router)
api.add_router("/planning/contrib-rules", contrib_rule_router)
api.add_router("/planning/contributions", contribution_router)
api.add_router("/transactions/transaction-types", transaction_type_router)
api.add_router("/reminders/repeat", repeat_router)
api.add_router("/accounts/forecast", forecast_router)
api.add_router("/reminders", reminder_router)
api.add_router("/planning/notes", note_router)
api.add_router("/administration/options", option_router)
api.add_router("/transactions/transaction-statuses", transaction_status_router)
api.add_router("/administration/payees", payee_router)
api.add_router("/transactions/paychecks", paycheck_router)
api.add_router("/transactions", transaction_router)
api.add_router("/administration/messages", message_router)
api.add_router("/transactions/transaction-details", transaction_detail_router)
api.add_router("/tags/tag-graphs", tag_graph_router)
api.add_router("/tags/graph-by-tags", graph_by_tags_router)
api.add_router("/file-imports", import_file_router)
api.add_router("/administration/version", version_router)
api.add_router(
    "/administration/description-histories", description_history_router
)
api.add_router("/planning/calculator", calculator_router)
api.add_router("/planning/graph", planning_graph_router)
api.add_router("/planning/budget", budget_router)
api.add_router("/planning/retirement", retirement_router)
api.add_router("/administration/health", health_router)
api.add_router("/administration/backups", backup_router)
api.add_router("/auth", auth_router)
