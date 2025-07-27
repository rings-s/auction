<!-- src/lib/components/PropertyCard.svelte -->
<script>
	import { t, locale } from '$lib/i18n'; // Fixed import path

	let { property = {} } = $props();

	// Computed value for RTL mode using $derived
	let isRTL = $derived($locale === 'ar');

	// Format currency based on locale
	const formatCurrency = (value) => {
		if (!value) return '';

		if ($locale === 'ar') {
			return new Intl.NumberFormat('ar-SA', {
				style: 'currency',
				currency: 'SAR',
				minimumFractionDigits: 0,
				maximumFractionDigits: 0
			}).format(value);
		}

		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			minimumFractionDigits: 0,
			maximumFractionDigits: 0
		}).format(value);
	};

	// Format date based on locale
	const formatDate = (dateString) => {
		if (!dateString) return '';

		const date = new Date(dateString);
		return date.toLocaleDateString($locale === 'ar' ? 'ar-SA' : 'en-US');
	};

	// Enhanced status class with gradients and animations
	const getStatusClass = (status) => {
		const classes = {
			available:
				'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-lg shadow-green-500/30 animate-pulse-soft',
			under_contract:
				'bg-gradient-to-r from-yellow-500 to-orange-600 text-white shadow-lg shadow-yellow-500/30',
			sold: 'bg-gradient-to-r from-red-500 to-pink-600 text-white shadow-lg shadow-red-500/30',
			auction:
				'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/30 animate-pulse-soft'
		};
		return classes[status] || classes.available;
	};

	// Get property type gradient class
	const getPropertyTypeClass = (propertyType) => {
		const typeClasses = {
			residential:
				'bg-gradient-to-r from-blue-100 to-indigo-200 text-blue-800 border border-blue-200',
			commercial:
				'bg-gradient-to-r from-purple-100 to-pink-200 text-purple-800 border border-purple-200',
			land: 'bg-gradient-to-r from-green-100 to-emerald-200 text-green-800 border border-green-200',
			industrial:
				'bg-gradient-to-r from-gray-100 to-slate-200 text-gray-800 border border-gray-200',
			mixed_use:
				'bg-gradient-to-r from-yellow-100 to-orange-200 text-yellow-800 border border-yellow-200'
		};
		return (
			typeClasses[propertyType?.toLowerCase()] ||
			'bg-gradient-to-r from-gray-100 to-slate-200 text-gray-800 border border-gray-200'
		);
	};

	// Helper function to get image URL from any property data format
	function getImageUrl(property) {
		if (!property) return '/images/property-placeholder.jpg';

		// Check main_image property
		if (property.main_image) {
			// Could be direct URL or nested object
			if (typeof property.main_image === 'string') {
				return property.main_image;
			}

			// Check for url property first
			if (property.main_image.url) {
				return property.main_image.url;
			}

			// Then check for file property
			if (property.main_image.file) {
				return property.main_image.file;
			}
		}

		// Try media array (first item that's an image)
		if (property.media && property.media.length > 0) {
			const firstImage = property.media.find(
				(m) => m.media_type === 'image' || (m.url && typeof m.url === 'string')
			);

			if (firstImage) {
				return firstImage.url || firstImage.file || '/images/property-placeholder.jpg';
			}
		}

		// Default placeholder
		return '/images/property-placeholder.jpg';
	}

	// Get translated status text
	function getStatusText(status) {
		if (!status) return $t('property.statusTypes.available');

		const statusKey = `property.statusTypes.${status}`;
		const translated = $t(statusKey);

		// If translation not found, return the original status or default
		return translated !== statusKey ? translated : $t('property.statusTypes.available');
	}

	// Get translated property type
	function getPropertyTypeText(propertyType) {
		if (!propertyType) return '';

		// If it's an object with name property
		if (typeof propertyType === 'object' && propertyType.name) {
			return propertyType.name;
		}

		// If it's a string, try to translate it
		const typeKey = `nav.propertyTypes.${propertyType}`;
		const translated = $t(typeKey);

		return translated !== typeKey ? translated : propertyType;
	}
</script>

<a
	href={`/properties/${property.slug || property.id}`}
	class="group block h-full transform transition-all duration-500 hover:-translate-y-2 hover:scale-[1.03] hover:shadow-2xl hover:shadow-blue-500/10"
