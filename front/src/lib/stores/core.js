// src/lib/stores/core.js
import { writable, derived, get } from 'svelte/store';
import { user } from './user.js';
import { 
  maintenanceAPI, 
  financialAPI, 
  contractAPI, 
  rentalAPI, 
  analyticsAPI 
} from '$lib/api/core.js';

// =============================================================================
// GLOBAL CORE STATE
// =============================================================================

export const coreLoading = writable(false);
export const coreError = writable(null);
export const activePage = writable('dashboard');
export const refreshTrigger = writable(0);

// =============================================================================
// MAINTENANCE MANAGEMENT
// =============================================================================

export const maintenanceRequests = writable([]);
export const vendors = writable([]);
export const maintenanceStats = writable({
  totalRequests: 0,
  pendingRequests: 0,
  inProgressRequests: 0,
  completedRequests: 0,
  emergencyRequests: 0,
  totalCostYTD: 0
});

export const maintenanceFilters = writable({
  status: '',
  priority: '',
  category: '',
  search: '',
  sort: 'newest',
  page: 1
});

export const maintenanceLoading = writable(false);
export const maintenanceError = writable(null);

// Derived store for filtered maintenance requests
export const filteredMaintenanceRequests = derived(
  [maintenanceRequests, maintenanceFilters],
  ([$requests, $filters]) => {
    if (!Array.isArray($requests)) return [];
    
    return $requests.filter(request => {
      const matchesSearch = !$filters.search || 
        request.title?.toLowerCase().includes($filters.search.toLowerCase()) ||
        request.description?.toLowerCase().includes($filters.search.toLowerCase()) ||
        request.property_info?.title?.toLowerCase().includes($filters.search.toLowerCase());
      
      const matchesStatus = !$filters.status || request.status === $filters.status;
      const matchesPriority = !$filters.priority || request.priority === $filters.priority;
      const matchesCategory = !$filters.category || request.category === $filters.category;
      
      return matchesSearch && matchesStatus && matchesPriority && matchesCategory;
    });
  }
);

// =============================================================================
// FINANCIAL MANAGEMENT
// =============================================================================

export const transactions = writable([]);
export const expenses = writable([]);
export const financialStats = writable({
  totalIncome: 0,
  totalExpenses: 0,
  netIncome: 0,
  monthlyIncome: 0,
  monthlyExpenses: 0,
  ytdIncome: 0,
  ytdExpenses: 0
});

export const financialFilters = writable({
  type: '', // income, expense
  category: '',
  property: '',
  dateFrom: '',
  dateTo: '',
  search: '',
  sort: 'newest',
  page: 1
});

export const financialLoading = writable(false);
export const financialError = writable(null);

// Derived store for filtered transactions
export const filteredTransactions = derived(
  [transactions, financialFilters],
  ([$transactions, $filters]) => {
    if (!Array.isArray($transactions)) return [];
    
    return $transactions.filter(transaction => {
      const matchesSearch = !$filters.search || 
        transaction.description?.toLowerCase().includes($filters.search.toLowerCase()) ||
        transaction.category?.toLowerCase().includes($filters.search.toLowerCase());
      
      const matchesType = !$filters.type || transaction.transaction_type === $filters.type;
      const matchesCategory = !$filters.category || transaction.category === $filters.category;
      const matchesProperty = !$filters.property || transaction.property_id === $filters.property;
      
      return matchesSearch && matchesType && matchesCategory && matchesProperty;
    });
  }
);

// =============================================================================
// CONTRACTS MANAGEMENT
// =============================================================================

export const contracts = writable([]);
export const contractTemplates = writable([]);
export const contractStats = writable({
  totalContracts: 0,
  activeContracts: 0,
  draftContracts: 0,
  signedContracts: 0,
  expiredContracts: 0,
  totalTemplates: 0
});

export const contractFilters = writable({
  status: '',
  type: '',
  party: '',
  search: '',
  sort: 'newest',
  page: 1
});

