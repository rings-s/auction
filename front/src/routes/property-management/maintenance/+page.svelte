<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import { userStore } from '$lib/stores/user.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import { maintenanceAPI } from '$lib/api/propertyManagement.js';
	import { fade } from 'svelte/transition';

	// State
	let loading = true;
	let error = '';
	let maintenanceRequests = [];
	let searchTerm = '';
	let statusFilter = 'all';
	let priorityFilter = 'all';
	let showCreateModal = false;
	let pagination = {
		page: 1,
		pageSize: 10,
		total: 0,
		totalPages: 0
	};

	// Form state
	let formData = {
		title: '',
		description: '',
		priority: 'medium',
		status: 'pending',
		tenant: '',
		property: '',
		category: ''
	};

	$: user = $userStore;
	$: hasAccess =
		(user && ['owner', 'appraiser', 'data_entry'].includes(user.role)) || user?.is_superuser;

	// Filter requests based on search term and filters
	$: filteredRequests = maintenanceRequests.filter((request) => {
		const matchesSearch =
			request.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
			request.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
			request.property?.name?.toLowerCase().includes(searchTerm.toLowerCase());

		const matchesStatus = statusFilter === 'all' || request.status === statusFilter;
		const matchesPriority = priorityFilter === 'all' || request.priority === priorityFilter;

		return matchesSearch && matchesStatus && matchesPriority;
	});

	onMount(() => {
		if (!hasAccess) {
			goto('/dashboard');
			return;
		}
		loadMaintenanceRequests();
	});

	async function loadMaintenanceRequests() {
		try {
			loading = true;
			error = '';

			const response = await maintenanceAPI.requests.getAll({
				page: pagination.page,
				page_size: pagination.pageSize,
				search: searchTerm || undefined,
				status: statusFilter !== 'all' ? statusFilter : undefined,
				priority: priorityFilter !== 'all' ? priorityFilter : undefined,
				ordering: '-created_at'
			});

			if (response.data) {
				maintenanceRequests = response.data.results || [];
				pagination = {
					...pagination,
					total: response.data.count || 0,
					totalPages: Math.ceil((response.data.count || 0) / pagination.pageSize)
				};
			}
		} catch (err) {
			error = err.message || $t('errors.loadingFailed');
			console.error('Failed to load maintenance requests:', err);
		} finally {
			loading = false;
		}
	}

	async function handleCreateRequest() {
		try {
			const response = await maintenanceAPI.requests.create(formData);
			if (response.data) {
				maintenanceRequests = [response.data, ...maintenanceRequests];
				showCreateModal = false;
				resetForm();
			}
		} catch (err) {
			error = err.message || $t('errors.createFailed');
		}
	}

	async function handleDeleteRequest(requestId) {
		if (!confirm($t('common.confirmDelete'))) return;

		try {
			await maintenanceAPI.requests.delete(requestId);
			maintenanceRequests = maintenanceRequests.filter((r) => r.id !== requestId);
		} catch (err) {
			error = err.message || $t('errors.deleteFailed');
		}
	}

	async function handleUpdateStatus(requestId, newStatus) {
		try {
			const response = await maintenanceAPI.requests.patch(requestId, { status: newStatus });
			if (response.data) {
				maintenanceRequests = maintenanceRequests.map((r) =>
					r.id === requestId ? { ...r, status: newStatus } : r
				);
			}
		} catch (err) {
			error = err.message || $t('errors.updateFailed');
		}
	}

	function resetForm() {
		formData = {
			title: '',
			description: '',
			priority: 'medium',
			status: 'pending',
			tenant: '',
			property: '',
			category: ''
		};
	}

	function getStatusBadge(status) {
		const classes = {
			pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100',
			'in-progress': 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100',
			completed: 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100',
			cancelled: 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
		};
		return classes[status] || classes.pending;
	}

	function getPriorityBadge(priority) {
		const classes = {
			low: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100',
			medium: 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100',
			high: 'bg-orange-100 text-orange-800 dark:bg-orange-800 dark:text-orange-100',
			urgent: 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
		};
		return classes[priority] || classes.medium;
	}

	function getPriorityIcon(priority) {
		switch (priority) {
			case 'low':
				return '🔵';
			case 'medium':
				return '🟡';
			case 'high':
				return '🟠';
			case 'urgent':
				return '🔴';
			default:
				return '🟡';
		}
	}

	function formatDate(dateString) {
		return new Date(dateString).toLocaleDateString();
	}
