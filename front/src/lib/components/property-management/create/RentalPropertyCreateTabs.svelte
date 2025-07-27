<!-- src/lib/components/property-management/create/PropertyCreateTabs.svelte -->
<script>
	import { t, locale } from '$lib/i18n';
	import { fade } from 'svelte/transition';
	import LocationSelector from '$lib/components/properties/create/LocationSelector.svelte';
	import MediaUploader from '$lib/components/properties/create/MediaUploader.svelte';
	import MultiSelect from '$lib/components/ui/MultiSelect.svelte';

	let {
		currentStep,
		propertyData,
		mediaFiles = [],
		validationErrors = {},
		availableFeatures = [],
		availableAmenities = [],
		propertyTypeOptions = [],
		onLocationChange,
		onFeaturesChange,
		onAmenitiesChange,
		onMediaChange
	} = $props();

	let isRTL = $derived($locale === 'ar');

	// Handle form field changes
	function handleFieldChange(field, value) {
		propertyData[field] = value;
	}

	// Handle features selection
	function handleFeaturesSelect(event) {
		onFeaturesChange?.(event);
	}

	// Handle amenities selection
	function handleAmenitiesSelect(event) {
		onAmenitiesChange?.(event);
	}

	// Format currency for display
	function formatCurrency(value) {
		if (!value) return '';
		return new Intl.NumberFormat($locale === 'ar' ? 'ar-SA' : 'en-US', {
			style: 'currency',
			currency: $locale === 'ar' ? 'SAR' : 'USD',
			minimumFractionDigits: 0
		}).format(value);
	}
</script>

<div
	class="rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
	dir={isRTL ? 'rtl' : 'ltr'}