>
	<div
		class="relative flex h-full flex-col overflow-hidden rounded-2xl border border-neutral-200 bg-white shadow-lg backdrop-blur-sm transition-all duration-500 hover:border-blue-300 hover:shadow-2xl dark:border-neutral-700 dark:bg-gray-800 dark:hover:border-blue-500"
		dir={isRTL ? 'rtl' : 'ltr'}
	>
		<!-- Gradient overlay for enhanced visual appeal -->
		<div
			class="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-br from-blue-50/30 via-transparent to-purple-50/30 opacity-0 transition-opacity duration-500 group-hover:opacity-100"
		></div>
		<!-- Enhanced Image Section with gradient overlay -->
		<div class="relative h-56 overflow-hidden">
			<img
				src={getImageUrl(property)}
				alt={property.title || $t('property.title')}
				class="h-full w-full object-cover transition-all duration-700 group-hover:scale-110 group-hover:brightness-110"
				loading="lazy"
			/>
			<!-- Enhanced gradient overlay -->
			<div
				class="absolute inset-0 bg-gradient-to-br from-black/20 via-transparent to-black/40 transition-all duration-500 group-hover:from-black/10 group-hover:to-black/30"
			></div>

			<!-- Enhanced Status Badge -->
			<div class="absolute top-0 {isRTL ? 'left-0' : 'right-0'} z-10 m-3">
				<span
					class={`inline-flex transform items-center rounded-full px-3 py-1.5 text-xs font-bold tracking-wider uppercase backdrop-blur-sm transition-all duration-300 hover:scale-105 ${getStatusClass(property.status)}`}
				>
					{getStatusText(property.status)}
				</span>
			</div>

			<!-- Enhanced Featured Badge with sparkle effect -->
			{#if property.is_featured}
				<div class="absolute top-0 {isRTL ? 'right-0' : 'left-0'} z-10 m-3">
					<span
						class="inline-flex transform animate-pulse items-center rounded-full bg-gradient-to-r from-amber-400 to-yellow-500 px-3 py-1.5 text-xs font-bold text-white shadow-lg shadow-amber-500/30 backdrop-blur-sm transition-all duration-300 hover:scale-105"
					>
						<svg class="mr-1 h-3 w-3 animate-spin" fill="currentColor" viewBox="0 0 20 20">
							<path
								d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
							/>
						</svg>
						{$t('property.featured')}
					</span>
				</div>
			{/if}

			<!-- Enhanced Title Overlay with better gradients -->
			<div
				class="absolute right-0 bottom-0 left-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent p-4 transition-all duration-300 group-hover:from-black/90 group-hover:via-black/50"
			>
				<h3
					class="mb-1 transform truncate text-lg font-bold text-white transition-all duration-300 group-hover:translate-x-1"
					title={property.title}
				>
					{property.title || $t('property.title')}
				</h3>
				<p class="flex items-center text-sm text-gray-200">
					<svg class="mr-1 h-3 w-3 opacity-70" fill="currentColor" viewBox="0 0 20 20">
						<path
							fill-rule="evenodd"
							d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z"
							clip-rule="evenodd"
						/>
					</svg>
					{#if property.location?.city || property.city}
						{property.location?.city ||
							property.city}{#if property.location?.state || property.state}, {property.location
								?.state || property.state}{/if}
					{:else}
						{$t('property.noLocationData')}
					{/if}
				</p>
			</div>
		</div>

		<!-- Enhanced Details Section -->
		<div class="relative z-10 flex-grow p-5">
			<!-- Enhanced Price and Type -->
			<div class="mb-4 flex items-center justify-between">
				<span
					class={`inline-block truncate rounded-full px-3 py-1.5 text-xs font-bold tracking-wider uppercase transition-all duration-300 hover:scale-105 ${getPropertyTypeClass(property.property_type || property.property_type_display)}`}
				>
					{getPropertyTypeText(property.property_type || property.property_type_display)}
				</span>
				<span
					class="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-2xl font-bold text-transparent transition-all duration-500 group-hover:from-purple-600 group-hover:to-pink-600"
				>
					{formatCurrency(property.market_value)}
				</span>
			</div>

			<!-- Description -->
			{#if property.description}
				<p class="mb-3 line-clamp-2 text-sm text-gray-600 dark:text-gray-300">
					{property.description}
				</p>
			{/if}

			<!-- Enhanced Property Stats with gradient backgrounds -->
			<div class="grid grid-cols-2 gap-3">
				<div
					class="flex items-center rounded-lg border border-blue-100 bg-gradient-to-r from-blue-50 to-indigo-50 p-2 transition-all duration-300 hover:from-blue-100 hover:to-indigo-100 dark:border-blue-800 dark:from-blue-900/20 dark:to-indigo-900/20"
				>
					<div
						class="rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 p-1.5 {isRTL
							? 'ml-2'
							: 'mr-2'}"
					>
						<svg class="h-3 w-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5v-4m0 4h-4m4 0l-5-5"
							/>
						</svg>
					</div>
					<div>
						<div class="text-sm font-bold text-blue-700 dark:text-blue-300">
							{property.size_sqm || 0}
						</div>
						<div class="text-xs text-blue-600 dark:text-blue-400">{$t('property.sqm')}</div>
					</div>
				</div>
				<div
					class="flex items-center rounded-lg border border-purple-100 bg-gradient-to-r from-purple-50 to-pink-50 p-2 transition-all duration-300 hover:from-purple-100 hover:to-pink-100 dark:border-purple-800 dark:from-purple-900/20 dark:to-pink-900/20"
				>
					<div
						class="rounded-full bg-gradient-to-r from-purple-500 to-pink-500 p-1.5 {isRTL
							? 'ml-2'
							: 'mr-2'}"
					>
						<svg class="h-3 w-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
							/>
						</svg>
					</div>
					<div>
						<div class="text-sm font-bold text-purple-700 dark:text-purple-300">
							{property.rooms?.length || 0}
						</div>
						<div class="text-xs text-purple-600 dark:text-purple-400">{$t('property.rooms')}</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Enhanced Footer Section with gradient -->
		<div
			class="relative z-10 border-t border-gray-200 bg-gradient-to-r from-gray-50 via-blue-50 to-gray-50 p-4 dark:border-gray-700 dark:from-gray-800 dark:via-blue-900 dark:to-gray-800"
		>
			<div class="flex items-center justify-between">
				<div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
					<div
						class="rounded-full bg-gradient-to-r from-gray-400 to-blue-400 p-1 {isRTL
							? 'ml-2'
							: 'mr-2'}"
					>
						<svg class="h-3 w-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
							/>
						</svg>
					</div>
					<span class="font-medium">{formatDate(property.created_at)}</span>
				</div>
				<span
					class="inline-flex items-center rounded-full bg-gradient-to-r from-blue-500 to-purple-500 px-3 py-1.5 text-sm font-bold text-white transition-all duration-300 group-hover:animate-pulse hover:scale-105 hover:from-purple-500 hover:to-pink-500 hover:shadow-lg"
				>
					{$t('property.viewDetails')}
					<svg
						class="h-4 w-4 {isRTL
							? 'mr-2'
							: 'ml-2'} transition-transform duration-300 group-hover:translate-x-1"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d={isRTL ? 'M15 19l-7-7 7-7' : 'M9 5l7 7-7 7'}
						/>
					</svg>
				</span>
			</div>
		</div>
	</div>