</script>

<svelte:head>
	<title>{$t('maintenance.title')} | {$t('app.name')}</title>
	<meta name="description" content={$t('maintenance.description')} />
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
					{$t('maintenance.management')}
				</h1>
				<p class="mt-2 text-gray-600 dark:text-gray-400">
					{$t('maintenance.subtitle')}
				</p>
			</div>

			<div class="flex flex-wrap gap-4">
				<Button
					variant="primary"
					class="bg-gradient-to-r from-indigo-500 to-purple-600 shadow-lg hover:from-indigo-600 hover:to-purple-700 hover:shadow-xl"
					on:click={() => goto('/property-management/maintenance/create')}
				>
					<svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 6v6m0 0v6m0-6h6m-6 0H6"
						/>
					</svg>
					{$t('maintenance.create')}
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
						<p class="text-sm font-medium text-gray-600 dark:text-gray-400">
							{$t('maintenance.pending')}
						</p>
						<p class="text-2xl font-bold text-gray-900 dark:text-gray-100">
							{maintenanceRequests.filter((r) => r.status === 'pending').length}
						</p>
					</div>
					<div class="text-2xl">⏳</div>
				</div>
			</div>

			<div
				class="rounded-2xl border border-gray-200 bg-white p-6 shadow-md dark:border-gray-700 dark:bg-gray-800"
			>
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600 dark:text-gray-400">
							{$t('maintenance.inProgress')}
						</p>
						<p class="text-2xl font-bold text-gray-900 dark:text-gray-100">
							{maintenanceRequests.filter((r) => r.status === 'in-progress').length}
						</p>
					</div>
					<div class="text-2xl">🔧</div>
				</div>
			</div>

			<div
				class="rounded-2xl border border-gray-200 bg-white p-6 shadow-md dark:border-gray-700 dark:bg-gray-800"
			>
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600 dark:text-gray-400">
							{$t('maintenance.completed')}
						</p>
						<p class="text-2xl font-bold text-gray-900 dark:text-gray-100">
							{maintenanceRequests.filter((r) => r.status === 'completed').length}
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
							{$t('maintenance.urgent')}
						</p>
						<p class="text-2xl font-bold text-gray-900 dark:text-gray-100">
							{maintenanceRequests.filter((r) => r.priority === 'urgent').length}
						</p>
					</div>
					<div class="text-2xl">🚨</div>
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
						on:input={loadMaintenanceRequests}
						placeholder={$t('maintenance.searchPlaceholder')}
						class="w-full rounded-xl border border-gray-300 bg-white py-3 pr-4 pl-10 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
					/>
				</div>

				<div class="flex gap-4">
					<select
						bind:value={statusFilter}
						on:change={loadMaintenanceRequests}
						class="rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
					>
						<option value="all">{$t('maintenance.allStatuses')}</option>
						<option value="pending">{$t('maintenance.status.pending')}</option>
						<option value="in-progress">{$t('maintenance.status.inProgress')}</option>
						<option value="completed">{$t('maintenance.status.completed')}</option>
						<option value="cancelled">{$t('maintenance.status.cancelled')}</option>
					</select>

					<select
						bind:value={priorityFilter}
						on:change={loadMaintenanceRequests}
						class="rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
					>
						<option value="all">{$t('maintenance.allPriorities')}</option>
						<option value="low">{$t('maintenance.priority.low')}</option>
						<option value="medium">{$t('maintenance.priority.medium')}</option>
						<option value="high">{$t('maintenance.priority.high')}</option>
						<option value="urgent">{$t('maintenance.priority.urgent')}</option>
					</select>
				</div>
			</div>
		</div>

		<!-- Maintenance Requests List -->
		<div
			class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-md dark:border-gray-700 dark:bg-gray-800"
		>
			{#if loading}
				<div class="space-y-4 p-6">
					{#each Array(5) as _}
						<LoadingSkeleton height="120px" />
					{/each}
				</div>
			{:else if filteredRequests.length === 0}
				<div class="p-12 text-center">
					<div class="mb-4 text-6xl">🔧</div>
					<h3 class="mb-2 text-lg font-medium text-gray-900 dark:text-gray-100">
						{$t('maintenance.noRequests')}
					</h3>
					<p class="mb-6 text-gray-600 dark:text-gray-400">
						{$t('maintenance.noRequestsDesc')}
					</p>
					<Button
						variant="primary"
						on:click={() => goto('/property-management/maintenance/create')}
					>
						{$t('maintenance.createFirst')}
					</Button>
				</div>
			{:else}
				<div class="divide-y divide-gray-200 dark:divide-gray-700">
					{#each filteredRequests as request (request.id)}
						<div
							class="p-6 transition-colors duration-200 hover:bg-gray-50 dark:hover:bg-gray-700"
							in:fade={{ duration: 200 }}
						>
							<div class="flex items-start justify-between">
								<div class="flex flex-1 items-start space-x-4">
									<!-- Priority Icon -->
									<div class="mt-1 text-2xl">
										{getPriorityIcon(request.priority)}
									</div>

									<!-- Request Info -->
									<div class="min-w-0 flex-1">
										<div class="mb-2 flex items-center space-x-3">
											<h3
												class="font-sans text-lg font-semibold tracking-tight text-gray-900 dark:text-gray-100"
											>
												{request.title}
											</h3>
											<span
												class="inline-flex items-center rounded-xl px-3 py-1 text-xs font-medium {getPriorityBadge(
													request.priority
												)}"
											>
												{$t(`maintenance.priority.${request.priority}`)}
											</span>
											<span
												class="inline-flex items-center rounded-xl px-3 py-1 text-xs font-medium {getStatusBadge(
													request.status
												)}"
											>
												{$t(`maintenance.status.${request.status}`)}
											</span>
										</div>

										<p class="mb-3 line-clamp-2 text-gray-600 dark:text-gray-400">
											{request.description}
										</p>

										<div
											class="flex items-center space-x-6 text-sm text-gray-500 dark:text-gray-400"
										>
											{#if request.property}
												<div class="flex items-center space-x-1">
													<svg
														class="h-4 w-4"
														fill="none"
														stroke="currentColor"
														viewBox="0 0 24 24"
													>
														<path
															stroke-linecap="round"
															stroke-linejoin="round"
															stroke-width="2"
															d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
														/>
													</svg>
													<span>{request.property.name}</span>
												</div>
											{/if}

											{#if request.tenant}
												<div class="flex items-center space-x-1">
													<svg
														class="h-4 w-4"
														fill="none"
														stroke="currentColor"
														viewBox="0 0 24 24"
													>
														<path
															stroke-linecap="round"
															stroke-linejoin="round"
															stroke-width="2"
															d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
														/>
													</svg>
													<span>{request.tenant.name}</span>
												</div>
											{/if}

											<div class="flex items-center space-x-1">
												<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path
														stroke-linecap="round"
														stroke-linejoin="round"
														stroke-width="2"
														d="M8 7V3a1 1 0 011-1h6a1 1 0 011 1v4c0 .552-.448 1-1 1H9a1 1 0 01-1-1zM3 21h18l-9-9-9 9z"
													/>
												</svg>
												<span>{formatDate(request.created_at)}</span>
											</div>
										</div>
									</div>
								</div>

								<!-- Actions -->
								<div class="ml-4 flex items-center space-x-2">
									{#if request.status === 'pending'}
										<Button
											variant="outline"
											size="sm"
											class="text-blue-600 hover:bg-blue-50 hover:text-blue-700 dark:hover:bg-blue-900/20"
											on:click={() => handleUpdateStatus(request.id, 'in-progress')}
										>
											{$t('maintenance.startWork')}
										</Button>
									{:else if request.status === 'in-progress'}
										<Button
											variant="outline"
											size="sm"
											class="text-green-600 hover:bg-green-50 hover:text-green-700 dark:hover:bg-green-900/20"
											on:click={() => handleUpdateStatus(request.id, 'completed')}
										>
											{$t('maintenance.markComplete')}
										</Button>
									{/if}

									<Button
										variant="ghost"
										size="sm"
										on:click={() => goto(`/property-management/maintenance/${request.id}`)}
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
										class="text-red-600 hover:bg-red-50 hover:text-red-700 dark:hover:bg-red-900/20"
										on:click={() => handleDeleteRequest(request.id)}
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
						loadMaintenanceRequests();
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
						loadMaintenanceRequests();
					}}
				>
					{$t('common.next')}
				</Button>
			</div>
		{/if}
	</div>
{/if}
