<!-- src/routes/create/worker/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t, locale } from '$lib/i18n';
	import { toast } from '$lib/stores/toastStore.svelte.js';
	import { createWorker } from '$lib/api/worker';
	import { user } from '$lib/stores/user.svelte.js';
	import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';
	import TabbedForm from '$lib/components/ui/TabbedForm.svelte';
	import FormStep from '$lib/components/ui/FormStep.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';

	// Breadcrumb items
	$: breadcrumbItems = [
		{ label: $t('nav.home'), href: '/' },
		{ label: $t('nav.dashboard'), href: '/dashboard' },
		{ label: $t('worker.workers'), href: '/dashboard/workers' },
		{ label: $t('worker.add'), href: '/create/worker', active: true }
	];

	// Form state
	let currentTab = 0;
	let loading = false;
	let submitting = false;
	let error = null;
	let success = null;
	let validationErrors = {};
	let completedTabs = [];

	// Form data
	let formData = {
		name: '',
		email: '',
		phone: '',
		worker_type: 'maintenance',
		specialization: '',
		experience_years: '',
		hourly_rate: '',
		daily_rate: '',
		address: '',
		city: '',
		state: '',
		postal_code: '',
		national_id: '',
		license_number: '',
		insurance_number: '',
		skills: [],
		languages: [],
		availability: 'full_time',
		emergency_contact_name: '',
		emergency_contact_phone: '',
		bank_account_name: '',
		bank_name: '',
		iban_number: '',
		notes: '',
		is_active: true
	};

	// Tab configuration
	$: tabs = [
		{
			id: 'personal',
			label: $t('worker.personalInfo'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>',
			fields: ['name', 'email', 'phone', 'address', 'city', 'state', 'postal_code']
		},
		{
			id: 'professional',
			label: $t('worker.professionalInfo'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 002 2h2a2 2 0 002-2V6M8 20h8"></path></svg>',
			fields: ['worker_type', 'specialization', 'experience_years', 'hourly_rate', 'daily_rate', 'skills', 'languages', 'availability']
		},
		{
			id: 'documents',
			label: $t('worker.documents'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>',
			fields: ['national_id', 'license_number', 'insurance_number']
		},
		{
			id: 'contacts',
			label: $t('worker.contactsPayment'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"></path></svg>',
			fields: ['emergency_contact_name', 'emergency_contact_phone', 'bank_account_name', 'bank_name', 'iban_number', 'notes']
		}
	];

	// Worker types
	$: workerTypes = [
		{ value: 'maintenance', label: $t('worker.maintenance') },
		{ value: 'cleaning', label: $t('worker.cleaning') },
		{ value: 'gardening', label: $t('worker.gardening') },
		{ value: 'security', label: $t('worker.security') },
		{ value: 'repair', label: $t('worker.repair') },
		{ value: 'plumbing', label: $t('worker.plumbing') },
		{ value: 'electrical', label: $t('worker.electrical') },
		{ value: 'painting', label: $t('worker.painting') },
		{ value: 'other', label: $t('worker.other') }
	];

	// Availability options
	$: availabilityOptions = [
		{ value: 'full_time', label: $t('worker.fullTime') },
		{ value: 'part_time', label: $t('worker.partTime') },
		{ value: 'contract', label: $t('worker.contract') },
		{ value: 'on_call', label: $t('worker.onCall') }
	];

	// Skills and languages (will be converted to arrays)
	let skillsText = '';
	let languagesText = '';

	// Validation
	function validateCurrentTab() {
		const currentTabData = tabs[currentTab];
		const tabErrors = {};
		
		if (currentTabData.id === 'personal') {
			if (!formData.name.trim()) {
				tabErrors.name = $t('validation.required');
			}
			if (!formData.email.trim()) {
				tabErrors.email = $t('validation.required');
			} else if (!isValidEmail(formData.email)) {
				tabErrors.email = $t('validation.invalidEmail');
			}
			if (!formData.phone.trim()) {
				tabErrors.phone = $t('validation.required');
			}
		} else if (currentTabData.id === 'professional') {
			if (!formData.worker_type) {
				tabErrors.worker_type = $t('validation.required');
			}
			if (formData.experience_years && (isNaN(parseInt(formData.experience_years)) || parseInt(formData.experience_years) < 0)) {
				tabErrors.experience_years = $t('validation.positiveNumber');
			}
			if (formData.hourly_rate && (isNaN(parseFloat(formData.hourly_rate)) || parseFloat(formData.hourly_rate) < 0)) {
				tabErrors.hourly_rate = $t('validation.positiveNumber');
			}
			if (formData.daily_rate && (isNaN(parseFloat(formData.daily_rate)) || parseFloat(formData.daily_rate) < 0)) {
				tabErrors.daily_rate = $t('validation.positiveNumber');
			}
		}

		// Update validation errors
		validationErrors = { ...validationErrors, ...tabErrors };
		
		// Remove errors for fields not in current tab
		const fieldsToKeep = currentTabData.fields;
		validationErrors = Object.fromEntries(
			Object.entries(validationErrors).filter(([key]) => fieldsToKeep.includes(key))
		);

		return Object.keys(tabErrors).length === 0;
	}

	function isValidEmail(email) {
		return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
	}

	// Convert text to arrays for skills and languages
	function updateArrayFields() {
		formData.skills = skillsText.split(',').map(s => s.trim()).filter(s => s);
		formData.languages = languagesText.split(',').map(l => l.trim()).filter(l => l);
	}

	function handleTabChange(event) {
		updateArrayFields();
		if (validateCurrentTab()) {
			if (!completedTabs.includes(currentTab)) {
				completedTabs = [...completedTabs, currentTab];
			}
		}
		currentTab = event.detail.tab;
	}

	function handleNext() {
		updateArrayFields();
		if (validateCurrentTab()) {
			if (!completedTabs.includes(currentTab)) {
				completedTabs = [...completedTabs, currentTab];
			}
			if (currentTab < tabs.length - 1) {
				currentTab++;
			}
		}
	}

	function handlePrevious() {
		if (currentTab > 0) {
			currentTab--;
		}
	}

	async function handleSubmit() {
		updateArrayFields();
		if (!validateCurrentTab()) {
			return;
		}

		try {
			submitting = true;
			error = null;

			// Prepare data for submission
			const submitData = {
				...formData,
				experience_years: formData.experience_years ? parseInt(formData.experience_years) : null,
				hourly_rate: formData.hourly_rate ? parseFloat(formData.hourly_rate) : null,
				daily_rate: formData.daily_rate ? parseFloat(formData.daily_rate) : null
			};

			const result = await createWorker(submitData);
			success = $t('worker.createSuccess');
			
			setTimeout(() => {
				goto('/dashboard/workers');
			}, 1500);
		} catch (err) {
			error = err.message || $t('worker.createError');
		} finally {
			submitting = false;
		}
	}

	function handleCancel() {
		goto('/dashboard/workers');
	}

	$: canProceed = validateCurrentTab();
	$: isFirstStep = currentTab === 0;
	$: isLastStep = currentTab === tabs.length - 1;

	onMount(() => {
		validateCurrentTab();
	});
</script>

<svelte:head>
	<title>{$t('worker.add')} - {$t('app.name')}</title>
	<meta name="description" content={$t('worker.addDescription')} />
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<div class="mx-auto max-w-4xl px-4 py-6 sm:px-6 lg:px-8">
		<div class="space-y-6">
			<!-- Breadcrumb -->
			<Breadcrumb items={breadcrumbItems} />

			<!-- Page Header -->
			<div class="text-center">
				<h1 class="text-3xl font-bold text-gray-900 dark:text-white">
					{$t('worker.add')}
				</h1>
				<p class="mt-2 text-lg text-gray-600 dark:text-gray-400">
					{$t('worker.addDescription')}
				</p>
			</div>

			<!-- Messages -->
			{#if error}
				<Alert type="error" message={error} dismissible on:dismiss={() => error = null} />
			{/if}

			{#if success}
				<Alert type="success" message={success} />
			{/if}

			<!-- Tabbed Form -->
			<div class="bg-white dark:bg-gray-800 shadow-lg rounded-lg p-6">
				<TabbedForm
					{tabs}
					{currentTab}
					{validationErrors}
					{completedTabs}
					showProgressBar={true}
					allowFreeNavigation={false}
					on:tabChange={handleTabChange}
				>
					<!-- Personal Information Tab -->
					{#if currentTab === 0}
						<FormStep
							step={{
								id: 'personal',
								title: $t('worker.personalInfo'),
								description: $t('worker.personalInfoDescription')
							}}
							{isFirstStep}
							{isLastStep}
							{canProceed}
							loading={submitting}
							on:next={handleNext}
							on:previous={handlePrevious}
							on:submit={handleSubmit}
						>
							<div class="space-y-6">
								<div>
									<label for="name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										{$t('worker.name')} *
									</label>
									<input
										type="text"
										id="name"
										bind:value={formData.name}
										class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
										placeholder={$t('worker.namePlaceholder')}
										class:border-red-500={validationErrors.name}
										on:input={validateCurrentTab}
									/>
									{#if validationErrors.name}
										<p class="mt-1 text-sm text-red-600">{validationErrors.name}</p>
									{/if}
								</div>

								<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
									<div>
										<label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('worker.email')} *
										</label>
										<input
											type="email"
											id="email"
											bind:value={formData.email}
											class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
											placeholder="worker@example.com"
											class:border-red-500={validationErrors.email}
											on:input={validateCurrentTab}
										/>
										{#if validationErrors.email}
											<p class="mt-1 text-sm text-red-600">{validationErrors.email}</p>
										{/if}
									</div>

									<div>
										<label for="phone" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('worker.phone')} *
										</label>
										<input
											type="tel"
											id="phone"
											bind:value={formData.phone}
											class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
											placeholder="+966 50 123 4567"
											class:border-red-500={validationErrors.phone}
											on:input={validateCurrentTab}
										/>
										{#if validationErrors.phone}
											<p class="mt-1 text-sm text-red-600">{validationErrors.phone}</p>
										{/if}
									</div>
								</div>

								<div>
									<label for="address" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										{$t('worker.address')}
									</label>
									<input
										type="text"
										id="address"
										bind:value={formData.address}
										class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
										placeholder={$t('worker.addressPlaceholder')}
									/>
								</div>

								<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
									<div>
										<label for="city" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('worker.city')}
										</label>
										<input
											type="text"
											id="city"
											bind:value={formData.city}
											class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
											placeholder={$t('worker.cityPlaceholder')}
										/>
									</div>

									<div>
										<label for="state" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('worker.state')}
										</label>
										<input
											type="text"
											id="state"
											bind:value={formData.state}
											class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
											placeholder={$t('worker.statePlaceholder')}
										/>
									</div>

									<div>
										<label for="postal_code" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('worker.postalCode')}
										</label>
										<input
											type="text"
											id="postal_code"
											bind:value={formData.postal_code}
											class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
											placeholder="12345"
										/>
									</div>
								</div>
							</div>
						</FormStep>
					{/if}

					<!-- Professional Information Tab -->
					{#if currentTab === 1}
						<FormStep
							step={{
								id: 'professional',
								title: $t('worker.professionalInfo'),
								description: $t('worker.professionalInfoDescription')
							}}
							{isFirstStep}
							{isLastStep}
							{canProceed}
							loading={submitting}
							on:next={handleNext}
							on:previous={handlePrevious}
							on:submit={handleSubmit}
						>
							<div class="space-y-6">
								<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
									<div>
										<label for="worker_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('worker.workerType')} *
										</label>
										<select
											id="worker_type"
											bind:value={formData.worker_type}
											class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
											class:border-red-500={validationErrors.worker_type}
											on:change={validateCurrentTab}
										>
											{#each workerTypes as type}
												<option value={type.value}>{type.label}</option>
											{/each}
										</select>
										{#if validationErrors.worker_type}
											<p class="mt-1 text-sm text-red-600">{validationErrors.worker_type}</p>
										{/if}
									</div>

									<div>
										<label for="availability" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('worker.availability')}
										</label>
										<select
											id="availability"
											bind:value={formData.availability}
											class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
										>
											{#each availabilityOptions as option}
												<option value={option.value}>{option.label}</option>
											{/each}
										</select>
									</div>
								</div>

								<div>
									<label for="specialization" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										{$t('worker.specialization')}
									</label>
									<input
										type="text"
										id="specialization"
										bind:value={formData.specialization}
										class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
										placeholder={$t('worker.specializationPlaceholder')}
									/>
								</div>

								<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
									<div>
										<label for="experience_years" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('worker.experienceYears')}
										</label>
										<input
											type="number"
											id="experience_years"
											bind:value={formData.experience_years}
											min="0"
											class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
											placeholder="0"
											class:border-red-500={validationErrors.experience_years}
											on:input={validateCurrentTab}
										/>
										{#if validationErrors.experience_years}
											<p class="mt-1 text-sm text-red-600">{validationErrors.experience_years}</p>
										{/if}
									</div>

									<div>
										<label for="hourly_rate" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('worker.hourlyRate')}
										</label>
										<div class="relative">
											<input
												type="number"
												id="hourly_rate"
												bind:value={formData.hourly_rate}
												step="0.01"
												min="0"
												class="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
												placeholder="0.00"
												class:border-red-500={validationErrors.hourly_rate}
												on:input={validateCurrentTab}
											/>
											<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
												<span class="text-gray-500 dark:text-gray-400">$</span>
											</div>
										</div>
										{#if validationErrors.hourly_rate}
											<p class="mt-1 text-sm text-red-600">{validationErrors.hourly_rate}</p>
										{/if}
									</div>

									<div>
										<label for="daily_rate" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('worker.dailyRate')}
										</label>
										<div class="relative">
											<input
												type="number"
												id="daily_rate"
												bind:value={formData.daily_rate}
												step="0.01"
												min="0"
												class="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
												placeholder="0.00"
												class:border-red-500={validationErrors.daily_rate}
												on:input={validateCurrentTab}
											/>
											<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
												<span class="text-gray-500 dark:text-gray-400">$</span>
											</div>
										</div>
										{#if validationErrors.daily_rate}
											<p class="mt-1 text-sm text-red-600">{validationErrors.daily_rate}</p>
										{/if}
									</div>
								</div>

								<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
									<div>
										<label for="skills" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('worker.skills')}
										</label>
										<textarea
											id="skills"
											bind:value={skillsText}
											rows="3"
											class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
											placeholder={$t('worker.skillsPlaceholder')}
										></textarea>
										<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
											{$t('worker.skillsHelp')}
										</p>
									</div>

									<div>
										<label for="languages" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('worker.languages')}
										</label>
										<textarea
											id="languages"
											bind:value={languagesText}
											rows="3"
											class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
											placeholder={$t('worker.languagesPlaceholder')}
										></textarea>
										<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
											{$t('worker.languagesHelp')}
										</p>
									</div>
								</div>
							</div>
						</FormStep>
					{/if}

					<!-- Documents Tab -->
					{#if currentTab === 2}
						<FormStep
							step={{
								id: 'documents',
								title: $t('worker.documents'),
								description: $t('worker.documentsDescription')
							}}
							{isFirstStep}
							{isLastStep}
							{canProceed}
							loading={submitting}
							on:next={handleNext}
							on:previous={handlePrevious}
							on:submit={handleSubmit}
						>
							<div class="space-y-6">
								<div>
									<label for="national_id" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										{$t('worker.nationalId')}
									</label>
									<input
										type="text"
										id="national_id"
										bind:value={formData.national_id}
										class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
										placeholder={$t('worker.nationalIdPlaceholder')}
									/>
								</div>

								<div>
									<label for="license_number" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										{$t('worker.licenseNumber')}
									</label>
									<input
										type="text"
										id="license_number"
										bind:value={formData.license_number}
										class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
										placeholder={$t('worker.licenseNumberPlaceholder')}
									/>
									<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
										{$t('worker.licenseHelp')}
									</p>
								</div>

								<div>
									<label for="insurance_number" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										{$t('worker.insuranceNumber')}
									</label>
									<input
										type="text"
										id="insurance_number"
										bind:value={formData.insurance_number}
										class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
										placeholder={$t('worker.insuranceNumberPlaceholder')}
									/>
									<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
										{$t('worker.insuranceHelp')}
									</p>
								</div>
							</div>
						</FormStep>
					{/if}

					<!-- Contacts & Payment Tab -->
					{#if currentTab === 3}
						<FormStep
							step={{
								id: 'contacts',
								title: $t('worker.contactsPayment'),
								description: $t('worker.contactsPaymentDescription'),
								submitText: $t('worker.createWorker'),
								submitLoadingText: $t('worker.creating')
							}}
							{isFirstStep}
							{isLastStep}
							{canProceed}
							loading={submitting}
							on:next={handleNext}
							on:previous={handlePrevious}
							on:submit={handleSubmit}
						>
							<div class="space-y-6">
								<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
									<div>
										<label for="emergency_contact_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('worker.emergencyContactName')}
										</label>
										<input
											type="text"
											id="emergency_contact_name"
											bind:value={formData.emergency_contact_name}
											class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
											placeholder={$t('worker.emergencyContactNamePlaceholder')}
										/>
									</div>

									<div>
										<label for="emergency_contact_phone" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('worker.emergencyContactPhone')}
										</label>
										<input
											type="tel"
											id="emergency_contact_phone"
											bind:value={formData.emergency_contact_phone}
											class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
											placeholder="+966 50 123 4567"
										/>
									</div>
								</div>

								<div class="border-t border-gray-200 dark:border-gray-700 pt-6">
									<h4 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
										{$t('worker.paymentInfo')}
									</h4>

									<div class="space-y-4">
										<div>
											<label for="bank_account_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
												{$t('worker.bankAccountName')}
											</label>
											<input
												type="text"
												id="bank_account_name"
												bind:value={formData.bank_account_name}
												class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
												placeholder={$t('worker.bankAccountNamePlaceholder')}
											/>
										</div>

										<div>
											<label for="bank_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
												{$t('worker.bankName')}
											</label>
											<input
												type="text"
												id="bank_name"
												bind:value={formData.bank_name}
												class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
												placeholder={$t('worker.bankNamePlaceholder')}
											/>
										</div>

										<div>
											<label for="iban_number" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
												{$t('worker.ibanNumber')}
											</label>
											<input
												type="text"
												id="iban_number"
												bind:value={formData.iban_number}
												class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
												placeholder="SA00 0000 0000 0000 0000 0000"
											/>
										</div>
									</div>
								</div>

								<div>
									<label for="notes" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										{$t('worker.notes')}
									</label>
									<textarea
										id="notes"
										bind:value={formData.notes}
										rows="4"
										class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
										placeholder={$t('worker.notesPlaceholder')}
									></textarea>
								</div>

								<div class="flex items-center">
									<input
										type="checkbox"
										id="is_active"
										bind:checked={formData.is_active}
										class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
									/>
									<label for="is_active" class="ml-2 block text-sm text-gray-900 dark:text-gray-100">
										{$t('worker.isActive')}
									</label>
								</div>

								<!-- Summary -->
								<div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
									<h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">
										{$t('form.summary')}
									</h4>
									<dl class="space-y-2 text-sm">
										<div class="flex justify-between">
											<dt class="text-gray-600 dark:text-gray-400">{$t('worker.name')}:</dt>
											<dd class="font-medium text-gray-900 dark:text-gray-100">{formData.name}</dd>
										</div>
										<div class="flex justify-between">
											<dt class="text-gray-600 dark:text-gray-400">{$t('worker.workerType')}:</dt>
											<dd class="font-medium text-gray-900 dark:text-gray-100">
												{workerTypes.find(t => t.value === formData.worker_type)?.label}
											</dd>
										</div>
										<div class="flex justify-between">
											<dt class="text-gray-600 dark:text-gray-400">{$t('worker.email')}:</dt>
											<dd class="font-medium text-gray-900 dark:text-gray-100">{formData.email}</dd>
										</div>
										<div class="flex justify-between">
											<dt class="text-gray-600 dark:text-gray-400">{$t('worker.phone')}:</dt>
											<dd class="font-medium text-gray-900 dark:text-gray-100">{formData.phone}</dd>
										</div>
									</dl>
								</div>
							</div>
						</FormStep>
					{/if}
				</TabbedForm>

				<!-- Cancel Button -->
				<div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
					<Button
						variant="outline"
						on:click={handleCancel}
						disabled={submitting}
						class="w-full sm:w-auto"
					>
						{$t('form.cancel')}
					</Button>
				</div>
			</div>
		</div>
	</div>
</div>
