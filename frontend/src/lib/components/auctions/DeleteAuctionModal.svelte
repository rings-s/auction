<!-- src/lib/components/auctions/DeleteAuctionModal.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    import { fade, fly } from 'svelte/transition';
    import { t, isRTL } from '$lib/i18n';
    import { formatCurrency, formatDate } from '$lib/utils/formatters';
    import { auctionActions, loading } from '$lib/stores/auction';
    import Button from '$lib/components/ui/Button.svelte';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    import { toast } from '$lib/stores/toast';
    
    // Props
    export let auction = null;
    export let isOpen = false;
    
    // State
    let confirmText = '';
    let confirmCheckbox = false;
    let isSubmitting = false;
    let error = null;
    
    // Check if auction can be deleted
    $: canDelete = ['draft', 'pending', 'cancelled'].includes(auction?.status);
    $: hasActiveBids = auction?.bid_count > 0;
    
    const dispatch = createEventDispatcher();
    
    // Close modal
    function close() {
        if (isSubmitting) return;
        
        // Reset state
        confirmText = '';
        confirmCheckbox = false;
        error = null;
        
        // Close modal
        isOpen = false;
        dispatch('close');
    }
    
    // Handle delete confirmation
    async function handleDelete() {
        // Validate confirmation
        if (!auction?.id) {
            error = t('auctions.no_auction_selected');
            return;
        }
        
        if (!confirmCheckbox) {
            error = t('auctions.confirm_checkbox_required');
            return;
        }
        
        const auctionId = auction.id.toString();
        if (confirmText !== auctionId) {
            error = t('auctions.confirm_text_mismatch');
            return;
        }
        
        // Delete auction
        isSubmitting = true;
        error = null;
        
        try {
            const result = await auctionActions.deleteAuction(auction.id);
            
            if (result.success) {
                // Show success toast
                toast.success(t('auctions.delete_success'));
                
                // Close modal and notify parent
                close();
                dispatch('success', { auctionId: auction.id });
            } else {
                error = result.error || t('auctions.delete_error');
            }
        } catch (err) {
            console.error('Error deleting auction:', err);
            error = err.message || t('auctions.delete_error');
        } finally {
            isSubmitting = false;
        }
    }
</script>

{#if isOpen}
    <div 
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
        transition:fade={{ duration: 200 }}
        on:click|self={close}
    >
        <div 
            class="w-full max-w-md rounded-xl bg-white dark:bg-neutral-800 shadow-xl overflow-hidden"
            transition:fly={{ duration: 250, y: 20 }}
            class:rtl={isRTL()}
        >
            <!-- Header -->
            <div class="px-6 py-4 border-b border-neutral-200 dark:border-neutral-700">
                <div class="flex items-center text-error-600 dark:text-error-400">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 {isRTL() ? 'ml-2' : 'mr-2'}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <h3 class="text-lg font-semibold">
                        {t('auctions.delete_confirmation')}
                    </h3>
                </div>
            </div>
            
            <!-- Content -->
            <div class="px-6 py-4">
                {#if auction}
                    <p class="mb-4 text-neutral-700 dark:text-neutral-300">
                        {t('auctions.delete_warning')} <strong>"{auction.title}"</strong>?
                    </p>
                    
                    <!-- Auction summary -->
                    <div class="mb-4 rounded-lg bg-neutral-50 dark:bg-neutral-700/30 p-4">
                        <div class="grid grid-cols-2 gap-2 text-sm">
                            <div>
                                <span class="text-neutral-500 dark:text-neutral-400">{t('auctions.auction_id')}:</span>
                                <span class="font-medium">{auction.id}</span>
                            </div>
                            <div>
                                <span class="text-neutral-500 dark:text-neutral-400">{t('auctions.status')}:</span>
                                <span class="font-medium">{auction.status_display || auction.status}</span>
                            </div>
                            <div>
                                <span class="text-neutral-500 dark:text-neutral-400">{t('auctions.start_date')}:</span>
                                <span class="font-medium">{formatDate(auction.start_date)}</span>
                            </div>
                            <div>
                                <span class="text-neutral-500 dark:text-neutral-400">{t('auctions.current_bid')}:</span>
                                <span class="font-medium">{formatCurrency(auction.current_bid || auction.starting_price)}</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Warning box -->
                    <div class="mb-6 rounded-lg bg-warning-50 dark:bg-warning-900/20 p-4 text-sm">
                        <h4 class="font-semibold text-warning-700 dark:text-warning-400 mb-2">
                            {t('general.warning')}
                        </h4>
                        <ul class="list-disc {isRTL() ? 'mr-4' : 'ml-4'} space-y-1 text-warning-700 dark:text-warning-400">
                            <li>{t('auctions.delete_warning_1')}</li>
                            <li>{t('auctions.delete_warning_2')}</li>
                            
                            {#if hasActiveBids}
                                <li class="font-medium">{t('auctions.delete_warning_bids')}</li>
                            {/if}
                            
                            {#if !canDelete}
                                <li class="font-medium">{t('auctions.delete_warning_status', { status: auction.status_display || auction.status })}</li>
                            {/if}
                        </ul>
                    </div>
                    
                    <!-- Confirmation input -->
                    <div class="mb-4">
                        <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                            {t('auctions.confirm_delete_prompt', { id: auction.id })}
                        </label>
                        <input 
                            type="text"
                            class="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary dark:bg-neutral-700 dark:text-white"
                            bind:value={confirmText}
                            placeholder={auction.id.toString()}
                            disabled={isSubmitting}
                        />
                    </div>
                    
                    <!-- Confirmation checkbox -->
                    <div class="mb-4 flex items-start">
                        <input 
                            type="checkbox"
                            id="confirm-checkbox"
                            class="mt-1 {isRTL() ? 'ml-2' : 'mr-2'}"
                            bind:checked={confirmCheckbox}
                            disabled={isSubmitting}
                        />
                        <label for="confirm-checkbox" class="text-sm text-neutral-700 dark:text-neutral-300">
                            {t('auctions.confirm_delete_checkbox')}
                        </label>
                    </div>
                    
                    <!-- Error message -->
                    {#if error}
                        <div class="mb-4 p-3 rounded-lg bg-error-50 dark:bg-error-900/20 text-error-600 dark:text-error-400 text-sm">
                            {error}
                        </div>
                    {/if}
                {/if}
            </div>
            
            <!-- Footer -->
            <div class="px-6 py-4 bg-neutral-50 dark:bg-neutral-700/30 border-t border-neutral-200 dark:border-neutral-700 flex justify-end space-x-3">
                <Button 
                    variant="outline"
                    size="md"
                    on:click={close}
                    disabled={isSubmitting}
                >
                    {t('general.cancel')}
                </Button>
                
                <Button 
                    variant="error"
                    size="md"
                    on:click={handleDelete}
                    disabled={isSubmitting || !confirmCheckbox || confirmText !== (auction?.id?.toString() || '')}
                    loading={isSubmitting}
                >
                    {t('auctions.delete_auction')}
                </Button>
            </div>
        </div>
    </div>
{/if}

<style>
    /* RTL styles */
    .rtl {
        direction: rtl;
        text-align: right;
    }
    
    .rtl .space-x-3 > :not([hidden]) ~ :not([hidden]) {
        --tw-space-x-reverse: 1;
    }
</style>