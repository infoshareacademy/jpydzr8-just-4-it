from django.urls import path
from . import dashboard_views
from . import profile_views

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard
    path('', dashboard_views.dashboard, name='dashboard'),
    
    # API endpoints
    path('api/reservations/calendar/', dashboard_views.api_reservations_calendar, name='api_reservations_calendar'),
    path('api/reservations/summary/', dashboard_views.api_reservations_summary, name='api_reservations_summary'),
    path('api/quick-reserve/', dashboard_views.api_quick_reserve, name='api_quick_reserve'),
    path('api/notifications/', dashboard_views.api_notifications, name='api_notifications'),
    path('api/notifications/<int:notification_id>/read/', dashboard_views.api_mark_notification_read, name='api_mark_notification_read'),
    
    # Profile endpoints
    path('api/profile/', profile_views.get_user_profile, name='api_user_profile'),
    path('api/profile/update/', profile_views.update_user_profile, name='api_update_profile'),
    path('api/profile/change-password/', profile_views.change_password, name='api_change_password'),
    path('api/profile/statistics/', profile_views.get_user_statistics, name='api_user_statistics'),
]

