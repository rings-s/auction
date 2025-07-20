<!-- src/lib/components/properties/edit/PropertyEditTabs.svelte -->
<script>
	import { t, locale } from '$lib/i18n';
	import { fade } from 'svelte/transition';
	import LocationPicker from '$lib/components/properties/LocationPicker.svelte';
	import MediaUploader from '$lib/components/shared/MediaUploader.svelte';
	import RoomManager from '$lib/components/properties/RoomManager.svelte';
	import TagSelector from '$lib/components/ui/TagSelector.svelte';

	export let currentStep;
	export let propertyData;
	export let rooms;
	export let mediaFiles;
	export let existingMedia;
	export let validationErrors;
	export let availableFeatures;
	export let availableAmenities;
	export let availableRoomFeatures;
	export let propertyTypeOptions;
	export let buildingTypeOptions;
	export let onLocationChange;
	export let onFeaturesChange;
	export let onAmenitiesChange;
	export let onRoomsChange;
	export let onMediaChange;
	export let onDeleteMedia;

	// Constants
	const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

	// Status options
	$: statusOptions = [
		{ value: 'available', label: $t('property.statusTypes.available') },
		{ value: 'under_contract', label: $t('property.statusTypes.under_contract') },
		{ value: 'sold', label: $t('property.statusTypes.sold') },
		{ value: 'auction', label: $t('property.statusTypes.auction') }
	];

	function handleDeleteExistingMedia(mediaId) {
		if (onDeleteMedia) {
			onDeleteMedia(mediaId);
		}
	}
</script>

