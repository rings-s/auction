// src/lib/stores/dashboard.js
import { writable, derived } from 'svelte/store';
import { user } from './user';

// Dashboard data stores
export const dashboardStats = writable(null);
export const dashboardActivity = writable([]);
export const dashboardProperties = writable([]);
export const dashboardAuctions = writable([]);
export const dashboardBids = writable([]);
export const dashboardLoading = writable(false);
export const dashboardError = writable(null);

// Dashboard filters
export const dashboardFilters = writable({
	properties: {
		status: '',
		verified: '',
		search: ''
	},
	auctions: {
		status: '',
		active_only: false,
		search: ''
	},
	bids: {
		status: '',
		winning_only: false,
		search: ''
	}
});

// Derived stores for computed values
export const userPriority = derived([user, dashboardStats], ([$user, $stats]) => {
	if ($stats && $stats.user_priority) {
		return $stats.user_priority;
	}

	if ($user) {
		// Calculate priority based on user role
		const roleMap = {
			owner: 3,
			appraiser: 4,
			data_entry: 2,
			user: 1
		};

		let priority = roleMap[$user.role] || 1;
		if ($user.is_superuser) priority = 5;
		else if ($user.is_staff) priority += 1;

		return priority;
	}

	return 1;
});

export const canAccessAdvancedFeatures = derived([user, userPriority], ([$user, $priority]) => {
	return $user && ($user.is_staff || $user.is_superuser || $priority >= 3);
});

export const canAccessSystemDashboard = derived([user], ([$user]) => {
	return $user && ($user.is_staff || $user.is_superuser);
});

// Dashboard summary for mobile view
export const dashboardSummary = derived(dashboardStats, ($stats) => {
	if (!$stats) return null;

	return {
		properties: $stats.total_properties || 0,
		auctions: $stats.total_auctions || 0,
		bids: $stats.total_bids || 0,
		messages: $stats.messages_unread || 0
	};
});

// Recent activity with priority sorting
export const prioritizedActivity = derived(dashboardActivity, ($activity) => {
	if (!Array.isArray($activity)) return [];

	const priorityOrder = { urgent: 4, high: 3, medium: 2, low: 1 };

	return [...$activity].sort((a, b) => {
		const aPriority = priorityOrder[a.priority] || 1;
		const bPriority = priorityOrder[b.priority] || 1;

		if (aPriority !== bPriority) {
			return bPriority - aPriority; // Higher priority first
		}

		// Sort by timestamp if priority is same
		return new Date(b.timestamp) - new Date(a.timestamp);
	});
});

// Helper functions
export function resetDashboardData() {
	dashboardStats.set(null);
	dashboardActivity.set([]);
	dashboardProperties.set([]);
	dashboardAuctions.set([]);
	dashboardBids.set([]);
	dashboardError.set(null);
}

export function setDashboardLoading(loading) {
	dashboardLoading.set(loading);
}

export function setDashboardError(error) {
	dashboardError.set(error);
}
