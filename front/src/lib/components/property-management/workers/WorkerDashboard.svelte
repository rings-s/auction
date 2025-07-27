<!-- src/lib/components/property-management/workers/WorkerDashboard.svelte -->
<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/i18n';
	import {
		getWorkers,
		getWorkerCategories,
		getWorkerAnalytics,
		formatWorkerName,
		getWorkerStatusColor,
		formatHourlyRate,
		calculateWorkerPerformance
	} from '$lib/api/worker';
	import { toast } from '$lib/stores/toastStore.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import StatCard from '$lib/components/dashboard/StatCard.svelte';

	// Icon definitions for StatCard components
	const icons = {
		users: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z"></path></svg>`,
		user: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path></svg>`,
		collection: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path></svg>`,
		star: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path></svg>`
	};

	// Svelte 5 runes for reactive state
	let workers = $state([]);
	let categories = $state([]);
	let analytics = $state(null);
	let loading = $state(true);
	let error = $state(null);
	let selectedCategory = $state('all');
	let selectedStatus = $state('all');

	// Derived state for statistics
	let totalWorkers = $derived(workers.length);
	let activeWorkers = $derived(workers.filter((w) => w.status === 'active').length);
	let availableWorkers = $derived(
		workers.filter((w) => w.is_available && w.status === 'active').length
	);
	let totalCapacity = $derived(workers.reduce((sum, w) => sum + (w.max_concurrent_jobs || 0), 0));
	let totalActiveJobs = $derived(workers.reduce((sum, w) => sum + (w.active_jobs_count || 0), 0));
	let utilizationRate = $derived(
		totalCapacity > 0 ? ((totalActiveJobs / totalCapacity) * 100).toFixed(1) : 0
	);
	let averageRating = $derived.by(() => {
		const workersWithRating = workers.filter(
			(w) => w.rating && typeof w.rating === 'number' && w.rating > 0
		);
		if (workersWithRating.length === 0) return '0.0';
		const average =
			workersWithRating.reduce((sum, w) => sum + w.rating, 0) / workersWithRating.length;
		return average.toFixed(1);
	});

	// Filter options
	let statusOptions = $derived([
		{ value: 'all', label: $t('common.all') },
		{ value: 'active', label: $t('worker.status.active') },
		{ value: 'inactive', label: $t('worker.status.inactive') },
		{ value: 'suspended', label: $t('worker.status.suspended') },
		{ value: 'on_leave', label: $t('worker.status.onLeave') }
	]);

	// Filtered workers
	let filteredWorkers = $derived(() => {
		let filtered = [...workers];

		// Apply category filter
		if (selectedCategory !== 'all') {
			filtered = filtered.filter(
				(worker) =>
					worker.categories &&
					worker.categories.some((cat) => cat.id === parseInt(selectedCategory))
			);
		}

		// Apply status filter
		if (selectedStatus !== 'all') {
			filtered = filtered.filter((worker) => worker.status === selectedStatus);
		}

		return filtered;
	});

	// Top performers
	let topPerformers = $derived(() => {
		return workers
			.map((worker) => ({
				...worker,
				performance: calculateWorkerPerformance(worker)
			}))
			.filter((worker) => worker.performance.totalJobs > 0)
			.sort(
				(a, b) =>
					parseFloat(b.performance.completionRate) - parseFloat(a.performance.completionRate)
			)
			.slice(0, 5);
	});

	// Workers needing attention
	let workersNeedingAttention = $derived(() => {
		return workers
			.map((worker) => ({
				...worker,
				performance: calculateWorkerPerformance(worker)
			}))
			.filter((worker) => {
				const perf = worker.performance;
				return (
					worker.status === 'active' &&
					(parseFloat(perf.completionRate) < 70 ||
						perf.averageRating < 3.5 ||
						parseFloat(perf.efficiency) > 90)
				);
			})
			.slice(0, 5);
	});

	// Load data on mount
	onMount(async () => {
		await loadWorkerData();
	});

	// Watch for filter changes
	$effect(() => {
		// Data is already loaded, just filtering locally
	});

	// Load worker data
	async function loadWorkerData() {
		try {
			loading = true;
			error = null;

			const [workersData, categoriesData, analyticsData] = await Promise.all([
				getWorkers(),
				getWorkerCategories(),
				getWorkerAnalytics()
			]);

			workers = workersData;
			categories = categoriesData;
			analytics = analyticsData;
		} catch (err) {
			error = err.message;
			toast.error($t('worker.loadError'));
		} finally {
			loading = false;
		}
	}

	// Get performance color
	function getPerformanceColor(completionRate) {
		const rate = parseFloat(completionRate);
		if (rate >= 90) return 'green';
		if (rate >= 80) return 'yellow';
		if (rate >= 70) return 'orange';
		return 'red';
	}

	// Get efficiency color
	function getEfficiencyColor(efficiency) {
		const eff = parseFloat(efficiency);
		if (eff <= 70) return 'green';
		if (eff <= 85) return 'yellow';
		if (eff <= 95) return 'orange';
		return 'red';
	}

	// Refresh data
	async function refreshData() {
		await loadWorkerData();
		toast.success($t('worker.dataRefreshed'));
	}
</script>

<svelte:head>
	<title>{$t('worker.dashboard')} - {$t('app.name')}</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
		<div>
			<h1 class="text-2xl font-bold text-gray-900 dark:text-white">
				{$t('worker.dashboard')}
			</h1>
			<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
				{$t('worker.dashboardDescription')}
			</p>
		</div>

		<div class="mt-4 flex space-x-3 sm:mt-0">
			<Button onClick={refreshData} variant="outline" {loading}>
				<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
					/>
				</svg>
				{$t('common.refresh')}
			</Button>

			<Button href="/create/worker" variant="primary">
				<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 4v16m8-8H4"
					/>
				</svg>
				{$t('worker.add')}
			</Button>
		</div>
	</div>

	<!-- Filters -->
	<div
		class="rounded-lg border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800"
	>
		<div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
			<!-- Category Filter -->
			<div>
				<label
					for="categoryFilter"
					class="block text-sm font-medium text-gray-700 dark:text-gray-300"
				>
					{$t('worker.category')}
				</label>
				<select
					id="categoryFilter"
					bind:value={selectedCategory}
					class="focus:border-primary-500 focus:ring-primary-500 mt-1 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
				>
					<option value="all">{$t('common.all')}</option>
					{#each categories as category}
						<option value={category.id}>{category.name}</option>
					{/each}
				</select>
			</div>

			<!-- Status Filter -->
			<div>
				<label
					for="statusFilter"
					class="block text-sm font-medium text-gray-700 dark:text-gray-300"
				>
					{$t('common.status')}
				</label>
				<select
					id="statusFilter"
					bind:value={selectedStatus}
					class="focus:border-primary-500 focus:ring-primary-500 mt-1 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
				>
					{#each statusOptions as option}
						<option value={option.value}>{option.label}</option>
					{/each}
				</select>
			</div>

			<!-- Results Count -->
			<div class="flex items-end">
				<p class="text-sm text-gray-600 dark:text-gray-400">
					{$t('common.showing')}
					{filteredWorkers.length}
					{$t('common.of')}
					{totalWorkers}
					{$t('worker.workers')}
				</p>
			</div>
		</div>
	</div>

	<!-- Error Alert -->
	{#if error}
		<Alert type="error" title={$t('error.title')} message={error} dismissible />
	{/if}

	<!-- Loading State -->
	{#if loading}
		<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
			{#each Array(4) as _}
				<LoadingSkeleton type="rect" height="120px" />
			{/each}
		</div>

		<!-- Statistics Overview -->
	{:else}
		<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
			<!-- Total Workers -->
			<StatCard
				title={$t('worker.totalWorkers')}
				value={totalWorkers}
				icon={icons.users}
				color="primary"
				href="/dashboard/workers"
			/>

			<!-- Active Workers -->
			<StatCard
				title={$t('worker.activeWorkers')}
				value={activeWorkers}
				icon={icons.user}
				color="success"
			/>

			<!-- Utilization Rate -->
			<StatCard
				title={$t('worker.utilizationRate')}
				value={`${utilizationRate}%`}
				icon={icons.collection}
				color={parseFloat(utilizationRate) >= 80
					? 'success'
					: parseFloat(utilizationRate) >= 60
						? 'warning'
						: 'error'}
			/>

			<!-- Average Rating -->
			<StatCard
				title={$t('worker.averageRating')}
				value={`${averageRating}/5`}
				icon={icons.star}
				color={parseFloat(averageRating) >= 4
					? 'success'
					: parseFloat(averageRating) >= 3
						? 'warning'
						: 'error'}
			/>
		</div>
	{/if}

	<!-- Performance Overview -->
	<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
		<!-- Top Performers -->
		{#if !loading && topPerformers.length > 0}
			<div
				class="rounded-lg border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800"
			>
				<div class="p-6">
					<h3 class="mb-4 text-lg font-medium text-gray-900 dark:text-white">
						{$t('worker.topPerformers')}
					</h3>

					<div class="space-y-4">
						{#each topPerformers as worker}
							<div
								class="flex items-center justify-between rounded-md bg-green-50 p-3 dark:bg-green-900/20"
							>
								<div class="flex items-center space-x-3">
									<div class="flex-shrink-0">
										<div
											class="flex h-8 w-8 items-center justify-center rounded-full bg-green-100 dark:bg-green-800"
										>
											<span class="text-sm font-medium text-green-800 dark:text-green-200">
												{formatWorkerName(worker).charAt(0)}
											</span>
										</div>
									</div>
									<div>
										<p class="text-sm font-medium text-gray-900 dark:text-white">
											{formatWorkerName(worker)}
										</p>
										<p class="text-xs text-gray-600 dark:text-gray-400">
											{worker.categories?.map((c) => c.name).join(', ') ||
												$t('worker.noCategories')}
										</p>
									</div>
								</div>
								<div class="text-right">
									<p class="text-sm font-medium text-green-600 dark:text-green-400">
										{worker.performance.completionRate}%
									</p>
									<p class="text-xs text-gray-500">
										{worker.performance.totalJobs}
										{$t('worker.jobs')}
									</p>
								</div>
							</div>
						{/each}
					</div>

					<div class="mt-4">
						<Button
							href="/dashboard/workers?sort=performance"
							variant="outline"
							size="compact"
							class="w-full"
						>
							{$t('worker.viewAllPerformers')}
						</Button>
					</div>
				</div>
			</div>
		{/if}

		<!-- Workers Needing Attention -->
		{#if !loading && workersNeedingAttention.length > 0}
			<div
				class="rounded-lg border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800"
			>
				<div class="p-6">
					<h3 class="mb-4 text-lg font-medium text-gray-900 dark:text-white">
						{$t('worker.needingAttention')} ({workersNeedingAttention.length})
					</h3>

					<div class="space-y-4">
						{#each workersNeedingAttention as worker}
							<div
								class="flex items-center justify-between rounded-md bg-yellow-50 p-3 dark:bg-yellow-900/20"
							>
								<div class="flex items-center space-x-3">
									<div class="flex-shrink-0">
										<div
											class="flex h-8 w-8 items-center justify-center rounded-full bg-yellow-100 dark:bg-yellow-800"
										>
											<span class="text-sm font-medium text-yellow-800 dark:text-yellow-200">
												{formatWorkerName(worker).charAt(0)}
											</span>
										</div>
									</div>
									<div>
										<p class="text-sm font-medium text-gray-900 dark:text-white">
											{formatWorkerName(worker)}
										</p>
										<div
											class="flex items-center space-x-2 text-xs text-gray-600 dark:text-gray-400"
										>
											{#if parseFloat(worker.performance.completionRate) < 70}
												<span class="text-red-600 dark:text-red-400">
													{$t('worker.lowCompletion')}
												</span>
											{/if}
											{#if worker.performance.averageRating < 3.5}
												<span class="text-red-600 dark:text-red-400">
													{$t('worker.lowRating')}
												</span>
											{/if}
											{#if parseFloat(worker.performance.efficiency) > 90}
												<span class="text-orange-600 dark:text-orange-400">
													{$t('worker.overloaded')}
												</span>
											{/if}
										</div>
									</div>
								</div>
								<div class="text-right">
									<p
										class="text-sm font-medium text-{getPerformanceColor(
											worker.performance.completionRate
										)}-600"
									>
										{worker.performance.completionRate}%
									</p>
									<p class="text-xs text-gray-500">
										{worker.performance.averageRating}/5 ⭐
									</p>
								</div>
							</div>
						{/each}
					</div>

					<div class="mt-4">
						<Button
							href="/dashboard/workers?filter=needs_attention"
							variant="outline"
							size="compact"
							class="w-full"
						>
							{$t('worker.reviewAll')}
						</Button>
					</div>
				</div>
			</div>
		{/if}
	</div>

	<!-- Category Overview -->
	{#if !loading && categories.length > 0}
		<div
			class="rounded-lg border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800"
		>
			<div class="p-6">
				<div class="mb-4 flex items-center justify-between">
					<h3 class="text-lg font-medium text-gray-900 dark:text-white">
						{$t('worker.categoriesOverview')}
					</h3>
					<Button href="/dashboard/worker-categories" variant="outline" size="compact">
						{$t('worker.manageCategories')}
					</Button>
				</div>

				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
					{#each categories as category}
						{@const categoryWorkers = workers.filter(
							(w) => w.categories && w.categories.some((c) => c.id === category.id)
						)}
						{@const activeInCategory = categoryWorkers.filter((w) => w.status === 'active').length}

						<div class="rounded-lg border border-gray-200 p-4 dark:border-gray-600">
							<div class="mb-2 flex items-center justify-between">
								<h4 class="text-sm font-medium text-gray-900 dark:text-white">
									{category.name}
								</h4>
								<span class="text-xs text-gray-500">
									{categoryWorkers.length}
									{$t('worker.workers')}
								</span>
							</div>

							<div class="space-y-2">
								<div class="flex justify-between text-sm">
									<span class="text-gray-600 dark:text-gray-400">{$t('worker.active')}:</span>
									<span class="text-gray-900 dark:text-white">{activeInCategory}</span>
								</div>

								{#if category.hourly_rate_min && category.hourly_rate_max}
									<div class="flex justify-between text-sm">
										<span class="text-gray-600 dark:text-gray-400">{$t('worker.rateRange')}:</span>
										<span class="text-gray-900 dark:text-white">
											{formatHourlyRate(category.hourly_rate_min)} - {formatHourlyRate(
												category.hourly_rate_max
											)}
										</span>
									</div>
								{/if}

								{#if categoryWorkers.length > 0}
									{@const avgRating =
										categoryWorkers.filter((w) => w.rating).reduce((sum, w) => sum + w.rating, 0) /
										categoryWorkers.filter((w) => w.rating).length}

									{#if !isNaN(avgRating)}
										<div class="flex justify-between text-sm">
											<span class="text-gray-600 dark:text-gray-400">{$t('worker.avgRating')}:</span
											>
											<span class="text-gray-900 dark:text-white">{avgRating.toFixed(1)}/5</span>
										</div>
									{/if}
								{/if}
							</div>
						</div>
					{/each}
				</div>
			</div>
		</div>
	{/if}

	<!-- Recent Activity Summary -->
	{#if !loading && workers.length > 0}
		<div
			class="rounded-lg border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800"
		>
			<div class="p-6">
				<div class="mb-4 flex items-center justify-between">
					<h3 class="text-lg font-medium text-gray-900 dark:text-white">
						{$t('worker.recentWorkers')}
					</h3>
					<Button href="/dashboard/workers" variant="outline" size="compact">
						{$t('common.viewAll')}
					</Button>
				</div>

				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
						<thead class="bg-gray-50 dark:bg-gray-700">
							<tr>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-300"
								>
									{$t('worker.name')}
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-300"
								>
									{$t('worker.categories')}
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-300"
								>
									{$t('common.status')}
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-300"
								>
									{$t('worker.activeJobs')}
								</th>
								<th
									class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-300"
								>
									{$t('worker.rating')}
								</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-200 bg-white dark:divide-gray-700 dark:bg-gray-800">
							{#each filteredWorkers.slice(0, 10) as worker}
								<tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
									<td class="px-6 py-4 whitespace-nowrap">
										<div class="flex items-center">
											<div class="h-8 w-8 flex-shrink-0">
												<div
													class="bg-primary-100 dark:bg-primary-800 flex h-8 w-8 items-center justify-center rounded-full"
												>
													<span class="text-primary-800 dark:text-primary-200 text-sm font-medium">
														{formatWorkerName(worker).charAt(0)}
													</span>
												</div>
											</div>
											<div class="ml-3">
												<div class="text-sm font-medium text-gray-900 dark:text-white">
													{formatWorkerName(worker)}
												</div>
												<div class="text-sm text-gray-500 dark:text-gray-400">
													{worker.employee_id}
												</div>
											</div>
										</div>
									</td>
									<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-500 dark:text-gray-400">
										{worker.categories?.map((c) => c.name).join(', ') || $t('worker.noCategories')}
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										<span
											class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-{getWorkerStatusColor(
												worker.status
											)}-100 text-{getWorkerStatusColor(
												worker.status
											)}-800 dark:bg-{getWorkerStatusColor(
												worker.status
											)}-900 dark:text-{getWorkerStatusColor(worker.status)}-200"
										>
											{worker.status}
										</span>
									</td>
									<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-500 dark:text-gray-400">
										{worker.active_jobs_count || 0} / {worker.max_concurrent_jobs || 0}
									</td>
									<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-500 dark:text-gray-400">
										{#if worker.rating}
											{worker.rating}/5 ⭐
										{:else}
											{$t('worker.noRating')}
										{/if}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>
		</div>
	{/if}
</div>
