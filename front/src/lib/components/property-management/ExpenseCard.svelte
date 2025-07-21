<script>
	import { createEventDispatcher } from 'svelte';
	import { t } from '$lib/i18n';
	import { formatCurrency } from '$lib/utils/currency.js';
	import Button from '$lib/components/ui/Button.svelte';

	const dispatch = createEventDispatcher();

	/** @type {Object} */
	export let expense;
	/** @type {string} */
	export let variant = 'default'; // 'default', 'compact', 'dashboard'
	/** @type {boolean} */
	export let showActions = true;
	/** @type {boolean} */
	export let loading = false;

	$: property = expense?.property;
	$: category = expense?.category;
	$: createdBy = expense?.created_by;
	$: approvedBy = expense?.approved_by;

	function handleViewDetails() {
		dispatch('view', { expense });
	}

	function handleEdit() {
		dispatch('edit', { expense });
	}

	function handleApprove() {
		dispatch('approve', { expense });
	}

	function handleReject() {
		dispatch('reject', { expense });
	}

	function handleViewProperty() {
		dispatch('viewProperty', { expense, property });
	}

	function getStatusBadgeClass(status) {
		switch (status) {
			case 'pending':
				return 'bg-yellow-100 text-yellow-800 border-yellow-200';
			case 'approved':
				return 'bg-green-100 text-green-800 border-green-200';
			case 'rejected':
				return 'bg-red-100 text-red-800 border-red-200';
			case 'paid':
				return 'bg-blue-100 text-blue-800 border-blue-200';
			default:
				return 'bg-gray-100 text-gray-800 border-gray-200';
		}
	}

	function getExpenseTypeIcon(type) {
		const iconMap = {
			maintenance: '🔧',
			utilities: '⚡',
			insurance: '🛡️',
			taxes: '🏛️',
			management: '👥',
			supplies: '📦',
			advertising: '📢',
			legal: '⚖️',
			accounting: '📊',
			other: '📝'
		};
		return iconMap[type] || '📝';
	}

	function formatDateAgo(dateString) {
		if (!dateString) return '';
		const date = new Date(dateString);
		const now = new Date();
		const diffTime = Math.abs(now - date);
		const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

		if (diffDays === 0) {
			return $t('common.today');
		} else if (diffDays === 1) {
			return $t('common.yesterday');
		} else if (diffDays < 7) {
			return $t('common.daysAgo', { count: diffDays });
		} else {
			return date.toLocaleDateString();
		}
	}

	function getInitials(firstName, lastName) {
		return `${firstName?.charAt(0) || ''}${lastName?.charAt(0) || ''}`.toUpperCase();
	}

	$: isOverdue =
		expense.due_date && new Date(expense.due_date) < new Date() && expense.status !== 'paid';
	$: daysUntilDue = expense.due_date
		? Math.ceil((new Date(expense.due_date) - new Date()) / (1000 * 60 * 60 * 24))
		: null;
</script>

<div
	class="rounded-lg border border-gray-200 bg-white shadow-sm transition-all duration-200 hover:border-gray-300 hover:shadow-md"
