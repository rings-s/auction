<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { t, locale } from '$lib/i18n';
	import { user } from '$lib/stores/user.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';
	import LoadingSpinner from '$lib/components/animations/LoadingSpinner.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import { tenantsAPI } from '$lib/api/propertyManagement.js';
	import { fade } from 'svelte/transition';

	let isRTL = $derived($locale === 'ar');

	// State using Svelte 5 runes
	let loading = $state(true);
	let saving = $state(false);
	let error = $state('');
	let validationErrors = $state({});
	let showUnsavedModal = $state(false);
	let hasUnsavedChanges = $state(false);

	// Get tenant ID from URL params
	let tenantId = $derived($page.params.id);

	// Form data
	let formData = $state({
		name: '',
		email: '',
		phone: '',
		property: null,
		lease_start: '',
		lease_end: '',
		monthly_rent: '',
		security_deposit: '',
		status: 'active',
		emergency_contact: '',
		notes: ''
	});

	// Permission check
	let hasAccess = $derived(
		($user && ['owner', 'appraiser', 'data_entry'].includes($user.role)) || $user?.is_superuser
	);

	// Property status options
	const statusOptions = [
		{ value: 'active', label: $t('tenant.status.active') },
		{ value: 'inactive', label: $t('tenant.status.inactive') },
		{ value: 'pending', label: $t('tenant.status.pending') }
	];

	onMount(() => {
		if (!hasAccess) {
			goto('/property-management/tenants');
			return;
		}
		if (tenantId) {
			loadTenant();
		}
	});

	async function loadTenant() {
		try {
			loading = true;
			error = '';

			const response = await tenantsAPI.getById(tenantId);
			if (response.data) {
				const tenant = response.data;
				formData = {
					name: tenant.name || '',
					email: tenant.email || '',
					phone: tenant.phone || '',
					property: tenant.property?.id || null,
					lease_start: tenant.lease_start || '',
					lease_end: tenant.lease_end || '',
					monthly_rent: tenant.monthly_rent || '',
					security_deposit: tenant.security_deposit || '',
					status: tenant.status || 'active',
					emergency_contact: tenant.emergency_contact || '',
					notes: tenant.notes || ''
				};
			}
		} catch (err) {
			error = err.message || $t('errors.loadingFailed');
			console.error('Failed to load tenant:', err);
		} finally {
			loading = false;
		}
	}

	function validateForm() {
		const errors = {};

		if (!formData.name?.trim()) {
			errors.name = $t('validation.required');
		}

		if (!formData.email?.trim()) {
			errors.email = $t('validation.required');
		} else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
			errors.email = $t('validation.invalidEmail');
		}

		if (formData.phone && !/^[\+]?[1-9][\d]{0,15}$/.test(formData.phone.replace(/\s/g, ''))) {
			errors.phone = $t('validation.invalidPhone');
		}

		if (formData.monthly_rent && parseFloat(formData.monthly_rent) < 0) {
			errors.monthly_rent = $t('validation.mustBePositive');
		}

		if (formData.security_deposit && parseFloat(formData.security_deposit) < 0) {
			errors.security_deposit = $t('validation.mustBePositive');
		}

		if (formData.lease_start && formData.lease_end) {
			const startDate = new Date(formData.lease_start);
			const endDate = new Date(formData.lease_end);
			if (startDate >= endDate) {
				errors.lease_end = $t('validation.endDateAfterStart');
			}
		}

		return errors;
	}

	async function handleSave() {
		try {
			saving = true;
			validationErrors = {};

			const errors = validateForm();
			if (Object.keys(errors).length > 0) {
				validationErrors = errors;
				saving = false;
				return;
			}

			// Convert numeric fields
			const updateData = {
				...formData,
				monthly_rent: formData.monthly_rent ? parseFloat(formData.monthly_rent) : null,
				security_deposit: formData.security_deposit ? parseFloat(formData.security_deposit) : null
			};

			const response = await tenantsAPI.update(tenantId, updateData);
			hasUnsavedChanges = false;
			goto(`/property-management/tenants/${tenantId}`);
		} catch (err) {
			error = err.message || $t('error.saveFailed');
			console.error('Failed to update tenant:', err);
		} finally {
			saving = false;
		}
	}

	function handleCancel() {
		if (hasUnsavedChanges) {
			showUnsavedModal = true;
		} else {
			goto(`/property-management/tenants/${tenantId}`);
		}
	}

	function handleDiscardChanges() {
		showUnsavedModal = false;
		hasUnsavedChanges = false;
		goto(`/property-management/tenants/${tenantId}`);
	}

	function markAsChanged() {
		hasUnsavedChanges = true;
	}
