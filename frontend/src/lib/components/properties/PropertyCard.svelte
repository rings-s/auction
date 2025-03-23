<!-- src/lib/components/properties/PropertyCard.svelte -->
<script>
	/**
	 * Property Card Component
	 * Displays a property listing with image, details, and key features.
	 */
	import { t, language } from '$lib/i18n';
	import { formatCurrency } from '$lib/utils/formatters';  // Or wherever this function is defined

	import Badge from '$lib/components/ui/Badge.svelte';
	
	// Property data
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
  
	// Default images
	const fallbackImage = '/images/placeholders/property-placeholder.jpg';
  
	// Extract property features for display
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
  
	// Get status color based on property status
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
  
	// Process features for display
	$: features = getPropertyFeatures();
	
	// Determine RTL layout based on language
	$: isRTL = $language === 'ar';
  </script>
  
  <a
	href={`/properties/${property.id}`}
	class="group block w-full overflow-hidden rounded-xl bg-cosmos-bg-light bg-opacity-30 backdrop-blur-sm transition-transform duration-300 hover:-translate-y-1 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-40 {property.is_featured ? 'ring-2 ring-primary ring-opacity-60' : ''}"
	aria-label={property.title}
  >
	<!-- Property Image -->
	<div class="relative aspect-[4/3] w-full overflow-hidden rounded-t-xl">
	  <img
		src={property.main_image_url || fallbackImage}
		alt={property.title}
		class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
		loading="lazy"
	  />
  
	  <!-- Property Type Badge -->
	  <div class="absolute top-3 {isRTL ? 'right-3' : 'left-3'} z-10">
		<Badge 
		  value={property.property_type_display || $t(`properties.types.${property.property_type}`)} 
		  variant={property.property_type === 'apartment' ? 'primary' : 
				  property.property_type === 'villa' ? 'success' : 
				  property.property_type === 'commercial' ? 'warning' : 'info'}
		  size="sm"
		/>
	  </div>
  
	  <!-- Feature Badges -->
	  <div class="absolute top-3 {isRTL ? 'left-3' : 'right-3'} z-10 flex flex-col gap-1">
		{#if property.is_featured}
		  <Badge value={$t('general.featured')} variant="warning" size="sm" />
		{/if}
  
		{#if property.is_verified}
		  <Badge value={$t('properties.verified')} variant="success" size="sm" />
		{/if}
	  </div>
  
	  <!-- Status Overlay -->
	  <div
		class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-cosmos-bg-dark to-transparent p-4"
	  >
		<div class="flex items-center justify-between">
		  <Badge 
			value={property.status_display || $t(`properties.status.${property.status}`)} 
			variant={property.status === 'active' ? 'success' : 
					property.status === 'pending_approval' ? 'warning' : 
					property.status === 'under_contract' ? 'info' : 'error'}
			size="sm"
			filled={true}
		  />
  
		  {#if property.has_auction}
			<Badge value={$t('properties.has_auction')} variant="primary" size="sm" />
		  {/if}
		</div>
	  </div>
	</div>
  
	<!-- Property Details -->
	<div class="p-4">
	  <h3 class="mb-2 text-lg font-bold text-cosmos-text group-hover:text-primary-light transition-colors">
		{property.title}
	  </h3>
  
	  <p class="mb-3 flex items-center text-sm text-cosmos-text-muted" aria-label={$t('properties.property_location')}>
		<svg class="mr-1 h-4 w-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
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
		<span class="truncate">{property.district}, {property.city}</span>
	  </p>
  
	  <!-- Property Features -->
	  <div class="mb-4 flex justify-between">
		{#each features as feature}
		  <div class="flex flex-col items-center" aria-label={`${feature.value}${feature.suffix || ''} ${feature.label}`}>
			<div
			  class="mb-1 flex h-8 w-8 items-center justify-center rounded-full bg-primary bg-opacity-10"
			  aria-hidden="true"
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
  
	  <!-- Price and View Button -->
	  <div class="flex items-center justify-between">
		<p class="text-lg font-bold text-primary" aria-label={$t('properties.property_price')}>
		  {formatCurrency(property.estimated_value)}
		</p>
  
		<span
		  class="rounded-full bg-primary bg-opacity-10 px-4 py-2 text-sm font-medium text-primary transition group-hover:bg-primary group-hover:text-white"
		  aria-hidden="true"
		>
		  {$t('general.view')}
		</span>
	  </div>
	</div>
  </a>