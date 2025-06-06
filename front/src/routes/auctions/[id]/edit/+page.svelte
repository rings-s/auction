<!-- src/routes/auctions/[id]/edit/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { t } from '$lib/i18n';
    import { user } from '$lib/stores/user';
    import { fetchAuctionById, updateAuction, deleteAuction } from '$lib/api/auction';
    import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import Modal from '$lib/components/ui/Modal.svelte';
    import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
    import AuctionForm from '$lib/components/auction/AuctionForm.svelte';

    let auction = null;
    let loading = true;
    let saving = false;
    let error = null;
    let authError = null;
    let auctionForm = null;
    let showDeleteModal = false;
    let deleteLoading = false;
    let breadcrumbs = [];

    // Safe translation helper
    function safeTranslate(key, fallback = '', params = {}) {
        try {
            return $t ? $t(key, params) : fallback;
        } catch (e) {
            console.warn(`Translation error for key: ${key}`, e);
            return fallback;
        }
    }

    // Check user authorization
    function checkUserAuthorization(currentUser, auctionData) {
        if (!currentUser) return false;
        
        const { id: currentUserId, is_admin, is_staff, is_superuser } = currentUser;
        const isAdmin = is_admin || is_staff || is_superuser;
        
        if (isAdmin) return true;
        
        if (auctionData.created_by && auctionData.created_by.id) {
            return String(currentUserId) === String(auctionData.created_by.id);
        }
        
        return false;
    }

    onMount(async () => {
        const auctionId = $page.params.id;
        const currentUser = $user;

        try {
            const fetchedAuction = await fetchAuctionById(auctionId);
            
            if (!checkUserAuthorization(currentUser, fetchedAuction)) {
                authError = safeTranslate('auction.editNotAuthorized', 'You are not authorized to edit this auction.');
                auction = null;
            } else {
                auction = fetchedAuction;
            }

        } catch (err) {
            console.error('Error fetching auction:', err);
            
            if (err?.status === 403 || err?.status === 401) {
                authError = safeTranslate('auction.editNotAuthorized', 'You are not authorized to edit this auction.');
            } else if (err?.status === 404) {
                error = safeTranslate('auction.notFound', 'Auction not found.');
            } else {
                error = err?.message || safeTranslate('error.fetchFailed', 'Failed to load auction.');
            }
        } finally {
            loading = false;
        }
    });

    async function handleSubmit() {
        if (!auctionForm || !auction?.id) return;
        
        saving = true;
        error = null;
        authError = null;

        try {
            // Validate the form first
            const validation = auctionForm.validateForm();
            if (!validation.valid) {
                error = validation.error || 'Please check the form for errors';
                return;
            }

            const formData = auctionForm.prepareDataForSubmission();
            if (!formData) {
                throw new Error('Failed to get form data');
            }

            const updatedAuctionData = await updateAuction(auction.id.toString(), formData);
            auction = updatedAuctionData;
            
            // Show success message
            const successMsg = safeTranslate('auction.updateSuccess', 'Auction updated successfully!');
            alert(successMsg);
            
        } catch (err) {
            console.error('Error updating auction:', err);
            
            let errMessage = safeTranslate('auction.updateFailed', 'Failed to update auction.');
            
            if (err?.response?.data) {
                const data = err.response.data;
                if (data.detail) {
                    errMessage = data.detail;
                } else if (typeof data === 'object') {
                    const errors = Object.values(data)
                        .map(e => Array.isArray(e) ? e.join(', ') : String(e))
                        .join('; ');
                    if (errors) errMessage = errors;
                }
            } else if (err?.message) {
                errMessage = err.message;
            }
            
            error = errMessage;
        } finally {
            saving = false;
        }
    }

    async function handleDelete() {
        if (!auction?.id) return;
        
        deleteLoading = true;
        error = null;
        authError = null;
        
        try {
            await deleteAuction(auction.id.toString());
            const successMsg = safeTranslate('auction.deleteSuccess', 'Auction deleted successfully!');
            alert(successMsg);
            goto('/auctions');
        } catch (err) {
            console.error('Error deleting auction:', err);
            error = err?.message || safeTranslate('auction.deleteFailed', 'Failed to delete auction.');
        } finally {
            deleteLoading = false;
            showDeleteModal = false;
        }
    }
    
    // Check if user can delete
    $: canDelete = $user && auction ? checkUserAuthorization($user, auction) : false;

    // Generate breadcrumbs
    $: if (auction) {
        breadcrumbs = [
            { label: safeTranslate('nav.home', 'Home'), href: '/' },
            { label: safeTranslate('nav.auctions', 'Auctions'), href: '/auctions' },
            { label: auction.title, href: `/auctions/${auction.slug || auction.id}` },
            { label: safeTranslate('auction.edit', 'Edit'), href: `/auctions/${auction.id}/edit`, active: true }
        ];
    } else {
        breadcrumbs = [
            { label: safeTranslate('nav.home', 'Home'), href: '/' },
            { label: safeTranslate('nav.auctions', 'Auctions'), href: '/auctions' },
            { label: safeTranslate('auction.edit', 'Edit'), active: true }
        ];
    }
