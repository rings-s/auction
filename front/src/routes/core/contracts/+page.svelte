<!-- src/routes/core/contracts/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { fade, slide, fly } from 'svelte/transition';
  import { t, locale } from '$lib/i18n';
  import { user } from '$lib/stores/user';
  import { 
    contracts,
    contractTemplates,
    contractStats,
    contractFilters,
    contractLoading,
    contractError,
    filteredContracts,
    contractActions
  } from '$lib/stores/core.js';
  
  // Components
  import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
  import EmptyState from '$lib/components/ui/EmptyState.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import CoreStatsCard from '$lib/components/core/CoreStatsCard.svelte';

  // Local UI state only
  let activeTab = $state('contracts');
  let showCreateModal = $state(false);
  let searchQuery = $state('');
  let isRTL = $derived($locale === 'ar');
  
  // Derived store values
  let loading = $derived($contractLoading);
  let error = $derived($contractError);
  let stats = $derived($contractStats);
  let templates = $derived($contractTemplates);
  let contractList = $derived($filteredContracts);
  let filters = $derived($contractFilters);

  // Form data for new contract
  let formData = $state({
    title: '',
    description: '',
    template_id: '',
    parties: '',
    terms: '',
    start_date: '',
    end_date: '',
    value: '',
    status: 'draft'
  });

  // Update search function
  function updateSearch(value) {
    contractFilters.update(f => ({ ...f, search: value }));
  }
  
  // Watch for search query changes and update filters
  $effect(() => {
    contractFilters.update(f => ({ ...f, search: searchQuery }));
  });

  onMount(async () => {
    await contractActions.loadAll();
  });

  async function handleCreateContract(event) {
    event.preventDefault();
    try {
      await contractActions.createContract(formData);
      showCreateModal = false;
      
      // Reset form
      formData = {
        title: '',
        description: '',
        template_id: '',
        parties: '',
        terms: '',
        start_date: '',
        end_date: '',
        value: '',
        status: 'draft'
      };
    } catch (err) {
      error = err.message || 'Failed to create contract';
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
      draft: 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400',
      active: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
      signed: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
      expired: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
      terminated: 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400'
    };
    return colors[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
  }
</script>

<svelte:head>
  <title>{$t('core.contracts.title')} | {$t('app.name')}</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header Section -->
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg" in:fade={{ duration: 300 }}>
    <div class="px-4 py-5 sm:p-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl sm:truncate">
            {$t('core.contracts.title')}
          </h1>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {$t('core.contracts.subtitle')}
          </p>
        </div>
        <div class="mt-4 flex items-center space-x-3 sm:mt-0 sm:ml-4">
          <Button
            onclick={() => showCreateModal = true}
            size="sm"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            {$t('core.contracts.newContract')}
          </Button>
        </div>
      </div>
    </div>
  </div>

  <!-- Stats Grid -->
  {#if !loading}
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6" in:slide={{ duration: 400 }}>
      <CoreStatsCard
        title={$t('core.contracts.totalContracts')}
        value={(stats?.totalContracts || 0).toString()}
        icon="document-text"
        color="blue"
      />
      
      <CoreStatsCard
        title={$t('core.contracts.active')}
        value={(stats?.activeContracts || 0).toString()}
        icon="check-circle"
        color="green"
      />
      
      <CoreStatsCard
        title={$t('core.contracts.draft')}
        value={(stats?.draftContracts || 0).toString()}
        icon="document"
        color="gray"
      />
      
      <CoreStatsCard
        title={$t('core.contracts.signed')}
        value={(stats?.signedContracts || 0).toString()}
        icon="pencil-alt"
        color="blue"
        trend="up"
        change="+5%"
      />
      
      <CoreStatsCard
        title={$t('core.contracts.expired')}
        value={(stats?.expiredContracts || 0).toString()}
        icon="exclamation-circle"
        color="red"
      />
      
      <CoreStatsCard
        title={$t('core.contracts.templates')}
        value={(stats?.totalTemplates || 0).toString()}
        icon="template"
        color="purple"
      />
    </div>
  {:else}
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
      {#each Array(6) as _}
        <LoadingSkeleton class="h-24" />
      {/each}
    </div>
  {/if}

  <!-- Tabs -->
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg" in:fade={{ delay: 100 }}>
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="-mb-px flex space-x-8 px-6" aria-label="Tabs">
        <button
          onclick={() => activeTab = 'contracts'}
          class={`${
            activeTab === 'contracts'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors duration-200`}
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          {$t('core.contracts.contractsCount', { count: stats?.totalContracts || 0 })}
        </button>
        <button
          onclick={() => activeTab = 'templates'}
          class={`${
            activeTab === 'templates'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors duration-200`}
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
          </svg>
          {$t('core.contracts.templatesCount', { count: stats?.totalTemplates || 0 })}
        </button>
      </nav>
    </div>

    <!-- Filters and Search -->
    <div class="p-6 border-b border-gray-200 dark:border-gray-700">
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
              placeholder={$t('core.common.searchPlaceholder', { type: activeTab === 'contracts' ? $t('core.contracts.contracts') : $t('core.contracts.templates') })}
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 text-sm"
            />
          </div>
        </div>
        
        {#if activeTab === 'contracts'}
          <div class="flex items-center space-x-3">
            <!-- Status Filter -->
            <div class="relative">
              <select
                value={filters?.status || ''}
                onchange={(e) => contractFilters.update(f => ({ ...f, status: e.target.value }))}
                class="block w-32 pl-3 pr-10 py-2 text-base border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">{$t('core.contracts.filters.allStatus')}</option>
                <option value="draft">{$t('core.contracts.status.draft')}</option>
                <option value="active">{$t('core.contracts.status.active')}</option>
                <option value="signed">{$t('core.contracts.status.signed')}</option>
                <option value="expired">{$t('core.contracts.status.expired')}</option>
                <option value="terminated">{$t('core.contracts.status.terminated')}</option>
              </select>
            </div>
          </div>
        {/if}
      </div>
    </div>

    <!-- Content -->
    <div class="p-6">
      {#if loading}
        <div class="space-y-4">
          {#each Array(5) as _}
            <LoadingSkeleton class="h-32" />
          {/each}
        </div>
      {:else if error}
        <EmptyState
          title={$t('core.common.failedToLoad')}
          description={error}
          actionText={$t('core.common.tryAgain')}
          onAction={() => contractActions.loadAll()}
        />
      {:else if (activeTab === 'contracts' ? (contractList || []) : (templates || [])).length === 0}
        <EmptyState
          title={$t('core.contracts.noItemsFound', { type: activeTab === 'contracts' ? $t('core.contracts.contracts') : $t('core.contracts.templates') })}
          description={$t('core.contracts.createFirstItem', { type: activeTab === 'contracts' ? $t('core.contracts.contract') : $t('core.contracts.template') })}
          actionText={$t('core.common.add') + ' ' + (activeTab === 'contracts' ? $t('core.contracts.contract') : $t('core.contracts.template'))}
          onAction={() => showCreateModal = true}
        />
      {:else}
        <div class="space-y-4" in:slide={{ duration: 300 }}>
          {#if activeTab === 'contracts'}
            <!-- Contracts List -->
            {#each (contractList || []) as contract, index}
              <div
                class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors duration-200"
                in:fly={{ y: 20, duration: 300, delay: index * 50 }}
              >
                <div class="flex items-start justify-between">
                  <div class="flex items-start space-x-4">
                    <div class="flex-shrink-0">
                      <div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                        <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center space-x-2 mb-2">
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                          {contract.title}
                        </h3>
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getStatusColor(contract.status)}">
                          {contract.status_display || contract.status}
                        </span>
                      </div>
                      <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                        <p>{contract.description}</p>
                        <div class="flex items-center space-x-4">
                          <span class="font-medium">{$t('core.contracts.parties')}:</span>
                          <span>{contract.parties}</span>
                        </div>
                        <div class="flex items-center space-x-4">
                          <span>{$t('core.contracts.startDate')}: {formatDate(contract.start_date)}</span>
                          {#if contract.end_date}
                            <span>{$t('core.contracts.endDate')}: {formatDate(contract.end_date)}</span>
                          {/if}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="flex items-center space-x-6">
                    {#if contract.value}
                      <div class="text-right">
                        <div class="text-lg font-semibold text-gray-900 dark:text-white">
                          {formatCurrency(contract.value)}
                        </div>
                        <div class="text-sm text-gray-500 dark:text-gray-400">{$t('core.contracts.contractValue')}</div>
                      </div>
                    {/if}
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
          {:else}
            <!-- Templates Grid -->
            <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
              {#each (templates || []) as template, index}
                <div
                  class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors duration-200"
                  in:fly={{ y: 20, duration: 300, delay: index * 50 }}
                >
                  <div class="flex items-start justify-between mb-4">
                    <div class="flex-1">
                      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                        {template.name}
                      </h3>
                      <p class="text-sm text-gray-500 dark:text-gray-400">
                        {template.category_display || template.category}
                      </p>
                    </div>
                  </div>

                  <div class="space-y-2">
                    <div class="text-sm text-gray-600 dark:text-gray-400">
                      {template.description}
                    </div>
                  </div>

                  <div class="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
                    <div class="text-xs text-gray-500 dark:text-gray-400">
                      {$t('core.contracts.created')}: {formatDate(template.created_at)}
                    </div>
                    <div class="flex space-x-2">
                      <Button size="sm" variant="outline">
                        {$t('core.contracts.useTemplate')}
                      </Button>
                      <Button size="sm" variant="outline">
                        {$t('core.common.edit')}
                      </Button>
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {/if}
    </div>
  </div>
</div>

<!-- Create Contract Modal -->
<Modal bind:open={showCreateModal} title={$t('core.contracts.newContract')}>
  <form onsubmit={handleCreateContract} class="space-y-4">
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div class="sm:col-span-2">
        <label for="title" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('core.contracts.contractTitle')}
        </label>
        <input
          type="text"
          id="title"
          bind:value={formData.title}
          required
          class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        />
      </div>

      <div>
        <label for="template_id" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('core.contracts.template')}
        </label>
        <select
          id="template_id"
          bind:value={formData.template_id}
          class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value="">{$t('core.contracts.selectTemplate')}</option>
          {#each (templates || []) as template}
            <option value={template.id}>{template.name}</option>
          {/each}
        </select>
      </div>

      <div>
        <label for="status" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('core.contracts.status.label')}
        </label>
        <select
          id="status"
          bind:value={formData.status}
          required
          class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value="draft">{$t('core.contracts.status.draft')}</option>
          <option value="active">{$t('core.contracts.status.active')}</option>
          <option value="signed">{$t('core.contracts.status.signed')}</option>
        </select>
      </div>

      <div>
        <label for="start_date" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('core.contracts.startDate')}
        </label>
        <input
          type="date"
          id="start_date"
          bind:value={formData.start_date}
          class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        />
      </div>

      <div>
        <label for="end_date" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('core.contracts.endDate')}
        </label>
        <input
          type="date"
          id="end_date"
          bind:value={formData.end_date}
          class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        />
      </div>
    </div>
    
    <div>
      <label for="parties" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {$t('core.contracts.partiesInvolved')}
      </label>
      <input
        type="text"
        id="parties"
        bind:value={formData.parties}
        placeholder={$t('core.contracts.partiesPlaceholder')}
        class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
      />
    </div>
    
    <div>
      <label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {$t('core.contracts.description')}
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
        {$t('core.contracts.createContract')}
      </Button>
    </div>
  </form>
</Modal>