<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import { userStore } from '$lib/stores/user.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import { expensesAPI } from '$lib/api/propertyManagement.js';
	import { fade } from 'svelte/transition';

	// State
	let loading = true;
	let error = '';
	let expenses = [];
	let searchTerm = '';
	let categoryFilter = 'all';
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

	// Filter expenses based on search term and filters
	$: filteredExpenses = expenses.filter((expense) => {
		const matchesSearch =
			expense.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
			expense.vendor?.toLowerCase().includes(searchTerm.toLowerCase()) ||
			expense.property?.name?.toLowerCase().includes(searchTerm.toLowerCase());

		const matchesCategory = categoryFilter === 'all' || expense.category === categoryFilter;
		const matchesStatus = statusFilter === 'all' || expense.status === statusFilter;

		return matchesSearch && matchesCategory && matchesStatus;
	});

	onMount(() => {
		if (!hasAccess) {
			goto('/dashboard');
			return;
		}
		loadExpenses();
	});

	async function loadExpenses() {
		try {
			loading = true;
			error = '';

			const response = await expensesAPI.expenses.getAll({
				page: pagination.page,
				page_size: pagination.pageSize,
				search: searchTerm || undefined,
				category: categoryFilter !== 'all' ? categoryFilter : undefined,
				status: statusFilter !== 'all' ? statusFilter : undefined,
				ordering: '-date'
			});

			if (response.data) {
				expenses = response.data.results || [];
				pagination = {
					...pagination,
					total: response.data.count || 0,
					totalPages: Math.ceil((response.data.count || 0) / pagination.pageSize)
				};
			}
		} catch (err) {
			error = err.message || $t('errors.loadingFailed');
			console.error('Failed to load expenses:', err);
		} finally {
			loading = false;
		}
	}

	async function handleDeleteExpense(expenseId) {
		if (!confirm($t('common.confirmDelete'))) return;

		try {
			await expensesAPI.expenses.delete(expenseId);
			expenses = expenses.filter((e) => e.id !== expenseId);
		} catch (err) {
			error = err.message || $t('errors.deleteFailed');
		}
	}

	async function handleUpdateStatus(expenseId, newStatus) {
		try {
			const response = await expensesAPI.expenses.patch(expenseId, { status: newStatus });
			if (response.data) {
				expenses = expenses.map((e) => (e.id === expenseId ? { ...e, status: newStatus } : e));
			}
		} catch (err) {
			error = err.message || $t('errors.updateFailed');
		}
	}

	function getStatusBadge(status) {
		const classes = {
			pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100',
			paid: 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100',
			overdue: 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
		};
		return classes[status] || classes.pending;
	}

	function getCategoryIcon(category) {
		const icons = {
			maintenance: '🔧',
			utilities: '⚡',
			insurance: '🛡️',
			taxes: '📊',
			supplies: '📦',
			services: '🤝',
			other: '📝'
		};
		return icons[category] || '💰';
	}

	function formatDate(dateString) {
		return new Date(dateString).toLocaleDateString();
	}

	// Calculate totals
	$: totalExpenses = expenses.reduce((sum, expense) => sum + (expense.amount || 0), 0);
	$: paidExpenses = expenses
		.filter((e) => e.status === 'paid')
		.reduce((sum, expense) => sum + (expense.amount || 0), 0);
	$: pendingExpenses = expenses
		.filter((e) => e.status === 'pending')
		.reduce((sum, expense) => sum + (expense.amount || 0), 0);
	$: overdueExpenses = expenses
		.filter((e) => e.status === 'overdue')
		.reduce((sum, expense) => sum + (expense.amount || 0), 0);
</script>