export const contractLoading = writable(false);
export const contractError = writable(null);

// Derived store for filtered contracts
export const filteredContracts = derived(
  [contracts, contractFilters],
  ([$contracts, $filters]) => {
    if (!Array.isArray($contracts)) return [];
    
    return $contracts.filter(contract => {
      const matchesSearch = !$filters.search || 
        contract.title?.toLowerCase().includes($filters.search.toLowerCase()) ||
        contract.description?.toLowerCase().includes($filters.search.toLowerCase()) ||
        contract.parties?.toLowerCase().includes($filters.search.toLowerCase());
      
      const matchesStatus = !$filters.status || contract.status === $filters.status;
      const matchesType = !$filters.type || contract.contract_type === $filters.type;
      
      return matchesSearch && matchesStatus && matchesType;
    });
  }
);

// =============================================================================
// ANALYTICS & REPORTS
// =============================================================================

export const analyticsData = writable({});
export const reports = writable([]);
export const performanceMetrics = writable({});
export const analyticsFilters = writable({
  period: '30d',
  metric: 'overview',
  property: '',
  dateFrom: '',
  dateTo: ''
});

export const analyticsLoading = writable(false);
export const analyticsError = writable(null);

// =============================================================================
// RENTAL MANAGEMENT
// =============================================================================

export const rentalProperties = writable([]);
export const leases = writable([]);
export const tenants = writable([]);
export const rentalStats = writable({
  totalProperties: 0,
  occupiedProperties: 0,
  vacantProperties: 0,
  activeLeases: 0,
  expiringLeases: 0,
  occupancyRate: 0
});

export const rentalFilters = writable({
  status: '',
  occupancy: '',
  search: '',
  sort: 'newest',
  page: 1
});

export const rentalLoading = writable(false);
export const rentalError = writable(null);

// Derived store for filtered rental properties
export const filteredRentalProperties = derived(
  [rentalProperties, rentalFilters],
  ([$properties, $filters]) => {
    if (!Array.isArray($properties)) return [];
    
    return $properties.filter(property => {
      const matchesSearch = !$filters.search || 
        property.title?.toLowerCase().includes($filters.search.toLowerCase()) ||
        property.address?.toLowerCase().includes($filters.search.toLowerCase());
      
      const matchesStatus = !$filters.status || property.status === $filters.status;
      const matchesOccupancy = !$filters.occupancy || property.occupancy_status === $filters.occupancy;
      
      return matchesSearch && matchesStatus && matchesOccupancy;
    });
  }
);

// =============================================================================
// DERIVED STORES FOR CROSS-SECTION DATA
// =============================================================================

// Overall dashboard summary
export const dashboardSummary = derived(
  [maintenanceStats, financialStats, contractStats, rentalStats],
  ([$maintenance, $financial, $contracts, $rental]) => ({
    totalProperties: $rental.totalProperties || 0,
    monthlyIncome: $financial.monthlyIncome || 0,
    occupancyRate: $rental.occupancyRate || 0,
    pendingMaintenance: $maintenance.pendingRequests || 0,
    activeContracts: $contracts.activeContracts || 0,
    netIncome: $financial.netIncome || 0
  })
);

// Recent activity across all modules
export const recentActivity = derived(
  [maintenanceRequests, transactions, contracts, leases],
  ([$maintenance, $transactions, $contracts, $leases]) => {
    const activity = [];
    
    // Add recent maintenance requests
    if (Array.isArray($maintenance)) {
      $maintenance.slice(0, 5).forEach(request => {
        activity.push({
          type: 'maintenance',
          title: request.title,
          date: request.requested_date,
          status: request.status,
          priority: request.priority
        });
      });
    }
    
    // Add recent transactions
    if (Array.isArray($transactions)) {
      $transactions.slice(0, 5).forEach(transaction => {
        activity.push({
          type: 'financial',
          title: transaction.description,
          date: transaction.transaction_date,
          amount: transaction.amount,
          category: transaction.category
        });
      });
    }
    
    // Add recent contracts
    if (Array.isArray($contracts)) {
      $contracts.slice(0, 3).forEach(contract => {
        activity.push({
          type: 'contract',
          title: contract.title,
          date: contract.created_at,
          status: contract.status
        });
      });
    }
    
    // Sort by date and return top 10
    return activity
      .sort((a, b) => new Date(b.date) - new Date(a.date))
      .slice(0, 10);
  }
);

