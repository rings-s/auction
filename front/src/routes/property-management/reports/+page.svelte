<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import { userStore } from '$lib/stores/user.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import { analyticsAPI } from '$lib/api/propertyManagement.js';
	import { fade } from 'svelte/transition';

	// State
	let loading = $state(true);
	let generating = $state(false);
	let error = $state('');
	let reports = $state([]);
	let showGenerateModal = $state(false);

	// Form data for report generation
	let reportData = $state({
		type: 'financial',
		period: 'month',
		start_date: '',
		end_date: '',
		format: 'pdf',
		properties: [],
		include_charts: true,
		include_summary: true
	});

	let user = $derived($userStore);
	let hasAccess = $derived(
		(user && ['owner', 'appraiser', 'data_entry'].includes(user.role)) || user?.is_superuser
	);

	// Debug function to test modal
	function testModal() {
		console.log('Test modal function called');
		showGenerateModal = true;
		console.log('showGenerateModal after setting to true:', showGenerateModal);
	}

	// Set default dates
	$effect(() => {
		const today = new Date();
		const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
		reportData.start_date = firstDayOfMonth.toISOString().split('T')[0];
		reportData.end_date = today.toISOString().split('T')[0];
	});

	onMount(() => {
		if (!hasAccess) {
			goto('/dashboard');
			return;
		}
		loadReports();
	});

	async function loadReports() {
		try {
			loading = true;
			error = '';

			const response = await analyticsAPI.getReports();

			if (response.data) {
				reports = response.data.results || [];
			}
		} catch (err) {
			error = err.message || $t('errors.loadingFailed');
			console.error('Failed to load reports:', err);
			// Fallback to mock data
			reports = [
				{
					id: '1',
					type: 'financial',
					period: 'month',
					created_at: '2024-01-15T10:00:00Z',
					status: 'completed',
					file_url: '#',
					title: 'Monthly Financial Report - January 2024'
				},
				{
					id: '2',
					type: 'occupancy',
					period: 'quarter',
					created_at: '2024-01-01T10:00:00Z',
					status: 'completed',
					file_url: '#',
					title: 'Q4 2023 Occupancy Report'
				}
			];
		} finally {
			loading = false;
		}
	}

	async function handleGenerateReport() {
		try {
			generating = true;
			error = '';

			const response = await analyticsAPI.generateReport(reportData);

			if (response.data) {
				reports = [response.data, ...reports];
				showGenerateModal = false;
				resetForm();
			}
		} catch (err) {
			error = err.message || $t('reports.generateError');
		} finally {
			generating = false;
		}
	}

	async function handleDownloadReport(reportId) {
		try {
			const response = await analyticsAPI.getReport(reportId);
			if (response.data?.file_url) {
				window.open(response.data.file_url, '_blank');
			}
		} catch (err) {
			error = err.message || $t('reports.downloadError');
		}
	}

	function resetForm() {
		const today = new Date();
		const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);

		reportData = {
			type: 'financial',
			period: 'month',
			start_date: firstDayOfMonth.toISOString().split('T')[0],
			end_date: today.toISOString().split('T')[0],
			format: 'pdf',
			properties: [],
			include_charts: true,
			include_summary: true
		};
	}

	function getReportTypeIcon(type) {
		const icons = {
			financial: '💰',
			occupancy: '🏠',
			maintenance: '🔧',
			tenant: '👥',
			expense: '📊'
		};
		return icons[type] || '📄';
	}

	function getStatusBadge(status) {
		const classes = {
			pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100',
			generating: 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100',
			completed: 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100',
			failed: 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
		};
		return classes[status] || classes.pending;
	}

	function formatDate(dateString) {
		return new Date(dateString).toLocaleDateString();
	}
</script>

