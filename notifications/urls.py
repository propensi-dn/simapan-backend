from django.urls import path
from . import views

urlpatterns = [
    # PBI-41 — list + mark all read
    path('', views.NotificationListView.as_view(), name='notification-list'),

    # Bell badge count — lightweight
    path('unread-count/', views.UnreadCountView.as_view(), name='notification-unread-count'),

    # PBI-42 — detail + mark single read
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
]