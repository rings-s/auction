<!-- front/src/routes/messages/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { fade, slide, fly } from 'svelte/transition';
    import { t, locale } from '$lib/i18n/i18n';
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
    import ContactForm from '$lib/components/messages/ContactForm.svelte';

    // State
    let messages = [];
    let stats = {};
    let loading = true;
    let error = null;
    let selectedMessage = null;
    let activeFilter = 'all';
    let searchQuery = '';
    let currentPage = 1;
    let totalPages = 1;
    let showMobileMenu = false;
    
    // Computed
    $: isRTL = $locale === 'ar';
    $: filteredMessages = messages.filter(message => {
      const matchesSearch = !searchQuery || 
        message.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
        message.body.toLowerCase().includes(searchQuery.toLowerCase()) ||
        message.sender_info?.name.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesFilter = activeFilter === 'all' || 
        (activeFilter === 'unread' && message.status === 'unread') ||
        (activeFilter === 'inbox' && message.recipient_info?.id === $user?.id) ||
        (activeFilter === 'sent' && message.sender_info?.id === $user?.id) ||
        (activeFilter === 'archived' && message.status === 'archived');
      
      return matchesSearch && matchesFilter;
    });
    
    // Filter options
    const filterOptions = [
      { id: 'all', label: 'messages.filters.all', icon: 'inbox', count: () => stats.total_messages || 0 },
      { id: 'inbox', label: 'messages.filters.inbox', icon: 'inbox', count: () => stats.received_count || 0 },
      { id: 'sent', label: 'messages.filters.sent', icon: 'send', count: () => stats.sent_count || 0 },
      { id: 'unread', label: 'messages.filters.unread', icon: 'mail', count: () => stats.unread_count || 0 },
      { id: 'archived', label: 'messages.filters.archived', icon: 'archive', count: () => 0 }
    ];
    
    // Load messages
    async function loadMessages() {
      try {
        loading = true;
        error = null;
        
        const [messagesResponse, statsResponse] = await Promise.all([
          getMessages({ 
            page: currentPage,
            box: activeFilter === 'all' ? undefined : activeFilter,
            search: searchQuery || undefined
          }),
          getMessageStats()
        ]);
        
        messages = messagesResponse.results || messagesResponse;
        stats = statsResponse;
        
        if (messagesResponse.count) {
          totalPages = Math.ceil(messagesResponse.count / (messagesResponse.page_size || 20));
        }
        
      } catch (err) {
        console.error('Error loading messages:', err);
        error = err.message;
      } finally {
        loading = false;
      }
    }
    
    // Handle filter change
    function setActiveFilter(filterId) {
      activeFilter = filterId;
      currentPage = 1;
      selectedMessage = null;
      showMobileMenu = false;
      loadMessages();
    }
    
    // Handle search
    let searchTimeout;
    function handleSearch() {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        currentPage = 1;
        loadMessages();
      }, 500);
    }
    
    // Select message
    async function selectMessage(message) {
      selectedMessage = message;
      
      // Mark as read if unread
      if (message.status === 'unread' && message.recipient_info?.id === $user?.id) {
        try {
          await markMessageAsRead(message.id);
          message.status = 'read';
          stats.unread_count = Math.max(0, stats.unread_count - 1);
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
        }
      } catch (err) {
        console.error('Error deleting message:', err);
      }
    }
    
    // Format date
    function formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      const now = new Date();
      const diffTime = Math.abs(now - date);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays === 1) {
        return $t('common.today');
      } else if (diffDays === 2) {
        return $t('common.yesterday');
      } else if (diffDays < 7) {
        return date.toLocaleDateString($locale, { weekday: 'long' });
      } else {
        return date.toLocaleDateString($locale, { 
          year: 'numeric', 
          month: 'short', 
          day: 'numeric' 
        });
      }
    }
    
    // Get icon by name
    function getIcon(name) {
      const icons = {
        inbox: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m14 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m14 0H8m12 0H4m0 0l4-4m0 4l4-4"></path></svg>`,
        send: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>`,
        mail: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>`,
        archive: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8l6 6 6-6"></path></svg>`
      };
      return icons[name] || '';
    }
    
    // Load data on mount
    onMount(() => {
      loadMessages();
    });
  </script>
  
  <svelte:head>
    <title>{$t('messages.title')} | Auction Platform</title>
  </svelte:head>
  
