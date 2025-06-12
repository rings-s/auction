<!-- src/lib/components/auction/create/AuctionCreateHeader.svelte -->
<script>
    import { t } from '$lib/i18n';
    import Button from '$lib/components/ui/Button.svelte';
    
    export let isPreview = false;
    export let submitting = false;
    export let onTogglePreview;
  </script>
  
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
    <div class="md:flex md:items-center md:justify-between">
      <div class="flex-1 min-w-0">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
          {isPreview ? $t('auction.preview') : $t('auction.createAuction')}
        </h1>
        <p class="mt-2 text-sm text-neutral-600 dark:text-neutral-400">
          {isPreview ? 
            $t('auction.previewDesc') : 
            $t('auction.createAuctionDesc')
          }
        </p>
      </div>
      
      <div class="mt-4 lg:mt-0 lg:ml-4">
        <Button
          variant={isPreview ? 'secondary' : 'outline'}
          size="sm"
          on:click={onTogglePreview}
          disabled={submitting}
          class="inline-flex items-center"
        >
          {#if isPreview}
            <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          {:else}
            <svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          {/if}
          {isPreview ? $t('common.edit') : $t('auction.preview')}
        </Button>
      </div>
    </div>
  </div>