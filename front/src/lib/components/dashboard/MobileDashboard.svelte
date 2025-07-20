<!-- src/lib/components/dashboard/MobileDashboard.svelte -->
<script>
	import { t } from '$lib/i18n';
	import { dashboardSummary, userPriority } from '$lib/stores/dashboard';
	import StatCard from './StatCard.svelte';
	import Button from '$lib/components/ui/Button.svelte';

	// Icons
	const menuIcon = `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
    </svg>`;

	const notificationIcon = `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5-5-5h5v-5h0z" />
    </svg>`;
</script>

<div class="sticky top-0 z-40 border-b border-gray-200 bg-white shadow-sm">
	<!-- Mobile Header -->
	<div class="px-4 py-3">
		<div class="flex items-center justify-between">
			<h1 class="text-lg font-semibold text-gray-900">
				{$t('dashboard.title')}
			</h1>

			<div class="flex items-center space-x-2">
				{#if $dashboardSummary?.messages > 0}
					<div class="relative">
						<button class="p-2 text-gray-400 hover:text-gray-600">
							{@html notificationIcon}
						</button>
						<div
							class="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500"
						>
							<span class="text-xs font-medium text-white">
								{$dashboardSummary.messages > 9 ? '9+' : $dashboardSummary.messages}
							</span>
						</div>
					</div>
				{/if}

				<button class="p-2 text-gray-400 hover:text-gray-600">
					{@html menuIcon}
				</button>
			</div>
		</div>
	</div>

	<!-- Quick Stats -->
	{#if $dashboardSummary}
		<div class="px-4 pb-4">
			<div class="grid grid-cols-2 gap-3">
				<StatCard
					title={$t('dashboard.properties')}
					value={$dashboardSummary.properties}
					color="primary"
					compact
					href="/dashboard/properties"
				/>

				<StatCard
					title={$t('dashboard.auctions')}
					value={$dashboardSummary.auctions}
					color="success"
					compact
					href="/dashboard/auctions"
				/>

				<StatCard
					title={$t('dashboard.bids')}
					value={$dashboardSummary.bids}
					color="warning"
					compact
					href="/dashboard/bids"
				/>

				<StatCard
					title={$t('nav.messages')}
					value={$dashboardSummary.messages}
					color="info"
					compact
					href="/messages"
				/>
			</div>
		</div>
	{/if}

	<!-- Quick Actions -->
	<div class="px-4 pb-4">
		<div class="flex space-x-2 overflow-x-auto">
			<Button variant="outline" size="compact" href="/properties" class="flex-shrink-0">
				{$t('nav.properties')}
			</Button>

			<Button variant="outline" size="compact" href="/auctions" class="flex-shrink-0">
				{$t('nav.auctions')}
			</Button>

			<Button variant="outline" size="compact" href="/messages" class="flex-shrink-0">
				{$t('nav.messages')}
			</Button>

			{#if $userPriority >= 3}
				<Button variant="primary" size="compact" href="/properties/create" class="flex-shrink-0">
					{$t('dashboard.addProperty')}
				</Button>
			{/if}
		</div>
	</div>
</div>
