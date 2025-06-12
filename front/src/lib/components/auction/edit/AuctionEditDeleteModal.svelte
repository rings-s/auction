<!-- src/lib/components/auction/edit/AuctionEditDeleteModal.svelte -->
<script>
    import { t } from '$lib/i18n';
    import Modal from '$lib/components/ui/Modal.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    
    export let show = false;
    export let auction;
    export let deleteLoading = false;
    export let onConfirm;
    export let onCancel;
  </script>
  
  <Modal 
    bind:show
    title={$t('auction.deleteConfirmTitle')}
    maxWidth="md"
    on:close={onCancel}
  >
    <div class="p-6">
      <!-- Warning Icon -->
      <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-danger-100 dark:bg-danger-900/30 mb-4">
        <svg class="h-6 w-6 text-danger-600 dark:text-danger-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      
      <!-- Content -->
      <div class="text-center">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          {$t('auction.deleteConfirmTitle')}
        </h3>
        <p class="text-sm text-neutral-600 dark:text-neutral-400 mb-6">
          {$t('auction.deleteConfirmMessage', { title: auction?.title || '' })}
        </p>
      </div>
      
      <!-- Auction Details -->
      {#if auction}
        <div class="bg-neutral-50 dark:bg-neutral-800 rounded-lg p-4 mb-6">
          <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-2">
            {$t('auction.deletingAuction')}:
          </h4>
          <dl class="space-y-1 text-sm">
            <div class="flex justify-between">
              <dt class="text-neutral-500 dark:text-neutral-400">{$t('auction.title')}:</dt>
              <dd class="font-medium text-gray-900 dark:text-white truncate ml-2 max-w-[200px]">
                {auction.title}
              </dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-neutral-500 dark:text-neutral-400">{$t('auction.status')}:</dt>
              <dd class="font-medium text-gray-900 dark:text-white">
                {auction.status.charAt(0).toUpperCase() + auction.status.slice(1)}
              </dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-neutral-500 dark:text-neutral-400">{$t('auction.totalBids')}:</dt>
              <dd class="font-medium text-gray-900 dark:text-white">
                {auction.bid_count || 0}
              </dd>
            </div>
          </dl>
        </div>
      {/if}
      
      <!-- Warning for Active Auctions -->
      {#if auction && (auction.status === 'live' || auction.status === 'scheduled')}
        <Alert 
          type="warning"
          title={$t('auction.deleteActiveWarningTitle')}"
          message={$t('auction.deleteActiveWarningMessage')}"
          class="mb-6"
        />
      {/if}
      
      <!-- Consequences List -->
      <div class="bg-danger-50 dark:bg-danger-900/20 border border-danger-200 dark:border-danger-800 rounded-lg p-4 mb-6">
        <h4 class="text-sm font-semibold text-danger-800 dark:text-danger-200 mb-2">
          {$t('auction.deleteConsequences')}:
        </h4>
        <ul class="text-sm text-danger-700 dark:text-danger-300 space-y-1">
          <li class="flex items-start">
            <span class="mr-2">•</span>
            <span>{$t('auction.deleteConsequence1')}</span>
          </li>
          <li class="flex items-start">
            <span class="mr-2">•</span>
            <span>{$t('auction.deleteConsequence2')}</span>
          </li>
          <li class="flex items-start">
            <span class="mr-2">•</span>
            <span>{$t('auction.deleteConsequence3')}</span>
          </li>
          <li class="flex items-start">
            <span class="mr-2">•</span>
            <span>{$t('auction.deleteConsequence4')}</span>
          </li>
        </ul>
      </div>
      
      <!-- Actions -->
      <div class="flex flex-col sm:flex-row-reverse gap-3">
        <Button 
          variant="danger" 
          size="default"
          on:click={onConfirm}
          loading={deleteLoading}
          disabled={deleteLoading}
          class="w-full sm:w-auto justify-center"
        >
          {deleteLoading ? $t('common.deleting') : $t('auction.confirmDelete')}
        </Button>
        
        <Button 
          variant="outline" 
          size="default"
          on:click={onCancel}
          disabled={deleteLoading}
          class="w-full sm:w-auto justify-center"
        >
          {$t('common.cancel')}
        </Button>
      </div>
    </div>
  </Modal>