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
    { id: 'all', label: 'messages.filters.all', icon: 'grid', color: 'gray' },
    { id: 'inbox', label: 'messages.filters.inbox', icon: 'inbox', color: 'blue' },
    { id: 'sent', label: 'messages.filters.sent', icon: 'send', color: 'green' },
    { id: 'unread', label: 'messages.filters.unread', icon: 'mail', color: 'amber' },
    { id: 'archived', label: 'messages.filters.archived', icon: 'archive', color: 'purple' }
  ];
  
  // Toggle mobile filters
  function toggleMobileFilters() {
    showMobileFilters = !showMobileFilters;
  }
  
  // Load messages
  async function loadMessages() {
    loading = true;
    error = null;
    
    try {
      const [messagesResponse, statsResponse] = await Promise.all([
        getMessages({ 
          page: currentPage,
          box: activeFilter === 'all' ? undefined : activeFilter,
          search: searchQuery || undefined
        }),
        getMessageStats()
      ]);
      
      messages = messagesResponse.results || messagesResponse;
      stats = statsResponse.data || statsResponse;
      
      if (messagesResponse.count) {
        totalPages = Math.ceil(messagesResponse.count / (messagesResponse.page_size || 20));
      }
      
    } catch (err) {
      console.error('Error loading messages:', err);
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
        console.error('Error marking message as read:', err);
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
    } catch (err) {
      console.error('Error archiving message:', err);
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
    } catch (err) {
      console.error('Error deleting message:', err);
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
  });
</script>

<svelte:head>
  <title>{$t('messages.title')} | {$t('app.name')}</title>
</svelte:head>

