<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t, locale } from '$lib/i18n';
	import { fade, slide } from 'svelte/transition';
	import { user } from '$lib/stores/user.svelte.js';
	import { getProperties } from '$lib/api/property.js';
	import { tenantsAPI, leasesAPI } from '$lib/api/propertyManagement.js';

	import LoadingSpinner from '$lib/components/animations/LoadingSpinner.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';

	let isRTL = $derived($locale === 'ar');

	// State using Svelte 5 runes
	let loading = $state(false);
	let saving = $state(false);
	let error = $state('');
	let validationErrors = $state({});
	let showUnsavedModal = $state(false);
	let hasUnsavedChanges = $state(false);
	let currentStep = $state(1);
	const totalSteps = 5;

	// Data
	let properties = $state([]);
	let tenants = $state([]);
	let uploadedFiles = $state({
		leaseAgreement: null,
		tenantId: null,
		incomeProof: null
	});

	// Form data using Svelte 5 state
	let formData = $state({
		// Step 1: Property Selection
		property: {
			id: '',
			title: '',
			address: '',
			type: ''
		},
		// Step 2: Tenant Information
		tenant: {
			id: '',
			firstName: '',
			lastName: '',
			email: '',
			phone: '',
			emergencyContact: '',
			employmentStatus: '',
			monthlyIncome: ''
		},
		// Step 3: Lease Terms
		leaseTerms: {
			startDate: '',
			endDate: '',
			rentAmount: '',
			securityDeposit: '',
			leaseType: 'fixed',
			petPolicy: 'no-pets',
			renewalOption: false
		},
		// Step 4: Financial Details
		financial: {
			rentDueDate: '1',
			lateFee: '',
			paymentMethod: 'bank-transfer',
			utilities: [],
			additionalFees: ''
		},
		// Step 5: Documents & Terms
		documents: {
			specialTerms: '',
			maintenanceResponsibility: 'tenant',
			parkingIncluded: false,
			smokingAllowed: false
		}
	});

	// Steps configuration
	const steps = [
		{
			id: 1,
			title: $t('lease.steps.property'),
			description: $t('lease.steps.propertyDesc'),
			icon: '🏠',
			fields: ['property']
		},
		{
			id: 2,
			title: $t('lease.steps.tenant'),
			description: $t('lease.steps.tenantDesc'),
			icon: '👤',
			fields: ['tenant']
		},
		{
			id: 3,
			title: $t('lease.steps.terms'),
			description: $t('lease.steps.termsDesc'),
			icon: '📋',
			fields: ['leaseTerms']
		},
		{
			id: 4,
			title: $t('lease.steps.financial'),
			description: $t('lease.steps.financialDesc'),
			icon: '💰',
			fields: ['financial']
		},
		{
			id: 5,
			title: $t('lease.steps.documents'),
			description: $t('lease.steps.documentsDesc'),
			icon: '📄',
			fields: ['documents']
		}
	];

	// Utility options
	const utilitiesOptions = [
		'water',
		'electricity',
		'gas',
		'internet',
		'cable',
		'trash',
		'heating',
		'airConditioning'
	];

	// Permission check
	let canCreate = $derived(
		$user && ($user.is_superuser || $user.is_staff || ['owner', 'appraiser'].includes($user.role))
	);

	onMount(() => {
		if (!canCreate) {
			goto('/property-management/leases');
			return;
		}
		loadInitialData();
	});

	async function loadInitialData() {
		try {
			loading = true;

			// Load properties and tenants in parallel
			const [propertiesResponse, tenantsResponse] = await Promise.all([
				getProperties({ page_size: 100 }),
				tenantsAPI.getAll({ page_size: 100 })
			]);

			// Handle properties response
			if (propertiesResponse.results) {
				properties = propertiesResponse.results;
			} else if (Array.isArray(propertiesResponse)) {
				properties = propertiesResponse;
			} else {
				properties = propertiesResponse.data?.results || [];
			}

			// Handle tenants response
			if (tenantsResponse.data?.results) {
				tenants = tenantsResponse.data.results;
			} else if (Array.isArray(tenantsResponse)) {
				tenants = tenantsResponse;
			} else {
				tenants = [];
			}
		} catch (err) {
			error = err.message || $t('errors.loadingFailed');
			console.error('Failed to load initial data:', err);
		} finally {
			loading = false;
		}
	}

	// Step validation
	function validateStep(step) {
		const errors = {};

		if (step === 1) {
			if (!formData.property.id) {
				errors.property = $t('validation.required');
			}
		} else if (step === 2) {
			if (!formData.tenant.firstName?.trim()) {
				errors.firstName = $t('validation.required');
			}
			if (!formData.tenant.lastName?.trim()) {
				errors.lastName = $t('validation.required');
			}
			if (!formData.tenant.email?.trim()) {
				errors.email = $t('validation.required');
			} else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.tenant.email)) {
				errors.email = $t('validation.invalidEmail');
			}
		} else if (step === 3) {
			if (!formData.leaseTerms.startDate) {
				errors.startDate = $t('validation.required');
			}
			if (!formData.leaseTerms.endDate) {
				errors.endDate = $t('validation.required');
			}
			if (!formData.leaseTerms.rentAmount) {
				errors.rentAmount = $t('validation.required');
			}
			if (formData.leaseTerms.startDate && formData.leaseTerms.endDate) {
				const startDate = new Date(formData.leaseTerms.startDate);
				const endDate = new Date(formData.leaseTerms.endDate);
				if (startDate >= endDate) {
					errors.endDate = $t('validation.endDateAfterStart');
				}
			}
		} else if (step === 4) {
			if (!formData.financial.rentDueDate) {
				errors.rentDueDate = $t('validation.required');
			}
			if (!formData.financial.paymentMethod) {
				errors.paymentMethod = $t('validation.required');
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
		if (step <= currentStep) {
			currentStep = step;
		} else if (step === currentStep + 1) {
			handleNext();
		}
	}

	function markAsChanged() {
		hasUnsavedChanges = true;
	}

	function handlePropertySelect(property) {
		formData.property = {
			id: property.id,
			title: property.title,
			address: property.location_data
				? `${property.location_data.city}, ${property.location_data.state}`
				: property.address,
			type: property.property_type
		};
		markAsChanged();
	}

	function handleTenantSelect(tenant) {
		formData.tenant = {
			id: tenant.id,
			firstName: tenant.name?.split(' ')[0] || '',
			lastName: tenant.name?.split(' ').slice(1).join(' ') || '',
			email: tenant.email || '',
			phone: tenant.phone || '',
			emergencyContact: tenant.emergency_contact || '',
			employmentStatus: '',
			monthlyIncome: ''
		};
		markAsChanged();
	}

	function handleUtilityToggle(utility) {
		const utilities = formData.financial.utilities.includes(utility)
			? formData.financial.utilities.filter((u) => u !== utility)
			: [...formData.financial.utilities, utility];
		formData.financial.utilities = utilities;
		markAsChanged();
	}

	function handleFileUpload(event, type) {
		const file = event.target.files?.[0];
		if (file) {
			uploadedFiles[type] = file;
			markAsChanged();
		}
	}

	async function handleSave() {
		try {
			saving = true;
			validationErrors = {};

			// Validate all steps
			for (let i = 1; i <= totalSteps - 1; i++) {
				const stepErrors = validateStep(i);
				if (Object.keys(stepErrors).length > 0) {
					validationErrors = stepErrors;
					currentStep = i;
					saving = false;
					return;
				}
			}

			// Prepare lease data for backend
			const leaseData = {
				property: formData.property.id,
				tenant_name: `${formData.tenant.firstName} ${formData.tenant.lastName}`,
				tenant_email: formData.tenant.email,
				tenant_phone: formData.tenant.phone,
				emergency_contact: formData.tenant.emergencyContact,
				start_date: formData.leaseTerms.startDate,
				end_date: formData.leaseTerms.endDate,
				monthly_rent: parseFloat(formData.leaseTerms.rentAmount),
				security_deposit: formData.leaseTerms.securityDeposit
					? parseFloat(formData.leaseTerms.securityDeposit)
					: null,
				lease_type: formData.leaseTerms.leaseType,
				pet_policy: formData.leaseTerms.petPolicy,
				rent_due_date: parseInt(formData.financial.rentDueDate),
				late_fee: formData.financial.lateFee ? parseFloat(formData.financial.lateFee) : null,
				payment_method: formData.financial.paymentMethod,
				utilities_included: formData.financial.utilities,
				special_terms: formData.documents.specialTerms,
				maintenance_responsibility: formData.documents.maintenanceResponsibility,
				parking_included: formData.documents.parkingIncluded,
				smoking_allowed: formData.documents.smokingAllowed,
				status: 'active'
			};

			const response = await leasesAPI.create(leaseData);
			hasUnsavedChanges = false;
			goto(`/property-management/leases/${response.data?.id || response.id}`);
		} catch (err) {
			error = err.message || $t('error.saveFailed');
			console.error('Failed to create lease:', err);
		} finally {
			saving = false;
		}
	}

	function handleCancel() {
		if (hasUnsavedChanges) {
			showUnsavedModal = true;
		} else {
			goto('/property-management/leases');
		}
	}

	function handleDiscardChanges() {
		showUnsavedModal = false;
		hasUnsavedChanges = false;
		goto('/property-management/leases');
	}

	function getStepIcon(step) {
		if (step < currentStep) return '✓';
		return step;
	}

	function getStepClass(step) {
		if (step < currentStep) return 'bg-green-500 text-white';
		if (step === currentStep) return 'bg-blue-500 text-white';
		return 'bg-gray-300 text-gray-700 dark:bg-gray-600 dark:text-gray-300';
	}

	function isStepComplete(step) {
		const errors = validateStep(step);
		return Object.keys(errors).length === 0;
	}
</script>

<svelte:head>
	<title>{$t('lease.createTitle')} | {$t('propertyManagement.title')} | {$t('app.name')}</title>
	<meta name="description" content={$t('lease.createDescription')} />
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
						onclick={() => goto('/property-management/leases')}
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
						{$t('lease.backToLeases')}
					</button>
					<h1
						class="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-4xl font-bold text-transparent"
					>
						{$t('lease.createNewLease')}
					</h1>
					<p class="mt-2 text-gray-600 dark:text-gray-400">
						{$t('lease.createDescription')}
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
						class="min-w-[120px] bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
					>
						{#if saving}
							<LoadingSpinner size="sm" color="white" class="mr-2" />
						{/if}
						{saving ? $t('common.creating') : $t('lease.generateLease')}
					</Button>
				</div>
			</div>
		</div>

		<!-- Permission Check -->
		{#if !canCreate}
			<div
				class="mx-auto max-w-3xl rounded-2xl border border-yellow-200 bg-yellow-50 p-8 text-yellow-800 shadow-xl dark:border-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-200"
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
						<p class="text-base">{$t('lease.noCreatePermission')}</p>
					</div>
				</div>
			</div>
		{:else}
			<div class="grid grid-cols-1 gap-8 lg:grid-cols-4">
				<!-- Sidebar - Progress Steps -->
				<div class="lg:col-span-1">
					<div
						class="sticky top-4 rounded-2xl border border-gray-200 bg-white p-6 shadow-xl dark:border-gray-700 dark:bg-gray-800"
					>
						<h2 class="mb-6 text-xl font-semibold text-gray-900 dark:text-white">
							{$t('lease.progress')}
						</h2>
						<div class="space-y-4">
							{#each steps as step}
								<div
									class="group flex cursor-pointer items-start space-x-3 rounded-xl p-3 transition-all duration-300
										{currentStep === step.id
										? 'border border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-900/20'
										: ''}
										{step.id < currentStep ? 'bg-green-50 dark:bg-green-900/20' : ''}
										hover:bg-gray-50 dark:hover:bg-gray-700"
									onclick={() => handleStepClick(step.id)}
								>
									<div
										class="flex h-10 w-10 items-center justify-center rounded-full border-2 transition-all duration-200 group-hover:scale-105
										{getStepClass(step.id)}"
									>
										<span class="text-sm font-medium">
											{step.id < currentStep ? '✓' : step.icon}
										</span>
									</div>
									<div class="min-w-0 flex-1">
										<p class="text-sm font-medium text-gray-900 dark:text-white">
											{step.title}
										</p>
										<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
											{step.description}
										</p>
									</div>
								</div>
							{/each}
						</div>

						<!-- Progress Bar -->
						<div class="mt-6 border-t border-gray-200 pt-6 dark:border-gray-700">
							<div
								class="mb-2 flex items-center justify-between text-sm text-gray-600 dark:text-gray-400"
							>
								<span>{$t('common.progress')}</span>
								<span>{Math.round((currentStep / totalSteps) * 100)}%</span>
							</div>
							<div class="h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
								<div
									class="h-2 rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-500"
									style="width: {(currentStep / totalSteps) * 100}%"
								></div>
							</div>
						</div>
					</div>
				</div>

				<!-- Main Content -->
				<div class="lg:col-span-3">
					<!-- Error Display -->
					{#if error}
						<div
							class="mb-8 rounded-2xl border border-red-200 bg-red-50 p-6 shadow-lg dark:border-red-800 dark:bg-red-900/20"
						>
							<div class="flex items-center">
								<svg
									class="mr-3 h-6 w-6 text-red-500"
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
									<h3 class="mb-1 text-lg font-semibold text-red-800 dark:text-red-200">
										{$t('error.title')}
									</h3>
									<p class="text-red-700 dark:text-red-300">{error}</p>
								</div>
							</div>
						</div>
					{/if}

					<div class="space-y-8">
						<!-- Step 1: Property Selection -->
						{#if currentStep === 1}
							<div
								class="rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
								transition:fade={{ duration: 300 }}
							>
								<div
									class="rounded-t-2xl bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-600 p-6 text-white"
								>
									<h2 class="flex items-center text-2xl font-semibold">
										<span class="mr-3 text-3xl">🏠</span>
										{$t('lease.selectProperty')}
									</h2>
									<p class="mt-2 text-blue-100">{$t('lease.selectPropertyDesc')}</p>
								</div>
								<div class="p-8">
									{#if loading}
										<div class="space-y-4">
											{#each Array(3) as _}
												<div
													class="h-20 animate-pulse rounded-xl bg-gray-200 dark:bg-gray-700"
												></div>
											{/each}
										</div>
									{:else if properties.length === 0}
										<div class="py-12 text-center">
											<div class="mb-4 text-6xl">🏠</div>
											<h3 class="mb-2 text-xl font-semibold text-gray-700 dark:text-gray-300">
												{$t('property.noPropertiesAvailable')}
											</h3>
											<p class="mb-6 text-gray-500 dark:text-gray-400">
												{$t('lease.addPropertyFirst')}
											</p>
											<Button
												variant="primary"
												onclick={() => goto('/property-management/properties/create')}
											>
												{$t('property.create')}
											</Button>
										</div>
									{:else}
										<div class="grid gap-4">
											{#each properties as property}
												<div
													class="cursor-pointer rounded-xl border-2 p-6 transition-all duration-200 hover:shadow-lg
														{formData.property.id === property.id
														? 'border-blue-500 bg-blue-50 shadow-lg dark:bg-blue-900/20'
														: 'border-gray-200 hover:border-blue-300 dark:border-gray-700'}"
													onclick={() => handlePropertySelect(property)}
												>
													<div class="flex items-center justify-between">
														<div class="flex-1">
															<h3 class="mb-2 text-lg font-semibold text-gray-900 dark:text-white">
																{property.title}
															</h3>
															<div
																class="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400"
															>
																<span class="flex items-center">
																	<svg
																		class="mr-1 h-4 w-4"
																		fill="none"
																		stroke="currentColor"
																		viewBox="0 0 24 24"
																	>
																		<path
																			stroke-linecap="round"
																			stroke-linejoin="round"
																			stroke-width="2"
																			d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
																		/>
																	</svg>
																	{property.location_data
																		? `${property.location_data.city}, ${property.location_data.state}`
																		: property.address}
																</span>
																<span>{$t(`property.type.${property.property_type}`)}</span>
																{#if property.bedrooms}
																	<span>{property.bedrooms} {$t('property.bedrooms')}</span>
																{/if}
																{#if property.bathrooms}
																	<span>{property.bathrooms} {$t('property.bathrooms')}</span>
																{/if}
															</div>
														</div>
														{#if formData.property.id === property.id}
															<div class="ml-4">
																<div
																	class="flex h-6 w-6 items-center justify-center rounded-full bg-blue-500"
																>
																	<svg
																		class="h-4 w-4 text-white"
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
															</div>
														{/if}
													</div>
												</div>
											{/each}
										</div>
									{/if}

									{#if validationErrors.property}
										<p class="mt-4 text-sm text-red-600 dark:text-red-400">
											{validationErrors.property}
										</p>
									{/if}
								</div>
							</div>
						{/if}

						<!-- Step 2: Tenant Information -->
						{#if currentStep === 2}
							<div
								class="rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
								transition:fade={{ duration: 300 }}
							>
								<div
									class="rounded-t-2xl bg-gradient-to-r from-green-500 via-teal-500 to-cyan-600 p-6 text-white"
								>
									<h2 class="flex items-center text-2xl font-semibold">
										<span class="mr-3 text-3xl">👤</span>
										{$t('lease.tenantInformation')}
									</h2>
									<p class="mt-2 text-green-100">{$t('lease.tenantInformationDesc')}</p>
								</div>
								<div class="space-y-6 p-8">
									<!-- Existing Tenant Selection -->
									{#if tenants.length > 0}
										<div class="mb-8">
											<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
												{$t('lease.selectExistingTenant')}
											</h3>
											<div class="grid gap-3">
												{#each tenants as tenant}
													<div
														class="cursor-pointer rounded-xl border-2 p-4 transition-all duration-200 hover:shadow-md
															{formData.tenant.id === tenant.id
															? 'border-green-500 bg-green-50 dark:bg-green-900/20'
															: 'border-gray-200 hover:border-green-300 dark:border-gray-700'}"
														onclick={() => handleTenantSelect(tenant)}
													>
														<div class="flex items-center justify-between">
															<div>
																<h4 class="font-medium text-gray-900 dark:text-white">
																	{tenant.name}
																</h4>
																<p class="text-sm text-gray-600 dark:text-gray-400">
																	{tenant.email}
																</p>
															</div>
															{#if formData.tenant.id === tenant.id}
																<div
																	class="flex h-5 w-5 items-center justify-center rounded-full bg-green-500"
																>
																	<svg
																		class="h-3 w-3 text-white"
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
															{/if}
														</div>
													</div>
												{/each}
											</div>
											<div class="mt-4 text-center">
												<span class="text-gray-500 dark:text-gray-400">{$t('common.or')}</span>
											</div>
										</div>
									{/if}

									<!-- Manual Tenant Information -->
									<div>
										<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
											{$t('lease.newTenantInfo')}
										</h3>
										<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
											<div>
												<label
													for="firstName"
													class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
												>
													{$t('tenant.firstName')} <span class="text-red-500">*</span>
												</label>
												<input
													type="text"
													id="firstName"
													bind:value={formData.tenant.firstName}
													oninput={markAsChanged}
													class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
														text-gray-900 transition-all duration-200
														focus:border-transparent focus:ring-2 focus:ring-green-500 dark:border-gray-600
														dark:bg-gray-700 dark:text-gray-100
														{validationErrors.firstName ? 'border-red-500 focus:ring-red-500' : ''}"
													placeholder={$t('tenant.firstNamePlaceholder')}
													required
												/>
												{#if validationErrors.firstName}
													<p class="mt-2 text-sm text-red-600 dark:text-red-400">
														{validationErrors.firstName}
													</p>
												{/if}
											</div>

											<div>
												<label
													for="lastName"
													class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
												>
													{$t('tenant.lastName')} <span class="text-red-500">*</span>
												</label>
												<input
													type="text"
													id="lastName"
													bind:value={formData.tenant.lastName}
													oninput={markAsChanged}
													class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
														text-gray-900 transition-all duration-200
														focus:border-transparent focus:ring-2 focus:ring-green-500 dark:border-gray-600
														dark:bg-gray-700 dark:text-gray-100
														{validationErrors.lastName ? 'border-red-500 focus:ring-red-500' : ''}"
													placeholder={$t('tenant.lastNamePlaceholder')}
													required
												/>
												{#if validationErrors.lastName}
													<p class="mt-2 text-sm text-red-600 dark:text-red-400">
														{validationErrors.lastName}
													</p>
												{/if}
											</div>

											<div>
												<label
													for="email"
													class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
												>
													{$t('tenant.email')} <span class="text-red-500">*</span>
												</label>
												<input
													type="email"
													id="email"
													bind:value={formData.tenant.email}
													oninput={markAsChanged}
													class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
														text-gray-900 transition-all duration-200
														focus:border-transparent focus:ring-2 focus:ring-green-500 dark:border-gray-600
														dark:bg-gray-700 dark:text-gray-100
														{validationErrors.email ? 'border-red-500 focus:ring-red-500' : ''}"
													placeholder={$t('tenant.emailPlaceholder')}
													required
												/>
												{#if validationErrors.email}
													<p class="mt-2 text-sm text-red-600 dark:text-red-400">
														{validationErrors.email}
													</p>
												{/if}
											</div>

											<div>
												<label
													for="phone"
													class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
												>
													{$t('tenant.phone')}
												</label>
												<input
													type="tel"
													id="phone"
													bind:value={formData.tenant.phone}
													oninput={markAsChanged}
													class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
														text-gray-900 transition-all duration-200
														focus:border-transparent focus:ring-2 focus:ring-green-500 dark:border-gray-600
														dark:bg-gray-700 dark:text-gray-100"
													placeholder={$t('tenant.phonePlaceholder')}
												/>
											</div>
										</div>

										<div class="mt-6">
											<label
												for="emergencyContact"
												class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
											>
												{$t('tenant.emergencyContact')}
											</label>
											<input
												type="text"
												id="emergencyContact"
												bind:value={formData.tenant.emergencyContact}
												oninput={markAsChanged}
												class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
													text-gray-900 transition-all duration-200
													focus:border-transparent focus:ring-2 focus:ring-green-500 dark:border-gray-600
													dark:bg-gray-700 dark:text-gray-100"
												placeholder={$t('tenant.emergencyContactPlaceholder')}
											/>
										</div>

										<div class="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
											<div>
												<label
													for="employmentStatus"
													class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
												>
													{$t('tenant.employmentStatus')}
												</label>
												<select
													id="employmentStatus"
													bind:value={formData.tenant.employmentStatus}
													onchange={markAsChanged}
													class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
														text-gray-900 transition-all duration-200
														focus:border-transparent focus:ring-2 focus:ring-green-500 dark:border-gray-600
														dark:bg-gray-700 dark:text-gray-100"
												>
													<option value="">{$t('tenant.selectEmploymentStatus')}</option>
													<option value="employed">{$t('tenant.employed')}</option>
													<option value="self-employed">{$t('tenant.selfEmployed')}</option>
													<option value="unemployed">{$t('tenant.unemployed')}</option>
													<option value="student">{$t('tenant.student')}</option>
													<option value="retired">{$t('tenant.retired')}</option>
												</select>
											</div>

											<div>
												<label
													for="monthlyIncome"
													class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
												>
													{$t('tenant.monthlyIncome')}
												</label>
												<input
													type="number"
													id="monthlyIncome"
													bind:value={formData.tenant.monthlyIncome}
													oninput={markAsChanged}
													min="0"
													step="100"
													class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
														text-gray-900 transition-all duration-200
														focus:border-transparent focus:ring-2 focus:ring-green-500 dark:border-gray-600
														dark:bg-gray-700 dark:text-gray-100"
													placeholder={$t('tenant.monthlyIncomePlaceholder')}
												/>
											</div>
										</div>
									</div>
								</div>
							</div>
						{/if}

						<!-- Step 3: Lease Terms -->
						{#if currentStep === 3}
							<div
								class="rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
								transition:fade={{ duration: 300 }}
							>
								<div
									class="rounded-t-2xl bg-gradient-to-r from-purple-500 via-pink-500 to-red-500 p-6 text-white"
								>
									<h2 class="flex items-center text-2xl font-semibold">
										<span class="mr-3 text-3xl">📋</span>
										{$t('lease.leaseTerms')}
									</h2>
									<p class="mt-2 text-purple-100">{$t('lease.leaseTermsDesc')}</p>
								</div>
								<div class="space-y-6 p-8">
									<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
										<div>
											<label
												for="startDate"
												class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
											>
												{$t('lease.startDate')} <span class="text-red-500">*</span>
											</label>
											<input
												type="date"
												id="startDate"
												bind:value={formData.leaseTerms.startDate}
												onchange={markAsChanged}
												class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
													text-gray-900 transition-all duration-200
													focus:border-transparent focus:ring-2 focus:ring-purple-500 dark:border-gray-600
													dark:bg-gray-700 dark:text-gray-100
													{validationErrors.startDate ? 'border-red-500 focus:ring-red-500' : ''}"
												required
											/>
											{#if validationErrors.startDate}
												<p class="mt-2 text-sm text-red-600 dark:text-red-400">
													{validationErrors.startDate}
												</p>
											{/if}
										</div>

										<div>
											<label
												for="endDate"
												class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
											>
												{$t('lease.endDate')} <span class="text-red-500">*</span>
											</label>
											<input
												type="date"
												id="endDate"
												bind:value={formData.leaseTerms.endDate}
												onchange={markAsChanged}
												class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
													text-gray-900 transition-all duration-200
													focus:border-transparent focus:ring-2 focus:ring-purple-500 dark:border-gray-600
													dark:bg-gray-700 dark:text-gray-100
													{validationErrors.endDate ? 'border-red-500 focus:ring-red-500' : ''}"
												required
											/>
											{#if validationErrors.endDate}
												<p class="mt-2 text-sm text-red-600 dark:text-red-400">
													{validationErrors.endDate}
												</p>
											{/if}
										</div>

										<div>
											<label
												for="rentAmount"
												class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
											>
												{$t('lease.monthlyRent')} <span class="text-red-500">*</span>
											</label>
											<input
												type="number"
												id="rentAmount"
												bind:value={formData.leaseTerms.rentAmount}
												oninput={markAsChanged}
												min="0"
												step="100"
												class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
													text-gray-900 transition-all duration-200
													focus:border-transparent focus:ring-2 focus:ring-purple-500 dark:border-gray-600
													dark:bg-gray-700 dark:text-gray-100
													{validationErrors.rentAmount ? 'border-red-500 focus:ring-red-500' : ''}"
												placeholder={$t('lease.rentAmountPlaceholder')}
												required
											/>
											{#if validationErrors.rentAmount}
												<p class="mt-2 text-sm text-red-600 dark:text-red-400">
													{validationErrors.rentAmount}
												</p>
											{/if}
										</div>

										<div>
											<label
												for="securityDeposit"
												class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
											>
												{$t('lease.securityDeposit')}
											</label>
											<input
												type="number"
												id="securityDeposit"
												bind:value={formData.leaseTerms.securityDeposit}
												oninput={markAsChanged}
												min="0"
												step="100"
												class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
													text-gray-900 transition-all duration-200
													focus:border-transparent focus:ring-2 focus:ring-purple-500 dark:border-gray-600
													dark:bg-gray-700 dark:text-gray-100"
												placeholder={$t('lease.securityDepositPlaceholder')}
											/>
										</div>

										<div>
											<label
												for="leaseType"
												class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
											>
												{$t('lease.leaseType')}
											</label>
											<select
												id="leaseType"
												bind:value={formData.leaseTerms.leaseType}
												onchange={markAsChanged}
												class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
													text-gray-900 transition-all duration-200
													focus:border-transparent focus:ring-2 focus:ring-purple-500 dark:border-gray-600
													dark:bg-gray-700 dark:text-gray-100"
											>
												<option value="fixed">{$t('lease.type.fixed')}</option>
												<option value="month-to-month">{$t('lease.type.monthToMonth')}</option>
												<option value="yearly">{$t('lease.type.yearly')}</option>
											</select>
										</div>

										<div>
											<label
												for="petPolicy"
												class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
											>
												{$t('lease.petPolicy')}
											</label>
											<select
												id="petPolicy"
												bind:value={formData.leaseTerms.petPolicy}
												onchange={markAsChanged}
												class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
													text-gray-900 transition-all duration-200
													focus:border-transparent focus:ring-2 focus:ring-purple-500 dark:border-gray-600
													dark:bg-gray-700 dark:text-gray-100"
											>
												<option value="no-pets">{$t('lease.pets.noPets')}</option>
												<option value="cats-only">{$t('lease.pets.catsOnly')}</option>
												<option value="dogs-only">{$t('lease.pets.dogsOnly')}</option>
												<option value="cats-and-dogs">{$t('lease.pets.catsAndDogs')}</option>
												<option value="all-pets">{$t('lease.pets.allPets')}</option>
											</select>
										</div>
									</div>

									<!-- Renewal Option -->
									<div class="flex items-center">
										<input
											type="checkbox"
											id="renewalOption"
											bind:checked={formData.leaseTerms.renewalOption}
											onchange={markAsChanged}
											class="h-4 w-4 rounded border-gray-300 bg-gray-100 text-purple-600 focus:ring-2 focus:ring-purple-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-purple-600"
										/>
										<label
											for="renewalOption"
											class="ml-2 text-sm font-medium text-gray-900 dark:text-gray-300"
										>
											{$t('lease.includeRenewalOption')}
										</label>
									</div>
								</div>
							</div>
						{/if}

						<!-- Step 4: Financial Details -->
						{#if currentStep === 4}
							<div
								class="rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
								transition:fade={{ duration: 300 }}
							>
								<div
									class="rounded-t-2xl bg-gradient-to-r from-orange-500 via-yellow-500 to-red-500 p-6 text-white"
								>
									<h2 class="flex items-center text-2xl font-semibold">
										<span class="mr-3 text-3xl">💰</span>
										{$t('lease.financialDetails')}
									</h2>
									<p class="mt-2 text-orange-100">{$t('lease.financialDetailsDesc')}</p>
								</div>
								<div class="space-y-6 p-8">
									<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
										<div>
											<label
												for="rentDueDate"
												class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
											>
												{$t('lease.rentDueDate')} <span class="text-red-500">*</span>
											</label>
											<select
												id="rentDueDate"
												bind:value={formData.financial.rentDueDate}
												onchange={markAsChanged}
												class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
													text-gray-900 transition-all duration-200
													focus:border-transparent focus:ring-2 focus:ring-orange-500 dark:border-gray-600
													dark:bg-gray-700 dark:text-gray-100
													{validationErrors.rentDueDate ? 'border-red-500 focus:ring-red-500' : ''}"
												required
											>
												{#each Array(28) as _, i}
													<option value={i + 1}>
														{i + 1}{i === 0 ? 'st' : i === 1 ? 'nd' : i === 2 ? 'rd' : 'th'}
														{$t('lease.ofEachMonth')}
													</option>
												{/each}
											</select>
											{#if validationErrors.rentDueDate}
												<p class="mt-2 text-sm text-red-600 dark:text-red-400">
													{validationErrors.rentDueDate}
												</p>
											{/if}
										</div>

										<div>
											<label
												for="lateFee"
												class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
											>
												{$t('lease.lateFee')}
											</label>
											<input
												type="number"
												id="lateFee"
												bind:value={formData.financial.lateFee}
												oninput={markAsChanged}
												min="0"
												step="10"
												class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
													text-gray-900 transition-all duration-200
													focus:border-transparent focus:ring-2 focus:ring-orange-500 dark:border-gray-600
													dark:bg-gray-700 dark:text-gray-100"
												placeholder={$t('lease.lateFeeAmount')}
											/>
										</div>

										<div>
											<label
												for="paymentMethod"
												class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
											>
												{$t('lease.paymentMethod')} <span class="text-red-500">*</span>
											</label>
											<select
												id="paymentMethod"
												bind:value={formData.financial.paymentMethod}
												onchange={markAsChanged}
												class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
													text-gray-900 transition-all duration-200
													focus:border-transparent focus:ring-2 focus:ring-orange-500 dark:border-gray-600
													dark:bg-gray-700 dark:text-gray-100
													{validationErrors.paymentMethod ? 'border-red-500 focus:ring-red-500' : ''}"
												required
											>
												<option value="bank-transfer">{$t('lease.payment.bankTransfer')}</option>
												<option value="check">{$t('lease.payment.check')}</option>
												<option value="cash">{$t('lease.payment.cash')}</option>
												<option value="online-portal">{$t('lease.payment.onlinePortal')}</option>
											</select>
											{#if validationErrors.paymentMethod}
												<p class="mt-2 text-sm text-red-600 dark:text-red-400">
													{validationErrors.paymentMethod}
												</p>
											{/if}
										</div>

										<div>
											<label
												for="additionalFees"
												class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
											>
												{$t('lease.additionalFees')}
											</label>
											<input
												type="text"
												id="additionalFees"
												bind:value={formData.financial.additionalFees}
												oninput={markAsChanged}
												class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
													text-gray-900 transition-all duration-200
													focus:border-transparent focus:ring-2 focus:ring-orange-500 dark:border-gray-600
													dark:bg-gray-700 dark:text-gray-100"
												placeholder={$t('lease.additionalFeesPlaceholder')}
											/>
										</div>
									</div>

									<!-- Utilities -->
									<div>
										<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-white">
											{$t('lease.utilitiesIncluded')}
										</h3>
										<div class="grid grid-cols-2 gap-3 md:grid-cols-4">
											{#each utilitiesOptions as utility}
												<label
													class="flex cursor-pointer items-center rounded-xl border border-gray-200 p-3 transition-colors hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-700"
												>
													<input
														type="checkbox"
														checked={formData.financial.utilities.includes(utility)}
														onchange={() => handleUtilityToggle(utility)}
														class="h-4 w-4 rounded border-gray-300 bg-gray-100 text-orange-600 focus:ring-2 focus:ring-orange-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-orange-600"
													/>
													<span class="ml-2 text-sm text-gray-900 dark:text-gray-300"
														>{$t(`lease.utilities.${utility}`)}</span
													>
												</label>
											{/each}
										</div>
									</div>
								</div>
							</div>
						{/if}

						<!-- Step 5: Documents & Additional Terms -->
						{#if currentStep === 5}
							<div
								class="rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
								transition:fade={{ duration: 300 }}
							>
								<div
									class="rounded-t-2xl bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 p-6 text-white"
								>
									<h2 class="flex items-center text-2xl font-semibold">
										<span class="mr-3 text-3xl">📄</span>
										{$t('lease.documentsAndTerms')}
									</h2>
									<p class="mt-2 text-indigo-100">{$t('lease.documentsAndTermsDesc')}</p>
								</div>
								<div class="space-y-8 p-8">
									<!-- Document Upload -->
									<div>
										<h3 class="mb-6 text-lg font-semibold text-gray-900 dark:text-white">
											{$t('lease.documentUpload')}
										</h3>
										<div class="grid gap-6">
											<!-- Lease Agreement Template -->
											<div>
												<label
													class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
												>
													{$t('lease.leaseAgreementTemplate')}
												</label>
												<div
													class="rounded-xl border-2 border-dashed border-gray-300 p-6 text-center transition-colors hover:border-indigo-400 dark:border-gray-600"
												>
													<div class="mb-3 text-4xl">📄</div>
													<p class="mb-3 text-sm text-gray-600 dark:text-gray-400">
														{$t('lease.uploadLeaseTemplate')}
													</p>
													<input
														type="file"
														accept=".pdf,.doc,.docx"
														onchange={(e) => handleFileUpload(e, 'leaseAgreement')}
														class="hidden"
														id="leaseAgreement"
													/>
													<Button
														variant="outline"
														onclick={() => document.getElementById('leaseAgreement').click()}
													>
														{$t('common.chooseFile')}
													</Button>
													{#if uploadedFiles.leaseAgreement}
														<p class="mt-2 text-sm text-indigo-600 dark:text-indigo-400">
															{uploadedFiles.leaseAgreement.name}
														</p>
													{/if}
												</div>
											</div>

											<!-- Tenant ID -->
											<div>
												<label
													class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
												>
													{$t('lease.tenantIdDocument')}
												</label>
												<div
													class="rounded-xl border-2 border-dashed border-gray-300 p-6 text-center transition-colors hover:border-indigo-400 dark:border-gray-600"
												>
													<div class="mb-3 text-4xl">🆔</div>
													<p class="mb-3 text-sm text-gray-600 dark:text-gray-400">
														{$t('lease.uploadTenantId')}
													</p>
													<input
														type="file"
														accept=".pdf,.jpg,.jpeg,.png"
														onchange={(e) => handleFileUpload(e, 'tenantId')}
														class="hidden"
														id="tenantId"
													/>
													<Button
														variant="outline"
														onclick={() => document.getElementById('tenantId').click()}
													>
														{$t('common.chooseFile')}
													</Button>
													{#if uploadedFiles.tenantId}
														<p class="mt-2 text-sm text-indigo-600 dark:text-indigo-400">
															{uploadedFiles.tenantId.name}
														</p>
													{/if}
												</div>
											</div>

											<!-- Income Proof -->
											<div>
												<label
													class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
												>
													{$t('lease.incomeProof')}
												</label>
												<div
													class="rounded-xl border-2 border-dashed border-gray-300 p-6 text-center transition-colors hover:border-indigo-400 dark:border-gray-600"
												>
													<div class="mb-3 text-4xl">💼</div>
													<p class="mb-3 text-sm text-gray-600 dark:text-gray-400">
														{$t('lease.uploadIncomeProof')}
													</p>
													<input
														type="file"
														accept=".pdf,.jpg,.jpeg,.png"
														onchange={(e) => handleFileUpload(e, 'incomeProof')}
														class="hidden"
														id="incomeProof"
													/>
													<Button
														variant="outline"
														onclick={() => document.getElementById('incomeProof').click()}
													>
														{$t('common.chooseFile')}
													</Button>
													{#if uploadedFiles.incomeProof}
														<p class="mt-2 text-sm text-indigo-600 dark:text-indigo-400">
															{uploadedFiles.incomeProof.name}
														</p>
													{/if}
												</div>
											</div>
										</div>
									</div>

									<!-- Additional Terms -->
									<div>
										<h3 class="mb-6 text-lg font-semibold text-gray-900 dark:text-white">
											{$t('lease.additionalTerms')}
										</h3>
										<div class="space-y-6">
											<div>
												<label
													for="specialTerms"
													class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
												>
													{$t('lease.specialTerms')}
												</label>
												<textarea
													id="specialTerms"
													bind:value={formData.documents.specialTerms}
													oninput={markAsChanged}
													rows="4"
													class="w-full resize-none rounded-xl border border-gray-300 bg-white px-4
														py-3 text-gray-900 transition-all
														duration-200 focus:border-transparent focus:ring-2 focus:ring-indigo-500
														dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
													placeholder={$t('lease.specialTermsPlaceholder')}
												></textarea>
											</div>

											<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
												<div>
													<label
														for="maintenanceResponsibility"
														class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
													>
														{$t('lease.maintenanceResponsibility')}
													</label>
													<select
														id="maintenanceResponsibility"
														bind:value={formData.documents.maintenanceResponsibility}
														onchange={markAsChanged}
														class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
															text-gray-900 transition-all duration-200
															focus:border-transparent focus:ring-2 focus:ring-indigo-500 dark:border-gray-600
															dark:bg-gray-700 dark:text-gray-100"
													>
														<option value="tenant">{$t('lease.maintenance.tenant')}</option>
														<option value="landlord">{$t('lease.maintenance.landlord')}</option>
														<option value="shared">{$t('lease.maintenance.shared')}</option>
													</select>
												</div>
											</div>

											<div class="space-y-4">
												<div class="flex items-center">
													<input
														type="checkbox"
														id="parkingIncluded"
														bind:checked={formData.documents.parkingIncluded}
														onchange={markAsChanged}
														class="h-4 w-4 rounded border-gray-300 bg-gray-100 text-indigo-600 focus:ring-2 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-indigo-600"
													/>
													<label
														for="parkingIncluded"
														class="ml-2 text-sm font-medium text-gray-900 dark:text-gray-300"
													>
														{$t('lease.parkingIncluded')}
													</label>
												</div>

												<div class="flex items-center">
													<input
														type="checkbox"
														id="smokingAllowed"
														bind:checked={formData.documents.smokingAllowed}
														onchange={markAsChanged}
														class="h-4 w-4 rounded border-gray-300 bg-gray-100 text-indigo-600 focus:ring-2 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-indigo-600"
													/>
													<label
														for="smokingAllowed"
														class="ml-2 text-sm font-medium text-gray-900 dark:text-gray-300"
													>
														{$t('lease.smokingAllowed')}
													</label>
												</div>
											</div>
										</div>
									</div>

									<!-- Lease Summary -->
									<div
										class="rounded-xl border border-gray-200 bg-gradient-to-r from-gray-50 to-blue-50 p-6 dark:border-gray-600 dark:from-gray-700 dark:to-blue-900/20"
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
											{$t('lease.leaseSummary')}
										</h3>
										<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
											<div>
												<h4 class="mb-3 font-medium text-gray-900 dark:text-white">
													{$t('lease.basicInfo')}
												</h4>
												<dl class="space-y-2 text-sm">
													<div class="flex justify-between">
														<dt class="text-gray-500 dark:text-gray-400">
															{$t('property.title')}:
														</dt>
														<dd class="font-medium text-gray-900 dark:text-white">
															{formData.property.title || '-'}
														</dd>
													</div>
													<div class="flex justify-between">
														<dt class="text-gray-500 dark:text-gray-400">{$t('tenant.name')}:</dt>
														<dd class="font-medium text-gray-900 dark:text-white">
															{formData.tenant.firstName}
															{formData.tenant.lastName || '-'}
														</dd>
													</div>
													<div class="flex justify-between">
														<dt class="text-gray-500 dark:text-gray-400">
															{$t('lease.duration')}:
														</dt>
														<dd class="font-medium text-gray-900 dark:text-white">
															{formData.leaseTerms.startDate} - {formData.leaseTerms.endDate}
														</dd>
													</div>
												</dl>
											</div>
											<div>
												<h4 class="mb-3 font-medium text-gray-900 dark:text-white">
													{$t('lease.financials')}
												</h4>
												<dl class="space-y-2 text-sm">
													<div class="flex justify-between">
														<dt class="text-gray-500 dark:text-gray-400">
															{$t('lease.monthlyRent')}:
														</dt>
														<dd class="font-medium text-gray-900 dark:text-white">
															{formData.leaseTerms.rentAmount || '-'}
															{$t('currency.sar')}
														</dd>
													</div>
													<div class="flex justify-between">
														<dt class="text-gray-500 dark:text-gray-400">
															{$t('lease.securityDeposit')}:
														</dt>
														<dd class="font-medium text-gray-900 dark:text-white">
															{formData.leaseTerms.securityDeposit || '-'}
															{$t('currency.sar')}
														</dd>
													</div>
													<div class="flex justify-between">
														<dt class="text-gray-500 dark:text-gray-400">
															{$t('lease.paymentMethod')}:
														</dt>
														<dd class="font-medium text-gray-900 dark:text-white">
															{$t(`lease.payment.${formData.financial.paymentMethod}`)}
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
							class="flex items-center justify-between border-t border-gray-200 pt-8 dark:border-gray-700"
						>
							<Button
								variant="outline"
								onclick={handlePrevious}
								disabled={currentStep === 1 || saving}
								class="min-w-[120px]"
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
									<Button
										variant="primary"
										onclick={handleNext}
										disabled={saving || !isStepComplete(currentStep)}
										class="min-w-[120px] bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
									>
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
										disabled={saving}
										size="lg"
										class="min-w-[140px] bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
									>
										{#if saving}
											<LoadingSpinner size="sm" color="white" class="mr-2" />
										{/if}
										{saving ? $t('common.creating') : $t('lease.generateLease')}
									</Button>
								{/if}
							</div>
						</div>
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

<style>
	/* Enhanced form styling */
	input:focus,
	select:focus,
	textarea:focus {
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
		transform: translateY(-1px);
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

	/* Progress indicator animations */
	@keyframes progress-glow {
		0%,
		100% {
			box-shadow: 0 0 5px rgba(59, 130, 246, 0.5);
		}
		50% {
			box-shadow: 0 0 20px rgba(59, 130, 246, 0.8);
		}
	}

	.progress-active {
		animation: progress-glow 2s ease-in-out infinite;
	}

	/* File upload hover effects */
	.file-upload-area:hover {
		background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(168, 85, 247, 0.05) 100%);
	}
</style>
