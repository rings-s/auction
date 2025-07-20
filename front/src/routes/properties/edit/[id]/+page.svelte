<!-- src/routes/properties/edit/[id]/+page.svelte -->
<script>
	import { onMount, tick } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { t, locale } from '$lib/i18n';
	import { user } from '$lib/stores/user';
	import {
		getProperty,
		updateProperty,
		uploadPropertyMediaBatch,
		deletePropertyMedia,
		updatePropertyRoom,
		addPropertyRoom,
		deletePropertyRoom
	} from '$lib/api/property';

	// Import components
	import PropertyEditHeader from '$lib/components/properties/edit/PropertyEditHeader.svelte';
	import PropertyEditTabs from '$lib/components/properties/edit/PropertyEditTabs.svelte';
	import PropertyEditFooter from '$lib/components/properties/edit/PropertyEditFooter.svelte';

	// Get property ID from URL
	$: propertyId = $page.params.id;

	// State variables
	let property = null;
	let loading = true;
	let saving = false;
	let error = null;
	let success = null;
	let uploadingMedia = false;
	let uploadProgress = 0;
	let hasUnsavedChanges = false;
	let showSuccessModal = false;

	// Form data
	let propertyData = {};
	let rooms = [];
	let mediaFiles = [];
	let existingMedia = [];
	let deletedMediaIds = [];
	let validationErrors = {};

	// Step management
	let currentStep = 1;
	const totalSteps = 4;

	// Feature/amenity lists with bilingual support
	let featuresList = [
		{ code: 'swimming-pool', enName: 'Swimming Pool', arName: 'حمام سباحة' },
		{ code: 'garden', enName: 'Garden', arName: 'حديقة' },
		{ code: 'garage', enName: 'Garage', arName: 'مرآب' },
		{ code: 'balcony', enName: 'Balcony', arName: 'شرفة' },
		{ code: 'air-conditioning', enName: 'Air Conditioning', arName: 'تكييف' },
		{ code: 'heating', enName: 'Heating', arName: 'تدفئة' },
		{ code: 'elevator', enName: 'Elevator', arName: 'مصعد' },
		{ code: 'security-system', enName: 'Security System', arName: 'نظام أمني' },
		{ code: 'parking', enName: 'Parking', arName: 'موقف سيارات' },
		{ code: 'gym', enName: 'Gym', arName: 'صالة رياضية' },
		{ code: 'furnished', enName: 'Furnished', arName: 'مفروش' },
		{ code: 'fireplace', enName: 'Fireplace', arName: 'موقد' },
		{ code: 'storage', enName: 'Storage', arName: 'مخزن' },
		{ code: 'laundry-room', enName: 'Laundry Room', arName: 'غرفة غسيل' }
	];

	let amenitiesList = [
		{ code: 'schools', enName: 'Schools', arName: 'مدارس' },
		{ code: 'hospitals', enName: 'Hospitals', arName: 'مستشفيات' },
		{ code: 'shopping-centers', enName: 'Shopping Centers', arName: 'مراكز تسوق' },
		{ code: 'parks', enName: 'Parks', arName: 'حدائق عامة' },
		{ code: 'public-transportation', enName: 'Public Transportation', arName: 'مواصلات عامة' },
		{ code: 'restaurants', enName: 'Restaurants', arName: 'مطاعم' },
		{ code: 'beach-access', enName: 'Beach Access', arName: 'وصول للشاطئ' },
		{ code: 'sports-facilities', enName: 'Sports Facilities', arName: 'مرافق رياضية' },
		{ code: 'university', enName: 'University', arName: 'جامعة' },
		{ code: 'mosque', enName: 'Mosque', arName: 'مسجد' }
	];

	let roomFeaturesList = [
		{ code: 'window', enName: 'Window', arName: 'نافذة' },
		{ code: 'air-conditioning', enName: 'Air Conditioning', arName: 'تكييف' },
		{ code: 'heating', enName: 'Heating', arName: 'تدفئة' },
		{ code: 'bathroom', enName: 'Bathroom', arName: 'حمام' },
		{ code: 'walk-in-closet', enName: 'Walk-in Closet', arName: 'خزانة كبيرة' },
		{ code: 'built-in-wardrobe', enName: 'Built-in Wardrobe', arName: 'خزانة مدمجة' },
		{ code: 'ceiling-fan', enName: 'Ceiling Fan', arName: 'مروحة سقف' }
	];

	// Localized options
	$: availableFeatures = featuresList.map((item) => ($locale === 'ar' ? item.arName : item.enName));
	$: availableAmenities = amenitiesList.map((item) =>
		$locale === 'ar' ? item.arName : item.enName
	);
	$: availableRoomFeatures = roomFeaturesList.map((item) =>
		$locale === 'ar' ? item.arName : item.enName
	);

	// Property types options
	$: propertyTypeOptions = [
		{ value: 'residential', label: $locale === 'ar' ? 'سكني' : 'Residential' },
		{ value: 'commercial', label: $locale === 'ar' ? 'تجاري' : 'Commercial' },
		{ value: 'industrial', label: $locale === 'ar' ? 'صناعي' : 'Industrial' },
		{ value: 'land', label: $locale === 'ar' ? 'أرض' : 'Land' },
		{ value: 'agricultural', label: $locale === 'ar' ? 'زراعي' : 'Agricultural' },
		{ value: 'mixed_use', label: $locale === 'ar' ? 'متعدد الاستخدامات' : 'Mixed Use' }
	];

	// Building types options
	$: buildingTypeOptions = [
		{ value: 'apartment', label: $locale === 'ar' ? 'شقة' : 'Apartment' },
		{ value: 'villa', label: $locale === 'ar' ? 'فيلا' : 'Villa' },
		{ value: 'house', label: $locale === 'ar' ? 'منزل' : 'House' },
		{ value: 'office', label: $locale === 'ar' ? 'مكتب' : 'Office' },
		{ value: 'retail', label: $locale === 'ar' ? 'محل تجاري' : 'Retail' },
		{ value: 'warehouse', label: $locale === 'ar' ? 'مستودع' : 'Warehouse' },
		{ value: 'other', label: $locale === 'ar' ? 'أخرى' : 'Other' }
	];

	// Check permissions - include Superuser and DataEntry
	$: canEdit =
		$user &&
		($user.is_superuser ||
			$user.is_staff ||
			$user.role === 'appraiser' ||
			$user.role === 'data_entry' ||
			property?.owner?.id === $user.id);

	// Track changes
	$: {
		if (property && propertyData) {
			hasUnsavedChanges = JSON.stringify(propertyData) !== JSON.stringify(getInitialData(property));
		}
	}

	// Load property data
	async function loadProperty() {
		try {
			loading = true;
			error = null;

			const response = await getProperty(propertyId);
			property = response;

			// Initialize form data
			propertyData = getInitialData(property);
			rooms = property.rooms || [];
			existingMedia = property.media || [];
		} catch (err) {
			error = err.message || $t('error.fetchFailed');
		} finally {
			loading = false;
		}
	}

	// Get initial data structure
	function getInitialData(prop) {
		return {
			title: prop.title || '',
			property_type: prop.property_type || '',
			building_type: prop.building_type || '',
			deed_number: prop.deed_number || '',
			description: prop.description || '',
			size_sqm: prop.size_sqm || '',
			floors: prop.floors || '',
			year_built: prop.year_built || '',
			address: prop.location?.address || prop.address || '',
			city: prop.location?.city || prop.city || '',
			state: prop.location?.state || prop.state || '',
			postal_code: prop.location?.postal_code || prop.postal_code || '',
			country: prop.location?.country || prop.country || 'المملكة العربية السعودية',
			latitude: prop.location?.latitude || prop.latitude || null,
			longitude: prop.location?.longitude || prop.longitude || null,
			market_value: prop.market_value || '',
			minimum_bid: prop.minimum_bid || '',
			features: prop.features || [],
			amenities: prop.amenities || [],
			status: prop.status || 'available',
			is_published: prop.is_published || false,
			is_featured: prop.is_featured || false,
			slug: prop.slug || ''
		};
	}

	// Event handlers
	function handleLocationChange(event) {
		const locationData = event.detail;
		propertyData = { ...propertyData, ...locationData };
	}

	function handleFeaturesChange(event) {
		propertyData.features = event.detail;
	}

	function handleAmenitiesChange(event) {
		propertyData.amenities = event.detail;
	}

	function handleRoomsChange(event) {
		rooms = event.detail;
	}

	function handleMediaChange(event) {
		mediaFiles = event.detail.files;
	}

	function handleDeleteMedia(mediaId) {
		deletedMediaIds = [...deletedMediaIds, mediaId];
		existingMedia = existingMedia.filter((media) => media.id !== mediaId);
	}

	// Validation
	function validateStep(step) {
		validationErrors = {};

		if (step === 1) {
			if (!propertyData.title) {
				validationErrors.title = $t('validation.titleRequired');
			}
			if (!propertyData.property_type) {
				validationErrors.property_type = $t('validation.propertyTypeRequired');
			}
			if (!propertyData.deed_number) {
				validationErrors.deed_number = $t('validation.deedNumberRequired');
			}
			if (!propertyData.description) {
				validationErrors.description = $t('validation.descriptionRequired');
			}
		} else if (step === 2) {
			if (!propertyData.address) {
				validationErrors.address = $t('validation.addressRequired');
			}
			if (!propertyData.city) {
				validationErrors.city = $t('validation.cityRequired');
			}
			if (!propertyData.state) {
				validationErrors.state = $t('validation.stateRequired');
			}
		} else if (step === 3) {
			if (!propertyData.size_sqm) {
				validationErrors.size_sqm = $t('validation.sizeRequired');
			} else {
				const size = parseFloat(propertyData.size_sqm);
				if (isNaN(size) || size <= 0) {
					validationErrors.size_sqm = $t('validation.invalidSizeFormat');
				}
			}
		} else if (step === 4) {
			if (!propertyData.market_value) {
				validationErrors.market_value = $t('validation.marketValueRequired');
			} else {
				const value = parseFloat(propertyData.market_value);
				if (isNaN(value) || value <= 0) {
					validationErrors.market_value = $t('validation.invalidMarketValueFormat');
				}
			}

			if (propertyData.minimum_bid) {
				const minBid = parseFloat(propertyData.minimum_bid);
				if (isNaN(minBid) || minBid <= 0) {
					validationErrors.minimum_bid = $t('validation.invalidMinimumBidFormat');
				} else if (propertyData.market_value && minBid >= parseFloat(propertyData.market_value)) {
					validationErrors.minimum_bid = $t('validation.invalidMinimumBidRange');
				}
			}
		}

		return Object.keys(validationErrors).length === 0;
	}

	// Navigation
	function goToNextStep() {
		if (validateStep(currentStep)) {
			if (currentStep < totalSteps) {
				currentStep++;
				window.scrollTo(0, 0);
			}
		}
	}

	function goToPrevStep() {
		if (currentStep > 1) {
			currentStep--;
			window.scrollTo(0, 0);
		}
	}

	// Save changes
	async function handleSave() {
		if (!validateStep(currentStep)) {
			return;
		}

		saving = true;
		error = null;

		try {
			// Update property data
			await updateProperty(propertyId, propertyData);

			// Handle deleted media
			for (const mediaId of deletedMediaIds) {
				try {
					await deletePropertyMedia(propertyId, mediaId);
				} catch (err) {
					console.warn('Failed to delete media:', err);
				}
			}

			// Upload new media files
			if (mediaFiles.length > 0) {
				uploadingMedia = true;
				try {
					await uploadPropertyMediaBatch(propertyId, mediaFiles, (completed, total) => {
						uploadProgress = Math.round((completed / total) * 100);
					});
				} catch (mediaError) {
					console.warn('Failed to upload some media files:', mediaError);
				} finally {
					uploadingMedia = false;
				}
			}

			// Handle room updates
			// This is simplified - you might want more sophisticated room diff logic
			const originalRoomIds = property.rooms?.map((r) => r.id) || [];
			const currentRoomIds = rooms
				.filter((r) => r.id && !r.id.toString().startsWith('temp-'))
				.map((r) => r.id);

			// Update existing rooms
			for (const room of rooms) {
				if (room.id && !room.id.toString().startsWith('temp-')) {
					try {
						await updatePropertyRoom(propertyId, room.id, room);
					} catch (err) {
						console.warn('Failed to update room:', err);
					}
				} else if (room.id && room.id.toString().startsWith('temp-')) {
					// Create new room
					try {
						const roomData = { ...room };
						delete roomData.id;
						roomData.property = propertyId;
						await addPropertyRoom(propertyId, roomData);
					} catch (err) {
						console.warn('Failed to add room:', err);
					}
				}
			}

			// Delete removed rooms
			const removedRoomIds = originalRoomIds.filter((id) => !currentRoomIds.includes(id));
			for (const roomId of removedRoomIds) {
				try {
					await deletePropertyRoom(propertyId, roomId);
				} catch (err) {
					console.warn('Failed to delete room:', err);
				}
			}

			success = $t('property.updateSuccess');
			hasUnsavedChanges = false;
			showSuccessModal = true;

			// Reload property data
			await loadProperty();
		} catch (err) {
			error = err.message || $t('property.updateFailed');
		} finally {
			saving = false;
		}
	}

	function handleCancel() {
		if (hasUnsavedChanges) {
			if (confirm($t('property.confirmDiscardChanges'))) {
				goto(`/properties/${propertyId}`);
			}
		} else {
			goto(`/properties/${propertyId}`);
		}
	}

	function closeSuccessModal() {
		showSuccessModal = false;
		goto(`/properties/${propertyId}`);
	}

	// Load property on mount and when ID changes
	$: if (propertyId) {
		loadProperty();
	}

	onMount(() => {
		// Warn user about unsaved changes when leaving page
		const handleBeforeUnload = (e) => {
			if (hasUnsavedChanges) {
				e.preventDefault();
				e.returnValue = '';
			}
		};

		window.addEventListener('beforeunload', handleBeforeUnload);

		return () => {
			window.removeEventListener('beforeunload', handleBeforeUnload);
		};
	});
