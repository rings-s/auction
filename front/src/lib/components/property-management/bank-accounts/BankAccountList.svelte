<!-- src/lib/components/property-management/bank-accounts/BankAccountList.svelte -->
<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/i18n';
	import { 
		getBankAccounts, 
		deleteBankAccount, 
		setPrimaryBankAccount,
		formatIBAN
	} from '$lib/api/bankAccount';
	import { toast } from '$lib/stores/toastStore.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';

	// Svelte 5 runes for reactive state
	let accounts = $state([]);
	let loading = $state(true);
	let error = $state(null);
	let selectedAccount = $state(null);
	let showDeleteModal = $state(false);
	let deleteLoading = $state(false);
	let primaryLoading = $state(false);

	// Derived state
	let hasAccounts = $derived(accounts.length > 0);
	let primaryAccount = $derived(accounts.find(acc => acc.is_primary));
	let sortedAccounts = $derived(
		accounts.sort((a, b) => {
			if (a.is_primary && !b.is_primary) return -1;
			if (!a.is_primary && b.is_primary) return 1;
			return new Date(b.created_at) - new Date(a.created_at);
		})
	);

	// Load bank accounts on mount
	onMount(async () => {
		await loadBankAccounts();
	});

	// Load bank accounts function
	async function loadBankAccounts() {
		try {
			loading = true;
			error = null;
			accounts = await getBankAccounts();
		} catch (err) {
			error = err.message;
			toast.error($t('bankAccount.loadError'));
		} finally {
			loading = false;
		}
	}

	// Set account as primary
	async function setPrimary(accountId) {
		try {
			primaryLoading = true;
			await setPrimaryBankAccount(accountId);
			
			// Update local state
			accounts = accounts.map(acc => ({
				...acc,
				is_primary: acc.id === accountId
			}));
			
			toast.success($t('bankAccount.primarySet'));
		} catch (err) {
			toast.error($t('bankAccount.primaryError'));
		} finally {
			primaryLoading = false;
		}
	}

	// Delete account
	async function handleDelete() {
		if (!selectedAccount) return;

		try {
			deleteLoading = true;
			await deleteBankAccount(selectedAccount.id);
			
			// Update local state
			accounts = accounts.filter(acc => acc.id !== selectedAccount.id);
			
			toast.success($t('bankAccount.deleteSuccess'));
			showDeleteModal = false;
			selectedAccount = null;
		} catch (err) {
			toast.error($t('bankAccount.deleteError'));
		} finally {
			deleteLoading = false;
		}
	}

	// Show delete confirmation
	function showDeleteConfirm(account) {
		selectedAccount = account;
		showDeleteModal = true;
	}

	// Cancel delete
	function cancelDelete() {
		showDeleteModal = false;
		selectedAccount = null;
	}

	// Get status color
	function getStatusColor(account) {
		if (account.is_verified) return 'green';
		return 'yellow';
	}

	// Get status text
	function getStatusText(account) {
		if (account.is_verified) return $t('bankAccount.verified');
		return $t('bankAccount.pending');
	}
</script>

