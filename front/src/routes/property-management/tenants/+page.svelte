<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { t } from '$lib/i18n';
	import { userStore } from '$lib/stores/user.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import { tenantsAPI } from '$lib/api/propertyManagement.js';
	import { fade, scale } from 'svelte/transition';

	// State
	let loading = true;
	let error = '';
	let tenants = [];
	let searchTerm = '';
	let showCreateModal = false;
	let pagination = {
		page: 1,
		pageSize: 10,
		total: 0,
		totalPages: 0
	};

	// Form state
	let formData = {
		name: '',
		email: '',
		phone: '',
		property: null,
		lease_start: '',
		lease_end: '',
		monthly_rent: '',
		security_deposit: '',
		status: 'active',
		emergency_contact: '',
		notes: ''
	};

	$: user = $userStore;
	$: hasAccess =
		(user && ['owner', 'appraiser', 'data_entry'].includes(user.role)) || user?.is_superuser;

	// Filter tenants based on search term
	$: filteredTenants = tenants.filter(
		(tenant) =>
			tenant.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
			tenant.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
			tenant.property?.name?.toLowerCase().includes(searchTerm.toLowerCase())
	);

	onMount(() => {
		if (!hasAccess) {
			goto('/dashboard');
			return;
		}
		loadTenants();
	});

	async function loadTenants() {
		try {
			loading = true;
			error = '';

			const response = await tenantsAPI.getAll({
				page: pagination.page,
				page_size: pagination.pageSize,
				search: searchTerm || undefined,
				ordering: '-created_at'
			});

			if (response.data) {
				tenants = response.data.results || [];
				pagination = {
					...pagination,
					total: response.data.count || 0,
					totalPages: Math.ceil((response.data.count || 0) / pagination.pageSize)
				};
			}
		} catch (err) {
			error = err.message || $t('errors.loadingFailed');
			console.error('Failed to load tenants:', err);
		} finally {
			loading = false;
		}
	}

	async function handleCreateTenant() {
		try {
			const response = await tenantsAPI.create(formData);
			if (response.data) {
				tenants = [response.data, ...tenants];
				showCreateModal = false;
				resetForm();
			}
		} catch (err) {
			error = err.message || $t('errors.createFailed');
		}
	}

	async function handleDeleteTenant(tenantId) {
		if (!confirm($t('common.confirmDelete'))) return;

		try {
			await tenantsAPI.delete(tenantId);
			tenants = tenants.filter((t) => t.id !== tenantId);
		} catch (err) {
			error = err.message || $t('errors.deleteFailed');
		}
	}

	function resetForm() {
		formData = {
			name: '',
			email: '',
			phone: '',
			property: null,
			lease_start: '',
			lease_end: '',
			monthly_rent: '',
			security_deposit: '',
			status: 'active',
			emergency_contact: '',
			notes: ''
		};
	}

	function getStatusBadge(status) {
		const classes = {
			active: 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100',
			inactive: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100',
			pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100'
		};
		return classes[status] || classes.inactive;
	}
</script>