</a>

<style>
	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	/* Enhanced gradient animations */
	@keyframes pulse-soft {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.8;
		}
	}

	.animate-pulse-soft {
		animation: pulse-soft 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}

	/* Gradient border animation */
	@keyframes gradient-border {
		0%,
		100% {
			border-image: linear-gradient(45deg, #3b82f6, #8b5cf6, #ef4444, #3b82f6) 1;
		}
		25% {
			border-image: linear-gradient(45deg, #8b5cf6, #ef4444, #3b82f6, #8b5cf6) 1;
		}
		50% {
			border-image: linear-gradient(45deg, #ef4444, #3b82f6, #8b5cf6, #ef4444) 1;
		}
		75% {
			border-image: linear-gradient(45deg, #3b82f6, #8b5cf6, #ef4444, #3b82f6) 1;
		}
	}

	/* Sparkle animation for featured badge */
	@keyframes sparkle {
		0%,
		100% {
			transform: rotate(0deg) scale(1);
		}
		50% {
			transform: rotate(180deg) scale(1.1);
		}
	}

	/* Hover effects */
	.group:hover .animate-pulse {
		animation-duration: 1s;
	}

	/* Enhanced shadow transitions */
	.group:hover {
		filter: drop-shadow(0 25px 25px rgba(59, 130, 246, 0.15));
	}
</style>
