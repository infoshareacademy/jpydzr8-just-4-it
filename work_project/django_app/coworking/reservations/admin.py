from django.contrib import admin
from .models import (
    Floor, Zone, Desk, Reservation, UserPreferences, DeskBookingLock,
    RecurringReservation, Waitlist, GuestReservation, Notification, 
    NotificationSubscription, GroupReservation, ConferenceRoom, ConferenceReservation
)

admin.site.register(Floor)
admin.site.register(Zone)
admin.site.register(Desk)
admin.site.register(Reservation)
admin.site.register(UserPreferences)
admin.site.register(DeskBookingLock)
admin.site.register(RecurringReservation)
admin.site.register(Waitlist)
admin.site.register(GuestReservation)
admin.site.register(Notification)
admin.site.register(NotificationSubscription)
admin.site.register(GroupReservation)
admin.site.register(ConferenceRoom)
admin.site.register(ConferenceReservation)
