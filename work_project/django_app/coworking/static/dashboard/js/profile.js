class ProfileManager {
  constructor() {
    this.currentAvatar = '👤';
    this.profileData = null;
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.loadProfile();
  }

  setupEventListeners() {
    // Open profile modal
    const openProfileBtn = document.getElementById('openProfileBtn');
    if (openProfileBtn) {
      openProfileBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.openProfileModal();
      });
    }

    // Open statistics tab
    const openStatisticsBtn = document.getElementById('openStatisticsBtn');
    if (openStatisticsBtn) {
      openStatisticsBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.openProfileModal('statistics');
      });
    }

    // Close modal
    const profileModal = document.getElementById('profileModal');
    const profileModalClose = document.getElementById('profileModalClose');
    const profileCancelBtn = document.getElementById('profileCancelBtn');
    const passwordCancelBtn = document.getElementById('passwordCancelBtn');
    
    if (profileModalClose) {
      profileModalClose.addEventListener('click', () => this.closeProfileModal());
    }
    if (profileCancelBtn) {
      profileCancelBtn.addEventListener('click', () => this.closeProfileModal());
    }
    if (passwordCancelBtn) {
      passwordCancelBtn.addEventListener('click', () => this.closeProfileModal());
    }
    
    if (profileModal) {
      const backdrop = profileModal.querySelector('.modal-backdrop');
      if (backdrop) {
        backdrop.addEventListener('click', () => this.closeProfileModal());
      }
    }

    // Tab switching
    const profileTabs = document.querySelectorAll('.profile-tab');
    profileTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const tabName = tab.getAttribute('data-tab');
        this.switchTab(tabName);
      });
    });

    // Avatar selection
    const avatarOptions = document.querySelectorAll('.avatar-option');
    avatarOptions.forEach(option => {
      option.addEventListener('click', () => {
        const avatar = option.getAttribute('data-avatar');
        this.selectAvatar(avatar);
      });
    });

    // Save profile
    const profileSaveBtn = document.getElementById('profileSaveBtn');
    if (profileSaveBtn) {
      profileSaveBtn.addEventListener('click', () => this.saveProfile());
    }

    // Change password
    const passwordChangeBtn = document.getElementById('passwordChangeBtn');
    if (passwordChangeBtn) {
      passwordChangeBtn.addEventListener('click', () => this.changePassword());
    }
  }

  async loadProfile() {
    try {
      const response = await fetch('/api/dashboard/api/profile/', {
        credentials: 'include',
        headers: {
          'X-CSRFToken': this.getCSRFToken()
        }
      });

      if (!response.ok) throw new Error('Failed to load profile');

      const data = await response.json();
      this.profileData = data;
      this.updateProfileDisplay(data);
    } catch (error) {
      console.error('Error loading profile:', error);
      this.showNotification('Błąd podczas ładowania profilu', 'error');
    }
  }

  updateProfileDisplay(data) {
    // Update header
    const userNameDisplay = document.getElementById('userNameDisplay');
    const userEmailDisplay = document.getElementById('userEmailDisplay');
    const userNameSmall = document.getElementById('userNameSmall');
    const userAvatarDisplay = document.getElementById('userAvatarDisplay');
    const userAvatarSmall = document.getElementById('userAvatarSmall');

    if (userNameDisplay) userNameDisplay.textContent = data.full_name || data.email.split('@')[0];
    if (userEmailDisplay) userEmailDisplay.textContent = data.email;
    if (userNameSmall) userNameSmall.textContent = data.full_name || data.email.split('@')[0];

    // Update avatar
    const avatar = data.avatar || '👤';
    this.currentAvatar = avatar;
    if (userAvatarDisplay) {
      userAvatarDisplay.innerHTML = '';
      userAvatarDisplay.textContent = avatar;
      userAvatarDisplay.style.fontSize = '24px';
    }
    if (userAvatarSmall) {
      userAvatarSmall.innerHTML = '';
      userAvatarSmall.textContent = avatar;
      userAvatarSmall.style.fontSize = '16px';
    }

    // Update profile form
    const profileFullName = document.getElementById('profileFullName');
    const profileEmail = document.getElementById('profileEmail');
    const profileCreatedAt = document.getElementById('profileCreatedAt');
    const profileLastLogin = document.getElementById('profileLastLogin');
    const avatarPreview = document.getElementById('avatarPreview');

    if (profileFullName) profileFullName.value = data.full_name || '';
    if (profileEmail) profileEmail.value = data.email;
    if (profileCreatedAt) {
      if (data.created_at) {
        const date = new Date(data.created_at);
        const currentLang = document.documentElement.lang || 'pl';
        const locale = currentLang === 'en' ? 'en-US' : 'pl-PL';
        profileCreatedAt.value = date.toLocaleDateString(locale, {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });
      }
    }
    if (profileLastLogin) {
      if (data.last_login) {
        const date = new Date(data.last_login);
        const currentLang = document.documentElement.lang || 'pl';
        const locale = currentLang === 'en' ? 'en-US' : 'pl-PL';
        profileLastLogin.value = date.toLocaleDateString(locale, {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      } else {
        const neverText = window.t ? window.t('Never') : (document.documentElement.lang === 'en' ? 'Never' : 'Nigdy');
        profileLastLogin.value = neverText;
      }
    }
    if (avatarPreview) {
      avatarPreview.innerHTML = '';
      avatarPreview.textContent = avatar;
      avatarPreview.style.fontSize = '48px';
    }
  }

  openProfileModal(defaultTab = 'profile') {
    const profileModal = document.getElementById('profileModal');
    if (profileModal) {
      profileModal.setAttribute('aria-hidden', 'false');
      this.switchTab(defaultTab);
      this.loadStatistics();
    }
  }

  closeProfileModal() {
    const profileModal = document.getElementById('profileModal');
    if (profileModal) {
      profileModal.setAttribute('aria-hidden', 'true');
    }
  }

  switchTab(tabName) {
    // Update tab buttons
    const tabs = document.querySelectorAll('.profile-tab');
    tabs.forEach(tab => {
      if (tab.getAttribute('data-tab') === tabName) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });

    // Update tab content
    const tabContents = document.querySelectorAll('.profile-tab-content');
    tabContents.forEach(content => {
      if (content.id === `tab-${tabName}`) {
        content.classList.add('active');
      } else {
        content.classList.remove('active');
      }
    });

    // Load statistics if switching to statistics tab
    if (tabName === 'statistics') {
      this.loadStatistics();
    }
  }

  selectAvatar(avatar) {
    this.currentAvatar = avatar;
    const avatarPreview = document.getElementById('avatarPreview');
    if (avatarPreview) {
      avatarPreview.innerHTML = '';
      avatarPreview.textContent = avatar;
      avatarPreview.style.fontSize = '48px';
    }

    // Update selected state
    const avatarOptions = document.querySelectorAll('.avatar-option');
    avatarOptions.forEach(option => {
      if (option.getAttribute('data-avatar') === avatar) {
        option.classList.add('selected');
      } else {
        option.classList.remove('selected');
      }
    });
  }

  async saveProfile() {
    try {
      const profileFullName = document.getElementById('profileFullName');
      const fullName = profileFullName ? profileFullName.value : '';

      const response = await fetch('/api/dashboard/api/profile/update/', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify({
          full_name: fullName,
          avatar: this.currentAvatar
        })
      });

      const data = await response.json();

      if (!response.ok) {
        const errorMsg = data.error || (window.t ? window.t('Error saving profile') : 'Error saving profile');
        throw new Error(errorMsg);
      }

      this.showNotification(window.t('Profile updated successfully'), 'success');
      this.loadProfile();
      this.closeProfileModal();
    } catch (error) {
      console.error('Error saving profile:', error);
      const errorMsg = error.message || window.t('Error saving profile');
      this.showNotification(window.t(errorMsg) || errorMsg, 'error');
    }
  }

  async changePassword() {
    try {
      const currentPassword = document.getElementById('currentPassword');
      const newPassword = document.getElementById('newPassword');
      const confirmPassword = document.getElementById('confirmPassword');

      if (!currentPassword || !newPassword || !confirmPassword) {
        throw new Error(window.t('All password fields are required'));
      }

      if (newPassword.value !== confirmPassword.value) {
        throw new Error(window.t('New passwords do not match'));
      }

      if (newPassword.value.length < 8) {
        throw new Error(window.t('Password must be at least 8 characters'));
      }

      const response = await fetch('/api/dashboard/api/profile/change-password/', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify({
          old_password: currentPassword.value,
          new_password: newPassword.value,
          confirm_password: confirmPassword.value
        })
      });

      const data = await response.json();

      if (!response.ok) {
        const errorMsg = data.error || window.t('Error changing password');
        throw new Error(window.t(errorMsg) || errorMsg);
      }

      this.showNotification(window.t('Password changed successfully'), 'success');
      
      // Clear password fields
      currentPassword.value = '';
      newPassword.value = '';
      confirmPassword.value = '';
      
      this.closeProfileModal();
    } catch (error) {
      console.error('Error changing password:', error);
      const errorMsg = error.message || window.t('Error changing password');
      this.showNotification(window.t(errorMsg) || errorMsg, 'error');
    }
  }

  async loadStatistics() {
    try {
      const response = await fetch('/api/dashboard/api/profile/statistics/', {
        credentials: 'include',
        headers: {
          'X-CSRFToken': this.getCSRFToken()
        }
      });

      if (!response.ok) {
        const errorMsg = window.t ? window.t('Error loading statistics') : 'Error loading statistics';
        throw new Error(errorMsg);
      }

      const data = await response.json();

      // Update statistics display
      const statTotalReservations = document.getElementById('statTotalReservations');
      const statTodayReservations = document.getElementById('statTodayReservations');
      const statWeekReservations = document.getElementById('statWeekReservations');
      const statMonthReservations = document.getElementById('statMonthReservations');

      if (statTotalReservations) statTotalReservations.textContent = data.total_reservations || 0;
      if (statTodayReservations) statTodayReservations.textContent = data.today_reservations || 0;
      if (statWeekReservations) statWeekReservations.textContent = data.week_reservations || 0;
      if (statMonthReservations) statMonthReservations.textContent = data.month_reservations || 0;

      // Update favorite seats
      const favoriteSeatsList = document.getElementById('favoriteSeatsList');
      if (favoriteSeatsList && data.favorite_seats) {
        if (data.favorite_seats.length === 0) {
          favoriteSeatsList.innerHTML = `<p style="color: var(--text-secondary);">${window.t('No favorite seats')}</p>`;
        } else {
          const reservationsText = window.t('reservations');
          favoriteSeatsList.innerHTML = data.favorite_seats.map(seat => `
            <div class="favorite-seat-item">
              <span class="seat-icon">🪑</span>
              <span class="seat-label">${seat.seat_id}</span>
              <span class="seat-count">${seat.count} ${reservationsText}</span>
            </div>
          `).join('');
        }
      }

      // Update account info
      if (this.profileData) {
        const statAccountAge = document.getElementById('statAccountAge');
        const statAccountStatus = document.getElementById('statAccountStatus');

        if (statAccountAge && this.profileData.statistics) {
          const days = this.profileData.statistics.account_age_days || 0;
          if (days === 0) {
            statAccountAge.textContent = window.t('Today');
          } else if (days === 1) {
            statAccountAge.textContent = window.t('1 day');
          } else if (days < 30) {
            statAccountAge.textContent = `${days} ${window.t('days')}`;
          } else if (days < 365) {
            const months = Math.floor(days / 30);
            statAccountAge.textContent = `${months} ${months === 1 ? window.t('1 month') : window.t('months')}`;
          } else {
            const years = Math.floor(days / 365);
            statAccountAge.textContent = `${years} ${years === 1 ? window.t('1 year') : window.t('years')}`;
          }
        }

        if (statAccountStatus) {
          statAccountStatus.textContent = this.profileData.is_active ? window.t('Active') : window.t('Inactive');
          statAccountStatus.style.color = this.profileData.is_active ? 'var(--success)' : 'var(--error)';
        }
      }
    } catch (error) {
      console.error('Error loading statistics:', error);
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

  showNotification(message, type = 'info') {
    // Use Toastify if available, otherwise use alert
    if (typeof Toastify !== 'undefined') {
      Toastify({
        text: message,
        duration: 3000,
        gravity: 'top',
        position: 'right',
        backgroundColor: type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6',
      }).showToast();
    } else {
      alert(message);
    }
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.profileManager = new ProfileManager();
});

