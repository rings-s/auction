// src/lib/api/core.js
import { API_BASE_URL } from '$lib/constants';
import { refreshToken } from './auth';

const CORE_URL = `${API_BASE_URL}/core`;

// Helper function for API requests with token refresh (matching auction.js pattern)
async function apiRequest(url, options = {}) {
  const token = localStorage.getItem('accessToken');
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  };

  const requestOptions = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
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
    
    // Handle rate limiting
    if (response.status === 429) {
      throw new Error('Too many requests. Please wait a moment before trying again.');
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
 * Extract error message from different response formats (matching auction.js pattern)
 */
function extractErrorMessage(data, status) {
  // Handle string responses
  if (typeof data === 'string') {
    return data || `HTTP Error ${status}`;
  }

  // Handle structured error responses
  if (data && typeof data === 'object') {
    // Check for nested error object with message
    if (data.error && data.error.message) {
      return data.error.message;
    }
    
    // Check for direct error message
    if (data.error && typeof data.error === 'string') {
      return data.error;
    }

    // Check for Django REST framework 'detail' field
    if (data.detail) {
      return data.detail;
    }

    // Check for direct message field
    if (data.message) {
      return data.message;
    }

    // Handle validation errors (field-specific errors)
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

// -------------------------------------------------------------------------
// Financial Management
// -------------------------------------------------------------------------

export const financialAPI = {
  // Financial Transactions
  async getTransactions(params = {}) {
    const searchParams = new URLSearchParams(params);
    return apiRequest(`${CORE_URL}/transactions/?${searchParams}`);
  },

  async createTransaction(transactionData) {
    return apiRequest(`${CORE_URL}/transactions/`, {
      method: 'POST',
      body: JSON.stringify(transactionData)
    });
  },

  async getTransaction(transactionId) {
    return apiRequest(`${CORE_URL}/transactions/${transactionId}/`);
  },

  async updateTransaction(transactionId, updateData) {
    return apiRequest(`${CORE_URL}/transactions/${transactionId}/`, {
      method: 'PATCH',
      body: JSON.stringify(updateData)
    });
  },

  async deleteTransaction(transactionId) {
    return apiRequest(`${CORE_URL}/transactions/${transactionId}/`, {
      method: 'DELETE'
    });
  },

  // Property Expenses
  async getExpenses(params = {}) {
    const searchParams = new URLSearchParams(params);
    return apiRequest(`${CORE_URL}/expenses/?${searchParams}`);
  },

  async createExpense(expenseData) {
    return apiRequest(`${CORE_URL}/expenses/`, {
      method: 'POST',
      body: JSON.stringify(expenseData)
    });
  },

  async getExpense(expenseId) {
    return apiRequest(`${CORE_URL}/expenses/${expenseId}/`);
  },

  async updateExpense(expenseId, updateData) {
    return apiRequest(`${CORE_URL}/expenses/${expenseId}/`, {
      method: 'PATCH',
      body: JSON.stringify(updateData)
    });
  },

  async deleteExpense(expenseId) {
    return apiRequest(`${CORE_URL}/expenses/${expenseId}/`, {
      method: 'DELETE'
    });
  }
};

// -------------------------------------------------------------------------
// Rental Property Management
// -------------------------------------------------------------------------

export const rentalAPI = {
  // Rental Properties
  async getRentalProperties(params = {}) {
    const searchParams = new URLSearchParams(params);
    return apiRequest(`${CORE_URL}/rental-properties/?${searchParams}`);
  },

  async createRentalProperty(propertyData) {
    return apiRequest(`${CORE_URL}/rental-properties/`, {
      method: 'POST',
      body: JSON.stringify(propertyData)
    });
  },

  async getRentalProperty(propertyId) {
    return apiRequest(`${CORE_URL}/rental-properties/${propertyId}/`);
  },

  async updateRentalProperty(propertyId, updateData) {
    return apiRequest(`${CORE_URL}/rental-properties/${propertyId}/`, {
      method: 'PATCH',
      body: JSON.stringify(updateData)
    });
  },

  async deleteRentalProperty(propertyId) {
    return apiRequest(`${CORE_URL}/rental-properties/${propertyId}/`, {
      method: 'DELETE'
    });
  },

  // Leases
  async getLeases(params = {}) {
    const searchParams = new URLSearchParams(params);
    return apiRequest(`${CORE_URL}/leases/?${searchParams}`);
  },

  async createLease(leaseData) {
    return apiRequest(`${CORE_URL}/leases/`, {
      method: 'POST',
      body: JSON.stringify(leaseData)
    });
  },

  async getLease(leaseId) {
    return apiRequest(`${CORE_URL}/leases/${leaseId}/`);
  },

  async updateLease(leaseId, updateData) {
    return apiRequest(`${CORE_URL}/leases/${leaseId}/`, {
      method: 'PATCH',
      body: JSON.stringify(updateData)
    });
  },

  async deleteLease(leaseId) {
    return apiRequest(`${CORE_URL}/leases/${leaseId}/`, {
      method: 'DELETE'
    });
  }
};

// -------------------------------------------------------------------------
// Maintenance Management
// -------------------------------------------------------------------------

export const maintenanceAPI = {
  // Maintenance Requests
  async getMaintenanceRequests(params = {}) {
    const searchParams = new URLSearchParams(params);
    return apiRequest(`${CORE_URL}/maintenance-requests/?${searchParams}`);
  },

  async createMaintenanceRequest(requestData) {
    return apiRequest(`${CORE_URL}/maintenance-requests/`, {
      method: 'POST',
      body: JSON.stringify(requestData)
    });
  },

  async getMaintenanceRequest(requestId) {
    return apiRequest(`${CORE_URL}/maintenance-requests/${requestId}/`);
  },

  async updateMaintenanceRequest(requestId, updateData) {
    return apiRequest(`${CORE_URL}/maintenance-requests/${requestId}/`, {
      method: 'PATCH',
      body: JSON.stringify(updateData)
    });
  },

  async deleteMaintenanceRequest(requestId) {
    return apiRequest(`${CORE_URL}/maintenance-requests/${requestId}/`, {
      method: 'DELETE'
    });
  },

  // Vendors
  async getVendors(params = {}) {
    const searchParams = new URLSearchParams(params);
    return apiRequest(`${CORE_URL}/vendors/?${searchParams}`);
  },

  async createVendor(vendorData) {
    return apiRequest(`${CORE_URL}/vendors/`, {
      method: 'POST',
      body: JSON.stringify(vendorData)
    });
  },

  async getVendor(vendorId) {
    return apiRequest(`${CORE_URL}/vendors/${vendorId}/`);
  },

  async updateVendor(vendorId, updateData) {
    return apiRequest(`${CORE_URL}/vendors/${vendorId}/`, {
      method: 'PATCH',
      body: JSON.stringify(updateData)
    });
  },

  async deleteVendor(vendorId) {
    return apiRequest(`${CORE_URL}/vendors/${vendorId}/`, {
      method: 'DELETE'
    });
  }
};

// -------------------------------------------------------------------------
// Contract Management
// -------------------------------------------------------------------------

export const contractAPI = {
  // Contract Templates
  async getContractTemplates(params = {}) {
    const searchParams = new URLSearchParams(params);
    return apiRequest(`${CORE_URL}/contract-templates/?${searchParams}`);
  },

  async createContractTemplate(templateData) {
    return apiRequest(`${CORE_URL}/contract-templates/`, {
      method: 'POST',
      body: JSON.stringify(templateData)
    });
  },

  async getContractTemplate(templateId) {
    return apiRequest(`${CORE_URL}/contract-templates/${templateId}/`);
  },

  async updateContractTemplate(templateId, updateData) {
    return apiRequest(`${CORE_URL}/contract-templates/${templateId}/`, {
      method: 'PATCH',
      body: JSON.stringify(updateData)
    });
  },

  async deleteContractTemplate(templateId) {
    return apiRequest(`${CORE_URL}/contract-templates/${templateId}/`, {
      method: 'DELETE'
    });
  },

  // Contracts
  async getContracts(params = {}) {
    const searchParams = new URLSearchParams(params);
    return apiRequest(`${CORE_URL}/contracts/?${searchParams}`);
  },

  async createContract(contractData) {
    return apiRequest(`${CORE_URL}/contracts/`, {
      method: 'POST',
      body: JSON.stringify(contractData)
    });
  },

  async getContract(contractId) {
    return apiRequest(`${CORE_URL}/contracts/${contractId}/`);
  },

  async updateContract(contractId, updateData) {
    return apiRequest(`${CORE_URL}/contracts/${contractId}/`, {
      method: 'PATCH',
      body: JSON.stringify(updateData)
    });
  },

  async deleteContract(contractId) {
    return apiRequest(`${CORE_URL}/contracts/${contractId}/`, {
      method: 'DELETE'
    });
  }
};

// -------------------------------------------------------------------------
// Analytics & Dashboard
// -------------------------------------------------------------------------

export const analyticsAPI = {
  // Property Analytics
  async getPropertyAnalytics(propertyId = null) {
    const url = propertyId 
      ? `${CORE_URL}/analytics/${propertyId}/`
      : `${CORE_URL}/analytics/`;
    return apiRequest(url);
  },

  // Dashboard Data
  async getDashboardData() {
    return apiRequest(`${CORE_URL}/dashboard/`);
  },

  // Financial Summary
  async getFinancialSummary(params = {}) {
    const searchParams = new URLSearchParams(params);
    // Use dashboard endpoint which should aggregate financial data
    return apiRequest(`${CORE_URL}/dashboard/?type=financial&${searchParams}`);
  },

  // Maintenance Stats
  async getMaintenanceStats(params = {}) {
    const searchParams = new URLSearchParams(params);
    // Get maintenance stats from dashboard or maintenance endpoint
    return apiRequest(`${CORE_URL}/dashboard/?type=maintenance&${searchParams}`);
  },

  // Lease Stats
  async getLeaseStats(params = {}) {
    const searchParams = new URLSearchParams(params);
    // Get lease stats from dashboard or lease endpoint
    return apiRequest(`${CORE_URL}/dashboard/?type=leases&${searchParams}`);
  },

  // Vendor Stats
  async getVendorStats(params = {}) {
    const searchParams = new URLSearchParams(params);
    // Get vendor stats from dashboard or vendor endpoint
    return apiRequest(`${CORE_URL}/dashboard/?type=vendors&${searchParams}`);
  },

  // Contract Stats
  async getContractStats(params = {}) {
    const searchParams = new URLSearchParams(params);
    // Get contract stats from dashboard or contract endpoint
    return apiRequest(`${CORE_URL}/dashboard/?type=contracts&${searchParams}`);
  },

  // Property Performance Report
  async getPropertyPerformance(propertyId = null, params = {}) {
    const searchParams = new URLSearchParams(params);
    const url = propertyId 
      ? `${CORE_URL}/analytics/${propertyId}/?${searchParams}`
      : `${CORE_URL}/analytics/?${searchParams}`;
    return apiRequest(url);
  },

  // Financial Reports
  async getFinancialReport(params = {}) {
    const searchParams = new URLSearchParams(params);
    return apiRequest(`${CORE_URL}/dashboard/?report=financial&${searchParams}`);
  },

  // Occupancy Report
  async getOccupancyReport(params = {}) {
    const searchParams = new URLSearchParams(params);
    return apiRequest(`${CORE_URL}/dashboard/?report=occupancy&${searchParams}`);
  },

  // Maintenance Report
  async getMaintenanceReport(params = {}) {
    const searchParams = new URLSearchParams(params);
    return apiRequest(`${CORE_URL}/dashboard/?report=maintenance&${searchParams}`);
  }
};

// -------------------------------------------------------------------------
// Utility Functions
// -------------------------------------------------------------------------

export const coreUtils = {
  // Format currency
  formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount);
  },

  // Format date
  formatDate(date, options = {}) {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      ...options
    }).format(new Date(date));
  },

  // Calculate days between dates
  daysBetween(date1, date2) {
    const oneDay = 24 * 60 * 60 * 1000;
    return Math.round(Math.abs((new Date(date1) - new Date(date2)) / oneDay));
  },

  // Get status color
  getStatusColor(status) {
    const colors = {
      pending: 'yellow',
      completed: 'green',
      failed: 'red',
      overdue: 'red',
      active: 'green',
      expired: 'gray',
      terminated: 'red',
      submitted: 'blue',
      in_progress: 'yellow',
      cancelled: 'gray',
      draft: 'gray',
      signed: 'green'
    };
    return colors[status] || 'gray';
  },

  // Get priority color
  getPriorityColor(priority) {
    const colors = {
      low: 'gray',
      medium: 'yellow',
      high: 'orange',
      emergency: 'red'
    };
    return colors[priority] || 'gray';
  }
};

// Export everything
export default {
  financialAPI,
  rentalAPI,
  maintenanceAPI,
  contractAPI,
  analyticsAPI,
  coreUtils
};