>
	<div class="p-4">
		<!-- Header with Type Icon and Status -->
		<div class="mb-3 flex items-start justify-between">
			<div class="flex items-center gap-2">
				<!-- Expense Type Icon -->
				<span class="text-2xl">{getExpenseTypeIcon(expense.expense_type)}</span>

				<!-- Recurring Badge -->
				{#if expense.is_recurring}
					<span
						class="inline-flex items-center rounded-full border border-purple-200 bg-purple-100 px-2 py-0.5 text-xs font-medium text-purple-800"
					>
						🔄 {$t('expense.recurring')}
					</span>
				{/if}

				<!-- Emergency Badge -->
				{#if expense.is_emergency}
					<span
						class="inline-flex items-center rounded-full border border-red-200 bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800"
					>
						🚨 {$t('expense.emergency')}
					</span>
				{/if}
			</div>

			<!-- Status Badge -->
			<span
				class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium {getStatusBadgeClass(
					expense.status
				)}"
			>
				{$t(`expense.status.${expense.status}`)}
			</span>
		</div>

		<!-- Expense Title and Description -->
		<div class="mb-3">
			<h3 class="mb-1 line-clamp-1 text-lg font-semibold text-gray-900">
				{expense.title || $t('expense.untitledExpense')}
			</h3>
			{#if expense.description}
				<p class="line-clamp-2 text-sm text-gray-600">
					{expense.description}
				</p>
			{/if}
		</div>

		<!-- Amount and Due Date -->
		<div class="mb-3 rounded-lg bg-gray-50 p-3">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-xs text-gray-600">{$t('expense.amount')}</p>
					<p class="text-xl font-bold text-gray-900">{formatCurrency(expense.amount || 0)}</p>
					{#if expense.tax_amount && expense.tax_amount > 0}
						<p class="text-xs text-gray-500">
							+ {formatCurrency(expense.tax_amount)}
							{$t('expense.tax')}
						</p>
					{/if}
				</div>

				{#if expense.due_date}
					<div class="text-right">
						<p class="text-xs text-gray-600">{$t('expense.dueDate')}</p>
						<p class="text-sm font-medium {isOverdue ? 'text-red-600' : 'text-gray-900'}">
							{formatDateAgo(expense.due_date)}
						</p>
						{#if daysUntilDue !== null && !isOverdue}
							<p class="text-xs text-gray-500">
								{daysUntilDue}
								{$t('common.daysRemaining')}
							</p>
						{/if}
					</div>
				{/if}
			</div>
		</div>

		<!-- Property Information -->
		{#if property}
			<div class="mb-3 rounded-lg bg-blue-50 p-2">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-xs font-medium text-blue-900">{$t('expense.property')}</p>
						<p class="truncate text-sm text-blue-800">{property.title}</p>
					</div>
					<Button variant="ghost" size="sm" on:click={handleViewProperty}>
						{$t('property.view')}
					</Button>
				</div>
			</div>
		{/if}

		<!-- Expense Details Grid -->
		<div class="mb-3 grid grid-cols-2 gap-3 text-sm">
			<!-- Category -->
			<div>
				<p class="text-gray-600">{$t('expense.category')}</p>
				<p class="font-medium">{category?.name || $t('common.uncategorized')}</p>
			</div>

			<!-- Expense Date -->
			<div>
				<p class="text-gray-600">{$t('expense.expenseDate')}</p>
				<p class="font-medium">{formatDateAgo(expense.expense_date)}</p>
			</div>

			<!-- Vendor -->
			{#if expense.vendor_name}
				<div>
					<p class="text-gray-600">{$t('expense.vendor')}</p>
					<p class="truncate font-medium">{expense.vendor_name}</p>
				</div>
			{/if}

			<!-- Total Amount (with tax) -->
			{#if expense.total_amount && expense.total_amount !== expense.amount}
				<div>
					<p class="text-gray-600">{$t('expense.totalAmount')}</p>
					<p class="font-bold text-green-600">{formatCurrency(expense.total_amount)}</p>
				</div>
			{/if}
		</div>

		<!-- People Involved -->
		<div class="mb-3 flex items-center gap-4 text-sm">
			<!-- Created By -->
			{#if createdBy}
				<div class="flex items-center gap-2">
					<div
						class="flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-xs font-semibold text-white"
					>
						{getInitials(createdBy.first_name, createdBy.last_name)}
					</div>
					<div>
						<p class="text-gray-600">{$t('expense.createdBy')}</p>
						<p class="text-xs font-medium">{createdBy.first_name} {createdBy.last_name}</p>
					</div>
				</div>
			{/if}

			<!-- Approved By -->
			{#if approvedBy}
				<div class="flex items-center gap-2">
					<div
						class="flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-green-500 to-teal-600 text-xs font-semibold text-white"
					>
						{getInitials(approvedBy.first_name, approvedBy.last_name)}
					</div>
					<div>
						<p class="text-gray-600">{$t('expense.approvedBy')}</p>
						<p class="text-xs font-medium">{approvedBy.first_name} {approvedBy.last_name}</p>
					</div>
				</div>
			{/if}
		</div>

		<!-- Overdue Warning -->
		{#if isOverdue}
			<div class="mb-3 rounded-lg border border-red-200 bg-red-50 p-2">
				<div class="flex items-center gap-2">
					<span class="text-red-600">⚠️</span>
					<span class="text-sm font-medium text-red-800">
						{$t('expense.overdue')} ({Math.abs(daysUntilDue)}
						{$t('common.daysOverdue')})
					</span>
				</div>
			</div>
		{/if}

		<!-- Tax Deductible Info -->
		{#if category?.is_tax_deductible}
			<div class="mb-3 rounded-lg border border-green-200 bg-green-50 p-2">
				<div class="flex items-center gap-2">
					<span class="text-green-600">💰</span>
					<span class="text-sm font-medium text-green-800">{$t('expense.taxDeductible')}</span>
				</div>
			</div>
		{/if}

		<!-- Notes -->
		{#if expense.notes && expense.notes.trim()}
			<div class="mb-3 rounded border-l-4 border-yellow-400 bg-yellow-50 p-2">
				<p class="text-sm text-yellow-800">
					<strong>{$t('common.notes')}:</strong>
					{expense.notes}
				</p>
			</div>
		{/if}

		<!-- Payment Date -->
		{#if expense.status === 'paid' && expense.payment_date}
			<div class="mb-3 rounded border-l-4 border-blue-400 bg-blue-50 p-2">
				<p class="text-sm text-blue-800">
					<strong>{$t('expense.paidOn')}:</strong>
					{new Date(expense.payment_date).toLocaleDateString()}
				</p>
			</div>
		{/if}

		<!-- Action Buttons -->
		{#if showActions}
			<div class="flex flex-wrap gap-2">
				<Button variant="primary" size="sm" {loading} on:click={handleViewDetails}>
					{$t('common.viewDetails')}
				</Button>

				<Button variant="outline" size="sm" on:click={handleEdit}>
					{$t('common.edit')}
				</Button>

				{#if expense.status === 'pending'}
					<Button variant="success" size="sm" on:click={handleApprove}>
						✅ {$t('expense.approve')}
					</Button>

					<Button variant="ghost" size="sm" on:click={handleReject}>
						❌ {$t('expense.reject')}
					</Button>
				{/if}
			</div>
		{/if}
	</div>
</div>

<style>
	.line-clamp-1 {
		display: -webkit-box;
		-webkit-line-clamp: 1;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
</style>
