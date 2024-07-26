"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from ninja import NinjaAPI
from administration.api.dependencies.auth import GlobalAuth

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
from administration.api.routers.error_level import error_level_router
from transactions.api.routers.transaction_type import transaction_type_router
from reminders.api.routers.repeat import repeat_router
from accounts.api.routers.forecast import forecast_router

api = NinjaAPI(auth=GlobalAuth())
api.title = "LenoreFin API"
api.version = "1.0.1"
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
api.add_router("/administration/error-levels", error_level_router)
api.add_router("/transactions/transaction-types", transaction_type_router)
api.add_router("/reminders/repeat", repeat_router)
api.add_router("/accounts/forecast", forecast_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),
]


admin.site.site_title = "LenoreFin site admin (DEV)"
admin.site.site_header = "LenoreFin administration"
admin.site.index_title = "Site administration"
