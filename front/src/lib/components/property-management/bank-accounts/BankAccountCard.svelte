<!-- src/lib/components/property-management/bank-accounts/BankAccountCard.svelte -->
<script>
	import { t } from '$lib/i18n';
	import { formatIBAN } from '$lib/api/bankAccount';
	import Button from '$lib/components/ui/Button.svelte';

	// Props
	export let account;
	export let onEdit = null;
	export let onDelete = null;
	export let onSetPrimary = null;
	export let compact = false;
	export let showActions = true;

	// Svelte 5 runes for reactive state
	let isHovered = $state(false);

	// Derived state
	let statusColor = $derived(account.is_verified ? 'green' : 'yellow');
	let statusText = $derived(account.is_verified ? $t('bankAccount.verified') : $t('bankAccount.pending'));
	let accountTypeLabel = $derived(getAccountTypeLabel(account.account_type));

	// Get account type label
	function getAccountTypeLabel(type) {
		const types = {
			checking: $t('bankAccount.types.checking'),
			savings: $t('bankAccount.types.savings'),
			business: $t('bankAccount.types.business'),
			investment: $t('bankAccount.types.investment')
		};
		return types[type] || type;
	}

	// Handle actions
	function handleEdit() {
		if (onEdit) onEdit(account);
	}

	function handleDelete() {
		if (onDelete) onDelete(account);
	}

	function handleSetPrimary() {
		if (onSetPrimary) onSetPrimary(account);
	}
</script>

<div 
	class="relative rounded-lg border bg-white shadow-sm transition-all duration-200 dark:bg-gray-800 
		{compact ? 'border-gray-200 p-4 dark:border-gray-700' : 'border-gray-200 p-6 dark:border-gray-700'} 
		{isHovered ? 'shadow-md' : 'shadow-sm'}"
	onmouseenter={() => isHovered = true}
	onmouseleave={() => isHovered = false}
>
	<!-- Primary Badge -->
	{#if account.is_primary}
		<div class="absolute {compact ? 'top-2 right-2' : 'top-4 right-4'}">
			<span class="inline-flex items-center rounded-full bg-primary-100 px-2 py-0.5 text-xs font-medium text-primary-800 dark:bg-primary-900 dark:text-primary-200">
				<svg class="mr-1 h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
					<path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
				</svg>
				{$t('bankAccount.primary')}
			</span>
		</div>
	{/if}

	<!-- Account Content -->
	<div class="space-y-{compact ? '3' : '4'}">
		<!-- Header: Bank Name & Account Name -->
		<div class="{account.is_primary ? 'pr-16' : ''}">
			<h3 class="text-{compact ? 'base' : 'lg'} font-medium text-gray-900 dark:text-white">
				{account.bank_name}
			</h3>
			<p class="text-sm text-gray-600 dark:text-gray-400">
				{account.bank_account_name}
			</p>
		</div>

		<!-- Account Details Grid -->
		<div class="space-y-{compact ? '2' : '3'}">
			<!-- IBAN -->
			<div>
				<label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
					{$t('bankAccount.iban')}
				</label>
				<p class="mt-0.5 font-mono text-{compact ? 'xs' : 'sm'} text-gray-900 dark:text-white break-all">
					{formatIBAN(account.iban_number)}
				</p>
			</div>

			<!-- Account Number (if available) -->
			{#if account.account_number}
				<div>
					<label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
						{$t('bankAccount.accountNumber')}
					</label>
					<p class="mt-0.5 font-mono text-{compact ? 'xs' : 'sm'} text-gray-900 dark:text-white">
						{account.account_number}
					</p>
				</div>
			{/if}

			<!-- SWIFT Code (if available) -->
			{#if account.swift_code && !compact}
				<div>
					<label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
						{$t('bankAccount.swiftCode')}
					</label>
					<p class="mt-0.5 font-mono text-sm text-gray-900 dark:text-white">
						{account.swift_code}
					</p>
				</div>
			{/if}

			<!-- Account Type & Status Row -->
			<div class="flex items-center justify-between">
				<!-- Account Type -->
				<div>
					<label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
						{$t('bankAccount.type')}
					</label>
					<p class="mt-0.5 text-{compact ? 'xs' : 'sm'} text-gray-900 dark:text-white">
						{accountTypeLabel}
					</p>
				</div>

				<!-- Status -->
				<div class="text-right">
					<label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
						{$t('common.status')}
					</label>
					<div class="mt-0.5 flex items-center justify-end space-x-1">
						<div class="flex h-2 w-2 rounded-full bg-{statusColor}-400"></div>
						<span class="text-{compact ? 'xs' : 'sm'} text-gray-600 dark:text-gray-400">
							{statusText}
						</span>
					</div>
				</div>
			</div>
		</div>

		<!-- Notes (if available and not compact) -->
		{#if account.notes && !compact}
			<div>
				<label class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
					{$t('bankAccount.notes')}
				</label>
				<p class="mt-0.5 text-sm text-gray-600 dark:text-gray-400">
					{account.notes}
				</p>
			</div>
		{/if}

		<!-- Actions -->
		{#if showActions}
			<div class="flex space-x-2 pt-{compact ? '3' : '4'} border-t border-gray-200 dark:border-gray-700">
				<!-- Edit Button -->
				<Button 
					onClick={handleEdit}
					variant="outline" 
					size={compact ? "compact" : "small"}
					class="flex-1"
				>
					<svg class="mr-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
					</svg>
					{$t('common.edit')}
				</Button>

				<!-- Set Primary Button -->
				{#if !account.is_primary}
					<Button 
						onClick={handleSetPrimary}
						variant="outline" 
						size={compact ? "compact" : "small"}
						class="flex-1"
					>
						<svg class="mr-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
						</svg>
						{compact ? $t('bankAccount.primary') : $t('bankAccount.setPrimary')}
					</Button>
				{/if}

				<!-- Delete Button -->
				<Button 
					onClick={handleDelete}
					variant="outline"
					size={compact ? "compact" : "small"}
					class="text-red-600 hover:text-red-700 hover:border-red-300 dark:text-red-400 dark:hover:text-red-300"
				>
					<svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
							d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
					</svg>
					{#if !compact}
						<span class="ml-1">{$t('common.delete')}</span>
					{/if}
				</Button>
			</div>
		{/if}

		<!-- Created Date -->
		{#if !compact}
			<div class="pt-2 border-t border-gray-100 dark:border-gray-700">
				<p class="text-xs text-gray-500 dark:text-gray-400">
					{$t('bankAccount.addedOn')} {new Date(account.created_at).toLocaleDateString()}
				</p>
			</div>
		{/if}
	</div>
</div>