// =============================================================================
// API INTEGRATION FUNCTIONS
// =============================================================================

// Maintenance API Functions
export const maintenanceActions = {
  async loadAll() {
    // GUARD: Only run on core pages
    if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/core')) {
      return;
    }
    
    maintenanceLoading.set(true);
    maintenanceError.set(null);
    
    try {
      const filters = get(maintenanceFilters);
      const [requestsResponse, vendorsResponse] = await Promise.all([
        maintenanceAPI.getMaintenanceRequests(filters),
        maintenanceAPI.getVendors(filters)
      ]);
      
      const requestList = requestsResponse.results || requestsResponse;
      const vendorList = vendorsResponse.results || vendorsResponse;
      
      maintenanceRequests.set(requestList);
      vendors.set(vendorList);
      
      // Calculate stats from real data
      const stats = {
        totalRequests: requestList.length,
        pendingRequests: requestList.filter(r => r.status === 'submitted').length,
        inProgressRequests: requestList.filter(r => r.status === 'in_progress').length,
        completedRequests: requestList.filter(r => r.status === 'completed').length,
        emergencyRequests: requestList.filter(r => r.priority === 'emergency').length,
        totalCostYTD: requestList.reduce((sum, r) => sum + (parseFloat(r.actual_cost) || parseFloat(r.estimated_cost) || 0), 0)
      };
      maintenanceStats.set(stats);
      
    } catch (error) {
      // Silently handle permission errors - don't spam console
      if (error.message?.includes('403') || error.message?.includes('Forbidden')) {
        maintenanceError.set(null);
      } else if (error.message?.includes('401') || error.message?.includes('Unauthorized')) {
        maintenanceError.set('Authentication required. Please log in again.');
      } else if (error.message?.includes('verification')) {
        maintenanceError.set('Email verification required to view maintenance data.');
      } else {
        console.error('Maintenance loading error:', error);
        maintenanceError.set(error.message || 'Failed to load maintenance data');
      }
    } finally {
      maintenanceLoading.set(false);
    }
  },
  
  async createRequest(requestData) {
    try {
      const response = await maintenanceAPI.createMaintenanceRequest(requestData);
      
      // Add to store
      maintenanceRequests.update(requests => [response, ...requests]);
      
      // Refresh stats
      await this.loadAll();
      
      return response;
    } catch (error) {
      maintenanceError.set(error.message || 'Failed to create maintenance request');
      throw error;
    }
  },
  
  async updateRequest(id, updateData) {
    try {
      const response = await maintenanceAPI.updateMaintenanceRequest(id, updateData);
      
      // Update in store
      maintenanceRequests.update(requests => 
        requests.map(r => r.id === id ? { ...r, ...response } : r)
      );
      
      return response;
    } catch (error) {
      maintenanceError.set(error.message || 'Failed to update maintenance request');
      throw error;
    }
  }
};

