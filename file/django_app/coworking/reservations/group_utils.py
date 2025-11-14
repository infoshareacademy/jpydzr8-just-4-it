from django.db import models
from .models import Desk, GroupReservation, Reservation
from datetime import date, time

def find_adjacent_desks(floor, start_desk, count, date, time_from, time_to):
    """Znajdź stanowiska obok siebie na tym samym piętrze"""
    if not start_desk:
        return []
    
    # Znajdź wszystkie stanowiska na tym samym piętrze
    floor_desks = Desk.objects.filter(floor=floor).order_by('x_pct', 'y_pct')
    
    # Znajdź pozycję startowego stanowiska
    start_index = None
    for i, desk in enumerate(floor_desks):
        if desk.id == start_desk.id:
            start_index = i
            break
    
    if start_index is None:
        return []
    
    # Sprawdź dostępność stanowisk obok siebie
    adjacent_desks = []
    
    # Sprawdź w prawo od startowego stanowiska
    for i in range(start_index, min(start_index + count, len(floor_desks))):
        desk = floor_desks[i]
        if is_desk_available_for_group(desk, date, time_from, time_to):
            adjacent_desks.append(desk)
        else:
            break
    
    # Jeśli nie ma wystarczająco stanowisk w prawo, spróbuj w lewo
    if len(adjacent_desks) < count:
        adjacent_desks = []
        for i in range(max(0, start_index - count + 1), start_index + 1):
            desk = floor_desks[i]
            if is_desk_available_for_group(desk, date, time_from, time_to):
                adjacent_desks.append(desk)
            else:
                break
    
    return adjacent_desks[:count]

def is_desk_available_for_group(desk, date, time_from, time_to):
    """Sprawdź czy stanowisko jest dostępne dla grupy"""
    # Sprawdź czy nie ma konfliktów z istniejącymi rezerwacjami
    conflicting_reservations = Reservation.objects.filter(
        desk=desk,
        date=date,
        is_cancelled=False,
        time_from__lt=time_to,
        time_to__gt=time_from
    ).exists()
    
    if conflicting_reservations:
        return False
    
    # Sprawdź czy nie ma konfliktów z grupowymi rezerwacjami
    conflicting_groups = GroupReservation.objects.filter(
        desks=desk,
        date=date,
        is_cancelled=False,
        time_from__lt=time_to,
        time_to__gt=time_from
    ).exists()
    
    return not conflicting_groups

def get_desk_neighbors(desk, max_distance=10.0):
    """Znajdź sąsiednie stanowiska w określonej odległości"""
    floor_desks = Desk.objects.filter(floor=desk.floor).exclude(id=desk.id)
    
    neighbors = []
    for other_desk in floor_desks:
        # Oblicz odległość między stanowiskami - konwertuj Decimal na float
        dx = float(desk.x_pct - other_desk.x_pct)
        dy = float(desk.y_pct - other_desk.y_pct)
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance <= max_distance:
            neighbors.append(other_desk)
    
    return sorted(neighbors, key=lambda d: (float(d.x_pct - desk.x_pct) ** 2 + float(d.y_pct - desk.y_pct) ** 2) ** 0.5)

def suggest_group_desks(floor, count, date, time_from, time_to):
    """Zasugeruj stanowiska dla grupy"""
    floor_desks = Desk.objects.filter(floor=floor).order_by('x_pct', 'y_pct')
    
    suggestions = []
    
    for desk in floor_desks:
        if is_desk_available_for_group(desk, date, time_from, time_to):
            # Znajdź sąsiadów
            neighbors = get_desk_neighbors(desk)
            available_neighbors = [n for n in neighbors if is_desk_available_for_group(n, date, time_from, time_to)]
            
            if len(available_neighbors) + 1 >= count:
                # Znajdź najlepsze stanowiska obok siebie
                group = find_adjacent_desks(floor, desk, count, date, time_from, time_to)
                
                if len(group) == count:
                    suggestions.append({
                        'desks': group,
                        'center_desk': desk,
                        'area': calculate_group_area(group)
                    })
    
    # Sortuj według obszaru (mniejsze grupy są lepsze)
    return sorted(suggestions, key=lambda x: x['area'])

def calculate_group_area(desks):
    """Oblicz obszar zajmowany przez grupę stanowisk"""
    if not desks:
        return float('inf')
    
    x_coords = [float(desk.x_pct) for desk in desks]
    y_coords = [float(desk.y_pct) for desk in desks]
    
    width = max(x_coords) - min(x_coords)
    height = max(y_coords) - min(y_coords)
    
    return width * height

def create_group_reservation(group_name, organizer_email, date, time_from, time_to, desk_ids, purpose=''):
    """Utwórz grupową rezerwację"""
    print(f"DEBUG: desk_ids przed konwersją: {desk_ids} (typ: {type(desk_ids)})")
    
    # Konwertuj desk_ids na listę liczb całkowitych
    if isinstance(desk_ids, str):
        desk_ids = [int(id.strip()) for id in desk_ids.split(',') if id.strip()]
        print(f"DEBUG: desk_ids po konwersji: {desk_ids} (typ: {type(desk_ids)})")
    
    # Sprawdź czy wszystkie stanowiska są dostępne
    desks = Desk.objects.filter(id__in=desk_ids)
    
    for desk in desks:
        if not is_desk_available_for_group(desk, date, time_from, time_to):
            return None, f"Stanowisko {desk.label} nie jest dostępne"
    
    # Utwórz rezerwację grupową
    group_reservation = GroupReservation.objects.create(
        group_name=group_name,
        organizer_email=organizer_email,
        date=date,
        time_from=time_from,
        time_to=time_to,
        purpose=purpose
    )
    
    # Dodaj stanowiska
    group_reservation.desks.set(desks)
    
    return group_reservation, "Rezerwacja grupowa została utworzona"
