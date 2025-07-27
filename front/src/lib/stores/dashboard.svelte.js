// Dashboard store using Svelte 5 runes
import { user } from './user.svelte.js';

// Dashboard data state using Svelte 5 runes
let stats = $state(null);
let activity = $state([]);
let properties = $state([]);
let auctions = $state([]);
let bids = $state([]);
let loading = $state(false);
let error = $state(null);

// Dashboard filters state
let filters = $state({
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

// Create store objects that provide subscribe method for $ syntax compatibility
function createDashboardStore(getter, setter) {
	const subscribers = new Set();

	function notify() {
		const currentValue = getter();
		subscribers.forEach((fn) => fn(currentValue));
	}

	return {
		subscribe(fn) {
			subscribers.add(fn);
			fn(getter()); // Call immediately with current value
			return () => subscribers.delete(fn);
		},
		get value() {
			return getter();
		},
		set(newValue) {
			setter(newValue);
			notify();
		}
	};
}

// Export dashboard data stores
export const dashboardStats = createDashboardStore(
	() => stats,
	(newStats) => {
		stats = newStats;
	}
);

export const dashboardActivity = createDashboardStore(
	() => activity,
	(newActivity) => {
		activity = newActivity;
	}
);

export const dashboardProperties = createDashboardStore(
	() => properties,
	(newProperties) => {
		properties = newProperties;
	}
);

export const dashboardAuctions = createDashboardStore(
	() => auctions,
	(newAuctions) => {
		auctions = newAuctions;
	}
);

export const dashboardBids = createDashboardStore(
	() => bids,
	(newBids) => {
		bids = newBids;
	}
);

export const dashboardLoading = createDashboardStore(
	() => loading,
	(newLoading) => {
		loading = newLoading;
	}
);

export const dashboardError = createDashboardStore(
	() => error,
	(newError) => {
		error = newError;
	}
);

export const dashboardFilters = {
	...createDashboardStore(
		() => filters,
		(newFilters) => {
			filters = newFilters;
		}
	),
	update(updater) {
		filters = updater(filters);
		// Notify subscribers manually since we're bypassing the setter
		this.subscribe(() => {})(); // Trigger notification
	}
};

// Derived values using Svelte 5 $derived as variable declarations
const userPriorityValue = $derived(() => {
	const currentUser = user.value;
	const currentStats = stats;

	if (currentStats && currentStats.user_priority) {
		return currentStats.user_priority;
	}

	if (currentUser) {
		// Calculate priority based on user role
		const roleMap = {
			owner: 3,
			appraiser: 4,
			data_entry: 2,
			user: 1
		};

		let priority = roleMap[currentUser.role] || 1;
		if (currentUser.is_superuser) priority = 5;
		else if (currentUser.is_staff) priority += 1;

		return priority;
	}

	return 1;
});

const canAccessAdvancedFeaturesValue = $derived(() => {
	const currentUser = user.value;
	const priority = userPriorityValue;
	return currentUser && (currentUser.is_staff || currentUser.is_superuser || priority >= 3);
});

const canAccessSystemDashboardValue = $derived(() => {
	const currentUser = user.value;
	return currentUser && (currentUser.is_staff || currentUser.is_superuser);
});

// Dashboard summary for mobile view
const dashboardSummaryValue = $derived(() => {
	if (!stats) return null;

	return {
		properties: stats.total_properties || 0,
		auctions: stats.total_auctions || 0,
		bids: stats.total_bids || 0,
		messages: stats.messages_unread || 0
	};
});

// Recent activity with priority sorting
const prioritizedActivityValue = $derived(() => {
	if (!Array.isArray(activity)) return [];

	const priorityOrder = { urgent: 4, high: 3, medium: 2, low: 1 };

	return [...activity].sort((a, b) => {
		const aPriority = priorityOrder[a.priority] || 1;
		const bPriority = priorityOrder[b.priority] || 1;

		if (aPriority !== bPriority) {
			return bPriority - aPriority; // Higher priority first
		}

		// Sort by timestamp if priority is same
		return new Date(b.timestamp) - new Date(a.timestamp);
	});
});

// Export functions that return current derived values
export function getUserPriority() {
	return userPriorityValue;
}

export function getCanAccessAdvancedFeatures() {
	return canAccessAdvancedFeaturesValue;
}

export function getCanAccessSystemDashboard() {
	return canAccessSystemDashboardValue;
}

export function getDashboardSummary() {
	return dashboardSummaryValue;
}

export function getPrioritizedActivity() {
	return prioritizedActivityValue;
}

// Legacy exports for backwards compatibility
export const userPriority = getUserPriority;
export const canAccessAdvancedFeatures = getCanAccessAdvancedFeatures;
export const canAccessSystemDashboard = getCanAccessSystemDashboard;
export const dashboardSummary = getDashboardSummary;
export const prioritizedActivity = getPrioritizedActivity;

// Helper functions
export function resetDashboardData() {
	stats = null;
	activity = [];
	properties = [];
	auctions = [];
	bids = [];
	error = null;
}

export function setDashboardLoading(isLoading) {
	loading = isLoading;
}

export function setDashboardError(newError) {
	error = newError;
}
