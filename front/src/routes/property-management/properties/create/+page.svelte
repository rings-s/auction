<!-- src/routes/property-management/properties/create/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t, locale } from '$lib/i18n';
	import { fade } from 'svelte/transition';
	import { user } from '$lib/stores/user.svelte.js';
	import { createProperty } from '$lib/api/property.js';

	import LoadingSpinner from '$lib/components/animations/LoadingSpinner.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';

	let isRTL = $derived($locale === 'ar');

	// State
	let loading = $state(false);
	let error = $state(null);
	let validationErrors = $state({});
	let showUnsavedModal = $state(false);
	let hasUnsavedChanges = $state(false);
	let currentStep = $state(1);
	const totalSteps = 4;

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

	// Available features and amenities
	const availableFeatures = [
		'مكيف هواء',
		'تدفئة مركزية',
		'مسبح',
		'حديقة',
		'شرفة',
		'مطبخ مجهز',
		'خزائن مدمجة',
		'غرفة غسيل',
		'مخزن',
		'مصعد',
		'انترنت عالي السرعة',
		'أمان 24/7',
		'كاميرات مراقبة'
	];

	const availableAmenities = [
		'نادي رياضي',
		'حمام سباحة',
		'ملعب أطفال',
		'مسجد',
		'صيدلية',
		'سوبر ماركت',
		'مطاعم',
		'محلات تجارية',
		'موقف سيارات مغطى',
		'حديقة عامة',
		'مدارس قريبة',
		'مستشفى قريب',
		'محطات مواصلات'
	];

	// Permissions
	let canCreate = $derived(
		$user && ($user.is_superuser || $user.is_staff || ['owner', 'appraiser'].includes($user.role))
	);

	onMount(() => {
		if (!canCreate) {
			goto('/property-management/properties');
			return;
		}
	});

	// Step validation
	function validateStep(step) {
		const errors = {};

		if (step === 1) {
			if (!formData.title?.trim()) {
				errors.title = $t('validation.required');
			}
			if (!formData.description?.trim()) {
				errors.description = $t('validation.required');
			}
			if (!formData.property_type) {
				errors.property_type = $t('validation.required');
			}
		} else if (step === 2) {
			if (!formData.location_data.address?.trim()) {
				errors.address = $t('validation.required');
			}
			if (!formData.location_data.city) {
				errors.city = $t('validation.required');
			}
		}

		return errors;
	}

	function handleNext() {
		const errors = validateStep(currentStep);
		validationErrors = errors;

		if (Object.keys(errors).length === 0) {
			currentStep = Math.min(currentStep + 1, totalSteps);
		}
	}

	function handlePrevious() {
		currentStep = Math.max(currentStep - 1, 1);
	}

	function handleStepClick(step) {
		// Allow going back to previous steps, but validate forward movement
		if (step < currentStep) {
			currentStep = step;
		} else if (step === currentStep + 1) {
			handleNext();
		}
	}

	async function handleSave() {
		try {
			loading = true;
			validationErrors = {};

			// Validate all steps
			const step1Errors = validateStep(1);
			const step2Errors = validateStep(2);
			const allErrors = { ...step1Errors, ...step2Errors };

			if (Object.keys(allErrors).length > 0) {
				validationErrors = allErrors;
				currentStep = 1; // Go back to first step with errors
				loading = false;
				return;
			}

			// Convert numeric fields
			const createData = {
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

			const response = await createProperty(createData);
			hasUnsavedChanges = false;
			goto(`/property-management/properties/${response.id || response.data?.id}`);
		} catch (err) {
			error = err.message || $t('error.saveFailed');
			console.error('Failed to create property:', err);
		} finally {
			loading = false;
		}
	}

	function handleCancel() {
		if (hasUnsavedChanges) {
			showUnsavedModal = true;
		} else {
			goto('/property-management/properties');
		}
	}

	function handleDiscardChanges() {
		showUnsavedModal = false;
		hasUnsavedChanges = false;
		goto('/property-management/properties');
	}

	function markAsChanged() {
		hasUnsavedChanges = true;
	}

	function getStepIcon(step) {
		if (step < currentStep) {
			return '✓';
		} else if (step === currentStep) {
			return step;
		} else {
			return step;
		}
	}

	function getStepClass(step) {
		if (step < currentStep) {
			return 'bg-green-500 text-white';
		} else if (step === currentStep) {
			return 'bg-blue-500 text-white';
		} else {
			return 'bg-gray-300 text-gray-700 dark:bg-gray-600 dark:text-gray-300';
		}
	}
</script>

<svelte:head>
	<title
		>{$t('propertyManagement.createProperty')} - {$t(
			'propertyManagement.propertyManagement'
		)}</title
	>
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
						onclick={() => goto('/property-management/properties')}
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
						{$t('propertyManagement.backToProperties')}
					</button>
					<h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">
						{$t('propertyManagement.createProperty')}
					</h1>
					<p class="mt-2 text-gray-600 dark:text-gray-400">
						{$t('propertyManagement.createPropertyDescription')}
					</p>
				</div>

				<!-- Save Actions -->
				<div class="flex gap-3">
					<Button variant="outline" onclick={handleCancel} disabled={loading}>
						{$t('common.cancel')}
					</Button>
					<Button variant="primary" onclick={handleSave} disabled={loading} class="min-w-[120px]">
						{#if loading}
							<LoadingSpinner size="sm" color="white" class="mr-2" />
						{/if}
						{loading ? $t('common.creating') : $t('common.create')}
					</Button>
				</div>
			</div>
		</div>

		<!-- Permission Check -->
		{#if !canCreate}
			<div
				class="mx-auto max-w-3xl rounded-2xl border border-yellow-200 bg-yellow-50 p-8 text-yellow-800 dark:border-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-200"
			>
				<div class="flex items-center">
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
					<div>
						<h2 class="mb-2 text-xl font-semibold">{$t('error.accessDenied')}</h2>
						<p class="text-base">{$t('propertyManagement.noCreatePermission')}</p>
					</div>
				</div>
				<div class="mt-6">
					<Button variant="outline" onclick={() => goto('/property-management/properties')}>
						{$t('propertyManagement.backToProperties')}
					</Button>
				</div>
			</div>
		{:else}
			<!-- Progress Steps -->
			<div class="mb-8">
				<div
					class="rounded-2xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800"
				>
					<div class="flex items-center justify-between">
						{#each Array(totalSteps) as _, i}
							{@const step = i + 1}
							<div class="flex items-center">
								<!-- Step Circle -->
								<button
									onclick={() => handleStepClick(step)}
									class="flex h-10 w-10 items-center justify-center rounded-full text-sm font-medium transition-all duration-200
										{getStepClass(step)}
										{step <= currentStep ? 'cursor-pointer hover:scale-105' : 'cursor-default'}"
								>
									{getStepIcon(step)}
								</button>

								<!-- Step Label -->
								<div class="ml-3 {isRTL ? 'mr-3 ml-0' : ''}">
									<div class="text-sm font-medium text-gray-900 dark:text-gray-100">
										{#if step === 1}
											{$t('propertyManagement.basicInfo')}
										{:else if step === 2}
											{$t('property.location')}
										{:else if step === 3}
											{$t('property.details')}
										{:else if step === 4}
											{$t('propertyManagement.publishingOptions')}
										{/if}
									</div>
									<div class="text-xs text-gray-500 dark:text-gray-400">
										{$t('common.step')}
										{step}
										{$t('common.of')}
										{totalSteps}
									</div>
								</div>

								<!-- Connector Line -->
								{#if step < totalSteps}
									<div class="ml-4 flex-1 {isRTL ? 'mr-4 ml-0' : ''}">
										<div class="h-1 rounded-full bg-gray-200 dark:bg-gray-700">
											<div
												class="h-1 rounded-full bg-blue-500 transition-all duration-300"
												style="width: {step < currentStep ? '100%' : '0%'}"
											></div>
										</div>
									</div>
								{/if}
							</div>
						{/each}
					</div>
				</div>
			</div>

			<!-- Form Content -->
			<div class="space-y-8">
				<!-- Step 1: Basic Information -->
				{#if currentStep === 1}
					<div
						class="rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
						transition:fade={{ duration: 300 }}
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
				{/if}

				<!-- Step 2: Location Information -->
				{#if currentStep === 2}
					<div
						class="rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
						transition:fade={{ duration: 300 }}
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
										<p class="mt-2 text-sm text-red-600 dark:text-red-400">
											{validationErrors.city}
										</p>
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
				{/if}

				<!-- Step 3: Property Details -->
				{#if currentStep === 3}
					<div
						class="rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
						transition:fade={{ duration: 300 }}
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
				{/if}

				<!-- Step 4: Publishing Options -->
				{#if currentStep === 4}
					<div
						class="rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
						transition:fade={{ duration: 300 }}
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

							<!-- Property Summary Preview -->
							<div
								class="mt-8 rounded-xl border border-gray-200 bg-gradient-to-r from-gray-50 to-blue-50 p-6 dark:border-gray-600 dark:from-gray-700 dark:to-blue-900/20"
							>
								<h3
									class="mb-4 flex items-center text-lg font-semibold text-gray-900 dark:text-white"
								>
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
								<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
									<div>
										<h4 class="mb-3 font-medium text-gray-900 dark:text-white">
											{$t('propertyManagement.basicInfo')}
										</h4>
										<dl class="space-y-2 text-sm">
											<div class="flex justify-between">
												<dt class="text-gray-500 dark:text-gray-400">{$t('property.title')}:</dt>
												<dd class="font-medium text-gray-900 dark:text-white">
													{formData.title || '-'}
												</dd>
											</div>
											<div class="flex justify-between">
												<dt class="text-gray-500 dark:text-gray-400">{$t('property.type')}:</dt>
												<dd class="font-medium text-gray-900 dark:text-white">
													{propertyTypeOptions.find((p) => p.value === formData.property_type)
														?.label || '-'}
												</dd>
											</div>
											<div class="flex justify-between">
												<dt class="text-gray-500 dark:text-gray-400">{$t('property.size')}:</dt>
												<dd class="font-medium text-gray-900 dark:text-white">
													{formData.size_sqm || '-'} m²
												</dd>
											</div>
										</dl>
									</div>
									<div>
										<h4 class="mb-3 font-medium text-gray-900 dark:text-white">
											{$t('property.location')}
										</h4>
										<dl class="space-y-2 text-sm">
											<div class="flex justify-between">
												<dt class="text-gray-500 dark:text-gray-400">{$t('property.city')}:</dt>
												<dd class="font-medium text-gray-900 dark:text-white">
													{formData.location_data.city || '-'}
												</dd>
											</div>
											<div class="flex justify-between">
												<dt class="text-gray-500 dark:text-gray-400">
													{$t('propertyManagement.publishProperty')}:
												</dt>
												<dd class="font-medium text-gray-900 dark:text-white">
													{formData.is_published ? $t('common.yes') : $t('common.no')}
												</dd>
											</div>
											<div class="flex justify-between">
												<dt class="text-gray-500 dark:text-gray-400">
													{$t('propertyManagement.featuredProperty')}:
												</dt>
												<dd class="font-medium text-gray-900 dark:text-white">
													{formData.is_featured ? $t('common.yes') : $t('common.no')}
												</dd>
											</div>
										</dl>
									</div>
								</div>
							</div>
						</div>
					</div>
				{/if}

				<!-- Navigation Buttons -->
				<div
					class="flex items-center justify-between border-t border-gray-200 pt-6 dark:border-gray-700"
				>
					<Button
						variant="outline"
						onclick={handlePrevious}
						disabled={currentStep === 1 || loading}
					>
						<svg
							class="h-4 w-4 {isRTL ? 'ml-2 rotate-180' : 'mr-2'}"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M15 19l-7-7 7-7"
							/>
						</svg>
						{$t('common.previous')}
					</Button>

					<div class="flex gap-3">
						{#if currentStep < totalSteps}
							<Button variant="primary" onclick={handleNext} disabled={loading}>
								{$t('common.next')}
								<svg
									class="h-4 w-4 {isRTL ? 'mr-2 rotate-180' : 'ml-2'}"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M9 5l7 7-7 7"
									/>
								</svg>
							</Button>
						{:else}
							<Button
								variant="primary"
								onclick={handleSave}
								disabled={loading}
								size="lg"
								class="min-w-[140px]"
							>
								{#if loading}
									<LoadingSpinner size="sm" color="white" class="mr-2" />
								{/if}
								{loading ? $t('common.creating') : $t('common.createProperty')}
							</Button>
						{/if}
					</div>
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

<!-- Error Display -->
{#if error}
	<div
		class="fixed right-4 bottom-4 max-w-md rounded-lg border border-red-200 bg-red-50 p-4 shadow-lg"
	>
		<div class="flex items-center">
			<svg class="mr-2 h-5 w-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
				/>
			</svg>
			<div>
				<h4 class="text-sm font-semibold text-red-800">{$t('error.title')}</h4>
				<p class="text-sm text-red-700">{error}</p>
			</div>
		</div>
		<button
			onclick={() => (error = null)}
			class="absolute top-2 right-2 text-red-400 hover:text-red-600"
		>
			<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M6 18L18 6M6 6l12 12"
				/>
			</svg>
		</button>
	</div>
{/if}

<style>
	/* Enhanced animations for property create theme */
	:global(.property-create-theme) {
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
		animation: gradient-shift 10s ease infinite;
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

	/* Step progress animations */
	@keyframes step-complete {
		0% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.1);
		}
		100% {
			transform: scale(1);
		}
	}

	.step-complete {
		animation: step-complete 0.3s ease-in-out;
	}
</style>
