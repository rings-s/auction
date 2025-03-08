<!-- src/routes/messages/+page.svelte -->
<script>
  import { onMount, tick } from 'svelte';
  import { goto } from '$app/navigation';
  import { fade, fly, slide } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import { isAuthenticated, user } from '$lib/stores/authStore';
  import { notificationStore } from '$lib/stores/notificationStore';
  import { api } from '$lib/api';
  // Removed external formatters import
  import { createChatConnection } from '$lib/websocketService';
  // Import formatters
  import { formatTimeAgo, formatDate } from '$lib/utils/formatters';  

  // UI Components
  import Button from '$lib/components/ui/Button.svelte';
  import Avatar from '$lib/components/ui/Avatar.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Chat from '$lib/components/chat/Chat.svelte';
  
  // Inline implementation of formatTimeAgo
  function formatTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    // Handle invalid date
    if (isNaN(date.getTime())) {
      return 'Invalid date';
    }
    
    // Less than a minute
    if (seconds < 60) {
      return 'just now';
    }
    
    // Less than an hour
    if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60);
      return `${minutes} ${minutes === 1 ? 'minute' : 'minutes'} ago`;
    }
    
    // Less than a day
    if (seconds < 86400) {
      const hours = Math.floor(seconds / 3600);
      return `${hours} ${hours === 1 ? 'hour' : 'hours'} ago`;
    }
    
    // Less than a week
    if (seconds < 604800) {
      const days = Math.floor(seconds / 86400);
      return `${days} ${days === 1 ? 'day' : 'days'} ago`;
    }
    
    // Less than a month
    if (seconds < 2592000) { // 30 days
      const weeks = Math.floor(seconds / 604800);
      return `${weeks} ${weeks === 1 ? 'week' : 'weeks'} ago`;
    }
    
    // Less than a year
    if (seconds < 31536000) {
      const months = Math.floor(seconds / 2592000);
      return `${months} ${months === 1 ? 'month' : 'months'} ago`;
    }
    
    // More than a year
    const years = Math.floor(seconds / 31536000);
    return `${years} ${years === 1 ? 'year' : 'years'} ago`;
  }
  
  // Data states
  let conversations = [];
  let filteredConversations = [];
  let loading = true;
  let error = null;
  let retryCount = 0;
  
  // UI states
  let searchQuery = '';
  let activeFilter = 'all';
  let selectedConversation = null;
  let isConversationOpen = false;
  let skeletonCount = 5;
  let isComposeOpen = false;
  let newMessageData = {
    recipient: '',
    subject: '',
    message: ''
  };
  let newMessageLoading = false;
  let newMessageError = null;
  
  // Filter options
  const filters = [
    { id: 'all', label: 'All Messages' },
    { id: 'unread', label: 'Unread' },
    { id: 'auctions', label: 'Auctions' },
    { id: 'support', label: 'Support' }
  ];
  
  // Get conversation participants excluding current user
  function getOtherParticipant(conversation) {
    if (!conversation || !conversation.participants) return null;
    const otherParticipant = conversation.participants.find(p => p.id !== $user?.id);
    return otherParticipant || { name: 'Unknown', avatar: null };
  }
  
  // Get conversation title
  function getConversationTitle(conversation) {
    if (conversation.auction) {
      return `RE: ${conversation.auction.title || 'Auction'}`;
    } else if (conversation.subject) {
      return conversation.subject;
    } else {
      const participant = getOtherParticipant(conversation);
      return `Conversation with ${participant?.name || 'Unknown'}`;
    }
  }
  
  // Get conversation preview text
  function getMessagePreview(conversation) {
    if (!conversation.last_message) return 'No messages yet';
    
    // Remove quoted content if any
    let preview = conversation.last_message.content
      .replace(/<blockquote>.*?<\/blockquote>/gs, '')
      .replace(/<[^>]*>/g, '')
      .trim();
      
    return preview.length > 60 ? preview.substring(0, 60) + '...' : preview;
  }
  
  // Load conversations data
  async function loadConversations() {
    if (!$isAuthenticated) {
      goto('/login?redirect=/messages');
      return;
    }
    
    try {
      loading = true;
      error = null;
      
      // API call to get conversations
      const response = await api.messages.getConversations();
      
      // Process conversations data
      conversations = (response.results || []).map(conversation => ({
        ...conversation,
        otherParticipant: getOtherParticipant(conversation),
        title: getConversationTitle(conversation),
        preview: getMessagePreview(conversation),
        isRead: conversation.is_read === true
      }));
      
      applyFilters();
      loading = false;
    } catch (err) {
      console.error('Error loading conversations:', err);
      
      if (retryCount < 2) {
        retryCount++;
        setTimeout(() => loadConversations(), 1000 * retryCount);
        return;
      }
      
      error = `Failed to load conversations: ${err.message || 'Unknown error'}`;
      loading = false;
      notificationStore.error(error);
    }
  }
  
  // Apply filters and search
  function applyFilters() {
    let filtered = [...conversations];
    
    // Apply category filter
    if (activeFilter === 'unread') {
      filtered = filtered.filter(conv => !conv.isRead);
    } else if (activeFilter === 'auctions') {
      filtered = filtered.filter(conv => conv.auction !== null);
    } else if (activeFilter === 'support') {
      filtered = filtered.filter(conv => conv.is_support);
    }
    
    // Apply search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim();
      filtered = filtered.filter(conv => 
        (conv.title && conv.title.toLowerCase().includes(query)) || 
        (conv.preview && conv.preview.toLowerCase().includes(query)) ||
        (conv.otherParticipant && conv.otherParticipant.name && 
         conv.otherParticipant.name.toLowerCase().includes(query))
      );
    }
    
    // Sort by most recent first
    filtered.sort((a, b) => {
      const dateA = a.last_message_date ? new Date(a.last_message_date) : new Date(0);
      const dateB = b.last_message_date ? new Date(b.last_message_date) : new Date(0);
      return dateB - dateA;
    });
    
    filteredConversations = filtered;
  }
  
  // Handle search input
  function handleSearchChange() {
    applyFilters();
  }
  
  // Set active filter
  function setFilter(filterId) {
    activeFilter = filterId;
    applyFilters();
  }
  
  // Mark conversation as read
  async function markAsRead(conversationId) {
    try {
      await api.messages.markAsRead(conversationId);
      
      // Update local state
      conversations = conversations.map(conv => {
        if (conv.id === conversationId) {
          return { ...conv, isRead: true };
        }
        return conv;
      });
      
      applyFilters();
    } catch (err) {
      console.error('Error marking conversation as read:', err);
    }
  }
  
  // Handle conversation selection
  function selectConversation(conversation) {
    if (!conversation) return;
    
    selectedConversation = conversation;
    
    // Mark as read if not already
    if (!conversation.isRead) {
      markAsRead(conversation.id);
    }
    
    // Navigate to conversation detail
    goto(`/messages/${conversation.id}`);
  }
  
  // Send new message
  async function sendNewMessage() {
    if (!newMessageData.recipient.trim()) {
      newMessageError = 'Recipient is required';
      return;
    }
    
    if (!newMessageData.message.trim()) {
      newMessageError = 'Message content is required';
      return;
    }
    
    try {
      newMessageLoading = true;
      newMessageError = null;
      
      // API call to send new message
      const response = await api.messages.sendMessage(newMessageData);
      
      // Close compose form and show notification
      isComposeOpen = false;
      notificationStore.success('Message sent successfully');
      
      // Reset form
      newMessageData = {
        recipient: '',
        subject: '',
        message: ''
      };
      
      // Reload conversations to include the new one
      loadConversations();
      
      // Navigate to the new conversation if available
      if (response && response.conversation_id) {
        goto(`/messages/${response.conversation_id}`);
      }
    } catch (err) {
      console.error('Error sending message:', err);
      newMessageError = err.message || 'Failed to send message';
    } finally {
      newMessageLoading = false;
    }
  }
  
  // Format date helper for message timestamps 
  function formatSimpleDate(date) {
    if (!date) return '';
    
    const d = new Date(date);
    if (isNaN(d.getTime())) return '';
    
    return d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: d.getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined
    });
  }
  
  // Initialize on mount
  onMount(() => {
    loadConversations();
  });
