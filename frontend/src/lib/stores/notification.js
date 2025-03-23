// src/lib/stores/notification.js
import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';

// Create writable stores for notifications
const notificationsStore = writable([]);
const connectionStatusStore = writable('disconnected');
export const unreadCount = writable(0);

// The base notification service
const notificationService = {
	subscribe: notificationsStore.subscribe,
	connectionStatus: connectionStatusStore,
	unreadCount,

	// WebSocket connection
	socket: null,
	
	// Initialize the notification system (safe to call)
	init() {
		// Only initialize in browser
		if (!browser) return;
		
		// Import auth stores here to avoid circular dependency
		const { isAuthenticated, authStore } = require('./auth');
		
		// Connect if authenticated
		if (get(isAuthenticated)) {
			this.connect();
		}
		
		// Set up subscription to auth changes
		// Store the unsubscribe function to clean up later
		this._unsubscribeAuth = isAuthenticated.subscribe(value => {
			if (value) {
				// User is now authenticated, connect to notifications
				this.connect();
			} else {
				// User logged out, disconnect
				this.disconnect();
				// Clear notifications
				notificationsStore.set([]);
				unreadCount.set(0);
			}
		});
	},
	
	// Clean up subscriptions
	cleanup() {
		if (this._unsubscribeAuth) {
			this._unsubscribeAuth();
		}
	},

	// Connect to notification service
	connect() {
		// Only connect if in browser
		if (!browser) return;
		
		try {
			// Import auth store here to avoid circular dependency on init
			const { authStore } = require('./auth');
			
			// Close existing connection if any
			if (this.socket) {
				this.disconnect();
			}
			
			const authState = authStore.getState();
			if (!authState.isAuthenticated || !authState.token) {
				console.warn('Cannot connect to notification service: not authenticated');
				return;
			}

			// Create a new WebSocket connection
			const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
			const host = import.meta.env.VITE_API_WS_URL || window.location.host;
			const wsUrl = `${protocol}//${host}/ws/notifications/`;

			this.socket = new WebSocket(wsUrl);

			// Set up event handlers
			this.socket.onopen = () => {
				connectionStatusStore.set('connected');
				console.log('Notification WebSocket connected');

				// Send authentication message
				if (authState.token) {
					this.socket.send(
						JSON.stringify({
							type: 'authenticate',
							token: authState.token
						})
					);
				}
			};

			this.socket.onmessage = (event) => {
				try {
					const data = JSON.parse(event.data);

					// Handle different message types
					switch (data.type) {
						case 'notification':
							// Add new notification
							notificationsStore.update((notifications) => [data.notification, ...notifications]);
							// Update unread count
							unreadCount.update((count) => count + 1);
							break;

						case 'notifications_list':
							// Replace notifications with the received list
							notificationsStore.set(data.notifications || []);
							// Update unread count
							unreadCount.set(data.unread_count || 0);
							break;

						case 'notification_read':
							// Mark specific notification as read
							notificationsStore.update((notifications) =>
								notifications.map((n) => (n.id === data.notification_id ? { ...n, read: true } : n))
							);
							// Update unread count
							unreadCount.update((count) => Math.max(0, count - 1));
							break;

						case 'notification_deleted':
							// Remove deleted notification
							notificationsStore.update((notifications) =>
								notifications.filter((n) => n.id !== data.notification_id)
							);
							break;

						case 'all_read':
							// Mark all notifications as read
							notificationsStore.update((notifications) =>
								notifications.map((n) => ({ ...n, read: true }))
							);
							// Reset unread count
							unreadCount.set(0);
							break;

						default:
							console.log('Unknown notification type:', data.type);
					}
				} catch (error) {
					console.error('Error processing notification:', error);
				}
			};

			this.socket.onclose = () => {
				connectionStatusStore.set('disconnected');
				console.log('Notification WebSocket disconnected');

				// Attempt to reconnect after a delay
				if (browser) {
					setTimeout(() => {
						const { isAuthenticated } = require('./auth');
						if (get(isAuthenticated)) {
							this.connect();
						}
					}, 5000);
				}
			};

			this.socket.onerror = (error) => {
				console.error('Notification WebSocket error:', error);
				connectionStatusStore.set('error');
			};
		} catch (error) {
			console.error('Failed to connect to notification service:', error);
			connectionStatusStore.set('error');
		}
	},

	// Disconnect from notification service
	disconnect() {
		if (this.socket) {
			this.socket.close();
			this.socket = null;
		}
		connectionStatusStore.set('disconnected');
	},

	// Send a command to mark a notification as read
	markAsRead(notificationId) {
		if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
			console.warn('Cannot mark notification as read: WebSocket not connected');
			return;
		}

		this.socket.send(
			JSON.stringify({
				type: 'mark_read',
				notification_id: notificationId
			})
		);
	},

	// Send a command to mark all notifications as read
	markAllAsRead() {
		if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
			console.warn('Cannot mark all notifications as read: WebSocket not connected');
			return;
		}

		this.socket.send(
			JSON.stringify({
				type: 'mark_all_read'
			})
		);
	},

	// Request notifications list (useful after reconnecting)
	requestNotifications() {
		if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
			console.warn('Cannot request notifications: WebSocket not connected');
			return;
		}

		this.socket.send(
			JSON.stringify({
				type: 'get_notifications'
			})
		);
	}
};

// Initialize notifications in browser
if (browser) {
	// Delay initialization to avoid circular dependency issues
	// This will run after all modules are loaded
	setTimeout(() => {
		notificationService.init();
	}, 0);
}

export default notificationService;