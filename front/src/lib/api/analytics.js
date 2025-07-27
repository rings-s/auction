// src/lib/api/analytics.js
import { API_BASE_URL } from '$lib/constants';
import { refreshToken } from './auth';

const ANALYTICS_URL = `${API_BASE_URL}/analytics`;

/**
 * Enhanced API request handler with authentication and error handling
 */
async function apiRequest(url, options = {}) {
	const token = localStorage.getItem('accessToken');

	const defaultHeaders = {
		'Content-Type': 'application/json',
		...(token ? { Authorization: `Bearer ${token}` } : {})
	};

	const requestOptions = {
		...options,
		headers: {
			...defaultHeaders,
			...options.headers
		}
	};

	try {
		let response = await fetch(url, requestOptions);

		// Handle token refresh for 401 responses
		if (response.status === 401 && token) {
			try {
				const newToken = await refreshToken();
				requestOptions.headers.Authorization = `Bearer ${newToken}`;
				response = await fetch(url, requestOptions);
			} catch (refreshError) {
				throw new Error('Your session has expired. Please log in again.');
			}
		}

		// Parse response data
		let data;
		const contentType = response.headers.get('content-type');

		if (contentType && contentType.includes('application/json')) {
			data = await response.json();
		} else {
			data = await response.text();
		}

		// Handle error responses
		if (!response.ok) {
			const errorMessage = extractErrorMessage(data, response.status);
			throw new Error(errorMessage);
		}

		return data;
	} catch (error) {
		throw error;
	}
}

/**
 * Extract error message from different response formats
 */
function extractErrorMessage(data, status) {
	if (typeof data === 'string') {
		return data || `HTTP Error ${status}`;
	}

	if (data && typeof data === 'object') {
		if (data.error && data.error.message) {
			return data.error.message;
		}

		if (data.error && typeof data.error === 'string') {
			return data.error;
		}

		if (data.detail) {
			return data.detail;
		}

		if (data.message) {
			return data.message;
		}

		// Handle validation errors
		const validationErrors = [];
		for (const [field, messages] of Object.entries(data)) {
			if (field !== 'error' && field !== 'message' && field !== 'detail') {
				if (Array.isArray(messages)) {
					validationErrors.push(`${field}: ${messages.join(', ')}`);
				} else if (typeof messages === 'string') {
					validationErrors.push(`${field}: ${messages}`);
				}
			}
		}

		if (validationErrors.length > 0) {
			return validationErrors.join('; ');
		}
	}

	return `HTTP Error ${status}`;
}

// ===========================
// PROPERTY ANALYTICS
// ===========================

/**
 * Get advanced property analytics with heat maps and charts
 */
export async function getAdvancedPropertyAnalytics(filters = {}) {
	const queryParams = new URLSearchParams();

	Object.entries(filters).forEach(([key, value]) => {
		if (value !== undefined && value !== null && value !== '') {
			queryParams.append(key, value);
		}
	});

	const url = `${ANALYTICS_URL}/advanced/?${queryParams.toString()}`;
	const response = await apiRequest(url, { method: 'GET' });
	return response;
}

/**
 * Get property performance heat map data
 */
export async function getPropertyHeatMap(filters = {}) {
	const analytics = await getAdvancedPropertyAnalytics(filters);
	return {
		heatmap: analytics.property_performance_heatmap || null,
		geoHeatmap: analytics.geographic_roi_heatmap || null,
		metrics: analytics.performance_metrics || {}
	};
}

// ===========================
// WORKER ANALYTICS
// ===========================

/**
 * Get worker analytics and performance data
 */
export async function getWorkerAnalytics(filters = {}) {
	const queryParams = new URLSearchParams();

	Object.entries(filters).forEach(([key, value]) => {
		if (value !== undefined && value !== null && value !== '') {
			queryParams.append(key, value);
		}
	});

	const url = `${ANALYTICS_URL}/workers/?${queryParams.toString()}`;
	const response = await apiRequest(url, { method: 'GET' });
	return response;
}

/**
 * Get worker performance heat map
 */
export async function getWorkerPerformanceHeatMap() {
	const analytics = await getWorkerAnalytics();
	return {
		heatmap: analytics.worker_performance_heatmap || null,
		performanceChart: analytics.performance_bar_chart || null,
		metrics: analytics.worker_metrics || {}
	};
}

// ===========================
// PAYMENT ANALYTICS
// ===========================

/**
 * Get payment analytics and financial reporting
 */
