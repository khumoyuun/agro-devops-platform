from django.urls import path
from .views import product_list, health, dashboard

urlpatterns = [
    path("", product_list, name="product_list"),
    path("health/", health, name="health"),
    path("dashboard/", dashboard, name="dashboard"),
]