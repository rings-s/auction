<!-- src/routes/properties/create/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t, language } from '$lib/i18n';
	import { property } from '$lib/stores/property';
	import { toast } from '$lib/stores/toast';
	import { fade, slide } from 'svelte/transition';

	// UI Components
	import Button from '$lib/components/ui/Button.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import { Textarea } from '$lib/components/ui/Textarea.svelte';
	import Switch from '$lib/components/ui/Switch.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import Spinner from '$lib/components/ui/Spinner.svelte';
	import { PropertyMediaUploader } from '$lib/components/properties/PropertyMediaUploader.svelte';
	import PropertyMap from '$lib/components/properties/PropertyMap.svelte';
	import PropertyFeaturesSelector from '$lib/components/properties/PropertyFeaturesSelector.svelte';

	// State variables
	let activeTab = 'basic';
	let submitting = false;
	let errors = {};
	let formValid = false;
	let locationMapVisible = false;

	// Form data state
	let propertyData = {
		title: '',
		property_type: '',
		description: '',
		status: 'draft',

		// Location
		address: '',
		city: '',
		district: '',
		country: '',
		postal_code: '',
		latitude: null,
		longitude: null,

		// Features
		bedrooms: null,
		bathrooms: null,
		area: null,
		year_built: null,
		floor_number: null,
		facing_direction: '',
		parking_spaces: null,

		// Additional features
		has_garden: false,
		has_pool: false,
		has_balcony: false,
		has_elevator: false,
		has_security: false,

		// Media
		images: [],
		main_image: null,
		videos: [],

		// Pricing
		estimated_value: null,

		// Settings
		is_featured: false,
		is_published: false
	};

	// Reactive variables
	$: isRTL = $language === 'ar';
	$: canSubmit = validateForm() && !submitting;

	// Options for dropdowns - using translations
	$: propertyTypeOptions = [
		{ value: 'apartment', label: $t('properties.types.apartment') },
		{ value: 'villa', label: $t('properties.types.villa') },
		{ value: 'land', label: $t('properties.types.land') },
		{ value: 'commercial', label: $t('properties.types.commercial') },
		{ value: 'industrial', label: $t('properties.types.industrial') },
		{ value: 'mixed_use', label: $t('properties.types.mixed_use') },
		{ value: 'building', label: $t('properties.types.building') },
		{ value: 'farm', label: $t('properties.types.farm') },
		{ value: 'office', label: $t('properties.types.office') },
		{ value: 'retail', label: $t('properties.types.retail') }
	];

	$: propertyStatusOptions = [
		{ value: 'draft', label: $t('properties.status.draft') || 'Draft' },
		{ value: 'active', label: $t('properties.status.active') || 'Active' },
		{ value: 'pending', label: $t('properties.status.pending') || 'Pending' }
	];

	$: facingDirectionOptions = [
		{ value: 'north', label: $t('properties.facing.north') || 'North' },
		{ value: 'south', label: $t('properties.facing.south') || 'South' },
		{ value: 'east', label: $t('properties.facing.east') || 'East' },
		{ value: 'west', label: $t('properties.facing.west') || 'West' },
		{ value: 'northeast', label: $t('properties.facing.northeast') || 'Northeast' },
		{ value: 'northwest', label: $t('properties.facing.northwest') || 'Northwest' },
		{ value: 'southeast', label: $t('properties.facing.southeast') || 'Southeast' },
		{ value: 'southwest', label: $t('properties.facing.southwest') || 'Southwest' }
	];

	// Tabs configuration - using translations
	$: tabs = [
		{ id: 'basic', label: $t('properties.create.tabs.basic') || 'Basic', icon: 'home' },
		{ id: 'location', label: $t('properties.create.tabs.location') || 'Location', icon: 'map-pin' },
		{ id: 'features', label: $t('properties.create.tabs.features') || 'Features', icon: 'list' },
		{ id: 'media', label: $t('properties.create.tabs.media') || 'Media', icon: 'image' },
		{
			id: 'pricing',
			label: $t('properties.create.tabs.pricing') || 'Pricing',
			icon: 'dollar-sign'
		},
		{ id: 'settings', label: $t('properties.create.tabs.settings') || 'Settings', icon: 'settings' }
	];

	// Computed classes for tabs
	$: getTabClasses = (tabId) => {
		const isActive = activeTab === tabId;
		return [
			'w-full flex items-center px-3 py-3 text-left rounded-lg transition-colors',
			isActive ? 'bg-primary-50' : '',
			isActive ? 'dark:bg-primary-900/20' : '',
			isActive ? 'text-primary-700' : 'text-neutral-700',
			isActive ? 'dark:text-primary-300' : 'dark:text-neutral-300',
			!isActive ? 'hover:bg-neutral-100' : '',
			!isActive ? 'dark:hover:bg-neutral-800/70' : ''
		]
			.filter(Boolean)
			.join(' ');
	};

	$: getIconClasses = (tabId) => {
		const isActive = activeTab === tabId;
		return [
			'mr-3 flex-shrink-0 h-6 w-6 flex items-center justify-center rounded-full',
			isActive ? 'bg-primary-100' : 'bg-neutral-100',
			isActive ? 'dark:bg-primary-800/30' : 'dark:bg-neutral-800/50',
			isActive ? 'text-primary-700' : 'text-neutral-500',
			isActive ? 'dark:text-primary-300' : 'dark:text-neutral-400'
		]
			.filter(Boolean)
			.join(' ');
	};

	// Handle tab change
	function changeTab(tabId) {
		if (submitting) return;
		activeTab = tabId;
	}

	// Go to next tab
	function goToNextTab() {
		const currentIndex = tabs.findIndex((tab) => tab.id === activeTab);
		if (currentIndex < tabs.length - 1) {
			activeTab = tabs[currentIndex + 1].id;
			window.scrollTo({ top: 0, behavior: 'smooth' });
		}
	}

	// Go to previous tab
	function goToPreviousTab() {
		const currentIndex = tabs.findIndex((tab) => tab.id === activeTab);
		if (currentIndex > 0) {
			activeTab = tabs[currentIndex - 1].id;
			window.scrollTo({ top: 0, behavior: 'smooth' });
		}
	}

	// Handle map location selection
	function handleLocationSelect(event) {
		const { lat, lng } = event.detail;
		propertyData.latitude = lat;
		propertyData.longitude = lng;
	}

	// Toggle location map visibility
	function toggleLocationMap() {
		locationMapVisible = !locationMapVisible;
	}

	// Handle media uploads
	function handleMediaUpdate(event) {
		const { images, mainImage } = event.detail;
		propertyData.images = images;
		propertyData.main_image = mainImage;
	}

	// Handle features update
	function handleFeaturesUpdate(event) {
		const { features } = event.detail;
		propertyData = { ...propertyData, ...features };
	}

	// Validate form fields
	function validateForm() {
		errors = {};
		let valid = true;

		// Basic tab validation
		if (!propertyData.title) {
			errors.title = $t('properties.create.errors.title_required') || 'Title is required';
			valid = false;
		}

		if (!propertyData.property_type) {
			errors.property_type =
				$t('properties.create.errors.type_required') || 'Property type is required';
			valid = false;
		}

		// Location tab validation
		if (activeTab === 'location' || activeTab === 'submit') {
			if (!propertyData.city) {
				errors.city = $t('properties.create.errors.city_required') || 'City is required';
				valid = false;
			}
		}

		// Features tab validation
		if (activeTab === 'features' || activeTab === 'submit') {
			if (propertyData.bedrooms !== null && propertyData.bedrooms < 0) {
				errors.bedrooms =
					$t('properties.create.errors.bedrooms_invalid') || 'Invalid number of bedrooms';
				valid = false;
			}

			if (propertyData.bathrooms !== null && propertyData.bathrooms < 0) {
				errors.bathrooms =
					$t('properties.create.errors.bathrooms_invalid') || 'Invalid number of bathrooms';
				valid = false;
			}

			if (propertyData.area !== null && propertyData.area <= 0) {
				errors.area =
					$t('properties.create.errors.area_invalid') || 'Area must be greater than zero';
				valid = false;
			}
		}

		// Pricing tab validation
		if (activeTab === 'pricing' || activeTab === 'submit') {
			if (propertyData.estimated_value !== null && propertyData.estimated_value <= 0) {
				errors.estimated_value =
					$t('properties.create.errors.price_invalid') || 'Price must be greater than zero';
				valid = false;
			}
		}

		formValid = valid;
		return valid;
	}

	// Handle form submission
	async function handleSubmit() {
		// Final validation
		if (!validateForm()) {
			toast.error(
				$t('properties.create.errors.form_invalid') || 'Please fix the errors in the form'
			);
			return;
		}

		submitting = true;

		try {
			// Create the property using the property store
			const result = await propertyStore.createProperty(propertyData);

			if (result) {
				toast.success($t('properties.create.success') || 'Property created successfully');

				// Redirect to the new property page
				goto(`/dashboard/properties/${result.id}`);
			} else {
				throw new Error('Failed to create property');
			}
		} catch (err) {
			console.error('Failed to create property:', err);

			// Handle error messages
			if (err.response?.data?.errors) {
				errors = { ...errors, ...err.response.data.errors };
			}

			toast.error($t('properties.create.errors.submission_failed') || 'Failed to create property');
		} finally {
			submitting = false;
		}
	}

	// Initialize
	onMount(() => {
		// Initialize any third-party components or load necessary data
	});
