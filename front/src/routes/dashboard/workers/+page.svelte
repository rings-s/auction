<!-- src/routes/dashboard/workers/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/i18n';
	import DashboardLayout from '$lib/components/dashboard/DashboardLayout.svelte';
	import WorkerDashboard from '$lib/components/property-management/workers/WorkerDashboard.svelte';
	import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';

	// Breadcrumb items
	let breadcrumbItems = [
		{ label: $t('nav.home'), href: '/' },
		{ label: $t('nav.dashboard'), href: '/dashboard' },
		{ label: $t('worker.workers'), href: '/dashboard/workers', active: true }
	];
</script>

<svelte:head>
	<title>{$t('worker.dashboard')} - {$t('app.name')}</title>
	<meta name="description" content={$t('worker.dashboardDescription')} />
</svelte:head>

<DashboardLayout>
	<div class="space-y-6">
		<!-- Breadcrumb -->
		<Breadcrumb items={breadcrumbItems} />
		
		<!-- Worker Dashboard -->
		<WorkerDashboard />
	</div>
</DashboardLayout>