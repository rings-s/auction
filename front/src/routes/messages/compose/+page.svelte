<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { fade, slide, scale } from 'svelte/transition';
  import { t, locale } from '$lib/i18n/i18n'; // $locale will be auto-subscribed
  import { user } from '$lib/stores/user'; // $user (if needed, for auto-subscription)
  import { sendMessage, replyToMessage, getMessage } from '$lib/api/messages';
  import { toast } from '$lib/stores/toastStore';
  import Button from '$lib/components/ui/Button.svelte';


  let data;

  // State management
  let replyToId = data?.replyId || null; // Initialized from prop
  let originalMessage = $state(null);
  let loading = $state(false);
  let sending = $state(false);
  let error = $state(null);
  let showPriorityFilters = $state(false);
  
  // Form data
  let formData = $state({
    recipient_email: '',
    subject: '',
    body: '',
    priority: 'normal'
  });

  // Field validation state
  let touched = $state({
    recipient_email: false,
    subject: false,
    body: false
  });

  // Derived values
  let isRTL = $derived($locale === 'ar'); // $locale is a Svelte store, $ prefix enables auto-subscription
  let isReply = $derived(!!replyToId);
  
  // Form validation
  let validation = $derived((() => { // Using an IIFE to keep the logic clean
    const errors = {};
    
    if (!isReply && touched.recipient_email && !formData.recipient_email) {
      errors.recipient_email = $t('validation.recipientRequired');
    } else if (!isReply && touched.recipient_email && !isValidEmail(formData.recipient_email)) {
      errors.recipient_email = $t('validation.invalidEmail');
    }
    
    if (touched.subject && !formData.subject.trim()) {
      errors.subject = $t('validation.subjectRequired');
    } else if (touched.subject && formData.subject.length < 3) {
      errors.subject = $t('validation.subjectTooShort');
    }
    
    if (touched.body && !formData.body.trim()) {
      errors.body = $t('validation.messageRequired');
    } else if (touched.body && formData.body.length < 10) {
      errors.body = $t('validation.messageTooShort');
    }
    
    return errors;
  })());

  let isValid = $derived(
    Object.keys(validation).length === 0 && 
    (isReply || formData.recipient_email) && 
    formData.subject.trim() && // Added trim() for robustness
    formData.body.trim()   // Added trim() for robustness
  );

  // Priority options with modern design (remains the same)
  const priorityOptions = [
    { 
      value: 'low', 
      label: 'messages.priority.low',
      color: 'bg-slate-50 border-slate-200 text-slate-700 dark:bg-slate-900/20 dark:border-slate-700 dark:text-slate-300',
      icon: '○',
      iconColor: 'text-slate-600 dark:text-slate-400'
    },
    { 
      value: 'normal', 
      label: 'messages.priority.normal',
      color: 'bg-emerald-50 border-emerald-200 text-emerald-700 dark:bg-emerald-900/20 dark:border-emerald-700 dark:text-emerald-300',
      icon: '◐',
      iconColor: 'text-emerald-600 dark:text-emerald-400'
    },
    { 
      value: 'high', 
      label: 'messages.priority.high',
      color: 'bg-amber-50 border-amber-200 text-amber-700 dark:bg-amber-900/20 dark:border-amber-700 dark:text-amber-300',
      icon: '◑',
      iconColor: 'text-amber-600 dark:text-amber-400'
    },
    { 
      value: 'urgent', 
      label: 'messages.priority.urgent',
      color: 'bg-rose-50 border-rose-200 text-rose-700 dark:bg-rose-900/20 dark:border-rose-700 dark:text-rose-300',
      icon: '●',
      iconColor: 'text-rose-600 dark:text-rose-400'
    }
  ];
  
  // Toggle priority filters panel
  function togglePriorityFilters() {
    showPriorityFilters = !showPriorityFilters;
  }

  // Load original message if replying
  let initialLoadDone = false;
  $effect(() => {
    if (replyToId && !initialLoadDone) { // Ensure it only loads once for a given replyToId initially or if replyToId changes
      loadOriginalMessage();
      initialLoadDone = true; // Mark that initial load for this replyToId has been attempted
    } else if (!replyToId) {
      originalMessage = null; // Clear message if not a reply
      initialLoadDone = false; // Reset for potential future replyToId
    }
  });

  // Alternatively, if replyToId is set once on component initialization:
  /*
  onMount(() => {
    if (replyToId) {
      loadOriginalMessage();
    }
  });
  */
  
  async function loadOriginalMessage() {
    loading = true;
    error = null;
    
    try {
      const response = await getMessage(replyToId);
      originalMessage = response.data || response;
      
      if (originalMessage) {
        formData.subject = `Re: ${originalMessage.subject}`;
        // Ensure reactive update for formData if needed by re-assigning the object
        // or ensure components using formData.body are reactive to its direct change.
        // Direct property assignment is usually fine if formData is declared with `let`.
        formData.body = `\n\n---\n${$t('messages.originalMessage')}:\n${originalMessage.body}`;
      }
      
    } catch (err) {
      console.error('Error loading original message:', err);
      error = err.message || $t('error.fetchFailed');
      toast.error($t('messages.couldNotLoadReplyMessage'));
    } finally {
      loading = false;
    }
  }

  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  async function handleSubmit() {
    // Mark all fields as touched to show all errors
    touched = {
      recipient_email: true,
      subject: true,
      body: true
    };

    // Re-check isValid as `touched` has changed, which affects `validation`
    // Svelte's reactivity should handle this, but explicit check can be added if needed.
    if (!isValid || sending) return;

    sending = true;
    error = null;

    try {
      const messagePayload = {
        subject: formData.subject.trim(),
        body: formData.body.trim(),
        priority: formData.priority
      };

      let response;
      if (isReply && originalMessage) {
        response = await replyToMessage(originalMessage.id, {
          body: messagePayload.body, // Use trimmed body from payload
          parent_message: originalMessage.id // It's good practice to ensure this is the correct field name expected by API
        });
      } else {
        // This part of your logic implies that sending a new message (not a reply)
        // is not fully implemented for recipient handling yet.
        // For this conversion, I'll keep your existing logic.
        // If you were to implement it, you'd use formData.recipient_email here.
        // messagePayload.recipient_email = formData.recipient_email;
        // response = await sendMessage(messagePayload);
        toast.error($t('messages.directMessagingNotImplemented'));
        sending = false; // Reset sending state as we are returning early
        return;
      }

      toast.success($t('messages.messageSentSuccess'));
      goto('/messages');
      
    } catch (err) {
      console.error('Error sending message:', err);
      error = err.message || $t('messages.sendError');
      toast.error(error); // Display the specific error
    } finally {
      sending = false;
    }
  }

  function handleCancel() {
    goto('/messages');
  }

  function autoResize(event) {
    const textarea = event.target;
    textarea.style.height = 'auto'; // Reset height
    // Ensure scrollHeight is not excessively large, cap at 400px
    textarea.style.height = `${Math.min(textarea.scrollHeight, 400)}px`;
  }