// Financial API Functions
export const financialActions = {
  async loadAll() {
    // GUARD: Only run on core pages
    if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/core')) {
      return;
    }
    
    financialLoading.set(true);
    financialError.set(null);
    
    try {
      const filters = get(financialFilters);
      const [transactionsResponse, expensesResponse] = await Promise.all([
        financialAPI.getTransactions(filters),
        financialAPI.getExpenses(filters)
      ]);
      
      const transactionList = transactionsResponse.results || transactionsResponse;
      const expenseList = expensesResponse.results || expensesResponse;
      
      transactions.set(transactionList);
      expenses.set(expenseList);
      
      // Calculate financial stats
      const totalIncome = transactionList
        .filter(t => t.transaction_type === 'income')
        .reduce((sum, t) => sum + parseFloat(t.amount || 0), 0);
      
      const totalExpenses = expenseList
        .reduce((sum, e) => sum + parseFloat(e.amount || 0), 0);
      
      const stats = {
        totalIncome,
        totalExpenses,
        netIncome: totalIncome - totalExpenses,
        monthlyIncome: totalIncome / 12, // Simplified calculation
        monthlyExpenses: totalExpenses / 12,
        ytdIncome: totalIncome,
        ytdExpenses: totalExpenses
      };
      financialStats.set(stats);
      
    } catch (error) {
      // Silently handle permission errors - don't spam console
      if (error.message?.includes('403') || error.message?.includes('Forbidden')) {
        financialError.set(null);
      } else if (error.message?.includes('401') || error.message?.includes('Unauthorized')) {
        financialError.set('Authentication required. Please log in again.');
      } else if (error.message?.includes('verification')) {
        financialError.set('Email verification required to view financial data.');
      } else {
        console.error('Financial loading error:', error);
        financialError.set(error.message || 'Failed to load financial data');
      }
    } finally {
      financialLoading.set(false);
    }
  },
  
  async createTransaction(transactionData) {
    try {
      const response = await financialAPI.createTransaction(transactionData);
      
      // Add to store
      transactions.update(txns => [response, ...txns]);
      
      // Refresh stats
      await this.loadAll();
      
      return response;
    } catch (error) {
      financialError.set(error.message || 'Failed to create transaction');
      throw error;
    }
  }
};

// Contract API Functions
export const contractActions = {
  async loadAll() {
    // GUARD: Only run on core pages
    if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/core')) {
      return;
    }
    
    contractLoading.set(true);
    contractError.set(null);
    
    try {
      const filters = get(contractFilters);
      const [contractsResponse, templatesResponse] = await Promise.all([
        contractAPI.getContracts(filters),
        contractAPI.getContractTemplates(filters)
      ]);
      
      const contractList = contractsResponse.results || contractsResponse;
      const templateList = templatesResponse.results || templatesResponse;
      
      contracts.set(contractList);
      contractTemplates.set(templateList);
      
      // Calculate stats from real data
      const stats = {
        totalContracts: contractList.length,
        activeContracts: contractList.filter(c => c.status === 'active').length,
        draftContracts: contractList.filter(c => c.status === 'draft').length,
        signedContracts: contractList.filter(c => c.status === 'signed').length,
        expiredContracts: contractList.filter(c => c.status === 'expired').length,
        totalTemplates: templateList.length
      };
      contractStats.set(stats);
      
    } catch (error) {
      // Silently handle permission errors - don't spam console
      if (error.message?.includes('403') || error.message?.includes('Forbidden')) {
        contractError.set(null);
      } else if (error.message?.includes('401') || error.message?.includes('Unauthorized')) {
        contractError.set('Authentication required. Please log in again.');
      } else if (error.message?.includes('verification')) {
        contractError.set('Email verification required to view contract data.');
      } else {
        console.error('Contract loading error:', error);
        contractError.set(error.message || 'Failed to load contract data');
      }
    } finally {
      contractLoading.set(false);
    }
  },
  
  async createContract(contractData) {
    try {
      const response = await contractAPI.createContract(contractData);
      
      // Add to store
      contracts.update(contracts => [response, ...contracts]);
      
      // Refresh stats
      await this.loadAll();
      
      return response;
    } catch (error) {
      contractError.set(error.message || 'Failed to create contract');
      throw error;
    }
  }
};

