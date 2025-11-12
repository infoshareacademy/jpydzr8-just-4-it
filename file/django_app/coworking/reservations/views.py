import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.conf import settings
from datetime import datetime, date, time
import json
from .models import Floor, Desk, Reservation, UserPreferences, DeskBookingLock, RecurringReservation, Waitlist, GuestReservation, Notification, NotificationSubscription, GroupReservation, ConferenceRoom, ConferenceReservation
from .forms import ReservationForm, RecurringReservationForm, WaitlistForm, GuestReservationForm, GroupReservationForm, ConferenceReservationForm
from .ai_utils import recommend_desks, surprise_me, alternative_for, is_available, get_user_favorites, save_user_preferences, lock_desk, is_desk_locked, unlock_desk, cleanup_expired_locks
from .recurring_utils import generate_recurring_reservations, check_waitlist_availability
from .notification_utils import send_reservation_reminder, send_waitlist_notification, send_cancellation_notification
from .push_notifications import send_push_notification, is_webpush_enabled
from .group_utils import find_adjacent_desks, suggest_group_desks, create_group_reservation
from .slack_bot import slack_events, slack_slash_commands


logger = logging.getLogger('reservations.booking')

def send_reservation_email(reservation):
    """Wyślij email z potwierdzeniem rezerwacji"""
    # Sprawdź czy konfiguracja email jest dostępna
    from django.conf import settings
    
    subject = f'Potwierdzenie rezerwacji - Stanowisko {reservation.desk.label}'
    
    # HTML template dla emaila
    html_message = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
            <h1 style="margin: 0; font-size: 24px;">Rezerwacja potwierdzona!</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">Stanowisko {reservation.desk.label} - Piętro {reservation.desk.floor.number}</p>
        </div>
        
        <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e2e8f0;">
            <div style="background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h2 style="color: #2d3748; margin: 0 0 20px 0; font-size: 20px;">Szczegoly rezerwacji</h2>
                
                <div style="display: grid; gap: 15px;">
                    <div style="display: flex; justify-content: space-between; padding: 12px; background: #f7fafc; border-radius: 6px;">
                        <span style="font-weight: 600; color: #4a5568;">Stanowisko:</span>
                        <span style="color: #2d3748;">{reservation.desk.label}</span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; padding: 12px; background: #f7fafc; border-radius: 6px;">
                        <span style="font-weight: 600; color: #4a5568;">Piętro:</span>
                        <span style="color: #2d3748;">{reservation.desk.floor.number}</span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; padding: 12px; background: #f7fafc; border-radius: 6px;">
                        <span style="font-weight: 600; color: #4a5568;">Data:</span>
                        <span style="color: #2d3748;">{reservation.date.strftime('%d.%m.%Y')}</span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; padding: 12px; background: #f7fafc; border-radius: 6px;">
                        <span style="font-weight: 600; color: #4a5568;">Godziny:</span>
                        <span style="color: #2d3748;">{reservation.time_from.strftime('%H:%M')} - {reservation.time_to.strftime('%H:%M')}</span>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; padding: 12px; background: #f7fafc; border-radius: 6px;">
                        <span style="font-weight: 600; color: #4a5568;">Rezerwujący:</span>
                        <span style="color: #2d3748;">{reservation.name}</span>
                    </div>
                </div>
                
                <div style="margin-top: 25px; padding: 20px; background: #e6fffa; border-left: 4px solid #38b2ac; border-radius: 4px;">
                    <h3 style="margin: 0 0 10px 0; color: #234e52; font-size: 16px;">Udogodnienia stanowiska:</h3>
                    <div style="color: #2c7a7b; font-size: 14px;">
                        {'Dock ' if reservation.desk.has_dock else ''}
                        {'Regulowane biurko ' if reservation.desk.has_adjustable_desk else ''}
                        {'2 monitory ' if reservation.desk.has_dual_monitors else ''}
                        {'Deep Work ' if reservation.desk.is_deep_work else ''}
                        {'' if any([reservation.desk.has_dock, reservation.desk.has_adjustable_desk, reservation.desk.has_dual_monitors, reservation.desk.is_deep_work]) else 'Podstawowe wyposażenie'}
                    </div>
                </div>
                
                <div style="margin-top: 25px; text-align: center;">
                    <p style="color: #718096; font-size: 14px; margin: 0;">
                        <strong>Wskazowka:</strong> Mozesz anulowac rezerwacje w dowolnym momencie w systemie rezerwacji.
                    </p>
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 20px; color: #a0aec0; font-size: 12px;">
            <p>Ten email został wygenerowany automatycznie przez system rezerwacji stanowisk.</p>
        </div>
    </div>
    """
    
    # Plain text version
    text_message = f"""
