<script>
  import { onMount } from 'svelte';
  import { fade, slide, fly } from 'svelte/transition';
  import { t, locale } from '$lib/i18n';
  import { user } from '$lib/stores/user';
  import { 
    getMessages, 
    getMessageStats, 
    markMessageAsRead, 
    archiveMessage,
    deleteMessage 
  } from '$lib/api/messages';
  import Button from '$lib/components/ui/Button.svelte';
  import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';

  // State management with Svelte 5
  let messages = $state([]);
  let stats = $state({});
  let loading = $state(true);
  let error = $state(null);
  let selectedMessage = $state(null);
  let activeFilter = $state('all');
  let searchQuery = $state('');
  let currentPage = $state(1);
  let totalPages = $state(1);
  let showMobileDetail = $state(false);
  let showMobileFilters = $state(false);
  let showFilterDropdown = $state({ status: false, priority: false, sort: false });
  let activeFiltersCount = $state(0);
  
  // Derived values
  let isRTL = $derived($locale === 'ar');
  
  let filteredMessages = $derived.by(() => {
    return messages.filter(message => {
      const matchesSearch = !searchQuery || 
        message.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
        message.body.toLowerCase().includes(searchQuery.toLowerCase()) ||
        message.sender_info?.name?.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesFilter = activeFilter === 'all' || 
        (activeFilter === 'unread' && message.status === 'unread') ||
        (activeFilter === 'inbox' && message.recipient_info?.id === $user?.id) ||
        (activeFilter === 'sent' && message.sender_info?.id === $user?.id) ||
        (activeFilter === 'archived' && message.status === 'archived');
      
      return matchesSearch && matchesFilter;
    });
  });
  
  // Filter options with modern design
  const filterOptions = [
    { id: 'all', label: 'messages.filters.all', icon: '📬', color: 'gray' },
    { id: 'inbox', label: 'messages.filters.inbox', icon: '📥', color: 'blue' },
    { id: 'sent', label: 'messages.filters.sent', icon: '📤', color: 'green' },
    { id: 'unread', label: 'messages.filters.unread', icon: '📨', color: 'amber' },
    { id: 'archived', label: 'messages.filters.archived', icon: '📦', color: 'purple' }
  ];

  // Sort options
  const sortOptions = [
    { value: 'newest', label: 'search.sortOptions.newest', icon: '🆕' },
    { value: 'oldest', label: 'search.sortOptions.oldest', icon: '📅' },
    { value: 'priority', label: 'messages.sortByPriority', icon: '🔥' }
  ];

  // Priority options
  const priorityOptions = [
    { value: '', label: 'messages.allPriorities' },
    { value: 'urgent', label: 'messages.priority.urgent', icon: '🚨' },
    { value: 'high', label: 'messages.priority.high', icon: '⚠️' },
    { value: 'normal', label: 'messages.priority.normal', icon: '📌' },
    { value: 'low', label: 'messages.priority.low', icon: '🔵' }
  ];

  // Filters state
  let filters = $state({
    search: '',
    priority: '',
    sort: 'newest'
  });

  // Calculate active filters count
  $effect(() => {
    let count = 0;
    if (filters.search) count++;
    if (filters.priority) count++;
    if (filters.sort !== 'newest') count++;
    if (activeFilter !== 'all') count++;
    activeFiltersCount = count;
  });

  // Toggle dropdown visibility
  function toggleDropdown(name) {
    showFilterDropdown = Object.keys(showFilterDropdown).reduce((acc, key) => {
      acc[key] = key === name ? !showFilterDropdown[key] : false;
      return acc;
    }, {});
  }

  // Close all dropdowns when clicking outside
  function handleClickOutside(event) {
    if (!event.target.closest('.filter-dropdown')) {
      showFilterDropdown = Object.keys(showFilterDropdown).reduce((acc, key) => {
        acc[key] = false;
        return acc;
      }, {});
    }
  }

  // Handle filter changes
  function handleFilterChange(name, value) {
    filters[name] = value;
    currentPage = 1;
    loadMessages();
  }
  
  // Toggle mobile filters
  function toggleMobileFilters() {
    showMobileFilters = !showMobileFilters;
  }
  
  // Load messages
  async function loadMessages() {
    loading = true;
    error = null;
    
    try {
      const params = {
        page: currentPage,
        box: activeFilter === 'all' ? undefined : activeFilter,
        search: filters.search || undefined,
        priority: filters.priority || undefined
      };

      // Add sorting
      switch (filters.sort) {
        case 'oldest':
          params.ordering = 'created_at';
          break;
        case 'priority':
          params.ordering = '-priority_level,-created_at';
          break;
        default:
          params.ordering = '-created_at';
      }

      const [messagesResponse, statsResponse] = await Promise.all([
        getMessages(params),
        getMessageStats()
      ]);
      
      messages = messagesResponse.results || messagesResponse;
      stats = statsResponse.data || statsResponse;
      
      if (messagesResponse.count) {
        totalPages = Math.ceil(messagesResponse.count / (messagesResponse.page_size || 20));
      }
      
    } catch (err) {
      error = err.message || $t('error.fetchFailed');
    } finally {
      loading = false;
    }
  }
  
  // Handle filter change
  function setActiveFilter(filterId) {
    activeFilter = filterId;
    currentPage = 1;
    selectedMessage = null;
    loadMessages();
  }
  
  // Clear all filters
  function clearFilters() {
    filters = {
      search: '',
      priority: '',
      sort: 'newest'
    };
    activeFilter = 'all';
    loadMessages();
  }
  
  // Handle search with debounce
  let searchTimeout;
  function handleSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      currentPage = 1;
      loadMessages();
    }, 300);
  }
  
  // Select message
  async function selectMessage(message) {
    selectedMessage = message;
    showMobileDetail = true;
    
    // Mark as read if unread
    if (message.status === 'unread' && message.recipient_info?.id === $user?.id) {
      try {
        await markMessageAsRead(message.id);
        message.status = 'read';
        stats.unread_count = Math.max(0, (stats.unread_count || 0) - 1);
      } catch (err) {
        // console.error('Error marking message as read:', err);
      }
    }
  }
  
  // Archive message
  async function handleArchiveMessage(messageId) {
    try {
      await archiveMessage(messageId);
      const messageIndex = messages.findIndex(m => m.id === messageId);
      if (messageIndex > -1) {
        messages[messageIndex].status = 'archived';
      }
      if (selectedMessage?.id === messageId) {
        selectedMessage = null;
        showMobileDetail = false;
      }
      loadMessages(); // Reload to update counts
    } catch (err) {
      // console.error('Error archiving message:', err);
    }
  }
  
  // Delete message
  async function handleDeleteMessage(messageId) {
    if (!confirm($t('messages.confirmDelete'))) return;
    
    try {
      await deleteMessage(messageId);
      messages = messages.filter(m => m.id !== messageId);
      if (selectedMessage?.id === messageId) {
        selectedMessage = null;
        showMobileDetail = false;
      }
      loadMessages(); // Reload to update counts
    } catch (err) {
      // console.error('Error deleting message:', err);
    }
  }
  
  // Format date/time
  function formatDateTime(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return $t('common.justNow');
    if (diffMins < 60) return $t('common.minutesAgo', { count: diffMins });
    if (diffMins < 1440) return $t('common.hoursAgo', { count: Math.floor(diffMins / 60) });
    if (diffMins < 2880) return $t('common.yesterday');
    
    return date.toLocaleDateString($locale, { 
      month: 'short', 
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
  }
  
  // Get priority badge color
  function getPriorityColor(priority) {
    const colors = {
      low: 'bg-slate-100 text-slate-700 dark:bg-slate-900 dark:text-slate-300',
      normal: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300',
      high: 'bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300',
      urgent: 'bg-rose-100 text-rose-700 dark:bg-rose-900 dark:text-rose-300'
    };
    return colors[priority] || colors.normal;
  }
  
  // Initialize
  onMount(() => {
    loadMessages();
    window.addEventListener('click', handleClickOutside);
    return () => {
      window.removeEventListener('click', handleClickOutside);
    };
  });
</script>

<svelte:head>
  <title>{$t('messages.title')} | {$t('app.name')}</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
  <!-- Enhanced Hero Section with Stats -->
  <div class="relative bg-gradient-to-br from-primary-600 via-primary-700 to-secondary-700 text-white">
    <div class="absolute inset-0 bg-black/20"></div>
    <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
      <div class="md:flex md:items-center md:justify-between">
        <div>
          <h1 class="text-3xl md:text-4xl font-bold flex items-center">
            {$t('messages.title')}
            {#if stats.unread_count > 0}
              <span class="ml-3 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-amber-500 text-white animate-pulse">
                <span class="w-2 h-2 bg-white rounded-full mr-2"></span>
                {stats.unread_count} {$t('messages.unread')}
              </span>
            {/if}
          </h1>
          <p class="mt-2 text-base md:text-lg text-white/90">
            {$t('messages.subtitle')}
          </p>
          
          <!-- Stats Bar -->
          {#if stats.total_messages}
            <div class="mt-4 flex flex-wrap gap-4">
              <div class="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2">
                <p class="text-xs text-white/70">Total Messages</p>
                <p class="text-xl font-bold">{stats.total_messages}</p>
              </div>
              <div class="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2">
                <p class="text-xs text-white/70">Received</p>
                <p class="text-xl font-bold">{stats.received_count || 0}</p>
              </div>
              <div class="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2">
                <p class="text-xs text-white/70">Sent</p>
                <p class="text-xl font-bold">{stats.sent_count || 0}</p>
              </div>
            </div>
          {/if}
        </div>
        
        <!-- Compose Button -->
        <div class="mt-6 md:mt-0">
          <Button
            href="/messages/compose"
            variant="primary"
            size="default"
            class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-full shadow-lg !bg-white !text-primary-600 hover:!bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white transition-all duration-300 hover:shadow-xl transform hover:-translate-y-0.5"
          >
            <svg class="w-5 h-5 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            {$t('messages.compose')}
          </Button>
        </div>
      </div>

      <!-- Filter Controls -->
      <div class="mt-8 flex flex-wrap items-center gap-3">
        <!-- Mobile Filters Button -->
        <button
          type="button"
          onclick={toggleMobileFilters}
          class="md:hidden flex items-center justify-center px-4 py-2 rounded-full bg-white/20 backdrop-blur-sm shadow-sm border border-white/30 text-sm font-medium text-white hover:bg-white/30 transition-colors"
        >
          <svg class="w-4 h-4 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
          </svg>
          <span>{$t('messages.filters.title')}</span>
          {#if activeFiltersCount > 0}
            <span class="{isRTL ? 'mr-2' : 'ml-2'} flex items-center justify-center w-5 h-5 text-xs font-semibold rounded-full bg-yellow-400 text-gray-900">
              {activeFiltersCount}
            </span>
          {/if}
        </button>

        <!-- Search Box -->
        <div class="relative flex-grow max-w-md">
          <div class="absolute inset-y-0 {isRTL ? 'right-0 pr-3' : 'left-0 pl-3'} flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-white/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            type="text"
            bind:value={filters.search}
            oninput={handleSearch}
            placeholder={$t('messages.search')}
            class="{isRTL ? 'pr-10 pl-4' : 'pl-10 pr-4'} py-2.5 w-full rounded-full bg-white/20 backdrop-blur-sm border border-white/30 text-white placeholder-white/70 focus:bg-white/30 focus:border-white/50 focus:ring-2 focus:ring-white/50 transition-all"
          />
          {#if filters.search}
            <button
              type="button"
              class="absolute inset-y-0 {isRTL ? 'left-0 pl-3' : 'right-0 pr-3'} flex items-center text-white/70 hover:text-white"
              onclick={() => handleFilterChange('search', '')}
              aria-label={$t('search.removeFilter')}
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          {/if}
        </div>
        
        <!-- Filter Controls - Desktop Only -->
        <div class="hidden md:flex flex-wrap items-center gap-2">
          <!-- Status Filter Pills -->
          {#each filterOptions as filter}
            {@const count = filter.id === 'all' ? stats.total_messages :
              filter.id === 'inbox' ? stats.received_count :
              filter.id === 'sent' ? stats.sent_count :
              filter.id === 'unread' ? stats.unread_count : 0}
            
            <button
              type="button"
              class="inline-flex items-center px-4 py-2.5 rounded-full shadow-sm text-sm font-medium transition-colors
                {activeFilter === filter.id
                  ? 'bg-white/30 backdrop-blur-sm border border-white/50 text-white'
                  : 'bg-white/20 backdrop-blur-sm border border-white/30 text-white hover:bg-white/30'
                }"
              onclick={() => setActiveFilter(filter.id)}
            >
              <span class="mr-1.5">{filter.icon}</span>
              {$t(filter.label)}
              {#if count > 0}
                <span class="ml-2 text-xs">({count})</span>
              {/if}
            </button>
          {/each}

          <!-- Priority Filter Dropdown -->
          <div class="relative filter-dropdown">
            <button
              type="button"
              onclick={() => toggleDropdown('priority')}
              class="inline-flex items-center px-4 py-2.5 rounded-full bg-white/20 backdrop-blur-sm shadow-sm border border-white/30 text-sm font-medium text-white hover:bg-white/30 transition-colors {filters.priority ? 'bg-white/30 border-white/50' : ''}"
            >
              <span>{filters.priority ? `${priorityOptions.find(o => o.value === filters.priority)?.icon} ${$t(priorityOptions.find(o => o.value === filters.priority)?.label)}` : '🎯 ' + $t('messages.priority.title')}</span>
              <svg class="w-4 h-4 {isRTL ? 'mr-2' : 'ml-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            {#if showFilterDropdown.priority}
              <div 
                class="absolute {isRTL ? 'right-0' : 'left-0'} mt-2 w-56 rounded-xl shadow-xl bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 focus:outline-none z-10 overflow-hidden"
                transition:fade={{ duration: 150 }}
              >
                <div class="py-1">
                  {#each priorityOptions as option}
                    <button
                      class="w-full text-start px-4 py-3 text-sm flex items-center {filters.priority === option.value ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 font-medium' : 'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700'} transition-colors"
                      onclick={() => handleFilterChange('priority', option.value)}
                    >
                      {#if option.icon}
                        <span class="mr-2 text-lg">{option.icon}</span>
                      {/if}
                      {$t(option.label)}
                    </button>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
          
          <!-- Sort Dropdown -->
          <div class="relative filter-dropdown">
            <button
              type="button"
              onclick={() => toggleDropdown('sort')}
              class="inline-flex items-center px-4 py-2.5 rounded-full bg-white/20 backdrop-blur-sm shadow-sm border border-white/30 text-sm font-medium text-white hover:bg-white/30 transition-colors {filters.sort !== 'newest' ? 'bg-white/30 border-white/50' : ''}"
            >
              <svg class="w-4 h-4 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
              </svg>
              <span>{sortOptions.find(o => o.value === filters.sort)?.icon} {$t(sortOptions.find(o => o.value === filters.sort)?.label)}</span>
            </button>
            
            {#if showFilterDropdown.sort}
              <div 
                class="absolute {isRTL ? 'right-0' : 'left-0'} mt-2 w-56 rounded-xl shadow-xl bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 focus:outline-none z-10 overflow-hidden"
                transition:fade={{ duration: 150 }}
              >
                <div class="py-1">
                  {#each sortOptions as option}
                    <button
                      class="w-full text-start px-4 py-3 text-sm flex items-center {filters.sort === option.value ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 font-medium' : 'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700'} transition-colors"
                      onclick={() => handleFilterChange('sort', option.value)}
                    >
                      <span class="mr-2 text-lg">{option.icon}</span>
                      {$t(option.label)}
                    </button>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
          
          <!-- Clear Filters Button -->
          {#if activeFiltersCount > 0}
            <button
              type="button"
              onclick={clearFilters}
              class="inline-flex items-center px-4 py-2.5 rounded-full bg-red-500/20 backdrop-blur-sm shadow-sm text-sm font-medium text-white hover:bg-red-500/30 transition-colors border border-red-500/30"
            >
              <svg class="w-4 h-4 {isRTL ? 'ml-1' : 'mr-1'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              {$t('search.clear')} ({activeFiltersCount})
            </button>
          {/if}
        </div>
      </div>
    </div>
  </div>

  <!-- Main Content Area -->
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <!-- Messages List -->
      <div class="lg:col-span-7">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
          {#if loading}
            <div class="p-4 space-y-3">
              {#each Array(5) as _}
                <LoadingSkeleton height="80px" />
              {/each}
            </div>
          {:else if error}
            <div class="p-8 text-center">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">{error}</p>
              <Button
                onclick={loadMessages}
                variant="outline"
                size="sm"
                class="mt-4"
              >
                {$t('common.tryAgain')}
              </Button>
            </div>
          {:else if filteredMessages.length === 0}
            <div class="p-8 text-center">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <p class="mt-2 text-sm font-medium text-gray-900 dark:text-white">
                {$t('messages.noMessages')}
              </p>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {filters.search ? $t('messages.noSearchResults') : $t('messages.startConversation')}
              </p>
              {#if activeFiltersCount > 0}
                <Button
                  onclick={clearFilters}
                  variant="outline"
                  size="sm"
                  class="mt-4"
                >
                  <svg class="w-4 h-4 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  {$t('search.clear')}
                </Button>
              {/if}
            </div>
          {:else}
            <div class="divide-y divide-gray-200 dark:divide-gray-700">
              {#each filteredMessages as message (message.id)}
                <button
                  type="button"
                  class="w-full px-4 py-4 text-left hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors
                    {selectedMessage?.id === message.id ? 'bg-primary-50 dark:bg-primary-900/10' : ''}
                    {message.status === 'unread' ? 'border-l-2 border-primary-500' : ''}"
                  onclick={() => selectMessage(message)}
                >
                  <div class="flex items-start gap-3">
                    <!-- Avatar -->
                    <div class="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center text-white font-medium text-sm">
                      {message.sender_info?.name?.[0]?.toUpperCase() || '?'}
                    </div>
                    
                    <!-- Content -->
                    <div class="flex-1 min-w-0">
                      <div class="flex items-start justify-between gap-2">
                        <div class="flex-1 min-w-0">
                          <p class={`text-sm ${message.status === 'unread' ? 'font-semibold' : 'font-medium'} text-gray-900 dark:text-white truncate`}>
                            {message.sender_info?.id === $user?.id 
                              ? $t('messages.to', { name: message.recipient_info?.name })
                              : message.sender_info?.name}
                          </p>
                          <p class={`text-sm ${message.status === 'unread' ? 'font-medium text-gray-900 dark:text-white' : 'text-gray-600 dark:text-gray-400'} truncate`}>
                            {message.subject}
                          </p>
                        </div>
                        <span class="flex-shrink-0 text-xs text-gray-500 dark:text-gray-400">
                          {formatDateTime(message.created_at)}
                        </span>
                      </div>
                      
                      <p class="mt-1 text-sm text-gray-600 dark:text-gray-400 line-clamp-1">
                        {message.body}
                      </p>
                      
                      <!-- Tags -->
                      <div class="mt-1.5 flex items-center gap-2">
                        {#if message.priority !== 'normal'}
                          <span class={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium ${getPriorityColor(message.priority)}`}>
                            {$t(`messages.priority.${message.priority}`)}
                          </span>
                        {/if}
                        {#if message.property_info}
                          <span class="inline-flex items-center text-xs text-primary-600 dark:text-primary-400">
                            <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                            </svg>
                            {message.property_info.title}
                          </span>
                        {/if}
                      </div>
                    </div>
                  </div>
                </button>
              {/each}
            </div>
          {/if}
        </div>
        
        <!-- Pagination -->
        {#if totalPages > 1}
          <div class="mt-4 flex items-center justify-center gap-2">
            <button
              type="button"
              onclick={() => {
                if (currentPage > 1) {
                  currentPage--;
                  loadMessages();
                }
              }}
              disabled={currentPage === 1}
              class="px-3 py-1.5 text-sm rounded-lg border border-gray-300 dark:border-gray-600 
                disabled:opacity-50 disabled:cursor-not-allowed
                hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              {$t('common.previous')}
            </button>
            <span class="text-sm text-gray-600 dark:text-gray-400">
              {currentPage} / {totalPages}
            </span>
            <button
              type="button"
              onclick={() => {
                if (currentPage < totalPages) {
                  currentPage++;
                  loadMessages();
                }
              }}
              disabled={currentPage === totalPages}
              class="px-3 py-1.5 text-sm rounded-lg border border-gray-300 dark:border-gray-600 
                disabled:opacity-50 disabled:cursor-not-allowed
                hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              {$t('common.next')}
            </button>
          </div>
        {/if}
      </div>
      
      <!-- Message Detail -->
      <div class="lg:col-span-5 {showMobileDetail ? 'block' : 'hidden'} lg:block">
        {#if selectedMessage}
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 h-full flex flex-col" in:fade>
            <!-- Message Header -->
            <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <div class="flex items-start justify-between">
                <div class="flex items-start gap-3">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center text-white font-medium text-sm">
                    {selectedMessage.sender_info?.name?.[0]?.toUpperCase() || '?'}
                  </div>
                  <div>
                    <h3 class="text-sm font-semibold text-gray-900 dark:text-white">
                      {selectedMessage.sender_info?.name}
                    </h3>
                    <p class="text-xs text-gray-500 dark:text-gray-400">
                      {selectedMessage.sender_info?.email}
                    </p>
                  </div>
                </div>
                
                <!-- Actions -->
                <div class="flex items-center gap-1">
                  <button
                    type="button"
                    onclick={() => handleArchiveMessage(selectedMessage.id)}
                    class="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                    title={$t('messages.archive')}
                    aria-label={$t('messages.archive')}
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                    </svg>
                  </button>
                  <button
                    type="button"
                    onclick={() => handleDeleteMessage(selectedMessage.id)}
                    class="p-1.5 text-gray-400 hover:text-red-600 dark:hover:text-red-400 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                    title={$t('messages.delete')}
                    aria-label={$t('messages.delete')}
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                  <button
                    type="button"
                    onclick={() => showMobileDetail = false}
                    class="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded hover:bg-gray-100 dark:hover:bg-gray-700 lg:hidden"
                    aria-label={$t('messages.close')}
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              
              <!-- Subject & Meta -->
              <div class="mt-3">
                <h2 class="text-base font-semibold text-gray-900 dark:text-white">
                  {selectedMessage.subject}
                </h2>
                <div class="mt-1 flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                  <span>{new Date(selectedMessage.created_at).toLocaleString($locale)}</span>
                  {#if selectedMessage.priority !== 'normal'}
                    <span class={`inline-flex items-center px-1.5 py-0.5 rounded font-medium ${getPriorityColor(selectedMessage.priority)}`}>
                      {$t(`messages.priority.${selectedMessage.priority}`)}
                    </span>
                  {/if}
                </div>
              </div>
            </div>
            
            <!-- Message Body -->
            <div class="px-6 py-4 flex-1 overflow-y-auto">
              <div class="prose prose-sm dark:prose-invert max-w-none">
                <p class="whitespace-pre-wrap text-gray-700 dark:text-gray-300">
                  {selectedMessage.body}
                </p>
              </div>
              
              <!-- Property Link -->
              {#if selectedMessage.property_info}
                <div class="mt-6 p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg border border-gray-200 dark:border-gray-700">
                  <p class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
                    {$t('messages.relatedProperty')}
                  </p>
                  <a 
                    href="/properties/{selectedMessage.property_info.slug}"
                    class="flex items-center gap-3 group"
                  >
                    <div class="flex-shrink-0 w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                      <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                      </svg>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400">
                        {selectedMessage.property_info.title}
                      </p>
                      {#if selectedMessage.property_info.market_value}
                        <p class="text-xs text-gray-600 dark:text-gray-400">
                          ${selectedMessage.property_info.market_value.toLocaleString()}
                        </p>
                      {/if}
                    </div>
                    <svg class="w-4 h-4 text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="{isRTL ? 'M15 19l-7-7 7-7' : 'M9 5l7 7-7 7'}" />
                    </svg>
                  </a>
                </div>
              {/if}
            </div>
            
            <!-- Reply Button -->
            <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
              <Button
                href="/messages/compose?reply={selectedMessage.id}"
                variant="primary"
                size="sm"
                class="w-full"
              >
                <svg class="w-4 h-4 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
                </svg>
                {$t('messages.reply')}
              </Button>
            </div>
          </div>
        {:else}
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 h-full flex items-center justify-center p-8">
            <div class="text-center">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <p class="mt-2 text-sm font-medium text-gray-900 dark:text-white">
                {$t('messages.selectToRead')}
              </p>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {$t('messages.selectToReadDesc')}
              </p>
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>

  <!-- Enhanced Mobile Filters Drawer -->
  {#if showMobileFilters}
    <div class="fixed inset-0 z-40 flex md:hidden" in:fade={{ duration: 200 }} out:fade={{ duration: 150 }}>
      <!-- Backdrop -->
      <div 
        class="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm"
        onclick={toggleMobileFilters} 
        onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') toggleMobileFilters(); }}
        role="button"
        tabindex="0"
        aria-label={$t('messages.closeFilters')}
      ></div>
      
      <!-- Drawer panel -->
      <div 
        class="relative max-w-sm w-full h-full bg-white dark:bg-gray-800 shadow-2xl flex flex-col overflow-y-auto {isRTL ? 'right-0' : 'left-0'}"
        in:slide={{ duration: 300, axis: 'x' }}
        out:slide={{ duration: 250, axis: 'x', easing: x => 1 - Math.pow(1 - x, 3) }}
      >
        <div class="px-4 py-5 flex items-center justify-between border-b border-gray-200 dark:border-gray-700 bg-primary-600 text-white">
          <h2 class="text-lg font-semibold flex items-center">
            <svg class="w-5 h-5 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
            </svg>
            {$t('messages.filters.title')}
          </h2>
          <button
            type="button"
            class="rounded-full p-2 text-white hover:bg-white/20 transition-colors"
            onclick={toggleMobileFilters}
            aria-label={$t('messages.closeFilters')}
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Mobile Filter Sections -->
        <div class="overflow-y-auto px-4 flex-1">
          <!-- Search -->
          <div class="py-5 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-base font-medium text-gray-900 dark:text-white mb-3 flex items-center">
              <svg class="h-5 w-5 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              {$t('messages.search')}
            </h3>
            <div class="relative rounded-lg">
              <input
                type="text"
                bind:value={filters.search}
                oninput={handleSearch}
                placeholder={$t('messages.searchPlaceholder')}
                class="block w-full {isRTL ? 'pr-4 pl-12' : 'pl-4 pr-12'} py-3 border border-gray-300 dark:border-gray-600 rounded-lg placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-base dark:bg-gray-700 dark:text-white"
              />
              {#if filters.search}
                <div class="absolute inset-y-0 {isRTL ? 'left-0 pl-3' : 'right-0 pr-3'} flex items-center">
                  <button 
                    class="text-gray-400 hover:text-gray-500 dark:text-gray-300 dark:hover:text-white"
                    onclick={() => handleFilterChange('search', '')}
                    aria-label={$t('search.removeFilter')}
                  >
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              {/if}
            </div>
          </div>
          
          <!-- Status Filter -->
          <div class="py-5 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-base font-medium text-gray-900 dark:text-white mb-3 flex items-center">
              <svg class="h-5 w-5 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              {$t('messages.filterByStatus')}
            </h3>
            <div class="space-y-2">
              {#each filterOptions as filter}
                {@const count = filter.id === 'all' ? stats.total_messages :
                  filter.id === 'inbox' ? stats.received_count :
                  filter.id === 'sent' ? stats.sent_count :
                  filter.id === 'unread' ? stats.unread_count : 0}
                
                <button
                  class="w-full flex items-center justify-between px-3 py-3 border text-sm font-medium rounded-lg transition-colors
                    {activeFilter === filter.id 
                      ? 'border-primary-400 bg-primary-50 text-primary-700 dark:border-primary-500 dark:bg-primary-900/20 dark:text-primary-300' 
                      : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}"
                  onclick={() => setActiveFilter(filter.id)}
                >
                  <span class="flex items-center">
                    <span class="mr-2 text-lg">{filter.icon}</span>
                    {$t(filter.label)}
                  </span>
                  {#if count > 0}
                    <span class={`text-xs px-2 py-0.5 rounded-full
                      ${activeFilter === filter.id 
                        ? 'bg-primary-200 dark:bg-primary-800 text-primary-800 dark:text-primary-200'
                        : 'bg-gray-200 dark:bg-gray-700'
                      }`}>
                      {count}
                    </span>
                  {/if}
                </button>
              {/each}
            </div>
          </div>
          
          <!-- Priority Filter -->
          <div class="py-5 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-base font-medium text-gray-900 dark:text-white mb-3 flex items-center">
              <svg class="h-5 w-5 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
              </svg>
              {$t('messages.priority.title')}
            </h3>
            <div class="space-y-2">
              {#each priorityOptions as option}
                <button
                  class="w-full flex items-center px-3 py-3 border text-sm font-medium rounded-lg transition-colors
                    {filters.priority === option.value 
                      ? 'border-primary-400 bg-primary-50 text-primary-700 dark:border-primary-500 dark:bg-primary-900/20 dark:text-primary-300' 
                      : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}"
                  onclick={() => handleFilterChange('priority', option.value)}
                >
                  {#if option.icon}
                    <span class="mr-2 text-lg">{option.icon}</span>
                  {/if}
                  <span>{$t(option.label)}</span>
                </button>
              {/each}
            </div>
          </div>
          
          <!-- Sort Filter -->
          <div class="py-5 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-base font-medium text-gray-900 dark:text-white mb-3 flex items-center">
              <svg class="h-5 w-5 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
              </svg>
              {$t('search.sort')}
            </h3>
            <div class="grid grid-cols-1 gap-2">
              {#each sortOptions as option}
                <button
                  class="flex items-center justify-between px-4 py-3 border text-sm font-medium rounded-lg transition-colors
                    {filters.sort === option.value 
                      ? 'border-primary-400 bg-primary-50 text-primary-700 dark:border-primary-500 dark:bg-primary-900/20 dark:text-primary-300' 
                      : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}"
                  onclick={() => handleFilterChange('sort', option.value)}
                >
                  <span class="flex items-center">
                    <span class="mr-2 text-lg">{option.icon}</span>
                    {$t(option.label)}
                  </span>
                  
                  {#if filters.sort === option.value}
                    <svg class="h-5 w-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  {/if}
                </button>
              {/each}
            </div>
          </div>
        </div>
        
        <!-- Footer Actions -->
        <div class="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 shadow-inner">
          <div class="grid grid-cols-2 gap-3">
            <button
              type="button"
              onclick={clearFilters}
              class="flex justify-center items-center px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              disabled={!activeFiltersCount}
              aria-label={$t('search.clearAllFilters')}
            >
              <svg class="w-4 h-4 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              {$t('search.clear')}
            </button>
            
            <button
              type="button"
              onclick={toggleMobileFilters}
              class="flex justify-center items-center px-4 py-3 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
            >
              <svg class="w-4 h-4 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              {$t('common.apply')}
              {#if activeFiltersCount > 0}
                <span class="{isRTL ? 'mr-1' : 'ml-1'}">({activeFiltersCount})</span>
              {/if}
            </button>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>

<!-- Mobile Compose Button -->
<div class="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 md:hidden">
  <Button
    href="/messages/compose"
    variant="primary"
    size="sm"
    rounded="full"
    class="!p-3 shadow-lg"
  >
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
    </svg>
  </Button>
</div>

<style>
  .line-clamp-1 {
    display: -webkit-box;
    -webkit-line-clamp: 1;
    line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  /* Animation for badges */
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(-4px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  /* Custom scrollbar for filters */
  .overflow-y-auto::-webkit-scrollbar {
    width: 4px;
  }
  
  .overflow-y-auto::-webkit-scrollbar-track {
    background: transparent;
  }
  
  .overflow-y-auto::-webkit-scrollbar-thumb {
    background-color: rgba(156, 163, 175, 0.5);
    border-radius: 2px;
  }
  
  .overflow-y-auto::-webkit-scrollbar-thumb:hover {
    background-color: rgba(156, 163, 175, 0.7);
  }
</style>