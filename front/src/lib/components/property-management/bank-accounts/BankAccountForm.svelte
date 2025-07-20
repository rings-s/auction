<!-- src/lib/components/property-management/bank-accounts/BankAccountForm.svelte -->
<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import { 
		createBankAccount, 
		updateBankAccount, 
		getBankAccount,
		validateBankAccountData,
		validateIBAN,
		formatIBAN,
		getBankAccountTypes
	} from '$lib/api/bankAccount';
	import { toast } from '$lib/stores/toastStore.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';
	import Tabs from '$lib/components/ui/Tabs.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';

	// Props using Svelte 5 runes
	const { accountId = null, onSuccess = null, embedded = false } = $props();

	// Svelte 5 runes for reactive state
	let loading = $state(false);
	let saving = $state(false);
	let error = $state(null);
	let currentStep = $state(1);
	let autoSaveEnabled = $state(true);
	let autoSaveTimer = $state(null);

	// Form data with Svelte 5 runes
	let formData = $state({
		bank_account_name: '',
		bank_name: '',
		iban_number: '',
		account_number: '',
		swift_code: '',
		account_type: 'checking',
		is_primary: false,
		notes: ''
	});

	// Validation errors
	let validationErrors = $state({});

	// Derived state
	let isEditing = $derived(!!accountId);
	let canProceed = $derived(Object.keys(validationErrors).length === 0);
	let formattedIBAN = $derived(formatIBAN(formData.iban_number));
	let accountTypes = $derived(getBankAccountTypes());

	// Tab configuration
	let tabs = $derived([
		{
			id: 1,
			label: $t('bankAccount.basicInfo'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>'
		},
		{
			id: 2,
			label: $t('bankAccount.bankDetails'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"></path></svg>'
		},
		{
			id: 3,
			label: $t('bankAccount.verification'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
		}
	]);

	// Load existing account data if editing
	onMount(async () => {
		if (isEditing) {
			await loadAccountData();
		}
		validateForm();
	});

	// Load account data for editing
	async function loadAccountData() {
		try {
			loading = true;
			error = null;
			const account = await getBankAccount(accountId);
			
			// Populate form data
			formData = {
				bank_account_name: account.bank_account_name || '',
				bank_name: account.bank_name || '',
				iban_number: account.iban_number || '',
				account_number: account.account_number || '',
				swift_code: account.swift_code || '',
				account_type: account.account_type || 'checking',
				is_primary: account.is_primary || false,
				notes: account.notes || ''
			};
		} catch (err) {
			error = err.message;
			toast.error($t('bankAccount.loadError'));
		} finally {
			loading = false;
		}
	}

	// Validate form
	function validateForm() {
		const validation = validateBankAccountData(formData);
		validationErrors = validation.errors;
		return validation.isValid;
	}

	// Handle form field changes
	function handleFieldChange(field, value) {
		formData[field] = value;
		
		// Special handling for IBAN formatting
		if (field === 'iban_number') {
			const ibanValidation = validateIBAN(value);
			if (ibanValidation.valid) {
				formData.iban_number = ibanValidation.cleanIban;
			}
		}
		
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
				saveAccount(true); // Silent save
			}
		}, 2000); // 2 second delay
	}

	// Save account
	async function saveAccount(silent = false) {
		if (!validateForm()) {
			if (!silent) {
				toast.error($t('bankAccount.validationError'));
			}
			return false;
		}

		try {
			saving = true;
			error = null;
			
			let result;
			if (isEditing) {
				result = await updateBankAccount(accountId, formData);
				if (!silent) {
					toast.success($t('bankAccount.updateSuccess'));
				}
			} else {
				result = await createBankAccount(formData);
				toast.success($t('bankAccount.createSuccess'));
			}
			
			// Call success callback if provided
			if (onSuccess) {
				onSuccess(result);
			}
			
			// Redirect if not embedded
			if (!embedded && !isEditing) {
				goto('/dashboard/bank-accounts');
			}
			
			return true;
		} catch (err) {
			error = err.message;
			if (!silent) {
				toast.error(isEditing ? $t('bankAccount.updateError') : $t('bankAccount.createError'));
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
			goto('/dashboard/bank-accounts');
		}
	}
</script>

<svelte:head>
	<title>
		{isEditing ? $t('bankAccount.edit') : $t('bankAccount.create')} - {$t('app.name')}
	</title>
</svelte:head>

<div class="max-w-4xl mx-auto space-y-6">
	<!-- Header -->
	{#if !embedded}
		<div class="border-b border-gray-200 pb-5 dark:border-gray-700">
			<h1 class="text-2xl font-bold text-gray-900 dark:text-white">
				{isEditing ? $t('bankAccount.edit') : $t('bankAccount.create')}
			</h1>
			<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
				{isEditing ? $t('bankAccount.editDescription') : $t('bankAccount.createDescription')}
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
				<!-- Step 1: Basic Information -->
				{#if currentStep === 1}
					<div class="space-y-6">
						<h3 class="text-lg font-medium text-gray-900 dark:text-white">
							{$t('bankAccount.basicInfo')}
						</h3>
						
						<div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
							<!-- Account Holder Name -->
							<div>
								<label for="bank_account_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('bankAccount.accountHolderName')} *
								</label>
								<input
									type="text"
									id="bank_account_name"
									value={formData.bank_account_name}
									oninput={(e) => handleFieldChange('bank_account_name', e.target.value)}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
									class:border-red-500={validationErrors.bank_account_name}
									placeholder={$t('bankAccount.accountHolderPlaceholder')}
								/>
								{#if validationErrors.bank_account_name}
									<p class="mt-1 text-sm text-red-600">{validationErrors.bank_account_name}</p>
								{/if}
							</div>

							<!-- Account Type -->
							<div>
								<label for="account_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('bankAccount.accountType')}
								</label>
								<select
									id="account_type"
									bind:value={formData.account_type}
									onchange={(e) => handleFieldChange('account_type', e.target.value)}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
								>
									{#each accountTypes as type}
										<option value={type.value}>{type.label}</option>
									{/each}
								</select>
							</div>
						</div>

						<!-- Primary Account -->
						<div class="flex items-start">
							<div class="flex h-5 items-center">
								<input
									id="is_primary"
									type="checkbox"
									bind:checked={formData.is_primary}
									onchange={(e) => handleFieldChange('is_primary', e.target.checked)}
									class="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700"
								/>
							</div>
							<div class="ml-3 text-sm">
								<label for="is_primary" class="font-medium text-gray-700 dark:text-gray-300">
									{$t('bankAccount.setPrimary')}
								</label>
								<p class="text-gray-500 dark:text-gray-400">
									{$t('bankAccount.primaryDescription')}
								</p>
							</div>
						</div>
					</div>
				
				<!-- Step 2: Bank Details -->
				{:else if currentStep === 2}
					<div class="space-y-6">
						<h3 class="text-lg font-medium text-gray-900 dark:text-white">
							{$t('bankAccount.bankDetails')}
						</h3>
						
						<div class="space-y-6">
							<!-- Bank Name -->
							<div>
								<label for="bank_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('bankAccount.bankName')} *
								</label>
								<input
									type="text"
									id="bank_name"
									value={formData.bank_name}
									oninput={(e) => handleFieldChange('bank_name', e.target.value)}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
									class:border-red-500={validationErrors.bank_name}
									placeholder={$t('bankAccount.bankNamePlaceholder')}
								/>
								{#if validationErrors.bank_name}
									<p class="mt-1 text-sm text-red-600">{validationErrors.bank_name}</p>
								{/if}
							</div>

							<!-- IBAN Number -->
							<div>
								<label for="iban_number" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('bankAccount.iban')} *
								</label>
								<input
									type="text"
									id="iban_number"
									value={formData.iban_number}
									oninput={(e) => handleFieldChange('iban_number', e.target.value)}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm font-mono"
									class:border-red-500={validationErrors.iban_number}
									placeholder="SA0000000000000000000000"
									maxlength="34"
								/>
								{#if formattedIBAN && !validationErrors.iban_number}
									<p class="mt-1 text-sm text-gray-500 font-mono">{formattedIBAN}</p>
								{/if}
								{#if validationErrors.iban_number}
									<p class="mt-1 text-sm text-red-600">{validationErrors.iban_number}</p>
								{/if}
								<p class="mt-1 text-xs text-gray-500">
									{$t('bankAccount.ibanHelp')}
								</p>
							</div>

							<!-- Account Number (Optional) -->
							<div>
								<label for="account_number" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('bankAccount.accountNumber')}
								</label>
								<input
									type="text"
									id="account_number"
									value={formData.account_number}
									oninput={(e) => handleFieldChange('account_number', e.target.value)}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
									class:border-red-500={validationErrors.account_number}
									placeholder={$t('bankAccount.accountNumberPlaceholder')}
								/>
								{#if validationErrors.account_number}
									<p class="mt-1 text-sm text-red-600">{validationErrors.account_number}</p>
								{/if}
							</div>

							<!-- SWIFT Code (Optional) -->
							<div>
								<label for="swift_code" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
									{$t('bankAccount.swiftCode')}
								</label>
								<input
									type="text"
									id="swift_code"
									value={formData.swift_code}
									oninput={(e) => handleFieldChange('swift_code', e.target.value)}
									class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm font-mono"
									class:border-red-500={validationErrors.swift_code}
									placeholder="RIBLSARI"
									maxlength="11"
								/>
								{#if validationErrors.swift_code}
									<p class="mt-1 text-sm text-red-600">{validationErrors.swift_code}</p>
								{/if}
								<p class="mt-1 text-xs text-gray-500">
									{$t('bankAccount.swiftHelp')}
								</p>
							</div>
						</div>
					</div>
				
				<!-- Step 3: Verification & Notes -->
				{:else if currentStep === 3}
					<div class="space-y-6">
						<h3 class="text-lg font-medium text-gray-900 dark:text-white">
							{$t('bankAccount.verification')}
						</h3>
						
						<!-- Account Summary -->
						<div class="rounded-lg bg-gray-50 p-4 dark:bg-gray-700">
							<h4 class="text-sm font-medium text-gray-900 dark:text-white mb-3">
								{$t('bankAccount.summary')}
							</h4>
							<dl class="space-y-2">
								<div class="flex justify-between">
									<dt class="text-sm text-gray-600 dark:text-gray-400">{$t('bankAccount.accountHolderName')}:</dt>
									<dd class="text-sm font-medium text-gray-900 dark:text-white">{formData.bank_account_name}</dd>
								</div>
								<div class="flex justify-between">
									<dt class="text-sm text-gray-600 dark:text-gray-400">{$t('bankAccount.bankName')}:</dt>
									<dd class="text-sm font-medium text-gray-900 dark:text-white">{formData.bank_name}</dd>
								</div>
								<div class="flex justify-between">
									<dt class="text-sm text-gray-600 dark:text-gray-400">{$t('bankAccount.iban')}:</dt>
									<dd class="text-sm font-mono text-gray-900 dark:text-white">{formattedIBAN}</dd>
								</div>
								{#if formData.account_number}
									<div class="flex justify-between">
										<dt class="text-sm text-gray-600 dark:text-gray-400">{$t('bankAccount.accountNumber')}:</dt>
										<dd class="text-sm font-mono text-gray-900 dark:text-white">{formData.account_number}</dd>
									</div>
								{/if}
								{#if formData.swift_code}
									<div class="flex justify-between">
										<dt class="text-sm text-gray-600 dark:text-gray-400">{$t('bankAccount.swiftCode')}:</dt>
										<dd class="text-sm font-mono text-gray-900 dark:text-white">{formData.swift_code}</dd>
									</div>
								{/if}
								<div class="flex justify-between">
									<dt class="text-sm text-gray-600 dark:text-gray-400">{$t('bankAccount.accountType')}:</dt>
									<dd class="text-sm text-gray-900 dark:text-white">
										{accountTypes.find(t => t.value === formData.account_type)?.label}
									</dd>
								</div>
								{#if formData.is_primary}
									<div class="flex justify-between">
										<dt class="text-sm text-gray-600 dark:text-gray-400">{$t('bankAccount.primary')}:</dt>
										<dd class="text-sm font-medium text-primary-600 dark:text-primary-400">
											{$t('common.yes')}
										</dd>
									</div>
								{/if}
							</dl>
						</div>

						<!-- Notes -->
						<div>
							<label for="notes" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
								{$t('bankAccount.notes')}
							</label>
							<textarea
								id="notes"
								rows="3"
								value={formData.notes}
								oninput={(e) => handleFieldChange('notes', e.target.value)}
								class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
								placeholder={$t('bankAccount.notesPlaceholder')}
							></textarea>
						</div>

						<!-- Verification Notice -->
						<div class="rounded-md bg-blue-50 p-4 dark:bg-blue-900/20">
							<div class="flex">
								<div class="flex-shrink-0">
									<svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
										<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
									</svg>
								</div>
								<div class="ml-3">
									<h3 class="text-sm font-medium text-blue-800 dark:text-blue-200">
										{$t('bankAccount.verificationNotice')}
									</h3>
									<div class="mt-2 text-sm text-blue-700 dark:text-blue-300">
										<p>{$t('bankAccount.verificationDescription')}</p>
									</div>
								</div>
							</div>
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
								onClick={() => saveAccount()} 
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