from datetime import date

def admin_metrics(request):
    total = None
    occ = None
    try:
        from .models import Reservation
        qs = Reservation.objects.filter(date=date.today())
        total = qs.count()
        seats = 120
        occ = round(100 * total / seats, 1) if seats else None
    except Exception:
        pass
    return {"request": request, "request.reservations_today": total, "request.occupancy_today": occ}