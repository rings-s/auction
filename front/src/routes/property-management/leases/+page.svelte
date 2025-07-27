<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import { userStore } from '$lib/stores/user.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import { leasesAPI } from '$lib/api/propertyManagement.js';
	import { fade } from 'svelte/transition';

	// State
	let loading = true;
	let error = '';
	let leases = [];
	let searchTerm = '';
	let statusFilter = 'all';
	let pagination = {
		page: 1,
		pageSize: 10,
		total: 0,
		totalPages: 0
	};

	$: user = $userStore;
	$: hasAccess =
		(user && ['owner', 'appraiser', 'data_entry'].includes(user.role)) || user?.is_superuser;

	// Filter leases based on search term and status
	$: filteredLeases = leases.filter((lease) => {
		const matchesSearch =
			lease.tenant?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
			lease.property?.name?.toLowerCase().includes(searchTerm.toLowerCase());

		const matchesStatus = statusFilter === 'all' || lease.status === statusFilter;

		return matchesSearch && matchesStatus;
	});

	onMount(() => {
		if (!hasAccess) {
			goto('/dashboard');
			return;
		}
		loadLeases();
	});

	async function loadLeases() {
		try {
			loading = true;
			error = '';

			const response = await leasesAPI.getAll({
				page: pagination.page,
				page_size: pagination.pageSize,
				search: searchTerm || undefined,
				status: statusFilter !== 'all' ? statusFilter : undefined,
				ordering: '-start_date'
			});

			if (response.data) {
				leases = response.data.results || [];
				pagination = {
					...pagination,
					total: response.data.count || 0,
					totalPages: Math.ceil((response.data.count || 0) / pagination.pageSize)
				};
			}
		} catch (err) {
			error = err.message || $t('errors.loadingFailed');
			console.error('Failed to load leases:', err);
		} finally {
			loading = false;
		}
	}

	async function handleDeleteLease(leaseId) {
		if (!confirm($t('common.confirmDelete'))) return;

		try {
			await leasesAPI.delete(leaseId);
			leases = leases.filter((l) => l.id !== leaseId);
		} catch (err) {
			error = err.message || $t('errors.deleteFailed');
		}
	}

	function getStatusBadge(status) {
		const classes = {
			active: 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100',
			expired: 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100',
			terminated: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100',
			pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100'
		};
		return classes[status] || classes.pending;
	}

	function formatDate(dateString) {
		return new Date(dateString).toLocaleDateString();
	}

	function isExpiringSoon(lease) {
		if (lease.status !== 'active') return false;
		const endDate = new Date(lease.end_date);
		const today = new Date();
		const daysUntilExpiry = Math.ceil((endDate - today) / (1000 * 60 * 60 * 24));
		return daysUntilExpiry <= 30 && daysUntilExpiry > 0;
	}

	function getDaysUntilExpiry(lease) {
		const endDate = new Date(lease.end_date);
		const today = new Date();
		return Math.ceil((endDate - today) / (1000 * 60 * 60 * 24));
	}
</script>

<svelte:head>
	<title>{$t('lease.title')} | {$t('app.name')}</title>
	<meta name="description" content={$t('lease.description')} />
</svelte:head>

