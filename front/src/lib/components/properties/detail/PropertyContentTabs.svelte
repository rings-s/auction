<script>
	import { t } from '$lib/i18n';
	import { tick } from 'svelte';
	import { fade } from 'svelte/transition';
	import Gallery from '$lib/components/ui/Gallery.svelte';
	import PropertyCard from '$lib/components/properties/PropertyCard.svelte';
	import ContactForm from '$lib/components/messages/ContactForm.svelte';
	import PropertyLocationTab from '$lib/components/properties/detail/PropertyLocationTab.svelte';
	import RentalRegistrationForm from '$lib/components/properties/RentalRegistrationForm.svelte';
	import { getFeatureKey, getRoomTypeKey } from '$lib/i18n/mappings';
	import { rentalPropertyAPI } from '$lib/api/propertyManagement.js';
	import { formatCurrency } from '$lib/utils/currency';

	let {
		property,
		activeTab,
		propertyType = 'sale', // 'sale' or 'rental'
		activeImageIndex,
		showFullScreenGallery = false, // External reference only
		filteredMedia,
		images,
		videos,
		documents = [], // External reference only
		otherFiles = [], // External reference only
		isImagesLoading,
		mapElement,
		activeMediaType,
		mediaTabs,
		mainImage,
		onToggleGallery,
		onHandleImageLoad,
		onSetActiveMediaType,
		canManageProperty = false,
		canCreateRental = false,
		canEdit = false
	} = $props();

	// Svelte 5 state for rental registration
	let showRentalForm = $state(false);

	let initializeMapFunction;

	function handleInitializeMap(fn) {
		initializeMapFunction = fn;
	}

	$effect(() => {
		if (
			activeTab === 'location' &&
			property?.location?.latitude &&
			property?.location?.longitude &&
			initializeMapFunction
		) {
			tick().then(() => {
				initializeMapFunction();
			});
		}
	});

	function formatFileSize(bytes) {
		if (!bytes) return '0 Bytes';
		const k = 1024;
		const sizes = ['Bytes', 'KB', 'MB', 'GB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
	}

	function translateRoomType(roomType) {
		if (!roomType) return '';

		const mappedKey = getRoomTypeKey(roomType);
		if (mappedKey) {
			const translationKey = `property.roomTypes.${mappedKey}`;
			const translation = $t(translationKey);
			if (translation !== translationKey) {
				return translation;
			}
		}

		const normalizedType = roomType.toLowerCase().replace(/\s+/g, '');
		const translationKey = `property.roomTypes.${normalizedType}`;
		const translation = $t(translationKey);
		if (translation !== translationKey) {
			return translation;
		}

		return roomType;
	}

	function translateFeatureOrAmenity(item, type) {
		if (!item) return '';

		let translationPrefix = 'property.';
		let itemsKey = '';

		if (type === 'feature') {
			itemsKey = 'featureItems';
		} else if (type === 'amenity') {
			itemsKey = 'amenityItems';
		} else if (type === 'roomFeature') {
			itemsKey = 'roomFeatureItems';
		} else {
			return item;
		}

		const mappedKey = getFeatureKey(item);
		if (mappedKey) {
			const mappedTranslationKey = `${translationPrefix}${itemsKey}.${mappedKey}`;
			const mappedTranslation = $t(mappedTranslationKey);
			if (mappedTranslation !== mappedTranslationKey) {
				return mappedTranslation;
			}
		}

		const normalizedItem = item.toLowerCase().replace(/\s+/g, '');
		const translationKey = `${translationPrefix}${itemsKey}.${normalizedItem}`;
		const translation = $t(translationKey);

		if (translation === translationKey) {
			const variations = [normalizedItem, item.toLowerCase(), item.replace(/\s+/g, '')];

			for (const variation of variations) {
				const variationKey = `property.${type}Items.${variation}`;
				const variationTranslation = $t(variationKey);
				if (variationTranslation !== variationKey) {
					return variationTranslation;
				}
			}

			return item;
		}

		return translation;
	}

	function getMediaTypeIcon(type) {
		switch (type) {
			case 'image':
				return `<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>`;
			case 'video':
				return `<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8v6a1 1 0 01-1 1v6a1 1 0 01-1-1v-6a1 1 0 00-1-1H9a1 1 0 00-1 1v6a1 1 0 001 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1V7a1 1 0 011-1h5m0 0V5a2 2 0 012-2h2a2 2 0 012 2v2m-6 3h6m-6 2h6a2 2 0 012 2v3m0 0h-9"></path></svg>`;
			case 'document':
				return `<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>`;
			default:
				return `<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>`;
		}
	}

	// Handle rental registration
	function openRentalForm() {
		showRentalForm = true;
	}

	function closeRentalForm() {
		showRentalForm = false;
	}

	async function handleRentalSubmit(rentalData) {
		try {
			// Create rental property using the API
			const response = await rentalPropertyAPI.create(rentalData);

			// Update property data to reflect new rental info
			if (response && response.id) {
				// Update the property object with new rental information
				property = {
					...property,
					rental_info: response
				};
			}
		} catch (error) {
			// Re-throw error to be handled by the calling component
			throw error;
		}
	}
</script>

<div class="overflow-hidden rounded-b-xl bg-white shadow-md dark:bg-gray-800">
	<!-- Overview Tab -->
	<div
		id="tab-overview"
		class="bg-white p-8 dark:bg-gray-800"
		style="display: {activeTab === 'overview' ? 'block' : 'none'}"
		transition:fade={{ duration: 200 }}
	>
		<div class="grid grid-cols-1 gap-10 md:grid-cols-3">
			<!-- Main Image and Gallery Preview -->
			<div class="md:col-span-2">
				<div
					class="relative mb-6 overflow-hidden rounded-xl bg-gray-100 shadow-lg dark:bg-gray-800"
					style="height: 400px;"
				>
					{#if isImagesLoading && images.length > 0}
						<div
							class="dark:bg-gray-750 absolute inset-0 flex items-center justify-center bg-gray-100"
						>
							<div class="flex animate-pulse flex-col items-center">
								<div class="mb-2 h-12 w-12 rounded-full bg-gray-300 dark:bg-gray-600"></div>
								<div class="text-gray-500 dark:text-gray-400">{$t('common.loading')}</div>
							</div>
						</div>
					{/if}

					{#if mainImage}
						<img
							src={mainImage?.url}
							alt={mainImage?.name || property.title}
							class="h-full w-full object-cover transition-opacity duration-300 {isImagesLoading
								? 'opacity-0'
								: 'loaded opacity-100'}"
							onload={onHandleImageLoad}
							onerror={(e) => {
								e.currentTarget.src = '/images/placeholder-property.jpg';
								isImagesLoading = false;
							}}
						/>

						<div
							class="pointer-events-none absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-black/60 to-transparent"
						></div>

						<!-- Gallery Overlay Button -->
						<button
							class="absolute right-4 bottom-4 z-10 rounded-full bg-white/90 p-2 shadow-lg transition-colors hover:bg-white dark:bg-gray-800/90 dark:hover:bg-gray-700"
							onclick={onToggleGallery}
							aria-label="View gallery"
						>
							<svg
								class="h-5 w-5 text-gray-700 dark:text-gray-200"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5v-4m0 4h-4m4 0l-5-5"
								/>
							</svg>
						</button>

						<!-- Image Counter -->
						<div
							class="absolute bottom-4 left-4 z-10 flex items-center rounded-md bg-black/70 px-3 py-1.5 text-sm text-white backdrop-blur-sm"
						>
							<svg class="mr-1.5 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
								/>
							</svg>
							{images.length}
							{$t('property.photos')}
						</div>
					{:else if videos.length > 0}
						<div class="flex h-full w-full items-center justify-center bg-black">
							<video
								src={videos[0].url}
								controls
								class="max-h-full max-w-full"
								poster={videos[0].thumbnail}
							>
								<track kind="captions" src="" label={$t('common.captions')} />
								<p>{$t('common.videoNotSupported')}</p>
							</video>
						</div>
					{:else}
						<div class="flex h-full items-center justify-center bg-gray-100 dark:bg-gray-700">
							<svg
								class="h-16 w-16 text-gray-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
								/>
							</svg>
						</div>
					{/if}
				</div>

				<!-- Thumbnail Preview Gallery -->
				{#if images.length > 1}
					<div class="relative mt-4">
						<div class="scrollbar-thin overflow-x-auto py-2">
							<div class="flex gap-2">
								{#each images.slice(0, Math.min(6, images.length)) as image, idx}
									<button
										class={`h-16 w-24 flex-shrink-0 overflow-hidden rounded-md border-2 transition-all ${idx === activeImageIndex ? 'border-primary-500 dark:border-primary-400' : 'border-transparent'}`}
										onclick={() => {
											activeImageIndex = idx;
											onToggleGallery();
										}}
									>
										<img
											src={image.url}
											alt={image.name || `Property image ${idx + 1}`}
											class="h-full w-full object-cover"
											loading="lazy"
										/>
									</button>
								{/each}

								{#if images.length > 6}
									<button
										class="dark:bg-gray-750 group flex h-16 w-24 flex-shrink-0 items-center justify-center overflow-hidden rounded-md border-2 border-transparent bg-gray-100"
										onclick={onToggleGallery}
									>
										<div class="text-center">
											<span
												class="group-hover:text-primary-600 dark:group-hover:text-primary-400 block text-sm font-semibold text-gray-800 dark:text-gray-200"
												>+{images.length - 6}</span
											>
											<span class="text-xs text-gray-500 dark:text-gray-400">More</span>
										</div>
									</button>
								{/if}
							</div>
						</div>
					</div>
				{/if}

				<!-- Description -->
				<div class="mt-10">
					<h2 class="mb-4 flex items-center text-xl font-bold text-gray-900 dark:text-white">
						<svg
							class="text-primary-500 mr-2 h-5 w-5"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						{$t('property.description')}
					</h2>
					<div class="prose dark:prose-invert max-w-none">
						<p class="text-base leading-relaxed text-gray-600 dark:text-gray-300">
							{property.description}
						</p>
					</div>
				</div>

				<!-- Key Features -->
				{#if (property.features && property.features.length > 0) || (property.amenities && property.amenities.length > 0)}
					<div class="mt-10 pb-4">
						<h2 class="mb-4 flex items-center text-xl font-bold text-gray-900 dark:text-white">
							<svg
								class="text-primary-500 mr-2 h-5 w-5"
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
							{$t('property.keyFeatures')}
						</h2>

						<div class="grid grid-cols-1 gap-8 sm:grid-cols-2">
							{#if property.features && property.features.length > 0}
								<div>
									<h3 class="mb-3 text-lg font-semibold text-gray-800 dark:text-gray-200">
										{$t('property.features')}
									</h3>
									<ul class="space-y-2">
										{#each property.features as feature}
											<li class="flex items-center text-gray-600 dark:text-gray-300">
												<svg
													class="text-primary-500 mr-2 h-5 w-5"
													fill="none"
													stroke="currentColor"
													viewBox="0 0 24 24"
												>
													<path
														stroke-linecap="round"
														stroke-linejoin="round"
														stroke-width="2"
														d="M5 13l4 4L19 7"
													/>
												</svg>
												{translateFeatureOrAmenity(feature, 'feature')}
											</li>
										{/each}
									</ul>
								</div>
							{/if}

							{#if property.amenities && property.amenities.length > 0}
								<div>
									<h3 class="mb-3 text-lg font-semibold text-gray-800 dark:text-gray-200">
										{$t('property.amenities')}
									</h3>
									<ul class="space-y-2">
										{#each property.amenities as amenity}
											<li class="flex items-center text-gray-600 dark:text-gray-300">
												<svg
													class="text-secondary-500 mr-2 h-5 w-5"
													fill="none"
													stroke="currentColor"
													viewBox="0 0 24 24"
												>
													<path
														stroke-linecap="round"
														stroke-linejoin="round"
														stroke-width="2"
														d="M5 13l4 4L19 7"
													/>
												</svg>
												{translateFeatureOrAmenity(amenity, 'amenity')}
											</li>
										{/each}
									</ul>
								</div>
							{/if}
						</div>
					</div>
				{/if}
			</div>

			<!-- Sidebar -->
			<div class="md:col-span-1">
				<!-- Property Details Card -->
				<div
					class="dark:bg-gray-750 overflow-hidden rounded-xl border border-gray-100 bg-gray-50 shadow-md dark:border-gray-700"
				>
					<div class="p-5">
						<h2 class="mb-4 flex items-center text-lg font-bold text-gray-900 dark:text-white">
							<svg
								class="text-primary-500 mr-2 h-5 w-5"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
								/>
							</svg>
							{$t('property.propertyDetails')}
						</h2>

						<!-- Details Grid -->
						<div class="space-y-5">
							<div class="grid grid-cols-2 gap-5">
								<!-- Size -->
								<div
									class="flex flex-col items-center rounded-lg border border-gray-100 bg-white p-4 shadow-sm transition-shadow hover:shadow-md dark:border-gray-700 dark:bg-gray-800"
								>
									<svg
										class="text-primary-500 mb-1 h-6 w-6"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
										/>
									</svg>
									<span class="text-sm text-gray-500 dark:text-gray-400">{$t('property.size')}</span
									>
									<span class="text-lg font-bold text-gray-900 dark:text-white"
										>{property.size_sqm} {$t('property.sqm')}</span
									>
								</div>

								<!-- Floors -->
								<div
									class="flex flex-col items-center rounded-lg border border-gray-100 bg-white p-4 shadow-sm transition-shadow hover:shadow-md dark:border-gray-700 dark:bg-gray-800"
								>
									<svg
										class="text-primary-500 mb-1 h-6 w-6"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
										/>
									</svg>
									<span class="text-sm text-gray-500 dark:text-gray-400"
										>{$t('property.floors')}</span
									>
									<span class="text-lg font-bold text-gray-900 dark:text-white"
										>{property.floors || '1'}</span
									>
								</div>

								<!-- Rooms -->
								<div
									class="flex flex-col items-center rounded-lg border border-gray-100 bg-white p-4 shadow-sm transition-shadow hover:shadow-md dark:border-gray-700 dark:bg-gray-800"
								>
									<svg
										class="text-primary-500 mb-1 h-6 w-6"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1V13z"
										/>
									</svg>
									<span class="text-sm text-gray-500 dark:text-gray-400"
										>{$t('property.rooms')}</span
									>
									<span class="text-lg font-bold text-gray-900 dark:text-white"
										>{property.rooms?.length || 0}</span
									>
								</div>

								<!-- Year Built -->
								<div
									class="flex flex-col items-center rounded-lg border border-gray-100 bg-white p-4 shadow-sm transition-shadow hover:shadow-md dark:border-gray-700 dark:bg-gray-800"
								>
									<svg
										class="text-primary-500 mb-1 h-6 w-6"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002 2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
										/>
									</svg>
									<span class="text-sm text-gray-500 dark:text-gray-400"
										>{$t('property.yearBuilt')}</span
									>
									<span class="text-lg font-bold text-gray-900 dark:text-white"
										>{property.year_built || 'N/A'}</span
									>
								</div>
							</div>

							<!-- Deed Number -->
							<div
								class="flex items-center justify-between border-t border-gray-200 py-2 dark:border-gray-700"
							>
								<span class="text-gray-500 dark:text-gray-400">{$t('property.deedNumber')}</span>
								<span class="font-medium text-gray-900 dark:text-white">{property.deed_number}</span
								>
							</div>

							<!-- Financial Info -->
							<div
								class="from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-900/30 mt-4 rounded-lg bg-gradient-to-r p-4"
							>
								<div class="flex items-baseline justify-between">
									<span class="text-gray-600 dark:text-gray-300">{$t('property.marketValue')}</span>
									<span class="text-primary-600 dark:text-primary-400 text-xl font-bold"
										>{formatCurrency(property.market_value)}</span
									>
								</div>

								{#if property.minimum_bid}
									<div class="mt-2 flex items-baseline justify-between">
										<span class="text-gray-600 dark:text-gray-300">{$t('property.minimumBid')}</span
										>
										<span class="text-lg font-semibold text-gray-900 dark:text-white"
											>{formatCurrency(property.minimum_bid)}</span
										>
									</div>
								{/if}
							</div>
						</div>
					</div>
				</div>

				<!-- Contact Owner Card -->
				<div class="mt-8">
					<ContactForm
						{property}
						compact={true}
						onsuccess={(e) => {
							// Handle success
						}}
						onerror={(e) => {
							// Handle error
						}}
					/>
				</div>
			</div>
		</div>
	</div>

	<!-- Rooms Tab -->
	<div
		id="tab-rooms"
		class="p-8"
		style="display: {activeTab === 'rooms' ? 'block' : 'none'}"
		transition:fade={{ duration: 200 }}
	>
		<h2 class="mb-6 flex items-center text-xl font-bold text-gray-900 dark:text-white">
			<svg
				class="text-primary-500 mr-2 h-6 w-6"
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
			{$t('property.rooms')} ({property.rooms?.length || 0})
		</h2>

		{#if property.rooms && property.rooms.length > 0}
			<div class="grid gap-6">
				{#each property.rooms as room, index}
					<div
						class="dark:bg-gray-750 rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md dark:border-gray-600"
					>
						<div class="mb-4 flex flex-col justify-between md:flex-row md:items-start">
							<div class="flex-grow">
								<div class="mb-2 flex items-center">
									<h3 class="mr-3 text-lg font-semibold text-gray-900 dark:text-white">
										{room.name}
									</h3>
									<span
										class="bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200 inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
									>
										{translateRoomType(room.room_type)}
									</span>
								</div>

								{#if room.description}
									<p class="mb-3 text-gray-600 dark:text-gray-300">
										{room.description}
									</p>
								{/if}
							</div>
						</div>

						<!-- Room Details Grid -->
						<div class="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
							{#if room.area_sqm}
								<div class="rounded-lg bg-gray-50 p-3 text-center dark:bg-gray-700">
									<div class="text-lg font-bold text-gray-900 dark:text-white">
										{room.area_sqm}
									</div>
									<div class="text-xs text-gray-500 dark:text-gray-400">
										{$t('property.sqm')}
									</div>
								</div>
							{/if}

							<div class="rounded-lg bg-gray-50 p-3 text-center dark:bg-gray-700">
								<div class="text-lg font-bold text-gray-900 dark:text-white">
									{room.floor || 1}
								</div>
								<div class="text-xs text-gray-500 dark:text-gray-400">
									{$t('property.floor')}
								</div>
							</div>

							{#if room.has_window}
								<div class="rounded-lg bg-blue-50 p-3 text-center dark:bg-blue-900/30">
									<svg
										class="mx-auto mb-1 h-6 w-6 text-blue-500"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M4 4h16v16H4V4zm0 0l16 16M4 20l16-16"
										/>
									</svg>
									<div class="text-xs text-blue-600 dark:text-blue-400">
										{$t('property.hasWindow')}
									</div>
								</div>
							{/if}

							{#if room.has_bathroom}
								<div class="rounded-lg bg-green-50 p-3 text-center dark:bg-green-900/30">
									<svg
										class="mx-auto mb-1 h-6 w-6 text-green-500"
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
									<div class="text-xs text-green-600 dark:text-green-400">
										{$t('property.hasBathroom')}
									</div>
								</div>
							{/if}
						</div>

						<!-- Room Features -->
						{#if room.features && room.features.length > 0}
							<div class="border-t border-gray-200 pt-4 dark:border-gray-600">
								<h4 class="mb-2 text-sm font-medium text-gray-900 dark:text-white">
									{$t('property.features')}
								</h4>
								<div class="flex flex-wrap gap-2">
									{#each room.features as feature}
										<span
											class="bg-secondary-100 text-secondary-800 dark:bg-secondary-900 dark:text-secondary-200 inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
										>
											{translateFeatureOrAmenity(feature, 'roomFeature')}
										</span>
									{/each}
								</div>
							</div>
						{/if}
					</div>
				{/each}
			</div>
		{:else}
			<!-- No Rooms State -->
			<div class="dark:bg-gray-750 rounded-xl bg-gray-50 py-12 text-center">
				<svg
					class="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500"
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
				<h3 class="mt-2 text-base font-medium text-gray-900 dark:text-white">
					{$t('property.noRooms')}
				</h3>
				<p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
					{$t('property.noRoomsInfo')}
				</p>
			</div>
		{/if}
	</div>

	<!-- Location Tab -->
	<div
		id="tab-location"
		style="display: {activeTab === 'location' ? 'block' : 'none'}"
		transition:fade={{ duration: 200 }}
	>
		<PropertyLocationTab {property} bind:mapElement onInitializeMap={handleInitializeMap} />
	</div>

	<!-- Gallery Tab -->
	<div
		id="tab-gallery"
		class="p-6"
		style="display: {activeTab === 'gallery' ? 'block' : 'none'}"
		transition:fade={{ duration: 200 }}
	>
		<h2 class="mb-6 flex items-center text-xl font-bold text-gray-900 dark:text-white">
			<svg
				class="text-primary-500 mr-2 h-6 w-6"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
				/>
			</svg>
			{$t('property.gallery')}
		</h2>

		<!-- Media Type Tabs -->
		<div class="dark:bg-gray-750 mb-6 flex overflow-x-auto rounded-lg bg-gray-50 p-1">
			{#each mediaTabs as tab}
				<button
					class={`flex items-center rounded-md px-4 py-2 text-sm font-medium whitespace-nowrap
            ${
							activeMediaType === tab.id
								? 'text-primary-600 dark:text-primary-400 bg-white shadow-sm dark:bg-gray-800'
								: 'bg-transparent text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200'
						} mx-1 transition-colors duration-200`}
					onclick={() => onSetActiveMediaType(tab.id)}
					disabled={property?.media?.filter((item) => item.media_type === tab.id).length === 0}
					class:opacity-50={property?.media?.filter((item) => item.media_type === tab.id).length ===
						0}
				>
					{@html getMediaTypeIcon(tab.id)}
					<span class="ml-2">{tab.label}</span>
					<span
						class="ml-1.5 rounded-full bg-gray-100 px-1.5 py-0.5 text-xs text-gray-600 dark:bg-gray-700 dark:text-gray-300"
					>
						{property?.media?.filter((item) => item.media_type === tab.id).length || 0}
					</span>
				</button>
			{/each}
		</div>

		{#if filteredMedia.length > 0}
			<div class="grid grid-cols-1 gap-5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
				{#each filteredMedia as mediaItem, index}
					<button
						type="button"
						class="group focus:ring-primary-500 relative cursor-pointer overflow-hidden rounded-lg border border-gray-200 bg-white shadow-md transition-all hover:-translate-y-1 hover:shadow-lg focus:ring-2 focus:ring-offset-2 focus:outline-none dark:border-gray-700 dark:bg-gray-800"
						onclick={() => {
							activeImageIndex = index;
							onToggleGallery();
						}}
						aria-label={`View ${mediaItem.name || 'media item'}`}
					>
						<div class="aspect-w-4 aspect-h-3 relative bg-gray-100 dark:bg-gray-700">
							{#if mediaItem.media_type === 'image'}
								<img
									src={mediaItem.url}
									alt={mediaItem.name || `${property.title} - Image ${index + 1}`}
									class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
									loading="lazy"
								/>
								<div
									class="bg-opacity-0 group-hover:bg-opacity-30 absolute inset-0 bg-black transition-opacity"
								></div>
							{:else if mediaItem.media_type === 'video'}
								<div class="flex h-full w-full items-center justify-center bg-black">
									<svg
										class="h-12 w-12 text-white opacity-80 transition-opacity group-hover:opacity-100"
										fill="currentColor"
										viewBox="0 0 20 20"
									>
										<path
											fill-rule="evenodd"
											d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"
										/>
									</svg>
								</div>
							{:else if mediaItem.media_type === 'document'}
								<div
									class="flex h-full w-full items-center justify-center bg-blue-50 dark:bg-blue-900/20"
								>
									<svg
										class="h-12 w-12 text-blue-400 transition-transform group-hover:scale-110 dark:text-blue-400"
										fill="currentColor"
										viewBox="0 0 20 20"
									>
										<path
											d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm2 3a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
										/>
									</svg>
								</div>
							{:else}
								<div
									class="flex h-full w-full items-center justify-center bg-gray-100 dark:bg-gray-800"
								>
									<svg
										class="h-12 w-12 text-gray-400 transition-colors group-hover:text-gray-500"
										fill="currentColor"
										viewBox="0 0 20 20"
									>
										<path
											fill-rule="evenodd"
											d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm12 12H4V6h12v10z"
											clip-rule="evenodd"
										/>
									</svg>
								</div>
							{/if}

							<!-- View icon overlay -->
							<div
								class="absolute inset-0 flex items-center justify-center opacity-0 transition-opacity duration-300 group-hover:opacity-100"
							>
								<div class="bg-opacity-50 rounded-full bg-black p-3 backdrop-blur-sm">
									<svg
										class="h-6 w-6 text-white"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
										/>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
										/>
									</svg>
								</div>
							</div>
						</div>

						<div class="p-3">
							<h3 class="truncate text-sm font-medium text-gray-900 dark:text-white">
								{mediaItem.name || `${activeMediaType} ${index + 1}`}
							</h3>

							<div class="mt-1 flex items-center justify-between">
								{#if mediaItem.dimensions}
									<span class="text-xs text-gray-500 dark:text-gray-400">
										{mediaItem.dimensions.width}×{mediaItem.dimensions.height}
									</span>
								{/if}

								{#if mediaItem.file_size}
									<span class="text-xs text-gray-500 dark:text-gray-400">
										{formatFileSize(mediaItem.file_size)}
									</span>
								{/if}
							</div>
						</div>
					</button>
				{/each}
			</div>
		{:else}
			<div class="dark:bg-gray-750 rounded-lg bg-gray-50 py-12 text-center">
				<svg
					class="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
					/>
				</svg>
				<h3 class="mt-2 text-base font-medium text-gray-900 dark:text-white">
					{$t('property.noImages')}
				</h3>
				<p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
					{$t('property.noImagesInfo')}
				</p>
			</div>
		{/if}
	</div>

	<!-- Property Management Tab -->
	<div
		id="tab-management"
		class="bg-white p-8 dark:bg-gray-800"
		style="display: {activeTab === 'management' ? 'block' : 'none'}"
		transition:fade={{ duration: 200 }}
	>
		{#if canManageProperty}
			<div class="space-y-8">
				<!-- Management Header -->
				<div class="flex items-center justify-between">
					<div>
						<h2 class="mb-2 flex items-center text-2xl font-bold text-gray-900 dark:text-white">
							<svg class="mr-3 h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
								/>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
								/>
							</svg>
							{$t('property.management.title')}
						</h2>
						<p class="text-gray-600 dark:text-gray-400">
							{$t('property.management.description')}
						</p>
					</div>

					{#if canCreateRental}
						<button
							class="inline-flex items-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
							onclick={openRentalForm}
						>
							<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 4v16m8-8H4"
								/>
							</svg>
							{$t('property.management.convertToRental')}
						</button>
					{/if}
				</div>

				<!-- Rental Property Information -->
				{#if property?.rental_info}
					<div
						class="rounded-xl border border-gray-200 bg-gradient-to-r from-green-50 to-blue-50 p-6 dark:border-gray-600 dark:from-green-900/20 dark:to-blue-900/20"
					>
						<div class="mb-4 flex items-center justify-between">
							<h3 class="flex items-center text-lg font-semibold text-gray-900 dark:text-white">
								<svg
									class="mr-2 h-5 w-5 text-green-600"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
									/>
								</svg>
								{$t('property.management.rentalProperty')}
							</h3>
							<span
								class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium
								{property.rental_info.rental_status === 'rented'
									? 'bg-green-100 text-green-800'
									: property.rental_info.rental_status === 'available'
										? 'bg-blue-100 text-blue-800'
										: 'bg-gray-100 text-gray-800'}"
							>
								{$t(`property.management.status.${property.rental_info.rental_status}`)}
							</span>
						</div>

						<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
							<div class="rounded-lg bg-white/60 p-4 dark:bg-gray-800/60">
								<div class="text-sm text-gray-600 dark:text-gray-400">
									{$t('property.management.monthlyRent')}
								</div>
								<div class="text-xl font-bold text-gray-900 dark:text-white">
									{formatCurrency(property.rental_info.monthly_rent)}
								</div>
							</div>
							<div class="rounded-lg bg-white/60 p-4 dark:bg-gray-800/60">
								<div class="text-sm text-gray-600 dark:text-gray-400">
									{$t('property.management.securityDeposit')}
								</div>
								<div class="text-xl font-bold text-gray-900 dark:text-white">
									{formatCurrency(property.rental_info.security_deposit)}
								</div>
							</div>
							<div class="rounded-lg bg-white/60 p-4 dark:bg-gray-800/60">
								<div class="text-sm text-gray-600 dark:text-gray-400">
									{$t('property.management.rentalType')}
								</div>
								<div class="text-lg font-semibold text-gray-900 dark:text-white">
									{$t(`property.management.rentalTypes.${property.rental_info.rental_type}`)}
								</div>
							</div>
						</div>

						{#if property.rental_info.current_tenant}
							<div class="mt-4 border-t border-gray-200 pt-4 dark:border-gray-600">
								<h4 class="mb-2 font-medium text-gray-900 dark:text-white">
									{$t('property.management.currentTenant')}
								</h4>
								<div class="flex items-center space-x-3">
									<div
										class="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-800"
									>
										<span class="text-sm font-medium text-blue-600 dark:text-blue-200">
											{property.rental_info.current_tenant.first_name?.[0]}{property.rental_info
												.current_tenant.last_name?.[0]}
										</span>
									</div>
									<div>
										<div class="text-sm font-medium text-gray-900 dark:text-white">
											{property.rental_info.current_tenant.first_name}
											{property.rental_info.current_tenant.last_name}
										</div>
										<div class="text-xs text-gray-500 dark:text-gray-400">
											{property.rental_info.current_tenant.email}
										</div>
									</div>
								</div>
							</div>
						{/if}
					</div>
				{:else if canCreateRental}
					<div
						class="rounded-xl border-2 border-dashed border-gray-300 p-12 text-center dark:border-gray-600"
					>
						<svg
							class="mx-auto h-12 w-12 text-gray-400"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
							/>
						</svg>
						<h3 class="mt-4 text-lg font-medium text-gray-900 dark:text-white">
							{$t('property.management.noRentalInfo')}
						</h3>
						<p class="mt-2 text-gray-500 dark:text-gray-400">
							{$t('property.management.createRentalDescription')}
						</p>
						<button
							class="mt-4 inline-flex items-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-blue-700"
							onclick={openRentalForm}
						>
							<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 4v16m8-8H4"
								/>
							</svg>
							{$t('property.management.setupRental')}
						</button>
					</div>
				{/if}

				<!-- Quick Actions -->
				<div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
					<button
						class="flex items-center rounded-lg border border-gray-200 bg-white p-4 text-left transition-colors hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:hover:bg-gray-700"
					>
						<div
							class="mr-3 flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-800"
						>
							<svg
								class="h-5 w-5 text-blue-600 dark:text-blue-200"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"
								/>
							</svg>
						</div>
						<div>
							<div class="font-medium text-gray-900 dark:text-white">
								{$t('property.management.payments')}
							</div>
							<div class="text-sm text-gray-500 dark:text-gray-400">
								{$t('property.management.managePayments')}
							</div>
						</div>
					</button>

					<button
						class="flex items-center rounded-lg border border-gray-200 bg-white p-4 text-left transition-colors hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:hover:bg-gray-700"
					>
						<div
							class="mr-3 flex h-10 w-10 items-center justify-center rounded-lg bg-green-100 dark:bg-green-800"
						>
							<svg
								class="h-5 w-5 text-green-600 dark:text-green-200"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
								/>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
								/>
							</svg>
						</div>
						<div>
							<div class="font-medium text-gray-900 dark:text-white">
								{$t('property.management.maintenance')}
							</div>
							<div class="text-sm text-gray-500 dark:text-gray-400">
								{$t('property.management.scheduleMaintenance')}
							</div>
						</div>
					</button>

					<button
						class="flex items-center rounded-lg border border-gray-200 bg-white p-4 text-left transition-colors hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:hover:bg-gray-700"
					>
						<div
							class="mr-3 flex h-10 w-10 items-center justify-center rounded-lg bg-purple-100 dark:bg-purple-800"
						>
							<svg
								class="h-5 w-5 text-purple-600 dark:text-purple-200"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
								/>
							</svg>
						</div>
						<div>
							<div class="font-medium text-gray-900 dark:text-white">
								{$t('property.management.analytics')}
							</div>
							<div class="text-sm text-gray-500 dark:text-gray-400">
								{$t('property.management.viewAnalytics')}
							</div>
						</div>
					</button>
				</div>
			</div>
		{:else}
			<div class="rounded-lg bg-yellow-50 p-4 dark:bg-yellow-900/20">
				<div class="flex">
					<svg class="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
						<path
							fill-rule="evenodd"
							d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
							clip-rule="evenodd"
						/>
					</svg>
					<div class="ml-3">
						<h3 class="text-sm font-medium text-yellow-800 dark:text-yellow-200">
							{$t('property.management.accessDenied')}
						</h3>
						<div class="mt-2 text-sm text-yellow-700 dark:text-yellow-300">
							<p>{$t('property.management.accessDeniedMessage')}</p>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>

	<!-- Rental-specific tabs -->
	{#if propertyType === 'rental'}
		<!-- Tenants Tab -->
		<div
			id="tab-tenants"
			class="bg-white p-8 dark:bg-gray-800"
			style="display: {activeTab === 'tenants' ? 'block' : 'none'}"
			transition:fade={{ duration: 200 }}
		>
			<div class="space-y-6">
				<div class="flex items-center justify-between">
					<h2 class="flex items-center text-2xl font-bold text-gray-900 dark:text-white">
						<svg
							class="mr-3 h-6 w-6 text-teal-500"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
							/>
						</svg>
						{$t('propertyManagement.tenants')}
					</h2>
					<button
						class="inline-flex items-center rounded-lg bg-teal-600 px-4 py-2 text-white transition-colors hover:bg-teal-700"
					>
						<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 4v16m8-8H4"
							/>
						</svg>
						{$t('tenant.add')}
					</button>
				</div>

				{#if property?.tenants && property.tenants.length > 0}
					<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
						{#each property.tenants as tenant}
							<div
								class="rounded-lg border border-gray-200 bg-gray-50 p-6 dark:border-gray-600 dark:bg-gray-700"
							>
								<div class="mb-4 flex items-center justify-between">
									<div class="flex items-center">
										<div
											class="mr-4 flex h-12 w-12 items-center justify-center rounded-full bg-teal-100 dark:bg-teal-900"
										>
											<svg
												class="h-6 w-6 text-teal-600 dark:text-teal-400"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
												/>
											</svg>
										</div>
										<div>
											<h3 class="font-semibold text-gray-900 dark:text-white">
												{tenant.full_name}
											</h3>
											<p class="text-sm text-gray-600 dark:text-gray-400">{tenant.email}</p>
										</div>
									</div>
									<span
										class="rounded-full px-3 py-1 text-xs font-medium
										{tenant.status === 'active'
											? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
											: tenant.status === 'pending'
												? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
												: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'}"
									>
										{$t(`tenant.status.${tenant.status}`)}
									</span>
								</div>
								<div class="grid grid-cols-2 gap-4 text-sm">
									<div>
										<span class="text-gray-500 dark:text-gray-400">{$t('tenant.phone')}:</span>
										<p class="font-medium">{tenant.phone || '-'}</p>
									</div>
									<div>
										<span class="text-gray-500 dark:text-gray-400">{$t('tenant.leaseStart')}:</span>
										<p class="font-medium">{tenant.lease_start_date || '-'}</p>
									</div>
								</div>
							</div>
						{/each}
					</div>
				{:else}
					<div class="py-12 text-center">
						<svg
							class="mx-auto h-16 w-16 text-gray-400"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
							/>
						</svg>
						<h3 class="mt-4 text-lg font-medium text-gray-900 dark:text-white">
							{$t('propertyManagement.noTenants')}
						</h3>
						<p class="mt-2 text-gray-500 dark:text-gray-400">
							{$t('propertyManagement.addFirstTenant')}
						</p>
					</div>
				{/if}
			</div>
		</div>

		<!-- Maintenance Tab -->
		<div
			id="tab-maintenance"
			class="bg-white p-8 dark:bg-gray-800"
			style="display: {activeTab === 'maintenance' ? 'block' : 'none'}"
			transition:fade={{ duration: 200 }}
		>
			<div class="space-y-6">
				<div class="flex items-center justify-between">
					<h2 class="flex items-center text-2xl font-bold text-gray-900 dark:text-white">
						<svg
							class="mr-3 h-6 w-6 text-orange-500"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
							/>
						</svg>
						{$t('propertyManagement.maintenance')}
					</h2>
					<button
						class="inline-flex items-center rounded-lg bg-orange-600 px-4 py-2 text-white transition-colors hover:bg-orange-700"
					>
						<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 4v16m8-8H4"
							/>
						</svg>
						{$t('maintenance.create')}
					</button>
				</div>

				{#if property?.maintenance_requests && property.maintenance_requests.length > 0}
					<div class="space-y-4">
						{#each property.maintenance_requests as request}
							<div
								class="rounded-lg border border-gray-200 bg-gray-50 p-6 dark:border-gray-600 dark:bg-gray-700"
							>
								<div class="mb-4 flex items-center justify-between">
									<div>
										<h3 class="font-semibold text-gray-900 dark:text-white">{request.title}</h3>
										<p class="text-sm text-gray-600 dark:text-gray-400">{request.description}</p>
									</div>
									<div class="flex flex-col items-end space-y-2">
										<span
											class="rounded-full px-3 py-1 text-xs font-medium
											{request.priority === 'urgent'
												? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
												: request.priority === 'high'
													? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
													: request.priority === 'medium'
														? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
														: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'}"
										>
											{$t(`maintenance.priority.${request.priority}`)}
										</span>
										<span
											class="rounded-full px-3 py-1 text-xs font-medium
											{request.status === 'completed'
												? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
												: request.status === 'in_progress'
													? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
													: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'}"
										>
											{$t(`maintenance.status.${request.status}`)}
										</span>
									</div>
								</div>
								<div class="grid grid-cols-3 gap-4 text-sm">
									<div>
										<span class="text-gray-500 dark:text-gray-400"
											>{$t('maintenance.reportedDate')}:</span
										>
										<p class="font-medium">
											{new Date(request.reported_date).toLocaleDateString()}
										</p>
									</div>
									<div>
										<span class="text-gray-500 dark:text-gray-400"
											>{$t('maintenance.assignedWorker')}:</span
										>
										<p class="font-medium">{request.assigned_worker?.full_name || '-'}</p>
									</div>
									<div>
										<span class="text-gray-500 dark:text-gray-400"
											>{$t('maintenance.estimatedCost')}:</span
										>
										<p class="font-medium">{formatCurrency(request.estimated_cost) || '-'}</p>
									</div>
								</div>
							</div>
						{/each}
					</div>
				{:else}
					<div class="py-12 text-center">
						<svg
							class="mx-auto h-16 w-16 text-gray-400"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
							/>
						</svg>
						<h3 class="mt-4 text-lg font-medium text-gray-900 dark:text-white">
							{$t('propertyManagement.noMaintenance')}
						</h3>
						<p class="mt-2 text-gray-500 dark:text-gray-400">
							{$t('propertyManagement.addFirstMaintenance')}
						</p>
					</div>
				{/if}
			</div>
		</div>

		<!-- Finances Tab -->
		<div
			id="tab-finances"
			class="bg-white p-8 dark:bg-gray-800"
			style="display: {activeTab === 'finances' ? 'block' : 'none'}"
			transition:fade={{ duration: 200 }}
		>
			<div class="space-y-6">
				<div class="flex items-center justify-between">
					<h2 class="flex items-center text-2xl font-bold text-gray-900 dark:text-white">
						<svg
							class="mr-3 h-6 w-6 text-green-500"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						{$t('propertyManagement.finances')}
					</h2>
				</div>

				<!-- Financial Summary Cards -->
				<div class="grid grid-cols-1 gap-6 md:grid-cols-3">
					<div class="rounded-lg bg-gradient-to-r from-green-500 to-emerald-600 p-6 text-white">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-green-100">{$t('propertyManagement.monthlyRent')}</p>
								<p class="text-2xl font-bold">
									{formatCurrency(property?.rental_info?.monthly_rent) || '-'}
								</p>
							</div>
							<svg
								class="h-8 w-8 text-green-200"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
								/>
							</svg>
						</div>
					</div>

					<div class="rounded-lg bg-gradient-to-r from-blue-500 to-cyan-600 p-6 text-white">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-blue-100">{$t('propertyManagement.yearlyIncome')}</p>
								<p class="text-2xl font-bold">
									{formatCurrency((property?.rental_info?.monthly_rent || 0) * 12)}
								</p>
							</div>
							<svg
								class="h-8 w-8 text-blue-200"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
								/>
							</svg>
						</div>
					</div>

					<div class="rounded-lg bg-gradient-to-r from-purple-500 to-indigo-600 p-6 text-white">
						<div class="flex items-center justify-between">
							<div>
								<p class="text-purple-100">{$t('propertyManagement.occupancyRate')}</p>
								<p class="text-2xl font-bold">{property?.rental_info?.occupancy_rate || '0'}%</p>
							</div>
							<svg
								class="h-8 w-8 text-purple-200"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
								/>
							</svg>
						</div>
					</div>
				</div>

				<!-- Recent Transactions -->
				<div>
					<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
						{$t('propertyManagement.recentTransactions')}
					</h3>
					{#if property?.financial_records && property.financial_records.length > 0}
						<div class="overflow-hidden rounded-lg bg-gray-50 dark:bg-gray-700">
							<table class="min-w-full divide-y divide-gray-200 dark:divide-gray-600">
								<thead class="bg-gray-100 dark:bg-gray-800">
									<tr>
										<th
											class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
											>{$t('propertyManagement.date')}</th
										>
										<th
											class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
											>{$t('propertyManagement.description')}</th
										>
										<th
											class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
											>{$t('propertyManagement.amount')}</th
										>
										<th
											class="px-6 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-400"
											>{$t('propertyManagement.type')}</th
										>
									</tr>
								</thead>
								<tbody class="divide-y divide-gray-200 dark:divide-gray-600">
									{#each property.financial_records.slice(0, 5) as record}
										<tr class="hover:bg-gray-50 dark:hover:bg-gray-600">
											<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-900 dark:text-white">
												{new Date(record.date).toLocaleDateString()}
											</td>
											<td class="px-6 py-4 text-sm whitespace-nowrap text-gray-900 dark:text-white">
												{record.description}
											</td>
											<td
												class="px-6 py-4 text-sm font-medium whitespace-nowrap
												{record.type === 'income'
													? 'text-green-600 dark:text-green-400'
													: 'text-red-600 dark:text-red-400'}"
											>
												{record.type === 'income' ? '+' : '-'}{formatCurrency(record.amount)}
											</td>
											<td class="px-6 py-4 whitespace-nowrap">
												<span
													class="rounded-full px-2 py-1 text-xs font-medium
													{record.type === 'income'
														? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
														: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'}"
												>
													{$t(`propertyManagement.${record.type}`)}
												</span>
											</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					{:else}
						<div class="py-8 text-center">
							<svg
								class="mx-auto h-12 w-12 text-gray-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
								/>
							</svg>
							<p class="mt-2 text-gray-500 dark:text-gray-400">
								{$t('propertyManagement.noTransactions')}
							</p>
						</div>
					{/if}
				</div>
			</div>
		</div>
	{/if}
</div>

<!-- Rental Registration Form Modal -->
<RentalRegistrationForm
	{property}
	bind:isOpen={showRentalForm}
	onClose={closeRentalForm}
	onSubmit={handleRentalSubmit}
/>

<style>
	.scrollbar-thin {
		scrollbar-width: thin;
	}

	.scrollbar-thin::-webkit-scrollbar {
		width: 5px;
		height: 5px;
	}

	.scrollbar-thin::-webkit-scrollbar-track {
		background: transparent;
	}

	.scrollbar-thin::-webkit-scrollbar-thumb {
		background-color: rgba(107, 114, 128, 0.5);
		border-radius: 9999px;
	}
</style>