<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
  <!-- Header -->
  <div class="bg-white dark:bg-gray-800 shadow-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="md:flex md:items-center md:justify-between">
        <div>
          <h1 class="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white flex items-center">
            <svg class="w-8 h-8 {isRTL ? 'ml-3' : 'mr-3'} text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            {$t('messages.title')}
          </h1>
          
          {#if stats.total_messages}
            <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
              {stats.total_messages} {$t('messages.totalMessages')}
              {#if stats.unread_count > 0}
                • <span class="font-semibold text-primary-600 dark:text-primary-400">
                  {stats.unread_count} {$t('messages.unread')}
                </span>
              {/if}
            </p>
          {/if}
        </div>
        
        <!-- Mobile Menu Button -->
        <button
          type="button"
          class="md:hidden mt-4 p-2 rounded-md bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
          on:click={() => showMobileMenu = !showMobileMenu}
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>
    </div>
  </div>
  
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
      <!-- Sidebar -->
      <div class="lg:col-span-1">
        <div class={`${showMobileMenu ? 'block' : 'hidden'} lg:block`}>
          <!-- Search -->
          <div class="mb-6">
            <div class="relative">
              <input
                type="text"
                bind:value={searchQuery}
                on:input={handleSearch}
                placeholder={$t('messages.searchPlaceholder')}
                class="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
              />
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>
          </div>
          
          <!-- Filters -->
          <nav class="space-y-2">
            {#each filterOptions as filter}
              <button
                type="button"
                class={`w-full flex items-center justify-between px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  activeFilter === filter.id
                    ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 border border-primary-200 dark:border-primary-700'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 border border-transparent'
                }`}
                on:click={() => setActiveFilter(filter.id)}
              >
                <div class="flex items-center">
                  {@html getIcon(filter.icon)}
                  <span class="{isRTL ? 'mr-3' : 'ml-3'}">{$t(filter.label)}</span>
                </div>
                
                {#if filter.count() > 0}
                  <span class={`px-2 py-1 text-xs rounded-full ${
                    activeFilter === filter.id
                      ? 'bg-primary-200 dark:bg-primary-800 text-primary-800 dark:text-primary-200'
                      : 'bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300'
                  }`}>
                    {filter.count()}
                  </span>
                {/if}
              </button>
            {/each}
          </nav>
        </div>
      </div>
      
      <!-- Messages List -->
      <div class="lg:col-span-2">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
          {#if loading}
            <div class="p-6 space-y-4">
              {#each Array(5) as _}
                <LoadingSkeleton height="80px" />
              {/each}
            </div>
          {:else if error}
            <div class="p-6 text-center">
              <svg class="mx-auto h-12 w-12 text-red-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <p class="text-red-600 dark:text-red-400">{error}</p>
              <Button
                onClick={loadMessages}
                variant="outline"
                size="default"
                class="mt-4"
              >
                {$t('common.tryAgain')}
              </Button>
            </div>
          {:else if filteredMessages.length === 0}
            <div class="p-12 text-center">
              <svg class="mx-auto h-16 w-16 text-gray-400 dark:text-gray-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m14 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m14 0H8m12 0H4m0 0l4-4m0 4l4-4" />
              </svg>
              <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
                {$t('messages.noMessages')}
              </h3>
              <p class="text-gray-600 dark:text-gray-400">
                {searchQuery ? $t('messages.noSearchResults') : $t('messages.noMessagesDesc')}
              </p>
            </div>
          {:else}
            <div class="divide-y divide-gray-200 dark:divide-gray-700">
              {#each filteredMessages as message, index (message.id)}
                <button
                  type="button"
                  class={`w-full p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors ${
                    selectedMessage?.id === message.id ? 'bg-primary-50 dark:bg-primary-900/20' : ''
                  } ${message.status === 'unread' ? 'border-l-4 border-primary-500' : ''}`}
                  on:click={() => selectMessage(message)}
                  in:fly={{ y: 20, duration: 200, delay: index * 50 }}
                >
                  <div class="flex items-start justify-between">
                    <div class="flex-1 min-w-0">
                      <!-- Sender/Recipient info -->
                      <div class="flex items-center mb-1">
                        <div class="w-8 h-8 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center text-white text-sm font-semibold {isRTL ? 'ml-3' : 'mr-3'}">
                          {(message.sender_info?.name || 'U')[0].toUpperCase()}
                        </div>
                        
                        <div class="flex-1 min-w-0">
                          <p class={`text-sm ${message.status === 'unread' ? 'font-semibold' : 'font-medium'} text-gray-900 dark:text-white truncate`}>
                            {message.sender_info?.id === $user?.id 
                              ? `To: ${message.recipient_info?.name}` 
                              : message.sender_info?.name}
                          </p>
                          
                          {#if message.property_info}
                            <p class="text-xs text-primary-600 dark:text-primary-400 truncate">
                              {$t('messages.aboutProperty')}: {message.property_info.title}
                            </p>
                          {/if}
                        </div>
                      </div>
                      
                      <!-- Subject -->
                      <h4 class={`text-sm ${message.status === 'unread' ? 'font-semibold' : 'font-medium'} text-gray-900 dark:text-white mb-1 truncate`}>
                        {message.subject}
                      </h4>
                      
                      <!-- Preview -->
                      <p class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                        {message.body}
                      </p>
                    </div>
                    
                    <!-- Meta info -->
                    <div class="flex flex-col items-end {isRTL ? 'mr-4' : 'ml-4'} flex-shrink-0">
                      <span class="text-xs text-gray-500 dark:text-gray-400">
                        {formatDate(message.created_at)}
                      </span>
                      
                      {#if message.status === 'unread'}
                        <div class="w-2 h-2 bg-primary-500 rounded-full mt-1"></div>
                      {/if}
                      
                      {#if message.priority === 'high' || message.priority === 'urgent'}
                        <svg class="w-4 h-4 text-red-500 mt-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                      {/if}
                    </div>
                  </div>
                </button>
              {/each}
            </div>
          {/if}
        </div>
      </div>
      
      <!-- Message Detail -->
      <div class="lg:col-span-1">
        {#if selectedMessage}
          <div 
            class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 sticky top-8"
            transition:slide={{ duration: 300 }}
          >
            <!-- Header -->
            <div class="p-6 border-b border-gray-200 dark:border-gray-700">
              <div class="flex items-start justify-between mb-4">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center text-white font-semibold {isRTL ? 'ml-3' : 'mr-3'}">
                    {(selectedMessage.sender_info?.name || 'U')[0].toUpperCase()}
                  </div>
                  <div>
                    <p class="font-medium text-gray-900 dark:text-white">
                      {selectedMessage.sender_info?.name}
                    </p>
                    <p class="text-sm text-gray-600 dark:text-gray-400">
                      {formatDate(selectedMessage.created_at)}
                    </p>
                  </div>
                </div>
                
                <!-- Actions -->
                <div class="flex items-center space-x-2">
                  <button
                    type="button"
                    on:click={() => handleArchiveMessage(selectedMessage.id)}
                    class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                    title={$t('messages.archive')}
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8l6 6 6-6" />
                    </svg>
                  </button>
                  
                  <button
                    type="button"
                    on:click={() => handleDeleteMessage(selectedMessage.id)}
                    class="p-2 text-gray-400 hover:text-red-600 dark:hover:text-red-400 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                    title={$t('messages.delete')}
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
              
              <!-- Subject and Priority -->
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {selectedMessage.subject}
              </h3>
              
              <div class="flex items-center space-x-2">
                {#if selectedMessage.priority !== 'normal'}
                  <span class={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    selectedMessage.priority === 'urgent' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                    selectedMessage.priority === 'high' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200' :
                    'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                  }`}>
                    {selectedMessage.priority_display}
                  </span>
                {/if}
                
                {#if selectedMessage.property_info}
                  <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200">
                    {$t('messages.propertyInquiry')}
                  </span>
                {/if}
              </div>
            </div>
            
            <!-- Message Content -->
            <div class="p-6">
              <div class="prose dark:prose-invert max-w-none">
                <p class="text-gray-800 dark:text-gray-200 whitespace-pre-wrap leading-relaxed">
                  {selectedMessage.body}
                </p>
              </div>
              
              <!-- Property Info -->
              {#if selectedMessage.property_info}
                <div class="mt-6 p-4 bg-gray-50 dark:bg-gray-750 rounded-lg">
                  <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-2">
                    {$t('messages.relatedProperty')}
                  </h4>
                  <a 
                    href="/properties/{selectedMessage.property_info.slug}"
                    class="flex items-center hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg p-2 transition-colors"
                  >
                    {#if selectedMessage.property_info.main_image}
                      <img 
                        src={selectedMessage.property_info.main_image.url} 
                        alt={selectedMessage.property_info.title}
                        class="w-12 h-12 rounded-lg object-cover {isRTL ? 'ml-3' : 'mr-3'}"
                      />
                    {/if}
                    <div>
                      <p class="font-medium text-gray-900 dark:text-white text-sm">
                        {selectedMessage.property_info.title}
                      </p>
                      {#if selectedMessage.property_info.market_value}
                        <p class="text-primary-600 dark:text-primary-400 text-sm">
                          ${selectedMessage.property_info.market_value.toLocaleString()}
                        </p>
                      {/if}
                    </div>
                  </a>
                </div>
              {/if}
            </div>
            
            <!-- Reply Button -->
            <div class="p-6 border-t border-gray-200 dark:border-gray-700">
              <Button
                href="/messages/compose?reply={selectedMessage.id}"
                variant="primary"
                size="default"
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
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-12 text-center">
            <svg class="mx-auto h-16 w-16 text-gray-400 dark:text-gray-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
              {$t('messages.selectMessage')}
            </h3>
            <p class="text-gray-600 dark:text-gray-400">
              {$t('messages.selectMessageDesc')}
            </p>
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>
  
<style>
    .line-clamp-2 {
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
</style>