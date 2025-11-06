from django import forms
from .models import Reservation, RecurringReservation, Waitlist, GuestReservation, GroupReservation, ConferenceReservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['name','email','date','time_from','time_to']
        widgets={'date':forms.DateInput(attrs={'type':'date'}),
                 'time_from':forms.TimeInput(attrs={'type':'time'}),
                 'time_to':forms.TimeInput(attrs={'type':'time'})}

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
