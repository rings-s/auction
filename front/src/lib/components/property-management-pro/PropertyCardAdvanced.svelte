<script>
	import { formatCurrency } from '$lib/utils/currency.js';
	import { t } from '$lib/i18n';
	import Button from '$lib/components/ui/Button.svelte';
	import FadeInUp from '$lib/components/animations/FadeInUp.svelte';
	import CountUp from '$lib/components/animations/CountUp.svelte';
	import ProgressRing from '$lib/components/animations/ProgressRing.svelte';
	import Ripple from '$lib/components/animations/Ripple.svelte';

	/** @type {Object} */
	let property = $props();
	/** @type {string} */
	let variant = $props('default'); // 'default', 'compact', 'dashboard', 'featured'
	/** @type {boolean} */
	let showActions = $props(true);
	/** @type {boolean} */
	let loading = $props(false);
	/** @type {number} */
	let index = $props(0);

	let rentalInfo = $derived(property?.rental_info);
	let occupancyStatus = $derived(rentalInfo?.occupancy_rate >= 100 ? 'occupied' : 'available');
	let tenantCount = $derived(rentalInfo?.current_tenant_count || 0);
	let maxTenants = $derived(rentalInfo?.max_tenants || 1);
	let monthlyRent = $derived(rentalInfo?.monthly_rent || 0);
	let annualIncome = $derived(monthlyRent * 12);
	let occupancyRate = $derived(rentalInfo?.occupancy_rate || 0);

	let cardElement = $state();
	let isHovered = $state(false);
	let imageLoaded = $state(false);

	// Event handlers
	let onclick = $props();
	let onview = $props();
	let onedit = $props();
	let onviewTenants = $props();
	let onviewMaintenance = $props();
	let onviewExpenses = $props();

	function handleViewDetails() {
		onview?.({ property });
	}

	function handleEdit() {
		onedit?.({ property });
	}

	function handleViewTenants() {
		onviewTenants?.({ property });
	}

	function handleViewMaintenance() {
		onviewMaintenance?.({ property });
	}

	function handleViewExpenses() {
		onviewExpenses?.({ property });
	}

	function getOccupancyStatusData(status) {
		switch (status) {
			case 'occupied':
				return {
					class: 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-glow-green',
					icon: '✅',
					label: $t('property.occupancy.occupied')
				};
			case 'available':
				return {
					class: 'bg-gradient-to-r from-blue-500 to-cyan-600 text-white shadow-glow',
					icon: '🏠',
					label: $t('property.occupancy.available')
				};
			default:
				return {
					class: 'bg-gradient-to-r from-gray-400 to-gray-500 text-white',
					icon: '❓',
					label: $t('property.occupancy.unknown')
				};
		}
	}

	function getPropertyTypeIcon(type) {
		const iconMap = {
			apartment: '🏠',
			villa: '🏡',
			commercial: '🏢',
			land: '🏞️',
			warehouse: '🏭'
		};
		return iconMap[type] || '🏘️';
	}

	function getROI() {
		if (!property.market_value || property.market_value === 0) return 0;
		const expenses = property.total_expenses || 0;
		const netIncome = annualIncome - expenses;
		return (netIncome / property.market_value) * 100;
	}

	let occupancyData = $derived(getOccupancyStatusData(occupancyStatus));
	let propertyIcon = $derived(getPropertyTypeIcon(property.property_type));
	let roi = $derived(getROI());
	let isFeatured = $derived(variant === 'featured');
	let cardClasses = $derived(`
        property-card-advanced group relative
        ${isFeatured ? 'lg:col-span-2 lg:row-span-2' : ''}
        bg-white rounded-3xl border border-gray-200/50
        hover:border-gray-300/70 hover:shadow-2xl
        transition-all duration-500 ease-out
        transform hover:-translate-y-2 hover:scale-[1.02]
        will-change-transform backdrop-blur-sm
        ${isHovered ? 'shadow-2xl border-blue-300/50' : 'shadow-soft'}
    `);
</script>

