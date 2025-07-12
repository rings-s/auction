<!-- src/routes/core/financial/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { fade, slide, fly } from 'svelte/transition';
  import { t, locale } from '$lib/i18n';
  import { user } from '$lib/stores/user';
  
  // Core store integration
  import {
    transactions,
    expenses,
    financialLoading,
    financialError,
    financialFilters,
    filteredTransactions,
    financialActions
  } from '$lib/stores/core.js';
  
  // Components
  import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
  import EmptyState from '$lib/components/ui/EmptyState.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';

  // State using Svelte 5 runes
  let activeTab = $state('transactions');
  let searchQuery = $state('');
  let currentPage = $state(1);
  let totalPages = $state(1);
  let showMobileFilters = $state(false);
  let showCreateModal = $state(false);
  let showFilterDropdown = $state({ status: false, type: false, sort: false });
  let isRTL = $derived($locale === 'ar');

  // Form data for new transaction/expense
  let formData = $state({
    transaction_type: '',
    amount: '',
    description: '',
    due_date: '',
    payee_id: '',
    property_id: '',
    category: '',
    vendor_name: '',
    expense_date: ''
  });

  // Computed values using core store
  let currentTransactions = $derived($transactions || []);
  let currentExpenses = $derived($expenses || []);
  let loading = $derived($financialLoading);
  let error = $derived($financialError);
  let filters = $derived($financialFilters);

  let displayedTransactions = $derived.by(() => {
    const baseTransactions = $filteredTransactions || [];
    return baseTransactions.filter(transaction => {
      return !searchQuery || 
        transaction.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        transaction.reference_number?.toLowerCase().includes(searchQuery.toLowerCase());
    });
  });

  let displayedExpenses = $derived.by(() => {
    return currentExpenses.filter(expense => {
      return !searchQuery || 
        expense.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        expense.vendor_name?.toLowerCase().includes(searchQuery.toLowerCase());
    });
  });

  onMount(async () => {
    await financialActions.loadAll();
  });

  async function handleCreateTransaction(event) {
    event.preventDefault();
    try {
      if (activeTab === 'transactions') {
        await financialActions.createTransaction(formData);
      } else {
        // For expenses, we'll use the same transaction API for now
        await financialActions.createTransaction({
          ...formData,
          transaction_type: 'expense'
        });
      }
      
      showCreateModal = false;
      
      // Reset form
      formData = {
        transaction_type: '',
        amount: '',
        description: '',
        due_date: '',
        payee_id: '',
        property_id: '',
        category: '',
        vendor_name: '',
        expense_date: ''
      };
    } catch (err) {
      console.error('Failed to create record:', err);
    }
  }

  function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  }

  function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }).format(new Date(date));
  }

  function getStatusColor(status) {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
      completed: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
      failed: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
      overdue: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
    };
    return colors[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
  }

  async function handlePageChange(page) {
    currentPage = page;
    await financialActions.loadAll();
  }

  // Update filters in the core store
  function updateFilters(newFilters) {
    financialFilters.update(current => ({ ...current, ...newFilters }));
  }
</script>