</script>

<svelte:head>
  <title>Messages | GUDIC</title>
  <meta name="description" content="View and manage your conversations with buyers and sellers" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <!-- Header with animated welcome -->
  <div class="mb-6 flex flex-col sm:flex-row justify-between gap-4 items-start sm:items-center" in:fly={{ y: -20, duration: 500 }}>
    <div>
      <h1 class="text-3xl font-bold text-text-dark">
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-blue to-secondary-blue">
          Messages
        </span>
      </h1>
      <p class="mt-2 text-text-medium max-w-2xl">
        Communicate with buyers, sellers, and support about your auctions and purchases.
      </p>
    </div>
    
    <div class="flex gap-3">
      <Button 
        variant="outline"
        size="sm"
        on:click={() => loadConversations()}
        disabled={loading}
        class="flex items-center"
      >
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          class="h-4 w-4 mr-1" 
          class:animate-spin={loading}
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Refresh
      </Button>
      
      <Button 
        variant="primary"
        size="sm"
        on:click={() => isComposeOpen = true}
        class="flex items-center"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        New Message
      </Button>
    </div>
  </div>
  
  <!-- Search and filters bar -->
  <div class="flex flex-col sm:flex-row gap-4 mb-6" in:fade={{ delay: 100, duration: 400 }}>
    <!-- Search box -->
    <div class="relative flex-grow">
      <input
        type="text"
        placeholder="Search messages..."
        bind:value={searchQuery}
        on:input={handleSearchChange}
        class="pl-10 pr-4 py-2.5 w-full bg-white border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-primary-blue/30 focus:border-primary-blue shadow-sm"
      />
      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
    </div>
    
    <!-- Filter tabs -->
    <div class="flex space-x-1 overflow-x-auto hide-scrollbar">
      {#each filters as filter}
        <button
          class={`px-4 py-2 rounded-full text-sm font-medium transition-colors whitespace-nowrap
            ${activeFilter === filter.id 
              ? 'bg-primary-blue text-white shadow-sm' 
              : 'bg-white hover:bg-slate-50 text-text-medium border border-slate-200'}`}
          on:click={() => setFilter(filter.id)}
        >
          {filter.label}
          {#if filter.id === 'unread' && conversations.filter(c => !c.isRead).length > 0}
            <span class="ml-1 inline-flex items-center justify-center w-5 h-5 rounded-full text-xs bg-white text-primary-blue">
              {conversations.filter(c => !c.isRead).length}
            </span>
          {/if}
        </button>
      {/each}
    </div>
  </div>
  
  <!-- Content section -->
  <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden" 
       in:fade={{ delay: 200, duration: 300 }}>
    
    <!-- Loading state with skeletons -->
    {#if loading}
      <div class="divide-y divide-slate-100">
        {#each Array(skeletonCount) as _, i}
          <div class="p-4 animate-pulse">
            <div class="flex items-center space-x-4">
              <!-- Avatar skeleton -->
              <div class="rounded-full bg-slate-200 h-12 w-12 flex-shrink-0"></div>
              
              <!-- Content skeleton -->
              <div class="flex-1 space-y-2">
                <div class="h-4 bg-slate-200 rounded w-1/4"></div>
                <div class="h-3 bg-slate-200 rounded w-1/2"></div>
                <div class="h-3 bg-slate-200 rounded w-3/4"></div>
              </div>
              
              <!-- Time skeleton -->
              <div class="h-3 bg-slate-200 rounded w-16"></div>
            </div>
          </div>
        {/each}
      </div>
    
    <!-- Error state -->
    {:else if error}
      <Alert variant="error" class="m-6">
        <div class="flex flex-col items-center p-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-red-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p class="font-medium mb-2">{error}</p>
          <Button 
            variant="primary" 
            size="sm"
            on:click={() => loadConversations()}
          >
            Try Again
          </Button>
        </div>
      </Alert>
    
    <!-- Empty state -->
    {:else if filteredConversations.length === 0}
      <div class="p-12">
        <div class="flex flex-col items-center max-w-md mx-auto text-center">
          <div class="w-20 h-20 rounded-full bg-primary-blue/10 flex items-center justify-center mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-primary-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <h2 class="text-xl font-semibold text-text-dark mb-2">No messages found</h2>
          <p class="text-text-medium mb-6">
            {#if searchQuery}
              No messages match your search criteria. Try adjusting your search terms.
            {:else if activeFilter !== 'all'}
              You don't have any {activeFilter === 'unread' ? 'unread' : activeFilter} messages.
            {:else}
              You don't have any messages yet. Start a conversation with a seller or buyer.
            {/if}
          </p>
          <div class="flex flex-wrap gap-3 justify-center">
            {#if searchQuery || activeFilter !== 'all'}
              <Button 
                variant="outline" 
                size="sm"
                on:click={() => {
                  searchQuery = '';
                  activeFilter = 'all';
                  applyFilters();
                }}
              >
                Clear Filters
              </Button>
            {/if}
            
            <Button 
              variant="primary" 
              size="sm"
              on:click={() => isComposeOpen = true}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              New Message
            </Button>
          </div>
        </div>
      </div>
    
    <!-- Conversation list -->
    {:else}
      <div class="divide-y divide-slate-100">
        {#each filteredConversations as conversation, i (conversation.id)}
          <button 
            class="w-full text-left p-4 hover:bg-slate-50 transition-colors relative
                   {!conversation.isRead ? 'bg-blue-50/30' : ''}"
            on:click={() => selectConversation(conversation)}
            in:fly={{ y: 10, delay: i * 50, duration: 200, easing: quintOut }}
          >
            <!-- Unread indicator dot -->
            {#if !conversation.isRead}
              <div class="absolute left-0 top-1/2 transform -translate-y-1/2 w-1 h-8 bg-primary-blue rounded-r-full"></div>
            {/if}
            
            <div class="flex items-start space-x-4">
              <!-- Avatar -->
              <div class="flex-shrink-0">
                {#if conversation.otherParticipant?.avatar}
                  <img 
                    src={conversation.otherParticipant.avatar} 
                    alt={conversation.otherParticipant.name}
                    class="h-12 w-12 rounded-full object-cover border border-slate-200"
                  />
                {:else if conversation.is_support}
                  <div class="h-12 w-12 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 border border-emerald-200">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                  </div>
                {:else}
                  <div class="h-12 w-12 rounded-full bg-primary-blue/10 flex items-center justify-center text-primary-blue border border-primary-blue/20">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                {/if}
              </div>
              
              <!-- Conversation content -->
              <div class="flex-1 min-w-0">
                <!-- Sender and subject line -->
                <div class="flex items-center justify-between">
                  <h3 class="text-sm font-semibold text-text-dark truncate max-w-xs sm:max-w-sm
                             {!conversation.isRead ? 'font-bold' : ''}"
                  >
                    {conversation.otherParticipant?.name || 'Unknown'}
                    
                    {#if conversation.is_support}
                      <span class="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                        Support
                      </span>
                    {/if}
                  </h3>
                  
                  <!-- Timestamp -->
                  <span class="text-xs text-text-medium whitespace-nowrap">
                    {conversation.last_message_date ? formatTimeAgo(conversation.last_message_date) : 'No messages'}
                  </span>
                </div>
                
                <!-- Subject -->
                <p class="text-sm font-medium text-text-dark truncate">
                  {conversation.title}
                </p>
                
                <!-- Message preview -->
                <p class="text-sm text-text-medium truncate mt-0.5
                          {!conversation.isRead ? 'font-medium text-text-dark' : ''}">
                  {conversation.preview}
                </p>
              </div>
            </div>
          </button>
        {/each}
      </div>
    {/if}
  </div>
</div>

<!-- Compose new message modal -->
{#if isComposeOpen}
  <div 
    class="fixed inset-0 bg-slate-900/50 z-50 backdrop-blur-sm transition-opacity duration-300 flex items-center justify-center"
    on:click={() => isComposeOpen = false}
    in:fade={{ duration: 200 }}
  >
    <div 
      class="w-full max-w-lg bg-white rounded-xl shadow-xl overflow-hidden"
      on:click|stopPropagation
      in:fly={{ y: 20, duration: 300, easing: quintOut }}
    >
      <!-- Header -->
      <div class="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
        <h3 class="text-lg font-semibold text-text-dark">New Message</h3>
        <button 
          class="p-2 rounded-full hover:bg-slate-100 transition-colors"
          on:click={() => isComposeOpen = false}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <!-- Form content -->
      <div class="p-6">
        {#if newMessageError}
          <Alert variant="error" class="mb-4">{newMessageError}</Alert>
        {/if}
        
        <div class="space-y-4">
          <!-- Recipient -->
          <div>
            <label for="recipient" class="block text-sm font-medium text-text-dark mb-1">
              Recipient
            </label>
            <input
              type="text"
              id="recipient"
              bind:value={newMessageData.recipient}
              placeholder="Enter username, email or select from your contacts"
              class="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
            />
          </div>
          
          <!-- Subject -->
          <div>
            <label for="subject" class="block text-sm font-medium text-text-dark mb-1">
              Subject
            </label>
            <input
              type="text"
              id="subject"
              bind:value={newMessageData.subject}
              placeholder="Enter message subject"
              class="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
            />
          </div>
          
          <!-- Message content -->
          <div>
            <label for="message" class="block text-sm font-medium text-text-dark mb-1">
              Message
            </label>
            <textarea
              id="message"
              bind:value={newMessageData.message}
              rows="6"
              placeholder="Type your message here..."
              class="w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
            ></textarea>
          </div>
          
          <!-- Actions -->
          <div class="flex justify-end space-x-3 pt-4">
            <Button
              variant="outline"
              on:click={() => isComposeOpen = false}
            >
              Cancel
            </Button>
            
            <Button
              variant="primary"
              on:click={sendNewMessage}
              disabled={newMessageLoading}
              loading={newMessageLoading}
            >
              Send Message
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  /* Hide scrollbar but allow scrolling */
  .hide-scrollbar {
    -ms-overflow-style: none;  /* IE and Edge */
    scrollbar-width: none;  /* Firefox */
  }
  .hide-scrollbar::-webkit-scrollbar {
    display: none;  /* Chrome, Safari and Opera */
  }
  
  /* Animation for skeleton loading */
  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: .5;
    }
  }
  
  .animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
  
  /* Animation for loading spinner */
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
  
  .animate-spin {
    animation: spin 1s linear infinite;
  }
</style>