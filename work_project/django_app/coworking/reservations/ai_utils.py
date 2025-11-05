import random
from .models import Desk, Reservation, UserPreferences, DeskBookingLock
from datetime import datetime, date, time, timedelta
from django.utils import timezone
def is_available(desk, when, t_from, t_to):
    return not Reservation.objects.filter(desk=desk,date=when,time_from__lt=t_to,time_to__gt=t_from,is_cancelled=False).exists()
def recommend_desks(floor,prefs,when,t_from,t_to,limit=3):
    qs=Desk.objects.filter(floor=floor)
    if prefs.get('dock'): qs=qs.filter(has_dock=True)
    if prefs.get('adjustable'): qs=qs.filter(has_adjustable_desk=True)
    if prefs.get('dual'): qs=qs.filter(has_dual_monitors=True)
    if prefs.get('deep'): qs=qs.filter(is_deep_work=True)
    desks=[d for d in qs if is_available(d,when,t_from,t_to)]
    if not desks: desks=[d for d in Desk.objects.filter(floor=floor) if is_available(d,when,t_from,t_to)]
    return desks[:limit]
def surprise_me(floor,when,t_from,t_to):
    c=[d for d in Desk.objects.filter(floor=floor) if is_available(d,when,t_from,t_to)]
    return random.choice(c) if c else None
def alternative_for(desk,when,t_from,t_to):
    qs=Desk.objects.filter(floor=desk.floor).exclude(id=desk.id).filter(
        has_dock=desk.has_dock, has_adjustable_desk=desk.has_adjustable_desk,
        has_dual_monitors=desk.has_dual_monitors, is_deep_work=desk.is_deep_work)
    for d in qs:
        if is_available(d,when,t_from,t_to): return d
    if desk.zone:
        for d in Desk.objects.filter(zone=desk.zone).exclude(id=desk.id):
            if is_available(d,when,t_from,t_to): return d
    for d in Desk.objects.filter(floor=desk.floor).exclude(id=desk.id):
        if is_available(d,when,t_from,t_to): return d
    return None

def get_user_favorites(email, floor, when, t_from, t_to, limit=3):
    """Pobierz ulubione stanowiska użytkownika na podstawie preferencji"""
    try:
        prefs = UserPreferences.objects.get(email=email)
        qs = Desk.objects.filter(floor=floor)
        
        # Filtruj na podstawie preferencji użytkownika
        if prefs.preferred_dock: qs = qs.filter(has_dock=True)
        if prefs.preferred_dual_monitors: qs = qs.filter(has_dual_monitors=True)
        if prefs.preferred_adjustable_desk: qs = qs.filter(has_adjustable_desk=True)
        if prefs.preferred_deep_work: qs = qs.filter(is_deep_work=True)
        
        # Zwróć dostępne stanowiska
        available_desks = [d for d in qs if is_available(d, when, t_from, t_to)]
        return available_desks[:limit]
    except UserPreferences.DoesNotExist:
        return []

def save_user_preferences(email, prefs_data):
    """Zapisz preferencje użytkownika"""
    prefs, created = UserPreferences.objects.get_or_create(
        email=email,
        defaults={
            'preferred_dock': prefs_data.get('dock', False),
            'preferred_dual_monitors': prefs_data.get('dual', False),
            'preferred_adjustable_desk': prefs_data.get('adjustable', False),
            'preferred_deep_work': prefs_data.get('deep', False),
        }
    )
    if not created:
        prefs.preferred_dock = prefs_data.get('dock', prefs.preferred_dock)
        prefs.preferred_dual_monitors = prefs_data.get('dual', prefs.preferred_dual_monitors)
        prefs.preferred_adjustable_desk = prefs_data.get('adjustable', prefs.preferred_adjustable_desk)
        prefs.preferred_deep_work = prefs_data.get('deep', prefs.preferred_deep_work)
        prefs.save()
    return prefs

def lock_desk(desk, email, duration_minutes=5):
    """Zablokuj stanowisko na określony czas"""
    locked_until = timezone.now() + timedelta(minutes=duration_minutes)
    lock, created = DeskBookingLock.objects.get_or_create(
        desk=desk,
        email=email,
        defaults={'locked_until': locked_until}
    )
    if not created:
        lock.locked_until = locked_until
        lock.save()
    return lock

def is_desk_locked(desk, email):
    """Sprawdź czy stanowisko jest zablokowane"""
    try:
        lock = DeskBookingLock.objects.get(desk=desk, email=email)
        if lock.locked_until > timezone.now():
            return True
        else:
            lock.delete()  # Usuń wygasłe blokady
            return False
    except DeskBookingLock.DoesNotExist:
        return False

def unlock_desk(desk, email):
    """Odblokuj stanowisko"""
    DeskBookingLock.objects.filter(desk=desk, email=email).delete()

def cleanup_expired_locks():
    """Usuń wygasłe blokady"""
    DeskBookingLock.objects.filter(locked_until__lt=timezone.now()).delete()
