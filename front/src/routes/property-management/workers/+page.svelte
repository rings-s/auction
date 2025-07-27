<!-- src/routes/property-management/workers/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t, locale } from '$lib/i18n';
	import { user } from '$lib/stores/user.svelte.js';
	import { workersAPI } from '$lib/api/propertyManagement.js';
	import Button from '$lib/components/ui/Button.svelte';
	import WorkerList from '$lib/components/property-management/workers/WorkerList.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	// import SearchFilter from '$lib/components/ui/SearchFilter.svelte'; // Component not found

	let isRTL = $derived($locale === 'ar');

	// State using Svelte 5 runes
	let loading = $state(true);
	let error = $state('');
	let workers = $state([]);
	let filteredWorkers = $state([]);
	let searchQuery = $state('');
	let selectedCategory = $state('');
	let selectedStatus = $state('');
	let selectedSkillLevel = $state('');
	let sortBy = $state('name');

	// Filters
	let categories = $state([]);
	let statusOptions = [
		{ value: '', label: $t('common.all') },
		{ value: 'active', label: $t('worker.status.active') },
		{ value: 'inactive', label: $t('worker.status.inactive') },
		{ value: 'on_leave', label: $t('worker.status.onLeave') }
	];

	let skillLevels = [
		{ value: '', label: $t('common.all') },
		{ value: 'beginner', label: $t('worker.skillLevel.beginner') },
		{ value: 'intermediate', label: $t('worker.skillLevel.intermediate') },
		{ value: 'advanced', label: $t('worker.skillLevel.advanced') },
		{ value: 'expert', label: $t('worker.skillLevel.expert') }
	];

	let sortOptions = [
		{ value: 'name', label: $t('worker.sortBy.name') },
		{ value: 'rating', label: $t('worker.sortBy.rating') },
		{ value: 'efficiency', label: $t('worker.sortBy.efficiency') },
		{ value: 'jobs_completed', label: $t('worker.sortBy.jobsCompleted') },
		{ value: 'hourly_rate', label: $t('worker.sortBy.hourlyRate') }
	];

	// Permissions
	let hasAccess = $derived(
		$user &&
			(['owner', 'appraiser', 'data_entry'].includes($user.role) ||
				$user.is_staff ||
				$user.is_superuser)
	);

	onMount(() => {
		if (!hasAccess) {
			goto('/dashboard');
			return;
		}
		loadWorkers();
	});

	async function loadWorkers() {
		try {
			loading = true;
			error = '';

			const response = await workersAPI.getAll();
			workers = response.data.results || [];

			// Extract unique categories
			const allCategories = workers.flatMap((w) => w.categories || []);
			categories = [
				{ value: '', label: $t('common.all') },
				...Array.from(new Set(allCategories)).map((cat) => ({
					value: cat,
					label: cat
				}))
			];

			applyFilters();
		} catch (err) {
			error = err.message || $t('errors.loadingFailed');
			console.error('Failed to load workers:', err);
		} finally {
			loading = false;
		}
	}

	function applyFilters() {
		let filtered = [...workers];

		// Search filter
		if (searchQuery) {
			const query = searchQuery.toLowerCase();
			filtered = filtered.filter(
				(worker) =>
					worker.full_name?.toLowerCase().includes(query) ||
					worker.email?.toLowerCase().includes(query) ||
					worker.employee_id?.toLowerCase().includes(query) ||
					worker.phone?.toLowerCase().includes(query)
			);
		}

		// Category filter
		if (selectedCategory) {
			filtered = filtered.filter((worker) => worker.categories?.includes(selectedCategory));
		}

		// Status filter
		if (selectedStatus) {
			filtered = filtered.filter((worker) => worker.status === selectedStatus);
		}

		// Skill level filter
		if (selectedSkillLevel) {
			filtered = filtered.filter((worker) => worker.skill_level === selectedSkillLevel);
		}

		// Sorting
		filtered.sort((a, b) => {
			switch (sortBy) {
				case 'name':
					return (a.full_name || '').localeCompare(b.full_name || '');
				case 'rating':
					return (b.rating || 0) - (a.rating || 0);
				case 'efficiency':
					return (b.efficiency_score || 0) - (a.efficiency_score || 0);
				case 'jobs_completed':
					return (b.total_jobs_completed || 0) - (a.total_jobs_completed || 0);
				case 'hourly_rate':
					return (b.hourly_rate || 0) - (a.hourly_rate || 0);
				default:
					return 0;
			}
		});

		filteredWorkers = filtered;
	}

	// Reactive filters
	$effect(() => {
		applyFilters();
	});

	// Event handlers
	function handleCreateWorker() {
		goto('/property-management/workers/create');
	}

	function handleViewWorker(event) {
		goto(`/property-management/workers/${event.detail.worker.id}`);
	}

	function handleEditWorker(event) {
		goto(`/property-management/workers/${event.detail.worker.id}/edit`);
	}

	function handleDeleteWorker(event) {
		// Implement delete functionality
		const worker = event.detail.worker;
		if (confirm($t('worker.confirmDelete', { name: worker.full_name }))) {
			deleteWorker(worker.id);
		}
	}

	async function deleteWorker(workerId) {
		try {
			await workersAPI.delete(workerId);
			workers = workers.filter((w) => w.id !== workerId);
			applyFilters();
		} catch (err) {
			error = err.message || $t('worker.deleteFailed');
		}
	}

	function clearFilters() {
		searchQuery = '';
		selectedCategory = '';
		selectedStatus = '';
		selectedSkillLevel = '';
		sortBy = 'name';
	}
</script>

<svelte:head>
	<title>{$t('propertyManagement.workers')} | {$t('app.name')}</title>
	<meta name="description" content={$t('propertyManagement.workersDescription')} />
</svelte:head>

