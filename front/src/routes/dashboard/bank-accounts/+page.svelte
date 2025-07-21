<!-- src/routes/dashboard/bank-accounts/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/i18n';
	import BankAccountList from '$lib/components/property-management/bank-accounts/BankAccountList.svelte';
	import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';

	// Breadcrumb items
	let breadcrumbItems = [
		{ label: $t('nav.home'), href: '/' },
		{ label: $t('nav.dashboard'), href: '/dashboard' },
		{ label: $t('bankAccount.accounts'), href: '/dashboard/bank-accounts', active: true }
	];
</script>

<svelte:head>
	<title>{$t('bankAccount.accounts')} - {$t('app.name')}</title>
	<meta name="description" content={$t('bankAccount.listDescription')} />
</svelte:head>

<div class="p-6 space-y-6">
	<!-- Breadcrumb -->
	<Breadcrumb items={breadcrumbItems} />
	
	<!-- Bank Account List -->
	<BankAccountList />
</div>