<svelte:head>
	<title>{$t('expense.title')} | {$t('app.name')}</title>
	<meta name="description" content={$t('expense.description')} />
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
					{$t('expense.management')}
				</h1>
				<p class="mt-2 text-gray-600 dark:text-gray-400">
					{$t('expense.subtitle')}
				</p>
			</div>

			<div class="flex flex-wrap gap-4">
				<Button
					variant="primary"
					class="bg-gradient-to-r from-indigo-500 to-purple-600 shadow-lg hover:from-indigo-600 hover:to-purple-700 hover:shadow-xl"
					on:click={() => goto('/property-management/expenses/create')}
				>
					<svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 6v6m0 0v6m0-6h6m-6 0H6"
						/>
					</svg>
					{$t('expense.create')}
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
							{$t('expense.total')}
						</p>
						<p class="text-2xl font-bold text-gray-900 dark:text-gray-100">
							{totalExpenses.toLocaleString()} SAR
						</p>
					</div>
					<div class="text-2xl">💰</div>
				</div>
			</div>

			<div
				class="rounded-2xl border border-gray-200 bg-white p-6 shadow-md dark:border-gray-700 dark:bg-gray-800"
			>
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600 dark:text-gray-400">{$t('expense.paid')}</p>
						<p class="text-2xl font-bold text-green-600 dark:text-green-400">
							{paidExpenses.toLocaleString()} SAR
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
							{$t('expense.pending')}
						</p>
						<p class="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
							{pendingExpenses.toLocaleString()} SAR
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
							{$t('expense.overdue')}
						</p>
						<p class="text-2xl font-bold text-red-600 dark:text-red-400">
							{overdueExpenses.toLocaleString()} SAR
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
						on:input={loadExpenses}
						placeholder={$t('expense.searchPlaceholder')}
						class="w-full rounded-xl border border-gray-300 bg-white py-3 pr-4 pl-10 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
					/>
				</div>

				<div class="flex gap-4">
					<select
						bind:value={categoryFilter}
						on:change={loadExpenses}
						class="rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
					>
						<option value="all">{$t('expense.allCategories')}</option>
						<option value="maintenance">{$t('expense.category.maintenance')}</option>
						<option value="utilities">{$t('expense.category.utilities')}</option>
						<option value="insurance">{$t('expense.category.insurance')}</option>
						<option value="taxes">{$t('expense.category.taxes')}</option>
						<option value="supplies">{$t('expense.category.supplies')}</option>
						<option value="services">{$t('expense.category.services')}</option>
						<option value="other">{$t('expense.category.other')}</option>
					</select>

					<select
						bind:value={statusFilter}
						on:change={loadExpenses}
						class="rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
					>
						<option value="all">{$t('expense.allStatuses')}</option>
						<option value="pending">{$t('expense.status.pending')}</option>
						<option value="paid">{$t('expense.status.paid')}</option>
						<option value="overdue">{$t('expense.status.overdue')}</option>
					</select>
				</div>
			</div>
		</div>

		<!-- Expenses List -->
		<div
			class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-md dark:border-gray-700 dark:bg-gray-800"
		>
			{#if loading}
				<div class="space-y-4 p-6">
					{#each Array(5) as _}
						<LoadingSkeleton height="100px" />
					{/each}
				</div>
			{:else if filteredExpenses.length === 0}
				<div class="p-12 text-center">
					<div class="mb-4 text-6xl">💰</div>
					<h3 class="mb-2 text-lg font-medium text-gray-900 dark:text-gray-100">
						{$t('expense.noExpenses')}
					</h3>
					<p class="mb-6 text-gray-600 dark:text-gray-400">
						{$t('expense.noExpensesDesc')}
					</p>
					<Button variant="primary" on:click={() => goto('/property-management/expenses/create')}>
						{$t('expense.createFirst')}
					</Button>
				</div>
			{:else}
				<div class="divide-y divide-gray-200 dark:divide-gray-700">
					{#each filteredExpenses as expense (expense.id)}
						<div
							class="p-6 transition-colors duration-200 hover:bg-gray-50 dark:hover:bg-gray-700"
							in:fade={{ duration: 200 }}
						>
							<div class="flex items-start justify-between">
								<div class="flex flex-1 items-start space-x-4">
									<!-- Category Icon -->
									<div class="mt-1 text-2xl">
										{getCategoryIcon(expense.category)}
									</div>

									<!-- Expense Info -->
									<div class="min-w-0 flex-1">
										<div class="mb-2 flex items-center space-x-3">
											<h3
												class="font-sans text-lg font-semibold tracking-tight text-gray-900 dark:text-gray-100"
											>
												{expense.description}
											</h3>
											<span
												class="inline-flex items-center rounded-xl px-3 py-1 text-xs font-medium {getStatusBadge(
													expense.status
												)}"
											>
												{$t(`expense.status.${expense.status}`)}
											</span>
											<span class="text-lg font-bold text-gray-900 dark:text-gray-100">
												{expense.amount?.toLocaleString() || 0} SAR
											</span>
										</div>

										<div
											class="grid grid-cols-2 gap-4 text-sm text-gray-600 md:grid-cols-4 dark:text-gray-400"
										>
											<div>
												<p class="font-medium text-gray-900 dark:text-gray-100">
													{$t('expense.vendor')}
												</p>
												<p>{expense.vendor || '-'}</p>
											</div>
											<div>
												<p class="font-medium text-gray-900 dark:text-gray-100">
													{$t('expense.category.title')}
												</p>
												<p>{$t(`expense.category.${expense.category}`) || expense.category}</p>
											</div>
											<div>
												<p class="font-medium text-gray-900 dark:text-gray-100">
													{$t('expense.date')}
												</p>
												<p>{formatDate(expense.date)}</p>
											</div>
											<div>
												<p class="font-medium text-gray-900 dark:text-gray-100">
													{$t('expense.property')}
												</p>
												<p>{expense.property?.name || '-'}</p>
											</div>
										</div>
									</div>
								</div>

								<!-- Actions -->
								<div class="ml-4 flex items-center space-x-2">
									{#if expense.status === 'pending'}
										<Button
											variant="outline"
											size="sm"
											class="text-green-600 hover:bg-green-50 hover:text-green-700 dark:hover:bg-green-900/20"
											on:click={() => handleUpdateStatus(expense.id, 'paid')}
										>
											{$t('expense.markPaid')}
										</Button>
									{/if}

									<Button
										variant="ghost"
										size="sm"
										on:click={() => goto(`/property-management/expenses/${expense.id}`)}
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
										on:click={() => goto(`/property-management/expenses/${expense.id}/edit`)}
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
										on:click={() => handleDeleteExpense(expense.id)}
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
						loadExpenses();
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
						loadExpenses();
					}}
				>
					{$t('common.next')}
				</Button>
			</div>
		{/if}
	</div>
{/if}
