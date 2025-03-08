<!-- src/routes/messages/[id]/+page.svelte -->
<script>
  import { onMount, onDestroy, tick } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { fade, fly, slide } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import { isAuthenticated, user } from '$lib/stores/authStore';
  import { notificationStore } from '$lib/stores/notificationStore';
  import { formatDate, formatTimeAgo } from '$lib/utils/formatters';
  import { api } from '$lib/api';
  
  // UI Components
  import Button from '$lib/components/ui/Button.svelte';
  import IconButton from '$lib/components/ui/IconButton.svelte';
  import Avatar from '$lib/components/ui/Avatar.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import TextField from '$lib/components/ui/TextField.svelte';
  import EmptyState from '$lib/components/ui/EmptyState.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Tooltip from '$lib/components/ui/ToolTipNew.svelte';
  
  // Get conversation ID from URL
  $: conversationId = $page.params.id;
  
  // State
  let conversation = null;
  let messages = [];
  let loading = true;
  let error = null;
  let replyText = '';
  let sendingReply = false;
  let replyError = null;
  let messageEndRef;
  let searchQuery = '';
  let websocketConnection = null;
  let isLoadingMore = false;
  let hasMoreMessages = true;
  let currentPage = 1;
  let messagesPerPage = 20;
  
  // Attachment handling
  let attachments = [];
  let uploadingAttachment = false;
  let attachmentError = null;
  const MAX_ATTACHMENTS = 5;
  const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
  
  // Message actions
  let selectedMessageId = null;
  let showActionsFor = null;
  let showDeleteConfirm = false;
  let deletingMessage = false;
  
  // Get other participant details
  function getOtherParticipant(conv) {
    if (!conv || !conv.participants) return null;
    return conv.participants.find(p => p.id !== $user?.id) || null;
  }
  
  // Load conversation data
  async function loadConversation() {
    if (!$isAuthenticated) {
      goto('/login?redirect=/messages/' + conversationId);
      return;
    }
    
    try {
      loading = true;
      error = null;
      
      // API call to get conversation details
      const response = await api.messages.getConversation(conversationId);
      
      // Process conversation data
      conversation = {
        ...response,
        otherParticipant: getOtherParticipant(response),
        title: getConversationTitle(response),
      };
      
      // Load messages
      await loadMessages();
      
      // Mark conversation as read
      if (!conversation.is_read) {
        markAsRead();
      }
      
      loading = false;
      
      // Setup websocket connection
      setupWebsocket();
      
      // Scroll to bottom on initial load
      setTimeout(scrollToBottom, 100);
      
    } catch (err) {
      console.error('Error loading conversation:', err);
      error = err.message || 'Failed to load conversation';
      loading = false;
      notificationStore.error('Failed to load conversation');
    }
  }
  
  // Get conversation title
  function getConversationTitle(conv) {
    if (conv.auction) {
      return `RE: ${conv.auction.title || 'Auction'}`;
    } else if (conv.subject) {
      return conv.subject;
    } else {
      const participant = getOtherParticipant(conv);
      return `Conversation with ${participant?.name || 'Unknown'}`;
    }
  }
  
  // Load messages
  async function loadMessages(page = 1, append = false) {
    try {
      if (page === 1) {
        isLoadingMore = false;
      } else {
        isLoadingMore = true;
      }
      
      // API call to get messages
      const response = await api.messages.getMessages(conversationId, {
        page,
        page_size: messagesPerPage
      });
      
      // Update messages
      if (append) {
        messages = [...response.results.reverse(), ...messages];
      } else {
        messages = response.results.reverse();
      }
      
      // Check if there are more messages
      hasMoreMessages = response.next !== null;
      currentPage = page;
      
      isLoadingMore = false;
    } catch (err) {
      console.error('Error loading messages:', err);
      isLoadingMore = false;
    }
  }
  
  // Load more messages
  async function loadMoreMessages() {
    if (hasMoreMessages && !isLoadingMore) {
      await loadMessages(currentPage + 1, true);
    }
  }
  
  // Mark conversation as read
  async function markAsRead() {
    try {
      await api.messages.markAsRead(conversationId);
      if (conversation) {
        conversation.is_read = true;
      }
    } catch (err) {
      console.error('Error marking conversation as read:', err);
    }
  }
  
  // Send a reply
  async function sendReply() {
    if (!replyText.trim() && attachments.length === 0) {
      replyError = 'Please enter a message or add an attachment';
      return;
    }
    
    try {
      sendingReply = true;
      replyError = null;
      
      // Prepare form data if there are attachments
      const formData = new FormData();
      formData.append('content', replyText.trim());
      
      attachments.forEach((attachment, index) => {
        formData.append(`attachments[${index}]`, attachment.file);
      });
      
      // API call to send message
      const response = await api.messages.sendReply(conversationId, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      // Add new message to list
      const newMessage = {
        id: response.id,
        content: replyText,
        sender: $user,
        created_at: new Date().toISOString(),
        attachments: attachments.map(a => ({
          id: a.id,
          name: a.file.name,
          url: URL.createObjectURL(a.file),
          size: a.file.size,
          type: a.file.type
        })),
        is_read: true
      };
      
      messages = [...messages, newMessage];
      
      // Clear reply and attachments
      replyText = '';
      attachments = [];
      
      // Scroll to bottom
      setTimeout(scrollToBottom, 100);
      
    } catch (err) {
      console.error('Error sending reply:', err);
      replyError = err.message || 'Failed to send message';
      notificationStore.error('Failed to send message');
    } finally {
      sendingReply = false;
    }
  }
  
  // Handle file upload
  function handleFileSelect(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    
    // Check attachment limit
    if (attachments.length + files.length > MAX_ATTACHMENTS) {
      attachmentError = `You can only attach up to ${MAX_ATTACHMENTS} files`;
      notificationStore.error(attachmentError);
      return;
    }
    
    attachmentError = null;
    
    // Process each file
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      
      // Check file size
      if (file.size > MAX_FILE_SIZE) {
        attachmentError = `File ${file.name} exceeds the maximum size limit (5MB)`;
        notificationStore.error(attachmentError);
        continue;
      }
      
      // Add to attachments list
      attachments = [...attachments, {
        id: Math.random().toString(36).substring(2, 10),
        file: file,
        name: file.name,
        size: file.size,
        type: file.type,
        progress: 0
      }];
    }
    
    // Reset file input
    event.target.value = '';
  }
  
  // Remove attachment
  function removeAttachment(id) {
    attachments = attachments.filter(a => a.id !== id);
  }
  
  // Get file icon based on type
  function getFileIcon(type) {
    if (type.startsWith('image/')) {
      return 'image';
    } else if (type.startsWith('video/')) {
      return 'film';
    } else if (type.startsWith('audio/')) {
      return 'music';
    } else if (type.includes('pdf')) {
      return 'file-text';
    } else if (type.includes('document') || type.includes('word')) {
      return 'file-text';
    } else if (type.includes('spreadsheet') || type.includes('excel')) {
      return 'file-spreadsheet';
    } else if (type.includes('presentation') || type.includes('powerpoint')) {
      return 'file-presentation';
    } else {
      return 'file';
    }
  }
  
  // Format file size
  function formatFileSize(bytes) {
    if (bytes < 1024) {
      return `${bytes} B`;
    } else if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(0)} KB`;
    } else {
      return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    }
  }
  
  // Check if a message is from the current user
  function isFromCurrentUser(message) {
    return message.sender?.id === $user?.id;
  }
  
  // Setup websocket connection for real-time updates
  function setupWebsocket() {
    // Check if WebSocket API is supported
    if (!window.WebSocket) {
      console.warn('WebSockets not supported by this browser');
      return;
    }
    
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/api/ws/conversations/${conversationId}/`;
    
    try {
      websocketConnection = new WebSocket(wsUrl);
      
      websocketConnection.onopen = () => {
        console.log('WebSocket connection established');
      };
      
      websocketConnection.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'new_message') {
            // Add new message if it's not from current user
            if (data.message.sender?.id !== $user?.id) {
              messages = [...messages, data.message];
              
              // Scroll to bottom if already at bottom
              if (isScrolledToBottom()) {
                setTimeout(scrollToBottom, 100);
              } else {
                notificationStore.info('New message received');
              }
              
              // Mark as read
              markAsRead();
            }
          } else if (data.type === 'message_read') {
            // Update message read status
            messages = messages.map(m => {
              if (m.id === data.message_id) {
                return { ...m, is_read: true };
              }
              return m;
            });
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };
      
      websocketConnection.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      websocketConnection.onclose = () => {
        console.log('WebSocket connection closed');
        // Attempt to reconnect after delay
        setTimeout(setupWebsocket, 5000);
      };
    } catch (err) {
      console.error('Error setting up WebSocket:', err);
    }
  }
  
  // Check if user is at bottom of message list
  function isScrolledToBottom() {
    const container = document.querySelector('.messages-container');
    if (!container) return true;
    
    return Math.abs(container.scrollHeight - container.scrollTop - container.clientHeight) < 50;
  }
  
  // Scroll to bottom of message list
  function scrollToBottom() {
    if (messageEndRef) {
      messageEndRef.scrollIntoView({ behavior: 'smooth' });
    }
  }
  
  // Safely render message content with HTML
  function renderMessageContent(content) {
    // This would ideally include proper sanitization in a real app
    return content;
  }
  
  // Handle keydown in reply textarea
  function handleKeyDown(event) {
    // Ctrl+Enter to send
    if (event.ctrlKey && event.key === 'Enter') {
      event.preventDefault();
      sendReply();
    }
  }
  
  // Delete a message
  async function deleteMessage(messageId) {
    if (!messageId) return;
    
    try {
      deletingMessage = true;
      
      // API call to delete message
      await api.messages.deleteMessage(conversationId, messageId);
      
      // Remove message from list
      messages = messages.filter(m => m.id !== messageId);
      
      // Hide confirmation dialog
      showDeleteConfirm = false;
      selectedMessageId = null;
      
      notificationStore.success('Message deleted');
    } catch (err) {
      console.error('Error deleting message:', err);
      notificationStore.error('Failed to delete message');
    } finally {
      deletingMessage = false;
    }
  }
  
  // Export conversation
  async function exportConversation() {
    try {
      notificationStore.info('Preparing conversation export...');
      
      // API call to export conversation
      const response = await api.messages.exportConversation(conversationId);
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response], { type: 'text/html' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `conversation-${conversationId}.html`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      notificationStore.success('Conversation exported successfully');
    } catch (err) {
      console.error('Error exporting conversation:', err);
      notificationStore.error('Failed to export conversation');
    }
  }
  
  // Archive conversation
  async function archiveConversation() {
    try {
      // API call to archive conversation
      await api.messages.archiveConversation(conversationId);
      
      notificationStore.success('Conversation archived');
      goto('/messages');
    } catch (err) {
      console.error('Error archiving conversation:', err);
      notificationStore.error('Failed to archive conversation');
    }
  }
  
  // Format date for message grouping
  function formatMessageDate(date) {
    const messageDate = new Date(date);
    const today = new Date();
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    
    if (messageDate.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (messageDate.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return messageDate.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: messageDate.getFullYear() !== today.getFullYear() ? 'numeric' : undefined
      });
    }
  }
  
  // Group messages by date
  function getMessageGroups() {
    const groups = [];
    let currentDate = null;
    let currentGroup = null;
    
    messages.forEach(message => {
      const messageDate = formatMessageDate(message.created_at);
      
      if (messageDate !== currentDate) {
        currentDate = messageDate;
        currentGroup = { date: messageDate, messages: [] };
        groups.push(currentGroup);
      }
      
      currentGroup.messages.push(message);
    });
    
    return groups;
  }
  
  // Handle scroll for infinite loading
  function handleScroll(event) {
    const target = event.target;
    
    // Load more messages when scrolled near top
    if (target.scrollTop < 100 && hasMoreMessages && !isLoadingMore) {
      loadMoreMessages();
    }
  }
  
  // Initialize
  onMount(() => {
    loadConversation();
    
    // Event listener for clicks outside message actions
    document.addEventListener('click', (event) => {
      const actionsMenu = document.querySelector('.message-actions-menu');
      if (actionsMenu && !actionsMenu.contains(event.target) && !event.target.closest('.message-actions-trigger')) {
        showActionsFor = null;
      }
    });
    
    return () => {
      // Cleanup
      if (websocketConnection) {
        websocketConnection.close();
      }
    };
  });
  
  // Cleanup on destroy
  onDestroy(() => {
    if (websocketConnection) {
      websocketConnection.close();
    }
  });
  
  // Reactive declarations
  $: messageGroups = getMessageGroups();