<svelte:head>
	<title>{$t('tenant.title')} | {$t('app.name')}</title>
	<meta name="description" content={$t('tenant.description')} />
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
					{$t('tenant.management')}
				</h1>
				<p class="mt-2 text-gray-600 dark:text-gray-400">
					{$t('tenant.subtitle')}
				</p>
			</div>

			<div class="flex flex-wrap gap-4">
				<Button
					variant="primary"
					class="bg-gradient-to-r from-indigo-500 to-purple-600 shadow-lg hover:from-indigo-600 hover:to-purple-700 hover:shadow-xl"
					on:click={() => (showCreateModal = true)}
				>
					<svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 6v6m0 0v6m0-6h6m-6 0H6"
						/>
					</svg>
					{$t('tenant.create')}
				</Button>
			</div>
		</div>

		<!-- Error Display -->
		{#if error}
			<Alert type="error" message={error} />
		{/if}

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
						on:input={loadTenants}
						placeholder={$t('tenant.searchPlaceholder')}
						class="w-full rounded-xl border border-gray-300 bg-white py-3 pr-4 pl-10 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
					/>
				</div>

				<Button variant="outline" class="flex items-center gap-2">
					<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.414A1 1 0 013 6.707V4z"
						/>
					</svg>
					{$t('common.filter')}
				</Button>
			</div>
		</div>

		<!-- Tenants Grid/List -->
		<div
			class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-md dark:border-gray-700 dark:bg-gray-800"
		>
			{#if loading}
				<div class="space-y-4 p-6">
					{#each Array(5) as _}
						<LoadingSkeleton height="80px" />
					{/each}
				</div>
			{:else if filteredTenants.length === 0}
				<div class="p-12 text-center">
					<div class="mb-4 text-6xl">👥</div>
					<h3 class="mb-2 text-lg font-medium text-gray-900 dark:text-gray-100">
						{$t('tenant.noTenants')}
					</h3>
					<p class="mb-6 text-gray-600 dark:text-gray-400">
						{$t('tenant.noTenantsDesc')}
					</p>
					<Button variant="primary" on:click={() => (showCreateModal = true)}>
						{$t('tenant.createFirst')}
					</Button>
				</div>
			{:else}
				<div class="divide-y divide-gray-200 dark:divide-gray-700">
					{#each filteredTenants as tenant (tenant.id)}
						<div
							class="p-6 transition-colors duration-200 hover:bg-gray-50 dark:hover:bg-gray-700"
							in:fade={{ duration: 200 }}
						>
							<div class="flex items-center justify-between">
								<div class="flex items-center space-x-4">
									<!-- Avatar -->
									<div
										class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 text-lg font-semibold text-white"
									>
										{tenant.name?.charAt(0)?.toUpperCase() || 'T'}
									</div>

									<!-- Tenant Info -->
									<div>
										<h3
											class="font-sans text-lg font-semibold tracking-tight text-gray-900 dark:text-gray-100"
										>
											{tenant.name}
										</h3>
										<div
											class="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400"
										>
											<span>{tenant.email}</span>
											<span>•</span>
											<span>{tenant.phone}</span>
											{#if tenant.property}
												<span>•</span>
												<span>{tenant.property.name}</span>
											{/if}
										</div>
										<div class="mt-1 flex items-center space-x-4">
											<span
												class="inline-flex items-center rounded-xl px-3 py-1 text-xs font-medium {getStatusBadge(
													tenant.status
												)}"
											>
												{$t(`tenant.status.${tenant.status}`)}
											</span>
											{#if tenant.monthly_rent}
												<span class="text-sm text-gray-600 dark:text-gray-400">
													{tenant.monthly_rent} SAR/month
												</span>
											{/if}
										</div>
									</div>
								</div>

								<!-- Actions -->
								<div class="flex items-center space-x-2">
									<Button
										variant="ghost"
										size="sm"
										on:click={() => goto(`/property-management/tenants/${tenant.id}`)}
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
										on:click={() => goto(`/property-management/tenants/${tenant.id}/edit`)}
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
									<Button
										variant="ghost"
										size="sm"
										class="text-red-600 hover:bg-red-50 hover:text-red-700 dark:hover:bg-red-900/20"
										on:click={() => handleDeleteTenant(tenant.id)}
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
						loadTenants();
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
						loadTenants();
					}}
				>
					{$t('common.next')}
				</Button>
			</div>
		{/if}
	</div>

	<!-- Create Tenant Modal -->
	<Modal bind:show={showCreateModal} title={$t('tenant.create')}>
		<form on:submit|preventDefault={handleCreateTenant} class="space-y-6">
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
				<div>
					<label for="name" class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
						{$t('tenant.name')} *
					</label>
					<input
						type="text"
						id="name"
						bind:value={formData.name}
						required
						class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
						placeholder={$t('tenant.namePlaceholder')}
					/>
				</div>

				<div>
					<label
						for="email"
						class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('tenant.email')} *
					</label>
					<input
						type="email"
						id="email"
						bind:value={formData.email}
						required
						class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
						placeholder={$t('tenant.emailPlaceholder')}
					/>
				</div>

				<div>
					<label
						for="phone"
						class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('tenant.phone')}
					</label>
					<input
						type="tel"
						id="phone"
						bind:value={formData.phone}
						class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
						placeholder={$t('tenant.phonePlaceholder')}
					/>
				</div>

				<div>
					<label
						for="monthly_rent"
						class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('tenant.monthlyRent')}
					</label>
					<input
						type="number"
						id="monthly_rent"
						bind:value={formData.monthly_rent}
						min="0"
						step="0.01"
						class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
						placeholder="0.00"
					/>
				</div>

				<div>
					<label
						for="lease_start"
						class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('tenant.leaseStart')}
					</label>
					<input
						type="date"
						id="lease_start"
						bind:value={formData.lease_start}
						class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
					/>
				</div>

				<div>
					<label
						for="lease_end"
						class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('tenant.leaseEnd')}
					</label>
					<input
						type="date"
						id="lease_end"
						bind:value={formData.lease_end}
						class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
					/>
				</div>
			</div>

			<div>
				<label
					for="emergency_contact"
					class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
				>
					{$t('tenant.emergencyContact')}
				</label>
				<input
					type="text"
					id="emergency_contact"
					bind:value={formData.emergency_contact}
					class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
					placeholder={$t('tenant.emergencyContactPlaceholder')}
				/>
			</div>

			<div>
				<label for="notes" class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
					{$t('tenant.notes')}
				</label>
				<textarea
					id="notes"
					bind:value={formData.notes}
					rows="3"
					class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
					placeholder={$t('tenant.notesPlaceholder')}
				></textarea>
			</div>

			<div class="flex justify-end space-x-4 border-t border-gray-200 pt-6 dark:border-gray-700">
				<Button type="button" variant="outline" on:click={() => (showCreateModal = false)}>
					{$t('common.cancel')}
				</Button>
				<Button
					type="submit"
					variant="primary"
					class="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700"
				>
					{$t('tenant.create')}
				</Button>
			</div>
		</form>
	</Modal>
{/if}