<div class="min-h-screen">
  <div class="max-w-7xl mx-auto">
    <!-- Header -->
    <div class="px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">
            {$t('messages.title')}
          </h1>
          {#if stats.total_messages}
            <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
              {stats.total_messages} {$t('messages.total')}
              {#if stats.unread_count > 0}
                · <span class="font-medium text-amber-600 dark:text-amber-400">
                  {stats.unread_count} {$t('messages.unread')}
                </span>
              {/if}
            </p>
          {/if}
        </div>
        
        <Button
          href="/messages/compose"
          variant="primary"
          size="default"
          class="hidden lg:inline-flex"
        >
          <svg class="w-4 h-4 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          {$t('messages.compose')}
        </Button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="px-4 sm:px-6 lg:px-8">
      <!-- Mobile Filters Toggle Button -->
      <div class="lg:hidden mb-4">
        <div class="flex items-center justify-between">
          <div class="flex-1">
            <div class="relative">
              <input
                type="text"
                bind:value={searchQuery}
                oninput={handleSearch}
                placeholder={$t('messages.search')}
                class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg 
                  bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                  focus:ring-2 focus:ring-primary-500 focus:border-primary-500 focus:outline-none"
              />
              <svg class="absolute left-3 top-2.5 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
          <button 
            type="button" 
            class="mobile-filter-toggle ml-3 flex-shrink-0 inline-flex items-center justify-center p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
            aria-expanded={showMobileFilters}
            aria-controls="mobile-filters-panel"
            onclick={toggleMobileFilters}
          >
            <span class="sr-only">{showMobileFilters ? $t('common.hideFilters') : $t('common.showFilters')}</span>
            <svg class="filter-icon w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
            <span class="ml-2 text-sm font-medium">{activeFilter !== 'all' ? $t(`messages.filters.${activeFilter}`) : $t('messages.filters.all')}</span>
            <span class="filter-badge ml-2 text-xs px-2 py-0.5 rounded-full bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200">
              {activeFilter === 'all' ? stats.total_messages :
               activeFilter === 'inbox' ? stats.received_count :
               activeFilter === 'sent' ? stats.sent_count :
               activeFilter === 'unread' ? stats.unread_count : 0}
            </span>
          </button>
        </div>

        <!-- Mobile Filters Panel -->
        {#if showMobileFilters}
          <div 
            id="mobile-filters-panel"
            class="mobile-filters-panel mt-3 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
            transition:slide={{ duration: 300, easing: (t) => 1 - Math.pow(1 - t, 3) }}
          >
            <div class="p-3 space-y-1">
              {#each filterOptions as filter}
                {@const count = filter.id === 'all' ? stats.total_messages :
                  filter.id === 'inbox' ? stats.received_count :
                  filter.id === 'sent' ? stats.sent_count :
                  filter.id === 'unread' ? stats.unread_count : 0}
                
                <button
                  type="button"
                  class="filter-option w-full flex items-center justify-between px-3 py-2.5 text-sm rounded-lg transition-all duration-200
                    {activeFilter === filter.id
                      ? `bg-${filter.color}-100 dark:bg-${filter.color}-900/20 text-${filter.color}-700 dark:text-${filter.color}-300 font-medium`
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                    }"
                  onclick={() => { 
                    setActiveFilter(filter.id);
                    // Close mobile filters after selection on small screens
                    if (window.innerWidth < 640) {
                      showMobileFilters = false;
                    }
                  }}
                >
                  <div class="flex items-center">
                    <span class="filter-icon flex-shrink-0 w-5 h-5 mr-2 {activeFilter === filter.id ? `text-${filter.color}-600 dark:text-${filter.color}-400` : 'text-gray-400 dark:text-gray-500'}">
                      {#if filter.icon === 'grid'}
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                        </svg>
                      {:else if filter.icon === 'inbox'}
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                        </svg>
                      {:else if filter.icon === 'send'}
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>
                      {:else if filter.icon === 'mail'}
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                      {:else if filter.icon === 'archive'}
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                        </svg>
                      {/if}
                    </span>
                    <span class="filter-label">{$t(filter.label)}</span>
                  </div>
                  {#if count > 0}
                    <span class={`filter-count text-xs px-2 py-0.5 rounded-full
                      ${activeFilter === filter.id 
                        ? `bg-${filter.color}-200 dark:bg-${filter.color}-800 text-${filter.color}-800 dark:text-${filter.color}-200`
                        : 'bg-gray-200 dark:bg-gray-700'
                      }`}>
                      {count}
                    </span>
                  {/if}
                </button>
              {/each}
            </div>
          </div>
        {/if}
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Sidebar - Desktop Only -->
        <div class="hidden lg:block lg:col-span-3">
          <!-- Search -->
          <div class="mb-4">
            <div class="relative">
              <input
                type="text"
                bind:value={searchQuery}
                oninput={handleSearch}
                placeholder={$t('messages.search')}
                class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg 
                  bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                  focus:ring-2 focus:ring-primary-500 focus:border-primary-500 focus:outline-none"
              />
              <svg class="absolute left-3 top-2.5 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
          
          <!-- Filters - Desktop -->
          <nav class="space-y-1">
            {#each filterOptions as filter}
              {@const count = filter.id === 'all' ? stats.total_messages :
                filter.id === 'inbox' ? stats.received_count :
                filter.id === 'sent' ? stats.sent_count :
                filter.id === 'unread' ? stats.unread_count : 0}
              
              <button
                type="button"
                class="w-full flex items-center justify-between px-3 py-2 text-sm rounded-lg transition-colors
                  {activeFilter === filter.id
                    ? `bg-${filter.color}-100 dark:bg-${filter.color}-900/20 text-${filter.color}-700 dark:text-${filter.color}-300 font-medium`
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                  }"
                onclick={() => setActiveFilter(filter.id)}
              >
                <span>{$t(filter.label)}</span>
                {#if count > 0}
                  <span class={`text-xs px-2 py-0.5 rounded-full
                    ${activeFilter === filter.id 
                      ? `bg-${filter.color}-200 dark:bg-${filter.color}-800 text-${filter.color}-800 dark:text-${filter.color}-200`
                      : 'bg-gray-200 dark:bg-gray-700'
                    }`}>
                    {count}
                  </span>
                {/if}
              </button>
            {/each}
          </nav>
        </div>
        
        <!-- Messages List -->
        <div class="lg:col-span-5">
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            {#if loading}
              <div class="p-4 space-y-3">
                {#each Array(5) as _}
                  <LoadingSkeleton height="72px" />
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
                  {searchQuery ? $t('messages.noSearchResults') : $t('messages.startConversation')}
                </p>
              </div>
            {:else}
              <div class="divide-y divide-gray-200 dark:divide-gray-700">
                {#each filteredMessages as message (message.id)}
                  <button
                    type="button"
                    class="w-full px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors
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
                        <div class="mt-1 flex items-center gap-2">
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
                class="px-3 py-1 text-sm rounded border border-gray-300 dark:border-gray-600 
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
                class="px-3 py-1 text-sm rounded border border-gray-300 dark:border-gray-600 
                  disabled:opacity-50 disabled:cursor-not-allowed
                  hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                {$t('common.next')}
              </button>
            </div>
          {/if}
        </div>
        
        <!-- Message Detail -->
        <div class="lg:col-span-4 {showMobileDetail ? 'block' : 'hidden'} lg:block">
          {#if selectedMessage}
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 h-full" in:fade>
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
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
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
  </div>
</div>

<!-- Mobile Compose Button -->
<div class="fixed bottom-4 right-4 sm:hidden">
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
  
  /* Mobile filter animations and styling */
  .mobile-filter-toggle {
    position: relative;
    transition: all 0.2s ease;
  }
  
  .mobile-filter-toggle:active {
    transform: scale(0.95);
  }
  
  .filter-icon {
    transition: transform 0.3s ease;
  }
  
  .mobile-filter-toggle[aria-expanded="true"] .filter-icon {
    transform: rotate(180deg);
  }
  
  .filter-badge {
    transition: all 0.2s ease;
  }
  
  .mobile-filters-panel {
    transform-origin: top center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  .filter-option {
    position: relative;
    overflow: hidden;
  }
  
  .filter-option:active {
    transform: translateY(1px);
  }
  
  .filter-option::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 100%;
    height: 100%;
    background-color: currentColor;
    border-radius: 50%;
    opacity: 0;
    transform: translate(-50%, -50%) scale(0);
    transition: opacity 0.5s, transform 0.3s;
  }
  
  .filter-option:active::after {
    opacity: 0.1;
    transform: translate(-50%, -50%) scale(1);
    transition: opacity 0s, transform 0s;
  }
  
  .filter-label, .filter-icon, .filter-count {
    position: relative;
    z-index: 1;
    transition: transform 0.2s ease;
  }
  
  .filter-option:hover .filter-label {
    transform: translateX(3px);
  }
  
  @media (prefers-reduced-motion: reduce) {
    *, ::before, ::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
    }
  }
</style>