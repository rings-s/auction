<!-- src/routes/dashboard/analytics/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { t } from '$lib/i18n';
	import AnalyticsDashboard from '$lib/components/analytics/AnalyticsDashboard.svelte';
	import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';

	// Breadcrumb items
	let breadcrumbItems = [
		{ label: $t('nav.home'), href: '/' },
		{ label: $t('nav.dashboard'), href: '/dashboard' },
		{ label: $t('analytics.analytics'), href: '/dashboard/analytics', active: true }
	];
</script>

<svelte:head>
	<title>{$t('analytics.dashboard')} - {$t('app.name')}</title>
	<meta name="description" content={$t('analytics.dashboardDescription')} />
</svelte:head>

<div class="space-y-6 p-6">
	<!-- Breadcrumb -->
	<Breadcrumb items={breadcrumbItems} />

	<!-- Analytics Dashboard -->
	<AnalyticsDashboard />
</div>