export async function getPaymentAnalytics(filters = {}) {
	const queryParams = new URLSearchParams();

	Object.entries(filters).forEach(([key, value]) => {
		if (value !== undefined && value !== null && value !== '') {
			queryParams.append(key, value);
		}
	});

	const url = `${ANALYTICS_URL}/payments/?${queryParams.toString()}`;
	const response = await apiRequest(url, { method: 'GET' });
	return response;
}

/**
 * Get payment trends and heat map
 */
export async function getPaymentHeatMap(filters = {}) {
	const analytics = await getPaymentAnalytics(filters);
	return {
		typeHeatmap: analytics.payment_types_heatmap || null,
		trendChart: analytics.payment_trend_chart || null,
		statusChart: analytics.payment_status_chart || null,
		metrics: analytics.payment_metrics || {}
	};
}

// ===========================
// COMPREHENSIVE ANALYTICS
// ===========================

/**
 * Get comprehensive dashboard analytics
 */
export async function getComprehensiveAnalytics(filters = {}) {
	try {
		const [propertyAnalytics, workerAnalytics, paymentAnalytics] = await Promise.all([
			getAdvancedPropertyAnalytics(filters),
			getWorkerAnalytics(filters),
			getPaymentAnalytics(filters)
		]);

		return {
			properties: propertyAnalytics,
			workers: workerAnalytics,
			payments: paymentAnalytics,
			summary: {
				totalProperties: propertyAnalytics.summary?.total_properties || 0,
				totalWorkers: workerAnalytics.summary?.total_workers || 0,
				totalPayments: paymentAnalytics.summary?.total_payments || 0,
				totalRevenue: paymentAnalytics.summary?.total_revenue || 0,
				lastUpdated: new Date().toISOString()
			}
		};
	} catch (error) {
		throw error;
	}
}

// ===========================
// CHART DATA UTILITIES
// ===========================

/**
 * Process heat map data for visualization
 */
export function processHeatMapData(rawData) {
	if (!rawData || !rawData.data) {
		return null;
	}

	return {
		data: rawData.data,
		layout: {
			title: rawData.title || 'Heat Map',
			xaxis: { title: rawData.xaxis_title || 'X Axis' },
			yaxis: { title: rawData.yaxis_title || 'Y Axis' },
			...rawData.layout
		},
		config: {
			responsive: true,
			displayModeBar: false,
			...rawData.config
		}
	};
}

/**
 * Process bar chart data for visualization
 */
export function processBarChartData(rawData) {
	if (!rawData || !rawData.data) {
		return null;
	}

	return {
		data: rawData.data,
		layout: {
			title: rawData.title || 'Bar Chart',
			xaxis: { title: rawData.xaxis_title || 'X Axis' },
			yaxis: { title: rawData.yaxis_title || 'Y Axis' },
			showlegend: true,
			...rawData.layout
		},
		config: {
			responsive: true,
			displayModeBar: false,
			...rawData.config
		}
	};
}

/**
 * Process geographic heat map data
 */
export function processGeoHeatMapData(rawData) {
	if (!rawData || !rawData.data) {
		return null;
	}

	return {
		data: rawData.data,
		layout: {
			title: rawData.title || 'Geographic Heat Map',
			mapbox: {
				style: 'open-street-map',
				center: { lat: 24.7136, lon: 46.6753 }, // Riyadh, Saudi Arabia
				zoom: 10
			},
			...rawData.layout
		},
		config: {
			responsive: true,
			displayModeBar: false,
			mapboxAccessToken: null, // Using open-street-map
			...rawData.config
		}
	};
}

// ===========================
// ANALYTICS FILTERS
// ===========================

/**
 * Get available analytics filters
 */
export function getAnalyticsFilters() {
	return {
		dateRanges: [
			{ value: '7d', label: 'Last 7 days' },
			{ value: '30d', label: 'Last 30 days' },
			{ value: '90d', label: 'Last 3 months' },
			{ value: '6m', label: 'Last 6 months' },
			{ value: '1y', label: 'Last year' },
			{ value: 'custom', label: 'Custom range' }
		],
		propertyTypes: [
			{ value: 'all', label: 'All Types' },
			{ value: 'residential', label: 'Residential' },
			{ value: 'commercial', label: 'Commercial' },
			{ value: 'industrial', label: 'Industrial' },
			{ value: 'land', label: 'Land' }
		],
		metrics: [
			{ value: 'roi', label: 'ROI' },
			{ value: 'occupancy', label: 'Occupancy Rate' },
			{ value: 'revenue', label: 'Revenue' },
			{ value: 'maintenance', label: 'Maintenance Costs' },
			{ value: 'performance', label: 'Overall Performance' }
		]
	};
}