</script>

<svelte:head>
  <title>{conversation ? conversation.title : 'Message'} | GUDIC</title>
  <meta name="description" content="Message conversation" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <!-- Loading state -->
  {#if loading}
    <div class="flex justify-center items-center py-16">
      <Spinner size="lg" />
    </div>
  
  <!-- Error state -->
  {:else if error}
    <Alert variant="error" class="mb-6">
      <div class="flex flex-col items-center p-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-red-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="font-medium mb-2">{error}</p>
        <div class="flex gap-3 mt-4">
          <Button 
            variant="outline" 
            on:click={() => goto('/messages')}
          >
            Back to Messages
          </Button>
          <Button 
            variant="primary"
            on:click={loadConversation}
          >
            Try Again
          </Button>
        </div>
      </div>
    </Alert>
  
  <!-- Content state -->
  {:else if conversation}
    <div class="grid grid-cols-1 gap-6 min-h-[75vh]">
      <!-- Conversation header -->
      <div 
        class="bg-white rounded-xl border border-slate-200 shadow-sm p-4 md:p-6"
        in:fly={{ y: -20, duration: 300 }}
      >
        <div class="flex flex-wrap gap-4 items-center justify-between">
          <!-- Back button -->
          <Button 
            variant="ghost" 
            size="sm"
            href="/messages"
            class="flex items-center text-text-medium hover:text-text-dark"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Messages
          </Button>
          
          <!-- Conversation actions -->
          <div class="flex items-center gap-2">
            <div class="relative">
              <IconButton
                icon="more-vertical"
                variant="ghost"
                size="sm"
                tooltipText="More actions"
                on:click={() => showActionsFor = 'conversation'}
              />
              
              {#if showActionsFor === 'conversation'}
                <div 
                  class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10 border border-slate-200"
                  in:fly={{ y: 5, duration: 200 }}
                >
                  <button 
                    class="flex w-full items-center px-4 py-2 text-sm text-text-medium hover:bg-slate-50 hover:text-text-dark"
                    on:click={exportConversation}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Export Conversation
                  </button>
                  <button 
                    class="flex w-full items-center px-4 py-2 text-sm text-text-medium hover:bg-slate-50 hover:text-text-dark"
                    on:click={archiveConversation}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                    </svg>
                    Archive Conversation
                  </button>
                  <button 
                    class="flex w-full items-center px-4 py-2 text-sm text-red-500 hover:bg-red-50"
                    on:click={() => {
                      showDeleteConfirm = true;
                      showActionsFor = null;
                    }}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    Delete Conversation
                  </button>
                </div>
              {/if}
            </div>
          </div>
        </div>
        
        <div class="flex flex-col md:flex-row items-start md:items-center gap-4 mt-4">
          <!-- Participant avatar -->
          <div class="flex-shrink-0">
            {#if conversation.otherParticipant?.avatar}
              <Avatar 
                src={conversation.otherParticipant.avatar} 
                alt={conversation.otherParticipant.name} 
                size="lg"
                status={conversation.otherParticipant.is_online ? 'online' : 'offline'}
              />
            {:else if conversation.is_support}
              <Avatar 
                variant="solid"
                backgroundColor="bg-emerald-600"
                initials="SP"
                size="lg"
                alt="Support"
              />
            {:else}
              <Avatar 
                initials={conversation.otherParticipant?.name?.charAt(0) || '?'}
                size="lg"
                alt={conversation.otherParticipant?.name || 'User'}
              />
            {/if}
          </div>
          
          <div class="flex-1 overflow-hidden">
            <!-- Conversation title -->
            <h1 class="text-xl font-semibold text-text-dark mb-1 truncate">
              {conversation.title}
            </h1>
            
            <!-- Participant info -->
            <div class="flex flex-wrap items-center gap-2">
              <span class="text-text-medium">
                {#if conversation.is_support}
                  GUDIC Support
                {:else}
                  {conversation.otherParticipant?.name || 'Unknown User'}
                {/if}
              </span>
              
              {#if conversation.is_support}
                <Badge variant="success" size="sm">Support</Badge>
              {/if}
              
              {#if conversation.auction}
                <Badge variant="primary" size="sm">
                  <a href="/auctions/{conversation.auction.id}" class="hover:underline">
                    Related Auction
                  </a>
                </Badge>
              {/if}
            </div>
          </div>
        </div>
      </div>
      
      <!-- Messages section -->
      <div 
        class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col min-h-[500px]"
        in:fade={{ delay: 200, duration: 300 }}
      >
        <!-- Messages container with infinite scroll -->
        <div 
          class="messages-container flex-1 overflow-y-auto p-4 md:p-6 bg-neutral-50/50"
          on:scroll={handleScroll}
        >
          <!-- Loading more indicator -->
          {#if isLoadingMore}
            <div class="flex justify-center py-4" in:fade>
              <Spinner size="sm" />
            </div>
          {/if}
          
          <!-- Empty state -->
          {#if !isLoadingMore && messages.length === 0}
            <div class="h-full flex items-center justify-center py-10">
              <EmptyState
                title="No messages yet"
                description="Start the conversation by sending a message below."
                icon="message-circle"
                iconColor="text-primary-blue"
                size="sm"
              />
            </div>
          {:else}
            <!-- Message groups by date -->
            {#each messageGroups as group}
              <!-- Date separator -->
              <div class="flex justify-center my-4">
                <div class="bg-primary-blue/10 text-primary-blue text-xs font-medium px-3 py-1 rounded-full">
                  {group.date}
                </div>
              </div>
              
              <!-- Messages -->
              {#each group.messages as message (message.id)}
                <div 
                  class="mb-4 {isFromCurrentUser(message) ? 'ml-12 sm:ml-24' : 'mr-12 sm:mr-24'}"
                  in:fly={{ y: 10, duration: 200 }}
                >
                  <div class="flex {isFromCurrentUser(message) ? 'justify-end' : 'justify-start'}">
                    <div class="relative group">
                      <!-- Message container -->
                      <div 
                        class="relative p-3 rounded-xl shadow-sm break-words
                               {isFromCurrentUser(message) 
                                ? 'bg-primary-blue/10 text-text-dark ml-2'
                                : 'bg-white border border-slate-200 mr-2'}"
                      >
                        <!-- Message sender avatar (for non-user messages) -->
                        {#if !isFromCurrentUser(message)}
                          <div class="absolute -left-10 top-0">
                            <Avatar 
                              src={message.sender?.avatar} 
                              initials={message.sender?.name?.charAt(0) || '?'}
                              alt={message.sender?.name || 'User'}
                              size="sm"
                            />
                          </div>
                        {/if}
                        
                        <!-- Message content -->
                        <div class="text-sm">
                          {#if message.content}
                            <div class="prose prose-sm max-w-none">
                              {@html renderMessageContent(message.content)}
                            </div>
                          {/if}
                          
                          <!-- Attachments -->
                          {#if message.attachments && message.attachments.length > 0}
                            <div class="mt-2 space-y-2">
                              {#each message.attachments as attachment}
                                <div class="bg-neutral-50 rounded-md p-2 border border-slate-200 flex items-center">
                                  <div class="flex-shrink-0 w-8 h-8 rounded-md bg-primary-blue/10 text-primary-blue flex items-center justify-center mr-2">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                    </svg>
                                  </div>
                                  <div class="flex-1 min-w-0">
                                    <div class="text-xs font-medium text-text-dark truncate">
                                      {attachment.name}
                                    </div>
                                    <div class="text-xs text-text-light">
                                      {formatFileSize(attachment.size)}
                                    </div>
                                  </div>
                                  <a 
                                    href={attachment.url}
                                    download={attachment.name}
                                    class="ml-2 p-1 rounded-md hover:bg-neutral-200 text-text-medium"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                  >
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                    </svg>
                                  </a>
                                </div>
                              {/each}
                            </div>
                          {/if}
                        </div>
                        
                        <!-- Message timestamp and status -->
                        <div class="mt-1 flex items-center justify-end gap-1">
                          <span class="text-xs text-text-light">
                            {formatTimeAgo(message.created_at)}
                          </span>
                          
                          {#if isFromCurrentUser(message)}
                            {#if message.is_read}
                              <span class="text-primary-blue">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                                </svg>
                              </span>
                            {:else}
                              <span class="text-text-light">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" />
                                </svg>
                              </span>
                            {/if}
                          {/if}
                        </div>
                        
                        <!-- Message actions -->
                        <div class="absolute {isFromCurrentUser(message) ? 'left-0' : 'right-0'} -top-2 transform {isFromCurrentUser(message) ? '-translate-x-full -translate-y-1/2 -left-2' : 'translate-x-full -translate-y-1/2 -right-2'} opacity-0 group-hover:opacity-100 transition-opacity">
                          <div class="relative">
                            <button 
                              class="message-actions-trigger p-1 rounded-full bg-white border border-slate-200 shadow-sm hover:bg-neutral-50 text-text-medium"
                              on:click|stopPropagation={() => showActionsFor = message.id}
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                              </svg>
                            </button>
                            
                            {#if showActionsFor === message.id}
                              <div 
                                class="message-actions-menu absolute {isFromCurrentUser(message) ? 'left-0' : 'right-0'} top-6 w-32 bg-white rounded-md shadow-lg py-1 z-10 border border-slate-200"
                                in:fly={{ y: 5, duration: 200 }}
                              >
                                <button 
                                  class="flex w-full items-center px-3 py-1 text-xs text-text-medium hover:bg-slate-50 hover:text-text-dark"
                                  on:click={() => {
                                    // Copy message text
                                    navigator.clipboard.writeText(message.content);
                                    notificationStore.success('Message copied to clipboard');
                                    showActionsFor = null;
                                  }}
                                >
                                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                  </svg>
                                  Copy
                                </button>
                                
                                {#if isFromCurrentUser(message)}
                                  <button 
                                    class="flex w-full items-center px-3 py-1 text-xs text-red-500 hover:bg-red-50"
                                    on:click={() => {
                                      selectedMessageId = message.id;
                                      showDeleteConfirm = true;
                                      showActionsFor = null;
                                    }}
                                  >
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                    Delete
                                  </button>
                                {/if}
                              </div>
                            {/if}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              {/each}
            {/each}
          {/if}
          
          <!-- Anchor for scrolling to bottom -->
          <div bind:this={messageEndRef}></div>
        </div>
        
        <!-- Compose message section -->
        <div class="border-t border-slate-200 p-4">
          {#if replyError}
            <Alert variant="error" class="mb-4">{replyError}</Alert>
          {/if}
          
          <!-- Attachments preview -->
          {#if attachments.length > 0}
            <div class="mb-4 flex flex-wrap gap-2">
              {#each attachments as attachment (attachment.id)}
                <div 
                  class="bg-neutral-50 rounded-md p-2 border border-slate-200 flex items-center"
                  in:slide={{ duration: 200 }}
                >
                  <div class="flex-shrink-0 w-6 h-6 rounded-md bg-primary-blue/10 text-primary-blue flex items-center justify-center mr-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                    </svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="text-xs font-medium text-text-dark truncate max-w-[150px]">
                      {attachment.name}
                    </div>
                    <div class="text-xs text-text-light">
                      {formatFileSize(attachment.size)}
                    </div>
                  </div>
                  <button 
                    class="ml-2 p-1 rounded-md hover:bg-neutral-200 text-text-medium"
                    on:click={() => removeAttachment(attachment.id)}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              {/each}
            </div>
          {/if}
          
          <div class="flex items-start gap-2">
            <!-- Message input -->
            <div class="flex-1">
              <TextField
                multiline={true}
                rows={3}
                placeholder="Type your message here..."
                bind:value={replyText}
                on:keydown={handleKeyDown}
                variant="filled"
                resize={true}
                helperText="Press Ctrl+Enter to send"
              />
            </div>
            
            <div class="flex flex-col gap-2">
              <!-- Attach file button -->
              <div class="relative">
                <input 
                  type="file" 
                  id="attach-file" 
                  class="sr-only" 
                  multiple 
                  on:change={handleFileSelect}
                />
                <Tooltip text="Attach files" position="top">
                  <label 
                    for="attach-file"
                    class="inline-flex items-center justify-center h-10 w-10 rounded-full bg-primary-blue/10 text-primary-blue hover:bg-primary-blue/20 transition-colors cursor-pointer"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                    </svg>
                  </label>
                </Tooltip>
              </div>
              
              <!-- Send button -->
              <Button
                variant="primary"
                on:click={sendReply}
                disabled={sendingReply || (!replyText.trim() && attachments.length === 0)}
                loading={sendingReply}
                class="h-10 w-10 p-0 rounded-full"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>

<!-- Delete confirmation modal -->
{#if showDeleteConfirm}
  <div 
    class="fixed inset-0 bg-slate-900/50 z-50 backdrop-blur-sm transition-opacity duration-300 flex items-center justify-center"
    on:click={() => showDeleteConfirm = false}
    in:fade={{ duration: 200 }}
  >
    <div 
      class="w-full max-w-md bg-white rounded-xl shadow-xl overflow-hidden"
      on:click|stopPropagation
      in:fly={{ y: 20, duration: 300, easing: quintOut }}
    >
      <!-- Header -->
      <div class="px-6 py-4 border-b border-slate-200 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
        <h3 class="text-lg font-semibold text-text-dark">Confirm {selectedMessageId ? 'Message' : 'Conversation'} Deletion</h3>
      </div>
      
      <!-- Content -->
      <div class="p-6">
        <div class="mb-6">
          <p class="text-text-dark mb-2">
            Are you sure you want to delete this {selectedMessageId ? 'message' : 'conversation'}?
          </p>
          <p class="text-text-medium text-sm">
            This action cannot be undone.
          </p>
        </div>
        
        <!-- Actions -->
        <div class="flex justify-end space-x-3">
          <Button
            variant="outline"
            size="sm"
            on:click={() => {
              showDeleteConfirm = false;
              selectedMessageId = null;
            }}
            disabled={deletingMessage}
          >
            Cancel
          </Button>
          
          <Button
            variant="error"
            size="sm"
            on:click={() => selectedMessageId ? deleteMessage(selectedMessageId) : deleteConversation()}
            loading={deletingMessage}
          >
            Delete
          </Button>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  /* Hide scrollbar but allow scrolling */
  .messages-container {
    scrollbar-width: thin;
    scrollbar-color: rgba(203, 213, 225, 0.5) transparent;
  }
  
  .messages-container::-webkit-scrollbar {
    width: 6px;
  }
  
  .messages-container::-webkit-scrollbar-track {
    background: transparent;
  }
  
  .messages-container::-webkit-scrollbar-thumb {
    background-color: rgba(203, 213, 225, 0.5);
    border-radius: 3px;
  }
  
  /* Message bubble styles */
  .prose p {
    margin-top: 0.5em;
    margin-bottom: 0.5em;
  }
  
  .prose p:first-child {
    margin-top: 0;
  }
  
  .prose p:last-child {
    margin-bottom: 0;
  }
</style>