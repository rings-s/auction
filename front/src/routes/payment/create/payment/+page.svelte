<!-- src/routes/create/payment/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t, locale } from '$lib/i18n';
	import { toast } from '$lib/stores/toastStore.svelte.js';
	import { createPayment } from '$lib/api/payment';
	import { getProperties } from '$lib/api/property';
	import { getBankAccounts } from '$lib/api/bankAccount';
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
		{ label: $t('payment.payments'), href: '/dashboard/payments' },
		{ label: $t('payment.add'), href: '/create/payment', active: true }
	];

	// Form state
	let currentTab = 0;
	let loading = false;
	let submitting = false;
	let error = null;
	let success = null;
	let validationErrors = {};
	let completedTabs = [];

	// Data for dropdowns
	let properties = [];
	let bankAccounts = [];

	// Form data
	let formData = {
		amount: '',
		payment_type: 'income',
		payment_method: 'bank_transfer',
		status: 'pending',
		description: '',
		recipient_name: '',
		recipient_email: '',
		recipient_phone: '',
		related_property: null,
		bank_account: null,
		due_date: '',
		payment_date: '',
		reference_number: '',
		notes: ''
	};

	// Tab configuration
	$: tabs = [
		{
			id: 'details',
			label: $t('payment.paymentDetails'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
			fields: ['amount', 'payment_type', 'payment_method', 'description']
		},
		{
			id: 'recipient',
			label: $t('payment.recipientInfo'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>',
			fields: ['recipient_name', 'recipient_email', 'recipient_phone']
		},
		{
			id: 'associations',
			label: $t('payment.associations'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>',
			fields: ['related_property', 'bank_account']
		},
		{
			id: 'schedule',
			label: $t('payment.scheduling'),
			icon: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>',
			fields: ['due_date', 'payment_date', 'status', 'reference_number', 'notes']
		}
	];

	// Payment types
	$: paymentTypes = [
		{ value: 'income', label: $t('payment.income') },
		{ value: 'expense', label: $t('payment.expense') },
		{ value: 'rent', label: $t('payment.rent') },
		{ value: 'maintenance', label: $t('payment.maintenance') },
		{ value: 'utility', label: $t('payment.utility') },
		{ value: 'other', label: $t('payment.other') }
	];

	// Payment methods
	$: paymentMethods = [
		{ value: 'bank_transfer', label: $t('payment.bankTransfer') },
		{ value: 'cash', label: $t('payment.cash') },
		{ value: 'check', label: $t('payment.check') },
		{ value: 'online', label: $t('payment.online') },
		{ value: 'credit_card', label: $t('payment.creditCard') }
	];

	// Payment statuses
	$: paymentStatuses = [
		{ value: 'pending', label: $t('payment.pending') },
		{ value: 'completed', label: $t('payment.completed') },
		{ value: 'failed', label: $t('payment.failed') },
		{ value: 'cancelled', label: $t('payment.cancelled') }
	];

	// Load data on mount
	onMount(async () => {
		try {
			loading = true;
			[properties, bankAccounts] = await Promise.all([
				getProperties(),
				getBankAccounts()
			]);
		} catch (err) {
			error = $t('payment.loadDataError');
		} finally {
			loading = false;
		}
	});

	// Validation
	function validateCurrentTab() {
		const currentTabData = tabs[currentTab];
		const tabErrors = {};
		
		if (currentTabData.id === 'details') {
			if (!formData.amount || parseFloat(formData.amount) <= 0) {
				tabErrors.amount = $t('validation.positiveNumber');
			}
			if (!formData.payment_type) {
				tabErrors.payment_type = $t('validation.required');
			}
			if (!formData.payment_method) {
				tabErrors.payment_method = $t('validation.required');
			}
			if (!formData.description.trim()) {
				tabErrors.description = $t('validation.required');
			}
		} else if (currentTabData.id === 'recipient') {
			if (!formData.recipient_name.trim()) {
				tabErrors.recipient_name = $t('validation.required');
			}
			if (formData.recipient_email && !isValidEmail(formData.recipient_email)) {
				tabErrors.recipient_email = $t('validation.invalidEmail');
			}
		} else if (currentTabData.id === 'schedule') {
			if (formData.due_date && formData.payment_date && 
				new Date(formData.payment_date) < new Date(formData.due_date)) {
				tabErrors.payment_date = $t('payment.paymentDateAfterDue');
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
				amount: parseFloat(formData.amount),
				related_property: formData.related_property || null,
				bank_account: formData.bank_account || null
			};

			const result = await createPayment(submitData);
			success = $t('payment.createSuccess');
			
			setTimeout(() => {
				goto('/dashboard/payments');
			}, 1500);
		} catch (err) {
			error = err.message || $t('payment.createError');
		} finally {
			submitting = false;
		}
	}

	function handleCancel() {
		goto('/dashboard/payments');
	}

	// Format today's date for default values
	function getTodayDate() {
		return new Date().toISOString().split('T')[0];
	}

	$: canProceed = validateCurrentTab();
	$: isFirstStep = currentTab === 0;
	$: isLastStep = currentTab === tabs.length - 1;
</script>

<svelte:head>
	<title>{$t('payment.add')} - {$t('app.name')}</title>
	<meta name="description" content={$t('payment.addDescription')} />
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<div class="mx-auto max-w-4xl px-4 py-6 sm:px-6 lg:px-8">
		<div class="space-y-6">
			<!-- Breadcrumb -->
			<Breadcrumb items={breadcrumbItems} />

			<!-- Page Header -->
			<div class="text-center">
				<h1 class="text-3xl font-bold text-gray-900 dark:text-white">
					{$t('payment.add')}
				</h1>
				<p class="mt-2 text-lg text-gray-600 dark:text-gray-400">
					{$t('payment.addDescription')}
				</p>
			</div>

			<!-- Messages -->
			{#if error}
				<Alert type="error" message={error} dismissible on:dismiss={() => error = null} />
			{/if}

			{#if success}
				<Alert type="success" message={success} />
			{/if}

			{#if loading}
				<div class="bg-white dark:bg-gray-800 shadow-lg rounded-lg p-6">
					<div class="animate-pulse space-y-4">
						<div class="h-4 bg-gray-200 rounded w-3/4"></div>
						<div class="h-4 bg-gray-200 rounded w-1/2"></div>
						<div class="h-4 bg-gray-200 rounded w-5/6"></div>
					</div>
				</div>
			{:else}
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
						<!-- Payment Details Tab -->
						{#if currentTab === 0}
							<FormStep
								step={{
									id: 'details',
									title: $t('payment.paymentDetails'),
									description: $t('payment.paymentDetailsDescription')
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
											<label for="amount" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
												{$t('payment.amount')} *
											</label>
											<div class="relative">
												<input
													type="number"
													id="amount"
													bind:value={formData.amount}
													step="0.01"
													min="0"
													class="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
													placeholder="0.00"
													class:border-red-500={validationErrors.amount}
													on:input={validateCurrentTab}
												/>
												<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
													<span class="text-gray-500 dark:text-gray-400">$</span>
												</div>
											</div>
											{#if validationErrors.amount}
												<p class="mt-1 text-sm text-red-600">{validationErrors.amount}</p>
											{/if}
										</div>

										<div>
											<label for="payment_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
												{$t('payment.paymentType')} *
											</label>
											<select
												id="payment_type"
												bind:value={formData.payment_type}
												class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
												class:border-red-500={validationErrors.payment_type}
												on:change={validateCurrentTab}
											>
												{#each paymentTypes as type}
													<option value={type.value}>{type.label}</option>
												{/each}
											</select>
											{#if validationErrors.payment_type}
												<p class="mt-1 text-sm text-red-600">{validationErrors.payment_type}</p>
											{/if}
										</div>
									</div>

									<div>
										<label for="payment_method" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('payment.paymentMethod')} *
										</label>
										<select
											id="payment_method"
											bind:value={formData.payment_method}
											class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
											class:border-red-500={validationErrors.payment_method}
											on:change={validateCurrentTab}
										>
											{#each paymentMethods as method}
												<option value={method.value}>{method.label}</option>
											{/each}
										</select>
										{#if validationErrors.payment_method}
											<p class="mt-1 text-sm text-red-600">{validationErrors.payment_method}</p>
										{/if}
									</div>

									<div>
										<label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('payment.description')} *
										</label>
										<textarea
											id="description"
											bind:value={formData.description}
											rows="3"
											class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
											placeholder={$t('payment.descriptionPlaceholder')}
											class:border-red-500={validationErrors.description}
											on:input={validateCurrentTab}
										></textarea>
										{#if validationErrors.description}
											<p class="mt-1 text-sm text-red-600">{validationErrors.description}</p>
										{/if}
									</div>
								</div>
							</FormStep>
						{/if}

						<!-- Recipient Information Tab -->
						{#if currentTab === 1}
							<FormStep
								step={{
									id: 'recipient',
									title: $t('payment.recipientInfo'),
									description: $t('payment.recipientInfoDescription')
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
										<label for="recipient_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('payment.recipientName')} *
										</label>
										<input
											type="text"
											id="recipient_name"
											bind:value={formData.recipient_name}
											class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
											placeholder={$t('payment.recipientNamePlaceholder')}
											class:border-red-500={validationErrors.recipient_name}
											on:input={validateCurrentTab}
										/>
										{#if validationErrors.recipient_name}
											<p class="mt-1 text-sm text-red-600">{validationErrors.recipient_name}</p>
										{/if}
									</div>

									<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
										<div>
											<label for="recipient_email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
												{$t('payment.recipientEmail')}
											</label>
											<input
												type="email"
												id="recipient_email"
												bind:value={formData.recipient_email}
												class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
												placeholder="example@email.com"
												class:border-red-500={validationErrors.recipient_email}
												on:input={validateCurrentTab}
											/>
											{#if validationErrors.recipient_email}
												<p class="mt-1 text-sm text-red-600">{validationErrors.recipient_email}</p>
											{/if}
										</div>

										<div>
											<label for="recipient_phone" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
												{$t('payment.recipientPhone')}
											</label>
											<input
												type="tel"
												id="recipient_phone"
												bind:value={formData.recipient_phone}
												class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
												placeholder="+966 50 123 4567"
											/>
										</div>
									</div>
								</div>
							</FormStep>
						{/if}

						<!-- Associations Tab -->
						{#if currentTab === 2}
							<FormStep
								step={{
									id: 'associations',
									title: $t('payment.associations'),
									description: $t('payment.associationsDescription')
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
										<label for="related_property" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('payment.relatedProperty')}
										</label>
										<select
											id="related_property"
											bind:value={formData.related_property}
											class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
										>
											<option value={null}>{$t('payment.selectProperty')}</option>
											{#each properties as property}
												<option value={property.id}>{property.title}</option>
											{/each}
										</select>
									</div>

									<div>
										<label for="bank_account" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('payment.bankAccount')}
										</label>
										<select
											id="bank_account"
											bind:value={formData.bank_account}
											class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
										>
											<option value={null}>{$t('payment.selectBankAccount')}</option>
											{#each bankAccounts as account}
												<option value={account.id}>{account.bank_account_name} - {account.bank_name}</option>
											{/each}
										</select>
									</div>
								</div>
							</FormStep>
						{/if}

						<!-- Scheduling Tab -->
						{#if currentTab === 3}
							<FormStep
								step={{
									id: 'schedule',
									title: $t('payment.scheduling'),
									description: $t('payment.schedulingDescription'),
									submitText: $t('payment.createPayment'),
									submitLoadingText: $t('payment.creating')
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
											<label for="due_date" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
												{$t('payment.dueDate')}
											</label>
											<input
												type="date"
												id="due_date"
												bind:value={formData.due_date}
												min={getTodayDate()}
												class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
												on:change={validateCurrentTab}
											/>
										</div>

										<div>
											<label for="payment_date" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
												{$t('payment.paymentDate')}
											</label>
											<input
												type="date"
												id="payment_date"
												bind:value={formData.payment_date}
												class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
												class:border-red-500={validationErrors.payment_date}
												on:change={validateCurrentTab}
											/>
											{#if validationErrors.payment_date}
												<p class="mt-1 text-sm text-red-600">{validationErrors.payment_date}</p>
											{/if}
										</div>
									</div>

									<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
										<div>
											<label for="status" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
												{$t('payment.status')}
											</label>
											<select
												id="status"
												bind:value={formData.status}
												class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
											>
												{#each paymentStatuses as status}
													<option value={status.value}>{status.label}</option>
												{/each}
											</select>
										</div>

										<div>
											<label for="reference_number" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
												{$t('payment.referenceNumber')}
											</label>
											<input
												type="text"
												id="reference_number"
												bind:value={formData.reference_number}
												class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
												placeholder={$t('payment.referenceNumberPlaceholder')}
											/>
										</div>
									</div>

									<div>
										<label for="notes" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
											{$t('payment.notes')}
										</label>
										<textarea
											id="notes"
											bind:value={formData.notes}
											rows="4"
											class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
											placeholder={$t('payment.notesPlaceholder')}
										></textarea>
									</div>

									<!-- Summary -->
									<div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
										<h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">
											{$t('form.summary')}
										</h4>
										<dl class="space-y-2 text-sm">
											<div class="flex justify-between">
												<dt class="text-gray-600 dark:text-gray-400">{$t('payment.amount')}:</dt>
												<dd class="font-medium text-gray-900 dark:text-gray-100">${formData.amount}</dd>
											</div>
											<div class="flex justify-between">
												<dt class="text-gray-600 dark:text-gray-400">{$t('payment.paymentType')}:</dt>
												<dd class="font-medium text-gray-900 dark:text-gray-100">
													{paymentTypes.find(t => t.value === formData.payment_type)?.label}
												</dd>
											</div>
											<div class="flex justify-between">
												<dt class="text-gray-600 dark:text-gray-400">{$t('payment.recipientName')}:</dt>
												<dd class="font-medium text-gray-900 dark:text-gray-100">{formData.recipient_name}</dd>
											</div>
											<div class="flex justify-between">
												<dt class="text-gray-600 dark:text-gray-400">{$t('payment.status')}:</dt>
												<dd class="font-medium text-gray-900 dark:text-gray-100">
													{paymentStatuses.find(s => s.value === formData.status)?.label}
												</dd>
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
			{/if}
		</div>
	</div>
</div>
