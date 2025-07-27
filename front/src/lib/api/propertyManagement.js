import { api } from '$lib/utils/api.js';

/**
 * Property Management API Service
 * Handles all property management related API calls
 */

// ===========================
// Rental Properties API
// ===========================

export const rentalPropertyAPI = {
	// Get all rental properties with filtering and pagination
	getAll: async (params = {}) => {
		return await api.get('/rental-properties/', { params });
	},

	// Get specific rental property
	get: async (id) => {
		return await api.get(`/rental-properties/${id}/`);
	},

	// Create new rental property
	create: async (data) => {
		return await api.post('/rental-properties/', data);
	},

	// Update rental property
	update: async (id, data) => {
		return await api.put(`/rental-properties/${id}/`, data);
	},

	// Partially update rental property
	patch: async (id, data) => {
		return await api.patch(`/rental-properties/${id}/`, data);
	},

	// Delete rental property
	delete: async (id) => {
		return await api.delete(`/rental-properties/${id}/`);
	}
};

// ===========================
// Tenants API
// ===========================

export const tenantsAPI = {
	// Get all tenants with filtering
	getAll: async (params = {}) => {
		return await api.get('/tenants/', { params });
	},

	// Get specific tenant
	get: async (id) => {
		return await api.get(`/tenants/${id}/`);
	},

	// Create new tenant
	create: async (data) => {
		return await api.post('/tenants/', data);
	},

	// Update tenant
	update: async (id, data) => {
		return await api.put(`/tenants/${id}/`, data);
	},

	// Partially update tenant
	patch: async (id, data) => {
		return await api.patch(`/tenants/${id}/`, data);
	},

	// Delete tenant
	delete: async (id) => {
		return await api.delete(`/tenants/${id}/`);
	}
};

// ===========================
// Leases API
// ===========================

export const leasesAPI = {
	// Get all leases with filtering
	getAll: async (params = {}) => {
		return await api.get('/leases/', { params });
	},

	// Get specific lease
	get: async (id) => {
		return await api.get(`/leases/${id}/`);
	},

	// Create new lease
	create: async (data) => {
		return await api.post('/leases/', data);
	},

	// Update lease
	update: async (id, data) => {
		return await api.put(`/leases/${id}/`, data);
	},

	// Partially update lease
	patch: async (id, data) => {
		return await api.patch(`/leases/${id}/`, data);
	},

	// Delete lease
	delete: async (id) => {
		return await api.delete(`/leases/${id}/`);
	}
};

// ===========================
// Workers API
// ===========================

export const workersAPI = {
	// Get all workers with filtering and pagination
	getAll: async (params = {}) => {
		return await api.get('/workers/', { params });
	},

	// Get specific worker by ID
	getById: async (id) => {
		return await api.get(`/workers/${id}/`);
	},

	// Create new worker
	create: async (data) => {
		return await api.post('/workers/', data);
	},

	// Update worker
	update: async (id, data) => {
		return await api.put(`/workers/${id}/`, data);
	},

	// Partially update worker
	patch: async (id, data) => {
		return await api.patch(`/workers/${id}/`, data);
	},

	// Delete worker
	delete: async (id) => {
		return await api.delete(`/workers/${id}/`);
	},

	// Get worker performance metrics
	getPerformanceMetrics: async (id) => {
		return await api.get(`/workers/${id}/performance/`);
	},

	// Get worker schedule
	getSchedule: async (id, params = {}) => {
		return await api.get(`/workers/${id}/schedule/`, { params });
	},

	// Update worker schedule
	updateSchedule: async (id, data) => {
		return await api.put(`/workers/${id}/schedule/`, data);
	}
};

// ===========================
// Maintenance API
// ===========================

export const maintenanceAPI = {
	// Categories
	categories: {
		getAll: async (params = {}) => {
			return await api.get('/maintenance/categories/', { params });
		},
		get: async (id) => {
			return await api.get(`/maintenance/categories/${id}/`);
		},
		create: async (data) => {
			return await api.post('/maintenance/categories/', data);
		},
		update: async (id, data) => {
			return await api.put(`/maintenance/categories/${id}/`, data);
		},
		delete: async (id) => {
			return await api.delete(`/maintenance/categories/${id}/`);
		}
	},

	// Requests
	requests: {
		getAll: async (params = {}) => {
			return await api.get('/maintenance/requests/', { params });
		},
		get: async (id) => {
			return await api.get(`/maintenance/requests/${id}/`);
		},
		create: async (data) => {
			return await api.post('/maintenance/requests/', data);
		},
		update: async (id, data) => {
			return await api.put(`/maintenance/requests/${id}/`, data);
		},
		patch: async (id, data) => {
			return await api.patch(`/maintenance/requests/${id}/`, data);
		},
		delete: async (id) => {
			return await api.delete(`/maintenance/requests/${id}/`);
		}
	}
};

// ===========================
// Expenses API
// ===========================

export const expensesAPI = {
	// Categories
	categories: {
		getAll: async (params = {}) => {
			return await api.get('/expenses/categories/', { params });
		},
		get: async (id) => {
			return await api.get(`/expenses/categories/${id}/`);
		},
		create: async (data) => {
			return await api.post('/expenses/categories/', data);
		},
		update: async (id, data) => {
			return await api.put(`/expenses/categories/${id}/`, data);
		},
		delete: async (id) => {
			return await api.delete(`/expenses/categories/${id}/`);
		}
	},

	// Expenses
	expenses: {
		getAll: async (params = {}) => {
			return await api.get('/expenses/', { params });
		},
		get: async (id) => {
			return await api.get(`/expenses/${id}/`);
		},
		create: async (data) => {
			return await api.post('/expenses/', data);
		},
		update: async (id, data) => {
			return await api.put(`/expenses/${id}/`, data);
		},
		patch: async (id, data) => {
			return await api.patch(`/expenses/${id}/`, data);
		},
		delete: async (id) => {
			return await api.delete(`/expenses/${id}/`);
		}
	}
};

// ===========================
// Analytics & Reports API
// ===========================

export const analyticsAPI = {
	// Get analytics for all properties or specific property
	getAnalytics: async (propertyId = null) => {
		const url = propertyId ? `/analytics/${propertyId}/` : '/analytics/';
		return await api.get(url);
	},

	// Generate report
	generateReport: async (data) => {
		return await api.post('/reports/generate/', data);
	},

	// Get all reports
	getReports: async (params = {}) => {
		return await api.get('/reports/', { params });
	},

	// Get specific report
	getReport: async (id) => {
		return await api.get(`/reports/${id}/`);
	}
};

// ===========================
// Combined Property Management API
// ===========================

export const propertyManagementAPI = {
	rentalProperties: rentalPropertyAPI,
	tenants: tenantsAPI,
	leases: leasesAPI,
	workers: workersAPI,
	maintenance: maintenanceAPI,
	expenses: expensesAPI,
	analytics: analyticsAPI
};

export default propertyManagementAPI;
