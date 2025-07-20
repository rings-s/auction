<!-- src/lib/components/property-management/payments/PaymentDashboard.svelte -->
<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/i18n';
	import { 
		getPayments, 
		generatePaymentReport,
		getOverduePayments,
		getUpcomingPayments,
		formatCurrency,
		getPaymentStatuses,
		getPaymentTypes
	} from '$lib/api/payment';
	import { toast } from '$lib/stores/toastStore.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import StatCard from '$lib/components/dashboard/StatCard.svelte';

	// Svelte 5 runes for reactive state
	let payments = $state([]);
	let overduePayments = $state([]);
	let upcomingPayments = $state([]);
	let loading = $state(true);
	let error = $state(null);
	let reportLoading = $state(false);
	let selectedTimeRange = $state('30d');
	let selectedPaymentType = $state('all');
	let selectedStatus = $state('all');

	// Derived state for statistics
	let totalPayments = $derived(payments.length);
	let completedPayments = $derived(payments.filter(p => p.status === 'completed').length);
	let pendingPayments = $derived(payments.filter(p => p.status === 'pending').length);
	let totalAmount = $derived(payments.reduce((sum, p) => sum + parseFloat(p.amount || 0), 0));
	let completedAmount = $derived(
		payments
			.filter(p => p.status === 'completed')
			.reduce((sum, p) => sum + parseFloat(p.amount || 0), 0)
	);
	let pendingAmount = $derived(
		payments
			.filter(p => p.status === 'pending')
			.reduce((sum, p) => sum + parseFloat(p.amount || 0), 0)
	);
	let overdueAmount = $derived(
		overduePayments.reduce((sum, p) => sum + parseFloat(p.amount || 0), 0)
	);

	// Completion rate
	let completionRate = $derived(
		totalPayments > 0 ? ((completedPayments / totalPayments) * 100).toFixed(1) : 0
	);

	// Filter options
	let timeRangeOptions = $derived([
		{ value: '7d', label: $t('common.last7days') },
		{ value: '30d', label: $t('common.last30days') },
		{ value: '90d', label: $t('common.last90days') },
		{ value: '1y', label: $t('common.lastYear') }
	]);

	let paymentTypeOptions = $derived([
		{ value: 'all', label: $t('common.all') },
		...getPaymentTypes()
	]);

	let statusOptions = $derived([
		{ value: 'all', label: $t('common.all') },
		...getPaymentStatuses()
	]);

	// Load data on mount and when filters change
	onMount(async () => {
		await loadPaymentData();
	});

	// Watch for filter changes
	$effect(() => {
		// Re-load data when filters change
		if (selectedTimeRange || selectedPaymentType || selectedStatus) {
			loadPaymentData();
		}
	});

	// Load payment data with filters
	async function loadPaymentData() {
		try {
			loading = true;
			error = null;

			const filters = buildFilters();
			
			const [allPayments, overdue, upcoming] = await Promise.all([
				getPayments(filters),
				getOverduePayments(),
				getUpcomingPayments()
			]);

			payments = allPayments;
			overduePayments = overdue;
			upcomingPayments = upcoming;
		} catch (err) {
			error = err.message;
			toast.error($t('payment.loadError'));
		} finally {
			loading = false;
		}
	}

	// Build filter object
	function buildFilters() {
		const filters = {};

		// Time range filter
		if (selectedTimeRange !== 'all') {
			const endDate = new Date();
			let startDate = new Date();

			switch (selectedTimeRange) {
				case '7d':
					startDate.setDate(endDate.getDate() - 7);
					break;
				case '30d':
					startDate.setDate(endDate.getDate() - 30);
					break;
				case '90d':
					startDate.setDate(endDate.getDate() - 90);
					break;
				case '1y':
					startDate.setFullYear(endDate.getFullYear() - 1);
					break;
			}

			filters.payment_date__gte = startDate.toISOString().split('T')[0];
			filters.payment_date__lte = endDate.toISOString().split('T')[0];
		}

		// Payment type filter
		if (selectedPaymentType !== 'all') {
			filters.payment_type = selectedPaymentType;
		}

		// Status filter
		if (selectedStatus !== 'all') {
			filters.status = selectedStatus;
		}

		return filters;
	}

	// Generate and download report
	async function generateReport() {
		try {
			reportLoading = true;
			const filters = buildFilters();
			const report = await generatePaymentReport(filters);
			
			// Create and download file
			const blob = new Blob([JSON.stringify(report, null, 2)], { 
				type: 'application/json' 
			});
			const url = URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = `payment-report-${new Date().toISOString().split('T')[0]}.json`;
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
			URL.revokeObjectURL(url);
			
			toast.success($t('payment.reportGenerated'));
		} catch (err) {
			toast.error($t('payment.reportError'));
		} finally {
			reportLoading = false;
		}
	}

	// Get status color for display
	function getStatusColor(status) {
		const colors = {
			completed: 'green',
			pending: 'yellow',
			processing: 'blue',
			failed: 'red',
			cancelled: 'gray',
			refunded: 'purple'
		};
		return colors[status] || 'gray';
	}
