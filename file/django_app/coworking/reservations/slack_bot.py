import os
import json
import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Floor, Desk, Reservation, GroupReservation
from .ai_utils import is_available
from datetime import datetime, date, time

# Slack Bot Configuration
SLACK_VERIFICATION_TOKEN = os.getenv('SLACK_VERIFICATION_TOKEN', 'your_verification_token')
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN', 'your_bot_token')
SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET', 'your_signing_secret')

def verify_slack_request(request):
    """Verify that the request is from Slack"""
    # In production, you should verify the request signature
    # For now, we'll skip verification for development
    return True

@csrf_exempt
@require_POST
def slack_events(request):
    """Handle Slack events"""
    if not verify_slack_request(request):
        return HttpResponse(status=403)
    
    data = json.loads(request.body)
    
    # Handle URL verification
    if data.get('type') == 'url_verification':
        return HttpResponse(data.get('challenge'))
    
    # Handle events
    if data.get('type') == 'event_callback':
        event = data.get('event', {})
        
        # Handle app mentions
        if event.get('type') == 'app_mention':
            handle_app_mention(event)
        
        # Handle slash commands
        elif event.get('type') == 'message':
            handle_message(event)
    
    return HttpResponse(status=200)

@csrf_exempt
@require_POST
def slack_slash_commands(request):
    """Handle Slack slash commands"""
    if not verify_slack_request(request):
        return HttpResponse(status=403)
    
    command = request.POST.get('command')
    text = request.POST.get('text', '')
    user_id = request.POST.get('user_id')
    channel_id = request.POST.get('channel_id')
    
    if command == '/rezerwuj':
        return handle_reserve_command(text, user_id, channel_id)
    elif command == '/anuluj':
        return handle_cancel_command(text, user_id, channel_id)
    elif command == '/dostepne':
        return handle_available_command(text, user_id, channel_id)
    elif command == '/pomoc':
        return handle_help_command()
    else:
        return JsonResponse({
            'response_type': 'ephemeral',
            'text': 'Nieznana komenda. Użyj `/pomoc` aby zobaczyć dostępne komendy.'
        })

def handle_reserve_command(text, user_id, channel_id):
    """Handle /rezerwuj command"""
    try:
        # Parse command: /rezerwuj piętro 4 stanowisko A1 data 2024-01-15 czas 09:00-17:00 email test@example.com
        parts = text.split()
        
        if len(parts) < 8:
            return JsonResponse({
                'response_type': 'ephemeral',
                'text': 'Nieprawidłowy format. Użyj: `/rezerwuj piętro 4 stanowisko A1 data 2024-01-15 czas 09:00-17:00 email test@example.com`'
            })
        
        # Extract parameters
        floor_num = int(parts[1])
        desk_label = parts[3]
        date_str = parts[5]
        time_str = parts[7]
        email = parts[9] if len(parts) > 9 else f"{user_id}@slack.local"
        
        # Parse date and time
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_from_str, time_to_str = time_str.split('-')
        time_from = datetime.strptime(time_from_str, '%H:%M').time()
        time_to = datetime.strptime(time_to_str, '%H:%M').time()
        
        # Find desk
        try:
            floor = Floor.objects.get(number=floor_num)
            desk = Desk.objects.get(floor=floor, label=desk_label)
        except (Floor.DoesNotExist, Desk.DoesNotExist):
            return JsonResponse({
                'response_type': 'ephemeral',
                'text': f'❌ Nie znaleziono stanowiska {desk_label} na piętrze {floor_num}'
            })
        
        # Check availability
        if not is_available(desk, date_obj, time_from, time_to):
            return JsonResponse({
                'response_type': 'ephemeral',
                'text': f'❌ Stanowisko {desk_label} nie jest dostępne w tym czasie'
            })
        
        # Create reservation
        reservation = Reservation.objects.create(
            desk=desk,
            name=f"Slack User {user_id}",
            email=email,
            date=date_obj,
            time_from=time_from,
            time_to=time_to
        )
        
        return JsonResponse({
            'response_type': 'in_channel',
            'text': f'✅ Rezerwacja utworzona!\n\n*Stanowisko:* {desk.label} (Piętro {floor.number})\n*Data:* {date_obj}\n*Godziny:* {time_from} - {time_to}\n*Email:* {email}'
        })
        
    except Exception as e:
        return JsonResponse({
            'response_type': 'ephemeral',
            'text': f'❌ Błąd: {str(e)}'
        })

