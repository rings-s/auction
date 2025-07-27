<!-- src/routes/dashboard/payments/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/i18n';
	import PaymentDashboard from '$lib/components/property-management/payments/PaymentDashboard.svelte';
	import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';

	// Breadcrumb items
	let breadcrumbItems = [
		{ label: $t('nav.home'), href: '/' },
		{ label: $t('nav.dashboard'), href: '/dashboard' },
		{ label: $t('payment.payments'), href: '/dashboard/payments', active: true }
	];
</script>

<svelte:head>
	<title>{$t('payment.dashboard')} - {$t('app.name')}</title>
	<meta name="description" content={$t('payment.dashboardDescription')} />
</svelte:head>

<div class="space-y-6 p-6">
	<!-- Breadcrumb -->
	<Breadcrumb items={breadcrumbItems} />

	<!-- Payment Dashboard -->
	<PaymentDashboard />
</div>
