from django.urls import path, include, re_path
from django.shortcuts import redirect
from rest_framework.routers import DefaultRouter
from .views_occupied import SeatsOccupiedView
from .views import (
    CsrfTokenView, LoginView, RegisterView, LogoutView, MeView, ReservationViewSet, 
    ics_reservation, ics_reservation_cancel,
    MagicLinkLoginView, MagicLinkAuthenticateView,
    CheckAuthPreferenceView, UpdateAuthPreferenceView
)
from .admin_views import (
    admin_dashboard_stats, bulk_user_operations, bulk_reservation_operations,
    export_reservations_csv, export_users_csv, system_health_check
)
from .mobile_views import (
    mobile_dashboard, mobile_api_stats, mobile_quick_action,
    mobile_user_activity, mobile_reservation_insights, mobile_bulk_operation,
    mobile_notifications, modern_dashboard
)
from .report_views import (
    generate_report_api, download_report, list_reports
)
from .dashboard_urls import urlpatterns as dashboard_urls

router = DefaultRouter()
router.trailing_slash = '/?'
router.register('reservations', ReservationViewSet, basename='reservation')

def _reservations_redirect(request):
    qs = request.META.get('QUERY_STRING') or ''
    return redirect('/api/reservations/' + (f'?{qs}' if qs else ''), permanent=False)

urlpatterns = [
    # Auth endpoints
    path('auth/csrf', CsrfTokenView.as_view(), name='csrf'),
    path('auth/register', RegisterView.as_view(), name='register'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('auth/logout', LogoutView.as_view(), name='logout'),
    path('auth/me', MeView.as_view(), name='me'),
    
    # Magic Link endpoints
    path('auth/magic-link-login/', MagicLinkLoginView.as_view(), name='magic_link_login'),
    path('auth/magic-link/<str:token>/', MagicLinkAuthenticateView.as_view(), name='magic_link_authenticate'),
    
    # Authentication preference endpoints
    path('auth/check-preference', CheckAuthPreferenceView.as_view(), name='check_auth_preference'),
    path('auth/update-preference', UpdateAuthPreferenceView.as_view(), name='update_auth_preference'),
    
    # Public endpoints
    path('seats/occupied', SeatsOccupiedView.as_view(), name='seats_occupied'),
    path('ics/reservations/<str:pk>.ics', ics_reservation, name='ics_reservation'),
    path('ics/reservations/<str:pk>/cancel.ics', ics_reservation_cancel, name='ics_reservation_cancel'),
    
    # Admin endpoints (superuser only)
    path('admin/stats', admin_dashboard_stats, name='admin_stats'),
    path('admin/users/bulk', bulk_user_operations, name='bulk_user_ops'),
    path('admin/reservations/bulk', bulk_reservation_operations, name='bulk_reservation_ops'),
    path('admin/export/reservations', export_reservations_csv, name='export_reservations'),
    path('admin/export/users', export_users_csv, name='export_users'),
    path('admin/health', system_health_check, name='system_health'),
    
    # Mobile endpoints (superuser only)
    path('mobile/dashboard', mobile_dashboard, name='mobile_dashboard'),
    path('admin/dashboard', modern_dashboard, name='modern_dashboard'),
    path('mobile/api/stats', mobile_api_stats, name='mobile_stats'),
    path('mobile/api/quick-action', mobile_quick_action, name='mobile_quick_action'),
    path('mobile/api/user-activity', mobile_user_activity, name='mobile_user_activity'),
    path('mobile/api/reservation-insights', mobile_reservation_insights, name='mobile_insights'),
    path('mobile/api/bulk-operation', mobile_bulk_operation, name='mobile_bulk'),
    path('mobile/api/notifications', mobile_notifications, name='mobile_notifications'),
    
    # Report endpoints (superuser only)
    path('admin/generate-report', generate_report_api, name='generate_report_api'),
    path('admin/download-report', download_report, name='download_report'),
    path('admin/list-reports', list_reports, name='list_reports'),
    
    # Dashboard endpoints
    path('dashboard/', include(dashboard_urls)),
    
    # Router URLs
    re_path('^reservations$', _reservations_redirect),
    path('', include(router.urls))
]