<!-- Tab Content Container -->
<div class="overflow-hidden rounded-b-xl bg-white shadow-md dark:bg-gray-800">
	<!-- Step 1: Basic Information -->
	<div
		id="tab-basic-info"
		class="p-8"
		style="display: {currentStep === 1 ? 'block' : 'none'}"
		transition:fade={{ duration: 200 }}
	>
		<div class="space-y-8">
			<div class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-6">
				<!-- Property Title -->
				<div class="sm:col-span-4">
					<label for="title" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
						{$t('property.title')} *
					</label>
					<div class="relative mt-1 rounded-md shadow-sm">
						<input
							type="text"
							id="title"
							bind:value={propertyData.title}
							class="focus:ring-primary-500 focus:border-primary-500 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white"
							class:border-red-500={validationErrors.title}
							placeholder={$t('property.titlePlaceholder')}
						/>
						{#if validationErrors.title}
							<div class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
								<svg class="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
									<path
										fill-rule="evenodd"
										d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
										clip-rule="evenodd"
									/>
								</svg>
							</div>
						{/if}
					</div>
					{#if validationErrors.title}
						<p class="mt-1 text-sm text-red-600 dark:text-red-500">{validationErrors.title}</p>
					{/if}
				</div>

				<!-- Property Status -->
				<div class="sm:col-span-2">
					<label for="status" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
						{$t('property.status')}
					</label>
					<div class="mt-1">
						<select
							id="status"
							bind:value={propertyData.status}
							class="focus:ring-primary-500 focus:border-primary-500 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white"
						>
							{#each statusOptions as option}
								<option value={option.value}>{option.label}</option>
							{/each}
						</select>
					</div>
				</div>

				<!-- Property Type -->
				<div class="sm:col-span-3">
					<label
						for="property_type"
						class="block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('property.propertyType')} *
					</label>
					<div class="relative mt-1 rounded-md shadow-sm">
						<select
							id="property_type"
							bind:value={propertyData.property_type}
							class="focus:ring-primary-500 focus:border-primary-500 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white"
							class:border-red-500={validationErrors.property_type}
						>
							<option value="">{$t('common.select')}</option>
							{#each propertyTypeOptions as option}
								<option value={option.value}>{option.label}</option>
							{/each}
						</select>
						{#if validationErrors.property_type}
							<div class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
								<svg class="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
									<path
										fill-rule="evenodd"
										d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
										clip-rule="evenodd"
									/>
								</svg>
							</div>
						{/if}
					</div>
					{#if validationErrors.property_type}
						<p class="mt-1 text-sm text-red-600 dark:text-red-500">
							{validationErrors.property_type}
						</p>
					{/if}
				</div>

				<!-- Building Type -->
				<div class="sm:col-span-3">
					<label
						for="building_type"
						class="block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('property.buildingType')}
					</label>
					<div class="mt-1">
						<select
							id="building_type"
							bind:value={propertyData.building_type}
							class="focus:ring-primary-500 focus:border-primary-500 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white"
						>
							<option value="">{$t('common.select')}</option>
							{#each buildingTypeOptions as option}
								<option value={option.value}>{option.label}</option>
							{/each}
						</select>
					</div>
				</div>

				<!-- Deed Number -->
				<div class="sm:col-span-3">
					<label
						for="deed_number"
						class="block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('property.deedNumber')} *
					</label>
					<div class="relative mt-1 rounded-md shadow-sm">
						<input
							type="text"
							id="deed_number"
							bind:value={propertyData.deed_number}
							class="focus:ring-primary-500 focus:border-primary-500 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white"
							class:border-red-500={validationErrors.deed_number}
							placeholder={$t('property.deedNumberPlaceholder')}
						/>
						{#if validationErrors.deed_number}
							<div class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
								<svg class="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
									<path
										fill-rule="evenodd"
										d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
										clip-rule="evenodd"
									/>
								</svg>
							</div>
						{/if}
					</div>
					{#if validationErrors.deed_number}
						<p class="mt-1 text-sm text-red-600 dark:text-red-500">
							{validationErrors.deed_number}
						</p>
					{/if}
					<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
						{$t('property.deedNumberHelp')}
					</p>
				</div>

				<!-- Slug (readonly) -->
				<div class="sm:col-span-3">
					<label for="slug" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
						{$t('property.slug')}
					</label>
					<div class="mt-1">
						<input
							type="text"
							id="slug"
							value={propertyData.slug || ''}
							readonly
							class="block w-full cursor-not-allowed rounded-md border-gray-300 bg-gray-100 shadow-sm sm:text-sm dark:border-gray-700 dark:bg-gray-700 dark:text-gray-400"
						/>
						<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
							{$t('property.slugHelp')}
						</p>
					</div>
				</div>

				<!-- Description -->
				<div class="sm:col-span-6">
					<label
						for="description"
						class="block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('property.description')} *
					</label>
					<div class="mt-1">
						<textarea
							id="description"
							bind:value={propertyData.description}
							rows="4"
							class="focus:ring-primary-500 focus:border-primary-500 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white"
							class:border-red-500={validationErrors.description}
							placeholder={$t('property.descriptionPlaceholder')}
						></textarea>
						{#if validationErrors.description}
							<p class="mt-1 text-sm text-red-600 dark:text-red-500">
								{validationErrors.description}
							</p>
						{/if}
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Step 2: Location Information -->
	<div
		id="tab-location"
		class="p-8"
		style="display: {currentStep === 2 ? 'block' : 'none'}"
		transition:fade={{ duration: 200 }}
	>
		<div class="space-y-8">
			<LocationPicker
				bind:address={propertyData.address}
				bind:city={propertyData.city}
				bind:state={propertyData.state}
				bind:postalCode={propertyData.postal_code}
				bind:country={propertyData.country}
				bind:latitude={propertyData.latitude}
				bind:longitude={propertyData.longitude}
				on:locationChange={onLocationChange}
			/>

			<div class="space-y-3">
				{#if validationErrors.address}
					<p class="text-sm text-red-600 dark:text-red-500">{validationErrors.address}</p>
				{/if}

				{#if validationErrors.city}
					<p class="text-sm text-red-600 dark:text-red-500">{validationErrors.city}</p>
				{/if}

				{#if validationErrors.state}
					<p class="text-sm text-red-600 dark:text-red-500">{validationErrors.state}</p>
				{/if}
			</div>
		</div>
	</div>

	<!-- Step 3: Property Details -->
	<div
		id="tab-details"
		class="p-8"
		style="display: {currentStep === 3 ? 'block' : 'none'}"
		transition:fade={{ duration: 200 }}
	>
		<div class="space-y-8">
			<div class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-6">
				<!-- Size -->
				<div class="sm:col-span-2">
					<label for="size_sqm" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
						{$t('property.size')} ({$t('property.sqm')}) *
					</label>
					<div class="relative mt-1 rounded-md shadow-sm">
						<input
							type="number"
							id="size_sqm"
							bind:value={propertyData.size_sqm}
							min="1"
							step="0.01"
							class="focus:ring-primary-500 focus:border-primary-500 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white"
							class:border-red-500={validationErrors.size_sqm}
						/>
						{#if validationErrors.size_sqm}
							<div class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
								<svg class="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
									<path
										fill-rule="evenodd"
										d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
										clip-rule="evenodd"
									/>
								</svg>
							</div>
						{/if}
					</div>
					{#if validationErrors.size_sqm}
						<p class="mt-1 text-sm text-red-600 dark:text-red-500">{validationErrors.size_sqm}</p>
					{/if}
				</div>

				<!-- Floors -->
				<div class="sm:col-span-2">
					<label for="floors" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
						{$t('property.floors')}
					</label>
					<div class="mt-1">
						<input
							type="number"
							id="floors"
							bind:value={propertyData.floors}
							min="1"
							step="1"
							class="focus:ring-primary-500 focus:border-primary-500 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white"
							class:border-red-500={validationErrors.floors}
						/>
						{#if validationErrors.floors}
							<p class="mt-1 text-sm text-red-600 dark:text-red-500">{validationErrors.floors}</p>
						{/if}
					</div>
				</div>

				<!-- Year Built -->
				<div class="sm:col-span-2">
					<label
						for="year_built"
						class="block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('property.yearBuilt')}
					</label>
					<div class="mt-1">
						<input
							type="number"
							id="year_built"
							bind:value={propertyData.year_built}
							min="1800"
							max="2025"
							step="1"
							class="focus:ring-primary-500 focus:border-primary-500 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white"
							class:border-red-500={validationErrors.year_built}
						/>
						{#if validationErrors.year_built}
							<p class="mt-1 text-sm text-red-600 dark:text-red-500">
								{validationErrors.year_built}
							</p>
						{/if}
					</div>
				</div>

				<!-- Features -->
				<div class="mt-2 sm:col-span-6">
					<TagSelector
						title={$t('property.features')}
						tags={availableFeatures}
						selectedTags={propertyData.features}
						on:change={onFeaturesChange}
						variant="pill"
					/>
				</div>

				<!-- Amenities -->
				<div class="mt-2 sm:col-span-6">
					<TagSelector
						title={$t('property.amenities')}
						tags={availableAmenities}
						selectedTags={propertyData.amenities}
						on:change={onAmenitiesChange}
						variant="pill"
					/>
				</div>

				<!-- Rooms -->
				<div class="mt-4 sm:col-span-6">
					<div class="rounded-lg bg-gray-50 p-6 shadow-inner dark:bg-gray-700">
						<RoomManager
							bind:rooms
							availableFeatures={availableRoomFeatures}
							on:change={onRoomsChange}
						/>
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Step 4: Financial Information & Media Upload -->
	<div
		id="tab-financial"
		class="p-8"
		style="display: {currentStep === 4 ? 'block' : 'none'}"
		transition:fade={{ duration: 200 }}
	>
		<div class="space-y-8">
			<div class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-6">
				<!-- Market Value -->
				<div class="sm:col-span-3">
					<label
						for="market_value"
						class="block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('property.marketValue')} *
					</label>
					<div class="relative mt-1 rounded-md shadow-sm">
						<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
							<span class="text-gray-500 sm:text-sm">$</span>
						</div>
						<input
							type="number"
							id="market_value"
							bind:value={propertyData.market_value}
							min="1"
							step="0.01"
							class="focus:ring-primary-500 focus:border-primary-500 block w-full rounded-md border-gray-300 pl-7 shadow-sm sm:text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white"
							class:border-red-500={validationErrors.market_value}
						/>
						{#if validationErrors.market_value}
							<div class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
								<svg class="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
									<path
										fill-rule="evenodd"
										d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
										clip-rule="evenodd"
									/>
								</svg>
							</div>
						{/if}
					</div>
					{#if validationErrors.market_value}
						<p class="mt-1 text-sm text-red-600 dark:text-red-500">
							{validationErrors.market_value}
						</p>
					{/if}
				</div>

				<!-- Minimum Bid -->
				<div class="sm:col-span-3">
					<label
						for="minimum_bid"
						class="block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('property.minimumBid')}
					</label>
					<div class="relative mt-1 rounded-md shadow-sm">
						<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
							<span class="text-gray-500 sm:text-sm">$</span>
						</div>
						<input
							type="number"
							id="minimum_bid"
							bind:value={propertyData.minimum_bid}
							min="1"
							step="0.01"
							class="focus:ring-primary-500 focus:border-primary-500 block w-full rounded-md border-gray-300 pl-7 shadow-sm sm:text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white"
							class:border-red-500={validationErrors.minimum_bid}
						/>
					</div>
					{#if validationErrors.minimum_bid}
						<p class="mt-1 text-sm text-red-600 dark:text-red-500">
							{validationErrors.minimum_bid}
						</p>
					{/if}
				</div>

				<!-- Publishing Options -->
				<div class="sm:col-span-6">
					<fieldset
						class="dark:to-gray-750 rounded-lg bg-gradient-to-br from-gray-50 to-white p-6 shadow-sm dark:from-gray-700"
					>
						<legend
							class="rounded-md border border-gray-200 bg-white px-3 py-1 text-base font-medium text-gray-700 shadow-sm dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300"
						>
							{$t('property.publishingOptions')}
						</legend>
						<div class="mt-4 space-y-4">
							<div class="flex items-start">
								<div class="flex h-5 items-center">
									<input
										id="is_published"
										type="checkbox"
										bind:checked={propertyData.is_published}
										class="focus:ring-primary-500 text-primary-600 h-5 w-5 rounded border-gray-300 dark:border-gray-600 dark:bg-gray-700"
									/>
								</div>
								<div class="ml-3 text-sm">
									<label for="is_published" class="font-medium text-gray-700 dark:text-gray-300">
										{$t('property.published')}
									</label>
									<p class="text-gray-500 dark:text-gray-400">
										{$t('property.publishedHelp')}
									</p>
								</div>
							</div>

							<div class="flex items-start">
								<div class="flex h-5 items-center">
									<input
										id="is_featured"
										type="checkbox"
										bind:checked={propertyData.is_featured}
										class="focus:ring-primary-500 text-primary-600 h-5 w-5 rounded border-gray-300 dark:border-gray-600 dark:bg-gray-700"
									/>
								</div>
								<div class="ml-3 text-sm">
									<label for="is_featured" class="font-medium text-gray-700 dark:text-gray-300">
										{$t('property.featured')}
									</label>
									<p class="text-gray-500 dark:text-gray-400">
										{$t('property.featuredHelp')}
									</p>
								</div>
							</div>
						</div>
					</fieldset>
				</div>

				<!-- Existing Media -->
				{#if existingMedia && existingMedia.length > 0}
					<div class="sm:col-span-6">
						<div
							class="dark:to-gray-750 rounded-lg bg-gradient-to-br from-gray-50 to-white p-6 shadow-sm dark:from-gray-700"
						>
							<h3 class="mb-4 flex items-center text-lg font-medium text-gray-900 dark:text-white">
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
										d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
									></path>
								</svg>
								{$t('property.existingMedia')}
							</h3>

							<div class="grid grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-6">
								{#each existingMedia as media}
									<div class="group relative">
										<div
											class="aspect-w-1 aspect-h-1 overflow-hidden rounded-lg bg-gray-200 dark:bg-gray-600"
										>
											{#if media.media_type === 'image'}
												<img src={media.url} alt={media.name} class="h-full w-full object-cover" />
											{:else}
												<div class="flex h-full items-center justify-center">
													<svg
														class="h-8 w-8 text-gray-400"
														fill="none"
														stroke="currentColor"
														viewBox="0 0 24 24"
													>
														<path
															stroke-linecap="round"
															stroke-linejoin="round"
															stroke-width="2"
															d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
														></path>
													</svg>
												</div>
											{/if}
										</div>

										<!-- Delete button -->
										<button
											type="button"
											on:click={() => handleDeleteExistingMedia(media.id)}
											class="absolute top-2 right-2 rounded-full bg-red-600 p-1 text-white opacity-0 shadow-lg transition-opacity group-hover:opacity-100 hover:bg-red-700"
										>
											<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M6 18L18 6M6 6l12 12"
												></path>
											</svg>
										</button>

										<p class="mt-2 truncate text-xs text-gray-600 dark:text-gray-400">
											{media.name}
										</p>
									</div>
								{/each}
							</div>
						</div>
					</div>
				{/if}

				<!-- New Media Upload -->
				<div class="mt-2 sm:col-span-6">
					<div
						class="dark:to-gray-750 rounded-lg bg-gradient-to-br from-gray-50 to-white p-6 shadow-sm dark:from-gray-700"
					>
						<h3 class="flex items-center text-lg font-medium text-gray-900 dark:text-white">
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
									d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
								></path>
							</svg>
							{$t('property.addNewMedia')}
						</h3>
						<p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
							{$t('property.mediaUploadDesc')}
						</p>

						<div class="mt-4">
							<MediaUploader
								maxFiles={10}
								maxSize={MAX_FILE_SIZE}
								allowedTypes={['image/jpeg', 'image/png', 'image/gif', 'application/pdf']}
								on:change={onMediaChange}
							/>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
