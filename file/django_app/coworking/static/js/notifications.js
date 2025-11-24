// Browser Notifications System
class NotificationManager {
    constructor() {
        this.isSupported = 'Notification' in window;
        this.permission = this.isSupported ? Notification.permission : 'denied';
        this.serviceWorker = null;
        this.publicKey = null;
        this.init();
    }

    async init() {
        if (!this.isSupported) {
            console.log('Notifications not supported');
            return;
        }

        await this.loadPublicKey();

        // Register service worker
        if ('serviceWorker' in navigator) {
            try {
                this.serviceWorker = await navigator.serviceWorker.register('/static/js/sw.js');
                console.log('Service Worker registered');
            } catch (error) {
                console.error('Service Worker registration failed:', error);
            }
        }
    }

    async loadPublicKey() {
        try {
            const response = await fetch('/reservations/api/notifications/public-key/');
            if (!response.ok) {
                console.warn('Unable to load web push public key');
                return;
            }
            const data = await response.json();
            if (data.enabled && data.publicKey) {
                this.publicKey = data.publicKey;
            } else {
                console.warn('Web push disabled on server');
            }
        } catch (error) {
            console.error('Failed to fetch web push public key:', error);
        }
    }

    async requestPermission() {
        if (!this.isSupported) {
            return false;
        }

        if (this.permission === 'granted') {
            return true;
        }

        if (this.permission === 'denied') {
            return false;
        }

        this.permission = await Notification.requestPermission();
        return this.permission === 'granted';
    }

    async subscribe(email, subscribeUrl) {
        if (!this.serviceWorker) {
            console.error('Service Worker not available');
            return false;
        }

        try {
            const registration = await navigator.serviceWorker.ready;
            if (!this.publicKey) {
                await this.loadPublicKey();
            }

            if (!this.publicKey) {
                throw new Error('Brak klucza VAPID po stronie serwera.');
            }

            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array(this.publicKey)
            });

            // Send subscription to server
            const response = await fetch(subscribeUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    email: email,
                    subscription: subscription
                })
            });

            const result = await response.json().catch(() => ({}));
            if (!response.ok) {
                throw new Error(result.error || 'Nie udało się zapisać subskrypcji.');
            }

            return Boolean(result.success);
        } catch (error) {
            console.error('Subscription failed:', error);
            throw error;
        }
    }

    showNotification(title, options = {}) {
        if (!this.isSupported || this.permission !== 'granted') {
            return;
        }

        const notification = new Notification(title, {
            icon: '/static/favicon.ico',
            badge: '/static/favicon.ico',
            ...options
        });

        notification.onclick = () => {
            window.focus();
            notification.close();
        };

        return notification;
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    async sendTestNotification(email, testUrl) {
        const response = await fetch(testUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            credentials: 'same-origin',
            body: JSON.stringify({ email })
        });

        const result = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(result.error || 'Nie udało się wysłać testowego powiadomienia.');
        }
        return Boolean(result.success);
    }
}

// Global notification manager
window.notificationManager = new NotificationManager();

// Notification UI
function setupNotificationUI() {
    const notificationButton = document.getElementById('notification-button');
    if (!notificationButton) return;

    notificationButton.addEventListener('click', async () => {
        // Try to get email from hidden input first
        let email = document.getElementById('user-email')?.value;
        
        // If no email, ask user
        if (!email) {
            email = prompt('Wprowadź swój email:');
            if (!email) return;
        }

        console.log('Requesting notification permission for:', email);

        try {
            const granted = await window.notificationManager.requestPermission();
            if (!granted) {
                alert('Powiadomienia zostały zablokowane. Włącz je w ustawieniach przeglądarki.');
                return;
            }

            console.log('Permission granted, subscribing...');
            const subscribeUrl = notificationButton.dataset.subscribeUrl || '/reservations/api/notifications/subscribe/';
            await window.notificationManager.subscribe(email, subscribeUrl);

            alert('Powiadomienia zostały włączone!');
            notificationButton.textContent = '✓ Powiadomienia włączone';
            notificationButton.disabled = true;
        } catch (error) {
            alert(error.message || 'Błąd włączania powiadomień. Spróbuj ponownie.');
        }
    });
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', setupNotificationUI);

document.addEventListener('DOMContentLoaded', () => {
    const testButton = document.getElementById('test-button');
    if (!testButton) {
        return;
    }

    testButton.addEventListener('click', async () => {
        const email = document.getElementById('user-email')?.value;
        if (!email) {
            alert('Najpierw podaj email i zapisz ustawienia.');
            return;
        }

        try {
            const testUrl = testButton.dataset.testUrl || '/reservations/api/notifications/test/';
            await window.notificationManager.sendTestNotification(email, testUrl);
            alert('Testowe powiadomienie zostało wysłane!');
        } catch (error) {
            alert(error.message || 'Nie udało się wysłać testowego powiadomienia.');
        }
    });
});
