from django.urls import path

from .admin_views import AdminMeView, AdminUsersView, AdminPromoteUserView, AdminDemoteUserView, AdminAnalyticsView, AdminActivityView

urlpatterns = [
    path('me/', AdminMeView.as_view(), name='admin-me'),
    path('analytics/', AdminAnalyticsView.as_view(), name='admin-analytics'),
    path('activity/', AdminActivityView.as_view(), name='admin-activity'),
    path('users/', AdminUsersView.as_view(), name='admin-users'),
    path('users/promote/', AdminPromoteUserView.as_view(), name='admin-users-promote'),
    path('users/demote/', AdminDemoteUserView.as_view(), name='admin-users-demote'),
]