</script>

<svelte:head>
	<title>{$t('payment.dashboard')} - {$t('app.name')}</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
		<div>
			<h1 class="text-2xl font-bold text-gray-900 dark:text-white">
				{$t('payment.dashboard')}
			</h1>
			<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
				{$t('payment.dashboardDescription')}
			</p>
		</div>
		
		<div class="mt-4 sm:mt-0 flex space-x-3">
			<Button 
				onClick={generateReport}
				variant="outline"
				loading={reportLoading}
			>
				<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
				</svg>
				{$t('payment.generateReport')}
			</Button>
			
			<Button 
				href="/create/payment" 
				variant="primary"
			>
				<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
				</svg>
				{$t('payment.add')}
			</Button>
		</div>
	</div>

	<!-- Filters -->
	<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
		<div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
			<!-- Time Range Filter -->
			<div>
				<label for="timeRange" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
					{$t('common.timeRange')}
				</label>
				<select
					id="timeRange"
					bind:value={selectedTimeRange}
					class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
				>
					{#each timeRangeOptions as option}
						<option value={option.value}>{option.label}</option>
					{/each}
				</select>
			</div>

			<!-- Payment Type Filter -->
			<div>
				<label for="paymentType" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
					{$t('payment.type')}
				</label>
				<select
					id="paymentType"
					bind:value={selectedPaymentType}
					class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
				>
					{#each paymentTypeOptions as option}
						<option value={option.value}>{option.label}</option>
					{/each}
				</select>
			</div>

			<!-- Status Filter -->
			<div>
				<label for="status" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
					{$t('common.status')}
				</label>
				<select
					id="status"
					bind:value={selectedStatus}
					class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
				>
					{#each statusOptions as option}
						<option value={option.value}>{option.label}</option>
					{/each}
				</select>
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
			<!-- Total Payments -->
			<StatCard
				title={$t('payment.totalPayments')}
				value={totalPayments}
				icon='<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M4 4a2 2 0 00-2 2v1h16V6a2 2 0 00-2-2H4z"></path><path fill-rule="evenodd" d="M18 9H2v5a2 2 0 002 2h12a2 2 0 002-2V9zM4 13a1 1 0 011-1h1a1 1 0 110 2H5a1 1 0 01-1-1zm5-1a1 1 0 100 2h1a1 1 0 100-2H9z" clip-rule="evenodd"></path></svg>'
				color="primary"
				href="/dashboard/payments"
			/>

			<!-- Total Amount -->
			<StatCard
				title={$t('payment.totalAmount')}
				value={formatCurrency(totalAmount)}
				icon='<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z"></path><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd"></path></svg>'
				color="success"
			/>

			<!-- Completion Rate -->
			<StatCard
				title={$t('payment.completionRate')}
				value={`${completionRate}%`}
				icon='<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>'
				color={parseFloat(completionRate) >= 80 ? 'success' : parseFloat(completionRate) >= 60 ? 'warning' : 'error'}
			/>

			<!-- Overdue Amount -->
			<StatCard
				title={$t('payment.overdueAmount')}
				value={formatCurrency(overdueAmount)}
				icon='<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"></path></svg>'
				color={overdueAmount > 0 ? 'error' : 'success'}
			/>
		</div>
	{/if}

	<!-- Quick Actions Section -->
	<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
		<!-- Overdue Payments -->
		{#if overduePayments.length > 0}
			<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
				<div class="p-6">
					<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
						{$t('payment.overduePayments')} ({overduePayments.length})
					</h3>
					
					<div class="space-y-3">
						{#each overduePayments.slice(0, 5) as payment}
							<div class="flex items-center justify-between p-3 bg-red-50 dark:bg-red-900/20 rounded-md">
								<div>
									<p class="text-sm font-medium text-gray-900 dark:text-white">
										{payment.payment_id}
									</p>
									<p class="text-xs text-gray-600 dark:text-gray-400">
										{$t('payment.dueDate')}: {new Date(payment.due_date).toLocaleDateString()}
									</p>
								</div>
								<div class="text-right">
									<p class="text-sm font-medium text-red-600 dark:text-red-400">
										{formatCurrency(payment.amount)}
									</p>
									<p class="text-xs text-gray-500">
										{payment.payment_type}
									</p>
								</div>
							</div>
						{/each}
						
						{#if overduePayments.length > 5}
							<Button 
								href="/dashboard/payments?filter=overdue"
								variant="outline"
								size="compact"
								class="w-full"
							>
								{$t('payment.viewAllOverdue', { count: overduePayments.length })}
							</Button>
						{/if}
					</div>
				</div>
			</div>
		{/if}

		<!-- Upcoming Payments -->
		{#if upcomingPayments.length > 0}
			<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
				<div class="p-6">
					<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
						{$t('payment.upcomingPayments')} ({upcomingPayments.length})
					</h3>
					
					<div class="space-y-3">
						{#each upcomingPayments.slice(0, 5) as payment}
							<div class="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-md">
								<div>
									<p class="text-sm font-medium text-gray-900 dark:text-white">
										{payment.payment_id}
									</p>
									<p class="text-xs text-gray-600 dark:text-gray-400">
										{$t('payment.dueDate')}: {new Date(payment.due_date).toLocaleDateString()}
									</p>
								</div>
								<div class="text-right">
									<p class="text-sm font-medium text-yellow-600 dark:text-yellow-400">
										{formatCurrency(payment.amount)}
									</p>
									<p class="text-xs text-gray-500">
										{payment.payment_type}
									</p>
								</div>
							</div>
						{/each}
						
						{#if upcomingPayments.length > 5}
							<Button 
								href="/dashboard/payments?filter=upcoming"
								variant="outline"
								size="compact"
								class="w-full"
							>
								{$t('payment.viewAllUpcoming', { count: upcomingPayments.length })}
							</Button>
						{/if}
					</div>
				</div>
			</div>
		{/if}
	</div>

	<!-- Recent Payments -->
	{#if !loading && payments.length > 0}
		<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
			<div class="p-6">
				<div class="flex items-center justify-between mb-4">
					<h3 class="text-lg font-medium text-gray-900 dark:text-white">
						{$t('payment.recentPayments')}
					</h3>
					<Button 
						href="/dashboard/payments"
						variant="outline"
						size="compact"
					>
						{$t('common.viewAll')}
					</Button>
				</div>
				
				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
						<thead class="bg-gray-50 dark:bg-gray-700">
							<tr>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
									{$t('payment.id')}
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
									{$t('payment.type')}
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
									{$t('common.amount')}
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
									{$t('common.status')}
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
									{$t('payment.date')}
								</th>
							</tr>
						</thead>
						<tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
							{#each payments.slice(0, 10) as payment}
								<tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
									<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
										{payment.payment_id}
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
										{payment.payment_type}
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
										{formatCurrency(payment.amount)}
									</td>
									<td class="px-6 py-4 whitespace-nowrap">
										<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-{getStatusColor(payment.status)}-100 text-{getStatusColor(payment.status)}-800 dark:bg-{getStatusColor(payment.status)}-900 dark:text-{getStatusColor(payment.status)}-200">
											{payment.status}
										</span>
									</td>
									<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
										{payment.payment_date ? new Date(payment.payment_date).toLocaleDateString() : $t('common.pending')}
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