"""Dashboard (non-admin) API URLs."""

from django.urls import path

from .dashboard_views import DashboardInsightsView

urlpatterns = [
    path('dashboard/insights/', DashboardInsightsView.as_view(), name='dashboard-insights'),
]