<svelte:head>
  <title>{$t('core.financial.title')} | {$t('app.name')}</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header Section -->
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg" in:fade={{ duration: 300 }}>
    <div class="px-4 py-5 sm:p-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl sm:truncate">
            {$t('core.financial.title')}
          </h1>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {$t('core.financial.subtitle')}
          </p>
        </div>
        <div class="mt-4 flex items-center space-x-3 sm:mt-0 sm:ml-4">
          <Button
            variant="outline"
            size="sm"
            onclick={() => showMobileFilters = !showMobileFilters}
            class="sm:hidden"
          >
            {$t('core.common.filters')}
          </Button>
          <Button
            onclick={() => showCreateModal = true}
            size="sm"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            {$t('core.common.add')} {activeTab === 'transactions' ? $t('core.financial.transaction') : $t('core.financial.expense')}
          </Button>
        </div>
      </div>
    </div>
  </div>

  <!-- Tabs -->
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg" in:fade={{ delay: 100 }}>
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="-mb-px flex space-x-8 px-6" aria-label="Tabs">
        <button
          onclick={() => activeTab = 'transactions'}
          class={`${
            activeTab === 'transactions'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors duration-200`}
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6v12m-3-2.818.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.467-.22-2.121-.659-1.172-.879-1.172-2.303 0-3.182s3.07-.879 4.242 0L15 9m-3 0V6m0 12v-3" />
          </svg>
          {$t('core.financial.transactions')}
        </button>
        <button
          onclick={() => activeTab = 'expenses'}
          class={`${
            activeTab === 'expenses'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors duration-200`}
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15.75 10.5V6a3.75 3.75 0 1 0-7.5 0v4.5m11.356-1.993 1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 0 1-1.12-1.243l1.264-12A1.125 1.125 0 0 1 5.513 7.5h12.974c.576 0 1.059.435 1.119 1.007ZM8.625 10.5a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm7.5 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
          </svg>
          {$t('core.financial.expenses')}
        </button>
      </nav>
    </div>

    <!-- Filters and Search -->
    <div class="p-6 border-b border-gray-200 dark:border-gray-700 {showMobileFilters ? 'block' : 'hidden sm:block'}">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0 sm:space-x-4">
        <div class="flex-1 max-w-lg">
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              bind:value={searchQuery}
              placeholder={$t('core.common.searchPlaceholder', { type: activeTab === 'transactions' ? $t('core.financial.transactions') : $t('core.financial.expenses') })}
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 text-sm"
            />
          </div>
        </div>
        
        <div class="flex items-center space-x-3">
          <!-- Status Filter -->
          <div class="relative">
            <select
              value={filters.status}
              onchange={(e) => updateFilters({ status: e.target.value })}
              class="block w-32 pl-3 pr-10 py-2 text-base border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">{$t('core.financial.filters.allStatus')}</option>
              <option value="pending">{$t('core.financial.status.pending')}</option>
              <option value="completed">{$t('core.financial.status.completed')}</option>
              <option value="failed">{$t('core.financial.status.failed')}</option>
              <option value="overdue">{$t('core.financial.status.overdue')}</option>
            </select>
          </div>

          {#if activeTab === 'transactions'}
            <!-- Transaction Type Filter -->
            <div class="relative">
              <select
                value={filters.transaction_type}
                onchange={(e) => updateFilters({ transaction_type: e.target.value })}
                class="block w-40 pl-3 pr-10 py-2 text-base border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">{$t('core.financial.filters.allTypes')}</option>
                <option value="rent_payment">{$t('core.financial.transactionTypes.rentPayment')}</option>
                <option value="security_deposit">{$t('core.financial.transactionTypes.securityDeposit')}</option>
                <option value="maintenance_cost">{$t('core.financial.transactionTypes.maintenanceCost')}</option>
                <option value="auction_payment">{$t('core.financial.transactionTypes.auctionPayment')}</option>
                <option value="commission">{$t('core.financial.transactionTypes.commission')}</option>
                <option value="utility_bill">{$t('core.financial.transactionTypes.utilityBill')}</option>
                <option value="insurance">{$t('core.financial.transactionTypes.insurance')}</option>
                <option value="tax_payment">{$t('core.financial.transactionTypes.taxPayment')}</option>
                <option value="other">{$t('core.financial.transactionTypes.other')}</option>
              </select>
            </div>
          {/if}

          <!-- Sort Filter -->
          <div class="relative">
            <select
              value={filters.sort}
              onchange={(e) => updateFilters({ sort: e.target.value })}
              class="block w-32 pl-3 pr-10 py-2 text-base border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="newest">{$t('core.financial.sort.newest')}</option>
              <option value="oldest">{$t('core.financial.sort.oldest')}</option>
              <option value="amount_high">{$t('core.financial.sort.amountHigh')}</option>
              <option value="amount_low">{$t('core.financial.sort.amountLow')}</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="p-6">
      {#if loading}
        <div class="space-y-4">
          {#each Array(5) as _}
            <LoadingSkeleton class="h-16" />
          {/each}
        </div>
      {:else if error}
        <EmptyState
          title={$t('core.common.failedToLoad')}
          description={error}
          actionText={$t('core.common.tryAgain')}
          onAction={() => financialActions.loadAll()}
        />
      {:else if (activeTab === 'transactions' ? displayedTransactions : displayedExpenses).length === 0}
        <EmptyState
          title={$t('core.financial.noItemsFound', { type: activeTab === 'transactions' ? $t('core.financial.transactions') : $t('core.financial.expenses') })}
          description={$t('core.financial.createFirstItem', { type: activeTab === 'transactions' ? $t('core.financial.transaction') : $t('core.financial.expense') })}
          actionText={$t('core.common.add') + ' ' + (activeTab === 'transactions' ? $t('core.financial.transaction') : $t('core.financial.expense'))}
          onAction={() => showCreateModal = true}
        />
      {:else}
        <div class="space-y-4" in:slide={{ duration: 300 }}>
          {#each (activeTab === 'transactions' ? displayedTransactions : displayedExpenses) as item, index}
            <div
              class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors duration-200"
              in:fly={{ y: 20, duration: 300, delay: index * 50 }}
            >
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3">
                    <div class="flex-shrink-0">
                      {#if activeTab === 'transactions'}
                        <div class="w-10 h-10 bg-primary-100 dark:bg-primary-900/20 rounded-lg flex items-center justify-center">
                          <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v12m-3-2.818.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.467-.22-2.121-.659-1.172-.879-1.172-2.303 0-3.182s3.07-.879 4.242 0L15 9m-3 0V6m0 12v-3" />
                          </svg>
                        </div>
                      {:else}
                        <div class="w-10 h-10 bg-red-100 dark:bg-red-900/20 rounded-lg flex items-center justify-center">
                          <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.75 10.5V6a3.75 3.75 0 1 0-7.5 0v4.5m11.356-1.993 1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 0 1-1.12-1.243l1.264-12A1.125 1.125 0 0 1 5.513 7.5h12.974c.576 0 1.059.435 1.119 1.007ZM8.625 10.5a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm7.5 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
                          </svg>
                        </div>
                      {/if}
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center space-x-2">
                        <h3 class="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {item.description}
                        </h3>
                        {#if activeTab === 'transactions' && item.status}
                          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getStatusColor(item.status)}">
                            {item.status}
                          </span>
                        {/if}
                      </div>
                      <div class="mt-1 flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                        {#if activeTab === 'transactions'}
                          <span>{item.transaction_type_display || item.transaction_type}</span>
                          {#if item.due_date}
                            <span>{$t('core.financial.due')}: {formatDate(item.due_date)}</span>
                          {/if}
                          {#if item.reference_number}
                            <span>{$t('core.financial.reference')}: {item.reference_number}</span>
                          {/if}
                        {:else}
                          <span>{item.category_display || item.category}</span>
                          <span>{$t('core.financial.vendor')}: {item.vendor_name}</span>
                          <span>{formatDate(item.expense_date)}</span>
                        {/if}
                      </div>
                    </div>
                  </div>
                </div>
                <div class="flex items-center space-x-4">
                  <div class="text-right">
                    <div class="text-lg font-semibold text-gray-900 dark:text-white">
                      {formatCurrency(item.amount)}
                    </div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">
                      {formatDate(item.created_at)}
                    </div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <Button size="sm" variant="outline">
                      {$t('core.common.edit')}
                    </Button>
                    <Button size="sm" variant="outline">
                      {$t('core.common.view')}
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          {/each}
        </div>

        <!-- Pagination -->
        {#if totalPages > 1}
          <div class="mt-6 flex items-center justify-between">
            <div class="flex-1 flex justify-between sm:hidden">
              <Button
                variant="outline"
                onclick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
              >
                {$t('core.common.previous')}
              </Button>
              <Button
                variant="outline"
                onclick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                {$t('core.common.next')}
              </Button>
            </div>
            <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p class="text-sm text-gray-700 dark:text-gray-300">
                  {$t('core.common.showingPage', { current: currentPage, total: totalPages })}
                </p>
              </div>
              <div>
                <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  {#each Array(Math.min(totalPages, 5)).fill(0) as _, i}
                    {@const page = i + 1}
                    <button
                      onclick={() => handlePageChange(page)}
                      class={`${
                        currentPage === page
                          ? 'z-10 bg-primary-50 border-primary-500 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400'
                          : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700'
                      } relative inline-flex items-center px-4 py-2 border text-sm font-medium transition-colors duration-200`}
                    >
                      {page}
                    </button>
                  {/each}
                </nav>
              </div>
            </div>
          </div>
        {/if}
      {/if}
    </div>
  </div>
</div>

<!-- Create Modal -->
<Modal bind:open={showCreateModal} title={$t('core.common.add') + ' ' + (activeTab === 'transactions' ? $t('core.financial.transaction') : $t('core.financial.expense'))}>
  <form onsubmit={handleCreateTransaction} class="space-y-4">
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      {#if activeTab === 'transactions'}
        <div>
          <label for="transaction_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('core.financial.transactionType')}
          </label>
          <select
            id="transaction_type"
            bind:value={formData.transaction_type}
            required
            class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">{$t('core.financial.selectType')}</option>
            <option value="rent_payment">{$t('core.financial.transactionTypes.rentPayment')}</option>
            <option value="security_deposit">{$t('core.financial.transactionTypes.securityDeposit')}</option>
            <option value="maintenance_cost">{$t('core.financial.transactionTypes.maintenanceCost')}</option>
            <option value="auction_payment">{$t('core.financial.transactionTypes.auctionPayment')}</option>
            <option value="commission">{$t('core.financial.transactionTypes.commission')}</option>
            <option value="utility_bill">{$t('core.financial.transactionTypes.utilityBill')}</option>
            <option value="insurance">{$t('core.financial.transactionTypes.insurance')}</option>
            <option value="tax_payment">{$t('core.financial.transactionTypes.taxPayment')}</option>
            <option value="other">{$t('core.financial.transactionTypes.other')}</option>
          </select>
        </div>
        <div>
          <label for="due_date" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('core.financial.dueDate')}
          </label>
          <input
            type="date"
            id="due_date"
            bind:value={formData.due_date}
            class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>
      {:else}
        <div>
          <label for="category" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('core.financial.category')}
          </label>
          <select
            id="category"
            bind:value={formData.category}
            required
            class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">{$t('core.financial.selectCategory')}</option>
            <option value="maintenance">{$t('core.financial.categories.maintenance')}</option>
            <option value="utilities">{$t('core.financial.categories.utilities')}</option>
            <option value="insurance">{$t('core.financial.categories.insurance')}</option>
            <option value="taxes">{$t('core.financial.categories.taxes')}</option>
            <option value="management">{$t('core.financial.categories.management')}</option>
            <option value="marketing">{$t('core.financial.categories.marketing')}</option>
            <option value="legal">{$t('core.financial.categories.legal')}</option>
            <option value="other">{$t('core.financial.categories.other')}</option>
          </select>
        </div>
        <div>
          <label for="vendor_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('core.financial.vendorName')}
          </label>
          <input
            type="text"
            id="vendor_name"
            bind:value={formData.vendor_name}
            required
            class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>
        <div>
          <label for="expense_date" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('core.financial.expenseDate')}
          </label>
          <input
            type="date"
            id="expense_date"
            bind:value={formData.expense_date}
            required
            class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>
      {/if}
      
      <div>
        <label for="amount" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('core.financial.amount')}
        </label>
        <input
          type="number"
          id="amount"
          bind:value={formData.amount}
          required
          step="0.01"
          min="0"
          class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        />
      </div>
    </div>
    
    <div>
      <label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {$t('core.financial.description')}
      </label>
      <textarea
        id="description"
        bind:value={formData.description}
        required
        rows="3"
        class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
      ></textarea>
    </div>

    <div class="flex justify-end space-x-3 pt-4">
      <Button
        type="button"
        variant="outline"
        onclick={() => showCreateModal = false}
      >
        {$t('core.common.cancel')}
      </Button>
      <Button type="submit">
        {$t('core.common.create')} {activeTab === 'transactions' ? $t('core.financial.transaction') : $t('core.financial.expense')}
      </Button>
    </div>
  </form>
</Modal>