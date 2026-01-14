// Notification Manager
class NotificationManager {
  constructor() {
    this.notifications = [];
    this.unreadCount = 0;
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
        this.notifications = data.notifications || [];
        this.unreadCount = data.unread_count || 0;
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
      info: 'info-circle'
    };
    return icons[type] || 'info-circle';
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

