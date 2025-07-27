<!-- src/routes/property-management/properties/[id]/edit/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { t, locale } from '$lib/i18n';
	import { fade } from 'svelte/transition';
	import { user } from '$lib/stores/user.svelte.js';
	import { getProperty, updateProperty } from '$lib/api/property.js';

	import LoadingSpinner from '$lib/components/animations/LoadingSpinner.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';

	let propertyId = $derived($page.params.id);
	let isRTL = $derived($locale === 'ar');

	// State
	let property = $state(null);
	let loading = $state(true);
	let saving = $state(false);
	let error = $state(null);
	let validationErrors = $state({});
	let showUnsavedModal = $state(false);
	let hasUnsavedChanges = $state(false);

	// Form data - mapping to actual backend structure
	let formData = $state({
		title: '',
		description: '',
		property_type: '',
		size_sqm: '',
		bedrooms: '',
		bathrooms: '',
		floors: '',
		year_built: '',
		parking_spaces: '',
		market_value: '',
		location_data: {
			address: '',
			city: '',
			state: '',
			country: 'المملكة العربية السعودية',
			postal_code: '',
			latitude: null,
			longitude: null
		},
		features: [],
		amenities: [],
		is_featured: false,
		is_published: true
	});

	// Property type options
	const propertyTypeOptions = [
		{ value: 'apartment', label: $t('property.type.apartment') },
		{ value: 'villa', label: $t('property.type.villa') },
		{ value: 'commercial', label: $t('property.type.commercial') },
		{ value: 'land', label: $t('property.type.land') },
		{ value: 'warehouse', label: $t('property.type.warehouse') }
	];

	// Saudi cities for location selector
	const saudiCities = [
		'الرياض',
		'جدة',
		'مكة المكرمة',
		'المدينة المنورة',
		'الدمام',
		'الخبر',
		'الظهران',
		'تبوك',
		'بريدة',
		'خميس مشيط',
		'حفر الباطن',
		'الطائف',
		'الجبيل',
		'الخرج',
		'ينبع',
		'الأحساء',
		'القطيف',
		'عرعر',
		'سكاكا',
		'جيزان',
		'نجران',
		'الباحة',
		'القنفذة'
	];

	// Permissions
	let canEdit = $derived(
		$user && ($user.is_superuser || $user.is_staff || ['owner', 'appraiser'].includes($user.role))
	);

	onMount(() => {
		if (!canEdit) {
			goto('/property-management/properties');
			return;
		}
		loadProperty();
	});

	async function loadProperty() {
		try {
			loading = true;
			error = null;

			const response = await getProperty(propertyId);
			property = response;

			// Map backend data to form structure
			formData = {
				title: property.title || '',
				description: property.description || '',
				property_type: property.property_type || '',
				size_sqm: property.size_sqm || '',
				bedrooms: property.bedrooms || '',
				bathrooms: property.bathrooms || '',
				floors: property.floors || '',
				year_built: property.year_built || '',
				parking_spaces: property.parking_spaces || '',
				market_value: property.market_value || '',
				location_data: {
					address: property.location_data?.address || property.address || '',
					city: property.location_data?.city || '',
					state: property.location_data?.state || '',
					country: property.location_data?.country || 'المملكة العربية السعودية',
					postal_code: property.location_data?.postal_code || '',
					latitude: property.location_data?.latitude || null,
					longitude: property.location_data?.longitude || null
				},
				features: property.features || [],
				amenities: property.amenities || [],
				is_featured: property.is_featured || false,
				is_published: property.is_published !== false
			};
		} catch (err) {
			error = err.message || $t('error.fetchFailed');
			console.error('Failed to load property:', err);
		} finally {
			loading = false;
		}
	}

	async function handleSave() {
		try {
			saving = true;
			validationErrors = {};

			// Basic validation
			if (!formData.title?.trim()) {
				validationErrors.title = $t('validation.required');
			}
			if (!formData.description?.trim()) {
				validationErrors.description = $t('validation.required');
			}
			if (!formData.property_type) {
				validationErrors.property_type = $t('validation.required');
			}
			if (!formData.location_data.address?.trim()) {
				validationErrors.address = $t('validation.required');
			}
			if (!formData.location_data.city) {
				validationErrors.city = $t('validation.required');
			}

			if (Object.keys(validationErrors).length > 0) {
				saving = false;
				return;
			}

			// Convert numeric fields
			const updateData = {
				...formData,
				size_sqm: formData.size_sqm ? parseFloat(formData.size_sqm) : null,
				bedrooms: formData.bedrooms ? parseInt(formData.bedrooms) : null,
				bathrooms: formData.bathrooms ? parseFloat(formData.bathrooms) : null,
				floors: formData.floors ? parseInt(formData.floors) : null,
				year_built: formData.year_built ? parseInt(formData.year_built) : null,
				parking_spaces: formData.parking_spaces ? parseInt(formData.parking_spaces) : null,
				market_value: formData.market_value ? parseFloat(formData.market_value) : null,
				location_data: {
					...formData.location_data,
					latitude: formData.location_data.latitude
						? parseFloat(formData.location_data.latitude)
						: null,
					longitude: formData.location_data.longitude
						? parseFloat(formData.location_data.longitude)
						: null
				}
			};

			await updateProperty(propertyId, updateData);
			hasUnsavedChanges = false;
			goto(`/property-management/properties/${propertyId}`);
		} catch (err) {
			error = err.message || $t('error.saveFailed');
			console.error('Failed to update property:', err);
		} finally {
			saving = false;
		}
	}

	function handleCancel() {
		if (hasUnsavedChanges) {
			showUnsavedModal = true;
		} else {
			goto(`/property-management/properties/${propertyId}`);
		}
	}

	function handleDiscardChanges() {
		showUnsavedModal = false;
		hasUnsavedChanges = false;
		goto(`/property-management/properties/${propertyId}`);
	}

	function markAsChanged() {
		hasUnsavedChanges = true;
	}

	// Format date for display
	function formatDate(dateString) {
		if (!dateString) return '-';
		return new Date(dateString).toLocaleDateString($locale === 'ar' ? 'ar-SA' : 'en-US');
	}