Potwierdzenie rezerwacji stanowiska

Stanowisko: {reservation.desk.label}
Piętro: {reservation.desk.floor.number}
Data: {reservation.date.strftime('%d.%m.%Y')}
Godziny: {reservation.time_from.strftime('%H:%M')} - {reservation.time_to.strftime('%H:%M')}
Rezerwujący: {reservation.name}

Udogodnienia:
{'Dock ' if reservation.desk.has_dock else ''}
{'Regulowane biurko ' if reservation.desk.has_adjustable_desk else ''}
{'2 monitory ' if reservation.desk.has_dual_monitors else ''}
{'Deep Work ' if reservation.desk.is_deep_work else ''}

Możesz anulować rezerwację w dowolnym momencie w systemie rezerwacji.

---
System rezerwacji stanowisk
    """
    
    logger.info(
        "Rozpoczynam wysyłkę emaila: reservation_id=%s email=%s desk_id=%s",
        reservation.id,
        reservation.email,
        reservation.desk_id,
    )
    try:
        result = send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email='noreply@office-reservations.com',
            recipient_list=[reservation.email],
            fail_silently=True,  # Nie rzucaj wyjątku w przypadku błędu email
        )
        # W trybie deweloperskim email będzie wyświetlony w konsoli
    except Exception as e:
        logger.exception(
            "Błąd podczas wysyłki emaila: reservation_id=%s email=%s",
            reservation.id,
            reservation.email,
        )
        # Nie rzucaj wyjątku - email nie jest krytyczny dla rezerwacji
    else:
        if result:
            logger.info(
                "Email z potwierdzeniem wysłany: reservation_id=%s email=%s",
                reservation.id,
                reservation.email,
            )
        else:
            logger.warning(
                "Backend email zwrócił status niepowodzenia (result=0): reservation_id=%s email=%s",
                reservation.id,
                reservation.email,
            )

def home(request): return redirect('floor', floor_number=4)

def floor_view(request, floor_number:int):
    floor=get_object_or_404(Floor, number=floor_number)
    desks=Desk.objects.filter(floor=floor).select_related('zone')
    return render(request,'reservations/floor.html',{'floors':Floor.objects.order_by('number'),'floor':floor,'desks':desks})

def reservation_modal(request, desk_id:int):
    desk=get_object_or_404(Desk,id=desk_id)
    return render(request,'reservations/_desk_modal.html',{'desk':desk,'form':ReservationForm()})

def reserve(request, desk_id:int):
    desk=get_object_or_404(Desk,id=desk_id)
    
    if request.method == 'GET':
        form = ReservationForm()
        return render(request,'reservations/reserve.html',{'desk':desk,'form':form})
    
    if request.method == 'POST':
        form=ReservationForm(request.POST)
        if form.is_valid():
            res=form.save(commit=False); res.desk=desk
            logger.info(
                "Próba rezerwacji: desk_id=%s label=%s email=%s date=%s time_from=%s time_to=%s",
                desk.id,
                desk.label,
                res.email,
                res.date.isoformat() if res.date else None,
                res.time_from.isoformat() if res.time_from else None,
                res.time_to.isoformat() if res.time_to else None,
            )
            if not is_available(desk,res.date,res.time_from,res.time_to):
                alt=alternative_for(desk,res.date,res.time_from,res.time_to)
                logger.warning(
                    "Rezerwacja odrzucona - stanowisko niedostępne: desk_id=%s label=%s email=%s date=%s time_from=%s time_to=%s",
                    desk.id,
                    desk.label,
                    res.email,
                    res.date.isoformat() if res.date else None,
                    res.time_from.isoformat() if res.time_from else None,
                    res.time_to.isoformat() if res.time_to else None,
                )
                return render(request,'reservations/reserve.html',{'desk':desk,'form':form,'error':'To miejsce jest już zajęte.','alternative':alt})
            res.save()
            logger.info(
                "Rezerwacja utworzona: reservation_id=%s desk_id=%s label=%s email=%s",
                res.id,
                desk.id,
                desk.label,
                res.email,
            )
            
            # Wyślij email z potwierdzeniem (nie blokuj rezerwacji w przypadku błędu)
            try:
                send_reservation_email(res)
                # Email zostanie wyświetlony w konsoli (console.EmailBackend w trybie dev)
            except Exception as e:
                logger.exception(
                    "Nieoczekiwany wyjątek przy wysyłce emaila: reservation_id=%s email=%s",
                    res.id,
                    res.email,
                )
                # Nie przerywaj procesu rezerwacji w przypadku błędu email
            
            # Odblokuj stanowisko po udanej rezerwacji
            try:
                unlock_desk(desk, res.email)
            except Exception as e:
                logger.exception(
                    "Błąd odblokowywania stanowiska: reservation_id=%s desk_id=%s email=%s",
                    res.id,
                    desk.id,
                    res.email,
                )
                # Nie przerywaj procesu rezerwacji w przypadku błędu odblokowywania
            
            return render(request,'reservations/reservation_success.html',{'reservation':res})
        return render(request,'reservations/reserve.html',{'desk':desk,'form':form})
    
    return HttpResponseBadRequest('Method not allowed')

def _ics_datetime(d,t): return f"{d.strftime('%Y%m%d')}T{t.strftime('%H%M%S')}"

def reservation_ics(request,res_id:int):
    res=get_object_or_404(Reservation,id=res_id)
    dtstart=_ics_datetime(res.date,res.time_from); dtend=_ics_datetime(res.date,res.time_to)
    lines=["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//Office Reservation//EN","CALSCALE:GREGORIAN","METHOD:PUBLISH","BEGIN:VEVENT",
           f"UID:{res.id}@office.local",f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
           f"DTSTART:{dtstart}",f"DTEND:{dtend}",f"SUMMARY:Rezerwacja: {res.desk.label}",f"LOCATION:Piętro {res.desk.floor.number}",
           f"DESCRIPTION:Stanowisko: {res.desk.label}","END:VEVENT","END:VCALENDAR"]
    ics='\r\n'.join(lines)+'\r\n'
    resp=HttpResponse(ics,content_type='text/calendar; charset=utf-8')
    resp['Content-Disposition']=f'attachment; filename="reservation_{res.id}.ics"'
    return resp

def ai_recommend(request,floor_number:int):
    floor=get_object_or_404(Floor,number=floor_number)
    prefs={'dock':request.GET.get('dock')=='1','dual':request.GET.get('dual')=='1',
           'adjustable':request.GET.get('adjustable')=='1','deep':request.GET.get('deep')=='1'}
    when=date.fromisoformat(request.GET.get('date') or date.today().isoformat())
    t_from=datetime.strptime(request.GET.get('from','09:00'),'%H:%M').time()
    t_to  =datetime.strptime(request.GET.get('to','17:00'),'%H:%M').time()
    desks=recommend_desks(floor,prefs,when,t_from,t_to)
    return JsonResponse({'results':[{'id':d.id,'label':d.label} for d in desks]})

def ai_surprise(request,floor_number:int):
    floor=get_object_or_404(Floor,number=floor_number)
    when=date.fromisoformat(request.GET.get('date') or date.today().isoformat())
    t_from=datetime.strptime(request.GET.get('from','09:00'),'%H:%M').time()
    t_to  =datetime.strptime(request.GET.get('to','17:00'),'%H:%M').time()
    d=surprise_me(floor,when,t_from,t_to)
    return JsonResponse({'result':{'id':d.id,'label':d.label} if d else None})

def floor_availability(request, floor_number:int):
    floor = get_object_or_404(Floor, number=floor_number)
    when = date.fromisoformat(request.GET.get('date') or date.today().isoformat())
    t_from = datetime.strptime(request.GET.get('from','09:00'),'%H:%M').time()
    t_to   = datetime.strptime(request.GET.get('to','17:00'),'%H:%M').time()
    res_qs = Reservation.objects.filter(desk__floor=floor, date=when, time_from__lt=t_to, time_to__gt=t_from, is_cancelled=False)
    reserved_ids = set(res_qs.values_list('desk_id', flat=True))
    all_ids = set(Desk.objects.filter(floor=floor).values_list('id', flat=True))
    available_ids = sorted(list(all_ids - reserved_ids))
    return JsonResponse({'reserved': sorted(list(reserved_ids)), 'available': available_ids})

def floor_edit(request,floor_number:int):
    floor=get_object_or_404(Floor,number=floor_number)
    desks=Desk.objects.filter(floor=floor)
    return render(request,'reservations/floor_edit.html',{'floor':floor,'desks':desks})

@csrf_exempt
def update_desk_position(request,desk_id:int):
    if request.method!='POST': return HttpResponseBadRequest('POST required')
    desk=get_object_or_404(Desk,id=desk_id)
    try:
        data=json.loads(request.body.decode('utf-8')); x=float(data.get('x_pct')); y=float(data.get('y_pct'))
    except Exception: return HttpResponseBadRequest('invalid payload')
    desk.x_pct=x; desk.y_pct=y; desk.save(update_fields=['x_pct','y_pct'])
    return JsonResponse({'ok':True,'id':desk.id,'x_pct':float(desk.x_pct),'y_pct':float(desk.y_pct)})

@ensure_csrf_cookie
def cancel_reservation(request, res_id:int):
    """Anuluj rezerwację"""
    reservation = get_object_or_404(Reservation, id=res_id)
    if request.method == 'POST':
        reservation.is_cancelled = True
        reservation.cancelled_at = timezone.now()
        reservation.save(update_fields=['is_cancelled', 'cancelled_at'])
        
        logger.info(
            "Rezerwacja anulowana: reservation_id=%s desk_id=%s email=%s",
            reservation.id,
            reservation.desk_id,
            reservation.email,
        )
        
        # Wyślij powiadomienie o anulowaniu
        try:
            send_cancellation_notification(reservation)
        except Exception as e:
            logger.exception(
                "Błąd wysyłania powiadomienia o anulowaniu: reservation_id=%s email=%s",
                reservation.id,
                reservation.email,
            )
        
        return JsonResponse({'success': True, 'message': 'Rezerwacja została anulowana'})
    return render(request, 'reservations/cancel_confirm.html', {'reservation': reservation})

def my_reservations(request):
    """Pokaż rezerwacje użytkownika"""
    email = request.GET.get('email', '')
    if email:
        reservations = Reservation.objects.filter(email=email, is_cancelled=False).order_by('-date', '-time_from')
    else:
        reservations = []
    return render(request, 'reservations/my_reservations.html', {
        'reservations': reservations,
        'email': email
    })

def ai_favorites(request, floor_number: int):
    """AI: Twoje ulubione stanowiska"""
    floor = get_object_or_404(Floor, number=floor_number)
    email = request.GET.get('email', '')
    date_str = request.GET.get('date', '')
    time_from = request.GET.get('from', '09:00')
    time_to = request.GET.get('to', '17:00')
    
    if not email or not date_str:
        return JsonResponse({'error': 'Brak email lub daty'}, status=400)
    
    try:
        when = datetime.strptime(date_str, '%Y-%m-%d').date()
        t_from = datetime.strptime(time_from, '%H:%M').time()
        t_to = datetime.strptime(time_to, '%H:%M').time()
    except ValueError:
        return JsonResponse({'error': 'Nieprawidłowy format daty/czasu'}, status=400)
    
    # Pobierz ulubione stanowiska
    favorites = get_user_favorites(email, floor, when, t_from, t_to, limit=5)
    
    # Zapisz preferencje użytkownika na podstawie wyborów
    prefs_data = {
        'dock': request.GET.get('dock') == 'true',
        'dual': request.GET.get('dual') == 'true',
        'adjustable': request.GET.get('adjustable') == 'true',
        'deep': request.GET.get('deep') == 'true',
    }
    save_user_preferences(email, prefs_data)
    
    return JsonResponse({
        'favorites': [{'id': d.id, 'label': d.label, 'floor': d.floor.number} for d in favorites],
        'message': f'Znaleziono {len(favorites)} ulubionych stanowisk! 💖'
    })

def lock_desk_view(request, desk_id: int):
    """Zablokuj stanowisko podczas rezerwacji"""
    desk = get_object_or_404(Desk, id=desk_id)
    email = request.GET.get('email', '')
    
    if not email:
        return JsonResponse({'error': 'Brak email'}, status=400)
    
    # Sprawdź czy stanowisko jest już zablokowane przez kogoś innego
    if is_desk_locked(desk, email):
        return JsonResponse({
            'success': True,
            'message': f'🔒 Stanowisko {desk.label} jest już zablokowane dla Ciebie!',
            'locked': True
        })
    
    # Sprawdź czy ktoś inny ma blokadę
    other_locks = DeskBookingLock.objects.filter(desk=desk).exclude(email=email)
    active_locks = [lock for lock in other_locks if lock.locked_until > timezone.now()]
    
    if active_locks:
        return JsonResponse({
            'error': f'❌ Stanowisko {desk.label} jest obecnie zablokowane przez innego użytkownika. Spróbuj za chwilę!',
            'locked': True
        })
    
    # Zablokuj stanowisko
    lock_desk(desk, email, duration_minutes=5)
    
    return JsonResponse({
        'success': True,
        'message': f'🔒 Stanowisko {desk.label} zostało zablokowane na 5 minut! Masz czas na dokończenie rezerwacji. ⏰',
        'locked': True
    })

def unlock_desk_view(request, desk_id: int):
    """Odblokuj stanowisko"""
    desk = get_object_or_404(Desk, id=desk_id)
    email = request.GET.get('email', '')
    
    if not email:
        return JsonResponse({'error': 'Brak email'}, status=400)
    
    unlock_desk(desk, email)
    
    return JsonResponse({
        'success': True,
        'message': f'🔓 Stanowisko {desk.label} zostało odblokowane!'
    })

# === NOWE FUNKCJE ===

def recurring_reservations(request):
    """Lista recurring reservations użytkownika"""
    email = request.GET.get('email', '')
    if not email:
        return render(request, 'reservations/recurring_reservations.html', {'error': 'Brak email'})
    
    recurring = RecurringReservation.objects.filter(email=email, is_active=True).order_by('-created_at')
    return render(request, 'reservations/recurring_reservations.html', {
        'recurring_reservations': recurring,
        'email': email
    })

def create_recurring_reservation(request, desk_id: int):
    """Utwórz recurring reservation"""
    desk = get_object_or_404(Desk, id=desk_id)
    
    if request.method == 'POST':
        form = RecurringReservationForm(request.POST)
        if form.is_valid():
            recurring = form.save(commit=False)
            recurring.desk = desk
            recurring.save()
            
            # Generuj pierwsze rezerwacje
            generate_recurring_reservations()
            
            return render(request, 'reservations/recurring_success.html', {
                'recurring': recurring,
                'desk': desk
            })
    else:
        form = RecurringReservationForm()
    
    return render(request, 'reservations/create_recurring.html', {
        'form': form,
        'desk': desk
    })

def add_to_waitlist(request, desk_id: int):
    """Dodaj do waitlist"""
    desk = get_object_or_404(Desk, id=desk_id)
    
    if request.method == 'POST':
        form = WaitlistForm(request.POST)
        if form.is_valid():
            waitlist_entry = form.save(commit=False)
            waitlist_entry.desk = desk
            waitlist_entry.save()
            
            # Sprawdź czy stanowisko się zwolniło i wyślij powiadomienie
            if is_available(desk, waitlist_entry.preferred_date, waitlist_entry.time_from, waitlist_entry.time_to):
                try:
                    send_waitlist_notification(waitlist_entry)
                    waitlist_entry.is_notified = True
                    waitlist_entry.save()
                except Exception as e:
                    print(f"Błąd wysyłania powiadomienia z waitlist: {e}")
            
            return render(request, 'reservations/waitlist_success.html', {
                'waitlist_entry': waitlist_entry,
                'desk': desk
            })
    else:
        form = WaitlistForm()
    
    return render(request, 'reservations/add_to_waitlist.html', {
        'form': form,
        'desk': desk
    })


def guest_reservation(request, desk_id: int):
    """Rezerwacja dla gościa"""
    desk = get_object_or_404(Desk, id=desk_id)
    
    if request.method == 'POST':
        form = GuestReservationForm(request.POST)
        if form.is_valid():
            guest_reservation = form.save(commit=False)
            guest_reservation.desk = desk
            guest_reservation.save()
            
            return render(request, 'reservations/guest_reservation_success.html', {
                'guest_reservation': guest_reservation,
                'desk': desk
            })
    else:
        form = GuestReservationForm()
    
    return render(request, 'reservations/guest_reservation.html', {
        'form': form,
        'desk': desk
    })

def cancel_recurring(request, recurring_id: int):
    """Anuluj recurring reservation"""
    recurring = get_object_or_404(RecurringReservation, id=recurring_id)
    
    if request.method == 'POST':
        recurring.is_active = False
        recurring.save()
        return JsonResponse({
            'success': True,
            'message': f'Recurring reservation dla {recurring.desk.label} została anulowana'
        })
    
    return render(request, 'reservations/cancel_recurring_confirm.html', {
        'recurring': recurring
    })

def advanced_features(request):
    """Strona z zaawansowanymi funkcjami"""
    return render(request, 'reservations/advanced_features.html')

def notification_settings(request):
    """Notification settings"""
    email = request.GET.get('email', '')
    error = None
    preferences = None
    
    if email:
        try:
            preferences = UserPreferences.objects.get(email=email)
        except UserPreferences.DoesNotExist:
            error = _("No settings found for %(email)s") % {'email': email}
    
    if request.method == 'POST' and email:
        try:
            preferences, created = UserPreferences.objects.get_or_create(email=email)
            
            # Aktualizuj ustawienia
            preferences.email_notifications = 'email_notifications' in request.POST
            preferences.reminder_before_booking = int(request.POST.get('reminder_before_booking', 30))
            preferences.daily_summary = 'daily_summary' in request.POST
            preferences.weekly_report = 'weekly_report' in request.POST
            preferences.waitlist_notifications = 'waitlist_notifications' in request.POST
            preferences.cancellation_notifications = 'cancellation_notifications' in request.POST
            preferences.save()
            
            return render(request, 'reservations/notification_settings.html', {
                'email': email,
                'preferences': preferences,
                'success': _('Settings have been saved!')
            })
        except Exception as e:
            error = _('Error saving settings: %(error)s') % {'error': str(e)}
    
    return render(request, 'reservations/notification_settings.html', {
        'email': email,
        'preferences': preferences,
        'error': error
    })

@csrf_exempt
def subscribe_notifications(request):
    """API endpoint dla subskrypcji powiadomień push"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not is_webpush_enabled():
        return JsonResponse({'error': 'webpush_disabled'}, status=503)

    try:
        data = json.loads(request.body)
        email = data.get('email')
        subscription = data.get('subscription')
        
        if not email or not subscription:
            return JsonResponse({'error': 'Missing email or subscription'}, status=400)
        
        # Zapisz subskrypcję
        NotificationSubscription.objects.update_or_create(
            email=email,
            endpoint=subscription['endpoint'],
            defaults={
                'p256dh_key': subscription['keys']['p256dh'],
                'auth_key': subscription['keys']['auth'],
                'is_active': True
            }
        )
        
        return JsonResponse({'success': True}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def notification_public_key(request):
    """Zwraca klucz publiczny VAPID do subskrypcji powiadomień push."""
    if not is_webpush_enabled():
        return JsonResponse({'enabled': False, 'publicKey': ''})
    return JsonResponse({'enabled': True, 'publicKey': settings.WEBPUSH_VAPID_PUBLIC_KEY})


@csrf_exempt
@require_POST
def test_push_notification(request):
    """Wysyła testowe powiadomienie push dla zalogowanego użytkownika."""
    if not is_webpush_enabled():
        return JsonResponse({'error': 'webpush_disabled'}, status=503)

    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid_json'}, status=400)

    email = payload.get('email')
    if not email:
        return JsonResponse({'error': 'missing_email'}, status=400)

    delivered = send_push_notification(
        email,
        _("Test notification"),
        _("This is a test push notification from the reservation system."),
        data={'notification_type': 'TEST'},
        tag='test',
    )

    if delivered:
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'no_active_subscriptions'}, status=404)

