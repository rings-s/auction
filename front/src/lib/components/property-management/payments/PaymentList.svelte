<!-- src/lib/components/property-management/payments/PaymentList.svelte -->
<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/i18n';
	import {
		getPayments,
		deletePayment,
		formatCurrency,
		getPaymentTypes,
		getPaymentStatuses,
		getPaymentStatusColor
	} from '$lib/api/payment';
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
	let payments = $state([]);
	let loading = $state(true);
	let error = $state(null);
	let selectedPayment = $state(null);
	let showDeleteModal = $state(false);
	let deleteLoading = $state(false);
	let sortField = $state('payment_date');
	let sortDirection = $state('desc');
	let filterType = $state('all');
	let filterStatus = $state('all');
	let searchQuery = $state('');

	// Derived state
	let hasPayments = $derived(payments.length > 0);
	let filteredPayments = $derived(getFilteredPayments());
	let displayedPayments = $derived(
		maxItems ? filteredPayments.slice(0, maxItems) : filteredPayments
	);
	let paymentTypes = $derived(getPaymentTypes());
	let paymentStatuses = $derived(getPaymentStatuses());

	// Load payments on mount
	onMount(async () => {
		await loadPayments();
	});

	// Watch for filter changes
	$effect(() => {
		if (filters) {
			loadPayments();
		}
	});

	// Load payments function
	async function loadPayments() {
		try {
			loading = true;
			error = null;
			payments = await getPayments(filters);
		} catch (err) {
			error = err.message;
			toast.error($t('payment.loadError'));
		} finally {
			loading = false;
		}
	}

	// Filter and sort payments
	function getFilteredPayments() {
		let filtered = [...payments];

		// Apply search filter
		if (searchQuery.trim()) {
			const query = searchQuery.toLowerCase();
			filtered = filtered.filter(
				(payment) =>
					payment.payment_id.toLowerCase().includes(query) ||
					payment.description?.toLowerCase().includes(query) ||
					payment.payment_type.toLowerCase().includes(query)
			);
		}

		// Apply type filter
		if (filterType !== 'all') {
			filtered = filtered.filter((payment) => payment.payment_type === filterType);
		}

		// Apply status filter
		if (filterStatus !== 'all') {
			filtered = filtered.filter((payment) => payment.status === filterStatus);
		}

		// Apply sorting
		filtered.sort((a, b) => {
			let valueA = a[sortField];
			let valueB = b[sortField];

			// Handle different data types
			if (sortField.includes('date')) {
				valueA = new Date(valueA || 0);
				valueB = new Date(valueB || 0);
			} else if (sortField === 'amount') {
				valueA = parseFloat(valueA) || 0;
				valueB = parseFloat(valueB) || 0;
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

	// Delete payment
	async function handleDelete() {
		if (!selectedPayment) return;

		try {
			deleteLoading = true;
			await deletePayment(selectedPayment.id);

			// Update local state
			payments = payments.filter((payment) => payment.id !== selectedPayment.id);

			toast.success($t('payment.deleteSuccess'));
			showDeleteModal = false;
			selectedPayment = null;
		} catch (err) {
			toast.error($t('payment.deleteError'));
		} finally {
			deleteLoading = false;
		}
	}

	// Show delete confirmation
	function showDeleteConfirm(payment) {
		selectedPayment = payment;
		showDeleteModal = true;
	}

	// Cancel delete
	function cancelDelete() {
		showDeleteModal = false;
		selectedPayment = null;
	}

	// Format date for display
	function formatDate(dateString) {
		if (!dateString) return $t('common.notSet');
		return new Date(dateString).toLocaleDateString();
	}

	// Get status badge classes
	function getStatusBadgeClass(status) {
		const color = getPaymentStatusColor(status);
		const baseClass = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium';
		return `${baseClass} bg-${color}-100 text-${color}-800 dark:bg-${color}-900 dark:text-${color}-200`;
	}

	// Check if payment is overdue
	function isOverdue(payment) {
		if (payment.status === 'completed' || !payment.due_date) return false;
		return new Date(payment.due_date) < new Date();
	}
</script>

<svelte:head>
	<title>{$t('payment.list')} - {$t('app.name')}</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	{#if !compact}
		<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="text-2xl font-bold text-gray-900 dark:text-white">
					{$t('payment.list')}
				</h1>
				<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
					{$t('payment.listDescription')}
				</p>
			</div>

			<div class="mt-4 sm:mt-0">
				<Button href="/create/payment" variant="primary" class="w-full sm:w-auto">
					<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 4v16m8-8H4"
						/>
					</svg>
					{$t('payment.add')}
				</Button>
			</div>
		</div>
	{/if}

	<!-- Filters -->
	{#if !compact}
		<div
			class="rounded-lg border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800"
		>
			<div class="grid grid-cols-1 gap-4 sm:grid-cols-4">
				<!-- Search -->
				<div>
					<label for="search" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
						{$t('common.search')}
					</label>
					<input
						type="text"
						id="search"
						bind:value={searchQuery}
						placeholder={$t('payment.searchPlaceholder')}
						class="focus:border-primary-500 focus:ring-primary-500 mt-1 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
					/>
				</div>

				<!-- Type Filter -->
				<div>
					<label
						for="typeFilter"
						class="block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('payment.type')}
					</label>
					<select
						id="typeFilter"
						bind:value={filterType}
						class="focus:border-primary-500 focus:ring-primary-500 mt-1 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
					>
						<option value="all">{$t('common.all')}</option>
						{#each paymentTypes as type}
							<option value={type.value}>{type.label}</option>
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
						bind:value={filterStatus}
						class="focus:border-primary-500 focus:ring-primary-500 mt-1 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
					>
						<option value="all">{$t('common.all')}</option>
						{#each paymentStatuses as status}
							<option value={status.value}>{status.label}</option>
						{/each}
					</select>
				</div>

				<!-- Results Count -->
				<div class="flex items-end">
					<p class="text-sm text-gray-600 dark:text-gray-400">
						{$t('common.showing')}
						{displayedPayments.length}
						{$t('common.of')}
						{filteredPayments.length}
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
	{:else if !hasPayments}
		<div class="py-12 text-center">
			<svg
				class="mx-auto h-12 w-12 text-gray-400"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
				/>
			</svg>
			<h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">
				{$t('payment.noPayments')}
			</h3>
			<p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
				{$t('payment.noPaymentsDesc')}
			</p>
			<div class="mt-6">
				<Button href="/create/payment" variant="primary">
					{$t('payment.addFirst')}
				</Button>
			</div>
		</div>

		<!-- Payment Table -->
	{:else}
		<div class="overflow-hidden rounded-lg bg-white shadow-sm dark:bg-gray-800">
			<div class="overflow-x-auto">
				<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
					<thead class="bg-gray-50 dark:bg-gray-700">
						<tr>
							<!-- Payment ID -->
							<th class="px-6 py-3 text-left">
								<button
									onclick={() => handleSort('payment_id')}
									class="group flex items-center space-x-1 text-xs font-medium tracking-wider text-gray-500 uppercase hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-100"
								>
									<span>{$t('payment.id')}</span>
									<svg
										class="h-4 w-4 {sortField === 'payment_id'
											? 'text-gray-700 dark:text-gray-100'
											: 'text-gray-400'}"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"
										/>
									</svg>
								</button>
							</th>

							<!-- Type -->
							<th class="px-6 py-3 text-left">
								<button
									onclick={() => handleSort('payment_type')}
									class="group flex items-center space-x-1 text-xs font-medium tracking-wider text-gray-500 uppercase hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-100"
								>
									<span>{$t('payment.type')}</span>
									<svg
										class="h-4 w-4 {sortField === 'payment_type'
											? 'text-gray-700 dark:text-gray-100'
											: 'text-gray-400'}"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"
										/>
									</svg>
								</button>
							</th>

							<!-- Amount -->
							<th class="px-6 py-3 text-left">
								<button
									onclick={() => handleSort('amount')}
									class="group flex items-center space-x-1 text-xs font-medium tracking-wider text-gray-500 uppercase hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-100"
								>
									<span>{$t('common.amount')}</span>
									<svg
										class="h-4 w-4 {sortField === 'amount'
											? 'text-gray-700 dark:text-gray-100'
											: 'text-gray-400'}"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"
										/>
									</svg>
								</button>
							</th>

							<!-- Status -->
							<th
								class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-300"
							>
								{$t('common.status')}
							</th>

							<!-- Due Date -->
							<th class="px-6 py-3 text-left">
								<button
									onclick={() => handleSort('due_date')}
									class="group flex items-center space-x-1 text-xs font-medium tracking-wider text-gray-500 uppercase hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-100"
								>
									<span>{$t('payment.dueDate')}</span>
									<svg
										class="h-4 w-4 {sortField === 'due_date'
											? 'text-gray-700 dark:text-gray-100'
											: 'text-gray-400'}"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"
										/>
									</svg>
								</button>
							</th>

							<!-- Payment Date -->
							<th class="px-6 py-3 text-left">
								<button
									onclick={() => handleSort('payment_date')}
									class="group flex items-center space-x-1 text-xs font-medium tracking-wider text-gray-500 uppercase hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-100"
								>
									<span>{$t('payment.paymentDate')}</span>
									<svg
										class="h-4 w-4 {sortField === 'payment_date'
											? 'text-gray-700 dark:text-gray-100'
											: 'text-gray-400'}"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"
										/>
									</svg>
								</button>
							</th>

							<!-- Actions -->
							<th
								class="px-6 py-3 text-right text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-300"
							>
								{$t('common.actions')}
							</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-gray-200 bg-white dark:divide-gray-700 dark:bg-gray-800">
						{#each displayedPayments as payment (payment.id)}
							<tr
								class="hover:bg-gray-50 dark:hover:bg-gray-700 {isOverdue(payment)
									? 'bg-red-50 dark:bg-red-900/20'
									: ''}"
							>
								<!-- Payment ID -->
								<td class="px-6 py-4 whitespace-nowrap">
									<div class="flex items-center">
										{#if isOverdue(payment)}
											<svg
												class="mr-2 h-4 w-4 text-red-500"
												fill="currentColor"
												viewBox="0 0 20 20"
											>
												<path
													fill-rule="evenodd"
													d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
													clip-rule="evenodd"
												/>
											</svg>
										{/if}
										<div>
											<div class="font-mono text-sm font-medium text-gray-900 dark:text-white">
												{payment.payment_id}
											</div>
											{#if payment.description}
												<div class="max-w-xs truncate text-sm text-gray-500 dark:text-gray-400">
													{payment.description}
												</div>
											{/if}
										</div>
									</div>
								</td>

								<!-- Type -->
								<td class="px-6 py-4 whitespace-nowrap">
									<span class="text-sm text-gray-900 capitalize dark:text-white">
										{paymentTypes.find((t) => t.value === payment.payment_type)?.label ||
											payment.payment_type}
									</span>
								</td>

								<!-- Amount -->
								<td class="px-6 py-4 whitespace-nowrap">
									<span class="text-sm font-medium text-gray-900 dark:text-white">
										{formatCurrency(payment.amount)}
									</span>
								</td>

								<!-- Status -->
								<td class="px-6 py-4 whitespace-nowrap">
									<span class={getStatusBadgeClass(payment.status)}>
										{paymentStatuses.find((s) => s.value === payment.status)?.label ||
											payment.status}
									</span>
								</td>

								<!-- Due Date -->
								<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-500 dark:text-gray-400">
									{formatDate(payment.due_date)}
								</td>

								<!-- Payment Date -->
								<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-500 dark:text-gray-400">
									{formatDate(payment.payment_date)}
								</td>

								<!-- Actions -->
								<td class="space-x-2 px-6 py-4 text-right text-sm font-medium whitespace-nowrap">
									<Button href="/payments/{payment.id}/edit" variant="outline" size="compact">
										{$t('common.edit')}
									</Button>

									<Button
										onClick={() => showDeleteConfirm(payment)}
										variant="outline"
										size="compact"
										class="text-red-600 hover:border-red-300 hover:text-red-700"
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
	{#if maxItems && filteredPayments.length > maxItems}
		<div class="text-center">
			<Button href="/dashboard/payments" variant="outline">
				{$t('common.viewAll')} ({filteredPayments.length})
			</Button>
		</div>
	{/if}
</div>

<!-- Delete Confirmation Modal -->
<Modal show={showDeleteModal} title={$t('payment.deleteConfirm')} onClose={cancelDelete}>
	<div class="space-y-4">
		<p class="text-sm text-gray-600 dark:text-gray-400">
			{$t('payment.deleteWarning')}
		</p>

		{#if selectedPayment}
			<div class="rounded-md bg-gray-50 p-4 dark:bg-gray-700">
				<div class="space-y-2">
					<p class="font-mono font-medium text-gray-900 dark:text-white">
						{selectedPayment.payment_id}
					</p>
					<p class="text-sm text-gray-600 dark:text-gray-400">
						{paymentTypes.find((t) => t.value === selectedPayment.payment_type)?.label} - {formatCurrency(
							selectedPayment.amount
						)}
					</p>
					{#if selectedPayment.description}
						<p class="text-sm text-gray-600 dark:text-gray-400">
							{selectedPayment.description}
						</p>
					{/if}
				</div>
			</div>
		{/if}

		<div class="flex space-x-3 pt-4">
			<Button onClick={cancelDelete} variant="outline" class="flex-1">
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
