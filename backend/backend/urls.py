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

api = NinjaAPI(auth=GlobalAuth())
api.title = "LenoreFin API"
api.version = "1.0.1"
api.description = "API documentation for LenoreFin"

# Add routers to the API
api.add_router("/", account_router)
api.add_router("/", account_type_router)
api.add_router("/", bank_router)
api.add_router("/", tag_type_router)
api.add_router("/", main_tag_router)
api.add_router("/", sub_tag_router)
api.add_router("/", tag_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),
]


admin.site.site_title = "LenoreFin site admin (DEV)"
admin.site.site_header = "LenoreFin administration"
admin.site.index_title = "Site administration"
