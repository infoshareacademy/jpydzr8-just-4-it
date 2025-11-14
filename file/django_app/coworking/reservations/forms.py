from django import forms
from django.utils import timezone
from .models import Reservation, RecurringReservation, Waitlist, GuestReservation, GroupReservation, ConferenceReservation

class ReservationForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and getattr(user, 'is_authenticated', False):
            first_name = getattr(user, 'first_name', '') or ''
            last_name = getattr(user, 'last_name', '') or ''
            full_name = f"{first_name} {last_name}".strip() or getattr(user, 'full_name', '') or ''
            if not full_name and hasattr(user, 'get_full_name'):
                full_name = (user.get_full_name() or '').strip()
            if not full_name:
                full_name = user.email

            self.fields['name'].initial = full_name
            self.fields['email'].initial = user.email

            self.fields['name'].required = False
            self.fields['email'].required = False

            # Make fields read-only in the form
            self.fields['name'].widget.attrs.update({
                'readonly': 'readonly',
                'class': self.fields['name'].widget.attrs.get('class', '') + ' bg-gray-100 cursor-not-allowed',
            })
            self.fields['email'].widget.attrs.update({
                'readonly': 'readonly',
                'class': self.fields['email'].widget.attrs.get('class', '') + ' bg-gray-100 cursor-not-allowed',
            })
        else:
            # ensure classes exist for validation styling
            for field_name in ['name', 'email']:
                css = self.fields[field_name].widget.attrs.get('class', '')
                if 'form-input' not in css:
                    self.fields[field_name].widget.attrs['class'] = (css + ' form-input').strip()

        # Ustaw minimalną datę na dziś (po stronie frontendu)
        self.fields['date'].widget.attrs['min'] = timezone.localdate().isoformat()

    class Meta:
        model = Reservation
        fields = ['name','email','date','time_from','time_to']
        widgets={'date':forms.DateInput(attrs={'type':'date'}),
                 'time_from':forms.TimeInput(attrs={'type':'time'}),
                 'time_to':forms.TimeInput(attrs={'type':'time'})}

    def clean(self):
        cleaned = super().clean()
        booking_date = cleaned.get('date')
        time_from = cleaned.get('time_from')
        time_to = cleaned.get('time_to')

        today = timezone.localdate()

        if booking_date and booking_date < today:
            self.add_error('date', 'Nie można rezerwować dat w przeszłości.')
        if time_from and time_to and time_from >= time_to:
            self.add_error('time_from', 'Godzina rozpoczęcia musi być wcześniejsza niż zakończenia.')
            self.add_error('time_to', 'Godzina zakończenia musi być późniejsza niż rozpoczęcia.')

        return cleaned

class RecurringReservationForm(forms.ModelForm):
    class Meta:
        model = RecurringReservation
        fields = ['name', 'email', 'start_date', 'end_date', 'time_from', 'time_to', 'frequency', 'days_of_week']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'time_from': forms.TimeInput(attrs={'type': 'time'}),
            'time_to': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['end_date'].required = False
        self.fields['days_of_week'].widget = forms.CheckboxSelectMultiple(
            choices=[
                ('1', 'Poniedziałek'),
                ('2', 'Wtorek'),
                ('3', 'Środa'),
                ('4', 'Czwartek'),
                ('5', 'Piątek'),
                ('6', 'Sobota'),
                   ('7', 'Niedziela'),
               ]
           )

class GroupReservationForm(forms.ModelForm):
    class Meta:
        model = GroupReservation
        fields = ['group_name', 'organizer_email', 'date', 'time_from', 'time_to', 'purpose']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time_from': forms.TimeInput(attrs={'type': 'time'}),
            'time_to': forms.TimeInput(attrs={'type': 'time'}),
            'purpose': forms.Textarea(attrs={'rows': 3}),
        }

class WaitlistForm(forms.ModelForm):
    class Meta:
        model = Waitlist
        fields = ['name', 'email', 'preferred_date', 'time_from', 'time_to']
        widgets = {
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'time_from': forms.TimeInput(attrs={'type': 'time'}),
            'time_to': forms.TimeInput(attrs={'type': 'time'}),
        }


class GuestReservationForm(forms.ModelForm):
    class Meta:
        model = GuestReservation
        fields = ['guest_name', 'guest_email', 'host_name', 'host_email', 'date', 'time_from', 'time_to', 'purpose']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time_from': forms.TimeInput(attrs={'type': 'time'}),
            'time_to': forms.TimeInput(attrs={'type': 'time'}),
            'purpose': forms.Textarea(attrs={'rows': 3}),
        }

class ConferenceReservationForm(forms.ModelForm):
    class Meta:
        model = ConferenceReservation
        fields = ['team_name', 'contact_email', 'date', 'time_from', 'time_to', 'attendees_count', 'purpose']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time_from': forms.TimeInput(attrs={'type': 'time'}),
            'time_to': forms.TimeInput(attrs={'type': 'time'}),
            'purpose': forms.Textarea(attrs={'rows': 3}),
        }
