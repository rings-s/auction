<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { t, locale } from '$lib/i18n';
	import { user } from '$lib/stores/user.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';
	import LoadingSpinner from '$lib/components/animations/LoadingSpinner.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import { tenantsAPI } from '$lib/api/propertyManagement.js';
	import { fade } from 'svelte/transition';

	let isRTL = $derived($locale === 'ar');

	// State using Svelte 5 runes
	let loading = $state(true);
	let error = $state('');
	let tenant = $state(null);
	let showDeleteModal = $state(false);
	let deleting = $state(false);

	// Get tenant ID from URL params
	let tenantId = $derived($page.params.id);

	// Permission check
	let hasAccess = $derived(
		($user && ['owner', 'appraiser', 'data_entry'].includes($user.role)) || $user?.is_superuser
	);

	onMount(() => {
		if (!hasAccess) {
			goto('/property-management/tenants');
			return;
		}
		if (tenantId) {
			loadTenant();
		}
	});

	async function loadTenant() {
		try {
			loading = true;
			error = '';

			const response = await tenantsAPI.getById(tenantId);
			if (response.data) {
				tenant = response.data;
			}
		} catch (err) {
			error = err.message || $t('errors.loadingFailed');
			console.error('Failed to load tenant:', err);
		} finally {
			loading = false;
		}
	}

	async function handleDeleteTenant() {
		try {
			deleting = true;
			await tenantsAPI.delete(tenantId);
			goto('/property-management/tenants');
		} catch (err) {
			error = err.message || $t('errors.deleteFailed');
		} finally {
			deleting = false;
			showDeleteModal = false;
		}
	}

	function getStatusBadge(status) {
		const statusMap = {
			active: {
				color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
				text: $t('tenant.status.active')
			},
			inactive: {
				color: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
				text: $t('tenant.status.inactive')
			},
			pending: {
				color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
				text: $t('tenant.status.pending')
			}
		};
		return statusMap[status] || statusMap.inactive;
	}

	function formatDate(dateString) {
		if (!dateString) return '-';
		return new Date(dateString).toLocaleDateString($locale);
	}

	function formatCurrency(amount) {
		if (!amount) return '-';
		return `${amount.toLocaleString()} ${$t('currency.sar')}`;
	}
</script>

<svelte:head>
	<title
		>{tenant?.name || $t('tenant.details')} | {$t('propertyManagement.title')} | {$t(
			'app.name'
		)}</title
	>
	<meta name="description" content={$t('tenant.detailsDescription')} />
</svelte:head>

<div
	class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-gray-900 dark:via-blue-900 dark:to-indigo-900"
	dir={isRTL ? 'rtl' : 'ltr'}
