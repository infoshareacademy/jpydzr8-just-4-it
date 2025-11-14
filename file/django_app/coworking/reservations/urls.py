from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('floor/<int:floor_number>/', views.floor_view, name='floor'),
    path('floor/<int:floor_number>/availability/', views.floor_availability, name='floor_availability'),
    path('desk/<int:desk_id>/modal/', views.reservation_modal, name='desk_modal'),
    path('desk/<int:desk_id>/reserve/', views.reserve, name='reserve'),
    path('reservation/<int:res_id>/ics/', views.reservation_ics, name='reservation_ics'),
    path('floor/<int:floor_number>/edit/', views.floor_edit, name='floor_edit'),
    path('desk/<int:desk_id>/position/', views.update_desk_position, name='update_desk_position'),
    path('floor/<int:floor_number>/ai/recommend/', views.ai_recommend, name='ai_recommend'),
    path('floor/<int:floor_number>/ai/surprise/', views.ai_surprise, name='ai_surprise'),
    path('floor/<int:floor_number>/ai/favorites/', views.ai_favorites, name='ai_favorites'),
    path('desk/<int:desk_id>/lock/', views.lock_desk_view, name='lock_desk'),
    path('desk/<int:desk_id>/unlock/', views.unlock_desk_view, name='unlock_desk'),
    path('reservation/<int:res_id>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    
    # Nowe funkcje
    path('recurring-reservations/', views.recurring_reservations, name='recurring_reservations'),
    path('desk/<int:desk_id>/recurring/', views.create_recurring_reservation, name='create_recurring'),
    path('desk/<int:desk_id>/waitlist/', views.add_to_waitlist, name='add_to_waitlist'),
    path('conference-rooms/', views.conference_rooms, name='conference_rooms'),
    path('floor/<int:floor_number>/conference-rooms/', views.conference_rooms, name='conference_rooms_floor'),
    path('conference-room/<int:room_id>/reserve/', views.conference_room_reservation, name='conference_room_reservation'),
    path('desk/<int:desk_id>/guest/', views.guest_reservation, name='guest_reservation'),
    path('recurring/<int:recurring_id>/cancel/', views.cancel_recurring, name='cancel_recurring'),
    path('advanced-features/', views.advanced_features, name='advanced_features'),
    path('notification-settings/', views.notification_settings, name='notification_settings'),
    path('api/notifications/subscribe/', views.subscribe_notifications, name='subscribe_notifications'),
    path('api/notifications/public-key/', views.notification_public_key, name='notification_public_key'),
    path('api/notifications/test/', views.test_push_notification, name='test_push_notification'),
    
    # Group Reservations
    path('floor/<int:floor_number>/group-reservations/', views.group_reservations, name='group_reservations'),
    path('floor/<int:floor_number>/suggest-group-desks/', views.suggest_group_desks_view, name='suggest_group_desks'),
    path('floor/<int:floor_number>/create-group/', views.create_group_reservation_view, name='create_group_reservation'),
    path('group-reservation/<int:group_id>/cancel/', views.cancel_group_reservation, name='cancel_group_reservation'),
    
    # Slack Integration
    path('slack/events/', views.slack_events, name='slack_events'),
    path('slack/commands/', views.slack_slash_commands, name='slack_commands'),
    path('slack/setup/', views.slack_setup, name='slack_setup'),
    path('reservation/<int:reservation_id>/download-ics/', views.download_ics, name='download_ics'),
]
