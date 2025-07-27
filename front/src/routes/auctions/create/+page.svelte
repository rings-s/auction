<!-- front/src/routes/auctions/create/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import { user } from '$lib/stores/user.svelte.js';
	import { createAuction } from '$lib/api/auction';

	// Components
	import AuctionForm from '$lib/components/auction/AuctionForm.svelte';
	import AuctionCreateHeader from '$lib/components/auction/create/AuctionCreateHeader.svelte';
	import AuctionCreateActions from '$lib/components/auction/create/AuctionCreateActions.svelte';
	import AuctionCreatePreview from '$lib/components/auction/create/AuctionCreatePreview.svelte';
	import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';

	let auctionForm;
	let isPreview = false;
	let loading = true;
	let submitting = false;
	let error = '';
	let success = '';
	let previewData = null;
	let validationErrors = {};

	function safeTranslate(key, fallback = '') {
		try {
			return $t ? $t(key) : fallback;
		} catch (e) {
			console.warn(`Translation error for key: ${key}`, e);
			return fallback;
		}
	}

	$: breadcrumbItems = [
		{ label: safeTranslate('nav.home', 'Home'), href: '/' },
		{ label: safeTranslate('nav.auctions', 'Auctions'), href: '/auctions' },
		{
			label: safeTranslate('auction.createAuction', 'Create Auction'),
			href: '/auctions/create',
			active: true
		}
	];

	onMount(async () => {
		try {
			if (!$user) {
				goto('/login?redirect=/auctions/create');
				return;
			}

			const hasPermission =
				$user.is_staff ||
				$user.is_superuser ||
				$user.role === 'owner' ||
				$user.role === 'appraiser' ||
				$user.role === 'admin';

			if (!hasPermission) {
				error = safeTranslate(
					'auction.unauthorizedMessage',
					'You do not have permission to create auctions.'
				);
			}
		} catch (e) {
			console.error('Error in onMount:', e);
			error = 'An error occurred while loading the page.';
		} finally {
			loading = false;
		}
	});

	async function handleSubmit() {
		try {
			submitting = true;
			error = '';
			success = '';
			validationErrors = {};

			if (!auctionForm) {
				throw new Error('Form not initialized');
			}

			const validation = auctionForm.validateForm();
			if (!validation.valid) {
				error = validation.error || 'Please check the form for errors';
				validationErrors = validation.errors || {};
				return;
			}

			const preparedAuction = auctionForm.prepareDataForSubmission();

			if (!preparedAuction) {
				throw new Error('Failed to get form data');
			}

			// Ensure the auction is published and has proper status
			preparedAuction.is_published = true;
			preparedAuction.status = 'scheduled'; // Will auto-change to 'live' when start time is reached

			if (!preparedAuction.title || !preparedAuction.description) {
				throw new Error('Title and description are required');
			}

			const response = await createAuction(preparedAuction);

			if (response && response.id) {
				try {
					await auctionForm.uploadTempMedia(response.id);
				} catch (mediaError) {
					console.warn('Media upload failed:', mediaError);
				}

				success = safeTranslate('auction.createSuccess', 'Auction created successfully!');

				setTimeout(() => {
					const redirectPath = response.slug
						? `/auctions/${response.slug}`
						: `/auctions/${response.id}`;
					goto(redirectPath);
				}, 1500);
			} else {
				throw new Error('Invalid response from server');
			}
		} catch (err) {
			console.error('Error creating auction:', err);
			error =
				err.message ||
				safeTranslate('auction.createFailed', 'Failed to create auction. Please try again.');
		} finally {
			submitting = false;
		}
	}

	function togglePreview() {
		try {
			if (!auctionForm) {
				error = 'Form not initialized';
				return;
			}

			if (!isPreview) {
				const validation = auctionForm.validateForm();
				if (!validation.valid) {
					error = validation.error || 'Please fix the errors before previewing';
					validationErrors = validation.errors || {};
					return;
				}

				previewData = auctionForm.prepareDataForSubmission();
				if (!previewData) {
					error = 'Failed to get form data for preview';
					return;
				}
			}

			error = '';
			isPreview = !isPreview;
		} catch (e) {
			console.error('Error toggling preview:', e);
			error = 'An error occurred while toggling preview mode.';
		}
	}

	function backToForm() {
		isPreview = false;
		error = '';
	}

	function handleCancel() {
		goto('/auctions');
	}
</script>

<svelte:head>
	<title>{safeTranslate('auction.createAuction', 'Create Auction')} | Real Estate Platform</title>
	<meta
		name="description"
		content={safeTranslate('auction.createAuctionDesc', 'Create a new auction for your property')}
	/>
</svelte:head>

<div class="min-h-screen bg-neutral-50 px-4 py-6 sm:px-6 lg:px-8 dark:bg-neutral-900">
	<div class="mx-auto max-w-6xl space-y-6">
		<!-- Breadcrumb Navigation -->
		<Breadcrumb items={breadcrumbItems} />

		<!-- Page Header -->
		<AuctionCreateHeader {isPreview} {submitting} onTogglePreview={togglePreview} />

		<!-- Messages -->
		{#if error}
			<Alert
				type="error"
				title={safeTranslate('error.title', 'Error')}
				message={error}
				dismissible={true}
				on:dismiss={() => {
					error = '';
				}}
			/>
		{/if}

		{#if success}
			<Alert type="success" title={safeTranslate('success.title', 'Success')} message={success} />
		{/if}

		<!-- Main Content -->
		{#if loading}
			<div class="rounded-lg bg-white p-6 shadow-sm dark:bg-gray-800">
				<LoadingSkeleton type="auctionForm" />
			</div>
		{:else if isPreview && previewData}
			<AuctionCreatePreview {previewData} />
			<AuctionCreateActions
				{isPreview}
				{submitting}
				onBackToForm={backToForm}
				onSubmit={handleSubmit}
			/>
		{:else}
			<div class="space-y-6">
				<AuctionForm
					bind:this={auctionForm}
					{validationErrors}
					on:validationChange={(e) => (validationErrors = e.detail)}
				/>

				<AuctionCreateActions
					{isPreview}
					{submitting}
					onCancel={handleCancel}
					onTogglePreview={togglePreview}
					onSubmit={handleSubmit}
				/>
			</div>
		{/if}
	</div>
</div>