<div
	class="min-h-screen bg-gradient-to-br from-slate-50 via-orange-50 to-amber-50 dark:from-gray-900 dark:via-orange-900 dark:to-amber-900"
	dir={isRTL ? 'rtl' : 'ltr'}
>
	<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
		<!-- Header -->
		<div class="mb-8">
			<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
				<div>
					<h1 class="flex items-center text-3xl font-bold text-gray-900 dark:text-white">
						<div class="mr-4 rounded-xl bg-gradient-to-r from-orange-500 to-amber-500 p-3">
							<svg class="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
								/>
							</svg>
						</div>
						{$t('propertyManagement.workers')}
					</h1>
					<p class="mt-2 text-gray-600 dark:text-gray-400">
						{$t('propertyManagement.workersSubtitle')}
					</p>
				</div>
				<Button
					variant="primary"
					on:click={handleCreateWorker}
					class="bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700"
				>
					<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 4v16m8-8H4"
						/>
					</svg>
					{$t('worker.create')}
				</Button>
			</div>
		</div>

		<!-- Error Display -->
		{#if error}
			<div class="mb-6">
				<Alert type="error" message={error} />
			</div>
		{/if}

		<!-- Search and Filters -->
		<div
			class="mb-8 rounded-2xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800"
		>
			<div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-6">
				<!-- Search -->
				<div class="lg:col-span-2">
					<label
						for="search"
						class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('common.search')}
					</label>
					<div class="relative">
						<input
							type="text"
							id="search"
							bind:value={searchQuery}
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 pl-10 text-gray-900 placeholder-gray-500 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
							placeholder={$t('worker.searchPlaceholder')}
						/>
						<svg
							class="absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 transform text-gray-400"
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
					</div>
				</div>

				<!-- Category Filter -->
				<div>
					<label
						for="category"
						class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('worker.category')}
					</label>
					<select
						id="category"
						bind:value={selectedCategory}
						class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-gray-900 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
					>
						{#each categories as category}
							<option value={category.value}>{category.label}</option>
						{/each}
					</select>
				</div>

				<!-- Status Filter -->
				<div>
					<label
						for="status"
						class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('common.status')}
					</label>
					<select
						id="status"
						bind:value={selectedStatus}
						class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-gray-900 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
					>
						{#each statusOptions as option}
							<option value={option.value}>{option.label}</option>
						{/each}
					</select>
				</div>

				<!-- Skill Level Filter -->
				<div>
					<label
						for="skill_level"
						class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('worker.skillLevel.title')}
					</label>
					<select
						id="skill_level"
						bind:value={selectedSkillLevel}
						class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-gray-900 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
					>
						{#each skillLevels as level}
							<option value={level.value}>{level.label}</option>
						{/each}
					</select>
				</div>

				<!-- Sort By -->
				<div>
					<label for="sort" class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
						{$t('common.sortBy')}
					</label>
					<select
						id="sort"
						bind:value={sortBy}
						class="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-gray-900 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
					>
						{#each sortOptions as option}
							<option value={option.value}>{option.label}</option>
						{/each}
					</select>
				</div>
			</div>

			<!-- Filter Actions -->
			<div class="mt-4 flex items-center justify-between">
				<div class="text-sm text-gray-500 dark:text-gray-400">
					{$t('common.showing')}
					{filteredWorkers.length}
					{$t('common.of')}
					{workers.length}
					{$t('propertyManagement.workers').toLowerCase()}
				</div>
				<Button variant="outline" size="sm" on:click={clearFilters}>
					<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						/>
					</svg>
					{$t('common.clearFilters')}
				</Button>
			</div>
		</div>

		<!-- Workers Grid -->
		<div class="space-y-6">
			{#if loading}
				<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
					{#each Array(6) as _}
						<LoadingSkeleton height="320px" />
					{/each}
				</div>
			{:else if filteredWorkers.length === 0}
				<div class="py-16 text-center">
					<div
						class="mx-auto mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-r from-orange-100 to-amber-100 dark:from-orange-900 dark:to-amber-900"
					>
						<svg
							class="h-12 w-12 text-orange-500"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
							/>
						</svg>
					</div>
					<h3 class="mb-2 text-xl font-semibold text-gray-900 dark:text-white">
						{searchQuery || selectedCategory || selectedStatus || selectedSkillLevel
							? $t('worker.noMatchingWorkers')
							: $t('worker.noWorkers')}
					</h3>
					<p class="mb-6 text-gray-500 dark:text-gray-400">
						{searchQuery || selectedCategory || selectedStatus || selectedSkillLevel
							? $t('worker.tryDifferentFilters')
							: $t('worker.createFirstWorker')}
					</p>
					{#if !searchQuery && !selectedCategory && !selectedStatus && !selectedSkillLevel}
						<Button
							variant="primary"
							on:click={handleCreateWorker}
							class="bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700"
						>
							<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 4v16m8-8H4"
								/>
							</svg>
							{$t('worker.createFirst')}
						</Button>
					{:else}
						<Button variant="outline" on:click={clearFilters}>
							{$t('common.clearFilters')}
						</Button>
					{/if}
				</div>
			{:else}
				<WorkerList
					filters={{
						category: selectedCategory,
						status: selectedStatus,
						skillLevel: selectedSkillLevel,
						search: searchQuery
					}}
				/>
			{/if}
		</div>
	</div>
</div>

<style>
	/* Enhanced orange-amber theme */
	:global(.worker-theme) {
		--primary-gradient: linear-gradient(135deg, #ea580c 0%, #f59e0b 50%, #d97706 100%);
		--accent-color: #ea580c;
		--accent-light: #fed7aa;
		--accent-dark: #c2410c;
	}

	/* Smooth transitions */
	* {
		transition: all 0.2s ease-in-out;
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
