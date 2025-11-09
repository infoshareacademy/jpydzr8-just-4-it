// Browser Notifications System
class NotificationManager {
    constructor() {
        this.isSupported = 'Notification' in window;
        this.permission = this.isSupported ? Notification.permission : 'denied';
        this.serviceWorker = null;
        this.init();
    }

    async init() {
        if (!this.isSupported) {
            console.log('Notifications not supported');
            return;
        }

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

    async subscribe(email) {
        if (!this.serviceWorker) {
            console.error('Service Worker not available');
            return false;
        }

        try {
            const registration = await navigator.serviceWorker.ready;
            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array('BEl62iUYgUivxIkv69yViEuiBIa40HI0Y0y4gV1vpVZ0X3lG5a2HFZ02kdmzVER3K7m5ZgDF0Z4HDKkiM5icnA')
            });

            // Send subscription to server
            const response = await fetch('/api/notifications/subscribe/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    email: email,
                    subscription: subscription
                })
            });

            return response.ok;
        } catch (error) {
            console.error('Subscription failed:', error);
            return false;
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

        const granted = await window.notificationManager.requestPermission();
        if (!granted) {
            alert('Powiadomienia zostały zablokowane. Włącz je w ustawieniach przeglądarki.');
            return;
        }

        console.log('Permission granted, subscribing...');
        const subscribed = await window.notificationManager.subscribe(email);
        if (subscribed) {
            alert('Powiadomienia zostały włączone!');
            notificationButton.textContent = '✓ Powiadomienia włączone';
            notificationButton.disabled = true;
        } else {
            alert('Błąd włączania powiadomień. Spróbuj ponownie.');
        }
    });
}

// Test notification
function testNotification() {
    if (window.notificationManager.permission === 'granted') {
        window.notificationManager.showNotification('Test powiadomienia', {
            body: 'To jest test powiadomienia z systemu rezerwacji',
            tag: 'test'
        });
    } else {
        alert('Najpierw włącz powiadomienia!');
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', setupNotificationUI);