</script>

<svelte:head>
	<title>{$t('properties.create.title') || 'Create Property'} | {$t('general.app_name')}</title>
	<meta
		name="description"
		content={$t('properties.create.meta_description') || 'Create a new property listing'}
	/>
</svelte:head>

<div class="container mx-auto px-4 py-6 md:py-12" class:rtl={isRTL}>
	<!-- Header Section -->
	<header class="mb-8">
		<h1 class="text-2xl font-bold text-neutral-900 dark:text-white md:text-3xl">
			{$t('properties.create.title') || 'Create New Property'}
		</h1>
		<p class="mt-2 text-neutral-600 dark:text-neutral-400">
			{$t('properties.create.subtitle') || 'Fill in the details to create a new property listing'}
		</p>
	</header>

	<!-- Main Content Area -->
	<div class="grid grid-cols-1 gap-8 lg:grid-cols-4">
		<!-- Sidebar with Tabs -->
		<div class="order-2 lg:order-1 lg:col-span-1">
			<Card padding={true} class="sticky top-24">
				<nav aria-label="Property creation steps" class="space-y-1">
					{#each tabs as tab}
						<button
							class={getTabClasses(tab.id)}
							on:click={() => changeTab(tab.id)}
							disabled={submitting}
							aria-selected={activeTab === tab.id}
							role="tab"
						>
							<!-- Tab Icon -->
							<span class={getIconClasses(tab.id)}>
								{#if tab.icon === 'home'}
									<svg
										xmlns="http://www.w3.org/2000/svg"
										class="h-4 w-4"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
										<polyline points="9 22 9 12 15 12 15 22" />
									</svg>
								{:else if tab.icon === 'map-pin'}
									<svg
										xmlns="http://www.w3.org/2000/svg"
										class="h-4 w-4"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" />
										<circle cx="12" cy="10" r="3" />
									</svg>
								{:else if tab.icon === 'list'}
									<svg
										xmlns="http://www.w3.org/2000/svg"
										class="h-4 w-4"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<line x1="8" y1="6" x2="21" y2="6" />
										<line x1="8" y1="12" x2="21" y2="12" />
										<line x1="8" y1="18" x2="21" y2="18" />
										<line x1="3" y1="6" x2="3.01" y2="6" />
										<line x1="3" y1="12" x2="3.01" y2="12" />
										<line x1="3" y1="18" x2="3.01" y2="18" />
									</svg>
								{:else if tab.icon === 'image'}
									<svg
										xmlns="http://www.w3.org/2000/svg"
										class="h-4 w-4"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
										<circle cx="9" cy="9" r="2" />
										<path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
									</svg>
								{:else if tab.icon === 'dollar-sign'}
									<svg
										xmlns="http://www.w3.org/2000/svg"
										class="h-4 w-4"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<line x1="12" y1="2" x2="12" y2="22" />
										<path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
									</svg>
								{:else if tab.icon === 'settings'}
									<svg
										xmlns="http://www.w3.org/2000/svg"
										class="h-4 w-4"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"
										/>
										<circle cx="12" cy="12" r="3" />
									</svg>
								{/if}
							</span>

							<span class="text-base font-medium">{tab.label}</span>

							<!-- Completion indicator -->
							<span class="ml-auto" aria-hidden="true">
								{#if activeTab === tab.id}
									<svg
										class="text-primary h-5 w-5"
										xmlns="http://www.w3.org/2000/svg"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<polyline points="9 11 12 14 22 4"></polyline>
										<path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
									</svg>
								{/if}
							</span>
						</button>
					{/each}
				</nav>

				<!-- Form Progress -->
				<div class="mt-8 border-t border-neutral-200 pt-6 dark:border-neutral-700">
					<div class="mb-2 flex items-center justify-between">
						<span class="text-sm font-medium text-neutral-700 dark:text-neutral-300">
							{$t('properties.create.form_progress') || 'Form Progress'}
						</span>
						<span class="text-xs font-medium text-neutral-700 dark:text-neutral-300">
							{(((tabs.findIndex((tab) => tab.id === activeTab) + 1) / tabs.length) * 100).toFixed(
								0
							)}%
						</span>
					</div>
					<div class="h-1.5 w-full rounded-full bg-neutral-200 dark:bg-neutral-700">
						<div
							class="bg-primary h-1.5 rounded-full transition-all duration-300"
							style="width: {(
								((tabs.findIndex((tab) => tab.id === activeTab) + 1) / tabs.length) *
								100
							).toFixed(0)}%"
						></div>
					</div>
				</div>
			</Card>
		</div>

		<!-- Form Area -->
		<div class="order-1 lg:order-2 lg:col-span-3">
			<Card padding={true}>
				<div class="property-create-form">
					{#if activeTab === 'basic'}
						<!-- Basic Information Tab -->
						<div transition:fade={{ duration: 200 }}>
							<h2 class="mb-6 text-xl font-semibold text-neutral-900 dark:text-white">
								{$t('properties.create.basic_info') || 'Basic Information'}
							</h2>

							<div class="space-y-6">
								<!-- Property Title -->
								<Input
									type="text"
									label={$t('properties.title_label') || 'Property Title'}
									placeholder={$t('properties.title_placeholder') || 'Enter property title'}
									bind:value={propertyData.title}
									error={errors.title}
									required
								/>

								<!-- Property Type -->
								<Select
									label={$t('properties.type_label') || 'Property Type'}
									placeholder={$t('properties.type_placeholder') || 'Select property type'}
									options={propertyTypeOptions}
									bind:value={propertyData.property_type}
									error={errors.property_type}
									required
								/>

								<!-- Property Status -->
								<Select
									label={$t('properties.status_label') || 'Status'}
									placeholder={$t('properties.status_placeholder') || 'Select status'}
									options={propertyStatusOptions}
									bind:value={propertyData.status}
									error={errors.status}
									required
								/>

								<!-- Property Description -->
								<Textarea
									label={$t('properties.description_label') || 'Description'}
									placeholder={$t('properties.description_placeholder') ||
										'Describe the property...'}
									bind:value={propertyData.description}
									rows={4}
								/>
							</div>
						</div>
					{:else if activeTab === 'location'}
						<!-- Location Tab -->
						<div transition:fade={{ duration: 200 }}>
							<h2 class="mb-6 text-xl font-semibold text-neutral-900 dark:text-white">
								{$t('properties.create.location_info') || 'Location Information'}
							</h2>

							<div class="space-y-6">
								<!-- Address -->
								<Input
									type="text"
									label={$t('properties.address_label') || 'Address'}
									placeholder={$t('properties.address_placeholder') || 'Enter property address'}
									bind:value={propertyData.address}
									error={errors.address}
								/>

								<!-- City & District -->
								<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
									<Input
										type="text"
										label={$t('properties.city_label') || 'City'}
										placeholder={$t('properties.city_placeholder') || 'Enter city'}
										bind:value={propertyData.city}
										error={errors.city}
										required
									/>

									<Input
										type="text"
										label={$t('properties.district_label') || 'District'}
										placeholder={$t('properties.district_placeholder') || 'Enter district'}
										bind:value={propertyData.district}
										error={errors.district}
									/>
								</div>

								<!-- Country & Postal Code -->
								<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
									<Input
										type="text"
										label={$t('properties.country_label') || 'Country'}
										placeholder={$t('properties.country_placeholder') || 'Enter country'}
										bind:value={propertyData.country}
										error={errors.country}
									/>

									<Input
										type="text"
										label={$t('properties.postal_code_label') || 'Postal Code'}
										placeholder={$t('properties.postal_code_placeholder') || 'Enter postal code'}
										bind:value={propertyData.postal_code}
										error={errors.postal_code}
									/>
								</div>

								<!-- Map Location -->
								<div>
									<div class="mb-2 flex items-center justify-between">
										<!-- Fix: Changed from label to span to fix a11y warning -->
										<span class="block text-sm font-medium text-neutral-700 dark:text-neutral-300">
											{$t('properties.map_location') || 'Map Location'}
										</span>

										<Button
											variant="outline"
											size="sm"
											on:click={toggleLocationMap}
											aria-label={locationMapVisible
												? $t('general.hide') || 'Hide'
												: $t('general.show') || 'Show'}
										>
											{locationMapVisible
												? $t('general.hide') || 'Hide'
												: $t('general.show') || 'Show'}
										</Button>
									</div>

									{#if locationMapVisible}
										<div
											class="mt-2 overflow-hidden rounded-lg"
											transition:slide={{ duration: 300 }}
										>
											<PropertyMap
												height="400px"
												editable={true}
												location={propertyData.latitude && propertyData.longitude
													? { lat: propertyData.latitude, lng: propertyData.longitude }
													: null}
												on:locationSelected={handleLocationSelect}
											/>
										</div>
									{/if}

									<div class="mt-3 grid grid-cols-1 gap-4 md:grid-cols-2">
										<Input
											type="number"
											label={$t('properties.latitude_label') || 'Latitude'}
											placeholder={$t('properties.latitude_placeholder') || 'Enter latitude'}
											bind:value={propertyData.latitude}
											error={errors.latitude}
											step="0.000001"
										/>

										<Input
											type="number"
											label={$t('properties.longitude_label') || 'Longitude'}
											placeholder={$t('properties.longitude_placeholder') || 'Enter longitude'}
											bind:value={propertyData.longitude}
											error={errors.longitude}
											step="0.000001"
										/>
									</div>
								</div>
							</div>
						</div>
					{:else if activeTab === 'features'}
						<!-- Features Tab -->
						<div transition:fade={{ duration: 200 }}>
							<h2 class="mb-6 text-xl font-semibold text-neutral-900 dark:text-white">
								{$t('properties.create.features_info') || 'Features & Details'}
							</h2>

							<div class="space-y-6">
								<!-- Basic Features -->
								<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
									<Input
										type="number"
										label={$t('properties.bedrooms_label') || 'Bedrooms'}
										placeholder="0"
										bind:value={propertyData.bedrooms}
										error={errors.bedrooms}
										min="0"
										step="1"
									/>

									<Input
										type="number"
										label={$t('properties.bathrooms_label') || 'Bathrooms'}
										placeholder="0"
										bind:value={propertyData.bathrooms}
										error={errors.bathrooms}
										min="0"
										step="0.5"
									/>

									<Input
										type="number"
										label={$t('properties.area_label') || 'Area (m²)'}
										placeholder="0"
										bind:value={propertyData.area}
										error={errors.area}
										min="0"
										step="0.01"
									/>
								</div>

								<!-- Additional Numeric Features -->
								<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
									<Input
										type="number"
										label={$t('properties.year_built_label') || 'Year Built'}
										placeholder={$t('properties.year_built_placeholder') || 'YYYY'}
										bind:value={propertyData.year_built}
										error={errors.year_built}
										min="1800"
										max="2100"
										step="1"
									/>

									<Input
										type="number"
										label={$t('properties.floor_number_label') || 'Floor Number'}
										placeholder="0"
										bind:value={propertyData.floor_number}
										error={errors.floor_number}
										min="0"
										step="1"
									/>

									<Input
										type="number"
										label={$t('properties.parking_spaces_label') || 'Parking Spaces'}
										placeholder="0"
										bind:value={propertyData.parking_spaces}
										error={errors.parking_spaces}
										min="0"
										step="1"
									/>
								</div>

								<!-- Direction facing -->
								<Select
									label={$t('properties.facing_direction_label') || 'Facing Direction'}
									placeholder={$t('properties.facing_direction_placeholder') || 'Select direction'}
									options={facingDirectionOptions}
									bind:value={propertyData.facing_direction}
									error={errors.facing_direction}
								/>

								<!-- Toggle Features -->
								<div class="mt-6">
									<h3 class="mb-4 text-base font-medium text-neutral-900 dark:text-white">
										{$t('properties.amenities') || 'Amenities'}
									</h3>

									<div class="grid grid-cols-1 gap-y-4 md:grid-cols-2">
										<div class="flex items-center">
											<Switch
												bind:checked={propertyData.has_garden}
												label={$t('properties.amenities.garden') || 'Garden'}
											/>
										</div>

										<div class="flex items-center">
											<Switch
												bind:checked={propertyData.has_pool}
												label={$t('properties.amenities.pool') || 'Swimming Pool'}
											/>
										</div>

										<div class="flex items-center">
											<Switch
												bind:checked={propertyData.has_balcony}
												label={$t('properties.amenities.balcony') || 'Balcony'}
											/>
										</div>

										<div class="flex items-center">
											<Switch
												bind:checked={propertyData.has_elevator}
												label={$t('properties.amenities.elevator') || 'Elevator'}
											/>
										</div>

										<div class="flex items-center">
											<Switch
												bind:checked={propertyData.has_security}
												label={$t('properties.amenities.security') || 'Security System'}
											/>
										</div>
									</div>
								</div>

								<!-- Additional Features Component -->
								<PropertyFeaturesSelector on:update={handleFeaturesUpdate} />
							</div>
						</div>
					{:else if activeTab === 'media'}
						<!-- Media Tab -->
						<div transition:fade={{ duration: 200 }}>
							<h2 class="mb-6 text-xl font-semibold text-neutral-900 dark:text-white">
								{$t('properties.create.media_info') || 'Media & Images'}
							</h2>

							<div class="space-y-6">
								<PropertyMediaUploader
									images={propertyData.images}
									mainImage={propertyData.main_image}
									on:update={handleMediaUpdate}
								/>
							</div>
						</div>
					{:else if activeTab === 'pricing'}
						<!-- Pricing Tab -->
						<div transition:fade={{ duration: 200 }}>
							<h2 class="mb-6 text-xl font-semibold text-neutral-900 dark:text-white">
								{$t('properties.create.pricing_info') || 'Pricing Information'}
							</h2>

							<div class="space-y-6">
								<Input
									type="number"
									label={$t('properties.estimated_value_label') || 'Estimated Value'}
									placeholder="0.00"
									bind:value={propertyData.estimated_value}
									error={errors.estimated_value}
									min="0"
									step="0.01"
								/>

								<Alert type="info">
									<p>
										{$t('properties.create.pricing_note') ||
											'This value will be used as a reference for setting auction starting prices and property evaluations.'}
									</p>
								</Alert>
							</div>
						</div>
					{:else if activeTab === 'settings'}
						<!-- Settings Tab -->
						<div transition:fade={{ duration: 200 }}>
							<h2 class="mb-6 text-xl font-semibold text-neutral-900 dark:text-white">
								{$t('properties.create.settings_info') || 'Publication Settings'}
							</h2>

							<div class="space-y-6">
								<div class="flex items-center">
									<Switch
										bind:checked={propertyData.is_featured}
										label={$t('properties.is_featured_label') || 'Feature this property'}
									/>
								</div>

								<div class="flex items-center">
									<Switch
										bind:checked={propertyData.is_published}
										label={$t('properties.is_published_label') || 'Publish immediately'}
									/>
								</div>

								<Alert type="warning">
									<p>
										{$t('properties.create.publishing_note') ||
											'Publishing a property will make it visible to all users. Ensure all information is accurate before publishing.'}
									</p>
								</Alert>
							</div>
						</div>
					{/if}

					<!-- Navigation Buttons -->
					<div
						class="mt-8 flex justify-between border-t border-neutral-200 pt-6 dark:border-neutral-700"
					>
						<Button
							variant="outline"
							on:click={goToPreviousTab}
							disabled={tabs.findIndex((tab) => tab.id === activeTab) === 0 || submitting}
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="mr-1 h-5 w-5"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
							>
								<path d="m15 18-6-6 6-6" />
							</svg>
							{$t('general.previous') || 'Previous'}
						</Button>

						{#if tabs.findIndex((tab) => tab.id === activeTab) === tabs.length - 1}
							<Button
								variant="primary"
								on:click={handleSubmit}
								disabled={!canSubmit}
								loading={submitting}
							>
								{submitting
									? $t('properties.create.submitting') || 'Creating...'
									: $t('properties.create.submit') || 'Create Property'}
							</Button>
						{:else}
							<Button variant="primary" on:click={goToNextTab} disabled={submitting}>
								{$t('general.next') || 'Next'}
								<svg
									xmlns="http://www.w3.org/2000/svg"
									class="ml-1 h-5 w-5"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
									stroke-linejoin="round"
								>
									<path d="m9 18 6-6-6-6" />
								</svg>
							</Button>
						{/if}
					</div>
				</div>
			</Card>
		</div>
	</div>
</div>

<style>
	/* RTL support */
	.rtl {
		direction: rtl;
		text-align: right;
	}

	.rtl .ml-auto {
		margin-left: 0;
		margin-right: auto;
	}

	.rtl .mr-1,
	.rtl .mr-3 {
		margin-right: 0;
		margin-left: 0.25rem;
	}

	.rtl .ml-1 {
		margin-left: 0;
		margin-right: 0.25rem;
	}

	/* Smooth transitions between tabs */
	.property-create-form {
		min-height: 400px;
	}
</style>
