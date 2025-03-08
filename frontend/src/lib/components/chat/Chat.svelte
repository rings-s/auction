<!-- src/lib/components/chat/Chat.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { authStore } from '$lib/stores/authStore';
  import { createChatConnection } from '$lib/websocketService';
  import { api } from '$lib/api';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  
  // Props
  export let roomId;
  export let title = 'Chat';
  export let recipientId = null;
  export let auctionId = null;
  export let minimized = false;
  export let maxHeight = '400px';
  
  // Internal state
  let message = '';
  let messagesContainer;
  let loading = true;
  let errorMessage = '';
  let historyLoaded = false;
  
  // Get user from auth store
  $: user = $authStore.user || {};
  
  // Initialize WebSocket connection
  let chat;
  let messages = [];
  let status = 'connecting';
  
  // Format timestamp
  function formatTime(timestamp) {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  }
  
  // Format date for message groups
  function formatDate(timestamp) {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    return new Intl.DateTimeFormat('en-US', {
      weekday: 'long',
      month: 'short',
      day: 'numeric'
    }).format(date);
  }
  
  // Check if message is from the current user
  function isCurrentUser(messageUserId) {
    return messageUserId === user.id;
  }
  
  // Send a message
  function sendMessage() {
    if (!message.trim() || status !== 'connected') return;
    
    try {
      chat.sendMessage(message.trim(), user.id);
      message = '';
    } catch (error) {
      console.error('Error sending message:', error);
      errorMessage = 'Failed to send message. Please try again.';
    }
  }
  
  // Handle Enter key to send message
  function handleKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }
  
  // Fetch message history
  async function fetchMessageHistory() {
    if (!roomId || historyLoaded) return;
    
    try {
      loading = true;
      const response = await api.message.getHistory(roomId, {
        params: {
          page_size: 50
        }
      });
      
      // Format and add messages to the store
      const historicalMessages = response.results.map(msg => ({
        id: msg.id,
        message: msg.content,
        user_id: msg.sender.id,
        username: msg.sender.first_name || msg.sender.email.split('@')[0],
        timestamp: msg.timestamp,
        type: 'message',
        pending: false
      }));
      
      // Add historical messages to the messages array
      messages = [...historicalMessages, ...messages];
      historyLoaded = true;
    } catch (error) {
      console.error('Error fetching message history:', error);
      errorMessage = 'Failed to load message history.';
    } finally {
      loading = false;
    }
  }
  
  // Group messages by date and sender
  $: groupedMessages = groupMessagesByDateAndUser(messages);
  
  function groupMessagesByDateAndUser(messages) {
    const groups = [];
    let currentGroup = null;
    let currentDate = '';
    
    messages.forEach(msg => {
      // Skip messages with errors
      if (msg.error) return;
      
      const messageDate = formatDate(msg.timestamp);
      
      // Check if we need a new date group
      if (messageDate !== currentDate) {
        currentDate = messageDate;
        groups.push({
          type: 'date',
          date: messageDate
        });
      }
      
      // Add system messages directly
      if (msg.type === 'system') {
        groups.push({
          type: 'system',
          message: msg.message,
          event: msg.event,
          timestamp: msg.timestamp
        });
        return;
      }
      
      // Check if we need a new message group (different user or more than 5 minutes apart)
      const needsNewGroup = !currentGroup || 
                           currentGroup.user_id !== msg.user_id ||
                           currentGroup.type !== 'messages' ||
                           new Date(msg.timestamp) - new Date(currentGroup.messages[currentGroup.messages.length - 1].timestamp) > 5 * 60 * 1000;
      
      if (needsNewGroup) {
        currentGroup = {
          type: 'messages',
          user_id: msg.user_id,
          username: msg.username,
          is_current_user: isCurrentUser(msg.user_id),
          messages: [msg]
        };
        groups.push(currentGroup);
      } else {
        currentGroup.messages.push(msg);
      }
    });
    
    return groups;
  }
  
  // Scroll to bottom on new messages
  $: if (messages && messagesContainer) {
    setTimeout(() => {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 0);
  }
  
  // Initialize chat
  function initChat() {
    // Create a deterministic room ID if needed but none provided
    if (!roomId && recipientId && user.id) {
      // Sort IDs to ensure consistent room ID regardless of who initiates
      const ids = [user.id, recipientId].sort();
      roomId = `chat-${ids[0]}-${ids[1]}`;
      
      // Add auction info if this is about an auction
      if (auctionId) {
        roomId = `${roomId}-auction-${auctionId}`;
      }
    }
    
    if (roomId) {
      // Create WebSocket connection using the service
      chat = createChatConnection(roomId);
      
      // Subscribe to messages store
      const unsubscribeMessages = chat.messages.subscribe(value => {
        // Update messages
        messages = value;
      });
      
      // Subscribe to connection status
      const unsubscribeStatus = chat.status.subscribe(value => {
        status = value;
        if (value === 'connected' && !historyLoaded) {
          // Load message history once connected
          fetchMessageHistory();
        } else if (value === 'failed') {
          errorMessage = 'Connection failed. Please try refreshing the page.';
        }
      });
      
      // Cleanup function
      return () => {
        unsubscribeMessages();
        unsubscribeStatus();
      };
    }
  }
  
  // Manually retry connection
  function retryConnection() {
    errorMessage = '';
    if (chat) {
      chat.reconnect();
    } else {
      initChat();
    }
  }
  
  onMount(() => {
    const unsubscribe = initChat();
    return unsubscribe;
  });
  
  // Clean up on component destroy
  onDestroy(() => {
    if (chat) {
      chat.close();
    }
  });
  
  // Toggle chat minimize/maximize
  function toggleMinimized() {
    minimized = !minimized;
  }
</script>

<div class="bg-white rounded-lg shadow-lg overflow-hidden flex flex-col {minimized ? 'h-16' : 'h-auto'}">
<!-- Chat header -->
<div class="px-4 py-3 bg-indigo-600 text-white flex items-center justify-between cursor-pointer" on:click={toggleMinimized}>
  <h3 class="font-semibold">{title}</h3>
  <div class="flex items-center">
    <!-- Connection status indicator -->
    {#if status === 'connected'}
      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 mr-2">
        <span class="h-2 w-2 mr-1 bg-green-400 rounded-full animate-pulse"></span>
        Live
      </span>
    {:else if status === 'connecting'}
      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800 mr-2">
        <Spinner size="xs" class="mr-1" />
        Connecting
      </span>
    {:else if status === 'reconnecting'}
      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800 mr-2">
        <Spinner size="xs" class="mr-1" />
        Reconnecting...
      </span>
    {:else if status === 'failed'}
      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800 mr-2">
        <span class="h-2 w-2 mr-1 bg-red-400 rounded-full animate-pulse"></span>
        Connection Failed
        <button class="ml-1 underline text-red-700" on:click|stopPropagation={retryConnection}>
          Retry
        </button>
      </span>
    {:else}
      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800 mr-2">
        <span class="h-2 w-2 mr-1 bg-red-400 rounded-full animate-pulse"></span>
        Offline
      </span>
    {/if}
    
    <!-- Minimize/Maximize button -->
    <button type="button" class="p-1 hover:bg-indigo-500 rounded">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 transform {minimized ? 'rotate-180' : ''}" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
      </svg>
    </button>
  </div>
</div>

{#if !minimized}
  <!-- Messages container -->
  <div 
    class="flex-1 p-4 overflow-y-auto"
    style="max-height: {maxHeight};"
    bind:this={messagesContainer}
  >
    {#if loading && !historyLoaded}
      <div class="flex justify-center items-center h-32">
        <Spinner />
      </div>
    {:else if errorMessage}
      <div class="bg-red-50 p-4 rounded-md text-red-600 text-center">
        <p>{errorMessage}</p>
        <button 
          class="mt-2 text-sm underline" 
          on:click={() => {
            errorMessage = '';
            retryConnection();
          }}
        >
          Try Again
        </button>
      </div>
    {:else if messages.length === 0}
      <div class="flex flex-col items-center justify-center h-32 text-gray-500">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        <p>No messages yet. Start the conversation!</p>
      </div>
    {:else}
      <div class="space-y-4">
        {#each groupedMessages as group}
          {#if group.type === 'date'}
            <div class="text-center my-4">
              <span class="bg-gray-100 text-gray-500 text-xs px-2 py-1 rounded-full">
                {group.date}
              </span>
            </div>
          {:else if group.type === 'system'}
            <div class="text-center my-2">
              <span class="bg-gray-50 text-gray-500 text-xs italic px-3 py-1 rounded-full">
                {group.message}
              </span>
            </div>
          {:else if group.type === 'messages'}
            <div class="flex {group.is_current_user ? 'justify-end' : 'justify-start'}">
              <div class="{group.is_current_user ? 'bg-indigo-50 text-gray-800' : 'bg-gray-100 text-gray-800'} rounded-lg px-4 py-2 max-w-xs sm:max-w-md">
                {#if !group.is_current_user}
                  <div class="font-semibold text-indigo-600 text-sm mb-1">{group.username}</div>
                {/if}
                
                <div class="space-y-2">
                  {#each group.messages as msg}
                    <div class="{msg.pending ? 'opacity-70' : ''}">
                      <p class="break-words whitespace-pre-wrap text-sm">{msg.message}</p>
                      <div class="text-xs text-gray-500 mt-1 text-right flex items-center justify-end">
                        {formatTime(msg.timestamp)}
                        
                        {#if msg.pending}
                          <span class="ml-2">
                            <Spinner size="xs" />
                          </span>
                        {:else if msg.confirmed}
                          <span class="ml-2 text-green-500">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                            </svg>
                          </span>
                        {/if}
                      </div>
                    </div>
                  {/each}
                </div>
              </div>
            </div>
          {/if}
        {/each}
      </div>
    {/if}
  </div>
  
  <!-- Chat input -->
  <div class="border-t border-gray-200 p-4">
    {#if status === 'connected'}
      <div class="flex items-center space-x-2">
        <textarea
          bind:value={message}
          on:keydown={handleKeydown}
          placeholder="Type a message..."
          class="flex-1 py-2 px-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
          rows="2"
        ></textarea>
        <Button
          variant="primary"
          size="sm"
          disabled={!message.trim()}
          on:click={sendMessage}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
          </svg>
        </Button>
      </div>
    {:else}
      <div class="flex items-center justify-center space-x-2 text-gray-500 py-2">
        {#if status === 'connecting' || status === 'reconnecting'}
          <Spinner size="sm" />
          <span>{status === 'connecting' ? 'Connecting...' : 'Reconnecting...'}</span>
        {:else}
          <span>Connection lost</span>
          <Button variant="outline" size="sm" on:click={retryConnection}>
            Reconnect
          </Button>
        {/if}
      </div>
    {/if}
  </div>
{/if}
</div>

<style>
/* Animation for connection status indicators */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>