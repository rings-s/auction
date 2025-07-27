<!-- src/lib/components/property-management/payments/PaymentForm.svelte -->
<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import {
		createPayment,
		updatePayment,
		getPayment,
		validatePaymentData,
		getPaymentTypes,
		getPaymentStatuses,
		formatCurrency
	} from '$lib/api/payment';
	import { getProperties } from '$lib/api/property';
	import { toast } from '$lib/stores/toastStore.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';
	import Tabs from '$lib/components/ui/Tabs.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';

	// Props using Svelte 5 runes
	const { paymentId = null, onSuccess = null, embedded = false } = $props();

	// Svelte 5 runes for reactive state
	let loading = $state(false);
	let saving = $state(false);
	let error = $state(null);
	let currentStep = $state(1);
	let properties = $state([]);
	let autoSaveEnabled = $state(true);
	let autoSaveTimer = $state(null);

	// Form data with Svelte 5 runes
	let formData = $state({
		payment_id: '',
		amount: '',
		payment_type: 'rent',
		description: '',
		due_date: '',
		payment_date: '',
		status: 'pending',
		property_reference: '',
		tenant_reference: '',
		notes: ''
	});

	// Validation errors
	let validationErrors = $state({});

	// Derived state
	let isEditing = $derived(!!paymentId);
	let canProceed = $derived(Object.keys(validationErrors).length === 0);
	let paymentTypes = $derived(getPaymentTypes());
	let paymentStatuses = $derived(getPaymentStatuses());
	let selectedProperty = $derived(
		properties.find((p) => p.id === parseInt(formData.property_reference))
	);

	// Tab configuration
	let tabs = $derived([
		{
			id: 1,
			label: $t('payment.basicInfo'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>'
		},
		{
			id: 2,
			label: $t('payment.references'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>'
		},
		{
			id: 3,
			label: $t('payment.schedule'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>'
		}
	]);

	// Load data on mount
	onMount(async () => {
		await loadInitialData();

		if (isEditing) {
			await loadPaymentData();
		} else {
			// Generate payment ID for new payments
			formData.payment_id = generatePaymentId();
		}

		validateForm();
	});

	// Load initial data (properties, etc.)
	async function loadInitialData() {
		try {
			loading = true;
			properties = await getProperties();
		} catch (err) {
			toast.error($t('payment.loadDataError'));
		} finally {
			loading = false;
		}
	}

	// Load payment data for editing
	async function loadPaymentData() {
		try {
			loading = true;
			error = null;
			const payment = await getPayment(paymentId);

			// Populate form data
			formData = {
				payment_id: payment.payment_id || '',
				amount: payment.amount || '',
				payment_type: payment.payment_type || 'rent',
				description: payment.description || '',
				due_date: payment.due_date || '',
				payment_date: payment.payment_date || '',
				status: payment.status || 'pending',
				property_reference: payment.property_reference?.id || '',
				tenant_reference: payment.tenant_reference?.id || '',
				notes: payment.notes || ''
			};
		} catch (err) {
			error = err.message;
			toast.error($t('payment.loadError'));
		} finally {
			loading = false;
		}
	}

	// Generate unique payment ID
	function generatePaymentId() {
		const prefix = 'PAY';
		const timestamp = Date.now().toString().slice(-6);
		const random = Math.random().toString(36).substr(2, 4).toUpperCase();
		return `${prefix}-${timestamp}-${random}`;
	}

	// Validate form
	function validateForm() {
		const validation = validatePaymentData(formData);
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

	// Schedule auto-save
	function scheduleAutoSave() {
		if (autoSaveTimer) {
			clearTimeout(autoSaveTimer);
		}

		autoSaveTimer = setTimeout(() => {
			if (validateForm()) {
				savePayment(true); // Silent save
			}
		}, 2000); // 2 second delay
	}

	// Save payment
	async function savePayment(silent = false) {
		if (!validateForm()) {
			if (!silent) {
				toast.error($t('payment.validationError'));
			}
			return false;
		}

		try {
			saving = true;
			error = null;

			// Prepare data for API
			const paymentData = {
				...formData,
				amount: parseFloat(formData.amount),
				property_reference: formData.property_reference
					? parseInt(formData.property_reference)
					: null,
				tenant_reference: formData.tenant_reference ? parseInt(formData.tenant_reference) : null
			};

			let result;
			if (isEditing) {
				result = await updatePayment(paymentId, paymentData);
				if (!silent) {
					toast.success($t('payment.updateSuccess'));
				}
			} else {
				result = await createPayment(paymentData);
				toast.success($t('payment.createSuccess'));
			}

			// Call success callback if provided
			if (onSuccess) {
				onSuccess(result);
			}

			// Redirect if not embedded
			if (!embedded && !isEditing) {
				goto('/dashboard/payments');
			}

			return true;
		} catch (err) {
			error = err.message;
			if (!silent) {
				toast.error(isEditing ? $t('payment.updateError') : $t('payment.createError'));
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
			// Emit cancel event for parent component
			if (typeof onCancel === 'function') {
				onCancel();
			}
		} else {
			goto('/dashboard/payments');
		}
	}

	// Get today's date in YYYY-MM-DD format
	function getTodayDate() {
		return new Date().toISOString().split('T')[0];
	}

	// Calculate amount if property is selected and type is rent
	function calculateRentAmount() {
		if (selectedProperty && formData.payment_type === 'rent' && selectedProperty.monthly_rent) {
			formData.amount = selectedProperty.monthly_rent.toString();
			handleFieldChange('amount', formData.amount);
		}
	}

	// Watch for property and type changes to auto-calculate amount
	$effect(() => {
		if (formData.property_reference && formData.payment_type === 'rent') {
			calculateRentAmount();
		}
	});
</script>

<svelte:head>
	<title>
		{isEditing ? $t('payment.edit') : $t('payment.create')} - {$t('app.name')}
	</title>
</svelte:head>

<div class="mx-auto max-w-4xl space-y-6">
	<!-- Header -->
	{#if !embedded}
		<div class="border-b border-gray-200 pb-5 dark:border-gray-700">
			<h1 class="text-2xl font-bold text-gray-900 dark:text-white">
				{isEditing ? $t('payment.edit') : $t('payment.create')}
			</h1>
			<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
				{isEditing ? $t('payment.editDescription') : $t('payment.createDescription')}
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
		<div class="overflow-hidden rounded-lg bg-white shadow-sm dark:bg-gray-800">
			<!-- Progress Steps -->
			<div class="border-b border-gray-200 px-6 py-4 dark:border-gray-700">
				<Tabs bind:activeTab={currentStep} {tabs} variant="pills" on:change={handleTabChange} />
			</div>

			<!-- Auto-save indicator -->
			{#if autoSaveEnabled && isEditing}
				<div
					class="border-b border-blue-200 bg-blue-50 px-6 py-2 dark:border-blue-800 dark:bg-blue-900/20"
				>
					<div class="flex items-center text-sm text-blue-700 dark:text-blue-300">
						<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M13 10V3L4 14h7v7l9-11h-7z"
							/>
						</svg>
						{$t('common.autoSaveEnabled')}
					</div>
				</div>
			{/if}

			<!-- Form Content -->
			<div class="p-6">
				<!-- Step 1: Basic Information -->
				{#if currentStep === 1}
					<div class="space-y-6">
						<h3 class="text-lg font-medium text-gray-900 dark:text-white">
							{$t('payment.basicInfo')}
						</h3>

						<div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
							<!-- Payment ID -->
							<div>
								<label
									for="payment_id"
									class="block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('payment.id')} *
								</label>
								<input
									type="text"
									id="payment_id"
									value={formData.payment_id}
									oninput={(e) => handleFieldChange('payment_id', e.target.value)}
									class="focus:border-primary-500 focus:ring-primary-500 mt-1 block w-full rounded-md border-gray-300 font-mono shadow-sm sm:text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
									class:border-red-500={validationErrors.payment_id}
									placeholder="PAY-123456-ABCD"
								/>
								{#if validationErrors.payment_id}
									<p class="mt-1 text-sm text-red-600">{validationErrors.payment_id}</p>
								{/if}
							</div>

							<!-- Amount -->
							<div>
								<label
									for="amount"
									class="block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('common.amount')} *
								</label>
								<div class="relative mt-1 rounded-md shadow-sm">
									<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
										<span class="text-gray-500 sm:text-sm">$</span>
									</div>
									<input
										type="number"
										id="amount"
										step="0.01"
										min="0"
										value={formData.amount}
										oninput={(e) => handleFieldChange('amount', e.target.value)}
										class="focus:border-primary-500 focus:ring-primary-500 block w-full rounded-md border-gray-300 pl-7 shadow-sm sm:text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
										class:border-red-500={validationErrors.amount}
										placeholder="0.00"
									/>
								</div>
								{#if validationErrors.amount}
									<p class="mt-1 text-sm text-red-600">{validationErrors.amount}</p>
								{/if}
							</div>

							<!-- Payment Type -->
							<div>
								<label
									for="payment_type"
									class="block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('payment.type')} *
								</label>
								<select
									id="payment_type"
									bind:value={formData.payment_type}
									onchange={(e) => handleFieldChange('payment_type', e.target.value)}
									class="focus:border-primary-500 focus:ring-primary-500 mt-1 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
								>
									{#each paymentTypes as type}
										<option value={type.value}>{type.label}</option>
									{/each}
								</select>
							</div>

							<!-- Status -->
							<div>
								<label
									for="status"
									class="block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('common.status')}
								</label>
								<select
									id="status"
									bind:value={formData.status}
									onchange={(e) => handleFieldChange('status', e.target.value)}
									class="focus:border-primary-500 focus:ring-primary-500 mt-1 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
								>
									{#each paymentStatuses as status}
										<option value={status.value}>{status.label}</option>
									{/each}
								</select>
							</div>
						</div>

						<!-- Description -->
						<div>
							<label
								for="description"
								class="block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('common.description')}
							</label>
							<textarea
								id="description"
								rows="3"
								value={formData.description}
								oninput={(e) => handleFieldChange('description', e.target.value)}
								class="focus:border-primary-500 focus:ring-primary-500 mt-1 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
								placeholder={$t('payment.descriptionPlaceholder')}
							></textarea>
						</div>
					</div>

					<!-- Step 2: References -->
				{:else if currentStep === 2}
					<div class="space-y-6">
						<h3 class="text-lg font-medium text-gray-900 dark:text-white">
							{$t('payment.references')}
						</h3>

						<!-- Property Reference -->
						<div>
							<label
								for="property_reference"
								class="block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('payment.propertyReference')}
							</label>
							<select
								id="property_reference"
								bind:value={formData.property_reference}
								onchange={(e) => handleFieldChange('property_reference', e.target.value)}
								class="focus:border-primary-500 focus:ring-primary-500 mt-1 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
							>
								<option value="">{$t('common.selectProperty')}</option>
								{#each properties as property}
									<option value={property.id}>
										{property.title} - {property.address}
									</option>
								{/each}
							</select>
							<p class="mt-1 text-xs text-gray-500">
								{$t('payment.propertyReferenceHelp')}
							</p>
						</div>

						<!-- Selected Property Info -->
						{#if selectedProperty}
							<div class="rounded-lg bg-blue-50 p-4 dark:bg-blue-900/20">
								<h4 class="mb-2 text-sm font-medium text-blue-800 dark:text-blue-200">
									{$t('payment.selectedProperty')}
								</h4>
								<div class="text-sm text-blue-700 dark:text-blue-300">
									<p><strong>{$t('property.title')}:</strong> {selectedProperty.title}</p>
									<p><strong>{$t('property.address')}:</strong> {selectedProperty.address}</p>
									{#if selectedProperty.monthly_rent}
										<p>
											<strong>{$t('property.monthlyRent')}:</strong>
											{formatCurrency(selectedProperty.monthly_rent)}
										</p>
									{/if}
								</div>

								{#if selectedProperty.monthly_rent && formData.payment_type === 'rent'}
									<Button
										onClick={calculateRentAmount}
										variant="outline"
										size="compact"
										class="mt-3"
									>
										{$t('payment.useMonthlyRent')}
									</Button>
								{/if}
							</div>
						{/if}

						<!-- Tenant Reference -->
						<div>
							<label
								for="tenant_reference"
								class="block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('payment.tenantReference')}
							</label>
							<input
								type="text"
								id="tenant_reference"
								value={formData.tenant_reference}
								oninput={(e) => handleFieldChange('tenant_reference', e.target.value)}
								class="focus:border-primary-500 focus:ring-primary-500 mt-1 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
								placeholder={$t('payment.tenantPlaceholder')}
							/>
							<p class="mt-1 text-xs text-gray-500">
								{$t('payment.tenantReferenceHelp')}
							</p>
						</div>
					</div>

					<!-- Step 3: Schedule -->
				{:else if currentStep === 3}
					<div class="space-y-6">
						<h3 class="text-lg font-medium text-gray-900 dark:text-white">
							{$t('payment.schedule')}
						</h3>

						<div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
							<!-- Due Date -->
							<div>
								<label
									for="due_date"
									class="block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('payment.dueDate')}
								</label>
								<input
									type="date"
									id="due_date"
									value={formData.due_date}
									oninput={(e) => handleFieldChange('due_date', e.target.value)}
									min={getTodayDate()}
									class="focus:border-primary-500 focus:ring-primary-500 mt-1 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
									class:border-red-500={validationErrors.due_date}
								/>
								{#if validationErrors.due_date}
									<p class="mt-1 text-sm text-red-600">{validationErrors.due_date}</p>
								{/if}
							</div>

							<!-- Payment Date -->
							<div>
								<label
									for="payment_date"
									class="block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('payment.paymentDate')}
								</label>
								<input
									type="date"
									id="payment_date"
									value={formData.payment_date}
									oninput={(e) => handleFieldChange('payment_date', e.target.value)}
									max={getTodayDate()}
									class="focus:border-primary-500 focus:ring-primary-500 mt-1 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
									class:border-red-500={validationErrors.payment_date}
								/>
								{#if validationErrors.payment_date}
									<p class="mt-1 text-sm text-red-600">{validationErrors.payment_date}</p>
								{/if}
								<p class="mt-1 text-xs text-gray-500">
									{$t('payment.paymentDateHelp')}
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
								class="focus:border-primary-500 focus:ring-primary-500 mt-1 block w-full rounded-md border-gray-300 shadow-sm sm:text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
								placeholder={$t('payment.notesPlaceholder')}
							></textarea>
						</div>

						<!-- Payment Summary -->
						<div class="rounded-lg bg-gray-50 p-4 dark:bg-gray-700">
							<h4 class="mb-3 text-sm font-medium text-gray-900 dark:text-white">
								{$t('payment.summary')}
							</h4>
							<dl class="space-y-2">
								<div class="flex justify-between">
									<dt class="text-sm text-gray-600 dark:text-gray-400">{$t('payment.id')}:</dt>
									<dd class="font-mono text-sm text-gray-900 dark:text-white">
										{formData.payment_id}
									</dd>
								</div>
								<div class="flex justify-between">
									<dt class="text-sm text-gray-600 dark:text-gray-400">{$t('common.amount')}:</dt>
									<dd class="text-sm font-medium text-gray-900 dark:text-white">
										{formData.amount ? formatCurrency(parseFloat(formData.amount)) : '$0.00'}
									</dd>
								</div>
								<div class="flex justify-between">
									<dt class="text-sm text-gray-600 dark:text-gray-400">{$t('payment.type')}:</dt>
									<dd class="text-sm text-gray-900 dark:text-white">
										{paymentTypes.find((t) => t.value === formData.payment_type)?.label}
									</dd>
								</div>
								<div class="flex justify-between">
									<dt class="text-sm text-gray-600 dark:text-gray-400">{$t('common.status')}:</dt>
									<dd class="text-sm text-gray-900 dark:text-white">
										{paymentStatuses.find((s) => s.value === formData.status)?.label}
									</dd>
								</div>
								{#if formData.due_date}
									<div class="flex justify-between">
										<dt class="text-sm text-gray-600 dark:text-gray-400">
											{$t('payment.dueDate')}:
										</dt>
										<dd class="text-sm text-gray-900 dark:text-white">
											{new Date(formData.due_date).toLocaleDateString()}
										</dd>
									</div>
								{/if}
								{#if selectedProperty}
									<div class="flex justify-between">
										<dt class="text-sm text-gray-600 dark:text-gray-400">
											{$t('payment.property')}:
										</dt>
										<dd class="text-sm text-gray-900 dark:text-white">{selectedProperty.title}</dd>
									</div>
								{/if}
							</dl>
						</div>
					</div>
				{/if}
			</div>

			<!-- Form Actions -->
			<div
				class="border-t border-gray-200 bg-gray-50 px-6 py-3 text-right dark:border-gray-600 dark:bg-gray-700"
			>
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
								onClick={() => savePayment()}
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
