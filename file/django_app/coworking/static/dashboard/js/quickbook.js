// Quick book functionality
class QuickBook {
  constructor() {
    this.modal = document.getElementById('qbModal');
    this.form = this.modal?.querySelector('.modern-modal-card');
    this.bindEvents();
    this.setDefaultDate();
  }

  bindEvents() {
    const quickBookBtn = document.getElementById('quickBookBtn');
    const quickReserveBtn = document.getElementById('quickReserveBtn');
    const cancelBtn = document.getElementById('qbCancel');
    const createBtn = document.getElementById('qbCreate');
    const timeFromInput = document.getElementById('qbTimeFrom');
    const timeToInput = document.getElementById('qbTimeTo');

    if (quickBookBtn) {
      quickBookBtn.addEventListener('click', () => this.open());
    }

    if (quickReserveBtn) {
      quickReserveBtn.addEventListener('click', () => this.open());
    }

    if (cancelBtn) {
      cancelBtn.addEventListener('click', () => this.close());
    }

    if (createBtn) {
      createBtn.addEventListener('click', () => this.createReservation());
    }

    // Validate time range dynamically
    if (timeFromInput && timeToInput) {
      timeFromInput.addEventListener('change', () => {
        const timeFrom = timeFromInput.value;
        if (timeFrom) {
          // Set minimum time for time_to to be at least 1 minute after time_from
          const [hours, minutes] = timeFrom.split(':');
          const fromDate = new Date();
          fromDate.setHours(parseInt(hours), parseInt(minutes) + 1, 0, 0);
          const minTime = fromDate.toTimeString().slice(0, 5);
          timeToInput.min = minTime;
          
          // If current time_to is less than or equal to time_from, update it
          if (timeToInput.value && timeToInput.value <= timeFrom) {
            timeToInput.value = minTime;
          }
        }
      });
      
      timeToInput.addEventListener('change', () => {
        const timeFrom = timeFromInput.value;
        const timeTo = timeToInput.value;
        if (timeFrom && timeTo && timeTo <= timeFrom) {
          const currentLang = document.documentElement.lang || 'pl';
          const errorMsg = currentLang === 'pl' 
            ? 'Godzina zakończenia musi być późniejsza niż rozpoczęcia'
            : 'End time must be after start time';
          this.showNotification(errorMsg, 'error');
          // Reset to valid minimum
          const [hours, minutes] = timeFrom.split(':');
          const fromDate = new Date();
          fromDate.setHours(parseInt(hours), parseInt(minutes) + 1, 0, 0);
          timeToInput.value = fromDate.toTimeString().slice(0, 5);
        }
      });
    }

    // Close modal on backdrop click
    if (this.modal) {
      const backdrop = this.modal.querySelector('.modal-backdrop');
      if (backdrop) {
        backdrop.addEventListener('click', () => this.close());
      }
    }

    // Close modal on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen()) {
        this.close();
      }
    });
  }

  setDefaultDate() {
    const dateInput = document.getElementById('qbDate');
    if (dateInput) {
      const today = new Date();
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);
      dateInput.value = tomorrow.toISOString().split('T')[0];
      // Set minimum date to today
      dateInput.min = today.toISOString().split('T')[0];
    }
  }

  open() {
    if (this.modal) {
      this.modal.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      this.setDefaultDate();
    }
  }

  close() {
    if (this.modal) {
      this.modal.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      this.clearForm();
    }
  }

  isOpen() {
    return this.modal?.getAttribute('aria-hidden') === 'false';
  }

  clearForm() {
    const inputs = this.form?.querySelectorAll('.modern-input');
    if (inputs) {
      inputs.forEach(input => {
        if (input.type === 'checkbox' || input.type === 'radio') {
          input.checked = false;
        } else {
          input.value = '';
        }
      });
    }
    this.setDefaultDate();
  }

  async createReservation() {
    const formData = this.getFormData();
    
    if (!this.validateForm(formData)) {
      return;
    }

    const createBtn = document.getElementById('qbCreate');
    const originalText = createBtn.textContent;
    const creatingText = window.t ? window.t('Creating...') : 'Creating...';
    createBtn.textContent = creatingText;
    createBtn.disabled = true;

    try {
      const response = await fetch('/api/dashboard/api/quick-reserve/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify(formData)
      });

      const result = await response.json();

             if (response.ok) {
               const successMsg = window.t ? window.t('Reservation created successfully') : 'Reservation created successfully';
               this.showNotification(successMsg, 'success');
               
               // Emit event with actual reservation data from API response
               window.dispatchEvent(new CustomEvent('reservation:created', { 
                 detail: {
                   id: result.reservation_id,
                   seat_id: formData.desk,
                   date: formData.date,
                   name: formData.name,
                   email: formData.email
                 }
               }));
               
               this.close();
               this.refreshDashboard();
               
               // Offer to download .ics file
               this.offerCalendarDownload(result.reservation_id);
             } else {
               const errorMsg = window.t ? window.t('Error creating reservation') : 'Error creating reservation';
               this.showNotification(result.error || errorMsg, 'error');
             }
    } catch (error) {
      console.error('Error creating reservation:', error);
      const errorMsg = window.t ? window.t('Error creating reservation') : 'Error creating reservation';
      this.showNotification(errorMsg, 'error');
    } finally {
      createBtn.textContent = originalText;
      createBtn.disabled = false;
    }
  }

  getFormData() {
    return {
      date: document.getElementById('qbDate')?.value,
      floor: document.getElementById('qbFloor')?.value,
      desk: document.getElementById('qbDesk')?.value,
      time_from: document.getElementById('qbTimeFrom')?.value,
      time_to: document.getElementById('qbTimeTo')?.value,
      name: document.getElementById('qbName')?.value,
      email: document.getElementById('qbEmail')?.value
    };
  }

  validateForm(data) {
    const required = ['date', 'desk', 'name', 'email'];
    const missing = required.filter(field => !data[field]);

    if (missing.length > 0) {
      const fillAllMsg = window.t ? window.t('Please fill in all required fields') : 'Please fill in all required fields';
      this.showNotification(fillAllMsg, 'error');
      return false;
    }

    // Validate date is not in the past
    if (data.date) {
      const selectedDate = new Date(data.date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      selectedDate.setHours(0, 0, 0, 0);
      
      if (selectedDate < today) {
        const currentLang = document.documentElement.lang || 'pl';
        const dateErrorMsg = currentLang === 'pl' 
          ? 'Nie można rezerwować dat w przeszłości'
          : 'Cannot reserve dates in the past';
        this.showNotification(dateErrorMsg, 'error');
        return false;
      }
    }

    // Validate time if both are provided
    if (data.time_from && data.time_to && data.time_from >= data.time_to) {
      const timeErrorMsg = window.t ? window.t('End time must be after start time') : 'End time must be after start time';
      this.showNotification(timeErrorMsg, 'error');
      return false;
    }

    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
      const emailErrorMsg = window.t ? window.t('Please enter a valid email address') : 'Please enter a valid email address';
      this.showNotification(emailErrorMsg, 'error');
      return false;
    }

    return true;
  }

  getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
  }

  showNotification(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelectorAll('.notification');
    existing.forEach(n => n.remove());

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
      <div style="display: flex; align-items: center; gap: 0.5rem;">
        <i class="fas fa-${this.getNotificationIcon(type)}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.parentElement.remove()" style="margin-left: auto; background: none; border: none; color: inherit; cursor: pointer;">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `;

    document.body.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
      if (notification.parentElement) {
        notification.remove();
      }
    }, 5000);
  }

  getNotificationIcon(type) {
    const icons = {
      success: 'check-circle',
      error: 'exclamation-circle',
      warning: 'exclamation-triangle',
      info: 'info-circle'
    };
    return icons[type] || 'info-circle';
  }

  refreshDashboard() {
    // Refresh calendar and charts
    if (window.calendarManager) {
      window.calendarManager.loadReservations();  // Reload reservations from API
    }
    if (window.chartManager) {
      window.chartManager.refresh();
    }
    if (window.dashboardManager) {
      window.dashboardManager.loadSummary();  // Reload summary with upcoming reservations count
    }
  }

  offerCalendarDownload(reservationId) {
    // Show notification with download option
    const currentLang = document.documentElement.lang || 'pl';
    const addToCalendarMsg = currentLang === 'en' 
      ? 'Reservation created! Add to calendar?' 
      : 'Rezerwacja utworzona! Dodać do kalendarza?';
    const downloadIcsText = window.t ? window.t('Download .ics') : (currentLang === 'en' ? 'Download .ics' : 'Pobierz .ics');
    
    const notification = document.createElement('div');
    notification.className = 'notification success';
    notification.innerHTML = `
      <div style="display: flex; align-items: center; gap: 0.5rem;">
        <i class="fas fa-calendar-plus"></i>
        <span>${addToCalendarMsg}</span>
        <button onclick="window.open('/reservations/reservation/${reservationId}/ics/', '_blank')" 
                style="margin-left: auto; background: var(--primary); color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.25rem; cursor: pointer; font-size: 0.875rem;">
          <i class="fas fa-download"></i> ${downloadIcsText}
        </button>
        <button onclick="this.parentElement.parentElement.remove()" 
                style="background: none; border: none; color: inherit; cursor: pointer; padding: 0.25rem;">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `;

    document.body.appendChild(notification);

    // Auto remove after 10 seconds
    setTimeout(() => {
      if (notification.parentElement) {
        notification.remove();
      }
    }, 10000);
  }
}

// Initialize quick book
document.addEventListener('DOMContentLoaded', () => {
  new QuickBook();
});
