// Calendar management
class CalendarManager {
  constructor() {
    this.calendar = null;
    this.init();
  }

  init() {
    if (document.getElementById('calendar')) {
      this.initializeCalendar();
      this.loadReservations();
      this.startAutoRefresh();
      this.bindRealTimeEvents();
    }
  }

  startAutoRefresh() {
    // Auto-refresh calendar every 30 seconds
    this.refreshInterval = setInterval(() => {
      this.loadReservations();
    }, 30000); // 30 seconds

    // Refresh when page becomes visible
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') {
        this.loadReservations();
      }
    });
  }

  bindRealTimeEvents() {
    // Listen for reservation events and refresh calendar immediately
    window.addEventListener('reservation:created', () => {
      this.loadReservations();
    });

    window.addEventListener('reservation:deleted', () => {
      this.loadReservations();
    });

    window.addEventListener('reservation:updated', () => {
      this.loadReservations();
    });
  }

  initializeCalendar() {
    // Get current language
    const currentLang = document.documentElement.lang || 'pl';
    const isEnglish = currentLang === 'en';
    
    // Calendar translations based on language
    const calendarTranslations = {
      pl: {
        noEventsText: 'Brak wydarzeń',
        moreLinkText: 'więcej',
        loadingText: 'Ładowanie...',
        errorText: 'Błąd podczas ładowania wydarzeń',
        today: 'Dziś',
        month: 'Miesiąc',
        week: 'Tydzień',
        day: 'Dzień',
        list: 'Lista',
        prev: 'Poprzedni',
        next: 'Następny',
        prevYear: 'Poprzedni rok',
        nextYear: 'Następny rok',
        prevMonth: 'Poprzedni miesiąc',
        nextMonth: 'Następny miesiąc',
        allDayText: 'Cały dzień',
        dayNames: ['Niedziela', 'Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota'],
        dayNamesShort: ['Ndz', 'Pon', 'Wt', 'Śr', 'Czw', 'Pt', 'Sob'],
        dayNamesMin: ['Nd', 'Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'So'],
        monthNames: ['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec', 'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień'],
        monthNamesShort: ['Sty', 'Lut', 'Mar', 'Kwi', 'Maj', 'Cze', 'Lip', 'Sie', 'Wrz', 'Paź', 'Lis', 'Gru']
      },
      en: {
        noEventsText: 'No events',
        moreLinkText: 'more',
        loadingText: 'Loading...',
        errorText: 'Error loading events',
        today: 'Today',
        month: 'Month',
        week: 'Week',
        day: 'Day',
        list: 'List',
        prev: 'Previous',
        next: 'Next',
        prevYear: 'Previous year',
        nextYear: 'Next year',
        prevMonth: 'Previous month',
        nextMonth: 'Next month',
        allDayText: 'All day',
        dayNames: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        dayNamesShort: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        dayNamesMin: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
        monthNames: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
        monthNamesShort: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      }
    };
    
    const t = calendarTranslations[currentLang] || calendarTranslations.pl;
    
    this.calendar = new FullCalendar.Calendar(document.getElementById('calendar'), {
      initialView: 'dayGridMonth',
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,listWeek'
      },
      height: 450,
      dayMaxEvents: 3,
      moreLinkClick: 'popover',
      noEventsText: t.noEventsText,
      moreLinkText: t.moreLinkText,
      eventClick: (info) => this.handleEventClick(info),
      dateClick: (info) => this.handleDateClick(info),
      eventDidMount: (info) => this.handleEventMount(info),
      themeSystem: 'standard',
      aspectRatio: 1.8,
      eventDisplay: 'block',
      eventTimeFormat: {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      },
      eventTextColor: '#ffffff',
      eventBackgroundColor: '#3b82f6',
      slotMinTime: '07:00:00',
      slotMaxTime: '20:00:00',
      weekends: true,
      firstDay: 1, // Monday
      buttonText: {
        today: t.today,
        month: t.month,
        week: t.week,
        day: t.day,
        list: t.list
      },
      dayHeaderFormat: { weekday: 'short' },
      titleFormat: { year: 'numeric', month: 'long' },
      locale: currentLang,
      firstDay: 1,
      dayNames: t.dayNames,
      dayNamesShort: t.dayNamesShort,
      dayNamesMin: t.dayNamesMin,
      monthNames: t.monthNames,
      monthNamesShort: t.monthNamesShort,
      allDayText: t.allDayText,
      today: t.today,
      prev: t.prev,
      next: t.next,
      prevYear: t.prevYear,
      nextYear: t.nextYear,
      prevMonth: t.prevMonth,
      nextMonth: t.nextMonth,
      weekText: t.week,
      weekTextLong: t.week,
      dayText: t.day,
      listText: t.list,
      noEventsText: t.noEventsText,
      moreLinkText: t.moreLinkText,
      loadingText: t.loadingText,
      errorText: t.errorText
    });

    this.calendar.render();
    this.bindCalendarControls();
  }

  async loadReservations() {
    try {
      const response = await fetch('/api/dashboard/api/reservations/calendar/', {
        credentials: 'include',
        headers: {
          'X-CSRFToken': this.getCSRFToken()
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const reservations = await response.json();

      if (this.calendar && Array.isArray(reservations)) {
        this.calendar.removeAllEvents();
        // Add events directly instead of using addEventSource
        reservations.forEach(event => {
          this.calendar.addEvent(event);
        });
      }
    } catch (error) {
      console.error('Error loading reservations:', error);
      const errorMsg = window.t ? window.t('Error loading calendar') : 'Error loading calendar';
      console.error(errorMsg, error);
    }
  }

  getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'csrftoken') {
        return value;
      }
    }
    return '';
  }

  bindCalendarControls() {
    const todayBtn = document.getElementById('calendarToday');
    const prevBtn = document.getElementById('calendarPrev');
    const nextBtn = document.getElementById('calendarNext');

    if (todayBtn) {
      todayBtn.addEventListener('click', () => {
        if (this.calendar) {
          this.calendar.today();
        }
      });
    }

    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        if (this.calendar) {
          this.calendar.prev();
        }
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        if (this.calendar) {
          this.calendar.next();
        }
      });
    }
  }

  handleEventClick(info) {
    const event = info.event;
    const reservationId = event.id;
    
    // Show event details popup instead of opening new tab
    this.showEventDetails(event);
  }

  handleDateClick(info) {
    // Open quick book modal for the clicked date
    const dateInput = document.getElementById('qbDate');
    if (dateInput) {
      dateInput.value = info.dateStr;
    }
    
    const quickBook = new QuickBook();
    quickBook.open();
  }

  handleEventMount(info) {
    const event = info.event;
    const element = info.el;
    
    // Add custom styling based on event type
    if (event.extendedProps.type === 'group') {
      element.style.borderLeft = '4px solid #10b981';
    } else if (event.extendedProps.type === 'recurring') {
      element.style.borderLeft = '4px solid #8b5cf6';
    } else if (event.extendedProps.type === 'team') {
      element.style.borderLeft = '4px solid #f59e0b';
    }

    // Add tooltip
    const currentLang = document.documentElement.lang || 'pl';
    const floorLabel = currentLang === 'en' ? 'Floor' : 'Piętro';
    const noFloorText = currentLang === 'en' ? 'N/A' : 'Brak';
    element.title = `${event.title}\n${event.start.toLocaleString(currentLang === 'en' ? 'en-US' : 'pl-PL')}\n${floorLabel}: ${event.extendedProps.floor || noFloorText}`;
  }

  refresh() {
    this.loadReservations();
  }

  updateLanguage(lang) {
    // Reinitialize calendar with new language
    if (this.calendar) {
      this.calendar.destroy();
    }
    this.initializeCalendar();
  }

  showEventDetails(event) {
    // Get translations
    const currentLang = document.documentElement.lang || 'pl';
    const translations = {
      pl: {
        desk: 'Stanowisko',
        floor: 'Piętro',
        time: 'Czas',
        reservedBy: 'Zarezerwowane przez',
        purpose: 'Cel',
        noPurpose: 'Brak',
        noFloor: 'Brak',
        downloadIcs: 'Pobierz .ics',
        viewDetails: 'Zobacz Szczegóły'
      },
      en: {
        desk: 'Desk',
        floor: 'Floor',
        time: 'Time',
        reservedBy: 'Reserved by',
        purpose: 'Purpose',
        noPurpose: 'N/A',
        noFloor: 'N/A',
        downloadIcs: 'Download .ics',
        viewDetails: 'View Details'
      }
    };
    const t = translations[currentLang] || translations.pl;
    
    // Create a nice popup with event details
    const popup = document.createElement('div');
    popup.className = 'event-popup';
    popup.innerHTML = `
      <div class="event-popup-content">
        <div class="event-popup-header">
          <h4>${t.desk} ${event.extendedProps.desk_label || event.title}</h4>
          <button class="event-popup-close">&times;</button>
        </div>
        <div class="event-popup-body">
          <p><strong>${t.floor}:</strong> ${event.extendedProps.floor || t.noFloor}</p>
          <p><strong>${t.time}:</strong> ${event.start.toLocaleTimeString(currentLang === 'en' ? 'en-US' : 'pl-PL')} - ${event.end.toLocaleTimeString(currentLang === 'en' ? 'en-US' : 'pl-PL')}</p>
          <p><strong>${t.reservedBy}:</strong> ${event.extendedProps.user_email || ''}</p>
          <p><strong>${t.purpose}:</strong> ${event.extendedProps.purpose || t.noPurpose}</p>
        </div>
        <div class="event-popup-actions">
          <button class="btn btn-primary btn-sm" onclick="window.open('/reservations/reservation/${event.id}/ics/', '_blank')">
            <i class="fas fa-download"></i> ${t.downloadIcs}
          </button>
          <button class="btn btn-ghost btn-sm" onclick="window.open('/reservation/${event.id}/', '_blank')">
            <i class="fas fa-external-link-alt"></i> ${t.viewDetails}
          </button>
        </div>
      </div>
    `;
    
    // Add styles
    popup.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    `;
    
    const content = popup.querySelector('.event-popup-content');
    content.style.cssText = `
      background: white;
      border-radius: 12px;
      padding: 1.5rem;
      max-width: 400px;
      width: 90%;
      box-shadow: 0 20px 25px rgba(0, 0, 0, 0.1);
      position: relative;
    `;
    
    const header = popup.querySelector('.event-popup-header');
    header.style.cssText = `
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid #e5e7eb;
    `;
    
    const closeBtn = popup.querySelector('.event-popup-close');
    closeBtn.style.cssText = `
      background: none;
      border: none;
      font-size: 1.5rem;
      cursor: pointer;
      color: #6b7280;
    `;
    
    const actions = popup.querySelector('.event-popup-actions');
    actions.style.cssText = `
      display: flex;
      gap: 0.5rem;
      margin-top: 1rem;
      justify-content: flex-end;
    `;
    
    document.body.appendChild(popup);
    
    // Close popup handlers
    closeBtn.addEventListener('click', () => popup.remove());
    popup.addEventListener('click', (e) => {
      if (e.target === popup) popup.remove();
    });
  }

  navigateToDate(date) {
    if (this.calendar) {
      this.calendar.gotoDate(date);
    }
  }

  changeView(view) {
    if (this.calendar) {
      this.calendar.changeView(view);
    }
  }
}

// Make calendar manager globally available
window.calendarManager = new CalendarManager();
