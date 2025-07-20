<!-- src/lib/components/dashboard/QuickActions.svelte -->
<script>
	import { t } from '$lib/i18n';
	import { user } from '$lib/stores/user';
	import { canAccessAdvancedFeatures } from '$lib/stores/dashboard';
	import Button from '$lib/components/ui/Button.svelte';

	const propertyIcon = `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
    </svg>`;

	const auctionIcon = `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>`;

	const messageIcon = `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>`;

	const searchIcon = `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>`;

	// Property Management Icons
	const paymentIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
		<path d="M4 4a2 2 0 00-2 2v1h16V6a2 2 0 00-2-2H4z"/>
		<path fill-rule="evenodd" d="M18 9H2v5a2 2 0 002 2h12a2 2 0 002-2V9zM4 13a1 1 0 011-1h1a1 1 0 110 2H5a1 1 0 01-1-1zm5-1a1 1 0 100 2h1a1 1 0 100-2H9z" clip-rule="evenodd"/>
	</svg>`;

	const workerIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
		<path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z"/>
	</svg>`;

	const bankIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
		<path d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z"/>
	</svg>`;

	const analyticsIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
		<path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"/>
	</svg>`;
</script>

<div class="rounded-lg border border-gray-200 bg-white p-4">
	<h3 class="mb-4 text-sm font-medium text-gray-900">{$t('dashboard.quickActions')}</h3>

	<div class="grid grid-cols-2 gap-3">
		<!-- Browse Properties -->
		<Button
			variant="outline"
			size="compact"
			href="/properties"
			iconLeft={searchIcon}
			class="justify-start text-left"
		>
			{$t('dashboard.browseProperties')}
		</Button>

		<!-- View Auctions -->
		<Button
			variant="outline"
			size="compact"
			href="/auctions"
			iconLeft={auctionIcon}
			class="justify-start text-left"
		>
			{$t('dashboard.viewAuctions')}
		</Button>

		<!-- Messages -->
		<Button
			variant="outline"
			size="compact"
			href="/messages"
			iconLeft={messageIcon}
			class="justify-start text-left"
		>
			{$t('nav.messages')}
		</Button>

		{#if $canAccessAdvancedFeatures}
			<!-- Add Property (for owners/appraisers) -->
			<Button
				variant="primary"
				size="compact"
				href="/properties/create"
				iconLeft={propertyIcon}
				class="justify-start text-left"
			>
				{$t('dashboard.addProperty')}
			</Button>
		{/if}
	</div>

	{#if $canAccessAdvancedFeatures}
		<div class="mt-4 border-t border-gray-200 pt-4">
			<div class="grid grid-cols-1 gap-2">
				<Button
					variant="secondary"
					size="compact"
					href="/auctions/create"
					iconLeft={auctionIcon}
					fullWidth
					class="justify-center"
				>
					{$t('dashboard.createAuction')}
				</Button>
			</div>
		</div>

		<!-- Property Management Section -->
		<div class="mt-4 border-t border-gray-200 pt-4">
			<h4 class="mb-3 text-xs font-semibold text-gray-600 uppercase tracking-wider">
				{$t('dashboard.propertyManagement')}
			</h4>
			<div class="grid grid-cols-2 gap-2">
				<Button
					variant="outline"
					size="compact"
					href="/dashboard/payments"
					iconLeft={paymentIcon}
					class="justify-start text-left"
				>
					{$t('payment.payments')}
				</Button>

				<Button
					variant="outline"
					size="compact"
					href="/dashboard/workers"
					iconLeft={workerIcon}
					class="justify-start text-left"
				>
					{$t('worker.workers')}
				</Button>

				<Button
					variant="outline"
					size="compact"
					href="/dashboard/bank-accounts"
					iconLeft={bankIcon}
					class="justify-start text-left"
				>
					{$t('bankAccount.accounts')}
				</Button>

				<Button
					variant="outline"
					size="compact"
					href="/dashboard/analytics"
					iconLeft={analyticsIcon}
					class="justify-start text-left"
				>
					{$t('analytics.analytics')}
				</Button>
			</div>
		</div>
	{/if}
</div>
