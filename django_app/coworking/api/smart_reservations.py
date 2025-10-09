from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from api.models import Reservation, User
import re

class SmartReservationManager:
    """Inteligentny menadżer rezerwacji"""
    
    @staticmethod
    def auto_cleanup_expired_reservations(days_threshold=1):
        """Automatyczne czyszczenie wygasłych rezerwacji"""
        today = datetime.now().strftime('%Y-%m-%d')
        cutoff_date = (datetime.now() - timedelta(days=days_threshold)).strftime('%Y-%m-%d')
        
        # Znajdź rezerwacje starsze niż threshold
        expired_reservations = Reservation.objects.filter(
            date__lt=cutoff_date
        )
        
        count = expired_reservations.count()
        expired_reservations.delete()
        
        return {
            'cleaned_count': count,
            'cutoff_date': cutoff_date,
            'threshold_days': days_threshold
        }
    
    @staticmethod
    def detect_conflicts():
        """Wykrywa konflikty rezerwacji"""
        conflicts = []
        
        # Znajdź duplikaty (te same miejsce i data)
        duplicates = Reservation.objects.values('seat_id', 'date').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        for duplicate in duplicates:
            conflicting_reservations = Reservation.objects.filter(
                seat_id=duplicate['seat_id'],
                date=duplicate['date']
            )
            
            conflicts.append({
                'type': 'duplicate',
                'seat_id': duplicate['seat_id'],
                'date': duplicate['date'],
                'count': duplicate['count'],
                'reservations': [
                    {
                        'id': res.id,
                        'name': res.name,
                        'email': res.email,
                        'created_at': res.created_at
                    } for res in conflicting_reservations
                ]
            })
        
        return conflicts
    
    @staticmethod
    def suggest_alternative_seats(preferred_seat, date, amenities=None):
        """Sugeruje alternatywne miejsca"""
        # Sprawdź czy preferowane miejsce jest dostępne
        if not Reservation.objects.filter(seat_id=preferred_seat, date=date).exists():
            return {
                'available': True,
                'suggested_seat': preferred_seat,
                'message': 'Preferred seat is available'
            }
        
        # Znajdź podobne miejsca (te same udogodnienia)
        similar_seats = SmartReservationManager._find_similar_seats(preferred_seat, amenities)
        
        # Sprawdź dostępność podobnych miejsc
        available_alternatives = []
        for seat in similar_seats:
            if not Reservation.objects.filter(seat_id=seat, date=date).exists():
                available_alternatives.append(seat)
        
        return {
            'available': False,
            'preferred_seat': preferred_seat,
            'alternatives': available_alternatives[:5],  # Top 5 alternatyw
            'message': f'Preferred seat unavailable, found {len(available_alternatives)} alternatives'
        }
    
    @staticmethod
    def _find_similar_seats(seat_id, amenities=None):
        """Znajduje podobne miejsca na podstawie udogodnień"""
        # Analizuj nazwę miejsca dla udogodnień
        seat_amenities = SmartReservationManager._extract_amenities_from_seat(seat_id)
        
        # Symulacja podobnych miejsc (w rzeczywistej aplikacji byłaby logika bazująca na bazie danych)
        all_seats = Reservation.objects.values_list('seat_id', flat=True).distinct()
        similar_seats = []
        
        for seat in all_seats:
            if seat != seat_id:
                seat_amenities_check = SmartReservationManager._extract_amenities_from_seat(seat)
                # Jeśli ma podobne udogodnienia
                if any(amenity in seat_amenities_check for amenity in seat_amenities):
                    similar_seats.append(seat)
        
        return similar_seats[:10]  # Top 10 podobnych miejsc
    
    @staticmethod
    def _extract_amenities_from_seat(seat_id):
        """Wyciąga udogodnienia z nazwy miejsca"""
        amenities = []
        seat_lower = seat_id.lower()
        
        if 'd' in seat_lower or 'dock' in seat_lower:
            amenities.append('docking')
        if 's' in seat_lower or 'screen' in seat_lower:
            amenities.append('screen')
        if 'e' in seat_lower or 'electric' in seat_lower:
            amenities.append('electric')
        
        return amenities
    
    @staticmethod
    def get_usage_patterns(days=30):
        """Analizuje wzorce wykorzystania miejsc"""
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Statystyki wykorzystania miejsc
        seat_usage = Reservation.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).values('seat_id').annotate(
            total_bookings=Count('id'),
            unique_users=Count('email', distinct=True)
        ).order_by('-total_bookings')
        
        # Popularne dni tygodnia
        weekday_stats = {}
        for i in range(7):
            weekday_stats[i] = 0
        
        reservations = Reservation.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )
        
        for res in reservations:
            try:
                date_obj = datetime.strptime(res.date, '%Y-%m-%d')
                weekday = date_obj.weekday()
                weekday_stats[weekday] += 1
            except:
                continue
        
        return {
            'seat_usage': list(seat_usage),
            'weekday_patterns': weekday_stats,
            'period_days': days,
            'total_reservations': reservations.count()
        }

