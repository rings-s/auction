<!-- src/routes/create/bank-account/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t, locale } from '$lib/i18n';
	import { toast } from '$lib/stores/toastStore.svelte.js';
	import { createBankAccount, validateIBAN, formatIBAN, getBankAccountTypes } from '$lib/api/bankAccount';
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
		{ label: $t('bankAccount.accounts'), href: '/dashboard/bank-accounts' },
		{ label: $t('bankAccount.add'), href: '/create/bank-account', active: true }
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
		bank_account_name: '',
		bank_name: '',
		iban_number: '',
		account_number: '',
		swift_code: '',
		account_type: 'checking',
		is_primary: false,
		notes: ''
	};

	// Tab configuration
	$: tabs = [
		{
			id: 'basic',
			label: $t('bankAccount.basicInfo'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>',
			fields: ['bank_account_name', 'account_type']
		},
		{
			id: 'details',
			label: $t('bankAccount.bankDetails'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"></path></svg>',
			fields: ['bank_name', 'iban_number', 'account_number', 'swift_code']
		},
		{
			id: 'verification',
			label: $t('bankAccount.verification'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
			fields: ['is_primary', 'notes']
		}
	];

	// Account types
	$: accountTypes = [
		{ value: 'checking', label: $t('bankAccount.checking') },
		{ value: 'savings', label: $t('bankAccount.savings') },
		{ value: 'business', label: $t('bankAccount.business') },
		{ value: 'investment', label: $t('bankAccount.investment') }
	];

	// Validation
	function validateCurrentTab() {
		const currentTabData = tabs[currentTab];
		const tabErrors = {};
		
		if (currentTabData.id === 'basic') {
			if (!formData.bank_account_name.trim()) {
				tabErrors.bank_account_name = $t('validation.required');
			}
			if (!formData.account_type) {
				tabErrors.account_type = $t('validation.required');
			}
		} else if (currentTabData.id === 'details') {
			if (!formData.bank_name.trim()) {
				tabErrors.bank_name = $t('validation.required');
			}
			if (!formData.iban_number.trim()) {
				tabErrors.iban_number = $t('validation.required');
			} else if (!validateIBAN(formData.iban_number)) {
				tabErrors.iban_number = $t('bankAccount.invalidIBAN');
			}
			if (!formData.account_number.trim()) {
				tabErrors.account_number = $t('validation.required');
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

	function handleTabChange(event) {
		if (validateCurrentTab()) {
			if (!completedTabs.includes(currentTab)) {
				completedTabs = [...completedTabs, currentTab];
			}
		}
		currentTab = event.detail.tab;
	}

	function handleNext() {
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
		if (!validateCurrentTab()) {
			return;
		}

		try {
			submitting = true;
			error = null;

			// Prepare data for submission
			const submitData = {
				...formData,
				iban_number: formData.iban_number.replace(/\s/g, '') // Remove spaces
			};

			const result = await createBankAccount(submitData);
			success = $t('bankAccount.createSuccess');
			
			setTimeout(() => {
				goto('/dashboard/bank-accounts');
			}, 1500);
		} catch (err) {
			error = err.message || $t('bankAccount.createError');
		} finally {
			submitting = false;
		}
	}

	function handleCancel() {
		goto('/dashboard/bank-accounts');
	}

	// Format IBAN on input
	function handleIBANInput(event) {
		formData.iban_number = formatIBAN(event.target.value);
		validateCurrentTab();
	}

	$: canProceed = validateCurrentTab();
	$: isFirstStep = currentTab === 0;
	$: isLastStep = currentTab === tabs.length - 1;

	onMount(() => {
		validateCurrentTab();
	});
</script>

<svelte:head>
	<title>{$t('bankAccount.add')} - {$t('app.name')}</title>
	<meta name="description" content={$t('bankAccount.addDescription')} />
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<div class="mx-auto max-w-4xl px-4 py-6 sm:px-6 lg:px-8">
		<div class="space-y-6">
			<!-- Breadcrumb -->
			<Breadcrumb items={breadcrumbItems} />

			<!-- Page Header -->
			<div class="text-center">
				<h1 class="text-3xl font-bold text-gray-900 dark:text-white">
					{$t('bankAccount.add')}
				</h1>
				<p class="mt-2 text-lg text-gray-600 dark:text-gray-400">
					{$t('bankAccount.addDescription')}
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
					<!-- Basic Information Tab -->
					{#if currentTab === 0}
						<FormStep
							step={{
								id: 'basic',
								title: $t('bankAccount.basicInfo'),
								description: $t('bankAccount.basicInfoDescription')
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
									<label for="bank_account_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										{$t('bankAccount.accountName')} *
									</label>
									<input
										type="text"
										id="bank_account_name"
										bind:value={formData.bank_account_name}
										class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
										placeholder={$t('bankAccount.accountNamePlaceholder')}
										class:border-red-500={validationErrors.bank_account_name}
										on:input={validateCurrentTab}
									/>
									{#if validationErrors.bank_account_name}
										<p class="mt-1 text-sm text-red-600">{validationErrors.bank_account_name}</p>
									{/if}
								</div>

								<div>
									<label for="account_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										{$t('bankAccount.accountType')} *
									</label>
									<select
										id="account_type"
										bind:value={formData.account_type}
										class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
										class:border-red-500={validationErrors.account_type}
										on:change={validateCurrentTab}
									>
										{#each accountTypes as type}
											<option value={type.value}>{type.label}</option>
										{/each}
									</select>
									{#if validationErrors.account_type}
										<p class="mt-1 text-sm text-red-600">{validationErrors.account_type}</p>
									{/if}
								</div>
							</div>
						</FormStep>
					{/if}

					<!-- Bank Details Tab -->
					{#if currentTab === 1}
						<FormStep
							step={{
								id: 'details',
								title: $t('bankAccount.bankDetails'),
								description: $t('bankAccount.bankDetailsDescription')
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
									<label for="bank_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										{$t('bankAccount.bankName')} *
									</label>
									<input
										type="text"
										id="bank_name"
										bind:value={formData.bank_name}
										class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
										placeholder={$t('bankAccount.bankNamePlaceholder')}
										class:border-red-500={validationErrors.bank_name}
										on:input={validateCurrentTab}
									/>
									{#if validationErrors.bank_name}
										<p class="mt-1 text-sm text-red-600">{validationErrors.bank_name}</p>
									{/if}
								</div>

								<div>
									<label for="iban_number" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										{$t('bankAccount.ibanNumber')} *
									</label>
									<input
										type="text"
										id="iban_number"
										value={formData.iban_number}
										class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
										placeholder="SA00 0000 0000 0000 0000 0000"
										class:border-red-500={validationErrors.iban_number}
										on:input={handleIBANInput}
									/>
									{#if validationErrors.iban_number}
										<p class="mt-1 text-sm text-red-600">{validationErrors.iban_number}</p>
									{/if}
									<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
										{$t('bankAccount.ibanFormat')}
									</p>
								</div>

								<div>
									<label for="account_number" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										{$t('bankAccount.accountNumber')} *
									</label>
									<input
										type="text"
										id="account_number"
										bind:value={formData.account_number}
										class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
										placeholder={$t('bankAccount.accountNumberPlaceholder')}
										class:border-red-500={validationErrors.account_number}
										on:input={validateCurrentTab}
									/>
									{#if validationErrors.account_number}
										<p class="mt-1 text-sm text-red-600">{validationErrors.account_number}</p>
									{/if}
								</div>

								<div>
									<label for="swift_code" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										{$t('bankAccount.swiftCode')}
									</label>
									<input
										type="text"
										id="swift_code"
										bind:value={formData.swift_code}
										class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
										placeholder="SWIFT0000"
										on:input={validateCurrentTab}
									/>
									<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
										{$t('bankAccount.swiftCodeOptional')}
									</p>
								</div>
							</div>
						</FormStep>
					{/if}

					<!-- Verification Tab -->
					{#if currentTab === 2}
						<FormStep
							step={{
								id: 'verification',
								title: $t('bankAccount.verification'),
								description: $t('bankAccount.verificationDescription'),
								submitText: $t('bankAccount.createAccount'),
								submitLoadingText: $t('bankAccount.creating')
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
								<div class="flex items-center">
									<input
										type="checkbox"
										id="is_primary"
										bind:checked={formData.is_primary}
										class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
									/>
									<label for="is_primary" class="ml-2 block text-sm text-gray-900 dark:text-gray-100">
										{$t('bankAccount.setPrimary')}
									</label>
								</div>
								<p class="text-xs text-gray-500 dark:text-gray-400">
									{$t('bankAccount.primaryAccountDescription')}
								</p>

								<div>
									<label for="notes" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										{$t('bankAccount.notes')}
									</label>
									<textarea
										id="notes"
										bind:value={formData.notes}
										rows="4"
										class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
										placeholder={$t('bankAccount.notesPlaceholder')}
									></textarea>
								</div>

								<!-- Summary -->
								<div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
									<h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">
										{$t('form.summary')}
									</h4>
									<dl class="space-y-2 text-sm">
										<div class="flex justify-between">
											<dt class="text-gray-600 dark:text-gray-400">{$t('bankAccount.accountName')}:</dt>
											<dd class="font-medium text-gray-900 dark:text-gray-100">{formData.bank_account_name}</dd>
										</div>
										<div class="flex justify-between">
											<dt class="text-gray-600 dark:text-gray-400">{$t('bankAccount.bankName')}:</dt>
											<dd class="font-medium text-gray-900 dark:text-gray-100">{formData.bank_name}</dd>
										</div>
										<div class="flex justify-between">
											<dt class="text-gray-600 dark:text-gray-400">{$t('bankAccount.accountType')}:</dt>
											<dd class="font-medium text-gray-900 dark:text-gray-100">
												{accountTypes.find(t => t.value === formData.account_type)?.label}
											</dd>
										</div>
										<div class="flex justify-between">
											<dt class="text-gray-600 dark:text-gray-400">{$t('bankAccount.ibanNumber')}:</dt>
											<dd class="font-medium text-gray-900 dark:text-gray-100 font-mono">{formData.iban_number}</dd>
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
