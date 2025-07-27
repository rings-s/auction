<!-- src/routes/property-management/expenses/create/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t, locale } from '$lib/i18n';
	import { user } from '$lib/stores/user.svelte.js';
	import { fade, slide } from 'svelte/transition';
	import Button from '$lib/components/ui/Button.svelte';
	import LoadingSpinner from '$lib/components/animations/LoadingSpinner.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import FileUploader from '$lib/components/ui/FileUploader.svelte';
	import { getProperties } from '$lib/api/property.js';
	import { api } from '$lib/utils/api.js';

	let isRTL = $derived($locale === 'ar');

	// Permission check
	let hasAccess = $derived(
		($user && ['owner', 'appraiser', 'data_entry'].includes($user.role)) || $user?.is_superuser
	);

	// State management
	let loading = $state(false);
	let saving = $state(false);
	let error = $state('');
	let validationErrors = $state({});
	let showSuccessModal = $state(false);
	let properties = $state([]);
	let currentStep = $state(1);
	let totalSteps = 5;

	// Form data with Svelte 5 state
	let formData = $state({
		// Basic Information
		title: '',
		description: '',
		category: '',
		amount: '',
		currency: 'USD',
		expense_date: new Date().toISOString().split('T')[0],

		// Property & Classification
		property: { id: '', title: '', address: '' },
		is_recurring: false,
		recurring_frequency: 'monthly',
		vendor_name: '',
		payment_method: 'cash',

		// Details & Documentation
		reference_number: '',
		tax_deductible: false,
		tax_category: '',
		approval_status: 'pending',
		notes: '',

		// Files
		receipt_files: [],
		supporting_documents: []
	});

	// Step configuration
	const steps = [
		{
			id: 1,
			title: $t('expense.steps.basic'),
			description: $t('expense.steps.basicDesc'),
			icon: '💰',
			fields: ['title', 'description', 'amount']
		},
		{
			id: 2,
			title: $t('expense.steps.category'),
			description: $t('expense.steps.categoryDesc'),
			icon: '📊',
			fields: ['category', 'property']
		},
		{
			id: 3,
			title: $t('expense.steps.details'),
			description: $t('expense.steps.detailsDesc'),
			icon: '🔍',
			fields: ['vendor_name', 'payment_method']
		},
		{
			id: 4,
			title: $t('expense.steps.tax'),
			description: $t('expense.steps.taxDesc'),
			icon: '📋',
			fields: ['tax_deductible', 'tax_category']
		},
		{
			id: 5,
			title: $t('expense.steps.documents'),
			description: $t('expense.steps.documentsDesc'),
			icon: '📎',
			fields: ['receipt_files']
		}
	];

	// Options data
	const expenseCategories = [
		{ value: 'maintenance', label: $t('expense.category.maintenance'), icon: '🔧' },
		{ value: 'utilities', label: $t('expense.category.utilities'), icon: '⚡' },
		{ value: 'insurance', label: $t('expense.category.insurance'), icon: '🛡️' },
		{ value: 'taxes', label: $t('expense.category.taxes'), icon: '📊' },
		{ value: 'legal', label: $t('expense.category.legal'), icon: '⚖️' },
		{ value: 'marketing', label: $t('expense.category.marketing'), icon: '📢' },
		{ value: 'management', label: $t('expense.category.management'), icon: '👥' },
		{ value: 'improvement', label: $t('expense.category.improvement'), icon: '🏗️' },
		{ value: 'other', label: $t('expense.category.other'), icon: '📝' }
	];

	const paymentMethods = [
		{ value: 'cash', label: $t('expense.payment.cash'), icon: '💵' },
		{ value: 'bank-transfer', label: $t('expense.payment.bankTransfer'), icon: '🏦' },
		{ value: 'credit-card', label: $t('expense.payment.creditCard'), icon: '💳' },
		{ value: 'check', label: $t('expense.payment.check'), icon: '📝' },
		{ value: 'online', label: $t('expense.payment.online'), icon: '🌐' }
	];

	const currencies = [
		{ value: 'USD', label: 'USD ($)', symbol: '$' },
		{ value: 'EUR', label: 'EUR (€)', symbol: '€' },
		{ value: 'GBP', label: 'GBP (£)', symbol: '£' },
		{ value: 'SAR', label: 'SAR (ر.س)', symbol: 'ر.س' },
		{ value: 'AED', label: 'AED (د.إ)', symbol: 'د.إ' }
	];

	const recurringFrequencies = [
		{ value: 'monthly', label: $t('expense.recurring.monthly') },
		{ value: 'quarterly', label: $t('expense.recurring.quarterly') },
		{ value: 'yearly', label: $t('expense.recurring.yearly') }
	];

	const taxCategories = [
		{ value: 'deductible', label: $t('expense.tax.deductible') },
		{ value: 'non-deductible', label: $t('expense.tax.nonDeductible') },
		{ value: 'partial', label: $t('expense.tax.partial') },
		{ value: 'capital', label: $t('expense.tax.capital') }
	];

	// Computed properties
	let progressPercentage = $derived((currentStep / totalSteps) * 100);
	let canProceed = $derived(validateCurrentStep());
	let currentStepData = $derived(steps.find((s) => s.id === currentStep));
	let selectedCurrency = $derived(currencies.find((c) => c.value === formData.currency));

	onMount(() => {
		if (!hasAccess) {
			goto('/property-management/expenses');
			return;
		}
		loadProperties();
	});

	async function loadProperties() {
		try {
			loading = true;
			const response = await getProperties();
			properties = Array.isArray(response) ? response : response.results || response.data || [];
		} catch (err) {
			console.error('Failed to load properties:', err);
			properties = [];
		} finally {
			loading = false;
		}
	}

	function validateCurrentStep() {
		const currentFields = currentStepData?.fields || [];

		switch (currentStep) {
			case 1:
				return formData.title.trim() && formData.amount && parseFloat(formData.amount) > 0;
			case 2:
				return formData.category && formData.property.id;
			case 3:
				return formData.vendor_name.trim() && formData.payment_method;
			case 4:
				return true; // Tax information is optional
			case 5:
				return true; // Documents are optional
			default:
				return false;
		}
	}

	function validateForm() {
		const errors = {};

		// Basic validation
		if (!formData.title?.trim()) {
			errors.title = $t('validation.required');
		}

		if (!formData.amount || parseFloat(formData.amount) <= 0) {
			errors.amount = $t('validation.mustBePositive');
		}

		if (!formData.category) {
			errors.category = $t('validation.required');
		}

		if (!formData.property.id) {
			errors.property = $t('validation.required');
		}

		if (!formData.vendor_name?.trim()) {
			errors.vendor_name = $t('validation.required');
		}

		if (!formData.payment_method) {
			errors.payment_method = $t('validation.required');
		}

		// Date validation
		if (formData.expense_date && new Date(formData.expense_date) > new Date()) {
			errors.expense_date = $t('validation.dateCannotBeFuture');
		}

		return errors;
	}

	async function handleSubmit() {
		try {
			saving = true;
			validationErrors = {};

			const errors = validateForm();
			if (Object.keys(errors).length > 0) {
				validationErrors = errors;
				currentStep = 1; // Go back to first step with errors
				return;
			}

			// Prepare form data for submission
			const expenseData = new FormData();

			// Add basic fields
			expenseData.append('title', formData.title);
			expenseData.append('description', formData.description);
			expenseData.append('category', formData.category);
			expenseData.append('amount', parseFloat(formData.amount));
			expenseData.append('currency', formData.currency);
			expenseData.append('expense_date', formData.expense_date);
			expenseData.append('property', formData.property.id);
			expenseData.append('vendor_name', formData.vendor_name);
			expenseData.append('payment_method', formData.payment_method);
			expenseData.append('is_recurring', formData.is_recurring);
			expenseData.append('tax_deductible', formData.tax_deductible);
			expenseData.append('approval_status', formData.approval_status);
			expenseData.append('notes', formData.notes);

			// Add optional fields
			if (formData.reference_number) {
				expenseData.append('reference_number', formData.reference_number);
			}
			if (formData.is_recurring) {
				expenseData.append('recurring_frequency', formData.recurring_frequency);
			}
			if (formData.tax_deductible && formData.tax_category) {
				expenseData.append('tax_category', formData.tax_category);
			}

			// Add files
			formData.receipt_files.forEach((file, index) => {
				expenseData.append(`receipt_files`, file);
			});
			formData.supporting_documents.forEach((file, index) => {
				expenseData.append(`supporting_documents`, file);
			});

			const response = await api.post('/api/property-management/expenses/', expenseData, {
				headers: {
					'Content-Type': 'multipart/form-data'
				}
			});

			showSuccessModal = true;
		} catch (err) {
			error = err.message || $t('error.saveFailed');
			console.error('Failed to create expense:', err);
		} finally {
			saving = false;
		}
	}

	function handleNext() {
		if (canProceed && currentStep < totalSteps) {
			currentStep++;
		}
	}

	function handlePrevious() {
		if (currentStep > 1) {
			currentStep--;
		}
	}

	function handleStepClick(step) {
		if (step <= currentStep || validateStepsUpTo(step - 1)) {
			currentStep = step;
		}
	}

	function validateStepsUpTo(stepNumber) {
		for (let i = 1; i <= stepNumber; i++) {
			// This would need actual validation logic for each step
			// For now, allowing navigation
		}
		return true;
	}

	function handlePropertySelect(property) {
		formData.property = {
			id: property.id,
			title: property.title,
			address: property.location_data
				? `${property.location_data.city}, ${property.location_data.state}`
				: property.address || ''
		};
	}

	function handleSuccess() {
		showSuccessModal = false;
		goto('/property-management/expenses');
	}

	function handleCancel() {
		goto('/property-management/expenses');
	}

	function formatAmount(amount) {
		if (!amount) return '';
		const symbol = selectedCurrency?.symbol || '$';
		return `${symbol}${parseFloat(amount).toLocaleString()}`;
	}
