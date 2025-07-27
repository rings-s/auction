<!-- src/routes/property-management/workers/[id]/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { t, locale } from '$lib/i18n';
	import { user } from '$lib/stores/user.svelte.js';
	import { workersAPI, maintenanceAPI } from '$lib/api/propertyManagement.js';
	import { formatCurrency } from '$lib/utils/currency';

	import LoadingSpinner from '$lib/components/animations/LoadingSpinner.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import WorkerDetailTabs from '$lib/components/property-management/workers/WorkerDetailTabs.svelte';

	let workerId = $derived($page.params.id);
	let isRTL = $derived($locale === 'ar');

	// State
	let worker = null;
	let loading = true;
	let error = null;
	let activeTab = 'overview';
	let maintenanceRequests = [];
	let performanceMetrics = null;

	// Permissions
	let canEdit = $derived(
		$user && ($user.is_superuser || $user.is_staff || ['owner', 'appraiser'].includes($user.role))
	);

	onMount(() => {
		loadWorker();
	});

	async function loadWorker() {
		try {
			loading = true;
			error = null;

			const [workerResponse, requestsResponse] = await Promise.all([
				workersAPI.getById(workerId),
				maintenanceAPI.requests.getAll({ assigned_worker: workerId })
			]);

			worker = workerResponse.data;
			maintenanceRequests = requestsResponse.data.results || [];

			// Calculate performance metrics
			calculatePerformanceMetrics();
		} catch (err) {
			error = err.message || $t('error.fetchFailed');
			console.error('Failed to load worker:', err);
		} finally {
			loading = false;
		}
	}

	function calculatePerformanceMetrics() {
		if (!worker || !maintenanceRequests) return;

		const completedRequests = maintenanceRequests.filter((r) => r.status === 'completed');
		const inProgressRequests = maintenanceRequests.filter((r) => r.status === 'in_progress');
		const totalRequests = maintenanceRequests.length;

		// Calculate average completion time
		const completionTimes = completedRequests
			.filter((r) => r.completion_date && r.reported_date)
			.map((r) => {
				const start = new Date(r.reported_date);
				const end = new Date(r.completion_date);
				return (end - start) / (1000 * 60 * 60 * 24); // days
			});

		const avgCompletionTime =
			completionTimes.length > 0
				? completionTimes.reduce((a, b) => a + b, 0) / completionTimes.length
				: 0;

		// Calculate efficiency score
		const completionRate = totalRequests > 0 ? (completedRequests.length / totalRequests) * 100 : 0;
		const ratingScore = worker.rating ? (worker.rating / 5) * 100 : 0;

		performanceMetrics = {
			totalJobs: totalRequests,
			completedJobs: completedRequests.length,
			inProgressJobs: inProgressRequests.length,
			completionRate,
			avgCompletionTime: Math.round(avgCompletionTime * 10) / 10,
			efficiencyScore: Math.round((completionRate * 0.6 + ratingScore * 0.4) * 10) / 10,
			monthlyEarnings: calculateMonthlyEarnings(completedRequests)
		};
	}

	function calculateMonthlyEarnings(completedRequests) {
		const currentMonth = new Date().getMonth();
		const currentYear = new Date().getFullYear();

		const thisMonthRequests = completedRequests.filter((r) => {
			const completionDate = new Date(r.completion_date);
			return (
				completionDate.getMonth() === currentMonth && completionDate.getFullYear() === currentYear
			);
		});

		return thisMonthRequests.reduce((total, request) => {
			return total + (request.labor_cost || 0);
		}, 0);
	}

	function handleEdit() {
		goto(`/property-management/workers/${workerId}/edit`);
	}

	function handleBack() {
		goto('/property-management/workers');
	}

	function handleTabChange(event) {
		activeTab = event.detail.tab;
	}

	function getStatusClass(status) {
		const classes = {
			active: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
			inactive: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
			on_leave: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
		};
		return classes[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
	}

	function getSkillLevelClass(skillLevel) {
		const classes = {
			beginner: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
			intermediate: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
			advanced: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
			expert: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
		};
		return classes[skillLevel] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
	}

	function formatPhoneNumber(phone) {
		if (!phone) return '-';
		// Format phone number for display
		return phone.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
	}
</script>

<svelte:head>
	<title>
		{worker?.full_name
			? `${worker.full_name} - ${$t('propertyManagement.worker')}`
			: $t('propertyManagement.worker')}
	</title>
</svelte:head>

<div
	class="min-h-screen bg-gradient-to-br from-slate-50 via-orange-50 to-amber-50 dark:from-gray-900 dark:via-orange-900 dark:to-amber-900"
	dir={isRTL ? 'rtl' : 'ltr'}
>
	<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
		<!-- Back Button -->
		<div class="mb-6">
			<button
				on:click={handleBack}
				class="group inline-flex items-center text-sm font-medium text-orange-600 transition-colors hover:text-orange-500 dark:text-orange-400 dark:hover:text-orange-300"
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
				{$t('propertyManagement.backToWorkers')}
			</button>
		</div>

		<!-- Loading State -->
		{#if loading && !worker}
			<div class="flex flex-col items-center justify-center py-20">
				<LoadingSpinner size="lg" color="orange" />
				<p class="mt-4 text-gray-500 dark:text-gray-400">{$t('common.loading')}</p>
			</div>

			<!-- Error State -->
		{:else if error && !worker}
			<div
				class="mx-auto max-w-3xl rounded-xl border border-red-200 bg-red-50 p-8 text-red-800 dark:border-red-800 dark:bg-red-900/20 dark:text-red-200"
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
				<div class="mt-6 flex space-x-4">
					<Button variant="primary" on:click={loadWorker}>
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
					<Button variant="outline" on:click={handleBack}>
						{$t('propertyManagement.backToWorkers')}
					</Button>
				</div>
			</div>

			<!-- Worker Content -->
		{:else if worker}
			<div class="space-y-8">
				<!-- Worker Header -->
				<div
					class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
				>
					<div class="bg-gradient-to-r from-orange-500 via-amber-500 to-yellow-600 p-8 text-white">
						<div class="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
							<div class="flex items-center space-x-6">
								<!-- Worker Avatar -->
								<div class="relative">
									{#if worker.profile_image}
										<img
											src={worker.profile_image}
											alt={worker.full_name}
											class="h-24 w-24 rounded-full border-4 border-white/20 object-cover"
										/>
									{:else}
										<div
											class="flex h-24 w-24 items-center justify-center rounded-full border-4 border-white/20 bg-white/20"
										>
											<svg
												class="h-12 w-12 text-white"
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
										</div>
									{/if}
									<!-- Status Indicator -->
									<div
										class="absolute -right-1 -bottom-1 h-6 w-6 rounded-full border-2 border-white
										{worker.status === 'active'
											? 'bg-green-500'
											: worker.status === 'on_leave'
												? 'bg-yellow-500'
												: 'bg-red-500'}"
									></div>
								</div>

								<!-- Worker Info -->
								<div class="flex-1">
									<div class="mb-2 flex items-center">
										<h1 class="mr-4 text-3xl font-bold text-white">{worker.full_name}</h1>
										<span
											class="rounded-full px-3 py-1 text-sm font-medium {getStatusClass(
												worker.status
											)}"
										>
											{$t(`worker.status.${worker.status}`)}
										</span>
									</div>
									<div class="flex items-center space-x-4 text-white/90">
										<div class="flex items-center">
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
													d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
												/>
											</svg>
											<span class="text-sm">{worker.employee_id}</span>
										</div>
										{#if worker.categories && worker.categories.length > 0}
											<div class="flex items-center">
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
														d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
													/>
												</svg>
												<span class="text-sm">{worker.categories.join(', ')}</span>
											</div>
										{/if}
										<div class="flex items-center">
											<span
												class="rounded-full px-2 py-1 text-xs font-medium {getSkillLevelClass(
													worker.skill_level
												)}"
											>
												{$t(`worker.skillLevel.${worker.skill_level}`)}
											</span>
										</div>
									</div>
								</div>
							</div>

							<!-- Action Buttons -->
							<div class="flex flex-wrap gap-3 lg:flex-col lg:items-end">
								{#if canEdit}
									<Button
										variant="outline"
										class="border-white/20 bg-white/10 text-white transition-all duration-300 hover:bg-white/20"
										on:click={handleEdit}
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
								{/if}
								<Button
									variant="outline"
									class="border-white/20 bg-white/10 text-white transition-all duration-300 hover:bg-white/20"
									on:click={() => window.open(`tel:${worker.phone}`, '_self')}
								>
									<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
										/>
									</svg>
									{$t('common.call')}
								</Button>
							</div>
						</div>
					</div>

					<!-- Quick Stats Bar -->
					{#if performanceMetrics}
						<div
							class="border-b border-gray-200 bg-gray-50 p-6 dark:border-gray-600 dark:bg-gray-700"
						>
							<div class="grid grid-cols-2 gap-6 md:grid-cols-4">
								<div class="text-center">
									<div class="text-2xl font-bold text-orange-600 dark:text-orange-400">
										{performanceMetrics.completedJobs}
									</div>
									<div class="text-sm text-gray-600 dark:text-gray-400">
										{$t('worker.completedJobs')}
									</div>
								</div>
								<div class="text-center">
									<div class="text-2xl font-bold text-green-600 dark:text-green-400">
										{performanceMetrics.completionRate.toFixed(1)}%
									</div>
									<div class="text-sm text-gray-600 dark:text-gray-400">
										{$t('worker.completionRate')}
									</div>
								</div>
								<div class="text-center">
									<div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
										{worker.rating ? worker.rating.toFixed(1) : '—'}
									</div>
									<div class="text-sm text-gray-600 dark:text-gray-400">{$t('worker.rating')}</div>
								</div>
								<div class="text-center">
									<div class="text-2xl font-bold text-purple-600 dark:text-purple-400">
										{formatCurrency(performanceMetrics.monthlyEarnings)}
									</div>
									<div class="text-sm text-gray-600 dark:text-gray-400">
										{$t('worker.monthlyEarnings')}
									</div>
								</div>
							</div>
						</div>
					{/if}
				</div>

				<!-- Worker Detail Tabs -->
				<WorkerDetailTabs
					{worker}
					{activeTab}
					{maintenanceRequests}
					{performanceMetrics}
					on:tabChange={handleTabChange}
				/>
			</div>
		{/if}
	</div>
</div>

<style>
	/* Enhanced animations for worker detail theme */
	:global(.worker-detail-theme) {
		--primary-gradient: linear-gradient(135deg, #ea580c 0%, #f59e0b 50%, #eab308 100%);
		--accent-color: #ea580c;
		--accent-light: #fed7aa;
		--accent-dark: #c2410c;
	}

	/* Smooth transitions for better UX */
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
		animation: gradient-shift 6s ease infinite;
	}

	/* Status indicator pulse animation */
	@keyframes pulse-status {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.7;
		}
	}

	.bg-green-500 {
		animation: pulse-status 2s ease-in-out infinite;
	}
</style>
