// Service Worker for Climate Awareness App
const CACHE_NAME = 'climate-awareness-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/js/push-notifications.js',
    '/static/img/tshirt.png',
    '/static/img/tshirt_text.png'
];

// Install event - cache resources
self.addEventListener('install', event => {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('Service Worker activating...');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            })
    );
});

// Push event - handle incoming push notifications
self.addEventListener('push', event => {
    console.log('Push event received:', event);
    
    let notificationData = {
        title: 'Climate Alert',
        body: 'New climate update available',
        icon: '/static/img/tshirt.png',
        badge: '/static/img/tshirt.png',
        data: {
            url: '/'
        }
    };

    // Parse push data if available
    if (event.data) {
        try {
            const data = event.data.json();
            notificationData = {
                ...notificationData,
                ...data
            };
        } catch (error) {
            console.log('Could not parse push data:', error);
        }
    }

    const options = {
        body: notificationData.body,
        icon: notificationData.icon,
        badge: notificationData.badge,
        data: notificationData.data,
        actions: [
            {
                action: 'view',
                title: 'View Details',
                icon: '/static/img/tshirt.png'
            },
            {
                action: 'dismiss',
                title: 'Dismiss'
            }
        ],
        requireInteraction: true,
        tag: 'climate-alert'
    };

    event.waitUntil(
        self.registration.showNotification(notificationData.title, options)
    );
});

// Notification click event
self.addEventListener('notificationclick', event => {
    console.log('Notification clicked:', event);
    
    event.notification.close();

    if (event.action === 'view') {
        // Open the app when notification is clicked
        event.waitUntil(
            clients.openWindow(event.notification.data.url)
        );
    } else if (event.action === 'dismiss') {
        // Just close the notification
        event.notification.close();
    } else {
        // Default action - open the app
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Background sync for offline functionality
self.addEventListener('sync', event => {
    console.log('Background sync event:', event);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(
            // Perform background sync tasks
            syncData()
        );
    }
});

async function syncData() {
    try {
        // Sync any pending data when connection is restored
        console.log('Performing background sync...');
        
        // You can add offline data sync logic here
        // For example, syncing temperature readings or user preferences
        
    } catch (error) {
        console.error('Background sync failed:', error);
    }
}

// Handle push subscription changes
self.addEventListener('pushsubscriptionchange', event => {
    console.log('Push subscription changed:', event);
    
    event.waitUntil(
        // Re-subscribe to push notifications
        self.registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: event.oldSubscription.options.applicationServerKey
        }).then(subscription => {
            // Send new subscription to server
            return fetch('/api/push-resubscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    subscription: subscription.toJSON()
                })
            });
        })
    );
}); 