def handle_cancel_command(text, user_id, channel_id):
    """Handle /anuluj command"""
    try:
        # Parse command: /anuluj rezerwacja_id
        reservation_id = int(text.strip())
        
        reservation = Reservation.objects.get(id=reservation_id)
        reservation.is_cancelled = True
        reservation.cancelled_at = datetime.now()
        reservation.save()
        
        return JsonResponse({
            'response_type': 'in_channel',
            'text': f'✅ Rezerwacja {reservation_id} została anulowana'
        })
        
    except (ValueError, Reservation.DoesNotExist):
        return JsonResponse({
            'response_type': 'ephemeral',
            'text': '❌ Nie znaleziono rezerwacji o podanym ID'
        })
    except Exception as e:
        return JsonResponse({
            'response_type': 'ephemeral',
            'text': f'❌ Błąd: {str(e)}'
        })

def handle_available_command(text, user_id, channel_id):
    """Handle /dostepne command"""
    try:
        # Parse command: /dostepne piętro 4 data 2024-01-15
        parts = text.split()
        
        if len(parts) < 4:
            return JsonResponse({
                'response_type': 'ephemeral',
                'text': 'Użyj: `/dostepne piętro 4 data 2024-01-15`'
            })
        
        floor_num = int(parts[1])
        date_str = parts[3]
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get available desks
        floor = Floor.objects.get(number=floor_num)
        desks = Desk.objects.filter(floor=floor)
        
        available_desks = []
        for desk in desks:
            if is_available(desk, date_obj, time(9, 0), time(17, 0)):
                available_desks.append(desk.label)
        
        if available_desks:
            return JsonResponse({
                'response_type': 'in_channel',
                'text': f'📅 Dostępne stanowiska na piętrze {floor_num} ({date_obj}):\n\n' + '\n'.join(f'• {desk}' for desk in available_desks[:10])
            })
        else:
            return JsonResponse({
                'response_type': 'in_channel',
                'text': f'❌ Brak dostępnych stanowisk na piętrze {floor_num} w dniu {date_obj}'
            })
            
    except Exception as e:
        return JsonResponse({
            'response_type': 'ephemeral',
            'text': f'❌ Błąd: {str(e)}'
        })

def handle_help_command():
    """Handle /pomoc command"""
    help_text = """
🤖 *Bot rezerwacji stanowisk - Dostępne komendy:*

• `/rezerwuj piętro 4 stanowisko A1 data 2024-01-15 czas 09:00-17:00 email test@example.com`
  - Rezerwuj stanowisko

• `/anuluj 123`
  - Anuluj rezerwację o ID 123

• `/dostepne piętro 4 data 2024-01-15`
  - Pokaż dostępne stanowiska

• `/pomoc`
  - Pokaż tę pomoc

*Przykłady:*
```
/rezerwuj piętro 4 stanowisko A1 data 2024-01-15 czas 09:00-17:00
/dostepne piętro 4 data 2024-01-15
/anuluj 123
```
    """
    
    return JsonResponse({
        'response_type': 'ephemeral',
        'text': help_text
    })

def send_slack_message(channel, text, blocks=None):
    """Send message to Slack channel"""
    url = 'https://slack.com/api/chat.postMessage'
    headers = {
        'Authorization': f'Bearer {SLACK_BOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'channel': channel,
        'text': text
    }
    
    if blocks:
        payload['blocks'] = blocks
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def notify_reservation_created(reservation):
    """Send notification when reservation is created"""
    text = f"✅ Nowa rezerwacja!\n\n*Stanowisko:* {reservation.desk.label} (Piętro {reservation.desk.floor.number})\n*Data:* {reservation.date}\n*Godziny:* {reservation.time_from} - {reservation.time_to}\n*Użytkownik:* {reservation.name}"
    
    # Send to general channel (you can configure this)
    send_slack_message('#office-reservations', text)

def notify_reservation_cancelled(reservation):
    """Send notification when reservation is cancelled"""
    text = f"❌ Rezerwacja anulowana!\n\n*Stanowisko:* {reservation.desk.label} (Piętro {reservation.desk.floor.number})\n*Data:* {reservation.date}\n*Godziny:* {reservation.time_from} - {reservation.time_to}"
    
    # Send to general channel
    send_slack_message('#office-reservations', text)

