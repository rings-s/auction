<script>
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import { userStore } from '$lib/stores/user.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import { tenantsAPI, rentalPropertyAPI } from '$lib/api/propertyManagement.js';
	import { onMount } from 'svelte';

	// State
	let submitting = false;
	let error = '';
	let success = '';
	let properties = [];

	// Form data
	let formData = {
		first_name: '',
		last_name: '',
		email: '',
		phone: '',
		national_id: '',
		current_address: '',
		property: '',
		lease_start: '',
		lease_end: '',
		monthly_rent: '',
		security_deposit: '',
		status: 'active',
		emergency_contact_name: '',
		emergency_contact_phone: '',
		notes: '',
		occupation: '',
		employer: ''
	};

	$: user = $userStore;
	$: hasAccess =
		(user && ['owner', 'appraiser', 'data_entry'].includes(user.role)) || user?.is_superuser;

	onMount(async () => {
		if (!hasAccess) {
			goto('/dashboard');
			return;
		}
		await loadProperties();
	});

	async function loadProperties() {
		try {
			const response = await rentalPropertyAPI.getAll({ page_size: 100 });
			properties = response.data?.results || [];
		} catch (err) {
			console.error('Failed to load properties:', err);
		}
	}

	async function handleSubmit() {
		try {
			submitting = true;
			error = '';
			success = '';

			// Prepare form data - remove non-tenant fields and format correctly
			const tenantData = {
				first_name: formData.first_name,
				last_name: formData.last_name,
				email: formData.email,
				phone: formData.phone,
				national_id: formData.national_id,
				current_address: formData.current_address,
				status: formData.status,
				emergency_contact_name: formData.emergency_contact_name,
				emergency_contact_phone: formData.emergency_contact_phone,
				notes: formData.notes,
				occupation: formData.occupation,
				employer: formData.employer
			};

			const response = await tenantsAPI.create(tenantData);

			if (response.data) {
				success = $t('tenant.createSuccess');
				setTimeout(() => {
					goto('/property-management/tenants');
				}, 1500);
			}
		} catch (err) {
			error = err.message || $t('tenant.createError');
		} finally {
			submitting = false;
		}
	}

	function handleCancel() {
		goto('/property-management/tenants');
	}
</script>

<svelte:head>
	<title>{$t('tenant.create')} | {$t('app.name')}</title>
</svelte:head>

