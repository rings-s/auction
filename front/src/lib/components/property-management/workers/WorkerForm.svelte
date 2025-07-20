<!-- src/lib/components/property-management/workers/WorkerForm.svelte -->
<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import { 
		createWorker, 
		updateWorker, 
		getWorker,
		getWorkerCategories,
		validateWorkerData,
		getEmploymentTypes,
		getWorkerStatuses,
		formatHourlyRate
	} from '$lib/api/worker';
	import { toast } from '$lib/stores/toastStore.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';
	import Tabs from '$lib/components/ui/Tabs.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';

	// Props using Svelte 5 runes
	const { workerId = null, onSuccess = null, embedded = false } = $props();

	// Svelte 5 runes for reactive state
	let loading = $state(false);
	let saving = $state(false);
	let error = $state(null);
	let currentStep = $state(1);
	let categories = $state([]);
	let autoSaveEnabled = $state(true);
	let autoSaveTimer = $state(null);

	// Form data with Svelte 5 runes
	let formData = $state({
		first_name: '',
		last_name: '',
		email: '',
		phone: '',
		date_of_birth: '',
		address: '',
		employment_type: 'full_time',
		hire_date: '',
		hourly_rate: '',
		max_concurrent_jobs: 3,
		categories: [],
		status: 'active',
		is_available: true,
		notes: ''
	});

	// Validation errors
	let validationErrors = $state({});

	// Derived state
	let isEditing = $derived(!!workerId);
	let canProceed = $derived(Object.keys(validationErrors).length === 0);
	let employmentTypes = $derived(getEmploymentTypes());
	let workerStatuses = $derived(getWorkerStatuses());
	let selectedCategories = $derived(
		categories.filter(cat => formData.categories.includes(cat.id))
	);

	// Tab configuration
	let tabs = $derived([
		{
			id: 1,
			label: $t('worker.personalInfo'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>'
		},
		{
			id: 2,
			label: $t('worker.skillsCategories'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>'
		},
		{
			id: 3,
			label: $t('worker.employment'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V8a2 2 0 012-2V6z"></path></svg>'
		}
	]);

	// Load data on mount
	onMount(async () => {
		await loadInitialData();
		
		if (isEditing) {
			await loadWorkerData();
		} else {
			// Set default hire date to today
			formData.hire_date = new Date().toISOString().split('T')[0];
		}
		
		validateForm();
	});

	// Load initial data (categories, etc.)
	async function loadInitialData() {
		try {
			loading = true;
			categories = await getWorkerCategories();
		} catch (err) {
			toast.error($t('worker.loadDataError'));
		} finally {
			loading = false;
		}
	}

	// Load worker data for editing
	async function loadWorkerData() {
		try {
			loading = true;
			error = null;
			const worker = await getWorker(workerId);
			
			// Populate form data
			formData = {
				first_name: worker.first_name || '',
				last_name: worker.last_name || '',
				email: worker.email || '',
				phone: worker.phone || '',
				date_of_birth: worker.date_of_birth || '',
				address: worker.address || '',
				employment_type: worker.employment_type || 'full_time',
				hire_date: worker.hire_date || '',
				hourly_rate: worker.hourly_rate || '',
				max_concurrent_jobs: worker.max_concurrent_jobs || 3,
				categories: worker.categories ? worker.categories.map(cat => cat.id) : [],
				status: worker.status || 'active',
				is_available: worker.is_available ?? true,
				notes: worker.notes || ''
			};
		} catch (err) {
			error = err.message;
			toast.error($t('worker.loadError'));
		} finally {
			loading = false;
		}
	}

	// Validate form
	function validateForm() {
		const validation = validateWorkerData(formData);
		validationErrors = validation.errors;
		return validation.isValid;
	}

	// Handle form field changes
	function handleFieldChange(field, value) {
		formData[field] = value;
		
		// Clear specific field error
		if (validationErrors[field]) {
			delete validationErrors[field];
			validationErrors = { ...validationErrors };
		}
		
		// Auto-save if enabled
		if (autoSaveEnabled && isEditing) {
			scheduleAutoSave();
		}
		
		// Re-validate form
		validateForm();
	}

	// Handle category selection
	function handleCategoryChange(categoryId, checked) {
		if (checked) {
			formData.categories = [...formData.categories, categoryId];
		} else {
			formData.categories = formData.categories.filter(id => id !== categoryId);
		}
		
		handleFieldChange('categories', formData.categories);
	}

	// Schedule auto-save
	function scheduleAutoSave() {
		if (autoSaveTimer) {
			clearTimeout(autoSaveTimer);
		}
		
		autoSaveTimer = setTimeout(() => {
			if (validateForm()) {
				saveWorker(true); // Silent save
			}
		}, 2000); // 2 second delay
	}

	// Save worker
	async function saveWorker(silent = false) {
		if (!validateForm()) {
			if (!silent) {
				toast.error($t('worker.validationError'));
			}
			return false;
		}

		try {
			saving = true;
			error = null;
			
			// Prepare data for API
			const workerData = {
				...formData,
				hourly_rate: parseFloat(formData.hourly_rate) || 0,
				max_concurrent_jobs: parseInt(formData.max_concurrent_jobs) || 3
			};
			
			let result;
			if (isEditing) {
				result = await updateWorker(workerId, workerData);
				if (!silent) {
					toast.success($t('worker.updateSuccess'));
				}
			} else {
				result = await createWorker(workerData);
				toast.success($t('worker.createSuccess'));
			}
			
			// Call success callback if provided
			if (onSuccess) {
				onSuccess(result);
			}
			
			// Redirect if not embedded
			if (!embedded && !isEditing) {
				goto('/dashboard/workers');
			}
			
			return true;
		} catch (err) {
			error = err.message;
			if (!silent) {
				toast.error(isEditing ? $t('worker.updateError') : $t('worker.createError'));
			}
			return false;
		} finally {
			saving = false;
		}
	}

	// Handle tab change
	function handleTabChange(event) {
		currentStep = event.detail.id;
	}

	// Step navigation
	function nextStep() {
		if (currentStep < tabs.length) {
			currentStep++;
		}
	}

	function prevStep() {
		if (currentStep > 1) {
			currentStep--;
		}
	}

	// Cancel form
	function cancelForm() {
		if (embedded) {
			if (typeof onCancel === 'function') {
				onCancel();
			}
		} else {
			goto('/dashboard/workers');
		}
	}

	// Get today's date in YYYY-MM-DD format
	function getTodayDate() {
		return new Date().toISOString().split('T')[0];
	}
</script>

<svelte:head>
	<title>
		{isEditing ? $t('worker.edit') : $t('worker.create')} - {$t('app.name')}
	</title>
</svelte:head>

<div class="max-w-4xl mx-auto space-y-6">
	<!-- Header -->
	{#if !embedded}
		<div class="border-b border-gray-200 pb-5 dark:border-gray-700">
			<h1 class="text-2xl font-bold text-gray-900 dark:text-white">
				{isEditing ? $t('worker.edit') : $t('worker.create')}
			</h1>
			<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
				{isEditing ? $t('worker.editDescription') : $t('worker.createDescription')}
			</p>
		</div>
	{/if}

	<!-- Loading State -->
	{#if loading}
		<LoadingSkeleton type="rect" height="400px" />
	
	<!-- Error Alert -->
	{:else if error}
		<Alert type="error" title={$t('error.title')} message={error} dismissible />
	
	<!-- Form -->
	{:else}
		<div class="bg-white dark:bg-gray-800 shadow-sm rounded-lg overflow-hidden">
			<!-- Progress Steps -->
			<div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
				<Tabs 
					bind:activeTab={currentStep}
					{tabs}
					variant="pills"
					on:change={handleTabChange}
				/>
			</div>

			<!-- Auto-save indicator -->
			{#if autoSaveEnabled && isEditing}
				<div class="px-6 py-2 bg-blue-50 dark:bg-blue-900/20 border-b border-blue-200 dark:border-blue-800">
					<div class="flex items-center text-sm text-blue-700 dark:text-blue-300">
						<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
						</svg>
						{$t('common.autoSaveEnabled')}
					</div>
				</div>
			{/if}

			<!-- Form Content -->
			<div class="p-6">
				<!-- Step 1: Personal Information -->
				{#if currentStep === 1}
					<div class="space-y-6">
						<h3 class="text-lg font-medium text-gray-900 dark:text-white">
							{$t('worker.personalInfo')}
						</h3>
						
						<div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
							<!-- First Name -->
							<div>
								<label for="first_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('worker.firstName')} *
								</label>
								<input
									type="text"
									id="first_name"
									value={formData.first_name}
									oninput={(e) => handleFieldChange('first_name', e.target.value)}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
									class:border-red-500={validationErrors.first_name}
									placeholder={$t('worker.firstNamePlaceholder')}
								/>
								{#if validationErrors.first_name}
									<p class="mt-1 text-sm text-red-600">{validationErrors.first_name}</p>
								{/if}
							</div>

							<!-- Last Name -->
							<div>
								<label for="last_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('worker.lastName')} *
								</label>
								<input
									type="text"
									id="last_name"
									value={formData.last_name}
									oninput={(e) => handleFieldChange('last_name', e.target.value)}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
									class:border-red-500={validationErrors.last_name}
									placeholder={$t('worker.lastNamePlaceholder')}
								/>
								{#if validationErrors.last_name}
									<p class="mt-1 text-sm text-red-600">{validationErrors.last_name}</p>
								{/if}
							</div>

							<!-- Email -->
							<div>
								<label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('worker.email')} *
								</label>
								<input
									type="email"
									id="email"
									value={formData.email}
									oninput={(e) => handleFieldChange('email', e.target.value)}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
									class:border-red-500={validationErrors.email}
									placeholder="worker@example.com"
								/>
								{#if validationErrors.email}
									<p class="mt-1 text-sm text-red-600">{validationErrors.email}</p>
								{/if}
							</div>

							<!-- Phone -->
							<div>
								<label for="phone" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('worker.phone')} *
								</label>
								<input
									type="tel"
									id="phone"
									value={formData.phone}
									oninput={(e) => handleFieldChange('phone', e.target.value)}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
									class:border-red-500={validationErrors.phone}
									placeholder="+966 50 123 4567"
								/>
								{#if validationErrors.phone}
									<p class="mt-1 text-sm text-red-600">{validationErrors.phone}</p>
								{/if}
							</div>

							<!-- Date of Birth -->
							<div>
								<label for="date_of_birth" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('worker.dateOfBirth')}
								</label>
								<input
									type="date"
									id="date_of_birth"
									value={formData.date_of_birth}
									oninput={(e) => handleFieldChange('date_of_birth', e.target.value)}
									max={getTodayDate()}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
									class:border-red-500={validationErrors.date_of_birth}
								/>
								{#if validationErrors.date_of_birth}
									<p class="mt-1 text-sm text-red-600">{validationErrors.date_of_birth}</p>
								{/if}
							</div>
						</div>

						<!-- Address -->
						<div>
							<label for="address" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
								{$t('worker.address')}
							</label>
							<textarea
								id="address"
								rows="3"
								value={formData.address}
								oninput={(e) => handleFieldChange('address', e.target.value)}
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
								placeholder={$t('worker.addressPlaceholder')}
							></textarea>
						</div>
					</div>
				
				<!-- Step 2: Skills & Categories -->
				{:else if currentStep === 2}
					<div class="space-y-6">
						<h3 class="text-lg font-medium text-gray-900 dark:text-white">
							{$t('worker.skillsCategories')}
						</h3>
						
						<!-- Categories Selection -->
						<fieldset>
							<legend class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
								{$t('worker.selectCategories')} *
							</legend>
							
							{#if categories.length === 0}
								<p class="text-sm text-gray-500 dark:text-gray-400">
									{$t('worker.noCategoriesAvailable')}
								</p>
							{:else}
								<div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
									{#each categories as category}
										<label class="relative flex items-start p-3 border border-gray-200 dark:border-gray-600 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700">
											<div class="flex h-5 items-center">
												<input
													type="checkbox"
													checked={formData.categories.includes(category.id)}
													onchange={(e) => handleCategoryChange(category.id, e.target.checked)}
													class="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700"
												/>
											</div>
											<div class="ml-3 min-w-0 flex-1">
												<div class="text-sm font-medium text-gray-900 dark:text-white">
													{category.name}
												</div>
												{#if category.description}
													<div class="text-xs text-gray-500 dark:text-gray-400">
														{category.description}
													</div>
												{/if}
												{#if category.hourly_rate_min && category.hourly_rate_max}
													<div class="text-xs text-gray-600 dark:text-gray-400 mt-1">
														{$t('worker.rateRange')}: {formatHourlyRate(category.hourly_rate_min)} - {formatHourlyRate(category.hourly_rate_max)}
													</div>
												{/if}
											</div>
										</label>
									{/each}
								</div>
							{/if}
							
							{#if validationErrors.categories}
								<p class="mt-1 text-sm text-red-600">{validationErrors.categories}</p>
							{/if}
						</fieldset>

						<!-- Selected Categories Summary -->
						{#if selectedCategories.length > 0}
							<div class="rounded-lg bg-blue-50 p-4 dark:bg-blue-900/20">
								<h4 class="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
									{$t('worker.selectedCategories')} ({selectedCategories.length})
								</h4>
								<div class="flex flex-wrap gap-2">
									{#each selectedCategories as category}
										<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200">
											{category.name}
										</span>
									{/each}
								</div>
							</div>
						{/if}
					</div>
				
				<!-- Step 3: Employment Details -->
				{:else if currentStep === 3}
					<div class="space-y-6">
						<h3 class="text-lg font-medium text-gray-900 dark:text-white">
							{$t('worker.employmentDetails')}
						</h3>
						
						<div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
							<!-- Employment Type -->
							<div>
								<label for="employment_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('worker.employmentType')} *
								</label>
								<select
									id="employment_type"
									bind:value={formData.employment_type}
									onchange={(e) => handleFieldChange('employment_type', e.target.value)}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
								>
									{#each employmentTypes as type}
										<option value={type.value}>{type.label}</option>
									{/each}
								</select>
							</div>

							<!-- Status -->
							<div>
								<label for="status" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('common.status')}
								</label>
								<select
									id="status"
									bind:value={formData.status}
									onchange={(e) => handleFieldChange('status', e.target.value)}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
								>
									{#each workerStatuses as status}
										<option value={status.value}>{status.label}</option>
									{/each}
								</select>
							</div>

							<!-- Hire Date -->
							<div>
								<label for="hire_date" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('worker.hireDate')}
								</label>
								<input
									type="date"
									id="hire_date"
									value={formData.hire_date}
									oninput={(e) => handleFieldChange('hire_date', e.target.value)}
									max={getTodayDate()}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
									class:border-red-500={validationErrors.hire_date}
								/>
								{#if validationErrors.hire_date}
									<p class="mt-1 text-sm text-red-600">{validationErrors.hire_date}</p>
								{/if}
							</div>

							<!-- Hourly Rate -->
							<div>
								<label for="hourly_rate" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('worker.hourlyRate')} *
								</label>
								<div class="relative mt-1 rounded-md shadow-sm">
									<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
										<span class="text-gray-500 sm:text-sm">$</span>
									</div>
									<input
										type="number"
										id="hourly_rate"
										step="0.01"
										min="0"
										value={formData.hourly_rate}
										oninput={(e) => handleFieldChange('hourly_rate', e.target.value)}
										class="block w-full rounded-md border-gray-300 pl-7 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
										class:border-red-500={validationErrors.hourly_rate}
										placeholder="0.00"
									/>
								</div>
								{#if validationErrors.hourly_rate}
									<p class="mt-1 text-sm text-red-600">{validationErrors.hourly_rate}</p>
								{/if}
							</div>

							<!-- Max Concurrent Jobs -->
							<div>
								<label for="max_concurrent_jobs" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('worker.maxConcurrentJobs')}
								</label>
								<input
									type="number"
									id="max_concurrent_jobs"
									min="1"
									max="10"
									value={formData.max_concurrent_jobs}
									oninput={(e) => handleFieldChange('max_concurrent_jobs', e.target.value)}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
									class:border-red-500={validationErrors.max_concurrent_jobs}
								/>
								{#if validationErrors.max_concurrent_jobs}
									<p class="mt-1 text-sm text-red-600">{validationErrors.max_concurrent_jobs}</p>
								{/if}
								<p class="mt-1 text-xs text-gray-500">
									{$t('worker.maxConcurrentJobsHelp')}
								</p>
							</div>
						</div>

						<!-- Available for Work -->
						<div class="flex items-start">
							<div class="flex h-5 items-center">
								<input
									id="is_available"
									type="checkbox"
									bind:checked={formData.is_available}
									onchange={(e) => handleFieldChange('is_available', e.target.checked)}
									class="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700"
								/>
							</div>
							<div class="ml-3 text-sm">
								<label for="is_available" class="font-medium text-gray-700 dark:text-gray-300">
									{$t('worker.availableForWork')}
								</label>
								<p class="text-gray-500 dark:text-gray-400">
									{$t('worker.availableForWorkDescription')}
								</p>
							</div>
						</div>

						<!-- Notes -->
						<div>
							<label for="notes" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
								{$t('common.notes')}
							</label>
							<textarea
								id="notes"
								rows="4"
								value={formData.notes}
								oninput={(e) => handleFieldChange('notes', e.target.value)}
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
								placeholder={$t('worker.notesPlaceholder')}
							></textarea>
						</div>
					</div>
				{/if}
			</div>

			<!-- Form Actions -->
			<div class="bg-gray-50 px-6 py-3 text-right dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600">
				<div class="flex justify-between">
					<div>
						{#if currentStep > 1}
							<Button onClick={prevStep} variant="outline" class="mr-3">
								{$t('common.previous')}
							</Button>
						{/if}
					</div>

					<div class="flex space-x-3">
						<Button onClick={cancelForm} variant="outline">
							{$t('common.cancel')}
						</Button>

						{#if currentStep < tabs.length}
							<Button onClick={nextStep} variant="primary" disabled={!canProceed}>
								{$t('common.next')}
							</Button>
						{:else}
							<Button 
								onClick={() => saveWorker()} 
								variant="primary" 
								loading={saving}
								disabled={!canProceed}
							>
								{isEditing ? $t('common.update') : $t('common.create')}
							</Button>
						{/if}
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>