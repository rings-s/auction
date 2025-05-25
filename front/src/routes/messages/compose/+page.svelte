<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores'; // page store gives access to URL params if not using +page.js's data
    import { t } from '$lib/i18n/i18n';
    import ContactForm from '$lib/components/messages/ContactForm.svelte';
    import { goto } from '$app/navigation';
    import { api } from '$lib/utils/api';
    import { toast } from '$lib/stores/toastStore'; // For user feedback
  
    export let data; // This will receive props from the load function in +page.js
  
    let replyToId = null;
    let replyToMessage = null;
    let loading = true; // Assume loading until data is fetched or determined not needed

    $: pageTitle = replyToId 
      ? `${$t('messages.replyToMessage')} | ${$t('app.name')}` 
      : `${$t('messages.composeNewMessage')} | ${$t('app.name')}`;

    onMount(async () => {
      if (data && data.replyId) {
        replyToId = parseInt(data.replyId, 10);
        if (isNaN(replyToId)) {
          console.error('Invalid replyId:', data.replyId);
          toast.error($t('messages.invalidReplyId'));
          loading = false;
          return;
        }
        console.log('Fetching message with replyToId:', replyToId);
        const { data: messageData, error: apiError } = await api.get(`/api/messages/${replyToId}/`);

        if (apiError) {
          console.error('API Error fetching message details. Status:', apiError.status, 'Message:', apiError.message, 'Full error object:', apiError);
          // Check if the error message from api.js already includes "Not Found" or similar
          if (apiError.status === 404) { // Specifically check for 404 status
            toast.error($t('messages.replyMessageNotFound'));
          } else if (apiError.status === 403) { // Specifically check for 403 status
            toast.error($t('messages.replyMessageForbidden'));
          } else {
            toast.error(apiError.message || $t('messages.errorFetchingReplyDetails'));
          }
          replyToMessage = null; // Ensure it's null on error
        } else {
          replyToMessage = messageData;
        }
        loading = false; // Set loading to false after the API call is handled
      } else {
        // Not a reply, or replyId is missing
        loading = false;
      }
    });
  
    function handleCancel() {
      goto('/messages');
    }
  </script>
  
  <svelte:head>
    <title>{pageTitle}</title>
  </svelte:head>
  
  <div class="container mx-auto px-4 py-8">
    <div class="max-w-3xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
          {#if replyToId && replyToMessage}{$t('messages.replyingToSubject', { subject: replyToMessage.subject })}{:else if replyToId}{$t('messages.replyToMessage')}{:else}{$t('messages.composeNewMessage')}{/if}
        </h1>
        <button
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 dark:text-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600"
          on:click={handleCancel}
          aria-label={$t('common.cancel')}
        >
          {$t('common.cancel')}
        </button>
      </div>
  
      {#if loading}
        <div class="flex justify-center items-center h-40">
          <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-500"></div>
          <p class="ml-3 text-gray-700 dark:text-gray-300">{$t('common.loadingDetails')}</p>
        </div>
      {:else}
        {#if replyToId && !replyToMessage && !loading}
          <div class="p-4 mb-4 text-sm text-red-700 bg-red-100 rounded-lg dark:bg-red-200 dark:text-red-800" role="alert">
            {$t('messages.couldNotLoadReplyMessage')}
          </div>
        {/if}
  
        {#if replyToMessage}
          <div class="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <h3 class="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-2">
              {$t('messages.replyingTo')}:
            </h3>
            <div class="font-medium text-gray-900 dark:text-white mb-1">
              <strong>{$t('messages.subject')}:</strong> {replyToMessage.subject}
            </div>
            {#if replyToMessage.sender}
            <p class="text-sm text-gray-600 dark:text-gray-300 mb-1">
              <strong>{$t('messages.from')}:</strong> {replyToMessage.sender.username || $t('common.unknownSender')}
            </p>
            {/if}
            <div class="text-sm text-gray-700 dark:text-gray-300 prose prose-sm dark:prose-invert max-w-none">
              <p class="font-semibold">{$t('messages.originalMessage')}:</p>
              <blockquote class="border-l-4 border-gray-300 dark:border-gray-600 pl-4 italic">
                {@html replyToMessage.content.substring(0, 300)}
                {#if replyToMessage.content.length > 300}...{/if}
              </blockquote>
            </div>
          </div>
        {/if}
  
        <ContactForm
          initialSubject={replyToMessage ? `Re: ${replyToMessage.subject}` : ''}
          initialRecipientId={replyToMessage && replyToMessage.sender ? replyToMessage.sender.id : null}
          replyToId={replyToId}
          onSuccess={() => goto('/messages')}
          onCancel={handleCancel}
        />
      {/if}
    </div>
  </div>