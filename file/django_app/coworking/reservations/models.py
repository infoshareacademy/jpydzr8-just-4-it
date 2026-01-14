from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
class Floor(models.Model):
    number = models.IntegerField(unique=True)
    image_path = models.CharField(max_length=200, default='floorplans/floor4.png', help_text='Ścieżka do pliku z planem piętra')
    def __str__(self): return f"Floor {self.number}"
class Zone(models.Model):
    TYPE_CHOICES=[('OPEN','Open Workspace'),('DEEP','Deep Work'),('CHILL','Chill'),('KITCH','Kitchen'),('CONF','Conference')]
    floor=models.ForeignKey(Floor,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    type=models.CharField(max_length=5,choices=TYPE_CHOICES,default='OPEN')
    def __str__(self): return f"{self.name} (F{self.floor.number})"
class Desk(models.Model):
    floor=models.ForeignKey(Floor,on_delete=models.CASCADE)
    zone=models.ForeignKey(Zone,on_delete=models.SET_NULL,null=True,blank=True)
    label=models.CharField(max_length=50)
    has_dock=models.BooleanField(default=False)
    has_adjustable_desk=models.BooleanField(default=False)
    has_dual_monitors=models.BooleanField(default=False)
    is_deep_work=models.BooleanField(default=False)
    x_pct=models.DecimalField(max_digits=5,decimal_places=2,default=0)
    y_pct=models.DecimalField(max_digits=5,decimal_places=2,default=0)
    def __str__(self): return f"{self.label} (F{self.floor.number})"
class Reservation(models.Model):
    desk=models.ForeignKey(Desk,on_delete=models.CASCADE,related_name='reservations')
    name=models.CharField(max_length=120)
    email=models.EmailField()
    date=models.DateField()
    time_from=models.TimeField()
    time_to=models.TimeField()
    is_cancelled=models.BooleanField(default=False)
    cancelled_at=models.DateTimeField(null=True,blank=True)
    class Meta:
        unique_together=('desk','date','time_from','time_to')
    def __str__(self): return f"{self.desk.label} {self.date} {self.time_from}-{self.time_to} by {self.name}"

class UserPreferences(models.Model):
    email = models.EmailField(unique=True)
    preferred_dock = models.BooleanField(default=False)
    preferred_dual_monitors = models.BooleanField(default=False)
    preferred_adjustable_desk = models.BooleanField(default=False)
    preferred_deep_work = models.BooleanField(default=False)
    preferred_floor = models.ForeignKey(Floor, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    reminder_before_booking = models.IntegerField(default=30, help_text='Przypomnienie X minut przed rezerwacją')
    daily_summary = models.BooleanField(default=True)
    weekly_report = models.BooleanField(default=False)
    waitlist_notifications = models.BooleanField(default=True)
    cancellation_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self): return f"Preferences for {self.email}"

class DeskBookingLock(models.Model):
    desk = models.ForeignKey(Desk, on_delete=models.CASCADE)
    email = models.EmailField()
    locked_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('desk', 'email')
    
    def __str__(self): return f"Lock for {self.desk.label} by {self.email} until {self.locked_until}"

class RecurringReservation(models.Model):
    FREQUENCY_CHOICES = [
        ('DAILY', 'Codziennie'),
        ('WEEKLY', 'Tygodniowo'),
        ('MONTHLY', 'Miesięcznie'),
    ]
    
    desk = models.ForeignKey(Desk, on_delete=models.CASCADE, related_name='recurring_reservations')
    name = models.CharField(max_length=120)
    email = models.EmailField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    time_from = models.TimeField()
    time_to = models.TimeField()
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='DAILY')
    days_of_week = models.CharField(max_length=7, default='1111111', help_text='1=Monday, 7=Sunday')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self): return f"Recurring {self.frequency} {self.desk.label} by {self.name}"

class Waitlist(models.Model):
    desk = models.ForeignKey(Desk, on_delete=models.CASCADE, related_name='waitlist')
    name = models.CharField(max_length=120)
    email = models.EmailField()
    preferred_date = models.DateField()
    time_from = models.TimeField()
    time_to = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_notified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self): return f"Waitlist {self.desk.label} by {self.name} on {self.preferred_date}"


class ConferenceRoom(models.Model):
    name = models.CharField(max_length=100)
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True)
    capacity = models.IntegerField(default=4)
    description = models.TextField(blank=True)
    has_projector = models.BooleanField(default=False)
    has_whiteboard = models.BooleanField(default=False)
    has_video_conference = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    def __str__(self): return f"Conference Room {self.name} (F{self.floor.number})"

class ConferenceReservation(models.Model):
    conference_room = models.ForeignKey(ConferenceRoom, on_delete=models.CASCADE, related_name='reservations')
    team_name = models.CharField(max_length=120)
    contact_email = models.EmailField()
    date = models.DateField()
    time_from = models.TimeField()
    time_to = models.TimeField()
    attendees_count = models.IntegerField(default=1)
    purpose = models.CharField(max_length=200, blank=True)
    is_cancelled = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('conference_room', 'date', 'time_from', 'time_to')
    
    def __str__(self): return f"Conference {self.team_name} in {self.conference_room.name} on {self.date}"

class GuestReservation(models.Model):
    desk = models.ForeignKey(Desk, on_delete=models.CASCADE, related_name='guest_reservations')
    guest_name = models.CharField(max_length=120)
    guest_email = models.EmailField()
    host_name = models.CharField(max_length=120)
    host_email = models.EmailField()
    date = models.DateField()
    time_from = models.TimeField()
    time_to = models.TimeField()
    purpose = models.CharField(max_length=200, blank=True)
    is_cancelled = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('desk', 'date', 'time_from', 'time_to')
    
    def __str__(self): return f"Guest {self.guest_name} hosted by {self.host_name} on {self.date}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('REMINDER', 'Przypomnienie o rezerwacji'),
        ('CANCELLATION', 'Anulowanie rezerwacji'),
        ('WAITLIST', 'Powiadomienie z waitlist'),
        ('DAILY_SUMMARY', 'Dzienne podsumowanie'),
        ('WEEKLY_REPORT', 'Tygodniowy raport'),
        ('CONFIRMATION', 'Potwierdzenie rezerwacji'),
    ]
    
    email = models.EmailField()
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self): return f"{self.type} for {self.email} - {self.title}"

class NotificationSubscription(models.Model):
    email = models.EmailField()
    endpoint = models.URLField()
    p256dh_key = models.CharField(max_length=255)
    auth_key = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('email', 'endpoint')
    
    def __str__(self): return f"Push subscription for {self.email}"

class GroupReservation(models.Model):
    """Rezerwacja grupy stanowisk obok siebie"""
    group_name = models.CharField(max_length=120)
    organizer_email = models.EmailField()
    date = models.DateField()
    time_from = models.TimeField()
    time_to = models.TimeField()
    desks = models.ManyToManyField(Desk, related_name='group_reservations')
    purpose = models.CharField(max_length=200, blank=True)
    is_cancelled = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self): return f"Group {self.group_name} - {self.desks.count()} desks on {self.date}"