</script>

<svelte:head>
	<title>
		{property?.title
			? `${$t('common.edit')} ${property.title} - ${$t('propertyManagement.propertyDetails')}`
			: $t('propertyManagement.editProperty')}
	</title>
</svelte:head>

<div
	class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-gray-900 dark:via-blue-900 dark:to-indigo-900"
	dir={isRTL ? 'rtl' : 'ltr'}
>
	<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
		<!-- Header -->
		<div class="mb-8">
			<div class="flex items-center justify-between">
				<div>
					<button
						onclick={() => goto(`/property-management/properties/${propertyId}`)}
						class="group mb-4 inline-flex items-center text-sm font-medium text-blue-600 transition-colors hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
					>
						<svg
							class="h-4 w-4 {isRTL
								? 'ml-2 rotate-180'
								: 'mr-2'} transition-transform group-hover:scale-110"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M10 19l-7-7m0 0l7-7m-7 7h18"
							/>
						</svg>
						{$t('propertyManagement.backToProperty')}
					</button>
					<h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">
						{$t('propertyManagement.editProperty')}
					</h1>
					<p class="mt-2 text-gray-600 dark:text-gray-400">
						{property?.title || $t('propertyManagement.editPropertyDescription')}
					</p>
				</div>

				<!-- Save Actions -->
				<div class="flex gap-3">
					<Button variant="outline" onclick={handleCancel} disabled={saving}>
						{$t('common.cancel')}
					</Button>
					<Button
						variant="primary"
						onclick={handleSave}
						disabled={saving || loading}
						class="min-w-[120px]"
					>
						{#if saving}
							<LoadingSpinner size="sm" color="white" class="mr-2" />
						{/if}
						{saving ? $t('common.saving') : $t('common.save')}
					</Button>
				</div>
			</div>
		</div>

		<!-- Loading State -->
		{#if loading && !property}
			<div class="flex flex-col items-center justify-center py-20">
				<LoadingSpinner size="lg" color="blue" />
				<p class="mt-4 text-gray-500 dark:text-gray-400">{$t('common.loading')}</p>
			</div>

			<!-- Error State -->
		{:else if error && !property}
			<div
				class="mx-auto max-w-3xl rounded-2xl border border-red-200 bg-red-50 p-8 text-red-800 dark:border-red-800 dark:bg-red-900/20 dark:text-red-200"
			>
				<div class="flex items-center">
					<svg
						class="mr-3 h-8 w-8 text-red-500"
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
					<div>
						<h2 class="mb-2 text-xl font-semibold">{$t('error.title')}</h2>
						<p class="text-base">{error}</p>
					</div>
				</div>
				<div class="mt-6 flex space-x-4">
					<Button variant="primary" onclick={loadProperty}>
						<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
							/>
						</svg>
						{$t('common.retry')}
					</Button>
					<Button variant="outline" onclick={() => goto('/property-management/properties')}>
						{$t('propertyManagement.backToProperties')}
					</Button>
				</div>
			</div>

			<!-- Edit Form -->
		{:else if property}
			<div class="space-y-8" transition:fade={{ duration: 300 }}>
				<!-- Basic Information -->
				<div
					class="rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
				>
					<div
						class="rounded-t-2xl bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-600 p-6 text-white"
					>
						<h2 class="flex items-center text-xl font-semibold">
							<svg class="mr-3 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
								/>
							</svg>
							{$t('propertyManagement.basicInformation')}
						</h2>
					</div>
					<div class="space-y-6 p-8">
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
									bind:value={formData.title}
									oninput={markAsChanged}
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100
										{validationErrors.title ? 'border-red-500 focus:ring-red-500' : ''}"
									placeholder={$t('property.titlePlaceholder')}
									required
								/>
								{#if validationErrors.title}
									<p class="mt-2 text-sm text-red-600 dark:text-red-400">
										{validationErrors.title}
									</p>
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
									bind:value={formData.property_type}
									onchange={markAsChanged}
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100
										{validationErrors.property_type ? 'border-red-500 focus:ring-red-500' : ''}"
									required
								>
									<option value="">{$t('property.selectType')}</option>
									{#each propertyTypeOptions as option}
										<option value={option.value}>{option.label}</option>
									{/each}
								</select>
								{#if validationErrors.property_type}
									<p class="mt-2 text-sm text-red-600 dark:text-red-400">
										{validationErrors.property_type}
									</p>
								{/if}
							</div>

							<!-- Market Value -->
							<div>
								<label
									for="market_value"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('property.marketValue')}
								</label>
								<input
									type="number"
									id="market_value"
									bind:value={formData.market_value}
									oninput={markAsChanged}
									min="0"
									step="1000"
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100"
									placeholder="500000"
								/>
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
								bind:value={formData.description}
								oninput={markAsChanged}
								rows="4"
								class="w-full resize-none rounded-xl border border-gray-300 bg-white px-4
									py-3 text-gray-900 transition-all
									duration-200 focus:border-transparent focus:ring-2 focus:ring-blue-500
									dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100
									{validationErrors.description ? 'border-red-500 focus:ring-red-500' : ''}"
								placeholder={$t('property.descriptionPlaceholder')}
								required
							></textarea>
							{#if validationErrors.description}
								<p class="mt-2 text-sm text-red-600 dark:text-red-400">
									{validationErrors.description}
								</p>
							{/if}
						</div>
					</div>
				</div>

				<!-- Location Information -->
				<div
					class="rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
				>
					<div
						class="rounded-t-2xl bg-gradient-to-r from-green-500 via-teal-500 to-cyan-600 p-6 text-white"
					>
						<h2 class="flex items-center text-xl font-semibold">
							<svg class="mr-3 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
							{$t('property.location')}
						</h2>
					</div>
					<div class="space-y-6 p-8">
						<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
							<!-- Address -->
							<div class="md:col-span-2">
								<label
									for="address"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('property.address')} <span class="text-red-500">*</span>
								</label>
								<input
									type="text"
									id="address"
									bind:value={formData.location_data.address}
									oninput={markAsChanged}
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100
										{validationErrors.address ? 'border-red-500 focus:ring-red-500' : ''}"
									placeholder={$t('property.addressPlaceholder')}
									required
								/>
								{#if validationErrors.address}
									<p class="mt-2 text-sm text-red-600 dark:text-red-400">
										{validationErrors.address}
									</p>
								{/if}
							</div>

							<!-- City -->
							<div>
								<label
									for="city"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('property.city')} <span class="text-red-500">*</span>
								</label>
								<select
									id="city"
									bind:value={formData.location_data.city}
									onchange={markAsChanged}
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100
										{validationErrors.city ? 'border-red-500 focus:ring-red-500' : ''}"
									required
								>
									<option value="">{$t('property.selectCity')}</option>
									{#each saudiCities as city}
										<option value={city}>{city}</option>
									{/each}
								</select>
								{#if validationErrors.city}
									<p class="mt-2 text-sm text-red-600 dark:text-red-400">{validationErrors.city}</p>
								{/if}
							</div>

							<!-- State -->
							<div>
								<label
									for="state"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('property.state')}
								</label>
								<input
									type="text"
									id="state"
									bind:value={formData.location_data.state}
									oninput={markAsChanged}
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100"
									placeholder={$t('property.statePlaceholder')}
								/>
							</div>

							<!-- Country -->
							<div>
								<label
									for="country"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('property.country')}
								</label>
								<input
									type="text"
									id="country"
									bind:value={formData.location_data.country}
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100"
									readonly
								/>
							</div>

							<!-- Postal Code -->
							<div>
								<label
									for="postal_code"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('property.postalCode')}
								</label>
								<input
									type="text"
									id="postal_code"
									bind:value={formData.location_data.postal_code}
									oninput={markAsChanged}
									pattern="[0-9]{5}"
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100"
									placeholder="12345"
								/>
							</div>
						</div>

						<!-- Coordinates -->
						<div class="border-t border-gray-200 pt-6 dark:border-gray-700">
							<h4 class="text-md mb-4 font-medium text-gray-900 dark:text-gray-100">
								{$t('property.coordinates')} ({$t('property.optional')})
							</h4>
							<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
								<!-- Latitude -->
								<div>
									<label
										for="latitude"
										class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
									>
										{$t('property.latitude')}
									</label>
									<input
										type="number"
										id="latitude"
										step="any"
										bind:value={formData.location_data.latitude}
										oninput={markAsChanged}
										class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
											text-gray-900 transition-all duration-200
											focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
											dark:bg-gray-700 dark:text-gray-100"
										placeholder="24.7136"
									/>
								</div>

								<!-- Longitude -->
								<div>
									<label
										for="longitude"
										class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
									>
										{$t('property.longitude')}
									</label>
									<input
										type="number"
										id="longitude"
										step="any"
										bind:value={formData.location_data.longitude}
										oninput={markAsChanged}
										class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
											text-gray-900 transition-all duration-200
											focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
											dark:bg-gray-700 dark:text-gray-100"
										placeholder="46.6753"
									/>
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Property Details -->
				<div
					class="rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
				>
					<div
						class="rounded-t-2xl bg-gradient-to-r from-purple-500 via-pink-500 to-red-500 p-6 text-white"
					>
						<h2 class="flex items-center text-xl font-semibold">
							<svg class="mr-3 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
								/>
							</svg>
							{$t('property.details')}
						</h2>
					</div>
					<div class="space-y-6 p-8">
						<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
							<!-- Size -->
							<div>
								<label
									for="size_sqm"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('property.size')} (m²)
								</label>
								<input
									type="number"
									id="size_sqm"
									bind:value={formData.size_sqm}
									oninput={markAsChanged}
									min="1"
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100"
									placeholder="150"
								/>
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
									bind:value={formData.bedrooms}
									oninput={markAsChanged}
									min="0"
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100"
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
									bind:value={formData.bathrooms}
									oninput={markAsChanged}
									min="0"
									step="0.5"
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100"
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
									bind:value={formData.floors}
									oninput={markAsChanged}
									min="1"
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100"
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
									bind:value={formData.year_built}
									oninput={markAsChanged}
									min="1800"
									max={new Date().getFullYear() + 1}
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100"
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
									bind:value={formData.parking_spaces}
									oninput={markAsChanged}
									min="0"
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100"
									placeholder="1"
								/>
							</div>
						</div>
					</div>
				</div>

				<!-- Publishing Options -->
				<div
					class="rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
				>
					<div
						class="rounded-t-2xl bg-gradient-to-r from-orange-500 via-yellow-500 to-red-500 p-6 text-white"
					>
						<h2 class="flex items-center text-xl font-semibold">
							<svg class="mr-3 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
								/>
							</svg>
							{$t('propertyManagement.publishingOptions')}
						</h2>
					</div>
					<div class="p-8">
						<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
							<!-- Published -->
							<div
								class="flex items-center justify-between rounded-xl bg-gray-50 p-4 dark:bg-gray-700"
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
										bind:checked={formData.is_published}
										onchange={markAsChanged}
										class="peer sr-only"
									/>
									<div
										class="peer h-6 w-11 rounded-full bg-gray-200 peer-checked:bg-blue-600 peer-focus:ring-4 peer-focus:ring-blue-300 peer-focus:outline-none after:absolute after:top-[2px] after:left-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:after:translate-x-full peer-checked:after:border-white dark:border-gray-600 dark:bg-gray-700 dark:peer-focus:ring-blue-800"
									></div>
								</label>
							</div>

							<!-- Featured -->
							<div
								class="flex items-center justify-between rounded-xl bg-gray-50 p-4 dark:bg-gray-700"
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
										bind:checked={formData.is_featured}
										onchange={markAsChanged}
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

				<!-- Save Actions Footer -->
				<div class="flex justify-end gap-4 border-t border-gray-200 pt-6 dark:border-gray-700">
					<Button variant="outline" onclick={handleCancel} disabled={saving} size="lg">
						{$t('common.cancel')}
					</Button>
					<Button
						variant="primary"
						onclick={handleSave}
						disabled={saving || loading}
						size="lg"
						class="min-w-[140px]"
					>
						{#if saving}
							<LoadingSpinner size="sm" color="white" class="mr-2" />
						{/if}
						{saving ? $t('common.saving') : $t('common.saveChanges')}
					</Button>
				</div>
			</div>
		{/if}
	</div>
</div>

<!-- Unsaved Changes Modal -->
<Modal bind:show={showUnsavedModal}>
	<div class="p-6">
		<div class="mb-4 flex items-center">
			<svg
				class="mr-3 h-8 w-8 text-yellow-500"
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
			<h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
				{$t('common.unsavedChanges')}
			</h3>
		</div>

		<p class="mb-6 text-gray-600 dark:text-gray-400">
			{$t('common.unsavedChangesMessage')}
		</p>

		<div class="flex justify-end gap-3">
			<Button variant="outline" onclick={() => (showUnsavedModal = false)}>
				{$t('common.keepEditing')}
			</Button>
			<Button variant="danger" onclick={handleDiscardChanges}>
				{$t('common.discardChanges')}
			</Button>
		</div>
	</div>
</Modal>

<style>
	/* Enhanced animations for property edit theme */
	:global(.property-edit-theme) {
		--primary-gradient: linear-gradient(135deg, #3b82f6 0%, #6366f1 50%, #8b5cf6 100%);
		--accent-color: #3b82f6;
		--accent-light: #dbeafe;
		--accent-dark: #1d4ed8;
	}

	/* Smooth transitions for better UX */
	* {
		transition: all 0.2s ease-in-out;
	}

	/* Custom gradient animations */
	@keyframes gradient-shift {
		0%,
		100% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 100% 50%;
		}
	}

	.bg-gradient-to-r {
		background-size: 200% 200%;
		animation: gradient-shift 8s ease infinite;
	}

	/* Form focus enhancements */
	input:focus,
	select:focus,
	textarea:focus {
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
		transform: translateY(-1px);
	}

	/* Custom toggle switch animations */
	input[type='checkbox']:checked + div {
		background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
	}
</style>
