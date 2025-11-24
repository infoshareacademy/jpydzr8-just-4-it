// Notification Manager
class NotificationManager {
  constructor() {
    this.notifications = [];
    this.unreadCount = 0;
    this.reminderShown = new Set(); // Track shown reminders
    this.init();
  }

  init() {
    this.bindEvents();
    this.loadNotifications();
    this.startPolling();
  }

  bindEvents() {
    const notificationBell = document.getElementById('notificationBell');
    const notificationDropdown = document.getElementById('notificationDropdown');
    const markAllReadBtn = document.getElementById('markAllRead');
    const userMenu = document.getElementById('userMenu');
    const userDropdown = document.getElementById('userDropdown');

    if (notificationBell) {
      notificationBell.addEventListener('click', (e) => {
        e.stopPropagation();
        this.toggleNotificationDropdown();
      });
    }

    if (markAllReadBtn) {
      markAllReadBtn.addEventListener('click', () => {
        this.markAllAsRead();
      });
    }

    if (userMenu) {
      userMenu.addEventListener('click', (e) => {
        e.stopPropagation();
        this.toggleUserDropdown();
      });
    }

    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
      if (!notificationBell?.contains(e.target)) {
        this.closeNotificationDropdown();
      }
      if (!userMenu?.contains(e.target)) {
        this.closeUserDropdown();
      }
    });

    // Close dropdowns on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closeNotificationDropdown();
        this.closeUserDropdown();
      }
    });
  }

  async loadNotifications() {
    try {
      const response = await fetch('/api/dashboard/api/notifications/');
      const data = await response.json();
      
      if (response.ok) {
        const previousIds = new Set(this.notifications.map(n => n.id));
        const newNotifications = data.notifications || [];
        const currentIds = new Set(newNotifications.map(n => n.id));
        
        // Find new notifications
        const trulyNew = newNotifications.filter(n => !previousIds.has(n.id) && !n.is_read);
        
        // Update notifications
        this.notifications = newNotifications;
        const previousUnreadCount = this.unreadCount;
        this.unreadCount = data.unread_count || 0;
        
        // Show toast for new unread notifications
        if (trulyNew.length > 0 && previousIds.size > 0) {
          trulyNew.forEach(notif => {
            this.showToastNotification(notif.title, notif.message, notif.type);
          });
        }
        
        // Show badge animation if new unread notifications
        if (this.unreadCount > previousUnreadCount) {
          this.animateBadge();
        }
        
        this.updateNotificationBadge();
        this.renderNotifications();
      }
    } catch (error) {
      console.error('Błąd podczas ładowania powiadomień:', error);
      this.showNotificationError();
    }
  }

  updateNotificationBadge() {
    const badge = document.getElementById('notificationBadge');
    if (badge) {
      badge.textContent = this.unreadCount;
      badge.style.display = this.unreadCount > 0 ? 'block' : 'none';
    }
  }

  renderNotifications() {
    const notificationList = document.getElementById('notificationList');
    if (!notificationList) return;

    if (this.notifications.length === 0) {
      const noNotificationsText = window.t ? window.t('No notifications') : 'No notifications';
      notificationList.innerHTML = `
        <div class="notification-empty">
          <i class="fas fa-bell-slash"></i>
          <p>${noNotificationsText}</p>
        </div>
      `;
      return;
    }

    const notificationsHTML = this.notifications.map(notification => `
      <div class="notification-item ${!notification.is_read ? 'unread' : ''}" 
           data-id="${notification.id}">
        <div class="notification-item-header">
          <h5 class="notification-item-title">${this.escapeHtml(notification.title)}</h5>
          <span class="notification-item-time">${this.formatTime(notification.created_at)}</span>
        </div>
        <p class="notification-item-message">${this.escapeHtml(notification.message)}</p>
      </div>
    `).join('');

    notificationList.innerHTML = notificationsHTML;

    // Add click handlers for individual notifications
    notificationList.querySelectorAll('.notification-item').forEach(item => {
      item.addEventListener('click', () => {
        const notificationId = item.dataset.id;
        this.markAsRead(notificationId);
        item.classList.remove('unread');
      });
    });
  }

  showNotificationError() {
    const notificationList = document.getElementById('notificationList');
    if (notificationList) {
      const errorText = window.t ? window.t('Error loading notifications') : 'Error loading notifications';
      const retryText = window.t ? window.t('Try again') : 'Try again';
      notificationList.innerHTML = `
        <div class="notification-error">
          <i class="fas fa-exclamation-triangle"></i>
          <p>${errorText}</p>
          <button onclick="notificationManager.loadNotifications()" class="retry-btn">
            ${retryText}
          </button>
        </div>
      `;
    }
  }

  async markAsRead(notificationId) {
    try {
      const response = await fetch(`/api/dashboard/api/notifications/${notificationId}/read/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        }
      });

      if (response.ok) {
        this.unreadCount = Math.max(0, this.unreadCount - 1);
        this.updateNotificationBadge();
      }
    } catch (error) {
      console.error('Błąd podczas oznaczania powiadomienia jako przeczytane:', error);
    }
  }

  async markAllAsRead() {
    try {
      const unreadNotifications = this.notifications.filter(n => !n.is_read);
      
      for (const notification of unreadNotifications) {
        await this.markAsRead(notification.id);
      }

      // Update local state
      this.notifications.forEach(notification => {
        notification.is_read = true;
      });
      
      this.unreadCount = 0;
      this.updateNotificationBadge();
      this.renderNotifications();
      
      const allReadMsg = window.t ? window.t('All notifications marked as read') : 'All notifications marked as read';
      this.showNotification(allReadMsg, 'success');
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      const errorMsg = window.t ? window.t('Error loading notifications') : 'Error loading notifications';
      this.showNotification(errorMsg, 'error');
    }
  }

  toggleNotificationDropdown() {
    const dropdown = document.getElementById('notificationDropdown');
    if (dropdown) {
      dropdown.classList.toggle('show');
      if (dropdown.classList.contains('show')) {
        this.loadNotifications(); // Refresh when opening
      }
    }
  }

  closeNotificationDropdown() {
    const dropdown = document.getElementById('notificationDropdown');
    if (dropdown) {
      dropdown.classList.remove('show');
    }
  }

  toggleUserDropdown() {
    const dropdown = document.getElementById('userDropdown');
    if (dropdown) {
      dropdown.classList.toggle('show');
    }
  }

  closeUserDropdown() {
    const dropdown = document.getElementById('userDropdown');
    if (dropdown) {
      dropdown.classList.remove('show');
    }
  }

  startPolling() {
    // Poll for new notifications every 30 seconds
    setInterval(() => {
      this.loadNotifications();
    }, 30000);
    
    // Check for upcoming reservations reminders
    this.startReminderChecker();
    
    // Listen for reservation events
    this.bindReservationEvents();
  }
  
  startReminderChecker() {
    // Check for upcoming reservations every minute
    setInterval(() => {
      this.checkUpcomingReservations();
    }, 60000);
    
    // Check immediately on load
    setTimeout(() => this.checkUpcomingReservations(), 5000);
  }
  
  async checkUpcomingReservations() {
    try {
      const response = await fetch('/api/dashboard/api/reservations/summary/');
      const data = await response.json();
      
      if (response.ok && data.next_reservation_text && data.next_reservation_id) {
        // Parse date - use datetime if available for accurate reminders
        let nextDate;
        if (data.next_reservation_datetime) {
          nextDate = new Date(data.next_reservation_datetime);
        } else {
          nextDate = new Date(data.next_reservation_text);
          // If only date is provided (YYYY-MM-DD), set time to 9:00 AM as default
          if (data.next_reservation_text.match(/^\d{4}-\d{2}-\d{2}$/)) {
            nextDate.setHours(9, 0, 0, 0);
          }
        }
        
        const now = new Date();
        const diff = nextDate - now;
        const minutesUntil = Math.floor(diff / 60000);
        
        // Show reminder 15 minutes before (but not if it's already past)
        if (minutesUntil > 0 && minutesUntil <= 15 && !this.reminderShown.has(data.next_reservation_id)) {
          const currentLang = document.documentElement.lang || 'pl';
          const title = currentLang === 'pl' 
            ? '⏰ Przypomnienie o rezerwacji' 
            : '⏰ Reservation Reminder';
          const seatText = data.next_reservation_seat ? ` dla stanowiska ${data.next_reservation_seat}` : '';
          const message = currentLang === 'pl'
            ? `Twoja rezerwacja${seatText} za ${minutesUntil} minut!`
            : `Your reservation${seatText ? ` for ${data.next_reservation_seat}` : ''} in ${minutesUntil} minutes!`;
          
          this.showToastNotification(title, message, 'reminder');
          this.reminderShown.add(data.next_reservation_id);
          
          // Remove from set after 20 minutes to allow reminder next time
          setTimeout(() => {
            this.reminderShown.delete(data.next_reservation_id);
          }, 20 * 60 * 1000);
        }
      }
    } catch (error) {
      console.error('Błąd podczas sprawdzania przypomnień:', error);
    }
  }
  
  bindReservationEvents() {
    // Listen for reservation creation
    window.addEventListener('reservation:created', (e) => {
      const { reservation_id, seat_id, date } = e.detail || {};
      if (reservation_id) {
        const currentLang = document.documentElement.lang || 'pl';
        const title = currentLang === 'pl' 
          ? '✅ Rezerwacja utworzona' 
          : '✅ Reservation Created';
        const message = currentLang === 'pl'
          ? `Rezerwacja dla stanowiska ${seat_id || ''} na ${date || ''} została utworzona`
          : `Reservation for ${seat_id || ''} on ${date || ''} has been created`;
        this.showToastNotification(title, message, 'success');
      }
    });
    
    // Listen for reservation cancellation
    window.addEventListener('reservation:deleted', (e) => {
      const { reservation_id, seat_id, date } = e.detail || {};
      if (reservation_id) {
        const currentLang = document.documentElement.lang || 'pl';
        const title = currentLang === 'pl' 
          ? '🗑️ Rezerwacja anulowana' 
          : '🗑️ Reservation Cancelled';
        const message = currentLang === 'pl'
          ? `Rezerwacja dla stanowiska ${seat_id || ''} na ${date || ''} została anulowana`
          : `Reservation for ${seat_id || ''} on ${date || ''} has been cancelled`;
        this.showToastNotification(title, message, 'info');
      }
    });
    
    // Listen for waitlist availability
    window.addEventListener('waitlist:available', (e) => {
      const { desk_id, desk_label, date } = e.detail || {};
      if (desk_id) {
        const currentLang = document.documentElement.lang || 'pl';
        const title = currentLang === 'pl' 
          ? '🎉 Stanowisko dostępne!' 
          : '🎉 Desk Available!';
        const message = currentLang === 'pl'
          ? `Stanowisko ${desk_label || ''} jest teraz dostępne na ${date || ''}!`
          : `Desk ${desk_label || ''} is now available on ${date || ''}!`;
        this.showToastNotification(title, message, 'success');
      }
    });
  }

  formatTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const currentLang = document.documentElement.lang || 'pl';
    
    if (diff < 60000) { // Less than 1 minute
      return currentLang === 'en' ? 'Just now' : 'Przed chwilą';
    } else if (diff < 3600000) { // Less than 1 hour
      const minutes = Math.floor(diff / 60000);
      return currentLang === 'en' ? `${minutes} min ago` : `${minutes} min temu`;
    } else if (diff < 86400000) { // Less than 1 day
      const hours = Math.floor(diff / 3600000);
      return currentLang === 'en' ? `${hours} hour${hours !== 1 ? 's' : ''} ago` : `${hours} godz. temu`;
    } else {
      const days = Math.floor(diff / 86400000);
      return currentLang === 'en' ? `${days} day${days !== 1 ? 's' : ''} ago` : `${days} dni temu`;
    }
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
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
      info: 'info-circle',
      reminder: 'clock',
      waitlist: 'bell'
    };
    return icons[type] || 'info-circle';
  }
  
  showToastNotification(title, message, type = 'info') {
    // Remove existing toasts
    const existing = document.querySelectorAll('.toast-notification');
    existing.forEach(t => t.remove());

    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
      <div class="toast-content">
        <div class="toast-icon">
          <i class="fas fa-${this.getNotificationIcon(type)}"></i>
        </div>
        <div class="toast-text">
          <div class="toast-title">${this.escapeHtml(title)}</div>
          <div class="toast-message">${this.escapeHtml(message)}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.parentElement.remove()">
          <i class="fas fa-times"></i>
        </button>
      </div>
    `;

    document.body.appendChild(toast);

    // Animate in
    setTimeout(() => toast.classList.add('show'), 10);

    // Auto remove after 6 seconds
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => {
        if (toast.parentElement) {
          toast.remove();
        }
      }, 300);
    }, 6000);
    
    // Update badge if it's a new notification
    if (type !== 'reminder') {
      this.unreadCount++;
      this.updateNotificationBadge();
      this.animateBadge();
    }
  }
  
  animateBadge() {
    const badge = document.getElementById('notificationBadge');
    if (badge) {
      badge.classList.add('animate-badge');
      setTimeout(() => {
        badge.classList.remove('animate-badge');
      }, 1000);
    }
  }

  // Method to add new notification (for testing or real-time updates)
  addNotification(notification) {
    this.notifications.unshift(notification);
    if (!notification.is_read) {
      this.unreadCount++;
    }
    this.updateNotificationBadge();
    this.renderNotifications();
  }
}

// Initialize notification manager
const notificationManager = new NotificationManager();