def group_reservations(request, floor_number: int):
    """Group reservations page"""
    floor = get_object_or_404(Floor, number=floor_number)
    return render(request, 'reservations/group_reservations.html', {
        'floor': floor
    })

def suggest_group_desks_view(request, floor_number: int):
    """API - suggest seats for group"""
    try:
        floor = get_object_or_404(Floor, number=floor_number)
        
        count = int(request.GET.get('count', 2))
        date_str = request.GET.get('date')
        time_from_str = request.GET.get('time_from')
        time_to_str = request.GET.get('time_to')
        
        if not all([date_str, time_from_str, time_to_str]):
            return JsonResponse({'error': _('Missing required parameters')}, status=400)
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            time_from_obj = datetime.strptime(time_from_str, '%H:%M').time()
            time_to_obj = datetime.strptime(time_to_str, '%H:%M').time()
        except ValueError:
            return JsonResponse({'error': _('Invalid date/time format')}, status=400)
        
        try:
            suggestions = suggest_group_desks(floor, count, date_obj, time_from_obj, time_to_obj)
        except Exception as e:
            return JsonResponse({'error': _('Error finding suggestions: %(error)s') % {'error': str(e)}}, status=500)
        
        result = []
        for suggestion in suggestions[:5]:  # Maksymalnie 5 sugestii
            result.append({
                'desks': [
                    {
                        'id': desk.id,
                        'label': desk.label,
                        'x_pct': float(desk.x_pct),
                        'y_pct': float(desk.y_pct),
                        'features': {
                            'has_dock': desk.has_dock,
                            'has_adjustable_desk': desk.has_adjustable_desk,
                            'has_dual_monitors': desk.has_dual_monitors,
                            'is_deep_work': desk.is_deep_work
                        }
                    }
                    for desk in suggestion['desks']
                ],
                'area': suggestion['area']
            })
        
        return JsonResponse({'suggestions': result})
        
    except Exception as e:
        return JsonResponse({'error': _('Unexpected error: %(error)s') % {'error': str(e)}}, status=500)