{#if !hasAccess}
	<div class="flex min-h-screen items-center justify-center">
		<Alert type="error" message={$t('errors.accessDenied')} />
	</div>
{:else}
	<div class="container mx-auto max-w-4xl space-y-8 px-4 py-8">
		<!-- Header -->
		<div class="flex items-center justify-between">
			<div>
				<h1 class="text-3xl font-bold tracking-tight text-gray-800 dark:text-gray-100">
					{$t('tenant.create')}
				</h1>
				<p class="mt-2 text-gray-600 dark:text-gray-400">
					{$t('tenant.createDescription')}
				</p>
			</div>

			<Button variant="ghost" on:click={handleCancel}>
				<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M10 19l-7-7m0 0l7-7m-7 7h18"
					/>
				</svg>
				{$t('common.back')}
			</Button>
		</div>

		<!-- Success/Error Messages -->
		{#if error}
			<Alert type="error" message={error} />
		{/if}

		{#if success}
			<Alert type="success" message={success} />
		{/if}

		<!-- Form -->
		<div
			class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
		>
			<form
				on:submit|preventDefault={handleSubmit}
				class="divide-y divide-gray-200 dark:divide-gray-700"
			>
				<!-- Personal Information -->
				<div class="p-8">
					<div class="mb-8">
						<h2
							class="font-sans text-xl font-semibold tracking-tight text-gray-900 dark:text-gray-100"
						>
							{$t('tenant.personalInfo')}
						</h2>
						<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
							{$t('tenant.personalInfoDesc')}
						</p>
					</div>

					<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
						<div>
							<label
								for="first_name"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('tenant.firstName')} *
							</label>
							<input
								type="text"
								id="first_name"
								bind:value={formData.first_name}
								required
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
								placeholder={$t('tenant.firstNamePlaceholder')}
							/>
						</div>

						<div>
							<label
								for="last_name"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('tenant.lastName')} *
							</label>
							<input
								type="text"
								id="last_name"
								bind:value={formData.last_name}
								required
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
								placeholder={$t('tenant.lastNamePlaceholder')}
							/>
						</div>

						<div>
							<label
								for="email"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('tenant.email')} *
							</label>
							<input
								type="email"
								id="email"
								bind:value={formData.email}
								required
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
								placeholder={$t('tenant.emailPlaceholder')}
							/>
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
								bind:value={formData.phone}
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
								placeholder={$t('tenant.phonePlaceholder')}
							/>
						</div>

						<div>
							<label
								for="national_id"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('tenant.nationalId')} *
							</label>
							<input
								type="text"
								id="national_id"
								bind:value={formData.national_id}
								required
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
								placeholder={$t('tenant.nationalIdPlaceholder')}
							/>
						</div>

						<div class="md:col-span-2">
							<label
								for="current_address"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('tenant.currentAddress')} *
							</label>
							<textarea
								id="current_address"
								bind:value={formData.current_address}
								required
								rows="3"
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
								placeholder={$t('tenant.currentAddressPlaceholder')}
							></textarea>
						</div>

						<div>
							<label
								for="occupation"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('tenant.occupation')}
							</label>
							<input
								type="text"
								id="occupation"
								bind:value={formData.occupation}
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
								placeholder={$t('tenant.occupationPlaceholder')}
							/>
						</div>

						<div>
							<label
								for="employer"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('tenant.employer')}
							</label>
							<input
								type="text"
								id="employer"
								bind:value={formData.employer}
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
								placeholder={$t('tenant.employerPlaceholder')}
							/>
						</div>
					</div>
				</div>

				<!-- Lease Information -->
				<div class="p-8">
					<div class="mb-8">
						<h2
							class="font-sans text-xl font-semibold tracking-tight text-gray-900 dark:text-gray-100"
						>
							{$t('tenant.leaseInfo')}
						</h2>
						<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
							{$t('tenant.leaseInfoDesc')}
						</p>
					</div>

					<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
						<div class="md:col-span-2">
							<label
								for="property"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('tenant.property')}
							</label>
							<select
								id="property"
								bind:value={formData.property}
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
							>
								<option value="">{$t('tenant.selectProperty')}</option>
								{#each properties as property}
									<option value={property.id}>{property.name} - {property.address}</option>
								{/each}
							</select>
						</div>

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
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
							/>
						</div>

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
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
							/>
						</div>

						<div>
							<label
								for="monthly_rent"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('tenant.monthlyRent')}
							</label>
							<div class="relative">
								<input
									type="number"
									id="monthly_rent"
									bind:value={formData.monthly_rent}
									min="0"
									step="0.01"
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 pr-12 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
									placeholder="0.00"
								/>
								<div class="absolute inset-y-0 right-0 flex items-center pr-3">
									<span class="text-gray-500 sm:text-sm">SAR</span>
								</div>
							</div>
						</div>

						<div>
							<label
								for="security_deposit"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('tenant.securityDeposit')}
							</label>
							<div class="relative">
								<input
									type="number"
									id="security_deposit"
									bind:value={formData.security_deposit}
									min="0"
									step="0.01"
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 pr-12 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
									placeholder="0.00"
								/>
								<div class="absolute inset-y-0 right-0 flex items-center pr-3">
									<span class="text-gray-500 sm:text-sm">SAR</span>
								</div>
							</div>
						</div>

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
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
							>
								<option value="active">{$t('tenant.status.active')}</option>
								<option value="inactive">{$t('tenant.status.inactive')}</option>
								<option value="pending">{$t('tenant.status.pending')}</option>
							</select>
						</div>
					</div>
				</div>

				<!-- Additional Information -->
				<div class="p-8">
					<div class="mb-8">
						<h2
							class="font-sans text-xl font-semibold tracking-tight text-gray-900 dark:text-gray-100"
						>
							{$t('tenant.additionalInfo')}
						</h2>
						<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
							{$t('tenant.additionalInfoDesc')}
						</p>
					</div>

					<div class="space-y-6">
						<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
							<div>
								<label
									for="emergency_contact_name"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('tenant.emergencyContactName')}
								</label>
								<input
									type="text"
									id="emergency_contact_name"
									bind:value={formData.emergency_contact_name}
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
									placeholder={$t('tenant.emergencyContactNamePlaceholder')}
								/>
							</div>

							<div>
								<label
									for="emergency_contact_phone"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('tenant.emergencyContactPhone')}
								</label>
								<input
									type="tel"
									id="emergency_contact_phone"
									bind:value={formData.emergency_contact_phone}
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
									placeholder={$t('tenant.emergencyContactPhonePlaceholder')}
								/>
							</div>
						</div>

						<div>
							<label
								for="notes"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('tenant.notes')}
							</label>
							<textarea
								id="notes"
								bind:value={formData.notes}
								rows="4"
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
								placeholder={$t('tenant.notesPlaceholder')}
							></textarea>
						</div>
					</div>
				</div>

				<!-- Form Actions -->
				<div class="bg-gray-50 px-8 py-6 dark:bg-gray-900">
					<div class="flex justify-end space-x-4">
						<Button type="button" variant="outline" on:click={handleCancel} disabled={submitting}>
							{$t('common.cancel')}
						</Button>
						<Button
							type="submit"
							variant="primary"
							class="bg-gradient-to-r from-indigo-500 to-purple-600 shadow-lg hover:from-indigo-600 hover:to-purple-700 hover:shadow-xl"
							disabled={submitting}
						>
							{#if submitting}
								<svg
									class="mr-3 -ml-1 h-4 w-4 animate-spin text-white"
									xmlns="http://www.w3.org/2000/svg"
									fill="none"
									viewBox="0 0 24 24"
								>
									<circle
										class="opacity-25"
										cx="12"
										cy="12"
										r="10"
										stroke="currentColor"
										stroke-width="4"
									></circle>
									<path
										class="opacity-75"
										fill="currentColor"
										d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
									></path>
								</svg>
								{$t('common.creating')}
							{:else}
								<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 6v6m0 0v6m0-6h6m-6 0H6"
									/>
								</svg>
								{$t('tenant.create')}
							{/if}
						</Button>
					</div>
				</div>
			</form>
		</div>
	</div>
{/if}
