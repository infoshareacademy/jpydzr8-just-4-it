from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import Reservation

class SeatsOccupiedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        date_str = (request.query_params.get('date') or '').strip()
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        occupied = list(Reservation.objects.filter(date=date_str).values_list('seat_id', flat=True))
        return Response({'date': date_str, 'occupied': occupied})
