/**
 * i18n Helper for Dashboard
 * Provides translations for JavaScript code
 */

class I18n {
  constructor() {
    this.translations = {};
    this.currentLanguage = document.documentElement.lang || 'pl';
    this.loadTranslations();
  }

  loadTranslations() {
    // Translations for common strings used in JavaScript
    this.translations = {
      'pl': {
        // Profile
        'Profile updated successfully': 'Profil został zaktualizowany',
        'Error saving profile': 'Błąd podczas zapisywania profilu',
        'Password changed successfully': 'Hasło zostało zmienione',
        'Error changing password': 'Błąd podczas zmiany hasła',
        'New passwords do not match': 'Nowe hasła nie są identyczne',
        'Password must be at least 8 characters': 'Hasło musi mieć minimum 8 znaków',
        'Current password is incorrect': 'Obecne hasło jest nieprawidłowe',
        'All password fields are required': 'Wszystkie pola hasła są wymagane',
        
        // Quick Book
        'Reservation created successfully': 'Rezerwacja została utworzona',
        'Error creating reservation': 'Błąd podczas tworzenia rezerwacji',
        'Please fill in all required fields': 'Proszę wypełnić wszystkie wymagane pola',
        'End time must be after start time': 'Czas zakończenia musi być po czasie rozpoczęcia',
        'Reservation already exists': 'Rezerwacja już istnieje',
        
        // Notifications
        'No notifications': 'Brak powiadomień',
        'Error loading notifications': 'Błąd podczas ładowania powiadomień',
        'Mark all as read': 'Oznacz wszystkie jako przeczytane',
        
        // Calendar
        'Error loading calendar': 'Błąd podczas ładowania kalendarza',
        'Reservation': 'Rezerwacja',
        'Desk': 'Stanowisko',
        'Upcoming reservation': 'Nadchodząca rezerwacja',
        'Latest reservation': 'Najnowsza rezerwacja',
        
        // Statistics
        'No favorite seats': 'Brak ulubionych stanowisk',
        'reservations': 'rezerwacji',
        'Today': 'Dzisiaj',
        '1 day': '1 dzień',
        'days': 'dni',
        '1 month': '1 miesiąc',
        'months': 'miesięcy',
        '1 year': '1 rok',
        'years': 'lat',
        'Active': 'Aktywne',
        'Inactive': 'Nieaktywne',
        
        // General
        'Are you sure you want to logout?': 'Czy na pewno chcesz się wylogować?',
        'Loading...': 'Ładowanie...',
        'Error': 'Błąd',
        'Success': 'Sukces',
        'Info': 'Informacja',
        'Error loading summary': 'Błąd podczas ładowania podsumowania',
        'Error loading statistics': 'Błąd podczas ładowania statystyk',
        'Never': 'Nigdy',
        'Creating...': 'Tworzenie...',
        'Please fill in all required fields': 'Proszę wypełnić wszystkie wymagane pola',
        'End time must be after start time': 'Czas zakończenia musi być po czasie rozpoczęcia',
        'Please enter a valid email address': 'Proszę podać prawidłowy adres email',
        'Reservation created successfully': 'Rezerwacja została utworzona!',
        'Error creating reservation': 'Nie udało się utworzyć rezerwacji',
        'Reservation cancelled successfully': 'Rezerwacja została anulowana!',
        'Error cancelling reservation': 'Nie udało się anulować rezerwacji',
        'Try again': 'Spróbuj ponownie',
        'All notifications marked as read': 'Wszystkie powiadomienia zostały oznaczone jako przeczytane',
        'Are you sure you want to cancel this reservation?': 'Czy na pewno chcesz anulować tę rezerwację?',
        
        // Auth pages
        'Please fill in all fields': 'Proszę wypełnić wszystkie pola',
        'Please enter your email': 'Proszę podać adres email',
        'Please enter verification code': 'Proszę podać kod weryfikacyjny',
        'Password is too weak': 'Hasło jest zbyt słabe',
        'Registration successful! Redirecting...': 'Rejestracja pomyślna! Przekierowywanie...',
        'Verification code sent to your email': 'Kod weryfikacyjny został wysłany na Twój email',
        'Magic link sent to your email!': 'Link logowania został wysłany na Twój email!',
        'Weak': 'Słabe',
        'Medium': 'Średnie',
        'Strong': 'Silne',
      },
      'en': {
        // Profile
        'Profile updated successfully': 'Profile updated successfully',
        'Error saving profile': 'Error saving profile',
        'Password changed successfully': 'Password changed successfully',
        'Error changing password': 'Error changing password',
        'New passwords do not match': 'New passwords do not match',
        'Password must be at least 8 characters': 'Password must be at least 8 characters',
        'Current password is incorrect': 'Current password is incorrect',
        'All password fields are required': 'All password fields are required',
        
        // Quick Book
        'Reservation created successfully': 'Reservation created successfully',
        'Error creating reservation': 'Error creating reservation',
        'Please fill in all required fields': 'Please fill in all required fields',
        'End time must be after start time': 'End time must be after start time',
        'Reservation already exists': 'Reservation already exists',
        
        // Notifications
        'No notifications': 'No notifications',
        'Error loading notifications': 'Error loading notifications',
        'Mark all as read': 'Mark all as read',
        
        // Calendar
        'Error loading calendar': 'Error loading calendar',
        'Reservation': 'Reservation',
        'Desk': 'Desk',
        'Upcoming reservation': 'Upcoming reservation',
        'Latest reservation': 'Latest reservation',
        
        // Statistics
        'No favorite seats': 'No favorite seats',
        'reservations': 'reservations',
        'Today': 'Today',
        '1 day': '1 day',
        'days': 'days',
        '1 month': '1 month',
        'months': 'months',
        '1 year': '1 year',
        'years': 'years',
        'Active': 'Active',
        'Inactive': 'Inactive',
        
        // General
        'Are you sure you want to logout?': 'Are you sure you want to logout?',
        'Loading...': 'Loading...',
        'Error': 'Error',
        'Success': 'Success',
        'Info': 'Info',
        'Error loading summary': 'Error loading summary',
        'Error loading statistics': 'Error loading statistics',
        'Never': 'Never',
        'Creating...': 'Creating...',
        'Please fill in all required fields': 'Please fill in all required fields',
        'End time must be after start time': 'End time must be after start time',
        'Please enter a valid email address': 'Please enter a valid email address',
        'Reservation created successfully': 'Reservation created successfully',
        'Error creating reservation': 'Error creating reservation',
        'Reservation cancelled successfully': 'Reservation cancelled successfully',
        'Error cancelling reservation': 'Error cancelling reservation',
        'Try again': 'Try again',
        'All notifications marked as read': 'All notifications marked as read',
        'Are you sure you want to cancel this reservation?': 'Are you sure you want to cancel this reservation?',
        
        // Auth pages
        'Please fill in all fields': 'Please fill in all fields',
        'Please enter your email': 'Please enter your email',
        'Please enter verification code': 'Please enter verification code',
        'Password is too weak': 'Password is too weak',
        'Registration successful! Redirecting...': 'Registration successful! Redirecting...',
        'Verification code sent to your email': 'Verification code sent to your email',
        'Magic link sent to your email!': 'Magic link sent to your email!',
        'Weak': 'Weak',
        'Medium': 'Medium',
        'Strong': 'Strong',
      }
    };
  }

  t(key, params = {}) {
    const lang = this.currentLanguage || 'pl';
    let translation = this.translations[lang]?.[key] || key;
    
    // Replace placeholders
    if (params && Object.keys(params).length > 0) {
      Object.keys(params).forEach(param => {
        translation = translation.replace(`{{${param}}}`, params[param]);
      });
    }
    
    return translation;
  }

  setLanguage(lang) {
    this.currentLanguage = lang;
    document.documentElement.lang = lang;
  }
}

// Create global instance
window.i18n = new I18n();

// Helper function for easy access
window.t = (key, params) => window.i18n.t(key, params);

