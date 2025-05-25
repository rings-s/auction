<!-- src/lib/components/messages/ContactForm.svelte -->
<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { fade, slide, scale, fly } from 'svelte/transition';
  import { t, locale } from '$lib/i18n/i18n';
  import { user } from '$lib/stores/user';
  import { contactPropertyOwner } from '$lib/api/messages';
  import Button from '$lib/components/ui/Button.svelte';
  
  export let property = null;
  export let recipient = null;
  export let initialSubject = '';
  export let initialMessage = '';
  export let compact = false;
  
  const dispatch = createEventDispatcher();
  
  // Form state
  let formData = {
    subject: initialSubject || (property ? `${$t('messages.inquiryAbout')} ${property.title}` : ''),
    body: initialMessage || '',
    priority: 'normal'
  };
  
  let loading = false;
  let error = null;
  let success = false;
  let showFullForm = !compact;
  let fieldErrors = {};
  let touched = {};
  let mounted = false;
  
  // Form validation
  let validationState = {
    subject: { isValid: false, message: '' },
    body: { isValid: false, message: '' }
  };
  
  // Computed values
  $: isRTL = $locale === 'ar';
  $: characterCount = formData.body.length;
  $: maxCharacters = 2000;
  $: subjectLength = formData.subject.length;
  $: maxSubjectLength = 255;
  
  // Real-time validation
  $: {
    // Subject validation
    if (formData.subject.length === 0) {
      validationState.subject = { isValid: false, message: $t('validation.subjectRequired') };
    } else if (formData.subject.length < 5) {
      validationState.subject = { isValid: false, message: $t('validation.subjectTooShort') };
    } else if (formData.subject.length > maxSubjectLength) {
      validationState.subject = { isValid: false, message: $t('validation.subjectTooLong') };
    } else {
      validationState.subject = { isValid: true, message: '' };
    }
    
    // Body validation
    if (formData.body.length === 0) {
      validationState.body = { isValid: false, message: $t('validation.messageRequired') };
    } else if (formData.body.length < 10) {
      validationState.body = { isValid: false, message: $t('validation.messageTooShort') };
    } else if (formData.body.length > maxCharacters) {
      validationState.body = { isValid: false, message: $t('validation.messageTooLong') };
    } else {
      validationState.body = { isValid: true, message: '' };
    }
  }
  
  $: canSubmit = validationState.subject.isValid && 
                 validationState.body.isValid && 
                 !loading && 
                 $user;
  
  // Priority options with enhanced design
  const priorityOptions = [
    { 
      value: 'low', 
      label: 'messages.priority.low', 
      icon: '🔵',
      color: 'bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-900/20 dark:border-blue-800 dark:text-blue-300',
      activeColor: 'bg-blue-100 border-blue-400 text-blue-800 dark:bg-blue-900/40 dark:border-blue-600 dark:text-blue-200'
    },
    { 
      value: 'normal', 
      label: 'messages.priority.normal', 
      icon: '🟢',
      color: 'bg-green-50 border-green-200 text-green-700 dark:bg-green-900/20 dark:border-green-800 dark:text-green-300',
      activeColor: 'bg-green-100 border-green-400 text-green-800 dark:bg-green-900/40 dark:border-green-600 dark:text-green-200'
    },
    { 
      value: 'high', 
      label: 'messages.priority.high', 
      icon: '🟡',
      color: 'bg-yellow-50 border-yellow-200 text-yellow-700 dark:bg-yellow-900/20 dark:border-yellow-800 dark:text-yellow-300',
      activeColor: 'bg-yellow-100 border-yellow-400 text-yellow-800 dark:bg-yellow-900/40 dark:border-yellow-600 dark:text-yellow-200'
    },
    { 
      value: 'urgent', 
      label: 'messages.priority.urgent', 
      icon: '🔴',
      color: 'bg-red-50 border-red-200 text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300',
      activeColor: 'bg-red-100 border-red-400 text-red-800 dark:bg-red-900/40 dark:border-red-600 dark:text-red-200'
    }
  ];
  
  // Handle form submission with enhanced UX
  async function handleSubmit() {
    if (!canSubmit) return;
    
    try {
      loading = true;
      error = null;
      
      const messageData = {
        subject: formData.subject.trim(),
        body: formData.body.trim(),
        priority: formData.priority
      };
      
      let response;
      if (property) {
        response = await contactPropertyOwner(property.id, messageData);
      } else {
        throw new Error($t('messages.directMessagingNotAvailable'));
      }
      
      success = true;
      
      // Auto-hide success message after 5 seconds
      setTimeout(() => {
        success = false;
      }, 5000);
      
      // Reset form after success
      setTimeout(() => {
        formData = {
          subject: '',
          body: '',
          priority: 'normal'
        };
        touched = {};
      }, 1000);
      
      dispatch('success', {
        message: $t('messages.messageSentSuccess'),
        data: response
      });
      
    } catch (err) {
      console.error('Error sending message:', err);
      error = err.message || $t('messages.sendError');
      dispatch('error', { error: err.message });
    } finally {
      loading = false;
    }
  }
  
  // Enhanced input handling with immediate feedback
  function handleInput(field, value) {
    formData[field] = value;
    touched[field] = true;
    if (error) error = null;
    if (success) success = false;
  }
  
  // Toggle form with smooth animation
  function toggleFullForm() {
    showFullForm = !showFullForm;
  }
  
  // Focus management
  function focusFirstInput() {
    if (mounted) {
      const firstInput = document.querySelector('#contact-subject');
      if (firstInput) firstInput.focus();
    }
  }
  
  // Auto-resize textarea
  function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
  }
  
  onMount(() => {
    mounted = true;
  });
