import { apiClient } from '$lib/utils/api.js';

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
		return await apiClient.get('/rental-properties/', { params });
	},

	// Get specific rental property
	get: async (id) => {
		return await apiClient.get(`/rental-properties/${id}/`);
	},

	// Create new rental property
	create: async (data) => {
		return await apiClient.post('/rental-properties/', data);
	},

	// Update rental property
	update: async (id, data) => {
		return await apiClient.put(`/rental-properties/${id}/`, data);
	},

	// Partially update rental property
	patch: async (id, data) => {
		return await apiClient.patch(`/rental-properties/${id}/`, data);
	},

	// Delete rental property
	delete: async (id) => {
		return await apiClient.delete(`/rental-properties/${id}/`);
	}
};

// ===========================
// Tenants API
// ===========================

export const tenantsAPI = {
	// Get all tenants with filtering
	getAll: async (params = {}) => {
		return await apiClient.get('/tenants/', { params });
	},

	// Get specific tenant
	get: async (id) => {
		return await apiClient.get(`/tenants/${id}/`);
	},

	// Create new tenant
	create: async (data) => {
		return await apiClient.post('/tenants/', data);
	},

	// Update tenant
	update: async (id, data) => {
		return await apiClient.put(`/tenants/${id}/`, data);
	},

	// Partially update tenant
	patch: async (id, data) => {
		return await apiClient.patch(`/tenants/${id}/`, data);
	},

	// Delete tenant
	delete: async (id) => {
		return await apiClient.delete(`/tenants/${id}/`);
	}
};

// ===========================
// Leases API
// ===========================

export const leasesAPI = {
	// Get all leases with filtering
	getAll: async (params = {}) => {
		return await apiClient.get('/leases/', { params });
	},

	// Get specific lease
	get: async (id) => {
		return await apiClient.get(`/leases/${id}/`);
	},

	// Create new lease
	create: async (data) => {
		return await apiClient.post('/leases/', data);
	},

	// Update lease
	update: async (id, data) => {
		return await apiClient.put(`/leases/${id}/`, data);
	},

	// Partially update lease
	patch: async (id, data) => {
		return await apiClient.patch(`/leases/${id}/`, data);
	},

	// Delete lease
	delete: async (id) => {
		return await apiClient.delete(`/leases/${id}/`);
	}
};

// ===========================
// Maintenance API
// ===========================

export const maintenanceAPI = {
	// Categories
	categories: {
		getAll: async (params = {}) => {
			return await apiClient.get('/maintenance/categories/', { params });
		},
		get: async (id) => {
			return await apiClient.get(`/maintenance/categories/${id}/`);
		},
		create: async (data) => {
			return await apiClient.post('/maintenance/categories/', data);
		},
		update: async (id, data) => {
			return await apiClient.put(`/maintenance/categories/${id}/`, data);
		},
		delete: async (id) => {
			return await apiClient.delete(`/maintenance/categories/${id}/`);
		}
	},

	// Requests
	requests: {
		getAll: async (params = {}) => {
			return await apiClient.get('/maintenance/requests/', { params });
		},
		get: async (id) => {
			return await apiClient.get(`/maintenance/requests/${id}/`);
		},
		create: async (data) => {
			return await apiClient.post('/maintenance/requests/', data);
		},
		update: async (id, data) => {
			return await apiClient.put(`/maintenance/requests/${id}/`, data);
		},
		patch: async (id, data) => {
			return await apiClient.patch(`/maintenance/requests/${id}/`, data);
		},
		delete: async (id) => {
			return await apiClient.delete(`/maintenance/requests/${id}/`);
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
			return await apiClient.get('/expenses/categories/', { params });
		},
		get: async (id) => {
			return await apiClient.get(`/expenses/categories/${id}/`);
		},
		create: async (data) => {
			return await apiClient.post('/expenses/categories/', data);
		},
		update: async (id, data) => {
			return await apiClient.put(`/expenses/categories/${id}/`, data);
		},
		delete: async (id) => {
			return await apiClient.delete(`/expenses/categories/${id}/`);
		}
	},

	// Expenses
	expenses: {
		getAll: async (params = {}) => {
			return await apiClient.get('/expenses/', { params });
		},
		get: async (id) => {
			return await apiClient.get(`/expenses/${id}/`);
		},
		create: async (data) => {
			return await apiClient.post('/expenses/', data);
		},
		update: async (id, data) => {
			return await apiClient.put(`/expenses/${id}/`, data);
		},
		patch: async (id, data) => {
			return await apiClient.patch(`/expenses/${id}/`, data);
		},
		delete: async (id) => {
			return await apiClient.delete(`/expenses/${id}/`);
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
		return await apiClient.get(url);
	},

	// Generate report
	generateReport: async (data) => {
		return await apiClient.post('/reports/generate/', data);
	},

	// Get all reports
	getReports: async (params = {}) => {
		return await apiClient.get('/reports/', { params });
	},

	// Get specific report
	getReport: async (id) => {
		return await apiClient.get(`/reports/${id}/`);
	}
};

// ===========================
// Combined Property Management API
// ===========================

export const propertyManagementAPI = {
	rentalProperties: rentalPropertyAPI,
	tenants: tenantsAPI,
	leases: leasesAPI,
	maintenance: maintenanceAPI,
	expenses: expensesAPI,
	analytics: analyticsAPI
};

export default propertyManagementAPI;
