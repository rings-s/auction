<!-- src/lib/components/property/PropertyCard.svelte -->
<script>
	import { t, language } from '$lib/i18n';
	import { formatCurrency } from '$lib/utils/formatters';  // Or wherever this function is defined
	// تصدير المتغيرات التي ستستقبلها البطاقة
	export let property = {
		id: '',
		property_number: '',
		title: '',
		status: 'active',
		status_display: '',
		address: '',
		city: '',
		district: '',
		area: 0,
		bedrooms: 0,
		bathrooms: 0,
		property_type: '',
		property_type_display: '',
		estimated_value: 0,
		main_image_url: '',
		is_featured: false,
		is_verified: false,
		has_auction: false
	};

	// دالة مساعدة لاستخراج الخصائص الرئيسية للعقار كمصفوفة
	function getPropertyFeatures() {
		const features = [];

		if (property.bedrooms) {
			features.push({
				icon: 'bed',
				value: property.bedrooms,
				label: $t('properties.bedrooms')
			});
		}

		if (property.bathrooms) {
			features.push({
				icon: 'bath',
				value: property.bathrooms,
				label: $t('properties.bathrooms')
			});
		}

		features.push({
			icon: 'area',
			value: property.area,
			label: $t('properties.property_area'),
			suffix: 'm²'
		});

		return features;
	}

	// لون حالة العقار
	function getStatusColor(status) {
		const colors = {
			active: 'bg-status-success',
			pending_approval: 'bg-status-warning',
			under_contract: 'bg-status-info',
			sold: 'bg-cosmos-text-dim',
			inactive: 'bg-status-error',
			rejected: 'bg-status-error'
		};

		return colors[status] || 'bg-cosmos-text-dim';
	}

	// صورة افتراضية إذا لم تكن هناك صورة
	const fallbackImage = '/images/placeholders/property-placeholder.jpg';

	// استخراج الخصائص
	$: features = getPropertyFeatures();
</script>

<a
	href={`/properties/${property.id}`}
	class="group relative w-full overflow-hidden rounded-xl bg-cosmos-bg-light bg-opacity-30 backdrop-blur-sm transition-transform duration-300 hover:-translate-y-1 hover:shadow-glow {property.is_featured
		? 'ring-2 ring-primary ring-opacity-60'
		: ''}"
>
	<!-- صورة العقار -->
	<div class="relative aspect-[4/3] w-full overflow-hidden rounded-t-xl">
		<img
			src={property.main_image_url || fallbackImage}
			alt={property.title}
			class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
			loading="lazy"
		/>

		<!-- شارة نوع العقار -->
		<div class="absolute top-3 {$language === 'ar' ? 'right-3' : 'left-3'} z-above">
			<span
				class="rounded-full bg-property-{property.property_type} bg-opacity-80 px-3 py-1 text-xs text-white backdrop-blur-sm"
			>
				{property.property_type_display || $t(`properties.types.${property.property_type}`)}
			</span>
		</div>

		<!-- الشارات الأخرى -->
		<div class="absolute top-3 {$language === 'ar' ? 'left-3' : 'right-3'} z-above flex space-x-1">
			{#if property.is_featured}
				<span class="rounded-full bg-[#FFD700] px-3 py-1 text-xs text-cosmos-bg-dark">
					{$t('general.featured')}
				</span>
			{/if}

			{#if property.is_verified}
				<span class="rounded-full bg-status-success bg-opacity-80 px-3 py-1 text-xs text-white">
					{$t('properties.verified')}
				</span>
			{/if}
		</div>

		<!-- حالة العقار -->
		<div
			class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-cosmos-bg-dark to-transparent p-4"
		>
			<div class="flex items-center justify-between">
				<span
					class={`rounded-full px-3 py-1 text-xs text-white ${getStatusColor(property.status)}`}
				>
					{property.status_display || $t(`properties.status.${property.status}`)}
				</span>

				{#if property.has_auction}
					<span
						class="rounded-full bg-primary bg-opacity-50 px-3 py-1 text-xs text-white backdrop-blur-sm"
					>
						{$t('properties.has_auction')}
					</span>
				{/if}
			</div>
		</div>
	</div>

	<!-- معلومات العقار -->
	<div class="p-4">
		<h3 class="mb-2 text-lg font-bold text-cosmos-text group-hover:text-primary-light">
			{property.title}
		</h3>

		<p class="mb-3 flex items-center text-sm text-cosmos-text-muted">
			<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
				/>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
				/>
			</svg>
			{property.district}, {property.city}
		</p>

		<!-- خصائص العقار -->
		<div class="mb-4 flex justify-between">
			{#each features as feature}
				<div class="flex flex-col items-center">
					<div
						class="mb-1 flex h-8 w-8 items-center justify-center rounded-full bg-primary bg-opacity-10"
					>
						{#if feature.icon === 'bed'}
							<svg
								class="h-4 w-4 text-primary"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M3 12h18M3 6h18M3 18h18"
								/>
							</svg>
						{:else if feature.icon === 'bath'}
							<svg
								class="h-4 w-4 text-primary"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
								/>
							</svg>
						{:else if feature.icon === 'area'}
							<svg
								class="h-4 w-4 text-primary"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z"
								/>
							</svg>
						{/if}
					</div>
					<p class="text-center text-sm font-medium text-cosmos-text">
						{feature.value}{feature.suffix || ''}
					</p>
					<p class="text-center text-xs text-cosmos-text-dim">
						{feature.label}
					</p>
				</div>
			{/each}
		</div>

		<!-- سعر العقار -->
		<div class="flex items-center justify-between">
			<p class="text-lg font-bold text-primary">
				{formatCurrency(property.estimated_value)}
			</p>

			<span
				class="rounded-full bg-primary bg-opacity-10 px-4 py-2 text-sm font-medium text-primary transition group-hover:bg-primary group-hover:text-white"
			>
				{$t('general.view')}
			</span>
		</div>
	</div>
</a>