class WaitlistManager:
    """Menadżer list oczekujących"""
    
    @staticmethod
    def add_to_waitlist(email, seat_id, date, name):
        """Dodaje do listy oczekujących"""
        # Sprawdź czy miejsce jest już zarezerwowane
        if Reservation.objects.filter(seat_id=seat_id, date=date).exists():
            # Dodaj do listy oczekujących (w rzeczywistej aplikacji byłaby osobna tabela)
            waitlist_entry = {
                'email': email,
                'seat_id': seat_id,
                'date': date,
                'name': name,
                'added_at': timezone.now().isoformat(),
                'status': 'waiting'
            }
            return waitlist_entry
        else:
            return {'error': 'Seat is actually available - no need for waitlist'}
    
    @staticmethod
    def notify_waitlist_availability(seat_id, date):
        """Powiadamia osoby z listy oczekujących o dostępności"""
        # W rzeczywistej aplikacji wysłałoby email/powiadomienia
        return {
            'notified_count': 0,  # Symulacja
            'seat_id': seat_id,
            'date': date,
            'message': 'Waitlist notifications sent'
        }

class RecurringReservationManager:
    """Menadżer cyklicznych rezerwacji"""
    
    @staticmethod
    def create_recurring_reservation(base_reservation, frequency, end_date=None):
        """Tworzy cykliczną rezerwację"""
        if not end_date:
            end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        created_reservations = []
        current_date = datetime.strptime(base_reservation['date'], '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        while current_date <= end_date_obj:
            # Sprawdź czy miejsce jest dostępne
            if not Reservation.objects.filter(
                seat_id=base_reservation['seat_id'],
                date=current_date.strftime('%Y-%m-%d')
            ).exists():
                
                # Utwórz rezerwację
                reservation = Reservation.objects.create(
                    id=f"recurring_{base_reservation['seat_id']}_{current_date.strftime('%Y%m%d')}",
                    seat_id=base_reservation['seat_id'],
                    date=current_date.strftime('%Y-%m-%d'),
                    name=base_reservation['name'],
                    email=base_reservation['email'],
                    notes=f"Recurring reservation (frequency: {frequency})"
                )
                
                created_reservations.append(reservation)
            
            # Przejdź do następnej daty
            if frequency == 'daily':
                current_date += timedelta(days=1)
            elif frequency == 'weekly':
                current_date += timedelta(weeks=1)
            elif frequency == 'monthly':
                # Prosta implementacja miesięczna
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            else:
                break  # Nieznana częstotliwość
        
        return {
            'created_count': len(created_reservations),
            'frequency': frequency,
            'base_date': base_reservation['date'],
            'end_date': end_date,
            'reservations': [
                {
                    'id': res.id,
                    'seat_id': res.seat_id,
                    'date': res.date
                } for res in created_reservations
            ]
        }