</script>

<svelte:head>
	<title>{$t('tenant.editTitle')} | {$t('propertyManagement.title')} | {$t('app.name')}</title>
	<meta name="description" content={$t('tenant.editDescription')} />
</svelte:head>

<div
	class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-gray-900 dark:via-blue-900 dark:to-indigo-900"
	dir={isRTL ? 'rtl' : 'ltr'}
>
	<div class="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
		<!-- Header -->
		<div class="mb-8">
			<div class="flex items-center justify-between">
				<div>
					<button
						onclick={() => goto(`/property-management/tenants/${tenantId}`)}
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
						{$t('tenant.backToDetails')}
					</button>
					<h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">
						{$t('tenant.editTitle')}
					</h1>
					<p class="mt-2 text-gray-600 dark:text-gray-400">
						{$t('tenant.editSubtitle')}
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
		{:else if loading}
			<!-- Loading State -->
			<div
				class="rounded-2xl border border-gray-200 bg-white p-8 shadow-xl dark:border-gray-700 dark:bg-gray-800"
			>
				<div class="animate-pulse space-y-6">
					<div class="h-8 w-1/3 rounded-xl bg-gray-200 dark:bg-gray-700"></div>
					<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
						{#each Array(8) as _}
							<div class="space-y-2">
								<div class="h-4 w-1/4 rounded bg-gray-200 dark:bg-gray-700"></div>
								<div class="h-10 rounded-xl bg-gray-200 dark:bg-gray-700"></div>
							</div>
						{/each}
					</div>
				</div>
			</div>
		{:else}
			<!-- Edit Form -->
			<div class="space-y-8" transition:fade={{ duration: 300 }}>
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
									d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
								/>
							</svg>
							{$t('tenant.basicInfo')}
						</h2>
					</div>
					<div class="space-y-6 p-8">
						<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
							<!-- Name -->
							<div>
								<label
									for="name"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('tenant.name')} <span class="text-red-500">*</span>
								</label>
								<input
									type="text"
									id="name"
									bind:value={formData.name}
									oninput={markAsChanged}
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100
										{validationErrors.name ? 'border-red-500 focus:ring-red-500' : ''}"
									placeholder={$t('tenant.namePlaceholder')}
									required
								/>
								{#if validationErrors.name}
									<p class="mt-2 text-sm text-red-600 dark:text-red-400">{validationErrors.name}</p>
								{/if}
							</div>

							<!-- Email -->
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
									bind:value={formData.email}
									oninput={markAsChanged}
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
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

							<!-- Phone -->
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
									bind:value={formData.phone}
									oninput={markAsChanged}
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100
										{validationErrors.phone ? 'border-red-500 focus:ring-red-500' : ''}"
									placeholder={$t('tenant.phonePlaceholder')}
								/>
								{#if validationErrors.phone}
									<p class="mt-2 text-sm text-red-600 dark:text-red-400">
										{validationErrors.phone}
									</p>
								{/if}
							</div>

							<!-- Status -->
							<div>
								<label
									for="status"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('tenant.status')}
								</label>
								<select
									id="status"
									bind:value={formData.status}
									onchange={markAsChanged}
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100"
								>
									{#each statusOptions as option}
										<option value={option.value}>{option.label}</option>
									{/each}
								</select>
							</div>
						</div>

						<!-- Emergency Contact -->
						<div>
							<label
								for="emergency_contact"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('tenant.emergencyContact')}
							</label>
							<input
								type="text"
								id="emergency_contact"
								bind:value={formData.emergency_contact}
								oninput={markAsChanged}
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
									text-gray-900 transition-all duration-200
									focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
									dark:bg-gray-700 dark:text-gray-100"
								placeholder={$t('tenant.emergencyContactPlaceholder')}
							/>
						</div>
					</div>
				</div>

				<!-- Lease Information -->
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
									d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
								/>
							</svg>
							{$t('tenant.leaseInfo')}
						</h2>
					</div>
					<div class="space-y-6 p-8">
						<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
							<!-- Monthly Rent -->
							<div>
								<label
									for="monthly_rent"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('tenant.monthlyRent')}
								</label>
								<input
									type="number"
									id="monthly_rent"
									bind:value={formData.monthly_rent}
									oninput={markAsChanged}
									min="0"
									step="0.01"
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100
										{validationErrors.monthly_rent ? 'border-red-500 focus:ring-red-500' : ''}"
									placeholder="0.00"
								/>
								{#if validationErrors.monthly_rent}
									<p class="mt-2 text-sm text-red-600 dark:text-red-400">
										{validationErrors.monthly_rent}
									</p>
								{/if}
							</div>

							<!-- Security Deposit -->
							<div>
								<label
									for="security_deposit"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('tenant.securityDeposit')}
								</label>
								<input
									type="number"
									id="security_deposit"
									bind:value={formData.security_deposit}
									oninput={markAsChanged}
									min="0"
									step="0.01"
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100
										{validationErrors.security_deposit ? 'border-red-500 focus:ring-red-500' : ''}"
									placeholder="0.00"
								/>
								{#if validationErrors.security_deposit}
									<p class="mt-2 text-sm text-red-600 dark:text-red-400">
										{validationErrors.security_deposit}
									</p>
								{/if}
							</div>

							<!-- Lease Start -->
							<div>
								<label
									for="lease_start"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('tenant.leaseStart')}
								</label>
								<input
									type="date"
									id="lease_start"
									bind:value={formData.lease_start}
									onchange={markAsChanged}
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100"
								/>
							</div>

							<!-- Lease End -->
							<div>
								<label
									for="lease_end"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('tenant.leaseEnd')}
								</label>
								<input
									type="date"
									id="lease_end"
									bind:value={formData.lease_end}
									onchange={markAsChanged}
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
										text-gray-900 transition-all duration-200
										focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
										dark:bg-gray-700 dark:text-gray-100
										{validationErrors.lease_end ? 'border-red-500 focus:ring-red-500' : ''}"
								/>
								{#if validationErrors.lease_end}
									<p class="mt-2 text-sm text-red-600 dark:text-red-400">
										{validationErrors.lease_end}
									</p>
								{/if}
							</div>
						</div>
					</div>
				</div>

				<!-- Notes -->
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
									d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
								/>
							</svg>
							{$t('tenant.notes')}
						</h2>
					</div>
					<div class="p-8">
						<div>
							<label
								for="notes"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('tenant.additionalNotes')}
							</label>
							<textarea
								id="notes"
								bind:value={formData.notes}
								oninput={markAsChanged}
								rows="4"
								class="w-full resize-none rounded-xl border border-gray-300 bg-white px-4
									py-3 text-gray-900 transition-all
									duration-200 focus:border-transparent focus:ring-2 focus:ring-blue-500
									dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
								placeholder={$t('tenant.notesPlaceholder')}
							></textarea>
						</div>
					</div>
				</div>

				<!-- Action Buttons -->
				<div
					class="flex items-center justify-between border-t border-gray-200 pt-6 dark:border-gray-700"
				>
					<Button variant="outline" onclick={handleCancel} disabled={saving}>
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
						{$t('common.cancel')}
					</Button>

					<Button
						variant="primary"
						onclick={handleSave}
						disabled={saving}
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
		animation: gradient-shift 8s ease infinite;
	}
</style>