def create_group_reservation_view(request, floor_number: int):
    """Create group reservation"""
    floor = get_object_or_404(Floor, number=floor_number)
    
    if request.method == 'POST':
        form = GroupReservationForm(request.POST)
        if form.is_valid():
            desk_ids = request.POST.get('desk_ids')
            
            if not desk_ids:
                return render(request, 'reservations/group_reservations.html', {
                    'floor': floor,
                    'form': form,
                    'error': _('Select at least one seat')
                })
            
            group_reservation, message = create_group_reservation(
                group_name=form.cleaned_data['group_name'],
                organizer_email=form.cleaned_data['organizer_email'],
                date=form.cleaned_data['date'],
                time_from=form.cleaned_data['time_from'],
                time_to=form.cleaned_data['time_to'],
                desk_ids=desk_ids,
                purpose=form.cleaned_data['purpose']
            )
            
            if group_reservation:
                return render(request, 'reservations/group_reservation_success.html', {
                    'group_reservation': group_reservation,
                    'floor': floor
                })
            else:
                return render(request, 'reservations/group_reservations.html', {
                    'floor': floor,
                    'form': form,
                    'error': message
                })
    else:
        form = GroupReservationForm()
    
    return render(request, 'reservations/group_reservations.html', {
        'floor': floor,
        'form': form
    })

