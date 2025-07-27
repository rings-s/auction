<!-- src/routes/auctions/[id]/edit/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import { user } from '$lib/stores/user.svelte.js';
	import { fetchAuctionById, updateAuction, deleteAuction } from '$lib/api/auction';

	// Components
	import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import AuctionForm from '$lib/components/auction/AuctionForm.svelte';
	import AuctionEditHeader from '$lib/components/auction/edit/AuctionEditHeader.svelte';
	import AuctionEditActions from '$lib/components/auction/edit/AuctionEditActions.svelte';
	import AuctionEditDeleteModal from '$lib/components/auction/edit/AuctionEditDeleteModal.svelte';

	let auction = null;
	let loading = true;
	let saving = false;
	let error = null;
	let success = null;
	let authError = null;
	let auctionForm = null;
	let showDeleteModal = false;
	let deleteLoading = false;
	let breadcrumbs = [];

	function safeTranslate(key, fallback = '', params = {}) {
		try {
			return $t ? $t(key, params) : fallback;
		} catch (e) {
			console.warn(`Translation error for key: ${key}`, e);
			return fallback;
		}
	}

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
				authError = safeTranslate(
					'auction.editNotAuthorized',
					'You are not authorized to edit this auction.'
				);
				auction = null;
			} else {
				auction = fetchedAuction;
			}
		} catch (err) {
			console.error('Error fetching auction:', err);

			if (err?.status === 403 || err?.status === 401) {
				authError = safeTranslate(
					'auction.editNotAuthorized',
					'You are not authorized to edit this auction.'
				);
			} else if (err?.status === 404) {
				error = safeTranslate('auction.notFound', 'Auction not found.');
			} else {
				error = err?.message || safeTranslate('error.fetchFailed', 'Failed to load auction.');
			}
		} finally {
			loading = false;
		}
	});

	async function handleSave() {
		if (!auctionForm || !auction?.id) return;

		saving = true;
		error = null;
		success = null;
		authError = null;

		try {
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

			success = safeTranslate('auction.updateSuccess', 'Auction updated successfully!');

			// Auto-hide success message after 3 seconds
			setTimeout(() => {
				success = null;
			}, 3000);
		} catch (err) {
			console.error('Error updating auction:', err);

			let errMessage = safeTranslate('auction.updateFailed', 'Failed to update auction.');

			if (err?.response?.data) {
				const data = err.response.data;
				if (data.detail) {
					errMessage = data.detail;
				} else if (typeof data === 'object') {
					const errors = Object.values(data)
						.map((e) => (Array.isArray(e) ? e.join(', ') : String(e)))
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

		try {
			await deleteAuction(auction.id.toString());

			// Show success and redirect
			success = safeTranslate('auction.deleteSuccess', 'Auction deleted successfully!');

			setTimeout(() => {
				goto('/auctions');
			}, 1500);
		} catch (err) {
			console.error('Error deleting auction:', err);
			error = err?.message || safeTranslate('auction.deleteFailed', 'Failed to delete auction.');
		} finally {
			deleteLoading = false;
			showDeleteModal = false;
		}
	}

	function handleCancel() {
		if (auction?.slug) {
			goto(`/auctions/${auction.slug}`);
		} else {
			goto('/auctions');
		}
	}

	function handleDeleteClick() {
		showDeleteModal = true;
	}

	function handleDeleteCancel() {
		showDeleteModal = false;
	}

	// Check if user can delete
	$: canDelete = $user && auction ? checkUserAuthorization($user, auction) : false;

	// Generate breadcrumbs
	$: if (auction) {
		breadcrumbs = [
			{ label: safeTranslate('nav.home', 'Home'), href: '/' },
			{ label: safeTranslate('nav.auctions', 'Auctions'), href: '/auctions' },
			{ label: auction.title, href: `/auctions/${auction.slug || auction.id}` },
			{
				label: safeTranslate('auction.edit', 'Edit'),
				href: `/auctions/${auction.id}/edit`,
				active: true
			}
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
	<title
		>{safeTranslate('auction.edit', 'Edit')} - {auction
			? auction.title
			: safeTranslate('common.loading', 'Loading...')}</title
	>
	<meta
		name="description"
		content={safeTranslate('auction.editMetaDescription', 'Edit auction details', {
			auctionTitle: auction?.title || ''
		})}
	/>
</svelte:head>

<div class="min-h-screen bg-neutral-50 px-4 py-6 sm:px-6 lg:px-8 dark:bg-neutral-900">
	<div class="mx-auto max-w-6xl space-y-6">
		<!-- Breadcrumb Navigation -->
		<Breadcrumb items={breadcrumbs} />

		<!-- Loading State -->
		{#if loading}
			<div class="space-y-6">
				<div class="rounded-lg bg-white p-6 shadow-sm dark:bg-gray-800">
					<LoadingSkeleton type="auctionHeader" />
				</div>
				<div class="rounded-lg bg-white p-6 shadow-sm dark:bg-gray-800">
					<LoadingSkeleton type="auctionForm" />
				</div>
			</div>

			<!-- Authorization Error -->
		{:else if authError}
			<div class="py-12 text-center">
				<Alert
					type="error"
					title={safeTranslate('error.accessDenied', 'Access Denied')}
					message={authError}
					action={{
						label: safeTranslate('auction.backToList', 'Back to Auctions'),
						href: '/auctions'
					}}
				/>
			</div>

			<!-- General Error -->
		{:else if error && !auction}
			<div class="py-12 text-center">
				<Alert
					type="error"
					title={safeTranslate('error.title', 'Error')}
					message={error}
					action={{
						label: safeTranslate('auction.backToList', 'Back to Auctions'),
						href: '/auctions'
					}}
				/>
			</div>

			<!-- Main Content -->
		{:else if auction}
			<!-- Messages -->
			{#if error}
				<Alert
					type="error"
					message={error}
					dismissible={true}
					on:dismiss={() => {
						error = null;
					}}
				/>
			{/if}

			{#if success}
				<Alert
					type="success"
					message={success}
					dismissible={true}
					on:dismiss={() => {
						success = null;
					}}
				/>
			{/if}

			<!-- Header -->
			<AuctionEditHeader {auction} {saving} />

			<!-- Form -->
			<div class="rounded-lg bg-white p-6 shadow-sm dark:bg-gray-800">
				<AuctionForm bind:this={auctionForm} initialAuction={auction} isEditing={true} />
			</div>

			<!-- Actions -->
			<AuctionEditActions
				{auction}
				{saving}
				{canDelete}
				onSave={handleSave}
				onCancel={handleCancel}
				onDelete={handleDeleteClick}
			/>

			<!-- Fallback Error -->
		{:else}
			<div class="py-12 text-center">
				<Alert
					type="error"
					title={safeTranslate('error.title', 'Error')}
					message={safeTranslate('error.generic', 'An unexpected error occurred.')}
					action={{
						label: safeTranslate('auction.backToList', 'Back to Auctions'),
						href: '/auctions'
					}}
				/>
			</div>
		{/if}
	</div>
</div>

<!-- Delete Confirmation Modal -->
<AuctionEditDeleteModal
	bind:show={showDeleteModal}
	{auction}
	{deleteLoading}
	onConfirm={handleDelete}
	onCancel={handleDeleteCancel}
/>