// Analytics API Functions
export const analyticsActions = {
  async loadDashboard() {
    // GUARD: Only run on core pages
    if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/core')) {
      return;
    }
    
    analyticsLoading.set(true);
    analyticsError.set(null);
    
    try {
      const filters = get(analyticsFilters);
      const dashboardData = await analyticsAPI.getDashboardData();
      
      analyticsData.set({
        dashboard: dashboardData
      });
      
      // Extract metrics from real dashboard data
      performanceMetrics.set({
        totalRevenue: dashboardData.total_rental_income_ytd || 0,
        totalExpenses: dashboardData.total_expenses_ytd || 0,
        netIncome: dashboardData.net_profit_ytd || 0,
        occupancyRate: dashboardData.occupancy_rate || 0,
        maintenanceRequests: dashboardData.pending_maintenance || 0,
        activeLeases: dashboardData.total_properties || 0
      });
      
    } catch (error) {
      analyticsError.set(error.message || 'Failed to load analytics data');
      console.error('Analytics loading error:', error);
    } finally {
      analyticsLoading.set(false);
    }
  }
};

// Rental API Functions
export const rentalActions = {
  async loadAll() {
    // GUARD: Only run on core pages
    if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/core')) {
      return;
    }
    
    rentalLoading.set(true);
    rentalError.set(null);
    
    try {
      const filters = get(rentalFilters);
      const [propertiesResponse, leasesResponse] = await Promise.all([
        rentalAPI.getRentalProperties(filters),
        rentalAPI.getLeases(filters)
      ]);
      
      const propertyList = propertiesResponse.results || propertiesResponse;
      const leaseList = leasesResponse.results || leasesResponse;
      
      rentalProperties.set(propertyList);
      leases.set(leaseList);
      
      // Calculate rental stats from real data
      const occupiedCount = propertyList.filter(p => p.is_currently_rented === true).length;
      const stats = {
        totalProperties: propertyList.length,
        occupiedProperties: occupiedCount,
        vacantProperties: propertyList.length - occupiedCount,
        activeLeases: leaseList.filter(l => l.status === 'active').length,
        expiringLeases: leaseList.filter(l => {
          const today = new Date();
          const endDate = new Date(l.end_date);
          const daysUntilExpiry = Math.ceil((endDate - today) / (1000 * 60 * 60 * 24));
          return daysUntilExpiry <= 30 && daysUntilExpiry > 0;
        }).length,
        occupancyRate: propertyList.length > 0 ? (occupiedCount / propertyList.length) * 100 : 0
      };
      rentalStats.set(stats);
      
    } catch (error) {
      // Silently handle permission errors - don't spam console
      if (error.message?.includes('403') || error.message?.includes('Forbidden')) {
        // User doesn't have permission - silently skip
        rentalError.set(null);
      } else if (error.message?.includes('401') || error.message?.includes('Unauthorized')) {
        rentalError.set('Authentication required. Please log in again.');
      } else if (error.message?.includes('verification')) {
        rentalError.set('Email verification required to view rental data.');
      } else {
        console.error('Rental loading error:', error);
        rentalError.set(error.message || 'Failed to load rental data');
      }
    } finally {
      rentalLoading.set(false);
    }
  }
};

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

// Refresh all data
export async function refreshAllData() {
  // GUARD: Only run on core pages
  if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/core')) {
    return; // Silently exit if not on core page
  }
  
  const trigger = get(refreshTrigger);
  refreshTrigger.set(trigger + 1);
  
  coreLoading.set(true);
  
  try {
    // Use Promise.allSettled to continue even if some modules fail
    const results = await Promise.allSettled([
      maintenanceActions.loadAll(),
      financialActions.loadAll(),
      contractActions.loadAll(),
      analyticsActions.loadDashboard(),
      rentalActions.loadAll()
    ]);
    
    // Log which modules failed
    results.forEach((result, index) => {
      const modules = ['maintenance', 'financial', 'contracts', 'analytics', 'rental'];
      if (result.status === 'rejected') {
        console.warn(`${modules[index]} module failed to load:`, result.reason);
      }
    });
    
    // Only set core error if ALL modules failed
    const allFailed = results.every(result => result.status === 'rejected');
    if (allFailed) {
      coreError.set('Failed to refresh data');
    } else {
      coreError.set(null); // Clear any previous errors
    }
  } catch (error) {
    console.error('Unexpected error in refreshAllData:', error);
    coreError.set('Failed to refresh data');
  } finally {
    coreLoading.set(false);
  }
}

