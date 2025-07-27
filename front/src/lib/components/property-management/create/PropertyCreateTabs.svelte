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
							class="w-full rounded-2xl border border-gray-300 bg-white px-4 py-3 text-gray-900 placeholder-gray-500 shadow-md transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
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
							class="w-full rounded-2xl border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-md transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
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

					<!-- Property Status -->
					<div>
						<label
							for="property_status"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('property.status')}
						</label>
						<select
							id="property_status"
							bind:value={propertyData.property_status}
							class="w-full rounded-2xl border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-md transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
						>
							<option value="available">{$t('property.status.available')}</option>
							<option value="sold">{$t('property.status.sold')}</option>
							<option value="pending">{$t('property.status.pending')}</option>
							<option value="off_market">{$t('property.status.offMarket')}</option>
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
						class="w-full resize-none rounded-2xl border border-gray-300 bg-white px-4 py-3 text-gray-900 placeholder-gray-500 shadow-md transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
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
			<!-- Location Information with proper mapping -->
			<LocationSelector
				address={propertyData.location_data?.address || ''}
				city={propertyData.location_data?.city || ''}
				state={propertyData.location_data?.state || ''}
				postalCode={propertyData.location_data?.postal_code || ''}
				country={propertyData.location_data?.country || 'المملكة العربية السعودية'}
				latitude={propertyData.location_data?.latitude || null}
				longitude={propertyData.location_data?.longitude || null}
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
							class="w-full rounded-2xl border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-md transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
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
							class="w-full rounded-2xl border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-md transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
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
							class="w-full rounded-2xl border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-md transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
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
							class="w-full rounded-2xl border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-md transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
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
							class="w-full rounded-2xl border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-md transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
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
							class="w-full rounded-2xl border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-md transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
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

	<!-- Step 4: Property Value & Pricing -->
	{#if currentStep === 4}
		<div class="step-content p-8" transition:fade={{ duration: 300 }}>
			<div class="space-y-6">
				<!-- Property Valuation -->
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
								d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						{$t('property.valuationPricing')}
					</h3>
					<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
						<!-- Market Value -->
						<div>
							<label
								for="market_value"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('property.marketValue')} <span class="text-red-500">*</span>
							</label>
							<input
								type="number"
								id="market_value"
								bind:value={propertyData.market_value}
								min="0"
								step="10000"
								class="w-full rounded-2xl border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-md transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
								placeholder="500000"
								class:border-red-500={validationErrors.market_value}
							/>
							{#if validationErrors.market_value}
								<p class="mt-1 text-sm text-red-600 dark:text-red-400">
									{validationErrors.market_value}
								</p>
							{/if}
						</div>

						<!-- Purchase Price -->
						<div>
							<label
								for="purchase_price"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('property.purchasePrice')}
							</label>
							<input
								type="number"
								id="purchase_price"
								bind:value={propertyData.purchase_price}
								min="0"
								step="10000"
								class="w-full rounded-2xl border border-gray-300 bg-white px-4 py-3 text-gray-900 shadow-md transition-all duration-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
								placeholder="450000"
							/>
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
						{$t('property.photos')}
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
						{$t('property.summary')}
					</h3>
					<div
						class="rounded-2xl border border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50 p-6 shadow-md dark:border-gray-600 dark:from-gray-700 dark:to-blue-900/20"
					>
						<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
							<div>
								<h4 class="mb-3 font-medium text-gray-900 dark:text-white">
									{$t('property.basicInfo')}
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
									{$t('property.valueInfo')}
								</h4>
								<dl class="space-y-2 text-sm">
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">{$t('property.marketValue')}:</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{formatCurrency(propertyData.market_value) || '-'}
										</dd>
									</div>
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">
											{$t('property.purchasePrice')}:
										</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{formatCurrency(propertyData.purchase_price) || '-'}
										</dd>
									</div>
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">{$t('property.status')}:</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{$t(`property.status.${propertyData.property_status || 'available'}`)}
										</dd>
									</div>
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">{$t('property.featured')}:</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{propertyData.is_featured ? $t('common.yes') : $t('common.no')}
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
							class="mr-2 h-5 w-5 text-blue-500"
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
						{$t('property.publishingOptions')}
					</h3>
					<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
						<div
							class="flex items-center justify-between rounded-2xl border border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50 p-4 shadow-md dark:border-gray-600 dark:from-gray-700 dark:to-gray-600"
						>
							<div>
								<label
									for="is_published"
									class="text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('property.publishProperty')}
								</label>
								<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
									{$t('property.publishDescription')}
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
									class="peer h-6 w-11 rounded-full bg-gray-200 peer-checked:bg-blue-600 peer-focus:ring-4 peer-focus:ring-blue-300 peer-focus:outline-none after:absolute after:top-[2px] after:left-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:after:translate-x-full peer-checked:after:border-white dark:border-gray-600 dark:bg-gray-700 dark:peer-focus:ring-blue-800"
								></div>
							</label>
						</div>

						<div
							class="flex items-center justify-between rounded-2xl border border-yellow-200 bg-gradient-to-r from-yellow-50 to-orange-50 p-4 shadow-md dark:border-gray-600 dark:from-gray-700 dark:to-gray-600"
						>
							<div>
								<label
									for="is_featured"
									class="text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('property.featuredProperty')}
								</label>
								<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
									{$t('property.featuredDescription')}
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
		background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
	}

	/* Enhanced form field focus states */
	input:focus,
	select:focus,
	textarea:focus {
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
		border-color: #3b82f6;
	}
</style>