>
	<!-- Step 1: Basic Information -->
	{#if currentStep === 1}
		<div class="step-content p-8" transition:fade={{ duration: 300 }}>
			<div class="space-y-6">
				<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
					<!-- Property Title -->
					<div class="lg:col-span-2">
						<label
							for="title"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('property.title')} <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							id="title"
							bind:value={propertyData.title}
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 placeholder-gray-500 transition-all duration-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
							placeholder={$t('property.titlePlaceholder')}
							class:border-red-500={validationErrors.title}
							class:ring-red-500={validationErrors.title}
						/>
						{#if validationErrors.title}
							<p class="mt-1 text-sm text-red-600 dark:text-red-400">{validationErrors.title}</p>
						{/if}
					</div>

					<!-- Property Type -->
					<div>
						<label
							for="property_type"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('property.type')} <span class="text-red-500">*</span>
						</label>
						<select
							id="property_type"
							bind:value={propertyData.property_type}
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
							class:border-red-500={validationErrors.property_type}
						>
							<option value="">{$t('property.selectType')}</option>
							{#each propertyTypeOptions as option}
								<option value={option.value}>{option.label}</option>
							{/each}
						</select>
						{#if validationErrors.property_type}
							<p class="mt-1 text-sm text-red-600 dark:text-red-400">
								{validationErrors.property_type}
							</p>
						{/if}
					</div>

					<!-- Building Type -->
					<div>
						<label
							for="building_type"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('property.buildingType')}
						</label>
						<select
							id="building_type"
							bind:value={propertyData.building_type}
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
						>
							<option value="">{$t('property.selectBuildingType')}</option>
							{#each buildingTypeOptions as option}
								<option value={option.value}>{option.label}</option>
							{/each}
						</select>
					</div>
				</div>

				<!-- Description -->
				<div>
					<label
						for="description"
						class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('property.description')} <span class="text-red-500">*</span>
					</label>
					<textarea
						id="description"
						bind:value={propertyData.description}
						rows="4"
						class="w-full resize-none rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 placeholder-gray-500 transition-all duration-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
						placeholder={$t('property.descriptionPlaceholder')}
						class:border-red-500={validationErrors.description}
					></textarea>
					{#if validationErrors.description}
						<p class="mt-1 text-sm text-red-600 dark:text-red-400">
							{validationErrors.description}
						</p>
					{/if}
				</div>
			</div>
		</div>
	{/if}

	<!-- Step 2: Location Information -->
	{#if currentStep === 2}
		<div class="step-content p-8" transition:fade={{ duration: 300 }}>
			<LocationSelector
				address={propertyData.address}
				city={propertyData.city}
				state={propertyData.state}
				postalCode={propertyData.postal_code}
				country={propertyData.country}
				latitude={propertyData.latitude}
				longitude={propertyData.longitude}
				{validationErrors}
				onChange={onLocationChange}
			/>
		</div>
	{/if}

	<!-- Step 3: Property Details -->
	{#if currentStep === 3}
		<div class="step-content p-8" transition:fade={{ duration: 300 }}>
			<div class="space-y-6">
				<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
					<!-- Size -->
					<div>
						<label
							for="size_sqm"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('property.size')} (m²) <span class="text-red-500">*</span>
						</label>
						<input
							type="number"
							id="size_sqm"
							bind:value={propertyData.size_sqm}
							min="1"
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
							placeholder="150"
							class:border-red-500={validationErrors.size_sqm}
						/>
						{#if validationErrors.size_sqm}
							<p class="mt-1 text-sm text-red-600 dark:text-red-400">{validationErrors.size_sqm}</p>
						{/if}
					</div>

					<!-- Bedrooms -->
					<div>
						<label
							for="bedrooms"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('property.bedrooms')}
						</label>
						<input
							type="number"
							id="bedrooms"
							bind:value={propertyData.bedrooms}
							min="0"
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
							placeholder="3"
						/>
					</div>

					<!-- Bathrooms -->
					<div>
						<label
							for="bathrooms"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('property.bathrooms')}
						</label>
						<input
							type="number"
							id="bathrooms"
							bind:value={propertyData.bathrooms}
							min="0"
							step="0.5"
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
							placeholder="2"
						/>
					</div>

					<!-- Floors -->
					<div>
						<label
							for="floors"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('property.floors')}
						</label>
						<input
							type="number"
							id="floors"
							bind:value={propertyData.floors}
							min="1"
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
							placeholder="1"
						/>
					</div>

					<!-- Year Built -->
					<div>
						<label
							for="year_built"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('property.yearBuilt')}
						</label>
						<input
							type="number"
							id="year_built"
							bind:value={propertyData.year_built}
							min="1800"
							max={new Date().getFullYear() + 1}
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
							placeholder="2020"
						/>
					</div>

					<!-- Parking Spaces -->
					<div>
						<label
							for="parking_spaces"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('property.parkingSpaces')}
						</label>
						<input
							type="number"
							id="parking_spaces"
							bind:value={propertyData.parking_spaces}
							min="0"
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
							placeholder="1"
						/>
					</div>
				</div>

				<!-- Features and Amenities -->
				<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
					<!-- Features -->
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
							{$t('property.features')}
						</label>
						<MultiSelect
							options={availableFeatures}
							selected={propertyData.features}
							placeholder={$t('property.selectFeatures')}
							onChange={handleFeaturesSelect}
						/>
					</div>

					<!-- Amenities -->
					<div>
						<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
							{$t('property.amenities')}
						</label>
						<MultiSelect
							options={availableAmenities}
							selected={propertyData.amenities}
							placeholder={$t('property.selectAmenities')}
							onChange={handleAmenitiesSelect}
						/>
					</div>
				</div>
			</div>
		</div>
	{/if}

	<!-- Step 4: Rental Information -->
	{#if currentStep === 4}
		<div class="step-content p-8" transition:fade={{ duration: 300 }}>
			<div class="space-y-6">
				<!-- Rental Pricing -->
				<div>
					<h3 class="mb-4 flex items-center text-lg font-semibold text-gray-900 dark:text-white">
						<svg
							class="mr-2 h-5 w-5 text-teal-500"
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
						{$t('propertyManagement.rentalPricing')}
					</h3>
					<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
						<!-- Monthly Rent -->
						<div>
							<label
								for="monthly_rent"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('propertyManagement.monthlyRent')} <span class="text-red-500">*</span>
							</label>
							<input
								type="number"
								id="monthly_rent"
								bind:value={propertyData.monthly_rent}
								min="0"
								step="100"
								class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
								placeholder="5000"
								class:border-red-500={validationErrors.monthly_rent}
							/>
							{#if validationErrors.monthly_rent}
								<p class="mt-1 text-sm text-red-600 dark:text-red-400">
									{validationErrors.monthly_rent}
								</p>
							{/if}
						</div>

						<!-- Security Deposit -->
						<div>
							<label
								for="security_deposit"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('propertyManagement.securityDeposit')}
							</label>
							<input
								type="number"
								id="security_deposit"
								bind:value={propertyData.security_deposit}
								min="0"
								step="100"
								class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
								placeholder="5000"
							/>
						</div>

						<!-- Lease Duration -->
						<div>
							<label
								for="lease_duration"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('propertyManagement.leaseDuration')} ({$t('propertyManagement.months')})
							</label>
							<select
								id="lease_duration"
								bind:value={propertyData.lease_duration_months}
								class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
							>
								<option value="6">6 {$t('propertyManagement.months')}</option>
								<option value="12">12 {$t('propertyManagement.months')}</option>
								<option value="18">18 {$t('propertyManagement.months')}</option>
								<option value="24">24 {$t('propertyManagement.months')}</option>
								<option value="36">36 {$t('propertyManagement.months')}</option>
							</select>
						</div>
					</div>
				</div>

				<!-- Property Policies -->
				<div>
					<h3 class="mb-4 flex items-center text-lg font-semibold text-gray-900 dark:text-white">
						<svg
							class="mr-2 h-5 w-5 text-blue-500"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						{$t('propertyManagement.propertyPolicies')}
					</h3>
					<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
						<!-- Available From -->
						<div>
							<label
								for="available_from"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('propertyManagement.availableFrom')}
							</label>
							<input
								type="date"
								id="available_from"
								bind:value={propertyData.available_from}
								class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
							/>
						</div>

						<!-- Pet Policy -->
						<div>
							<label
								for="pet_policy"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('propertyManagement.petPolicy')}
							</label>
							<select
								id="pet_policy"
								bind:value={propertyData.pet_policy}
								class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
							>
								{#each petPolicyOptions as option}
									<option value={option.value}>{option.label}</option>
								{/each}
							</select>
						</div>
					</div>
				</div>

				<!-- Utilities and Features -->
				<div>
					<h3 class="mb-4 flex items-center text-lg font-semibold text-gray-900 dark:text-white">
						<svg
							class="mr-2 h-5 w-5 text-purple-500"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M13 10V3L4 14h7v7l9-11h-7z"
							/>
						</svg>
						{$t('propertyManagement.utilitiesFeatures')}
					</h3>
					<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
						<!-- Utilities Included -->
						<div>
							<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
								{$t('propertyManagement.utilitiesIncluded')}
							</label>
							<MultiSelect
								options={utilitiesOptions.map((u) => u.label)}
								selected={propertyData.utilities_included}
								placeholder={$t('propertyManagement.selectUtilities')}
								onChange={(event) => handleUtilitiesSelect(event.detail)}
							/>
						</div>

						<!-- Furnished -->
						<div
							class="flex items-center justify-between rounded-lg bg-gray-50 p-4 dark:bg-gray-700"
						>
							<div>
								<label for="furnished" class="text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('propertyManagement.furnished')}
								</label>
								<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
									{$t('propertyManagement.furnishedDescription')}
								</p>
							</div>
							<label class="relative inline-flex cursor-pointer items-center">
								<input
									type="checkbox"
									id="furnished"
									bind:checked={propertyData.furnished}
									class="peer sr-only"
								/>
								<div
									class="peer h-6 w-11 rounded-full bg-gray-200 peer-checked:bg-teal-600 peer-focus:ring-4 peer-focus:ring-teal-300 peer-focus:outline-none after:absolute after:top-[2px] after:left-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:after:translate-x-full peer-checked:after:border-white dark:border-gray-600 dark:bg-gray-700 dark:peer-focus:ring-teal-800"
								></div>
							</label>
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}

	<!-- Step 5: Media & Review -->
	{#if currentStep === 5}
		<div class="step-content p-8" transition:fade={{ duration: 300 }}>
			<div class="space-y-8">
				<!-- Media Upload -->
				<div>
					<h3 class="mb-4 flex items-center text-lg font-semibold text-gray-900 dark:text-white">
						<svg
							class="mr-2 h-5 w-5 text-indigo-500"
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
						{$t('propertyManagement.photos')}
					</h3>
					<MediaUploader
						files={mediaFiles}
						onChange={onMediaChange}
						acceptedTypes="image/*,video/*"
						maxFiles={20}
						maxSize={10 * 1024 * 1024}
					/>
				</div>

				<!-- Property Summary -->
				<div>
					<h3 class="mb-4 flex items-center text-lg font-semibold text-gray-900 dark:text-white">
						<svg
							class="mr-2 h-5 w-5 text-green-500"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						{$t('propertyManagement.summary')}
					</h3>
					<div
						class="rounded-xl border border-gray-200 bg-gradient-to-r from-gray-50 to-blue-50 p-6 dark:border-gray-600 dark:from-gray-700 dark:to-blue-900/20"
					>
						<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
							<div>
								<h4 class="mb-3 font-medium text-gray-900 dark:text-white">
									{$t('propertyManagement.basicInfo')}
								</h4>
								<dl class="space-y-2 text-sm">
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">{$t('property.title')}:</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{propertyData.title || '-'}
										</dd>
									</div>
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">{$t('property.type')}:</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{propertyTypeOptions.find((p) => p.value === propertyData.property_type)
												?.label || '-'}
										</dd>
									</div>
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">{$t('property.size')}:</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{propertyData.size_sqm || '-'} m²
										</dd>
									</div>
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">{$t('property.bedrooms')}:</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{propertyData.bedrooms || '-'}
										</dd>
									</div>
								</dl>
							</div>
							<div>
								<h4 class="mb-3 font-medium text-gray-900 dark:text-white">
									{$t('propertyManagement.rentalInfo')}
								</h4>
								<dl class="space-y-2 text-sm">
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">
											{$t('propertyManagement.monthlyRent')}:
										</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{formatCurrency(propertyData.monthly_rent) || '-'}
										</dd>
									</div>
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">
											{$t('propertyManagement.securityDeposit')}:
										</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{formatCurrency(propertyData.security_deposit) || '-'}
										</dd>
									</div>
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">
											{$t('propertyManagement.leaseDuration')}:
										</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{propertyData.lease_duration_months || '-'}
											{$t('propertyManagement.months')}
										</dd>
									</div>
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">
											{$t('propertyManagement.furnished')}:
										</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{propertyData.furnished ? $t('common.yes') : $t('common.no')}
										</dd>
									</div>
								</dl>
							</div>
						</div>
					</div>
				</div>

				<!-- Publishing Options -->
				<div>
					<h3 class="mb-4 flex items-center text-lg font-semibold text-gray-900 dark:text-white">
						<svg
							class="mr-2 h-5 w-5 text-orange-500"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
							/>
						</svg>
						{$t('propertyManagement.publishingOptions')}
					</h3>
					<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
						<div
							class="flex items-center justify-between rounded-lg bg-gray-50 p-4 dark:bg-gray-700"
						>
							<div>
								<label
									for="is_published"
									class="text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('propertyManagement.publishProperty')}
								</label>
								<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
									{$t('propertyManagement.publishDescription')}
								</p>
							</div>
							<label class="relative inline-flex cursor-pointer items-center">
								<input
									type="checkbox"
									id="is_published"
									bind:checked={propertyData.is_published}
									class="peer sr-only"
								/>
								<div
									class="peer h-6 w-11 rounded-full bg-gray-200 peer-checked:bg-teal-600 peer-focus:ring-4 peer-focus:ring-teal-300 peer-focus:outline-none after:absolute after:top-[2px] after:left-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:after:translate-x-full peer-checked:after:border-white dark:border-gray-600 dark:bg-gray-700 dark:peer-focus:ring-teal-800"
								></div>
							</label>
						</div>

						<div
							class="flex items-center justify-between rounded-lg bg-gray-50 p-4 dark:bg-gray-700"
						>
							<div>
								<label
									for="is_featured"
									class="text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('propertyManagement.featuredProperty')}
								</label>
								<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
									{$t('propertyManagement.featuredDescription')}
								</p>
							</div>
							<label class="relative inline-flex cursor-pointer items-center">
								<input
									type="checkbox"
									id="is_featured"
									bind:checked={propertyData.is_featured}
									class="peer sr-only"
								/>
								<div
									class="peer h-6 w-11 rounded-full bg-gray-200 peer-checked:bg-orange-600 peer-focus:ring-4 peer-focus:ring-orange-300 peer-focus:outline-none after:absolute after:top-[2px] after:left-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:after:translate-x-full peer-checked:after:border-white dark:border-gray-600 dark:bg-gray-700 dark:peer-focus:ring-orange-800"
								></div>
							</label>
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	/* Step content animations */
	.step-content {
		animation: slide-up 0.3s ease-out;
	}

	@keyframes slide-up {
		from {
			opacity: 0;
			transform: translateY(20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	/* Custom toggle switch animations */
	input[type='checkbox']:checked + div {
		background: linear-gradient(135deg, #14b8a6 0%, #06b6d4 100%);
	}

	/* Enhanced form field focus states */
	input:focus,
	select:focus,
	textarea:focus {
		box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.1);
		border-color: #14b8a6;
	}
</style>