def cancel_group_reservation(request, group_id: int):
    """Anuluj grupową rezerwację"""
    group_reservation = get_object_or_404(GroupReservation, id=group_id)
    
    if request.method == 'POST':
        group_reservation.is_cancelled = True
        group_reservation.cancelled_at = timezone.now()
        group_reservation.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Grupowa rezerwacja "{group_reservation.group_name}" została anulowana'
        })
    
    return render(request, 'reservations/cancel_group_confirm.html', {
        'group_reservation': group_reservation
    })

def conference_rooms(request, floor_number: int = None):
    """Conference rooms listing with floor selection"""
    floors = Floor.objects.all().order_by('number')
    
    if floor_number:
        floor = get_object_or_404(Floor, number=floor_number)
        conference_rooms = ConferenceRoom.objects.filter(floor=floor, is_active=True)
    else:
        floor = None
        conference_rooms = ConferenceRoom.objects.filter(is_active=True)
    
    return render(request, 'reservations/conference_rooms.html', {
        'floor': floor,
        'floors': floors,
        'conference_rooms': conference_rooms
    })

def conference_room_reservation(request, room_id: int):
    """Conference room reservation"""
    conference_room = get_object_or_404(ConferenceRoom, id=room_id)
    
    if request.method == 'POST':
        form = ConferenceReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.conference_room = conference_room
            reservation.save()
            
            return render(request, 'reservations/conference_reservation_success.html', {
                'reservation': reservation,
                'conference_room': conference_room
            })
    else:
        form = ConferenceReservationForm()
    
    return render(request, 'reservations/conference_room_reservation.html', {
        'form': form,
        'conference_room': conference_room
    })

