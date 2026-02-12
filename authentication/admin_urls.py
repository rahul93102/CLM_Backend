from django.urls import path

from .admin_views import (
    AdminMeView,
    AdminUsersView,
    AdminPromoteUserView,
    AdminDemoteUserView,
    AdminAnalyticsView,
    AdminActivityView,
    AdminFeatureUsageView,
    AdminUserRegistrationView,
    AdminUserFeatureUsageView,
)

urlpatterns = [
    path('me/', AdminMeView.as_view(), name='admin-me'),
    path('analytics/', AdminAnalyticsView.as_view(), name='admin-analytics'),
    path('activity/', AdminActivityView.as_view(), name='admin-activity'),
    path('feature-usage/', AdminFeatureUsageView.as_view(), name='admin-feature-usage'),
    path('user-registration/', AdminUserRegistrationView.as_view(), name='admin-user-registration'),
    path('user-feature-usage/', AdminUserFeatureUsageView.as_view(), name='admin-user-feature-usage'),
    path('users/', AdminUsersView.as_view(), name='admin-users'),
    path('users/promote/', AdminPromoteUserView.as_view(), name='admin-users-promote'),
    path('users/demote/', AdminDemoteUserView.as_view(), name='admin-users-demote'),
]