</script>

<svelte:head>
    <title>{safeTranslate('auction.edit', 'Edit')} - {auction ? auction.title : safeTranslate('common.loading', 'Loading...')}</title>
    <meta name="description" content={safeTranslate('auction.editMetaDescription', 'Edit auction details', { auctionTitle: auction?.title || '' })} />
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-6 px-4 sm:px-6 lg:px-8">
    <div class="max-w-6xl mx-auto space-y-6">
        <Breadcrumb items={breadcrumbs} />

        {#if loading}
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
                <LoadingSkeleton type="auctionForm" />
            </div>
        {:else if authError}
            <Alert type="error" message={authError} />
            <div class="text-center">
                <Button href="/auctions" variant="primary" size="sm">
                    {safeTranslate('auction.backToList', 'Back to Auctions')}
                </Button>
            </div>
        {:else if error && !auction}
            <Alert type="error" message={error} />
            <div class="text-center">
                <Button href="/auctions" variant="primary" size="sm">
                    {safeTranslate('auction.backToList', 'Back to Auctions')}
                </Button>
            </div>
        {:else if auction}
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
                <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                    {safeTranslate('auction.editTitle', 'Edit: {title}', { title: auction.title })}
                </h1>

                {#if error}
                    <Alert type="error" message={error} class="mb-6" />
                {/if}

                <AuctionForm 
                    bind:this={auctionForm} 
                    initialAuction={auction} 
                    isEditing={true}
                />

                <div class="mt-8 flex flex-wrap justify-between items-center gap-4">
                    <div class="flex space-x-3">
                        <Button 
                            variant="primary" 
                            size="sm"
                            on:click={handleSubmit} 
                            disabled={saving || deleteLoading}
                            loading={saving}
                            iconLeft='<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>'
                        >
                            {saving ? safeTranslate('common.saving', 'Saving...') : safeTranslate('common.saveChanges', 'Save Changes')}
                        </Button>

                        <Button 
                            variant="outline" 
                            size="sm"
                            href={auction.slug ? `/auctions/${auction.slug}` : '/auctions'}
                            disabled={saving || deleteLoading}
                            iconLeft='<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>'
                        >
                            {safeTranslate('common.cancel', 'Cancel')}
                        </Button>
                    </div>

                    {#if canDelete}
                        <Button 
                            variant="danger" 
                            size="sm"
                            on:click={() => showDeleteModal = true} 
                            disabled={saving || deleteLoading}
                            iconLeft='<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>'
                        >
                            {safeTranslate('auction.delete', 'Delete')}
                        </Button>
                    {/if}
                </div>
            </div>
        {:else}
            <Alert type="error" message={safeTranslate('error.generic', 'An unexpected error occurred.')} />
        {/if}
    </div>
</div>

{#if showDeleteModal}
    <Modal 
        title={safeTranslate('auction.deleteConfirmTitle', 'Delete Auction')}
        show={showDeleteModal}
        on:close={() => showDeleteModal = false}
        maxWidth="md"
    >
        <div class="p-6">
            <p class="text-gray-600 dark:text-gray-400 mb-6">
                {safeTranslate('auction.deleteConfirmMessage', 'Are you sure you want to delete "{title}"? This action cannot be undone.', { title: auction?.title || '' })}
            </p>
            
            <div class="flex justify-end space-x-3">
                <Button 
                    variant="outline" 
                    size="sm"
                    on:click={() => showDeleteModal = false}
                    disabled={deleteLoading}
                >
                    {safeTranslate('common.cancel', 'Cancel')}
                </Button>
                
                <Button 
                    variant="danger" 
                    size="sm"
                    on:click={handleDelete}
                    loading={deleteLoading}
                    disabled={deleteLoading}
                >
                    {deleteLoading ? safeTranslate('common.deleting', 'Deleting...') : safeTranslate('auction.delete', 'Delete')}
                </Button>
            </div>
        </div>
    </Modal>
{/if}