<svelte:head>
	<title>{$t('reports.title')} | {$t('app.name')}</title>
	<meta name="description" content={$t('reports.description')} />
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
					{$t('reports.management')}
				</h1>
				<p class="mt-2 text-gray-600 dark:text-gray-400">
					{$t('reports.subtitle')}
				</p>
			</div>

			<div class="flex flex-wrap gap-4">
				<Button variant="outline" on:click={() => goto('/property-management/analytics')}>
					<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M10 19l-7-7m0 0l7-7m-7 7h18"
						/>
					</svg>
					{$t('reports.backToAnalytics')}
				</Button>

				<Button
					variant="primary"
					class="bg-gradient-to-r from-indigo-500 to-purple-600 shadow-lg hover:from-indigo-600 hover:to-purple-700 hover:shadow-xl"
					on:click={() => {
						console.log('Generate Report button clicked');
						showGenerateModal = true;
						console.log('showGenerateModal:', showGenerateModal);
					}}
				>
					<svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 6v6m0 0v6m0-6h6m-6 0H6"
						/>
					</svg>
					{$t('reports.generate')}
				</Button>

				<!-- Debug test button -->
				<Button variant="outline" on:click={testModal}>Test Modal</Button>
			</div>
		</div>

		<!-- Error Display -->
		{#if error}
			<Alert type="error" message={error} />
		{/if}

		<!-- Quick Report Templates -->
		<div
			class="rounded-2xl border border-gray-200 bg-white p-6 shadow-md dark:border-gray-700 dark:bg-gray-800"
		>
			<h3
				class="mb-4 font-sans text-lg font-semibold tracking-tight text-gray-900 dark:text-gray-100"
			>
				{$t('reports.quickTemplates')}
			</h3>
			<div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
				<Button
					variant="outline"
					class="flex h-auto flex-col items-center space-y-3 p-6 hover:bg-gradient-to-br hover:from-blue-50 hover:to-indigo-50 dark:hover:from-blue-900/20 dark:hover:to-indigo-900/20"
					on:click={() => {
						console.log('Monthly Financial button clicked');
						reportData.type = 'financial';
						reportData.period = 'month';
						showGenerateModal = true;
						console.log('reportData:', reportData);
						console.log('showGenerateModal:', showGenerateModal);
					}}
				>
					<div class="text-3xl">💰</div>
					<div class="text-center">
						<h4 class="font-medium">{$t('reports.monthlyFinancial')}</h4>
						<p class="mt-1 text-xs text-gray-600 dark:text-gray-400">
							{$t('reports.monthlyFinancialDesc')}
						</p>
					</div>
				</Button>

				<Button
					variant="outline"
					class="flex h-auto flex-col items-center space-y-3 p-6 hover:bg-gradient-to-br hover:from-green-50 hover:to-emerald-50 dark:hover:from-green-900/20 dark:hover:to-emerald-900/20"
					on:click={() => {
						console.log('Occupancy Report button clicked');
						reportData.type = 'occupancy';
						reportData.period = 'quarter';
						showGenerateModal = true;
					}}
				>
					<div class="text-3xl">🏠</div>
					<div class="text-center">
						<h4 class="font-medium">{$t('reports.occupancyReport')}</h4>
						<p class="mt-1 text-xs text-gray-600 dark:text-gray-400">
							{$t('reports.occupancyReportDesc')}
						</p>
					</div>
				</Button>

				<Button
					variant="outline"
					class="flex h-auto flex-col items-center space-y-3 p-6 hover:bg-gradient-to-br hover:from-orange-50 hover:to-red-50 dark:hover:from-orange-900/20 dark:hover:to-red-900/20"
					on:click={() => {
						console.log('Maintenance Report button clicked');
						reportData.type = 'maintenance';
						reportData.period = 'month';
						showGenerateModal = true;
					}}
				>
					<div class="text-3xl">🔧</div>
					<div class="text-center">
						<h4 class="font-medium">{$t('reports.maintenanceReport')}</h4>
						<p class="mt-1 text-xs text-gray-600 dark:text-gray-400">
							{$t('reports.maintenanceReportDesc')}
						</p>
					</div>
				</Button>

				<Button
					variant="outline"
					class="flex h-auto flex-col items-center space-y-3 p-6 hover:bg-gradient-to-br hover:from-purple-50 hover:to-pink-50 dark:hover:from-purple-900/20 dark:hover:to-pink-900/20"
					on:click={() => {
						console.log('Tenant Report button clicked');
						reportData.type = 'tenant';
						reportData.period = 'year';
						showGenerateModal = true;
					}}
				>
					<div class="text-3xl">👥</div>
					<div class="text-center">
						<h4 class="font-medium">{$t('reports.tenantReport')}</h4>
						<p class="mt-1 text-xs text-gray-600 dark:text-gray-400">
							{$t('reports.tenantReportDesc')}
						</p>
					</div>
				</Button>
			</div>
		</div>

		<!-- Reports List -->
		<div
			class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-md dark:border-gray-700 dark:bg-gray-800"
		>
			<div class="border-b border-gray-200 p-6 dark:border-gray-700">
				<h3 class="font-sans text-lg font-semibold tracking-tight text-gray-900 dark:text-gray-100">
					{$t('reports.generatedReports')}
				</h3>
				<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
					{$t('reports.generatedReportsDesc')}
				</p>
			</div>

			{#if loading}
				<div class="space-y-4 p-6">
					{#each Array(3) as _}
						<LoadingSkeleton height="80px" />
					{/each}
				</div>
			{:else if reports.length === 0}
				<div class="p-12 text-center">
					<div class="mb-4 text-6xl">📊</div>
					<h3 class="mb-2 text-lg font-medium text-gray-900 dark:text-gray-100">
						{$t('reports.noReports')}
					</h3>
					<p class="mb-6 text-gray-600 dark:text-gray-400">
						{$t('reports.noReportsDesc')}
					</p>
					<Button variant="primary" on:click={() => (showGenerateModal = true)}>
						{$t('reports.generateFirst')}
					</Button>
				</div>
			{:else}
				<div class="divide-y divide-gray-200 dark:divide-gray-700">
					{#each reports as report (report.id)}
						<div
							class="p-6 transition-colors duration-200 hover:bg-gray-50 dark:hover:bg-gray-700"
							in:fade={{ duration: 200 }}
						>
							<div class="flex items-center justify-between">
								<div class="flex items-center space-x-4">
									<!-- Report Icon -->
									<div class="text-2xl">
										{getReportTypeIcon(report.type)}
									</div>

									<!-- Report Info -->
									<div>
										<h4
											class="font-sans text-lg font-semibold tracking-tight text-gray-900 dark:text-gray-100"
										>
											{report.title || $t(`reports.type.${report.type}`)}
										</h4>
										<div
											class="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400"
										>
											<span>{$t(`reports.period.${report.period}`)}</span>
											<span>•</span>
											<span>{formatDate(report.created_at)}</span>
											<span>•</span>
											<span
												class="inline-flex items-center rounded-xl px-2 py-1 text-xs font-medium {getStatusBadge(
													report.status
												)}"
											>
												{$t(`reports.status.${report.status}`)}
											</span>
										</div>
									</div>
								</div>

								<!-- Actions -->
								<div class="flex items-center space-x-2">
									{#if report.status === 'completed'}
										<Button
											variant="outline"
											size="sm"
											on:click={() => handleDownloadReport(report.id)}
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
													d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
												/>
											</svg>
											{$t('reports.download')}
										</Button>
									{:else if report.status === 'generating'}
										<div
											class="flex items-center space-x-2 text-sm text-blue-600 dark:text-blue-400"
										>
											<svg
												class="mr-2 -ml-1 h-4 w-4 animate-spin"
												xmlns="http://www.w3.org/2000/svg"
												fill="none"
												viewBox="0 0 24 24"
											>
												<circle
													class="opacity-25"
													cx="12"
													cy="12"
													r="10"
													stroke="currentColor"
													stroke-width="4"
												></circle>
												<path
													class="opacity-75"
													fill="currentColor"
													d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
												></path>
											</svg>
											{$t('reports.generating')}
										</div>
									{/if}

									<Button
										variant="ghost"
										size="sm"
										class="text-red-600 hover:bg-red-50 hover:text-red-700 dark:hover:bg-red-900/20"
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
	</div>

	<!-- Generate Report Modal -->
	<Modal bind:show={showGenerateModal} title={$t('reports.generateNew')}>
		<form on:submit|preventDefault={handleGenerateReport} class="space-y-6">
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
				<div>
					<label for="type" class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
						{$t('reports.reportType')} *
					</label>
					<select
						id="type"
						bind:value={reportData.type}
						required
						class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
					>
						<option value="financial">{$t('reports.type.financial')}</option>
						<option value="occupancy">{$t('reports.type.occupancy')}</option>
						<option value="maintenance">{$t('reports.type.maintenance')}</option>
						<option value="tenant">{$t('reports.type.tenant')}</option>
						<option value="expense">{$t('reports.type.expense')}</option>
					</select>
				</div>

				<div>
					<label
						for="period"
						class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('reports.period.title')} *
					</label>
					<select
						id="period"
						bind:value={reportData.period}
						required
						class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
					>
						<option value="week">{$t('reports.period.week')}</option>
						<option value="month">{$t('reports.period.month')}</option>
						<option value="quarter">{$t('reports.period.quarter')}</option>
						<option value="year">{$t('reports.period.year')}</option>
						<option value="custom">{$t('reports.period.custom')}</option>
					</select>
				</div>

				{#if reportData.period === 'custom'}
					<div>
						<label
							for="start_date"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('reports.startDate')} *
						</label>
						<input
							type="date"
							id="start_date"
							bind:value={reportData.start_date}
							required
							class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
						/>
					</div>

					<div>
						<label
							for="end_date"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('reports.endDate')} *
						</label>
						<input
							type="date"
							id="end_date"
							bind:value={reportData.end_date}
							required
							class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
						/>
					</div>
				{/if}

				<div>
					<label
						for="format"
						class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('reports.format')} *
					</label>
					<select
						id="format"
						bind:value={reportData.format}
						required
						class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
					>
						<option value="pdf">PDF</option>
						<option value="excel">Excel</option>
						<option value="csv">CSV</option>
					</select>
				</div>
			</div>

			<!-- Options -->
			<div class="space-y-4">
				<h4 class="text-md font-medium text-gray-900 dark:text-gray-100">
					{$t('reports.options')}
				</h4>

				<div class="flex items-center space-x-3">
					<input
						type="checkbox"
						id="include_charts"
						bind:checked={reportData.include_charts}
						class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
					/>
					<label for="include_charts" class="text-sm text-gray-700 dark:text-gray-300">
						{$t('reports.includeCharts')}
					</label>
				</div>

				<div class="flex items-center space-x-3">
					<input
						type="checkbox"
						id="include_summary"
						bind:checked={reportData.include_summary}
						class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
					/>
					<label for="include_summary" class="text-sm text-gray-700 dark:text-gray-300">
						{$t('reports.includeSummary')}
					</label>
				</div>
			</div>

			<div class="flex justify-end space-x-4 border-t border-gray-200 pt-6 dark:border-gray-700">
				<Button
					type="button"
					variant="outline"
					on:click={() => (showGenerateModal = false)}
					disabled={generating}
				>
					{$t('common.cancel')}
				</Button>
				<Button
					type="submit"
					variant="primary"
					class="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700"
					disabled={generating}
				>
					{#if generating}
						<svg
							class="mr-3 -ml-1 h-4 w-4 animate-spin text-white"
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
						>
							<circle
								class="opacity-25"
								cx="12"
								cy="12"
								r="10"
								stroke="currentColor"
								stroke-width="4"
							></circle>
							<path
								class="opacity-75"
								fill="currentColor"
								d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
							></path>
						</svg>
						{$t('reports.generating')}
					{:else}
						<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 6v6m0 0v6m0-6h6m-6 0H6"
							/>
						</svg>
						{$t('reports.generate')}
					{/if}
				</Button>
			</div>
		</form>
	</Modal>
{/if}
