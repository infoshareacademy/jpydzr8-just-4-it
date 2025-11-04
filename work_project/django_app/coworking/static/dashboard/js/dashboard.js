// Main dashboard functionality
class DashboardManager {
  constructor() {
    this.reservations = [];
    this.init();
  }

  init() {
    this.loadReservations();
    this.loadSummary();
    this.bindEvents();
  }

  async loadReservations() {
    // Reservations are now handled by the calendar
    // This method is kept for compatibility but does nothing
  }

  async loadSummary() {
    try {
      const response = await fetch('/api/dashboard/api/reservations/summary/');
      const data = await response.json();
      
      if (response.ok) {
        this.updateSummary(data);
        this.updateStats(data);
      }
    } catch (error) {
      console.error('Error loading summary:', error);
      const errorMsg = window.t ? window.t('Error loading summary') : 'Error loading summary';
      console.error(errorMsg, error);
    }
  }

  updateStats(data) {
    // Update stat cards
    const totalReservations = document.getElementById('totalReservations');
    const upcomingReservations = document.getElementById('upcomingReservations');
    const favoriteDesks = document.getElementById('favoriteDesks');
    const efficiency = document.getElementById('efficiency');

    if (totalReservations) {
      totalReservations.textContent = data.total_reservations || '0';
    }
    
    if (upcomingReservations) {
      upcomingReservations.textContent = data.upcoming_count || '0';
    }
    
    if (favoriteDesks) {
      favoriteDesks.textContent = data.favorite_desks || '0';
    }
    
    if (efficiency) {
      efficiency.textContent = data.efficiency || '95%';
    }

    // Update hero stats
    this.updateHeroStats(data);
  }

  updateHeroStats(data) {
    const todayReservations = document.getElementById('todayReservations');
    const weekReservations = document.getElementById('weekReservations');
    const monthReservations = document.getElementById('monthReservations');

    if (todayReservations) {
      todayReservations.textContent = data.today_count || '0';
    }
    
    if (weekReservations) {
      weekReservations.textContent = data.week_count || '0';
    }
    
    if (monthReservations) {
      monthReservations.textContent = data.month_count || '0';
    }
  }

  // Removed renderReservationsTable - reservations are now shown in calendar

  // Removed renderReservationRow - reservations are now shown in calendar

  updateSummary(data) {
    const nextReservation = document.getElementById('sumNext');
    const lastReservation = document.getElementById('sumLast');
    const upcomingCount = document.getElementById('sumCount');
    const icsLink = document.getElementById('sumIcs');
    const nextMeta = document.getElementById('sumNextMeta');
    const lastMeta = document.getElementById('sumLastMeta');

    if (nextReservation) {
      if (data.next_reservation) {
        nextReservation.textContent = data.next_reservation;
        if (nextMeta) {
          const upcomingText = window.t ? window.t('Upcoming reservation') : 'Upcoming reservation';
          nextMeta.textContent = upcomingText;
        }
      } else {
        nextReservation.textContent = '—';
        if (nextMeta) {
          const noUpcomingText = window.t ? window.t('No upcoming reservations') : 'No upcoming reservations';
          nextMeta.textContent = noUpcomingText;
        }
      }
    }

    if (lastReservation) {
      if (data.last_reservation) {
        lastReservation.textContent = data.last_reservation;
        if (lastMeta) {
          const latestText = window.t ? window.t('Latest reservation') : 'Latest reservation';
          lastMeta.textContent = latestText;
        }
      } else {
        lastReservation.textContent = '—';
        if (lastMeta) {
          const noPastText = window.t ? window.t('No past reservations') : 'No past reservations';
          lastMeta.textContent = noPastText;
        }
      }
    }

    if (upcomingCount) {
      upcomingCount.textContent = data.upcoming_count || '0';
    }

    if (icsLink && data.next_reservation_id) {
      icsLink.href = `/reservations/reservation/${data.next_reservation_id}/ics/`;
      icsLink.style.display = 'inline-flex';
    } else if (icsLink) {
      icsLink.style.display = 'none';
    }
  }

  // Removed showReservationsError - reservations are now shown in calendar

  async cancelReservation(reservationId) {
    const confirmMsg = window.t ? window.t('Are you sure you want to cancel this reservation?') : 'Are you sure you want to cancel this reservation?';
    if (!confirm(confirmMsg)) {
      return;
    }

    try {
      const response = await fetch(`/reservation/${reservationId}/cancel/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        }
      });

      const result = await response.json();

      if (response.ok) {
        const successMsg = window.t ? window.t('Reservation cancelled successfully') : 'Reservation cancelled successfully';
        this.showNotification(successMsg, 'success');
        this.refresh();
      } else {
        const errorMsg = window.t ? window.t('Error cancelling reservation') : 'Error cancelling reservation';
        this.showNotification(result.error || errorMsg, 'error');
      }
    } catch (error) {
      console.error('Error cancelling reservation:', error);
      const errorMsg = window.t ? window.t('Error cancelling reservation') : 'Error cancelling reservation';
      this.showNotification(errorMsg, 'error');
    }
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

  getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
  }

  refresh() {
    this.loadSummary();
    // Also refresh calendar if available
    if (window.calendarManager) {
      window.calendarManager.loadReservations();
    }
  }

  bindEvents() {
    // Refresh button if exists
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => this.refresh());
    }

    // Logout button (now in user dropdown)
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const confirmMsg = window.t ? window.t('Are you sure you want to logout?') : 'Are you sure you want to logout?';
        if (confirm(confirmMsg)) {
          window.location.href = '/api/auth/logout';
        }
      });
    }

    // Modern modal events
    this.bindModalEvents();
    
    // View calendar button
    const viewCalendarBtn = document.getElementById('viewCalendarBtn');
    if (viewCalendarBtn) {
      viewCalendarBtn.addEventListener('click', () => {
        const calendarCard = document.querySelector('.calendar-card');
        if (calendarCard) {
          calendarCard.scrollIntoView({ behavior: 'smooth' });
        }
      });
    }
  }

  bindModalEvents() {
    const modal = document.getElementById('qbModal');
    const cancelBtn = document.getElementById('qbCancel');
    const cancelBtn2 = document.getElementById('qbCancelBtn');
    const backdrop = modal?.querySelector('.modal-backdrop');

    if (cancelBtn) {
      cancelBtn.addEventListener('click', () => this.closeModal());
    }

    if (cancelBtn2) {
      cancelBtn2.addEventListener('click', () => this.closeModal());
    }

    if (backdrop) {
      backdrop.addEventListener('click', () => this.closeModal());
    }

    // Close modal on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modal && modal.getAttribute('aria-hidden') === 'false') {
        this.closeModal();
      }
    });
  }

  closeModal() {
    const modal = document.getElementById('qbModal');
    if (modal) {
      modal.setAttribute('aria-hidden', 'true');
    }
  }

  openModal() {
    const modal = document.getElementById('qbModal');
    if (modal) {
      modal.setAttribute('aria-hidden', 'false');
    }
  }
}

// Initialize dashboard manager
const dashboardManager = new DashboardManager();