// Reset all filters
export function resetAllFilters() {
  maintenanceFilters.set({
    status: '',
    priority: '',
    category: '',
    search: '',
    sort: 'newest',
    page: 1
  });
  
  financialFilters.set({
    type: '',
    category: '',
    property: '',
    dateFrom: '',
    dateTo: '',
    search: '',
    sort: 'newest',
    page: 1
  });
  
  contractFilters.set({
    status: '',
    type: '',
    party: '',
    search: '',
    sort: 'newest',
    page: 1
  });
  
  rentalFilters.set({
    status: '',
    occupancy: '',
    search: '',
    sort: 'newest',
    page: 1
  });
}

// Clear all error states
export function clearAllErrors() {
  coreError.set(null);
  maintenanceError.set(null);
  financialError.set(null);
  contractError.set(null);
  analyticsError.set(null);
  rentalError.set(null);
}

// Initialize core store (call this when user logs in and needs core data)
export async function initializeCoreStore(modules = []) {
  // GUARD: Only run on core pages
  if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/core')) {
    return; // Silently exit if not on core page
  }
  
  const currentUser = get(user);
  if (!currentUser) return;
  
  clearAllErrors();
  
  // If no specific modules requested, load all
  if (modules.length === 0) {
    await refreshAllData();
    return;
  }
  
  // Load only requested modules
  coreLoading.set(true);
  
  try {
    const promises = [];
    
    if (modules.includes('maintenance')) {
      promises.push(maintenanceActions.loadAll());
    }
    if (modules.includes('financial')) {
      promises.push(financialActions.loadAll());
    }
    if (modules.includes('contracts')) {
      promises.push(contractActions.loadAll());
    }
    if (modules.includes('analytics')) {
      promises.push(analyticsActions.loadDashboard());
    }
    if (modules.includes('rental')) {
      promises.push(rentalActions.loadAll());
    }
    
    if (promises.length > 0) {
      const results = await Promise.allSettled(promises);
      
      // Log any failures
      results.forEach((result, index) => {
        if (result.status === 'rejected') {
          console.warn(`Module ${modules[index]} failed to load:`, result.reason);
        }
      });
    }
  } catch (error) {
    console.error('Error initializing core store modules:', error);
    coreError.set('Failed to initialize core modules');
  } finally {
    coreLoading.set(false);
  }
}

// Cleanup core store (call this when user logs out)
export function cleanupCoreStore() {
  // Reset all data
  maintenanceRequests.set([]);
  vendors.set([]);
  transactions.set([]);
  expenses.set([]);
  contracts.set([]);
  contractTemplates.set([]);
  rentalProperties.set([]);
  leases.set([]);
  tenants.set([]);
  analyticsData.set({});
  reports.set([]);
  performanceMetrics.set({});
  
  // Reset all stats
  maintenanceStats.set({ totalRequests: 0, pendingRequests: 0, inProgressRequests: 0, completedRequests: 0, emergencyRequests: 0, totalCostYTD: 0 });
  financialStats.set({ totalIncome: 0, totalExpenses: 0, netIncome: 0, monthlyIncome: 0, monthlyExpenses: 0, ytdIncome: 0, ytdExpenses: 0 });
  contractStats.set({ totalContracts: 0, activeContracts: 0, draftContracts: 0, signedContracts: 0, expiredContracts: 0, totalTemplates: 0 });
  rentalStats.set({ totalProperties: 0, occupiedProperties: 0, vacantProperties: 0, activeLeases: 0, expiringLeases: 0, occupancyRate: 0 });
  
  // Reset filters
  resetAllFilters();
  
  // Clear errors and loading states
  clearAllErrors();
  coreLoading.set(false);
  maintenanceLoading.set(false);
  financialLoading.set(false);
  contractLoading.set(false);
  analyticsLoading.set(false);
  rentalLoading.set(false);
}