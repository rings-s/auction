<script>
	import { onMount, tick } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import { user } from '$lib/stores/user';
	import { getPropertyBySlug } from '$lib/api/property';

	// Import the new components
	import PropertyHeader from '$lib/components/properties/detail/PropertyHeader.svelte';
	import PropertyContentTabs from '$lib/components/properties/detail/PropertyContentTabs.svelte';
	import PropertyGalleryModal from '$lib/components/properties/detail/PropertyGalleryModal.svelte';

	// State variables
	let property = null;
	let loading = true;
	let error = null;
	let activeImageIndex = 0;
	let showFullScreenGallery = false;
	let mapInitialized = false;
	let mapElement;
	let map;
	let marker;
	let activeMediaType = 'image';
	let touchStartX = 0;
	let touchEndX = 0;
	let isImagesLoading = true;
	let imagesLoaded = 0;
	let thumbnailsContainer;

	// Filter media by type
	$: filteredMedia = property?.media?.filter((item) => item.media_type === activeMediaType) || [];
	$: images = property?.media?.filter((item) => item.media_type === 'image') || [];
	$: videos = property?.media?.filter((item) => item.media_type === 'video') || [];
	$: documents = property?.media?.filter((item) => item.media_type === 'document') || [];
	$: otherFiles = property?.media?.filter((item) => item.media_type === 'other') || [];

	// Get main image
	$: mainImage =
		property?.main_image ||
		(images.length > 0 ? images.find((img) => img.is_primary) || images[0] : null);

	// Tabs management
	let activeTab = 'overview';
	const tabs = [
		{ id: 'overview', label: $t('property.tab.overview'), icon: 'home' },
		{ id: 'rooms', label: $t('property.tab.rooms'), icon: 'layout' },
		{ id: 'location', label: $t('property.tab.location'), icon: 'map-pin' },
		{ id: 'gallery', label: $t('property.tab.gallery'), icon: 'image' }
	];

	// Gallery tabs
	const mediaTabs = [
		{ id: 'image', label: $t('property.galleryTabs.photos') },
		{ id: 'video', label: $t('property.galleryTabs.videos') },
		{ id: 'document', label: $t('property.galleryTabs.documents') },
		{ id: 'other', label: $t('property.galleryTabs.otherFiles') }
	];

	// Sticky header control
	let scrollY = 0;
	let headerHeight = 0;
	let headerElement;
	let isHeaderSticky = false;
	$: isHeaderSticky = scrollY > headerHeight;

	// Get slug from URL and ensure it's properly decoded
	$: slug = decodeURIComponent($page.params.slug);

	// Check edit permissions
	$: canEdit =
		$user && ($user.is_staff || $user.role === 'appraiser' || property?.owner?.id === $user.id);

	// Track image loading progress
	function handleImageLoad() {
		imagesLoaded++;
		if (imagesLoaded >= 1) {
			isImagesLoading = false;
		}
	}

	// Load property data
	async function loadProperty() {
		try {
			loading = true;
			error = null;
			imagesLoaded = 0;
			isImagesLoading = true;

			const response = await getPropertyBySlug(slug);
			property = response;

			// Initialize after data loads
			await tick();
			if (headerElement) {
				headerHeight = headerElement.offsetHeight;
			}

			// Initialize map if location tab is active
			if (
				activeTab === 'location' &&
				property?.location?.latitude &&
				property?.location?.longitude
			) {
				initializeMap();
			}
		} catch (err) {
			error = err.message || $t('error.fetchFailed');
		} finally {
			loading = false;
		}
	}

	// Switch tabs with smooth transitions
	async function setActiveTab(tabId) {
		if (activeTab === tabId) return;
		activeTab = tabId;

		// Initialize map if switching to location tab
		if (tabId === 'location' && property?.location?.latitude && property?.location?.longitude) {
			await tick();
			initializeMap();
		}

		// Scroll to tab content on mobile
		if (window.innerWidth < 768) {
			const tabContent = document.getElementById(`tab-${tabId}`);
			if (tabContent) {
				const offset = isHeaderSticky ? 60 : 0;
				window.scrollTo({
					top: tabContent.offsetTop - offset,
					behavior: 'smooth'
				});
			}
		}
	}

	// Switch media type for gallery
	function setActiveMediaType(mediaType) {
		activeMediaType = mediaType;
		activeImageIndex = 0;
	}

	// Initialize map with property location
	function initializeMap() {
		if (typeof window === 'undefined' || !property?.location || mapInitialized) return;

		// Load Leaflet if not already loaded
		if (!window.L) {
			const cssLink = document.createElement('link');
			cssLink.rel = 'stylesheet';
			cssLink.href = 'https://unpkg.com/leaflet@1.9.3/dist/leaflet.css';
			document.head.appendChild(cssLink);

			const script = document.createElement('script');
			script.src = 'https://unpkg.com/leaflet@1.9.3/dist/leaflet.js';
			script.onload = createMap;
			document.head.appendChild(script);
		} else {
			createMap();
		}
	}

	// Create the map with property location
	function createMap() {
		if (!mapElement || !property?.location) return;

		const lat = property.location.latitude || 0;
		const lng = property.location.longitude || 0;

		if (!lat || !lng) return;

		map = L.map(mapElement, {
			scrollWheelZoom: false,
			dragging: !L.Browser.mobile
		}).setView([lat, lng], 15);

		L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
			attribution:
				'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
			subdomains: 'abcd',
			maxZoom: 19
		}).addTo(map);

		const customIcon = L.divIcon({
			className: 'custom-map-marker',
			html: `<div class="marker-pin"></div>
             <span class="marker-icon">
               <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
                 <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
               </svg>
             </span>
             ${property.location.house_number ? `<div class="house-number">${property.location.house_number}</div>` : ''}
             `,
			iconSize: [30, 42],
			iconAnchor: [15, 42]
		});

		marker = L.marker([lat, lng], { icon: customIcon })
			.addTo(map)
			.bindPopup(
				`
        <div class="map-popup">
          <h3 class="text-base font-semibold">${property.title}</h3>
          <p class="text-sm mt-1">${property.location.address}</p>
          <p class="text-primary-600 font-bold mt-2">${formatCurrency(property.market_value)}</p>
        </div>
      `,
				{ className: 'custom-popup' }
			);

		L.circle([lat, lng], {
			radius: 500,
			fillColor: '#3b82f6',
			fillOpacity: 0.1,
			color: '#3b82f6',
			weight: 1
		}).addTo(map);

		map.on('click', function () {
			if (!map.scrollWheelZoom.enabled()) {
				map.scrollWheelZoom.enable();
				L.DomUtil.addClass(mapElement, 'active-map');
			}
		});

		document.addEventListener('click', function (e) {
			if (mapElement && !mapElement.contains(e.target)) {
				map.scrollWheelZoom.disable();
				L.DomUtil.removeClass(mapElement, 'active-map');
			}
		});

		mapInitialized = true;

		setTimeout(() => {
			if (map) map.invalidateSize();
		}, 400);
	}

	// Gallery navigation functions
	function showMedia(index) {
		activeImageIndex = index;

		if (thumbnailsContainer && showFullScreenGallery) {
			const thumbnailWidth = 72;
			thumbnailsContainer.scrollTo({
				left: index * thumbnailWidth - thumbnailsContainer.clientWidth / 2 + thumbnailWidth / 2,
				behavior: 'smooth'
			});
		}
	}

	function toggleGallery(index = 0) {
		if (typeof index === 'number') {
			activeImageIndex = index;
		}
		showFullScreenGallery = !showFullScreenGallery;
		document.body.style.overflow = showFullScreenGallery ? 'hidden' : '';
	}

	function nextMedia() {
		if (filteredMedia.length) {
			activeImageIndex = (activeImageIndex + 1) % filteredMedia.length;
			showMedia(activeImageIndex);
		}
	}

	function prevMedia() {
		if (filteredMedia.length) {
			activeImageIndex = (activeImageIndex - 1 + filteredMedia.length) % filteredMedia.length;
			showMedia(activeImageIndex);
		}
	}

	// Touch events for swipe on gallery
	function handleTouchStart(e) {
		touchStartX = e.touches[0].clientX;
	}

	function handleTouchEnd(e) {
		touchEndX = e.changedTouches[0].clientX;
		if (touchStartX - touchEndX > 50) {
			nextMedia();
		} else if (touchEndX - touchStartX > 50) {
			prevMedia();
		}
	}

	// Contact property owner
	function contactOwner() {
		if (!$user) {
			goto('/login');
			return;
		}
	}

	// Format currency
	function formatCurrency(value) {
		if (!value) return '$0';
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			maximumFractionDigits: 0
		}).format(value);
	}

	// Keyboard shortcuts for gallery
	function handleKeydown(event) {
		if (showFullScreenGallery) {
			if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
				nextMedia();
			} else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
				prevMedia();
			} else if (event.key === 'Escape') {
				showFullScreenGallery = false;
				document.body.style.overflow = '';
			}
		}
	}

	// Load property on mount and when slug changes
	$: if (slug) {
		loadProperty();
	}

	onMount(() => {
		loadProperty();

		// Setup keyboard listener
		window.addEventListener('keydown', handleKeydown);

		// Cleanup on unmount
		return () => {
			window.removeEventListener('keydown', handleKeydown);
			if (map) {
				map.remove();
				mapInitialized = false;
			}
			document.body.style.overflow = '';
		};
	});
