<!-- src/lib/components/property-management/workers/WorkerList.svelte -->
<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/i18n';
	import { 
		getWorkers, 
		deleteWorker,
		getWorkerCategories,
		formatWorkerName,
		getWorkerStatusColor,
		formatHourlyRate,
		calculateWorkerPerformance,
		getEmploymentTypes,
		getWorkerStatuses
	} from '$lib/api/worker';
	import { toast } from '$lib/stores/toastStore.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';

	// Props
	export let filters = {};
	export let compact = false;
	export let maxItems = null;

	// Svelte 5 runes for reactive state
	let workers = $state([]);
	let categories = $state([]);
	let loading = $state(true);
	let error = $state(null);
	let selectedWorker = $state(null);
	let showDeleteModal = $state(false);
	let deleteLoading = $state(false);
	let sortField = $state('hire_date');
	let sortDirection = $state('desc');
	let filterCategory = $state('all');
	let filterStatus = $state('all');
	let filterEmploymentType = $state('all');
	let searchQuery = $state('');

	// Derived state
	let hasWorkers = $derived(workers.length > 0);
	let filteredWorkers = $derived(getFilteredWorkers());
	let displayedWorkers = $derived(
		maxItems ? filteredWorkers.slice(0, maxItems) : filteredWorkers
	);
	let employmentTypes = $derived(getEmploymentTypes());
	let workerStatuses = $derived(getWorkerStatuses());

	// Load workers on mount
	onMount(async () => {
		await loadWorkers();
	});

	// Watch for filter changes
	$effect(() => {
		if (filters) {
			loadWorkers();
		}
	});

	// Load workers function
	async function loadWorkers() {
		try {
			loading = true;
			error = null;
			
			const [workersData, categoriesData] = await Promise.all([
				getWorkers(filters),
				getWorkerCategories()
			]);
			
			workers = workersData;
			categories = categoriesData;
		} catch (err) {
			error = err.message;
			toast.error($t('worker.loadError'));
		} finally {
			loading = false;
		}
	}

	// Filter and sort workers
	function getFilteredWorkers() {
		let filtered = [...workers];

		// Apply search filter
		if (searchQuery.trim()) {
			const query = searchQuery.toLowerCase();
			filtered = filtered.filter(worker => 
				`${worker.first_name} ${worker.last_name}`.toLowerCase().includes(query) ||
				worker.email.toLowerCase().includes(query) ||
				worker.employee_id?.toLowerCase().includes(query) ||
				worker.categories?.some(cat => cat.name.toLowerCase().includes(query))
			);
		}

		// Apply category filter
		if (filterCategory !== 'all') {
			filtered = filtered.filter(worker => 
				worker.categories && worker.categories.some(cat => 
					cat.id === parseInt(filterCategory)
				)
			);
		}

		// Apply status filter
		if (filterStatus !== 'all') {
			filtered = filtered.filter(worker => worker.status === filterStatus);
		}

		// Apply employment type filter
		if (filterEmploymentType !== 'all') {
			filtered = filtered.filter(worker => worker.employment_type === filterEmploymentType);
		}

		// Apply sorting
		filtered.sort((a, b) => {
			let valueA = a[sortField];
			let valueB = b[sortField];

			// Handle different data types
			if (sortField.includes('date')) {
				valueA = new Date(valueA || 0);
				valueB = new Date(valueB || 0);
			} else if (sortField === 'hourly_rate') {
				valueA = parseFloat(valueA) || 0;
				valueB = parseFloat(valueB) || 0;
			} else if (sortField === 'name') {
				valueA = formatWorkerName(a).toLowerCase();
				valueB = formatWorkerName(b).toLowerCase();
			} else if (typeof valueA === 'string') {
				valueA = valueA.toLowerCase();
				valueB = valueB.toLowerCase();
			}

			if (sortDirection === 'asc') {
				return valueA > valueB ? 1 : valueA < valueB ? -1 : 0;
			} else {
				return valueA < valueB ? 1 : valueA > valueB ? -1 : 0;
			}
		});

		return filtered;
	}

	// Handle sorting
	function handleSort(field) {
		if (sortField === field) {
			sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
		} else {
			sortField = field;
			sortDirection = 'desc';
		}
	}

	// Delete worker
	async function handleDelete() {
		if (!selectedWorker) return;

		try {
			deleteLoading = true;
			await deleteWorker(selectedWorker.id);
			
			// Update local state
			workers = workers.filter(worker => worker.id !== selectedWorker.id);
			
			toast.success($t('worker.deleteSuccess'));
			showDeleteModal = false;
			selectedWorker = null;
		} catch (err) {
			toast.error($t('worker.deleteError'));
		} finally {
			deleteLoading = false;
		}
	}

	// Show delete confirmation
	function showDeleteConfirm(worker) {
		selectedWorker = worker;
		showDeleteModal = true;
	}

	// Cancel delete
	function cancelDelete() {
		showDeleteModal = false;
		selectedWorker = null;
	}

	// Format date for display
	function formatDate(dateString) {
		if (!dateString) return $t('common.notSet');
		return new Date(dateString).toLocaleDateString();
	}

	// Get status badge classes
	function getStatusBadgeClass(status) {
		const color = getWorkerStatusColor(status);
		const baseClass = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium';
		return `${baseClass} bg-${color}-100 text-${color}-800 dark:bg-${color}-900 dark:text-${color}-200`;
	}

	// Get availability indicator
	function getAvailabilityIndicator(worker) {
		if (!worker.is_available) return { color: 'gray', text: $t('worker.unavailable') };
		if (worker.status !== 'active') return { color: 'gray', text: $t('worker.inactive') };
		
		const activeJobs = worker.active_jobs_count || 0;
		const maxJobs = worker.max_concurrent_jobs || 0;
		
		if (activeJobs >= maxJobs) {
			return { color: 'red', text: $t('worker.atCapacity') };
		} else if (activeJobs > maxJobs * 0.8) {
			return { color: 'yellow', text: $t('worker.nearCapacity') };
		} else {
			return { color: 'green', text: $t('worker.available') };
		}
	}

	// Get performance indicator color
	function getPerformanceColor(worker) {
		const performance = calculateWorkerPerformance(worker);
		const completionRate = parseFloat(performance.completionRate);
		
		if (completionRate >= 90) return 'green';
		if (completionRate >= 80) return 'yellow';
		if (completionRate >= 70) return 'orange';
		return 'red';
	}
