<!-- src/routes/create/bank-account/+page.svelte -->
<script>
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import { toast } from '$lib/stores/toastStore.svelte.js';
	import { createBankAccount } from '$lib/api/bankAccount';
	import BankAccountForm from '$lib/components/property-management/bank-accounts/BankAccountForm.svelte';
	import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';

	// Breadcrumb items
	let breadcrumbItems = [
		{ label: $t('nav.home'), href: '/' },
		{ label: $t('nav.dashboard'), href: '/dashboard' },
		{ label: $t('bankAccount.accounts'), href: '/dashboard/bank-accounts' },
		{ label: $t('bankAccount.add'), href: '/create/bank-account', active: true }
	];

	// Handle form submission
	async function handleSubmit(event) {
		try {
			const bankAccount = await createBankAccount(event.detail);
			toast.success($t('bankAccount.createSuccess'));
			goto('/dashboard/bank-accounts');
		} catch (error) {
			toast.error($t('bankAccount.createError'));
		}
	}

	// Handle form cancel
	function handleCancel() {
		goto('/dashboard/bank-accounts');
	}
</script>

<svelte:head>
	<title>{$t('bankAccount.add')} - {$t('app.name')}</title>
	<meta name="description" content={$t('bankAccount.addDescription')} />
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<div class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
		<div class="space-y-6">
			<!-- Breadcrumb -->
			<Breadcrumb items={breadcrumbItems} />
			
			<!-- Page Header -->
			<div>
				<h1 class="text-2xl font-bold text-gray-900 dark:text-white">
					{$t('bankAccount.add')}
				</h1>
				<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
					{$t('bankAccount.addDescription')}
				</p>
			</div>

			<!-- Bank Account Form -->
			<BankAccountForm 
				on:submit={handleSubmit}
				on:cancel={handleCancel}
			/>
		</div>
	</div>
</div>