{#if !hasAccess}
	<div class="flex min-h-screen items-center justify-center">
		<Alert type="error" message={$t('errors.accessDenied')} />
	</div>
{:else}
	<div class="container mx-auto space-y-8 px-4 py-8">
		<!-- Header -->
		<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="text-3xl font-bold tracking-tight text-gray-800 dark:text-gray-100">
					{$t('lease.management')}
				</h1>
				<p class="mt-2 text-gray-600 dark:text-gray-400">
					{$t('lease.subtitle')}
				</p>
			</div>

			<div class="flex flex-wrap gap-4">
				<Button
					variant="primary"
					class="bg-gradient-to-r from-indigo-500 to-purple-600 shadow-lg hover:from-indigo-600 hover:to-purple-700 hover:shadow-xl"
					on:click={() => goto('/property-management/leases/create')}
				>
					<svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 6v6m0 0v6m0-6h6m-6 0H6"
						/>
					</svg>
					{$t('lease.create')}
				</Button>
			</div>
		</div>

		<!-- Error Display -->
		{#if error}
			<Alert type="error" message={error} />
		{/if}

		<!-- Stats Cards -->
		<div class="grid grid-cols-1 gap-6 md:grid-cols-4">
			<div
				class="rounded-2xl border border-gray-200 bg-white p-6 shadow-md dark:border-gray-700 dark:bg-gray-800"
			>
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600 dark:text-gray-400">{$t('lease.active')}</p>
						<p class="text-2xl font-bold text-gray-900 dark:text-gray-100">
							{leases.filter((l) => l.status === 'active').length}
						</p>
					</div>
					<div class="text-2xl">✅</div>
				</div>
			</div>

			<div
				class="rounded-2xl border border-gray-200 bg-white p-6 shadow-md dark:border-gray-700 dark:bg-gray-800"
			>
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600 dark:text-gray-400">
							{$t('lease.expiringSoon')}
						</p>
						<p class="text-2xl font-bold text-gray-900 dark:text-gray-100">
							{leases.filter((l) => isExpiringSoon(l)).length}
						</p>
					</div>
					<div class="text-2xl">⚠️</div>
				</div>
			</div>

			<div
				class="rounded-2xl border border-gray-200 bg-white p-6 shadow-md dark:border-gray-700 dark:bg-gray-800"
			>
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600 dark:text-gray-400">
							{$t('lease.expired')}
						</p>
						<p class="text-2xl font-bold text-gray-900 dark:text-gray-100">
							{leases.filter((l) => l.status === 'expired').length}
						</p>
					</div>
					<div class="text-2xl">❌</div>
				</div>
			</div>

			<div
				class="rounded-2xl border border-gray-200 bg-white p-6 shadow-md dark:border-gray-700 dark:bg-gray-800"
			>
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600 dark:text-gray-400">
							{$t('lease.totalRevenue')}
						</p>
						<p class="text-2xl font-bold text-gray-900 dark:text-gray-100">
							{leases
								.filter((l) => l.status === 'active')
								.reduce((sum, l) => sum + (l.monthly_rent || 0), 0)
								.toLocaleString()} SAR
						</p>
					</div>
					<div class="text-2xl">💰</div>
				</div>
			</div>
		</div>

		<!-- Search and Filters -->
		<div
			class="rounded-2xl border border-gray-200 bg-white p-6 shadow-md dark:border-gray-700 dark:bg-gray-800"
		>
			<div class="flex flex-col gap-4 sm:flex-row sm:items-center">
				<div class="relative flex-1">
					<svg
						class="absolute top-1/2 left-3 h-5 w-5 -translate-y-1/2 text-gray-400"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
						/>
					</svg>
					<input
						type="text"
						bind:value={searchTerm}
						on:input={loadLeases}
						placeholder={$t('lease.searchPlaceholder')}
						class="w-full rounded-xl border border-gray-300 bg-white py-3 pr-4 pl-10 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
					/>
				</div>

				<select
					bind:value={statusFilter}
					on:change={loadLeases}
					class="rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
				>
					<option value="all">{$t('lease.allStatuses')}</option>
					<option value="active">{$t('lease.status.active')}</option>
					<option value="expired">{$t('lease.status.expired')}</option>
					<option value="terminated">{$t('lease.status.terminated')}</option>
					<option value="pending">{$t('lease.status.pending')}</option>
				</select>
			</div>
		</div>

		<!-- Leases List -->
		<div
			class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-md dark:border-gray-700 dark:bg-gray-800"
		>
			{#if loading}
				<div class="space-y-4 p-6">
					{#each Array(5) as _}
						<LoadingSkeleton height="120px" />
					{/each}
				</div>
			{:else if filteredLeases.length === 0}
				<div class="p-12 text-center">
					<div class="mb-4 text-6xl">📄</div>
					<h3 class="mb-2 text-lg font-medium text-gray-900 dark:text-gray-100">
						{$t('lease.noLeases')}
					</h3>
					<p class="mb-6 text-gray-600 dark:text-gray-400">
						{$t('lease.noLeasesDesc')}
					</p>
					<Button variant="primary" on:click={() => goto('/property-management/leases/create')}>
						{$t('lease.createFirst')}
					</Button>
				</div>
			{:else}
				<div class="divide-y divide-gray-200 dark:divide-gray-700">
					{#each filteredLeases as lease (lease.id)}
						<div
							class="p-6 transition-colors duration-200 hover:bg-gray-50 dark:hover:bg-gray-700"
							in:fade={{ duration: 200 }}
						>
							<div class="flex items-start justify-between">
								<div class="flex flex-1 items-start space-x-4">
									<!-- Document Icon -->
									<div
										class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 text-xl text-white"
									>
										📄
									</div>

									<!-- Lease Info -->
									<div class="min-w-0 flex-1">
										<div class="mb-2 flex items-center space-x-3">
											<h3
												class="font-sans text-lg font-semibold tracking-tight text-gray-900 dark:text-gray-100"
											>
												{lease.tenant?.name} - {lease.property?.name}
											</h3>
											<span
												class="inline-flex items-center rounded-xl px-3 py-1 text-xs font-medium {getStatusBadge(
													lease.status
												)}"
											>
												{$t(`lease.status.${lease.status}`)}
											</span>
											{#if isExpiringSoon(lease)}
												<span
													class="inline-flex items-center rounded-xl bg-orange-100 px-3 py-1 text-xs font-medium text-orange-800 dark:bg-orange-800 dark:text-orange-100"
												>
													{$t('lease.expiring')} ({getDaysUntilExpiry(lease)}
													{$t('common.days')})
												</span>
											{/if}
										</div>

										<div
											class="grid grid-cols-2 gap-4 text-sm text-gray-600 md:grid-cols-4 dark:text-gray-400"
										>
											<div>
												<p class="font-medium text-gray-900 dark:text-gray-100">
													{$t('lease.startDate')}
												</p>
												<p>{formatDate(lease.start_date)}</p>
											</div>
											<div>
												<p class="font-medium text-gray-900 dark:text-gray-100">
													{$t('lease.endDate')}
												</p>
												<p>{formatDate(lease.end_date)}</p>
											</div>
											<div>
												<p class="font-medium text-gray-900 dark:text-gray-100">
													{$t('lease.monthlyRent')}
												</p>
												<p>{lease.monthly_rent?.toLocaleString() || 0} SAR</p>
											</div>
											<div>
												<p class="font-medium text-gray-900 dark:text-gray-100">
													{$t('lease.securityDeposit')}
												</p>
												<p>{lease.security_deposit?.toLocaleString() || 0} SAR</p>
											</div>
										</div>

										{#if lease.property?.address}
											<div
												class="mt-2 flex items-center space-x-1 text-sm text-gray-500 dark:text-gray-400"
											>
												<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path
														stroke-linecap="round"
														stroke-linejoin="round"
														stroke-width="2"
														d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
													/>
													<path
														stroke-linecap="round"
														stroke-linejoin="round"
														stroke-width="2"
														d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
													/>
												</svg>
												<span>{lease.property.address}</span>
											</div>
										{/if}
									</div>
								</div>

								<!-- Actions -->
								<div class="ml-4 flex items-center space-x-2">
									<Button
										variant="ghost"
										size="sm"
										on:click={() => goto(`/property-management/leases/${lease.id}`)}
									>
										<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
											/>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
											/>
										</svg>
									</Button>
									<Button
										variant="ghost"
										size="sm"
										on:click={() => goto(`/property-management/leases/${lease.id}/edit`)}
									>
										<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
											/>
										</svg>
									</Button>
									{#if lease.status === 'active' && isExpiringSoon(lease)}
										<Button
											variant="outline"
											size="sm"
											class="text-orange-600 hover:bg-orange-50 hover:text-orange-700 dark:hover:bg-orange-900/20"
											on:click={() => goto(`/property-management/leases/${lease.id}/renew`)}
										>
											<svg
												class="mr-1 h-4 w-4"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
												/>
											</svg>
											{$t('lease.renew')}
										</Button>
									{/if}
									<Button
										variant="ghost"
										size="sm"
										class="text-red-600 hover:bg-red-50 hover:text-red-700 dark:hover:bg-red-900/20"
										on:click={() => handleDeleteLease(lease.id)}
									>
										<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
											/>
										</svg>
									</Button>
								</div>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Pagination -->
		{#if pagination.totalPages > 1}
			<div class="flex justify-center space-x-2">
				<Button
					variant="outline"
					disabled={pagination.page <= 1}
					on:click={() => {
						pagination.page--;
						loadLeases();
					}}
				>
					{$t('common.previous')}
				</Button>
				<span class="flex items-center px-4 py-2 text-sm text-gray-600 dark:text-gray-400">
					{$t('common.pageOf', { current: pagination.page, total: pagination.totalPages })}
				</span>
				<Button
					variant="outline"
					disabled={pagination.page >= pagination.totalPages}
					on:click={() => {
						pagination.page++;
						loadLeases();
					}}
				>
					{$t('common.next')}
				</Button>
			</div>
		{/if}
	</div>
{/if}