</script>

<svelte:head>
  <title>{isReply ? $t('messages.reply') : $t('messages.compose')} | {$t('app.name')}</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
    <div class="mb-6">
      <Button
        size="small"
        on:click={handleCancel}
        class="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors mb-4"
      >
        <svg class="w-4 h-4 {isRTL ? 'ml-1.5' : 'mr-1.5'}" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={isRTL ? "M14 5l7 7m0 0l-7 7m7-7H3" : "M10 19l-7-7m0 0l7-7m-7 7h18"} />
        </svg>
        {$t('messages.backToMessages')}
      </Button>
      
      <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">
        {isReply ? $t('messages.replyToMessage') : $t('messages.composeNewMessage')}
      </h1>
    </div>

    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
      {#if loading && isReply} <div class="p-8 text-center">
          <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-700 mb-4">
            <div class="w-6 h-6 border-2 border-gray-300 dark:border-gray-500 border-t-primary-500 rounded-full animate-spin"></div>
          </div>
          <p class="text-sm text-gray-500 dark:text-gray-400">{$t('common.loading')}</p>
        </div>
        
      {:else if error && isReply && !originalMessage} <div class="p-8 text-center">
          <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/20 mb-4">
            <svg class="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p class="text-sm text-gray-900 dark:text-white font-medium mb-1">{$t('error.fetchFailed')}</p>
          <p class="text-sm text-gray-500 dark:text-gray-400">{error}</p>
          <Button
            onclick={handleCancel}
            variant="outline"
            size="sm"
            class="mt-4"
          >
            {$t('common.back')}
          </Button>
        </div>
        
      {:else}
        <form class="p-6 space-y-5" onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
          {#if isReply && originalMessage}
            <div class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 border border-gray-200 dark:border-gray-700" transition:slide>
              <div class="flex items-start gap-3">
                <div class="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                  <span class="text-xs font-medium text-gray-600 dark:text-gray-300">
                    {originalMessage.sender_info?.name?.[0]?.toUpperCase() || '?'}
                  </span>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900 dark:text-white">
                    {originalMessage.sender_info?.name || $t('common.unknown')}
                  </p>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                    {new Date(originalMessage.created_at).toLocaleString($locale)}
                  </p>
                  <div class="mt-2 text-sm text-gray-600 dark:text-gray-300 line-clamp-3">
                    {originalMessage.body}
                  </div>
                </div>
              </div>
            </div>
          {/if}

          {#if !isReply}
            <div>
              <label for="recipient" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                {$t('messages.to')}
                <span class="text-red-500">*</span>
              </label>
              <input
                id="recipient_email"
                type="email"
                bind:value={formData.recipient_email}
                onfocus={() => touched.recipient_email = true}
                placeholder={$t('messages.recipientEmailPlaceholder')}
                class="w-full px-3.5 py-2.5 text-sm border rounded-lg transition-colors
                  {(validation.recipient_email && touched.recipient_email)
                    ? 'border-red-300 focus:border-red-500 focus:ring-red-200'
                    : 'border-gray-300 focus:border-primary-500 focus:ring-primary-200'
                  }
                  dark:bg-gray-900 dark:border-gray-600 dark:text-white 
                  focus:ring-2 focus:ring-opacity-20 focus:outline-none"
                aria-invalid={!!(validation.recipient_email && touched.recipient_email)}
                aria-describedby={validation.recipient_email && touched.recipient_email ? "recipient-error" : undefined}
                disabled={isReply || sending}
              />
              {#if validation.recipient_email && touched.recipient_email}
                <p id="recipient-error" class="mt-1 text-xs text-red-600 dark:text-red-400" transition:slide>
                  {validation.recipient_email}
                </p>
              {/if}
            </div>
          {/if}

          <div>
            <label for="subject" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
              {$t('messages.subject')}
              <span class="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="subject"
              bind:value={formData.subject}
              onfocus={() => touched.subject = true}
              placeholder={$t('messages.subjectPlaceholder')}
              class="w-full px-3.5 py-2.5 text-sm border rounded-lg transition-colors
                {(validation.subject && touched.subject)
                  ? 'border-red-300 focus:border-red-500 focus:ring-red-200'
                  : 'border-gray-300 focus:border-primary-500 focus:ring-primary-200'
                }
                dark:bg-gray-900 dark:border-gray-600 dark:text-white 
                focus:ring-2 focus:ring-opacity-20 focus:outline-none"
              aria-invalid={!!(validation.subject && touched.subject)}
              aria-describedby={validation.subject && touched.subject ? "subject-error" : undefined}
            />
            {#if validation.subject && touched.subject}
              <p id="subject-error" class="mt-1 text-xs text-red-600 dark:text-red-400" transition:slide>
                {validation.subject}
              </p>
            {/if}
          </div>
          
          <div>
            <label id="priority-label" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
              {$t('messages.form.priority')}
              <span class="text-red-500">*</span>
            </label>
            
            <!-- Mobile Priority Toggle (xs, sm, md screens) -->
            <div class="md:hidden">
              <button 
                type="button" 
                class="priority-toggle w-full flex items-center justify-between px-3.5 py-2.5 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 transition-colors"
                aria-expanded={showPriorityFilters}
                aria-controls="priority-filters-panel"
                onclick={togglePriorityFilters}
              >
                <div class="flex items-center gap-2">
                  {#each priorityOptions as option}
                    {#if formData.priority === option.value}
                      <span class={`priority-icon text-lg leading-none ${option.iconColor}`}>{option.icon}</span>
                      <span class="priority-label">{$t(option.label)}</span>
                    {/if}
                  {/each}
                </div>
                <svg class="filter-icon w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="{showPriorityFilters ? 'M5 15l7-7 7 7' : 'M19 9l-7 7-7-7'}" />
                </svg>
              </button>
              
              <!-- Mobile Priority Panel -->
              {#if showPriorityFilters}
                <div 
                  id="priority-filters-panel"
                  class="priority-panel mt-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
                  role="radiogroup" 
                  aria-labelledby="priority-label"
                  transition:slide={{ duration: 300, easing: (t) => 1 - Math.pow(1 - t, 3) }}
                >
                  <div class="p-2 grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {#each priorityOptions as option}
                      <button
                        type="button"
                        role="radio"
                        aria-checked={formData.priority === option.value}
                        onclick={() => {
                          formData.priority = option.value;
                          // Close panel after selection on small screens
                          if (window.innerWidth < 640) {
                            showPriorityFilters = false;
                          }
                        }}
                        class="priority-option flex items-center justify-between px-3 py-2.5 text-sm rounded-lg border transition-all duration-200
                          {formData.priority === option.value ? option.color : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300'}
                          hover:bg-opacity-80 dark:hover:bg-opacity-80 focus:outline-none"
                      >
                        <div class="flex items-center gap-2">
                          <span class={`text-lg leading-none ${option.iconColor}`}>{option.icon}</span>
                          <span>{$t(option.label)}</span>
                        </div>
                        {#if formData.priority === option.value}
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                          </svg>
                        {/if}
                      </button>
                    {/each}
                  </div>
                </div>
              {/if}
            </div>
            
            <!-- Desktop Priority Options (lg+ screens) -->
            <div class="hidden md:flex flex-wrap gap-2.5">
              {#each priorityOptions as option}
                <button
                  type="button"
                  role="radio"
                  aria-checked={formData.priority === option.value}
                  onclick={() => formData.priority = option.value}
                  class="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-md border transition-colors
                    {formData.priority === option.value ? option.color : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300'}
                    hover:bg-opacity-80 dark:hover:bg-opacity-80 focus:outline-none"
                >
                  <span class="flex items-center gap-1.5">
                    <span class={`text-base leading-none ${option.iconColor}`}>{option.icon}</span>
                    <span>{$t(option.label)}</span>
                  </span>
                </button>
              {/each}
            </div>
          </div>

          <div>
            <label for="body" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
              {$t('messages.message')}
              <span class="text-red-500">*</span>
            </label>
            <textarea
              id="body"
              bind:value={formData.body}
              onfocus={() => touched.body = true}
              oninput={autoResize}
              placeholder={$t('messages.messagePlaceholder')}
              rows="6"
              class="w-full px-3.5 py-2.5 text-sm border rounded-lg transition-colors resize-none
                {(validation.body && touched.body)
                  ? 'border-red-300 focus:border-red-500 focus:ring-red-200'
                  : 'border-gray-300 focus:border-primary-500 focus:ring-primary-200'
                }
                dark:bg-gray-900 dark:border-gray-600 dark:text-white 
                focus:ring-2 focus:ring-opacity-20 focus:outline-none"
              aria-invalid={!!(validation.body && touched.body)}
              aria-describedby={validation.body && touched.body ? "body-error" : undefined}
            ></textarea>
            <div class="mt-1 flex items-center justify-between">
              {#if validation.body && touched.body}
                <p id="body-error" class="text-xs text-red-600 dark:text-red-400" transition:slide>
                  {validation.body}
                </p>
              {:else}
                <span></span> {/if}
              <span class="text-xs text-gray-500 dark:text-gray-400">
                {formData.body.length} / 2000
              </span>
            </div>
          </div>

          <!-- Added pt-3 for a bit more space -->
          <div class="flex flex-wrap justify-end gap-3 pt-3">
            <Button 
              variant="outline" 
              size="small" 
              on:click={handleCancel}
              type="button" 
              class="w-full sm:w-auto"
            >
              {$t('common.cancel')}
            </Button>
            
            <Button
              type="submit"
              variant="primary"
              size="small"
              disabled={!isValid || sending}
              loading={sending}
              class="w-full sm:w-auto"
            >
              {#if sending}
                <svg class="w-4 h-4 animate-spin {isRTL ? 'ml-2' : 'mr-2'}" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
                {$t('common.sending')}
              {:else}
                <svg class="w-4 h-4 {isRTL ? 'ml-2' : 'mr-2'}" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                </svg>
                {$t('messages.send')}
              {/if}
            </Button>
          </div>
        </form>
      {/if}
    </div>
  </div>
</div>

<style>
  .line-clamp-3 {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    line-clamp: 3; /* Standard property for modern browsers */
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  /* Add focus-visible styling for better accessibility with keyboard navigation */
  button[role="radio"]:focus-visible {
    outline: 2px solid var(--primary-color, #3b82f6); /* Use your primary color variable or a default */
    outline-offset: 2px;
  }
  input:focus-visible, textarea:focus-visible {
     outline: 2px solid var(--primary-color, #3b82f6);
     outline-offset: 1px;
  }
  
  /* Priority filter animations and styling */
  .priority-toggle {
    position: relative;
    transition: all 0.2s ease;
  }
  
  .priority-toggle:active {
    transform: scale(0.98);
  }
  
  .filter-icon {
    transition: transform 0.3s ease;
  }
  
  .priority-toggle[aria-expanded="true"] .filter-icon {
    transform: rotate(180deg);
  }
  
  .priority-panel {
    transform-origin: top center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  .priority-option {
    position: relative;
    overflow: hidden;
  }
  
  .priority-option:active {
    transform: translateY(1px);
  }
  
  .priority-option::after {
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
  
  .priority-option:active::after {
    opacity: 0.1;
    transform: translate(-50%, -50%) scale(1);
    transition: opacity 0s, transform 0s;
  }
  
  @media (prefers-reduced-motion: reduce) {
    .priority-panel, .filter-icon, .priority-option::after {
      transition: none !important;
    }
  }
</style>