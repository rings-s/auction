<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import { userStore } from '$lib/stores/user.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import AdvancedAnalyticsDashboard from '$lib/components/analytics/AdvancedAnalyticsDashboard.svelte';
	import { fade } from 'svelte/transition';

	// State
	let selectedPeriod = 'month';
	let selectedProperty = 'all';

	$: user = $userStore;
	$: hasAccess =
		(user && ['owner', 'appraiser', 'data_entry'].includes(user.role)) || user?.is_superuser;

	onMount(() => {
		if (!hasAccess) {
			goto('/dashboard');
			return;
		}
	});
</script>

<svelte:head>
	<title>{$t('analytics.title')} | {$t('app.name')}</title>
	<meta name="description" content={$t('analytics.description')} />
</svelte:head>

{#if !hasAccess}
	<div class="flex min-h-screen items-center justify-center">
		<Alert type="error" message={$t('errors.accessDenied')} />
	</div>
{:else}
	<div class="container mx-auto space-y-8 px-4 py-8">
		<!-- Header -->
		<div
			class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
			in:fade={{ duration: 400 }}
		>
			<div>
				<h1 class="text-3xl font-bold tracking-tight text-gray-800 dark:text-gray-100">
					{$t('analytics.propertyAnalytics')}
				</h1>
				<p class="mt-2 text-gray-600 dark:text-gray-400">
					{$t('analytics.subtitle')}
				</p>
			</div>

			<div class="flex flex-wrap gap-4">
				<select
					bind:value={selectedPeriod}
					class="rounded-xl border border-gray-300 bg-white px-4 py-2 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
				>
					<option value="week">{$t('analytics.thisWeek')}</option>
					<option value="month">{$t('analytics.thisMonth')}</option>
					<option value="quarter">{$t('analytics.thisQuarter')}</option>
					<option value="year">{$t('analytics.thisYear')}</option>
				</select>

				<Button variant="outline" on:click={() => goto('/property-management/reports')}>
					<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
						/>
					</svg>
					{$t('analytics.generateReport')}
				</Button>
			</div>
		</div>

		<!-- Advanced Analytics Dashboard -->
		<AdvancedAnalyticsDashboard bind:selectedPeriod bind:selectedProperty />
	</div>
{/if}
