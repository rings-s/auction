<!-- Enhanced Modern QuickActions Component -->
<script>
	import { t } from '$lib/i18n';
	import { user } from '$lib/stores/user.svelte.js';
	import { getCanAccessAdvancedFeatures } from '$lib/stores/dashboard.svelte.js';
	import { fade, scale } from 'svelte/transition';

	// Enhanced SVG Icons with modern styling
	const propertyIcon = `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
    </svg>`;

	const auctionIcon = `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>`;

	const messageIcon = `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>`;

	const searchIcon = `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>`;

	// Property Management Icons with enhanced styling
	const paymentIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
		<path d="M4 4a2 2 0 00-2 2v1h16V6a2 2 0 00-2-2H4z"/>
		<path fill-rule="evenodd" d="M18 9H2v5a2 2 0 002 2h12a2 2 0 002-2V9zM4 13a1 1 0 011-1h1a1 1 0 110 2H5a1 1 0 01-1-1zm5-1a1 1 0 100 2h1a1 1 0 100-2H9z" clip-rule="evenodd"/>
	</svg>`;

	const workerIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
		<path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z"/>
	</svg>`;

	const maintenanceIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
		<path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd"/>
	</svg>`;

	const analyticsIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
		<path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"/>
	</svg>`;

	// Enhanced color schemes with gradients
	const actionColorSchemes = {
		outline: {
			base: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700',
			hover:
				'hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-300 dark:hover:border-gray-600 hover:shadow-lg',
			text: 'text-gray-700 dark:text-gray-300',
			iconBg: 'bg-gray-100 dark:bg-gray-700 group-hover:bg-gray-200 dark:group-hover:bg-gray-600',
			iconText:
				'text-gray-600 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-300'
		},
		primary: {
			base: 'bg-gradient-to-r from-indigo-500 to-purple-600',
			hover: 'hover:from-indigo-600 hover:to-purple-700 hover:shadow-xl hover:shadow-indigo-500/25',
			text: 'text-white',
			iconBg: 'bg-white/20',
			iconText: 'text-white'
		},
		secondary: {
			base: 'bg-gradient-to-r from-emerald-500 to-green-600',
			hover:
				'hover:from-emerald-600 hover:to-green-700 hover:shadow-xl hover:shadow-emerald-500/25',
			text: 'text-white',
			iconBg: 'bg-white/20',
			iconText: 'text-white'
		}
	};

	// Quick action data with modern styling
	const quickActions = [
		{
			title: $t('dashboard.browseProperties'),
			href: '/properties',
			icon: searchIcon,
			variant: 'outline',
			priority: 1
		},
		{
			title: $t('dashboard.viewAuctions'),
			href: '/auctions',
			icon: auctionIcon,
			variant: 'outline',
			priority: 1
		},
		{
			title: $t('nav.messages'),
			href: '/messages',
			icon: messageIcon,
			variant: 'outline',
			priority: 2
		}
	];

	const advancedActions = [
		{
			title: $t('dashboard.addProperty'),
			href: '/properties/create',
			icon: propertyIcon,
			variant: 'primary',
			priority: 1
		},
		{
			title: $t('dashboard.createAuction'),
			href: '/auctions/create',
			icon: auctionIcon,
			variant: 'secondary',
			priority: 1
		}
	];

	const managementActions = [
		{
			title: $t('expense.expenses'),
			href: '/property-management/expenses',
			icon: paymentIcon,
			variant: 'outline',
			priority: 2
		},
		{
			title: $t('worker.workers'),
			href: '/property-management/workers',
			icon: workerIcon,
			variant: 'outline',
			priority: 2
		},
		{
			title: $t('maintenance.maintenance'),
			href: '/property-management/maintenance',
			icon: maintenanceIcon,
			variant: 'outline',
			priority: 2
		},
		{
			title: $t('analytics.analytics'),
			href: '/property-management/analytics',
			icon: analyticsIcon,
			variant: 'outline',
			priority: 2
		}
	];
</script>

<!-- Enhanced Modern QuickActions Template -->
<div
	class="relative overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm backdrop-blur-sm dark:border-gray-700 dark:bg-gray-800"
	in:scale={{ duration: 200, delay: 150 }}