/**
 * Build analytics query from filters
 */
export function buildAnalyticsQuery(filters) {
	const query = {};

	// Date range
	if (filters.dateRange && filters.dateRange !== 'all') {
		let endDate = new Date();
		let startDate = new Date();

		switch (filters.dateRange) {
			case '7d':
				startDate.setDate(endDate.getDate() - 7);
				break;
			case '30d':
				startDate.setDate(endDate.getDate() - 30);
				break;
			case '90d':
				startDate.setDate(endDate.getDate() - 90);
				break;
			case '6m':
				startDate.setMonth(endDate.getMonth() - 6);
				break;
			case '1y':
				startDate.setFullYear(endDate.getFullYear() - 1);
				break;
			case 'custom':
				if (filters.startDate) startDate = new Date(filters.startDate);
				if (filters.endDate) endDate = new Date(filters.endDate);
				break;
		}

		query.start_date = startDate.toISOString().split('T')[0];
		query.end_date = endDate.toISOString().split('T')[0];
	}

	// Property type
	if (filters.propertyType && filters.propertyType !== 'all') {
		query.property_type = filters.propertyType;
	}

	// Location
	if (filters.city) {
		query.city = filters.city;
	}

	// Metric focus
	if (filters.metric) {
		query.focus = filters.metric;
	}

	return query;
}

// ===========================
// PERFORMANCE CALCULATIONS
// ===========================

/**
 * Calculate property performance score
 */
export function calculatePropertyPerformance(property) {
	let score = 0;
	let factors = 0;

	// ROI (0-40 points)
	if (property.roi !== undefined) {
		score += Math.min(40, Math.max(0, property.roi * 4));
		factors++;
	}

	// Occupancy rate (0-30 points)
	if (property.occupancy_rate !== undefined) {
		score += Math.min(30, property.occupancy_rate * 0.3);
		factors++;
	}

	// Revenue vs market (0-20 points)
	if (property.revenue && property.market_average_revenue) {
		const revenueRatio = property.revenue / property.market_average_revenue;
		score += Math.min(20, revenueRatio * 20);
		factors++;
	}

	// Maintenance efficiency (0-10 points)
	if (property.maintenance_requests !== undefined) {
		const maintenanceScore = Math.max(0, 10 - property.maintenance_requests * 2);
		score += maintenanceScore;
		factors++;
	}

	return factors > 0 ? Math.round((score / factors) * (100 / 100)) : 0;
}

/**
 * Calculate worker performance score
 */
export function calculateWorkerPerformanceScore(worker) {
	let score = 0;
	let factors = 0;

	// Completion rate (0-30 points)
	if (worker.completion_rate !== undefined) {
		score += worker.completion_rate * 0.3;
		factors++;
	}

	// Rating (0-25 points)
	if (worker.rating !== undefined) {
		score += (worker.rating / 5) * 25;
		factors++;
	}

	// Efficiency (jobs vs capacity) (0-25 points)
	if (worker.total_jobs && worker.max_concurrent_jobs) {
		const efficiency = Math.min(1, worker.total_jobs / (worker.max_concurrent_jobs * 30)); // 30 days
		score += efficiency * 25;
		factors++;
	}

	// Speed (time to completion) (0-20 points)
	if (worker.average_completion_time && worker.category_average_time) {
		const speedRatio = worker.category_average_time / worker.average_completion_time;
		score += Math.min(20, speedRatio * 20);
		factors++;
	}

	return factors > 0 ? Math.round((score / factors) * (100 / 100)) : 0;
}

/**
 * Generate analytics export data
 */
export function generateAnalyticsExport(analyticsData, format = 'json') {
	const exportData = {
		generatedAt: new Date().toISOString(),
		summary: analyticsData.summary || {},
		properties: analyticsData.properties || {},
		workers: analyticsData.workers || {},
		payments: analyticsData.payments || {}
	};

	switch (format) {
		case 'csv':
			return convertToCSV(exportData);
		case 'json':
		default:
			return JSON.stringify(exportData, null, 2);
	}
}

/**
 * Convert analytics data to CSV format
 */
function convertToCSV(data) {
	const csvRows = [];

	// Add headers
	csvRows.push(['Metric', 'Value', 'Category'].join(','));

	// Add summary data
	if (data.summary) {
		Object.entries(data.summary).forEach(([key, value]) => {
			csvRows.push([key, value, 'Summary'].join(','));
		});
	}

	return csvRows.join('\n');
}
