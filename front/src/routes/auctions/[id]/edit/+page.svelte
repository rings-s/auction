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

    onMount(async () => {
        const auctionId = $page.params.id;
        const currentUser = $user;

        try {
            const fetchedAuction = await fetchAuctionById(auctionId);
            let isAuthorized = false;
            let currentUserIsAdmin = false;

            if (currentUser) {
                const { id: currentUserId, is_admin } = currentUser;
                currentUserIsAdmin = is_admin === true;

                if (currentUserIsAdmin) {
                    isAuthorized = true;
                } else if (fetchedAuction.created_by && fetchedAuction.created_by.id && currentUserId) {
                    if (String(currentUserId) === String(fetchedAuction.created_by.id)) {
                        isAuthorized = true;
                    }
                }
            }
            
            if (!isAuthorized && fetchedAuction.created_by) { 
                authError = $t('auction.editNotAuthorized');
                auction = null;
            } else if (!isAuthorized && !fetchedAuction.created_by) {
                if (currentUserIsAdmin) {
                    isAuthorized = true; 
                    auction = fetchedAuction;
                } else {
                    authError = $t('auction.editNotAuthorized');
                    auction = null;
                }
            } else if (isAuthorized) {
                auction = fetchedAuction;
            } else {
                authError = $t('auction.editNotAuthorized');
                auction = null;
            }

        } catch (err) {
            let message = $t('error.fetchFailed');
            if (err && typeof err === 'object') {
                if ('status' in err) {
                    const status = err.status;
                    if (status === 403 || status === 401) {
                        authError = $t('auction.editNotAuthorized');
                        message = '';
                    } else if (status === 404) {
                        error = $t('auction.notFound'); 
                        message = '';
                    }
                }
                if (message && 'message' in err && typeof err.message === 'string') {
                    error = err.message;
                } else if (message) {
                    error = message;
                }
            } else {
                error = message;
            }
        } finally {
            loading = false;
        }
    });

    async function handleSubmit() {
        if (!auctionForm || !auction || !auction.id) return;
        const currentData = auctionForm.getFormData(); 
        if (!currentData) return;

        saving = true;
        error = null; 
        authError = null;

        try {
            const updatedAuctionData = await updateAuction(auction.id.toString(), currentData);
            auction = updatedAuctionData;
            alert($t('auction.updateSuccess'));
        } catch (err) {
            let errMessage = $t('auction.updateFailed');
            if (err && typeof err === 'object' && 'response' in err && err.response && typeof err.response === 'object' && 'data' in err.response && err.response.data) {
                const data = err.response.data;
                if (typeof data === 'object' && data !== null && 'detail' in data && typeof data.detail === 'string') {
                    errMessage = data.detail;
                } else if (typeof data === 'object' && data !== null){
                    try {
                        errMessage = Object.values(data).map(e => Array.isArray(e) ? e.join(', ') : String(e)).join('; ');
                    } catch (_) {
                        // Keep default errMessage
                    }
                }
            } else if (err && typeof err === 'object' && 'message' in err && typeof err.message === 'string') {
                errMessage = err.message;
            }
            error = errMessage;
        } finally {
            saving = false;
        }
    }

    async function handleDelete() {
        if (!auction || !auction.id) return;
        deleteLoading = true;
        error = null;
        authError = null;
        try {
            await deleteAuction(auction.id.toString());
            alert($t('auction.deleteSuccess'));
            goto('/dashboard/my-auctions'); 
        } catch (err) {
            if (err && typeof err === 'object' && 'message' in err && typeof err.message === 'string'){
                error = err.message;
            } else {
                error = $t('auction.deleteFailed');
            }
        } finally {
            deleteLoading = false;
            showDeleteModal = false;
        }
    }
    
    let canDelete = false; 
    $: {
        const currentUser = $user;
        if (currentUser && auction && auction.created_by) {
            const { id: currentUserId, is_admin: currentUserIsAdmin } = currentUser;
            if (currentUserId && auction.created_by.id) { 
                 canDelete = (String(currentUserId) === String(auction.created_by.id)) || (currentUserIsAdmin === true);
            } else {
                canDelete = currentUserIsAdmin === true; 
            }
        } else if (currentUser && auction && !auction.created_by) {
            const { is_admin: currentUserIsAdmin } = currentUser;
            canDelete = currentUserIsAdmin === true;
        } else {
            canDelete = false;
        }
    }

    $: if (auction) {
        breadcrumbs = [
            { label: $t('nav.home'), href: '/' },
            { label: $t('nav.auctions'), href: '/auctions' },
            { label: auction.title, href: `/auctions/${auction.slug}` },
            { label: $t('auction.edit'), href: `/auctions/${auction.id}/edit`, current: true }
        ];
    } else {
        breadcrumbs = [
            { label: $t('nav.home'), href: '/' },
            { label: $t('nav.auctions'), href: '/auctions' },
            { label: $t('auction.edit'), current: true } 
        ];
    }

</script>

<svelte:head>
    <title>{$t('auction.edit')} - {auction ? auction.title : $t('common.loading')}</title>
    <meta name="description" content={$t('auction.editMetaDescription', { auctionTitle: auction ? auction.title : '' })} />
</svelte:head>

<div class="container mx-auto px-4 py-8">
    <Breadcrumb items={breadcrumbs} />

    {#if loading}
        <LoadingSkeleton class="mt-6" />
    {:else if authError}
        <Alert type="error" message={authError} class="mt-6" />
        <div class="mt-6 text-center">
            <Button href="/auctions" variant="primary">{$t('auction.backToList')}</Button>
        </div>
    {:else if error && !auction} 
        <Alert type="error" message={error} class="mt-6" />
        <div class="mt-6 text-center">
            <Button href="/auctions" variant="primary">{$t('auction.backToList')}</Button>
        </div>
    {:else if auction} 
        <h1 class="text-3xl font-bold my-6">{$t('auction.editTitle', { title: auction.title })}</h1>

        {#if error && auction} 
            <Alert type="error" message={error} class="mb-6" />
        {/if}

        <AuctionForm bind:this={auctionForm} initialAuction={auction} isEditing={true} on:submit={handleSubmit} />

        <div class="mt-8 flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0 sm:space-x-4">
            <Button 
                variant="primary" 
                on:click={() => auctionForm?.submitForm()} 
                disabled={saving || deleteLoading}
                loading={saving}
            >
                {saving ? $t('common.saving') : $t('common.saveChanges')}
            </Button>

            {#if canDelete}
                <Button 
                    variant="danger-outline" 
                    on:click={() => showDeleteModal = true} 
                    disabled={saving || deleteLoading}                    
                >
                    {$t('auction.delete')}
                </Button>
            {/if}

            <Button 
                variant="neutral-outline" 
                href={auction.slug ? `/auctions/${auction.slug}` : '/auctions'}
                disabled={saving || deleteLoading}
            >
                {$t('common.cancel')}
            </Button>
        </div>
    {:else}
        <Alert type="error" message={$t('error.generic')} class="mt-6" />
    {/if}
</div>

{#if showDeleteModal}
    <Modal 
        title={$t('auction.deleteConfirmTitle')}
        on:confirm={handleDelete}
        on:cancel={() => showDeleteModal = false}
        confirmButtonVariant="danger"
        closeButton={true} 
        disabled={deleteLoading} 
    >
        <p>{$t('auction.deleteConfirmMessage', { title: auction?.title ?? ''})}</p>
    </Modal>
{/if}