>
	<!-- Decorative gradient background -->
	<div
		class="absolute -top-2 -right-2 h-20 w-20 rounded-full bg-gradient-to-br from-indigo-500/10 to-purple-600/10 blur-2xl"
	></div>

	<div class="relative z-10 p-6">
		<!-- Header with modern styling -->
		<div class="mb-6 flex items-center justify-between">
			<div>
				<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
					{$t('dashboard.quickActions')}
				</h3>
				<p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
					{$t('dashboard.quickActionsDesc')}
				</p>
			</div>
			<div
				class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600"
			>
				<svg class="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M13 10V3L4 14h7v7l9-11h-7z"
					/>
				</svg>
			</div>
		</div>

		<!-- Primary Quick Actions Grid -->
		<div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
			{#each quickActions as action}
				<a
					href={action.href}
					class="group relative transform overflow-hidden rounded-lg border border-gray-200 bg-white p-4 transition-all duration-300 hover:scale-[1.02] hover:border-gray-300 hover:shadow-lg dark:border-gray-700 dark:bg-gray-800 dark:hover:border-gray-600"
					in:fade={{ duration: 200, delay: 100 }}
				>
					<!-- Subtle gradient overlay on hover -->
					<div
						class="absolute inset-0 bg-gradient-to-br from-gray-50/50 to-gray-100/50 opacity-0 transition-opacity duration-300 group-hover:opacity-100 dark:from-gray-700/50 dark:to-gray-600/50"
					></div>

					<div class="relative z-10 flex items-center space-x-3">
						<div class="flex-shrink-0">
							<div
								class="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100 transition-colors duration-200 group-hover:bg-gray-200 dark:bg-gray-700 dark:group-hover:bg-gray-600"
							>
								{@html action.icon}
							</div>
						</div>
						<div class="min-w-0 flex-1">
							<span class="block truncate text-sm font-medium text-gray-900 dark:text-white">
								{action.title}
							</span>
						</div>
					</div>
				</a>
			{/each}
		</div>

		{#if getCanAccessAdvancedFeatures()}
			<!-- Advanced Actions Section -->
			<div class="mb-6 border-t border-gray-200 pt-6 dark:border-gray-700">
				<h4 class="mb-4 flex items-center text-sm font-semibold text-gray-700 dark:text-gray-300">
					<svg class="mr-2 h-4 w-4 text-indigo-500" fill="currentColor" viewBox="0 0 20 20">
						<path
							fill-rule="evenodd"
							d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.293l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z"
							clip-rule="evenodd"
						/>
					</svg>
					{$t('dashboard.advancedActions')}
				</h4>

				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
					{#each advancedActions as action}
						<a
							href={action.href}
							class="group relative transform overflow-hidden rounded-lg p-4 shadow-lg transition-all duration-300 hover:scale-[1.02] {actionColorSchemes[
								action.variant
							].base} {actionColorSchemes[action.variant].hover}"
							in:scale={{ duration: 200, delay: 200 }}
						>
							<!-- Enhanced gradient overlay -->
							<div
								class="absolute -top-1 -right-1 h-16 w-16 rounded-full bg-gradient-to-br from-white/10 to-transparent blur-xl"
							></div>

							<div class="relative z-10 flex items-center space-x-4">
								<div class="flex-shrink-0">
									<div
										class="h-12 w-12 rounded-xl {actionColorSchemes[action.variant]
											.iconBg} flex items-center justify-center shadow-lg transition-transform duration-200 group-hover:scale-110"
									>
										<div class={actionColorSchemes[action.variant].iconText}>
											{@html action.icon}
										</div>
									</div>
								</div>
								<div class="min-w-0 flex-1">
									<span
										class="block text-sm font-semibold {actionColorSchemes[action.variant]
											.text} truncate"
									>
										{action.title}
									</span>
									<span
										class="block text-xs {actionColorSchemes[action.variant].text} mt-1 opacity-75"
									>
										{action.variant === 'primary'
											? $t('dashboard.createNewProperty')
											: $t('dashboard.startNewAuction')}
									</span>
								</div>
								<div class="flex-shrink-0">
									<svg
										class="h-5 w-5 {actionColorSchemes[action.variant]
											.text} opacity-50 transition-opacity duration-200 group-hover:opacity-100"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M9 5l7 7-7 7"
										/>
									</svg>
								</div>
							</div>
						</a>
					{/each}
				</div>
			</div>

			<!-- Property Management Section -->
			<div class="border-t border-gray-200 pt-6 dark:border-gray-700">
				<h4 class="mb-4 flex items-center text-sm font-semibold text-gray-700 dark:text-gray-300">
					<svg class="mr-2 h-4 w-4 text-emerald-500" fill="currentColor" viewBox="0 0 20 20">
						<path
							d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"
						/>
					</svg>
					{$t('dashboard.propertyManagement')}
				</h4>

				<div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
					{#each managementActions as action}
						<a
							href={action.href}
							class="group relative overflow-hidden rounded-lg border border-gray-200 bg-white p-3 transition-all duration-300 hover:border-gray-300 hover:bg-gray-50 hover:shadow-md dark:border-gray-700 dark:bg-gray-800 dark:hover:border-gray-600 dark:hover:bg-gray-700"
							in:fade={{ duration: 200, delay: 250 }}
						>
							<div class="text-center">
								<div
									class="mx-auto mb-2 flex h-8 w-8 items-center justify-center rounded-lg bg-gray-100 transition-colors duration-200 group-hover:bg-gray-200 dark:bg-gray-700 dark:group-hover:bg-gray-600"
								>
									{@html action.icon}
								</div>
								<span class="block truncate text-xs font-medium text-gray-900 dark:text-white">
									{action.title}
								</span>
							</div>
						</a>
					{/each}
				</div>
			</div>
		{/if}
	</div>
</div>