<svelte:head>
	<title>{$t('bankAccount.list')} - {$t('app.name')}</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
		<div>
			<h1 class="text-2xl font-bold text-gray-900 dark:text-white">
				{$t('bankAccount.list')}
			</h1>
			<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
				{$t('bankAccount.listDescription')}
			</p>
		</div>
		
		<div class="mt-4 sm:mt-0">
			<Button 
				href="/create/bank-account" 
				variant="primary"
				class="w-full sm:w-auto"
			>
				<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
				</svg>
				{$t('bankAccount.add')}
			</Button>
		</div>
	</div>

	<!-- Error Alert -->
	{#if error}
		<Alert type="error" title={$t('error.title')} message={error} dismissible />
	{/if}

	<!-- Loading State -->
	{#if loading}
		<div class="space-y-4">
			{#each Array(3) as _}
				<LoadingSkeleton type="rect" height="120px" />
			{/each}
		</div>
	
	<!-- Empty State -->
	{:else if !hasAccounts}
		<div class="text-center py-12">
			<svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
					d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
			</svg>
			<h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">
				{$t('bankAccount.noAccounts')}
			</h3>
			<p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
				{$t('bankAccount.noAccountsDesc')}
			</p>
			<div class="mt-6">
				<Button href="/create/bank-account" variant="primary">
					{$t('bankAccount.addFirst')}
				</Button>
			</div>
		</div>
	
	<!-- Account List -->
	{:else}
		<div class="grid gap-6 sm:grid-cols-1 lg:grid-cols-2">
			{#each sortedAccounts as account (account.id)}
				<div class="relative rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800 hover:shadow-md transition-shadow">
					<!-- Primary Badge -->
					{#if account.is_primary}
						<div class="absolute top-4 right-4">
							<span class="inline-flex items-center rounded-full bg-primary-100 px-2.5 py-0.5 text-xs font-medium text-primary-800 dark:bg-primary-900 dark:text-primary-200">
								{$t('bankAccount.primary')}
							</span>
						</div>
					{/if}

					<!-- Account Info -->
					<div class="space-y-4">
						<!-- Bank Name & Account Name -->
						<div>
							<h3 class="text-lg font-medium text-gray-900 dark:text-white">
								{account.bank_name}
							</h3>
							<p class="text-sm text-gray-600 dark:text-gray-400">
								{account.bank_account_name}
							</p>
						</div>

						<!-- IBAN -->
						<div>
							<span class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
								{$t('bankAccount.iban')}
							</span>
							<p class="mt-1 font-mono text-sm text-gray-900 dark:text-white">
								{formatIBAN(account.iban_number)}
							</p>
						</div>

						<!-- Account Number (if available) -->
						{#if account.account_number}
							<div>
								<span class="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
									{$t('bankAccount.accountNumber')}
								</span>
								<p class="mt-1 font-mono text-sm text-gray-900 dark:text-white">
									{account.account_number}
								</p>
							</div>
						{/if}

						<!-- Status -->
						<div class="flex items-center space-x-2">
							<div class="flex h-2 w-2 rounded-full bg-{getStatusColor(account)}-400"></div>
							<span class="text-sm text-gray-600 dark:text-gray-400">
								{getStatusText(account)}
							</span>
						</div>

						<!-- Actions -->
						<div class="flex space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
							<!-- Edit Button -->
							<Button 
								href="/bank-accounts/{account.id}/edit" 
								variant="outline" 
								size="compact"
								class="flex-1"
							>
								{$t('common.edit')}
							</Button>

							<!-- Set Primary Button -->
							{#if !account.is_primary}
								<Button 
									onClick={() => setPrimary(account.id)}
									variant="outline" 
									size="compact"
									loading={primaryLoading}
									class="flex-1"
								>
									{$t('bankAccount.setPrimary')}
								</Button>
							{/if}

							<!-- Delete Button -->
							<Button 
								onClick={() => showDeleteConfirm(account)}
								variant="outline"
								size="compact"
								class="text-red-600 hover:text-red-700 hover:border-red-300"
							>
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
										d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
								</svg>
							</Button>
						</div>

						<!-- Additional Info -->
						<div class="text-xs text-gray-500 dark:text-gray-400">
							{$t('bankAccount.addedOn')} {new Date(account.created_at).toLocaleDateString()}
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<!-- Delete Confirmation Modal -->
<Modal 
	show={showDeleteModal} 
	title={$t('bankAccount.deleteConfirm')}
	onClose={cancelDelete}
>
	<div class="space-y-4">
		<p class="text-sm text-gray-600 dark:text-gray-400">
			{$t('bankAccount.deleteWarning')}
		</p>
		
		{#if selectedAccount}
			<div class="rounded-md bg-gray-50 p-4 dark:bg-gray-700">
				<div class="space-y-2">
					<p class="font-medium text-gray-900 dark:text-white">
						{selectedAccount.bank_name}
					</p>
					<p class="text-sm text-gray-600 dark:text-gray-400">
						{selectedAccount.bank_account_name}
					</p>
					<p class="font-mono text-sm text-gray-600 dark:text-gray-400">
						{formatIBAN(selectedAccount.iban_number)}
					</p>
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