</script>

<div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden backdrop-blur-sm">
  <!-- Enhanced Header with Property Context -->
  <div class="bg-gradient-to-r from-primary-50 via-white to-secondary-50 dark:from-primary-900/10 dark:via-gray-800 dark:to-secondary-900/10 px-6 py-5">
    <div class="flex items-start justify-between">
      <div class="flex-1">
        <div class="flex items-center gap-3 mb-2">
          <div class="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-xl">
            <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">
              {$t('property.contactOwner')}
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              {$t('messages.getInTouch')}
            </p>
          </div>
        </div>
        
        {#if property}
          <div class="bg-white/50 dark:bg-gray-700/30 rounded-lg p-3 border border-gray-200/50 dark:border-gray-600/50">
            <div class="flex items-center gap-3">
              {#if property.images && property.images[0]}
                <img 
                  src={property.images[0].image_url} 
                  alt={property.title}
                  class="w-12 h-12 rounded-lg object-cover"
                />
              {:else}
                <div class="w-12 h-12 bg-gray-200 dark:bg-gray-600 rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                </div>
              {/if}
              <div class="flex-1 min-w-0">
                <p class="font-semibold text-gray-900 dark:text-white truncate">
                  {property.title}
                </p>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  {property.location?.city || ''} • ${property.market_value?.toLocaleString() || 'N/A'}
                </p>
              </div>
            </div>
          </div>
        {/if}
      </div>
      
      {#if compact}
        <button
          type="button"
          on:click={toggleFullForm}
          class="p-2 rounded-xl hover:bg-white/60 dark:hover:bg-gray-700/50 transition-all duration-200 group"
          aria-label={showFullForm ? $t('common.collapse') : $t('common.expand')}
        >
          <svg 
            class="w-5 h-5 text-gray-600 dark:text-gray-400 transition-all duration-300 group-hover:text-primary-600 dark:group-hover:text-primary-400 {showFullForm ? 'rotate-180' : ''}" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      {/if}
    </div>
  </div>
  
  <!-- Enhanced Form Content -->
  {#if showFullForm}
    <div class="p-6" transition:slide={{ duration: 400, easing: (t) => t * (2 - t) }}>
      {#if !$user}
        <!-- Enhanced Login Required State -->
        <div class="text-center py-12" in:fade={{ duration: 300 }}>
          <div class="mx-auto w-20 h-20 bg-primary-100 dark:bg-primary-900/30 rounded-2xl flex items-center justify-center mb-6">
            <svg class="h-10 w-10 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h4 class="text-2xl font-bold text-gray-900 dark:text-white mb-3">
            {$t('messages.loginRequired')}
          </h4>
          <p class="text-gray-600 dark:text-gray-400 mb-8 max-w-md mx-auto">
            {$t('property.loginToContact')}
          </p>
          <div class="flex flex-col sm:flex-row gap-3 justify-center">
            <Button
              href="/login"
              variant="primary"
              size="large"
              rounded="full"
              class="inline-flex items-center shadow-lg hover:shadow-xl transition-all"
            >
              <svg class="w-5 h-5 {isRTL ? 'ml-3' : 'mr-3'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
              </svg>
              {$t('nav.login')}
            </Button>
            <Button
              href="/register"
              variant="outline"
              size="large"
              rounded="full"
              class="inline-flex items-center"
            >
              <svg class="w-5 h-5 {isRTL ? 'ml-3' : 'mr-3'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
              </svg>
              {$t('nav.register')}
            </Button>
          </div>
        </div>
        
      {:else}
        <!-- Enhanced Message Form -->
        <form on:submit|preventDefault={handleSubmit} class="space-y-8">
          <!-- Enhanced Success/Error Messages -->
          {#if success}
            <div 
              class="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-l-4 border-green-400 rounded-xl p-6 shadow-sm"
              transition:fly={{ y: -20, duration: 400 }}
            >
              <div class="flex items-start">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-green-100 dark:bg-green-900/40 rounded-full flex items-center justify-center">
                    <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <div class="{isRTL ? 'mr-4' : 'ml-4'}">
                  <h4 class="text-lg font-semibold text-green-800 dark:text-green-200 mb-1">
                    {$t('messages.messageSentSuccess')}
                  </h4>
                  <p class="text-green-700 dark:text-green-300">
                    {$t('messages.messageDelivered')}
                  </p>
                </div>
              </div>
            </div>
          {/if}
          
          {#if error}
            <div 
              class="bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 border-l-4 border-red-400 rounded-xl p-6 shadow-sm"
              transition:fly={{ y: -20, duration: 400 }}
            >
              <div class="flex items-start">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-red-100 dark:bg-red-900/40 rounded-full flex items-center justify-center">
                    <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                </div>
                <div class="{isRTL ? 'mr-4' : 'ml-4'}">
                  <h4 class="text-lg font-semibold text-red-800 dark:text-red-200 mb-1">
                    {$t('error.sendingFailed')}
                  </h4>
                  <p class="text-red-700 dark:text-red-300">{error}</p>
                </div>
              </div>
            </div>
          {/if}
          
          <!-- Enhanced Sender Info -->
          <div class="bg-gradient-to-r from-gray-50 to-blue-50 dark:from-gray-800 dark:to-blue-900/20 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
            <div class="flex items-center">
              <div class="relative">
                <div class="w-14 h-14 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center text-white font-bold text-lg shadow-lg">
                  {$user.first_name?.charAt(0)}{$user.last_name?.charAt(0)}
                </div>
                <div class="absolute -bottom-1 -right-1 w-5 h-5 bg-green-400 rounded-full border-2 border-white dark:border-gray-800"></div>
              </div>
              <div class="{isRTL ? 'mr-4' : 'ml-4'} flex-1">
                <p class="text-lg font-bold text-gray-900 dark:text-white">
                  {$user.first_name} {$user.last_name}
                </p>
                <p class="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  {$user.email}
                </p>
              </div>
              <div class="text-xs bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 px-3 py-1 rounded-full font-medium">
                {$t('messages.sender')}
              </div>
            </div>
          </div>
          
          <!-- Enhanced Subject Field -->
          <div class="space-y-2">
            <label for="contact-subject" class="flex items-center justify-between text-sm font-semibold text-gray-700 dark:text-gray-300">
              <span class="flex items-center gap-2">
                {$t('messages.subject')}
                <span class="text-red-500 text-base">*</span>
              </span>
              <span class="text-xs text-gray-500 dark:text-gray-400">
                {subjectLength}/{maxSubjectLength}
              </span>
            </label>
            <div class="relative">
              <input
                id="contact-subject"
                type="text"
                bind:value={formData.subject}
                on:input={(e) => handleInput('subject', e.target.value)}
                on:focus={() => touched.subject = true}
                placeholder={$t('messages.subjectPlaceholder')}
                class="block w-full px-6 py-4 border-2 rounded-2xl shadow-sm transition-all duration-200 text-base
                  {validationState.subject.isValid && touched.subject
                    ? 'border-green-300 bg-green-50/30 dark:border-green-600 dark:bg-green-900/10 focus:border-green-400 focus:ring-green-200'
                    : !validationState.subject.isValid && touched.subject
                    ? 'border-red-300 bg-red-50/30 dark:border-red-600 dark:bg-red-900/10 focus:border-red-400 focus:ring-red-200'
                    : 'border-gray-300 dark:border-gray-600 focus:border-primary-400 focus:ring-primary-200'
                  }
                  dark:bg-gray-700 dark:text-white placeholder-gray-400 focus:ring-4 focus:ring-opacity-20"
                required
                maxlength={maxSubjectLength}
              />
              {#if validationState.subject.isValid && touched.subject}
                <div class="absolute top-1/2 transform -translate-y-1/2 {isRTL ? 'left-4' : 'right-4'}">
                  <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              {/if}
            </div>
            {#if !validationState.subject.isValid && touched.subject}
              <p class="text-sm text-red-600 dark:text-red-400 flex items-center gap-2" transition:slide={{ duration: 200 }}>
                <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                {validationState.subject.message}
              </p>
            {/if}
          </div>
          
          <!-- Enhanced Priority Selection -->
          <div class="space-y-3">
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300">
              {$t('messages.form.priority')}
              <span class="text-red-500 text-base {isRTL ? 'mr-1' : 'ml-1'}">*</span>
            </label>
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
              {#each priorityOptions as option (option.value)}
                <button
                  type="button"
                  class="relative p-4 rounded-2xl border-2 transition-all duration-300 text-sm font-medium group hover:scale-105 hover:shadow-lg {
                    formData.priority === option.value
                      ? option.activeColor + ' shadow-md transform scale-105'
                      : option.color + ' hover:shadow-md'
                  }"
                  on:click={() => handleInput('priority', option.value)}
                  in:scale={{ duration: 200, delay: priorityOptions.indexOf(option) * 50 }}
                >
                  <div class="text-center">
                    <span class="block text-2xl mb-2 group-hover:scale-110 transition-transform duration-200">{option.icon}</span>
                    <span class="block text-xs font-semibold">{$t(option.label)}</span>
                  </div>
                  {#if formData.priority === option.value}
                    <div class="absolute top-2 {isRTL ? 'left-2' : 'right-2'}" transition:scale={{ duration: 200 }}>
                      <svg class="w-4 h-4 text-current" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                  {/if}
                </button>
              {/each}
            </div>
          </div>
          
          <!-- Enhanced Message Body -->
          <div class="space-y-2">
            <label for="contact-message" class="flex items-center justify-between text-sm font-semibold text-gray-700 dark:text-gray-300">
              <span class="flex items-center gap-2">
                {$t('property.message')}
                <span class="text-red-500 text-base">*</span>
              </span>
              <span class="text-xs text-gray-500 dark:text-gray-400 {characterCount > maxCharacters * 0.9 ? 'text-orange-500' : ''}">
                {characterCount}/{maxCharacters}
              </span>
            </label>
            <div class="relative">
              <textarea
                id="contact-message"
                bind:value={formData.body}
                on:input={(e) => {
                  handleInput('body', e.target.value);
                  autoResize(e.target);
                }}
                on:focus={() => touched.body = true}
                placeholder={$t('property.messagePlaceholder')}
                rows="6"
                maxlength={maxCharacters}
                class="block w-full px-6 py-4 border-2 rounded-2xl shadow-sm transition-all duration-200 text-base resize-none
                  {validationState.body.isValid && touched.body
                    ? 'border-green-300 bg-green-50/30 dark:border-green-600 dark:bg-green-900/10 focus:border-green-400 focus:ring-green-200'
                    : !validationState.body.isValid && touched.body
                    ? 'border-red-300 bg-red-50/30 dark:border-red-600 dark:bg-red-900/10 focus:border-red-400 focus:ring-red-200'
                    : 'border-gray-300 dark:border-gray-600 focus:border-primary-400 focus:ring-primary-200'
                  }
                  dark:bg-gray-700 dark:text-white placeholder-gray-400 focus:ring-4 focus:ring-opacity-20"
                required
              ></textarea>
              {#if validationState.body.isValid && touched.body}
                <div class="absolute top-4 {isRTL ? 'left-4' : 'right-4'}">
                  <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              {/if}
            </div>
            {#if !validationState.body.isValid && touched.body}
              <p class="text-sm text-red-600 dark:text-red-400 flex items-center gap-2" transition:slide={{ duration: 200 }}>
                <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                {validationState.body.message}
              </p>
            {/if}
          </div>
          
          <!-- Enhanced Submit Section -->
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pt-6 border-t-2 border-gray-100 dark:border-gray-700">
            <div class="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2">
              <svg class="w-4 h-4 text-primary-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{$t('messages.messageDisclaimer')}</span>
            </div>
            
            <Button
              type="submit"
              variant="primary"
              size="large"
              disabled={!canSubmit}
              loading={loading}
              rounded="full"
              class="min-w-[160px] shadow-lg hover:shadow-xl transition-all duration-300 {canSubmit ? 'hover:scale-105' : ''}"
            >
              {#if loading}
                <svg class="w-5 h-5 {isRTL ? 'ml-3' : 'mr-3'} animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {$t('common.sending')}
              {:else}
                <svg class="w-5 h-5 {isRTL ? 'ml-3' : 'mr-3'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
                {$t('property.sendMessage')}
              {/if}
            </Button>
          </div>
        </form>
      {/if}
    </div>
  {/if}
</div>

<style>
  /* Enhanced animations */
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-4px); }
    75% { transform: translateX(4px); }
  }
  
  /* Auto-resize textarea */
  textarea {
    transition: height 0.2s ease;
  }
  
  /* Enhanced focus styles */
  input:focus,
  textarea:focus {
    transform: translateY(-1px);
  }
  
  /* Priority button animations */
  .priority-option:hover {
    animation: subtle-bounce 0.4s ease;
  }
  
  @keyframes subtle-bounce {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
  }
  
  /* Character counter color transitions */
  .character-counter {
    transition: color 0.3s ease;
  }
  
  /* Validation state transitions */
  .validation-enter {
    animation: slideDown 0.2s ease;
  }
  
  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-8px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  /* RTL-specific adjustments */
  :global(.rtl) .character-counter {
    left: 1rem;
    right: auto;
  }
  
  /* High contrast mode */
  @media (prefers-contrast: high) {
    input, textarea {
      border-width: 3px;
    }
  }
  
  /* Reduced motion */
  @media (prefers-reduced-motion: reduce) {
    * {
      animation: none !important;
      transition: none !important;
    }
  }
</style>