</script>

<svelte:window bind:scrollY />

<svelte:head>
	<title>{property?.title || $t('property.loading')} | Real Estate Platform</title>
	<meta
		name="description"
		content={property?.meta_description || property?.description?.substr(0, 160) || ''}
	/>
</svelte:head>

<div class="min-h-screen pb-16">
	<!-- Back Button -->
	<div class="mx-auto max-w-7xl px-4 pt-6 sm:px-6 lg:px-8">
		<a
			href="/properties"
			class="text-primary-600 dark:text-primary-400 hover:text-primary-500 dark:hover:text-primary-300 inline-flex items-center text-sm font-medium transition-colors"
		>
			<svg
				class="mr-2 h-4 w-4"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M10 19l-7-7m0 0l7-7m-7 7h18"
				/>
			</svg>
			{$t('properties.backToProperties')}
		</a>
	</div>

	<!-- Main Content -->
	<div class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
		<!-- Loading State -->
		{#if loading && !property}
			<div class="flex flex-col items-center justify-center py-20">
				<div
					class="border-primary-500 h-16 w-16 animate-spin rounded-full border-t-2 border-b-2"
				></div>
				<p class="mt-4 text-gray-500 dark:text-gray-400">{$t('common.loading')}</p>
			</div>

			<!-- Error State -->
		{:else if error}
			<div
				class="mx-auto my-12 max-w-3xl rounded-lg bg-red-50 p-6 text-red-800 dark:bg-red-900/20 dark:text-red-200"
			>
				<h2 class="mb-2 flex items-center text-xl font-semibold">
					<svg
						class="mr-2 h-6 w-6 text-red-500"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
						/>
					</svg>
					{$t('error.title')}
				</h2>
				<p>{error}</p>
				<div class="mt-4 flex space-x-4">
					<button
						class="bg-primary-600 hover:bg-primary-700 focus:ring-primary-500 inline-flex items-center rounded-md border border-transparent px-4 py-2 text-sm font-medium text-white shadow-sm transition-all focus:ring-2 focus:ring-offset-2"
						on:click={loadProperty}
					>
						<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
							/>
						</svg>
						{$t('auction.tryAgain')}
					</button>
					<a
						href="/properties"
						class="focus:ring-primary-500 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50 focus:ring-2 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
					>
						{$t('properties.backToProperties')}
					</a>
				</div>
			</div>

			<!-- Property Details -->
		{:else if property}
			<!-- Property Header -->
			<PropertyHeader
				bind:this={headerElement}
				{property}
				{canEdit}
				{isHeaderSticky}
				{activeTab}
				{tabs}
				onSetActiveTab={setActiveTab}
				onContactOwner={contactOwner}
			/>

			<!-- Property Content Tabs -->
			<PropertyContentTabs
				{property}
				{activeTab}
				{activeImageIndex}
				{showFullScreenGallery}
				{filteredMedia}
				{images}
				{videos}
				{documents}
				{otherFiles}
				{isImagesLoading}
				bind:mapElement
				{activeMediaType}
				{mediaTabs}
				{mainImage}
				onToggleGallery={toggleGallery}
				onHandleImageLoad={handleImageLoad}
				onSetActiveMediaType={setActiveMediaType}
				onInitializeMap={initializeMap}
			/>
		{/if}
	</div>
</div>

<!-- Gallery Modal -->
<PropertyGalleryModal
	{showFullScreenGallery}
	{filteredMedia}
	{activeImageIndex}
	{activeMediaType}
	{property}
	bind:thumbnailsContainer
	onToggleGallery={toggleGallery}
	onNextMedia={nextMedia}
	onPrevMedia={prevMedia}
	onShowMedia={showMedia}
	onHandleTouchStart={handleTouchStart}
	onHandleTouchEnd={handleTouchEnd}
/>

<style>
	/* Map styling */
	:global(.active-map) {
		border: 2px solid #3b82f6;
	}

	:global(.leaflet-container) {
		z-index: 1 !important;
	}

	:global(.custom-map-marker) {
		width: 30px;
		height: 42px;
		position: relative;
	}

	:global(.marker-pin) {
		width: 30px;
		height: 30px;
		border-radius: 50% 50% 50% 0;
		background: #3b82f6;
		position: absolute;
		transform: rotate(-45deg);
		left: 50%;
		top: 50%;
		margin: -15px 0 0 -15px;
		border: 2px solid white;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
	}

	:global(.marker-icon) {
		background: white;
		width: 14px;
		height: 14px;
		position: absolute;
		margin: 8px 0 0 8px;
		border-radius: 50%;
		left: 0;
		top: 0;
		color: #3b82f6;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	:global(.custom-popup .leaflet-popup-content-wrapper) {
		background: white;
		border-radius: 8px;
		box-shadow:
			0 4px 6px -1px rgba(0, 0, 0, 0.1),
			0 2px 4px -1px rgba(0, 0, 0, 0.06);
		padding: 12px;
	}

	:global(.map-popup h3) {
		margin: 0 0 5px 0;
		color: #1f2937;
	}

	:global(.map-popup p) {
		margin: 0;
		color: #6b7280;
	}
</style>