</script>

<svelte:head>
	<title>{$t('expense.createTitle')} | {$t('propertyManagement.title')} | {$t('app.name')}</title>
	<meta name="description" content={$t('expense.createDescription')} />
</svelte:head>

<div
	class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-gray-900 dark:via-blue-900 dark:to-indigo-900"
	dir={isRTL ? 'rtl' : 'ltr'}
>
	<div class="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
		<!-- Header -->
		<div class="mb-8">
			<button
				onclick={handleCancel}
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
				{$t('expense.backToExpenses')}
			</button>

			<div class="flex items-center justify-between">
				<div>
					<h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">
						{$t('expense.createTitle')}
					</h1>
					<p class="mt-2 text-gray-600 dark:text-gray-400">
						{$t('expense.createSubtitle')}
					</p>
				</div>

				<!-- Progress Indicator -->
				<div class="hidden sm:block">
					<div class="flex items-center space-x-2">
						<span class="text-sm font-medium text-gray-600 dark:text-gray-400">
							{$t('common.step')}
							{currentStep}
							{$t('common.of')}
							{totalSteps}
						</span>
						<div class="h-2 w-32 rounded-full bg-gray-200 dark:bg-gray-700">
							<div
								class="h-2 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 transition-all duration-500 ease-out"
								style="width: {progressPercentage}%"
							></div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Permission Check -->
		{#if !hasAccess}
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
						<p class="text-base">{$t('error.insufficientPermissions')}</p>
					</div>
				</div>
			</div>
		{:else}
			<!-- Main Content -->
			<div class="space-y-8">
				<!-- Progress Steps -->
				<div
					class="rounded-2xl border border-gray-200 bg-white p-6 shadow-xl dark:border-gray-700 dark:bg-gray-800"
				>
					<div class="flex items-center justify-between">
						{#each steps as step, index}
							<div class="relative flex flex-col items-center">
								{#if index < steps.length - 1}
									<div
										class="absolute top-6 {isRTL
											? 'right-10'
											: 'left-10'} h-0.5 w-20 bg-gray-200 dark:bg-gray-600 {step.id <= currentStep
											? 'bg-gradient-to-r from-blue-500 to-indigo-600'
											: ''}"
									></div>
								{/if}

								<button
									onclick={() => handleStepClick(step.id)}
									class="flex h-12 w-12 items-center justify-center rounded-full text-lg font-semibold transition-all duration-300 {step.id ===
									currentStep
										? 'scale-110 bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg'
										: step.id < currentStep
											? 'bg-green-500 text-white'
											: 'bg-gray-200 text-gray-500 dark:bg-gray-700 dark:text-gray-400'} hover:scale-105"
									disabled={step.id > currentStep && !validateStepsUpTo(step.id - 1)}
								>
									{step.id < currentStep ? '✓' : step.icon}
								</button>

								<div class="mt-2 text-center">
									<div class="text-xs font-medium text-gray-900 dark:text-gray-100">
										{step.title}
									</div>
									<div class="mt-1 max-w-20 text-xs text-gray-500 dark:text-gray-400">
										{step.description}
									</div>
								</div>
							</div>
						{/each}
					</div>
				</div>

				<!-- Error Display -->
				{#if error}
					<div
						class="rounded-2xl border border-red-200 bg-red-50 p-6 shadow-lg dark:border-red-800 dark:bg-red-900/20"
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

				<!-- Step Content -->
				<div
					class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
					transition:fade={{ duration: 300 }}
				>
					<!-- Step 1: Basic Information -->
					{#if currentStep === 1}
						<div class="bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-600 p-6 text-white">
							<h2 class="flex items-center text-2xl font-bold">
								<span class="mr-4 text-3xl">💰</span>
								{$t('expense.steps.basic')}
							</h2>
							<p class="mt-2 text-blue-100">{$t('expense.steps.basicDesc')}</p>
						</div>

						<div class="space-y-6 p-8">
							<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
								<!-- Title -->
								<div class="md:col-span-2">
									<label
										for="title"
										class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
									>
										{$t('expense.title')} <span class="text-red-500">*</span>
									</label>
									<input
										type="text"
										id="title"
										bind:value={formData.title}
										class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
											text-gray-900 transition-all duration-200
											focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
											dark:bg-gray-700 dark:text-gray-100
											{validationErrors.title ? 'border-red-500 focus:ring-red-500' : ''}"
										placeholder={$t('expense.titlePlaceholder')}
										required
									/>
									{#if validationErrors.title}
										<p class="mt-2 text-sm text-red-600 dark:text-red-400">
											{validationErrors.title}
										</p>
									{/if}
								</div>

								<!-- Amount -->
								<div>
									<label
										for="amount"
										class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
									>
										{$t('expense.amount')} <span class="text-red-500">*</span>
									</label>
									<div class="relative">
										<div
											class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3"
										>
											<span class="text-lg text-gray-500 dark:text-gray-400">
												{selectedCurrency?.symbol || '$'}
											</span>
										</div>
										<input
											type="number"
											id="amount"
											bind:value={formData.amount}
											min="0"
											step="0.01"
											class="w-full rounded-xl border border-gray-300 bg-white py-3 pr-4 pl-10
												text-gray-900 transition-all duration-200
												focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
												dark:bg-gray-700 dark:text-gray-100
												{validationErrors.amount ? 'border-red-500 focus:ring-red-500' : ''}"
											placeholder="0.00"
											required
										/>
									</div>
									{#if validationErrors.amount}
										<p class="mt-2 text-sm text-red-600 dark:text-red-400">
											{validationErrors.amount}
										</p>
									{/if}
								</div>

								<!-- Currency -->
								<div>
									<label
										for="currency"
										class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
									>
										{$t('expense.currency')}
									</label>
									<select
										id="currency"
										bind:value={formData.currency}
										class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
											text-gray-900 transition-all duration-200
											focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
											dark:bg-gray-700 dark:text-gray-100"
									>
										{#each currencies as currency}
											<option value={currency.value}>{currency.label}</option>
										{/each}
									</select>
								</div>

								<!-- Date -->
								<div>
									<label
										for="expense_date"
										class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
									>
										{$t('expense.date')}
									</label>
									<input
										type="date"
										id="expense_date"
										bind:value={formData.expense_date}
										class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
											text-gray-900 transition-all duration-200
											focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
											dark:bg-gray-700 dark:text-gray-100
											{validationErrors.expense_date ? 'border-red-500 focus:ring-red-500' : ''}"
									/>
									{#if validationErrors.expense_date}
										<p class="mt-2 text-sm text-red-600 dark:text-red-400">
											{validationErrors.expense_date}
										</p>
									{/if}
								</div>

								<!-- Description -->
								<div class="md:col-span-2">
									<label
										for="description"
										class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
									>
										{$t('expense.description')}
									</label>
									<textarea
										id="description"
										bind:value={formData.description}
										rows="3"
										class="w-full resize-none rounded-xl border border-gray-300 bg-white px-4
											py-3 text-gray-900 transition-all
											duration-200 focus:border-transparent focus:ring-2 focus:ring-blue-500
											dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
										placeholder={$t('expense.descriptionPlaceholder')}
									></textarea>
								</div>
							</div>
						</div>

						<!-- Step 2: Category & Property -->
					{:else if currentStep === 2}
						<div class="bg-gradient-to-r from-green-500 via-teal-500 to-cyan-600 p-6 text-white">
							<h2 class="flex items-center text-2xl font-bold">
								<span class="mr-4 text-3xl">📊</span>
								{$t('expense.steps.category')}
							</h2>
							<p class="mt-2 text-green-100">{$t('expense.steps.categoryDesc')}</p>
						</div>

						<div class="space-y-6 p-8">
							<!-- Category Selection -->
							<div>
								<label class="mb-4 block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('expense.category')} <span class="text-red-500">*</span>
								</label>
								<div class="grid grid-cols-2 gap-4 md:grid-cols-3">
									{#each expenseCategories as category}
										<button
											type="button"
											onclick={() => (formData.category = category.value)}
											class="rounded-xl border-2 p-4 transition-all duration-200 hover:scale-105 {formData.category ===
											category.value
												? 'border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300'
												: 'border-gray-200 hover:border-blue-300 dark:border-gray-600 dark:hover:border-blue-500'}"
										>
											<div class="mb-2 text-2xl">{category.icon}</div>
											<div class="text-sm font-medium">{category.label}</div>
										</button>
									{/each}
								</div>
								{#if validationErrors.category}
									<p class="mt-2 text-sm text-red-600 dark:text-red-400">
										{validationErrors.category}
									</p>
								{/if}
							</div>

							<!-- Property Selection -->
							<div>
								<label class="mb-4 block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('expense.property')} <span class="text-red-500">*</span>
								</label>
								{#if loading}
									<div class="animate-pulse">
										<div class="h-20 rounded-xl bg-gray-200 dark:bg-gray-700"></div>
									</div>
								{:else if properties.length === 0}
									<div class="rounded-xl bg-gray-50 py-8 text-center dark:bg-gray-700">
										<p class="text-gray-500 dark:text-gray-400">
											{$t('property.noPropertiesFound')}
										</p>
									</div>
								{:else}
									<div class="max-h-64 space-y-3 overflow-y-auto">
										{#each properties as property}
											<button
												type="button"
												onclick={() => handlePropertySelect(property)}
												class="w-full rounded-xl border-2 p-4 text-left transition-all duration-200 hover:scale-[1.02] {formData
													.property.id === property.id
													? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
													: 'border-gray-200 hover:border-blue-300 dark:border-gray-600 dark:hover:border-blue-500'}"
											>
												<div class="flex items-center">
													<div
														class="mr-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 text-lg font-bold text-white"
													>
														{property.title?.charAt(0)?.toUpperCase() || 'P'}
													</div>
													<div class="flex-1">
														<h3 class="font-semibold text-gray-900 dark:text-gray-100">
															{property.title}
														</h3>
														<p class="text-sm text-gray-600 dark:text-gray-400">
															{property.location_data
																? `${property.location_data.city}, ${property.location_data.state}`
																: property.address || ''}
														</p>
													</div>
													{#if formData.property.id === property.id}
														<svg
															class="h-6 w-6 text-blue-500"
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
													{/if}
												</div>
											</button>
										{/each}
									</div>
								{/if}
								{#if validationErrors.property}
									<p class="mt-2 text-sm text-red-600 dark:text-red-400">
										{validationErrors.property}
									</p>
								{/if}
							</div>

							<!-- Recurring Expense Option -->
							<div class="rounded-xl bg-gray-50 p-4 dark:bg-gray-700">
								<label class="flex items-center space-x-3">
									<input
										type="checkbox"
										bind:checked={formData.is_recurring}
										class="h-5 w-5 rounded border-2 border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500"
									/>
									<div>
										<div class="font-medium text-gray-900 dark:text-gray-100">
											{$t('expense.recurringExpense')}
										</div>
										<div class="text-sm text-gray-600 dark:text-gray-400">
											{$t('expense.recurringExpenseDesc')}
										</div>
									</div>
								</label>

								{#if formData.is_recurring}
									<div class="mt-4">
										<label
											for="recurring_frequency"
											class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
										>
											{$t('expense.recurringFrequency')}
										</label>
										<select
											id="recurring_frequency"
											bind:value={formData.recurring_frequency}
											class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
												text-gray-900 transition-all duration-200
												focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
												dark:bg-gray-700 dark:text-gray-100"
										>
											{#each recurringFrequencies as frequency}
												<option value={frequency.value}>{frequency.label}</option>
											{/each}
										</select>
									</div>
								{/if}
							</div>
						</div>

						<!-- Step 3: Details -->
					{:else if currentStep === 3}
						<div class="bg-gradient-to-r from-purple-500 via-pink-500 to-red-500 p-6 text-white">
							<h2 class="flex items-center text-2xl font-bold">
								<span class="mr-4 text-3xl">🔍</span>
								{$t('expense.steps.details')}
							</h2>
							<p class="mt-2 text-purple-100">{$t('expense.steps.detailsDesc')}</p>
						</div>

						<div class="space-y-6 p-8">
							<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
								<!-- Vendor Name -->
								<div>
									<label
										for="vendor_name"
										class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
									>
										{$t('expense.vendorName')} <span class="text-red-500">*</span>
									</label>
									<input
										type="text"
										id="vendor_name"
										bind:value={formData.vendor_name}
										class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
											text-gray-900 transition-all duration-200
											focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
											dark:bg-gray-700 dark:text-gray-100
											{validationErrors.vendor_name ? 'border-red-500 focus:ring-red-500' : ''}"
										placeholder={$t('expense.vendorNamePlaceholder')}
										required
									/>
									{#if validationErrors.vendor_name}
										<p class="mt-2 text-sm text-red-600 dark:text-red-400">
											{validationErrors.vendor_name}
										</p>
									{/if}
								</div>

								<!-- Reference Number -->
								<div>
									<label
										for="reference_number"
										class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
									>
										{$t('expense.referenceNumber')}
									</label>
									<input
										type="text"
										id="reference_number"
										bind:value={formData.reference_number}
										class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
											text-gray-900 transition-all duration-200
											focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
											dark:bg-gray-700 dark:text-gray-100"
										placeholder={$t('expense.referenceNumberPlaceholder')}
									/>
								</div>
							</div>

							<!-- Payment Method -->
							<div>
								<label class="mb-4 block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('expense.paymentMethod')} <span class="text-red-500">*</span>
								</label>
								<div class="grid grid-cols-2 gap-4 md:grid-cols-5">
									{#each paymentMethods as method}
										<button
											type="button"
											onclick={() => (formData.payment_method = method.value)}
											class="rounded-xl border-2 p-4 transition-all duration-200 hover:scale-105 {formData.payment_method ===
											method.value
												? 'border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300'
												: 'border-gray-200 hover:border-blue-300 dark:border-gray-600 dark:hover:border-blue-500'}"
										>
											<div class="mb-2 text-2xl">{method.icon}</div>
											<div class="text-sm font-medium">{method.label}</div>
										</button>
									{/each}
								</div>
								{#if validationErrors.payment_method}
									<p class="mt-2 text-sm text-red-600 dark:text-red-400">
										{validationErrors.payment_method}
									</p>
								{/if}
							</div>

							<!-- Notes -->
							<div>
								<label
									for="notes"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('expense.notes')}
								</label>
								<textarea
									id="notes"
									bind:value={formData.notes}
									rows="4"
									class="w-full resize-none rounded-xl border border-gray-300 bg-white px-4
										py-3 text-gray-900 transition-all
										duration-200 focus:border-transparent focus:ring-2 focus:ring-blue-500
										dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
									placeholder={$t('expense.notesPlaceholder')}
								></textarea>
							</div>
						</div>

						<!-- Step 4: Tax Information -->
					{:else if currentStep === 4}
						<div class="bg-gradient-to-r from-yellow-500 via-orange-500 to-red-500 p-6 text-white">
							<h2 class="flex items-center text-2xl font-bold">
								<span class="mr-4 text-3xl">📋</span>
								{$t('expense.steps.tax')}
							</h2>
							<p class="mt-2 text-yellow-100">{$t('expense.steps.taxDesc')}</p>
						</div>

						<div class="space-y-6 p-8">
							<!-- Tax Deductible -->
							<div class="rounded-xl bg-gray-50 p-6 dark:bg-gray-700">
								<label class="flex items-center space-x-3">
									<input
										type="checkbox"
										bind:checked={formData.tax_deductible}
										class="h-5 w-5 rounded border-2 border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500"
									/>
									<div>
										<div class="font-medium text-gray-900 dark:text-gray-100">
											{$t('expense.taxDeductible')}
										</div>
										<div class="text-sm text-gray-600 dark:text-gray-400">
											{$t('expense.taxDeductibleDesc')}
										</div>
									</div>
								</label>

								{#if formData.tax_deductible}
									<div class="mt-4">
										<label
											for="tax_category"
											class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
										>
											{$t('expense.taxCategory')}
										</label>
										<select
											id="tax_category"
											bind:value={formData.tax_category}
											class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
												text-gray-900 transition-all duration-200
												focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
												dark:bg-gray-700 dark:text-gray-100"
										>
											<option value="">{$t('common.selectOption')}</option>
											{#each taxCategories as category}
												<option value={category.value}>{category.label}</option>
											{/each}
										</select>
									</div>
								{/if}
							</div>

							<!-- Approval Status -->
							<div>
								<label
									for="approval_status"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('expense.approvalStatus')}
								</label>
								<select
									id="approval_status"
									bind:value={formData.approval_status}
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100"
								>
									<option value="pending">{$t('expense.status.pending')}</option>
									<option value="approved">{$t('expense.status.approved')}</option>
									<option value="rejected">{$t('expense.status.rejected')}</option>
								</select>
							</div>

							<!-- Tax Information Notice -->
							<div
								class="rounded-xl border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-900/20"
							>
								<div class="flex items-start">
									<svg
										class="mt-0.5 mr-3 h-6 w-6 text-blue-500"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
										/>
									</svg>
									<div>
										<h4 class="mb-1 text-sm font-medium text-blue-800 dark:text-blue-200">
											{$t('expense.taxNoticeTitle')}
										</h4>
										<p class="text-sm text-blue-700 dark:text-blue-300">
											{$t('expense.taxNoticeText')}
										</p>
									</div>
								</div>
							</div>
						</div>

						<!-- Step 5: Documents -->
					{:else if currentStep === 5}
						<div class="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-600 p-6 text-white">
							<h2 class="flex items-center text-2xl font-bold">
								<span class="mr-4 text-3xl">📎</span>
								{$t('expense.steps.documents')}
							</h2>
							<p class="mt-2 text-indigo-100">{$t('expense.steps.documentsDesc')}</p>
						</div>

						<div class="space-y-6 p-8">
							<!-- Receipt Files -->
							<div>
								<label class="mb-4 block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('expense.receiptFiles')}
								</label>
								<FileUploader
									files={formData.receipt_files}
									acceptedTypes="image/*,.pdf"
									multiple={true}
									maxSize={10485760}
									on:change={(e) => (formData.receipt_files = e.detail)}
								/>
							</div>

							<!-- Supporting Documents -->
							<div>
								<label class="mb-4 block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('expense.supportingDocuments')}
								</label>
								<FileUploader
									files={formData.supporting_documents}
									acceptedTypes=".pdf,.doc,.docx,.xls,.xlsx"
									multiple={true}
									maxSize={10485760}
									on:change={(e) => (formData.supporting_documents = e.detail)}
								/>
							</div>

							<!-- Upload Guidelines -->
							<div class="rounded-xl bg-gray-50 p-4 dark:bg-gray-700">
								<h4 class="mb-2 text-sm font-medium text-gray-900 dark:text-gray-100">
									{$t('expense.uploadGuidelines')}
								</h4>
								<ul class="space-y-1 text-sm text-gray-600 dark:text-gray-400">
									<li>• {$t('expense.uploadGuideline1')}</li>
									<li>• {$t('expense.uploadGuideline2')}</li>
									<li>• {$t('expense.uploadGuideline3')}</li>
									<li>• {$t('expense.uploadGuideline4')}</li>
								</ul>
							</div>

							<!-- Summary Review -->
							<div
								class="rounded-xl border border-gray-200 bg-gradient-to-r from-gray-50 to-blue-50 p-6 dark:border-gray-600 dark:from-gray-700 dark:to-blue-900/20"
							>
								<h4 class="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
									{$t('expense.expenseSummary')}
								</h4>
								<div class="grid grid-cols-1 gap-4 text-sm md:grid-cols-2">
									<div>
										<span class="font-medium text-gray-600 dark:text-gray-400"
											>{$t('expense.title')}:</span
										>
										<span class="ml-2 text-gray-900 dark:text-gray-100"
											>{formData.title || '-'}</span
										>
									</div>
									<div>
										<span class="font-medium text-gray-600 dark:text-gray-400"
											>{$t('expense.amount')}:</span
										>
										<span class="ml-2 text-lg font-semibold text-gray-900 dark:text-gray-100">
											{formatAmount(formData.amount) || '-'}
										</span>
									</div>
									<div>
										<span class="font-medium text-gray-600 dark:text-gray-400"
											>{$t('expense.category')}:</span
										>
										<span class="ml-2 text-gray-900 dark:text-gray-100">
											{expenseCategories.find((c) => c.value === formData.category)?.label || '-'}
										</span>
									</div>
									<div>
										<span class="font-medium text-gray-600 dark:text-gray-400"
											>{$t('expense.property')}:</span
										>
										<span class="ml-2 text-gray-900 dark:text-gray-100"
											>{formData.property.title || '-'}</span
										>
									</div>
									<div>
										<span class="font-medium text-gray-600 dark:text-gray-400"
											>{$t('expense.vendorName')}:</span
										>
										<span class="ml-2 text-gray-900 dark:text-gray-100"
											>{formData.vendor_name || '-'}</span
										>
									</div>
									<div>
										<span class="font-medium text-gray-600 dark:text-gray-400"
											>{$t('expense.paymentMethod')}:</span
										>
										<span class="ml-2 text-gray-900 dark:text-gray-100">
											{paymentMethods.find((p) => p.value === formData.payment_method)?.label ||
												'-'}
										</span>
									</div>
								</div>
							</div>
						</div>
					{/if}
				</div>

				<!-- Navigation -->
				<div class="flex items-center justify-between">
					<Button
						variant="outline"
						onclick={handlePrevious}
						disabled={currentStep === 1}
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
								d="M10 19l-7-7m0 0l7-7m-7 7h18"
							/>
						</svg>
						{$t('common.previous')}
					</Button>

					<div class="flex gap-3">
						<Button variant="outline" onclick={handleCancel}>
							{$t('common.cancel')}
						</Button>

						{#if currentStep < totalSteps}
							<Button
								variant="primary"
								onclick={handleNext}
								disabled={!canProceed}
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
										d="M14 5l7 7m0 0l-7 7m7-7H3"
									/>
								</svg>
							</Button>
						{:else}
							<Button
								variant="primary"
								onclick={handleSubmit}
								disabled={saving || !canProceed}
								class="min-w-[140px] bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
							>
								{#if saving}
									<LoadingSpinner size="sm" color="white" class="mr-2" />
								{/if}
								{saving ? $t('common.creating') : $t('expense.createExpense')}
							</Button>
						{/if}
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>

<!-- Success Modal -->
<Modal bind:show={showSuccessModal}>
	<div class="p-6 text-center">
		<div
			class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/20"
		>
			<svg class="h-8 w-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
			</svg>
		</div>

		<h3 class="mb-2 text-lg font-semibold text-gray-900 dark:text-gray-100">
			{$t('expense.expenseCreated')}
		</h3>
		<p class="mb-6 text-gray-600 dark:text-gray-400">
			{$t('expense.expenseCreatedMessage')}
		</p>

		<div class="flex justify-center gap-3">
			<Button variant="outline" onclick={() => (showSuccessModal = false)}>
				{$t('expense.createAnother')}
			</Button>
			<Button variant="primary" onclick={handleSuccess}>
				{$t('expense.viewExpenses')}
			</Button>
		</div>
	</div>
</Modal>

<style>
	/* Enhanced animations and transitions */
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
		animation: gradient-shift 6s ease infinite;
	}

	/* Enhanced form field focus states */
	input:focus,
	select:focus,
	textarea:focus {
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
		transform: translateY(-1px);
	}

	/* Custom scrollbar for property list */
	.max-h-64::-webkit-scrollbar {
		width: 6px;
	}

	.max-h-64::-webkit-scrollbar-track {
		background: #f3f4f6;
		border-radius: 3px;
	}

	.max-h-64::-webkit-scrollbar-thumb {
		background: #60a5fa;
		border-radius: 3px;
	}

	.max-h-64::-webkit-scrollbar-thumb:hover {
		background: #2563eb;
	}

	/* Dark mode scrollbar */
	.dark .max-h-64::-webkit-scrollbar-track {
		background: #374151;
	}

	.dark .max-h-64::-webkit-scrollbar-thumb {
		background: #3b82f6;
	}

	.dark .max-h-64::-webkit-scrollbar-thumb:hover {
		background: #60a5fa;
	}

	/* Step transition animations */
	@keyframes slideIn {
		from {
			opacity: 0;
			transform: translateX(20px);
		}
		to {
			opacity: 1;
			transform: translateX(0);
		}
	}

	.step-content {
		animation: slideIn 0.3s ease-out;
	}
</style>
