from django.db import IntegrityError
from rest_framework import serializers
from .models import Reservation

class ReservationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'seat_id', 'date', 'name', 'email', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']

    def to_internal_value(self, data):
        data = dict(data)
        if 'seat_id' not in data:
            for alt in ('seatId', 'seat', 'reserveSeatId', 'formSeat'):
                if alt in data:
                    data['seat_id'] = data[alt]
                    break
        if 'date' not in data:
            for alt in ('reserveDate', 'dateStr', 'formDate'):
                if alt in data:
                    data['date'] = data[alt]
                    break
        import re
        d = str(data.get('date') or '').strip()
        if d:
            m = re.match('^(\\d{4})[-/](\\d{2})[-/](\\d{2})$', d)
            if m:
                data['date'] = f'{m.group(1)}-{m.group(2)}-{m.group(3)}'
            else:
                m2 = re.match('^(\\d{2})[./-](\\d{2})[./-](\\d{4})$', d)
                if m2:
                    data['date'] = f'{m2.group(3)}-{m2.group(2)}-{m2.group(1)}'
        if 'name' not in data:
            for alt in ('fullName', 'formName'):
                if alt in data:
                    data['name'] = data[alt]
                    break
        if 'email' not in data:
            for alt in ('mail', 'formEmail'):
                if alt in data:
                    data['email'] = data[alt]
                    break
        if 'notes' not in data and 'formNotes' in data:
            data['notes'] = data['formNotes']
        return super().to_internal_value(data)

    def validate(self, attrs):
        date = (attrs.get('date') or '').strip()
        if len(date) != 10:
            raise serializers.ValidationError({'date': 'Use YYYY-MM-DD format.'})
        if not attrs.get('seat_id'):
            raise serializers.ValidationError({'seat_id': 'This field is required.'})
        req = self.context.get('request')
        if not attrs.get('name'):
            user_name = ''
            if req and getattr(req, 'user', None) and req.user.is_authenticated:
                user_name = getattr(req.user, 'get_full_name', lambda: '')() or getattr(req.user, 'username', '') or getattr(req.user, 'email', '')
            attrs['name'] = user_name or 'User'
        if not attrs.get('email'):
            user_email = ''
            if req and getattr(req, 'user', None) and req.user.is_authenticated:
                user_email = getattr(req.user, 'email', '')
            attrs['email'] = user_email or 'unknown@example.com'
        return attrs

    def create(self, validated_data):
        if not validated_data.get('id'):
            sid = validated_data.get('seat_id') or ''
            dt = validated_data.get('date') or ''
            validated_data['id'] = f'{sid}-{dt}'
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError({'detail': 'Seat already reserved for this date.'})
