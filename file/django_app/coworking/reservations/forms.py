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
    DAY_CHOICES = [
        ('1', 'Poniedziałek'),
        ('2', 'Wtorek'),
        ('3', 'Środa'),
        ('4', 'Czwartek'),
        ('5', 'Piątek'),
        ('6', 'Sobota'),
        ('7', 'Niedziela'),
    ]
    
    class Meta:
        model = RecurringReservation
        fields = ['name', 'email', 'start_date', 'end_date', 'time_from', 'time_to', 'frequency', 'days_of_week']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'time_from': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'time_to': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'frequency': forms.Select(attrs={'class': 'form-input'}),
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['end_date'].required = False
        # Zmień pole days_of_week na MultipleChoiceField zamiast CharField
        # to pozwoli na poprawną obsługę checkboxów
        self.fields['days_of_week'] = forms.MultipleChoiceField(
            choices=self.DAY_CHOICES,
            widget=forms.CheckboxSelectMultiple(attrs={'class': 'days-of-week-checkboxes'}),
            required=True,
            label='Dni tygodnia'
        )
        
        # Pre-fill user data if authenticated
        if user and getattr(user, 'is_authenticated', False):
            self.fields['name'].initial = getattr(user, 'full_name', '') or user.email.split('@')[0]
            self.fields['email'].initial = user.email
            self.fields['name'].widget.attrs.update({
                'readonly': 'readonly',
                'class': self.fields['name'].widget.attrs.get('class', '') + ' bg-gray-100 cursor-not-allowed',
            })
            self.fields['email'].widget.attrs.update({
                'readonly': 'readonly',
                'class': self.fields['email'].widget.attrs.get('class', '') + ' bg-gray-100 cursor-not-allowed',
            })
        
        # Set minimum date to today
        from django.utils import timezone
        self.fields['start_date'].widget.attrs['min'] = timezone.localdate().isoformat()
        if self.fields['end_date'].initial:
            self.fields['end_date'].widget.attrs['min'] = timezone.localdate().isoformat()
        
        # Default time values
        if not self.fields['time_from'].initial:
            self.fields['time_from'].initial = '09:00'
        if not self.fields['time_to'].initial:
            self.fields['time_to'].initial = '17:00'
        
        # Default to weekly if not set
        if not self.fields['frequency'].initial:
            self.fields['frequency'].initial = 'WEEKLY'
        
        # Default to weekdays if not set
        if not self.fields['days_of_week'].initial:
            # Jeśli instancja istnieje (edycja), skonwertuj string do listy
            if self.instance and self.instance.pk and isinstance(self.instance.days_of_week, str):
                days_list = []
                for i, char in enumerate(self.instance.days_of_week):
                    if char == '1':
                        days_list.append(str(i + 1))
                self.fields['days_of_week'].initial = days_list
            else:
                self.fields['days_of_week'].initial = ['1', '2', '3', '4', '5']  # Mon-Fri
    
    def clean_days_of_week(self):
        """Konwertuj listę checkboxów na string format '1111111'"""
        # W Django clean_<field>(), wartość jest przetwarzana przez pole przed wywołaniem
        # Dla MultipleChoiceField, wartość jest już listą, ale może być też pusta
        
        # Pobierz wartość bezpośrednio z danych formularza (QueryDict.getlist())
        days_of_week = []
        if hasattr(self, 'data'):
            if hasattr(self.data, 'getlist'):
                days_of_week = self.data.getlist('days_of_week')
            elif 'days_of_week' in self.data:
                value = self.data.get('days_of_week')
                if isinstance(value, list):
                    days_of_week = value
                elif value:
                    days_of_week = [value]
        
        # Jeśli to lista jest pusta, sprawdź czy może jest w cleaned_data (po to_python)
        if not days_of_week and 'days_of_week' in self.cleaned_data:
            value = self.cleaned_data['days_of_week']
            if isinstance(value, list):
                days_of_week = value
            elif isinstance(value, str):
                # Jeśli to string (z modelu przy edycji), skonwertuj do listy
                if len(value) == 7 and all(c in '01' for c in value):
                    days_list = []
                    for i, char in enumerate(value):
                        if char == '1':
                            days_list.append(str(i + 1))
                    days_of_week = days_list
        
        # Upewnij się, że to lista
        if not isinstance(days_of_week, list):
            days_of_week = []
        
        # Walidacja - przynajmniej jeden dzień musi być wybrany
        if not days_of_week:
            raise forms.ValidationError('Musisz wybrać co najmniej jeden dzień tygodnia.')
        
        # Konwertuj listę na string format '1111111'
        days_str = ['0'] * 7
        for day in days_of_week:
            try:
                idx = int(day) - 1
                if 0 <= idx < 7:
                    days_str[idx] = '1'
            except (ValueError, TypeError):
                continue
        
        result = ''.join(days_str)
        
        # Ponowna walidacja - upewnij się, że przynajmniej jeden dzień jest wybrany
        if not any(d == '1' for d in days_str):
            raise forms.ValidationError('Musisz wybrać co najmniej jeden dzień tygodnia.')
        
        return result
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        time_from = cleaned_data.get('time_from')
        time_to = cleaned_data.get('time_to')
        frequency = cleaned_data.get('frequency')
        
        from django.utils import timezone
        today = timezone.localdate()
        
        if start_date and start_date < today:
            self.add_error('start_date', 'Data rozpoczęcia nie może być w przeszłości.')
        
        if end_date and start_date and end_date < start_date:
            self.add_error('end_date', 'Data zakończenia musi być późniejsza niż data rozpoczęcia.')
        
        if time_from and time_to and time_from >= time_to:
            self.add_error('time_from', 'Godzina rozpoczęcia musi być wcześniejsza niż zakończenia.')
            self.add_error('time_to', 'Godzina zakończenia musi być późniejsza niż rozpoczęcia.')
        
        return cleaned_data

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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set minimum date to today
        from django.utils import timezone
        self.fields['date'].widget.attrs['min'] = timezone.localdate().isoformat()
    
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time_from = cleaned_data.get('time_from')
        time_to = cleaned_data.get('time_to')
        
        from django.utils import timezone
        today = timezone.localdate()
        
        if date and date < today:
            self.add_error('date', 'Nie można rezerwować dat w przeszłości.')
        
        if time_from and time_to and time_from >= time_to:
            self.add_error('time_from', 'Godzina rozpoczęcia musi być wcześniejsza niż zakończenia.')
            self.add_error('time_to', 'Godzina zakończenia musi być późniejsza niż rozpoczęcia.')
        
        return cleaned_data

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