</script>

<svelte:head>
	<title>{$t('worker.list')} - {$t('app.name')}</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	{#if !compact}
		<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="text-2xl font-bold text-gray-900 dark:text-white">
					{$t('worker.list')}
				</h1>
				<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
					{$t('worker.listDescription')}
				</p>
			</div>
			
			<div class="mt-4 sm:mt-0 flex space-x-3">
				<Button 
					href="/dashboard/workers" 
					variant="outline"
				>
					<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
					</svg>
					{$t('worker.dashboard')}
				</Button>
				
				<Button 
					href="/create/worker" 
					variant="primary"
					class="w-full sm:w-auto"
				>
					<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
					</svg>
					{$t('worker.add')}
				</Button>
			</div>
		</div>
	{/if}

	<!-- Filters -->
	{#if !compact}
		<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
			<div class="grid grid-cols-1 gap-4 sm:grid-cols-5">
				<!-- Search -->
				<div>
					<label for="search" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
						{$t('common.search')}
					</label>
					<input
						type="text"
						id="search"
						bind:value={searchQuery}
						placeholder={$t('worker.searchPlaceholder')}
						class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
					/>
				</div>

				<!-- Category Filter -->
				<div>
					<label for="categoryFilter" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
						{$t('worker.category')}
					</label>
					<select
						id="categoryFilter"
						bind:value={filterCategory}
						class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
					>
						<option value="all">{$t('common.all')}</option>
						{#each categories as category}
							<option value={category.id}>{category.name}</option>
						{/each}
					</select>
				</div>

				<!-- Status Filter -->
				<div>
					<label for="statusFilter" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
						{$t('common.status')}
					</label>
					<select
						id="statusFilter"
						bind:value={filterStatus}
						class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
					>
						<option value="all">{$t('common.all')}</option>
						{#each workerStatuses as status}
							<option value={status.value}>{status.label}</option>
						{/each}
					</select>
				</div>

				<!-- Employment Type Filter -->
				<div>
					<label for="employmentFilter" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
						{$t('worker.employmentType')}
					</label>
					<select
						id="employmentFilter"
						bind:value={filterEmploymentType}
						class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
					>
						<option value="all">{$t('common.all')}</option>
						{#each employmentTypes as type}
							<option value={type.value}>{type.label}</option>
						{/each}
					</select>
				</div>

				<!-- Results Count -->
				<div class="flex items-end">
					<p class="text-sm text-gray-600 dark:text-gray-400">
						{$t('common.showing')} {displayedWorkers.length} {$t('common.of')} {filteredWorkers.length}
					</p>
				</div>
			</div>
		</div>
	{/if}

	<!-- Error Alert -->
	{#if error}
		<Alert type="error" title={$t('error.title')} message={error} dismissible />
	{/if}

	<!-- Loading State -->
	{#if loading}
		<div class="space-y-4">
			{#each Array(5) as _}
				<LoadingSkeleton type="rect" height="80px" />
			{/each}
		</div>
	
	<!-- Empty State -->
	{:else if !hasWorkers}
		<div class="text-center py-12">
			<svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
					d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
			</svg>
			<h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">
				{$t('worker.noWorkers')}
			</h3>
			<p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
				{$t('worker.noWorkersDesc')}
			</p>
			<div class="mt-6">
				<Button href="/create/worker" variant="primary">
					{$t('worker.addFirst')}
				</Button>
			</div>
		</div>
	
	<!-- Worker Table -->
	{:else}
		<div class="bg-white dark:bg-gray-800 shadow-sm rounded-lg overflow-hidden">
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
					<thead class="bg-gray-50 dark:bg-gray-700">
						<tr>
							<!-- Worker Name -->
							<th class="px-6 py-3 text-left">
								<button
									onclick={() => handleSort('name')}
									class="group flex items-center space-x-1 text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider hover:text-gray-700 dark:hover:text-gray-100"
								>
									<span>{$t('worker.name')}</span>
									<svg class="h-4 w-4 {sortField === 'name' ? 'text-gray-700 dark:text-gray-100' : 'text-gray-400'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
									</svg>
								</button>
							</th>

							<!-- Categories -->
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
								{$t('worker.categories')}
							</th>

							<!-- Employment -->
							<th class="px-6 py-3 text-left">
								<button
									onclick={() => handleSort('employment_type')}
									class="group flex items-center space-x-1 text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider hover:text-gray-700 dark:hover:text-gray-100"
								>
									<span>{$t('worker.employment')}</span>
									<svg class="h-4 w-4 {sortField === 'employment_type' ? 'text-gray-700 dark:text-gray-100' : 'text-gray-400'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
									</svg>
								</button>
							</th>

							<!-- Hourly Rate -->
							<th class="px-6 py-3 text-left">
								<button
									onclick={() => handleSort('hourly_rate')}
									class="group flex items-center space-x-1 text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider hover:text-gray-700 dark:hover:text-gray-100"
								>
									<span>{$t('worker.rate')}</span>
									<svg class="h-4 w-4 {sortField === 'hourly_rate' ? 'text-gray-700 dark:text-gray-100' : 'text-gray-400'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
									</svg>
								</button>
							</th>

							<!-- Status -->
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
								{$t('common.status')}
							</th>

							<!-- Availability -->
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
								{$t('worker.availability')}
							</th>

							<!-- Performance -->
							<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
								{$t('worker.performance')}
							</th>

							<!-- Hire Date -->
							<th class="px-6 py-3 text-left">
								<button
									onclick={() => handleSort('hire_date')}
									class="group flex items-center space-x-1 text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider hover:text-gray-700 dark:hover:text-gray-100"
								>
									<span>{$t('worker.hireDate')}</span>
									<svg class="h-4 w-4 {sortField === 'hire_date' ? 'text-gray-700 dark:text-gray-100' : 'text-gray-400'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
									</svg>
								</button>
							</th>

							<!-- Actions -->
							<th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
								{$t('common.actions')}
							</th>
						</tr>
					</thead>
					<tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
						{#each displayedWorkers as worker (worker.id)}
							{@const availability = getAvailabilityIndicator(worker)}
							{@const performance = calculateWorkerPerformance(worker)}
							<tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
								<!-- Worker Name -->
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="flex items-center">
										<div class="flex-shrink-0 h-10 w-10">
											<div class="h-10 w-10 rounded-full bg-primary-100 dark:bg-primary-800 flex items-center justify-center">
												<span class="text-sm font-medium text-primary-800 dark:text-primary-200">
													{formatWorkerName(worker).charAt(0)}
												</span>
											</div>
										</div>
										<div class="ml-4">
											<div class="text-sm font-medium text-gray-900 dark:text-white">
												{formatWorkerName(worker)}
											</div>
											<div class="text-sm text-gray-500 dark:text-gray-400">
												{worker.email}
											</div>
											{#if worker.employee_id}
												<div class="text-xs text-gray-400 font-mono">
													ID: {worker.employee_id}
												</div>
											{/if}
										</div>
									</div>
								</td>

								<!-- Categories -->
								<td class="px-6 py-4 whitespace-nowrap">
									{#if worker.categories && worker.categories.length > 0}
										<div class="flex flex-wrap gap-1">
											{#each worker.categories.slice(0, 2) as category}
												<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200">
													{category.name}
												</span>
											{/each}
											{#if worker.categories.length > 2}
												<span class="text-xs text-gray-500">
													+{worker.categories.length - 2}
												</span>
											{/if}
										</div>
									{:else}
										<span class="text-sm text-gray-500 dark:text-gray-400">
											{$t('worker.noCategories')}
										</span>
									{/if}
								</td>

								<!-- Employment -->
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="text-sm text-gray-900 dark:text-white">
										{employmentTypes.find(t => t.value === worker.employment_type)?.label || worker.employment_type}
									</div>
									{#if worker.hire_date}
										<div class="text-xs text-gray-500">
											{formatDate(worker.hire_date)}
										</div>
									{/if}
								</td>

								<!-- Hourly Rate -->
								<td class="px-6 py-4 whitespace-nowrap">
									{#if worker.hourly_rate}
										<span class="text-sm font-medium text-gray-900 dark:text-white">
											{formatHourlyRate(worker.hourly_rate)}
										</span>
									{:else}
										<span class="text-sm text-gray-500 dark:text-gray-400">
											{$t('common.notSet')}
										</span>
									{/if}
								</td>

								<!-- Status -->
								<td class="px-6 py-4 whitespace-nowrap">
									<span class={getStatusBadgeClass(worker.status)}>
										{workerStatuses.find(s => s.value === worker.status)?.label || worker.status}
									</span>
								</td>

								<!-- Availability -->
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="flex items-center">
										<div class="flex-shrink-0 w-2.5 h-2.5 rounded-full bg-{availability.color}-400 mr-2"></div>
										<span class="text-sm text-gray-900 dark:text-white">
											{availability.text}
										</span>
									</div>
									<div class="text-xs text-gray-500 mt-1">
										{worker.active_jobs_count || 0}/{worker.max_concurrent_jobs || 0} {$t('worker.jobs')}
									</div>
								</td>

								<!-- Performance -->
								<td class="px-6 py-4 whitespace-nowrap">
									{#if performance.totalJobs > 0}
										<div class="flex items-center">
											<div class="flex-shrink-0 w-2.5 h-2.5 rounded-full bg-{getPerformanceColor(worker)}-400 mr-2"></div>
											<span class="text-sm font-medium text-gray-900 dark:text-white">
												{performance.completionRate}%
											</span>
										</div>
										<div class="text-xs text-gray-500">
											{performance.totalJobs} {$t('worker.jobs')} | {performance.averageRating}/5 ⭐
										</div>
									{:else}
										<span class="text-sm text-gray-500 dark:text-gray-400">
											{$t('worker.noData')}
										</span>
									{/if}
								</td>

								<!-- Hire Date -->
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
									{formatDate(worker.hire_date)}
								</td>

								<!-- Actions -->
								<td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
									<Button 
										href="/workers/{worker.id}"
										variant="outline"
										size="compact"
									>
										{$t('common.view')}
									</Button>
									
									<Button 
										href="/workers/{worker.id}/edit"
										variant="outline"
										size="compact"
									>
										{$t('common.edit')}
									</Button>
									
									<Button 
										onClick={() => showDeleteConfirm(worker)}
										variant="outline"
										size="compact"
										class="text-red-600 hover:text-red-700 hover:border-red-300"
									>
										{$t('common.delete')}
									</Button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{/if}

	<!-- Show more button if maxItems is set -->
	{#if maxItems && filteredWorkers.length > maxItems}
		<div class="text-center">
			<Button 
				href="/dashboard/workers"
				variant="outline"
			>
				{$t('common.viewAll')} ({filteredWorkers.length})
			</Button>
		</div>
	{/if}
</div>

<!-- Delete Confirmation Modal -->
<Modal 
	show={showDeleteModal} 
	title={$t('worker.deleteConfirm')}
	onClose={cancelDelete}
>
	<div class="space-y-4">
		<p class="text-sm text-gray-600 dark:text-gray-400">
			{$t('worker.deleteWarning')}
		</p>
		
		{#if selectedWorker}
			<div class="rounded-md bg-gray-50 p-4 dark:bg-gray-700">
				<div class="space-y-2">
					<p class="font-medium text-gray-900 dark:text-white">
						{formatWorkerName(selectedWorker)}
					</p>
					<p class="text-sm text-gray-600 dark:text-gray-400">
						{selectedWorker.email}
					</p>
					{#if selectedWorker.categories && selectedWorker.categories.length > 0}
						<p class="text-sm text-gray-600 dark:text-gray-400">
							{$t('worker.categories')}: {selectedWorker.categories.map(c => c.name).join(', ')}
						</p>
					{/if}
					{#if selectedWorker.active_jobs_count > 0}
						<p class="text-sm text-yellow-600 dark:text-yellow-400">
							⚠️ {$t('worker.hasActiveJobs', { count: selectedWorker.active_jobs_count })}
						</p>
					{/if}
				</div>
			</div>
		{/if}

		<div class="flex space-x-3 pt-4">
			<Button 
				onClick={cancelDelete}
				variant="outline" 
				class="flex-1"
			>
				{$t('common.cancel')}
			</Button>
			<Button 
				onClick={handleDelete}
				variant="primary"
				loading={deleteLoading}
				class="flex-1 bg-red-600 hover:bg-red-700"
			>
				{$t('common.delete')}
			</Button>
		</div>
	</div>
</Modal>