</script>

<svelte:head>
	<title
		>{property?.title
			? `${$t('property.edit')} - ${property.title}`
			: $t('property.editProperty')}</title
	>
</svelte:head>

<div class="min-h-screen py-12">
	<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
		<!-- Back Button -->
		<div class="mb-6">
			<a
				href={`/properties/${propertyId}`}
				class="text-primary-600 dark:text-primary-400 hover:text-primary-500 dark:hover:text-primary-300 inline-flex items-center text-sm font-medium transition-colors"
			>
				<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M10 19l-7-7m0 0l7-7m-7 7h18"
					/>
				</svg>
				{$t('property.backToProperty')}
			</a>
		</div>

		<!-- Loading State -->
		{#if loading && !property}
			<div class="flex flex-col items-center justify-center py-20">
				<div
					class="border-primary-500 h-16 w-16 animate-spin rounded-full border-t-2 border-b-2"
				></div>
				<p class="mt-4 text-gray-500 dark:text-gray-400">{$t('common.loading')}</p>
			</div>

			<!-- Error State -->
		{:else if error && !property}
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

			<!-- Permission Denied -->
		{:else if property && !canEdit}
			<div
				class="mx-auto max-w-3xl rounded-md border-l-4 border-yellow-400 bg-yellow-50 p-4 shadow-md dark:border-yellow-600 dark:bg-yellow-900/20"
			>
				<div class="flex">
					<div class="flex-shrink-0">
						<svg class="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
							<path
								fill-rule="evenodd"
								d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
								clip-rule="evenodd"
							/>
						</svg>
					</div>
					<div class="ml-3">
						<p class="text-sm text-yellow-700 dark:text-yellow-200">
							{$t('property.noEditPermission')}
						</p>
					</div>
				</div>
			</div>

			<!-- Edit Form -->
		{:else if property && canEdit}
			<div class="mx-auto max-w-4xl">
				<!-- Header Component -->
				<PropertyEditHeader
					{property}
					{currentStep}
					{totalSteps}
					loading={saving}
					{hasUnsavedChanges}
				/>

				<!-- Content Tabs Component -->
				<PropertyEditTabs
					{currentStep}
					{propertyData}
					{rooms}
					{mediaFiles}
					{existingMedia}
					{validationErrors}
					{availableFeatures}
					{availableAmenities}
					{availableRoomFeatures}
					{propertyTypeOptions}
					{buildingTypeOptions}
					onLocationChange={handleLocationChange}
					onFeaturesChange={handleFeaturesChange}
					onAmenitiesChange={handleAmenitiesChange}
					onRoomsChange={handleRoomsChange}
					onMediaChange={handleMediaChange}
					onDeleteMedia={handleDeleteMedia}
				/>

				<!-- Footer Component -->
				<PropertyEditFooter
					{currentStep}
					{totalSteps}
					loading={saving}
					{uploadingMedia}
					{uploadProgress}
					{hasUnsavedChanges}
					{propertyId}
					onNext={goToNextStep}
					onPrev={goToPrevStep}
					onSave={handleSave}
					onCancel={handleCancel}
				/>

				<!-- Error Message -->
				{#if error}
					<div
						class="mt-6 rounded-md border-l-4 border-red-400 bg-red-50 p-4 shadow-md dark:border-red-600 dark:bg-red-900/20"
					>
						<div class="flex">
							<div class="flex-shrink-0">
								<svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
									<path
										fill-rule="evenodd"
										d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
										clip-rule="evenodd"
									/>
								</svg>
							</div>
							<div class="ml-3">
								<p class="text-sm text-red-700 dark:text-red-200">
									{error}
								</p>
							</div>
						</div>
					</div>
				{/if}
			</div>
		{/if}

		<!-- Success Modal -->
		{#if showSuccessModal}
			<div
				class="bg-opacity-75 fixed inset-0 z-50 flex items-center justify-center bg-gray-500 p-4"
			>
				<div class="w-full max-w-md rounded-xl bg-white p-8 shadow-2xl dark:bg-gray-800">
					<div class="text-center">
						<div
							class="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-green-100 dark:bg-green-900"
						>
							<svg
								class="h-12 w-12 text-green-500 dark:text-green-300"
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
						</div>

						<h3 class="mt-6 text-xl font-bold text-gray-900 dark:text-white">
							{$t('property.updateSuccess')}
						</h3>

						<p class="mt-4 text-base text-gray-500 dark:text-gray-400">
							{$t('property.propertyUpdatedMessage')}
						</p>

						<div
							class="mt-10 flex flex-col justify-center space-y-4 sm:flex-row sm:space-y-0 sm:space-x-4"
						>
							<button
								type="button"
								on:click={() => goto('/properties')}
								class="focus:ring-primary-500 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition-all duration-200 hover:bg-gray-50 focus:ring-2 focus:ring-offset-2 focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
							>
								{$t('properties.backToProperties')}
							</button>

							<button
								type="button"
								on:click={closeSuccessModal}
								class="btn-modern-primary rounded-md px-4 py-2 text-sm font-medium shadow-sm transition-all duration-200"
							>
								{$t('property.viewProperty')}
							</button>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>