<FadeInUp delay={index * 100} className="h-full">
	<div
		bind:this={cardElement}
		class={cardClasses}
		on:mouseenter={() => (isHovered = true)}
		on:mouseleave={() => (isHovered = false)}
	>
		<!-- Property Image with Gradient Overlay -->
		<div class="relative h-64 {isFeatured ? 'lg:h-80' : ''} overflow-hidden rounded-t-3xl">
			{#if property.featured_image}
				<img
					src={property.featured_image}
					alt={property.title}
					class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
					class:opacity-0={!imageLoaded}
					class:opacity-100={imageLoaded}
					on:load={() => (imageLoaded = true)}
					loading="lazy"
				/>
			{:else}
				<div
					class="flex h-full w-full items-center justify-center bg-gradient-to-br from-gray-100 via-gray-200 to-gray-300"
				>
					<span class="text-6xl opacity-60">{propertyIcon}</span>
				</div>
			{/if}

			<!-- Gradient Overlay -->
			<div
				class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"
			></div>

			<!-- Floating Status Badges -->
			<div class="absolute top-4 left-4">
				<span
					class="inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-medium backdrop-blur-lg {occupancyData.class}"
				>
					<span>{occupancyData.icon}</span>
					{occupancyData.label}
				</span>
			</div>

			<div class="absolute top-4 right-4">
				<span
					class="inline-flex items-center gap-2 rounded-full bg-white/90 px-3 py-1.5 text-sm font-medium text-gray-700 backdrop-blur-lg"
				>
					<span>{propertyIcon}</span>
					{$t(`property.type.${property.property_type}`)}
				</span>
			</div>

			<!-- ROI Badge (if positive) -->
			{#if roi > 0}
				<div class="absolute right-4 bottom-4">
					<div
						class="shadow-glow-green rounded-full bg-gradient-to-r from-green-500 to-emerald-600 px-3 py-1.5 text-sm font-bold text-white backdrop-blur-lg"
					>
						<CountUp value={roi} decimals={1} suffix="% ROI" />
					</div>
				</div>
			{/if}
		</div>

		<!-- Card Content -->
		<div class="p-6 {isFeatured ? 'lg:p-8' : ''}">
			<!-- Property Title & Address -->
			<div class="mb-6">
				<h3
					class="text-xl {isFeatured
						? 'lg:text-2xl'
						: ''} mb-2 line-clamp-2 font-bold text-gray-900 transition-colors duration-300 group-hover:text-blue-600"
				>
					{property.title}
				</h3>
				<p class="flex items-center gap-2 text-gray-600">
					<span class="text-blue-500">📍</span>
					{property.address}
				</p>
			</div>

			<!-- Key Metrics Grid -->
			{#if rentalInfo}
				<div class="grid grid-cols-2 {isFeatured ? 'lg:grid-cols-4' : ''} mb-6 gap-4">
					<!-- Monthly Rent -->
					<div
						class="rounded-2xl border border-green-100 bg-gradient-to-br from-green-50 to-emerald-50 p-4"
					>
						<div class="mb-1 flex items-center gap-2">
							<span class="text-lg text-green-600">💰</span>
							<p class="text-xs font-medium text-green-700">{$t('rental.monthlyRent')}</p>
						</div>
						<p class="text-lg font-bold text-green-800">
							<CountUp value={monthlyRent} format="currency" />
						</p>
					</div>

					<!-- Occupancy with Progress Ring -->
					<div
						class="rounded-2xl border border-blue-100 bg-gradient-to-br from-blue-50 to-cyan-50 p-4"
					>
						<div class="flex items-center justify-between">
							<div>
								<div class="mb-1 flex items-center gap-2">
									<span class="text-lg text-blue-600">📊</span>
									<p class="text-xs font-medium text-blue-700">{$t('rental.occupancy')}</p>
								</div>
								<p class="text-sm font-bold text-blue-800">
									{tenantCount}/{maxTenants}
								</p>
							</div>
							<ProgressRing
								progress={occupancyRate}
								size={40}
								strokeWidth={4}
								color="#3b82f6"
								showText={false}
							/>
						</div>
					</div>

					<!-- Annual Income -->
					<div
						class="rounded-2xl border border-purple-100 bg-gradient-to-br from-purple-50 to-violet-50 p-4"
					>
						<div class="mb-1 flex items-center gap-2">
							<span class="text-lg text-purple-600">📈</span>
							<p class="text-xs font-medium text-purple-700">{$t('rental.annualIncome')}</p>
						</div>
						<p class="text-lg font-bold text-purple-800">
							<CountUp value={annualIncome} format="compact" />
						</p>
					</div>

					<!-- Property Stats -->
					<div
						class="rounded-2xl border border-orange-100 bg-gradient-to-br from-orange-50 to-amber-50 p-4"
					>
						<div class="mb-1 flex items-center gap-2">
							<span class="text-lg text-orange-600">🏠</span>
							<p class="text-xs font-medium text-orange-700">{$t('property.details')}</p>
						</div>
						<div class="space-y-1 text-xs text-orange-800">
							{#if property.rooms?.length}
								<div>{property.rooms.length} {$t('property.rooms')}</div>
							{/if}
							{#if property.area}
								<div>{property.area} {$t('property.sqm')}</div>
							{/if}
						</div>
					</div>
				</div>
			{/if}

			<!-- Quick Actions Bar -->
			{#if showActions}
				<div class="flex items-center gap-2 border-t border-gray-100 pt-4">
					<Ripple className="flex-1" on:click={handleViewDetails}>
						<Button
							variant="primary"
							size="sm"
							className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 shadow-lg"
							{loading}
						>
							<span class="flex items-center gap-2">
								<span>👁️</span>
								{$t('common.viewDetails')}
							</span>
						</Button>
					</Ripple>

					<Ripple on:click={handleEdit}>
						<Button variant="outline" size="sm" className="hover:bg-gray-50 border-gray-200">
							✏️
						</Button>
					</Ripple>

					{#if rentalInfo}
						<Ripple on:click={handleViewTenants}>
							<Button
								variant="ghost"
								size="sm"
								className="text-gray-600 hover:text-blue-600 hover:bg-blue-50"
							>
								👥
							</Button>
						</Ripple>

						<Ripple on:click={handleViewMaintenance}>
							<Button
								variant="ghost"
								size="sm"
								className="text-gray-600 hover:text-orange-600 hover:bg-orange-50"
							>
								🔧
							</Button>
						</Ripple>

						<Ripple on:click={handleViewExpenses}>
							<Button
								variant="ghost"
								size="sm"
								className="text-gray-600 hover:text-green-600 hover:bg-green-50"
							>
								💰
							</Button>
						</Ripple>
					{/if}
				</div>
			{/if}
		</div>

		<!-- Hover Overlay Effect -->
		<div
			class="pointer-events-none absolute inset-0 rounded-3xl bg-gradient-to-t from-blue-500/5 to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100"
		></div>
	</div>
</FadeInUp>

<style>
	.property-card-advanced {
		isolation: isolate;
	}

	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	/* Enhanced hover animations */
	@media (hover: hover) {
		.property-card-advanced:hover {
			animation: cardHover 0.3s ease-out forwards;
		}
	}

	/* Reduced motion support */
	@media (prefers-reduced-motion: reduce) {
		.property-card-advanced,
		.property-card-advanced * {
			animation-duration: 0.01ms !important;
			animation-iteration-count: 1 !important;
			transition-duration: 0.01ms !important;
		}
	}
</style>