def slack_setup(request):
    """Slack bot configuration page"""
    return render(request, 'reservations/slack_setup.html')


def generate_ics_content(reservation):
    """Generate .ics content for a reservation"""
    # Generate unique ID for the event
    event_id = f"reservation-{reservation.id}@office-reservations.com"
    
    # Convert to UTC format (simplified - in production you'd handle timezones properly)
    start_utc = f"{reservation.date}T{reservation.time_from}:00Z"
    end_utc = f"{reservation.date}T{reservation.time_to}:00Z"
    
    # Current timestamp for the ICS file
    now = timezone.now().strftime("%Y%m%dT%H%M%SZ")
    
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Office Reservations//Office Reservations//EN
BEGIN:VEVENT
UID:{event_id}
DTSTAMP:{now}
DTSTART:{start_utc}
DTEND:{end_utc}
SUMMARY:Desk Reservation - {reservation.desk.label}
DESCRIPTION:Desk reservation for {reservation.name}\\nFloor: {reservation.desk.floor.number}\\nDesk: {reservation.desk.label}\\nEmail: {reservation.email}
LOCATION:Floor {reservation.desk.floor.number}, Desk {reservation.desk.label}
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR"""
    
    return ics_content


def download_ics(request, reservation_id):
    """Download .ics file for a reservation"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    ics_content = generate_ics_content(reservation)
    
    response = HttpResponse(ics_content, content_type='text/calendar; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="reservation-{reservation.id}.ics"'
    
    return response