>
	<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
		<!-- Header -->
		<div class="mb-8">
			<div class="flex items-center justify-between">
				<div>
					<button
						onclick={() => goto('/property-management/tenants')}
						class="group mb-4 inline-flex items-center text-sm font-medium text-blue-600 transition-colors hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
					>
						<svg
							class="h-4 w-4 {isRTL
								? 'ml-2 rotate-180'
								: 'mr-2'} transition-transform group-hover:scale-110"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M10 19l-7-7m0 0l7-7m-7 7h18"
							/>
						</svg>
						{$t('tenant.backToTenants')}
					</button>
					<h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">
						{tenant?.name || $t('tenant.details')}
					</h1>
					<p class="mt-2 text-gray-600 dark:text-gray-400">
						{$t('tenant.detailsSubtitle')}
					</p>
				</div>

				<!-- Actions -->
				{#if tenant && hasAccess}
					<div class="flex gap-3">
						<Button
							variant="outline"
							onclick={() => goto(`/property-management/tenants/${tenantId}/edit`)}
						>
							<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
								/>
							</svg>
							{$t('common.edit')}
						</Button>
						<Button variant="danger" onclick={() => (showDeleteModal = true)}>
							<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
								/>
							</svg>
							{$t('common.delete')}
						</Button>
					</div>
				{/if}
			</div>
		</div>

		<!-- Permission Check -->
		{#if !hasAccess}
			<div
				class="mx-auto max-w-3xl rounded-2xl border border-yellow-200 bg-yellow-50 p-8 text-yellow-800 shadow-xl dark:border-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-200"
			>
				<div class="flex items-center">
					<svg
						class="mr-3 h-8 w-8 text-yellow-500"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
						/>
					</svg>
					<div>
						<h2 class="mb-2 text-xl font-semibold">{$t('error.accessDenied')}</h2>
						<p class="text-base">{$t('error.insufficientPermissions')}</p>
					</div>
				</div>
			</div>
		{:else if loading}
			<!-- Loading State -->
			<div class="space-y-8">
				<div
					class="rounded-2xl border border-gray-200 bg-white p-8 shadow-xl dark:border-gray-700 dark:bg-gray-800"
				>
					<div class="animate-pulse space-y-6">
						<div class="h-8 w-1/3 rounded-xl bg-gray-200 dark:bg-gray-700"></div>
						<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
							{#each Array(6) as _}
								<div class="space-y-2">
									<div class="h-4 w-1/4 rounded bg-gray-200 dark:bg-gray-700"></div>
									<div class="h-6 w-3/4 rounded bg-gray-200 dark:bg-gray-700"></div>
								</div>
							{/each}
						</div>
					</div>
				</div>
			</div>
		{:else if error}
			<!-- Error State -->
			<div
				class="mx-auto max-w-3xl rounded-2xl border border-red-200 bg-red-50 p-8 text-red-800 shadow-xl dark:border-red-800 dark:bg-red-900/20 dark:text-red-200"
			>
				<div class="flex items-center">
					<svg
						class="mr-3 h-8 w-8 text-red-500"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
						/>
					</svg>
					<div>
						<h2 class="mb-2 text-xl font-semibold">{$t('error.title')}</h2>
						<p class="text-base">{error}</p>
					</div>
				</div>
				<div class="mt-6">
					<Button variant="outline" onclick={loadTenant}>
						<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
							/>
						</svg>
						{$t('common.retry')}
					</Button>
				</div>
			</div>
		{:else if tenant}
			<!-- Tenant Details -->
			<div class="space-y-8" transition:fade={{ duration: 300 }}>
				<!-- Basic Information -->
				<div
					class="rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
				>
					<div
						class="rounded-t-2xl bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-600 p-6 text-white"
					>
						<div class="flex items-center">
							<!-- Avatar -->
							<div
								class="mr-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-white/20 text-2xl font-bold text-white"
							>
								{tenant.name?.charAt(0)?.toUpperCase() || 'T'}
							</div>
							<div>
								<h2 class="text-2xl font-semibold">{tenant.name}</h2>
								{#if tenant.status}
									{@const statusInfo = getStatusBadge(tenant.status)}
									<span
										class="inline-flex items-center rounded-full px-3 py-1 text-sm font-medium {statusInfo.color} mt-2"
									>
										{statusInfo.text}
									</span>
								{/if}
							</div>
						</div>
					</div>
					<div class="p-8">
						<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
							<!-- Contact Information -->
							<div>
								<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
									{$t('tenant.contactInfo')}
								</h3>
								<div class="space-y-3">
									<div>
										<label class="block text-sm font-medium text-gray-500 dark:text-gray-400"
											>{$t('tenant.email')}</label
										>
										<p class="text-gray-900 dark:text-white">{tenant.email || '-'}</p>
									</div>
									<div>
										<label class="block text-sm font-medium text-gray-500 dark:text-gray-400"
											>{$t('tenant.phone')}</label
										>
										<p class="text-gray-900 dark:text-white">{tenant.phone || '-'}</p>
									</div>
									<div>
										<label class="block text-sm font-medium text-gray-500 dark:text-gray-400"
											>{$t('tenant.emergencyContact')}</label
										>
										<p class="text-gray-900 dark:text-white">{tenant.emergency_contact || '-'}</p>
									</div>
								</div>
							</div>

							<!-- Lease Information -->
							<div>
								<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
									{$t('tenant.leaseInfo')}
								</h3>
								<div class="space-y-3">
									<div>
										<label class="block text-sm font-medium text-gray-500 dark:text-gray-400"
											>{$t('tenant.property')}</label
										>
										<p class="text-gray-900 dark:text-white">{tenant.property?.name || '-'}</p>
									</div>
									<div>
										<label class="block text-sm font-medium text-gray-500 dark:text-gray-400"
											>{$t('tenant.monthlyRent')}</label
										>
										<p class="font-semibold text-gray-900 dark:text-white">
											{formatCurrency(tenant.monthly_rent)}
										</p>
									</div>
									<div>
										<label class="block text-sm font-medium text-gray-500 dark:text-gray-400"
											>{$t('tenant.securityDeposit')}</label
										>
										<p class="text-gray-900 dark:text-white">
											{formatCurrency(tenant.security_deposit)}
										</p>
									</div>
								</div>
							</div>

							<!-- Lease Dates -->
							<div>
								<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
									{$t('tenant.leaseDates')}
								</h3>
								<div class="space-y-3">
									<div>
										<label class="block text-sm font-medium text-gray-500 dark:text-gray-400"
											>{$t('tenant.leaseStart')}</label
										>
										<p class="text-gray-900 dark:text-white">{formatDate(tenant.lease_start)}</p>
									</div>
									<div>
										<label class="block text-sm font-medium text-gray-500 dark:text-gray-400"
											>{$t('tenant.leaseEnd')}</label
										>
										<p class="text-gray-900 dark:text-white">{formatDate(tenant.lease_end)}</p>
									</div>
									<div>
										<label class="block text-sm font-medium text-gray-500 dark:text-gray-400"
											>{$t('tenant.createdAt')}</label
										>
										<p class="text-gray-900 dark:text-white">{formatDate(tenant.created_at)}</p>
									</div>
								</div>
							</div>
						</div>

						<!-- Notes -->
						{#if tenant.notes}
							<div class="mt-8 border-t border-gray-200 pt-8 dark:border-gray-700">
								<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
									{$t('tenant.notes')}
								</h3>
								<div class="rounded-xl bg-gray-50 p-4 dark:bg-gray-700">
									<p class="whitespace-pre-wrap text-gray-700 dark:text-gray-300">{tenant.notes}</p>
								</div>
							</div>
						{/if}
					</div>
				</div>

				<!-- Quick Actions -->
				<div
					class="rounded-2xl border border-gray-200 bg-white p-6 shadow-xl dark:border-gray-700 dark:bg-gray-800"
				>
					<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
						{$t('tenant.quickActions')}
					</h3>
					<div class="grid grid-cols-2 gap-4 md:grid-cols-4">
						<Button
							variant="outline"
							class="flex h-auto flex-col items-center space-y-2 p-4"
							onclick={() => goto(`/property-management/tenants/${tenantId}/edit`)}
						>
							<div class="text-2xl">✏️</div>
							<span class="text-sm">{$t('tenant.editTenant')}</span>
						</Button>

						{#if tenant.property?.id}
							<Button
								variant="outline"
								class="flex h-auto flex-col items-center space-y-2 p-4"
								onclick={() => goto(`/property-management/properties/${tenant.property.id}`)}
							>
								<div class="text-2xl">🏠</div>
								<span class="text-sm">{$t('tenant.viewProperty')}</span>
							</Button>
						{/if}

						<Button
							variant="outline"
							class="flex h-auto flex-col items-center space-y-2 p-4"
							onclick={() => goto(`/property-management/maintenance?tenant=${tenantId}`)}
						>
							<div class="text-2xl">🔧</div>
							<span class="text-sm">{$t('tenant.viewMaintenance')}</span>
						</Button>

						<Button
							variant="outline"
							class="flex h-auto flex-col items-center space-y-2 p-4"
							onclick={() => goto(`/property-management/leases?tenant=${tenantId}`)}
						>
							<div class="text-2xl">📄</div>
							<span class="text-sm">{$t('tenant.viewLeases')}</span>
						</Button>
					</div>
				</div>
			</div>
		{:else}
			<!-- Not Found State -->
			<div
				class="mx-auto max-w-3xl rounded-2xl border-2 border-dashed border-gray-300 bg-gray-50 p-12 text-center dark:border-gray-600 dark:bg-gray-800"
			>
				<div class="mb-4 text-6xl">👤</div>
				<h3 class="mb-2 text-xl font-semibold text-gray-700 dark:text-gray-300">
					{$t('tenant.notFound')}
				</h3>
				<p class="mb-6 text-gray-500 dark:text-gray-400">{$t('tenant.notFoundDesc')}</p>
				<Button variant="primary" onclick={() => goto('/property-management/tenants')}>
					{$t('tenant.backToTenants')}
				</Button>
			</div>
		{/if}
	</div>
</div>

<!-- Delete Confirmation Modal -->
<Modal bind:show={showDeleteModal}>
	<div class="p-6">
		<div class="mb-4 flex items-center">
			<svg class="mr-3 h-8 w-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
				/>
			</svg>
			<h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
				{$t('tenant.confirmDelete')}
			</h3>
		</div>

		<p class="mb-6 text-gray-600 dark:text-gray-400">
			{$t('tenant.confirmDeleteMessage', { name: tenant?.name || '' })}
		</p>

		<div class="flex justify-end gap-3">
			<Button variant="outline" onclick={() => (showDeleteModal = false)} disabled={deleting}>
				{$t('common.cancel')}
			</Button>
			<Button variant="danger" onclick={handleDeleteTenant} disabled={deleting}>
				{#if deleting}
					<LoadingSpinner size="sm" color="white" class="mr-2" />
				{/if}
				{deleting ? $t('common.deleting') : $t('common.delete')}
			</Button>
		</div>
	</div>
</Modal>

<style>
	/* Enhanced hover effects */
	.group:hover {
		transform: translateY(-2px);
	}

	/* Custom gradient animations */
	@keyframes gradient-shift {
		0%,
		100% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 100% 50%;
		}
	}

	.bg-gradient-to-r {
		background-size: 200% 200%;
		animation: gradient-shift 8s ease infinite;
	}
</style>
