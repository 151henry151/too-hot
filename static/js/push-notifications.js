// Push Notifications for Climate Awareness App
class PushNotificationManager {
    constructor() {
        this.isSupported = 'serviceWorker' in navigator && 'PushManager' in window;
        this.subscription = null;
        this.vapidPublicKey = 'BLNVhEWtDO7l_-KXcw6alKLE4ECCLdCWZT0kZi1mhFc469P3c9Sp7uOWP4O8jU6pMHAMI5ahmj-u437zrSt9kjA';
    }

    async initialize() {
        if (!this.isSupported) {
            console.log('Push notifications not supported');
            return false;
        }

        try {
            // Register service worker
            const registration = await navigator.serviceWorker.register('/static/js/sw.js');
            console.log('Service Worker registered:', registration);

            // Check if already subscribed
            this.subscription = await registration.pushManager.getSubscription();
            
            if (this.subscription) {
                console.log('Already subscribed to push notifications');
                this.updateUI(true);
            } else {
                console.log('Not subscribed to push notifications');
                this.updateUI(false);
            }

            return true;
        } catch (error) {
            console.error('Error initializing push notifications:', error);
            return false;
        }
    }

    async subscribe() {
        if (!this.isSupported) {
            alert('Push notifications are not supported in your browser');
            return;
        }

        try {
            const registration = await navigator.serviceWorker.ready;
            
            // Convert VAPID key to Uint8Array
            const vapidKey = this.urlBase64ToUint8Array(this.vapidPublicKey);
            
            // Subscribe to push notifications
            this.subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: vapidKey
            });

            // Send subscription to server
            await this.sendSubscriptionToServer(this.subscription);
            
            console.log('Successfully subscribed to push notifications');
            this.updateUI(true);
            
            return true;
        } catch (error) {
            console.error('Error subscribing to push notifications:', error);
            alert('Failed to subscribe to push notifications');
            return false;
        }
    }

    async unsubscribe() {
        if (!this.subscription) {
            console.log('Not subscribed to push notifications');
            return;
        }

        try {
            await this.subscription.unsubscribe();
            
            // Notify server about unsubscription
            await this.sendUnsubscriptionToServer();
            
            this.subscription = null;
            console.log('Successfully unsubscribed from push notifications');
            this.updateUI(false);
            
            return true;
        } catch (error) {
            console.error('Error unsubscribing from push notifications:', error);
            return false;
        }
    }

    async sendSubscriptionToServer(subscription) {
        try {
            const response = await fetch('/api/push-subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    subscription: subscription.toJSON(),
                    user_agent: navigator.userAgent,
                    timestamp: new Date().toISOString()
                })
            });

            if (!response.ok) {
                throw new Error('Failed to send subscription to server');
            }

            console.log('Subscription sent to server successfully');
        } catch (error) {
            console.error('Error sending subscription to server:', error);
        }
    }

    async sendUnsubscriptionToServer() {
        try {
            const response = await fetch('/api/push-unsubscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error('Failed to send unsubscription to server');
            }

            console.log('Unsubscription sent to server successfully');
        } catch (error) {
            console.error('Error sending unsubscription to server:', error);
        }
    }

    updateUI(isSubscribed) {
        const subscribeBtn = document.getElementById('subscribe-push');
        const unsubscribeBtn = document.getElementById('unsubscribe-push');
        const statusText = document.getElementById('push-status');

        if (subscribeBtn && unsubscribeBtn && statusText) {
            if (isSubscribed) {
                subscribeBtn.style.display = 'none';
                unsubscribeBtn.style.display = 'inline-block';
                statusText.textContent = '✅ Push notifications enabled';
                statusText.className = 'text-green-600 font-medium';
            } else {
                subscribeBtn.style.display = 'inline-block';
                unsubscribeBtn.style.display = 'none';
                statusText.textContent = '🔔 Get climate alerts via push notifications';
                statusText.className = 'text-gray-600';
            }
        }
    }

    // Utility function to convert VAPID key
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

    // Request notification permission
    async requestPermission() {
        if (!this.isSupported) {
            return false;
        }

        const permission = await Notification.requestPermission();
        return permission === 'granted';
    }
}

// Initialize push notifications when page loads
document.addEventListener('DOMContentLoaded', async () => {
    const pushManager = new PushNotificationManager();
    
    // Check if push notifications are supported
    if (!pushManager.isSupported) {
        console.log('Push notifications not supported in this browser');
        return;
    }

    // Initialize
    await pushManager.initialize();

    // Set up event listeners
    const subscribeBtn = document.getElementById('subscribe-push');
    const unsubscribeBtn = document.getElementById('unsubscribe-push');

    if (subscribeBtn) {
        subscribeBtn.addEventListener('click', async () => {
            const permission = await pushManager.requestPermission();
            if (permission) {
                await pushManager.subscribe();
            } else {
                alert('Permission denied for push notifications');
            }
        });
    }

    if (unsubscribeBtn) {
        unsubscribeBtn.addEventListener('click', async () => {
            await pushManager.unsubscribe();
        });
    }
}); 