<script>
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { t } from '$lib/i18n';
	import { userStore } from '$lib/stores/user.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';
	import { maintenanceAPI, rentalPropertyAPI, tenantsAPI } from '$lib/api/propertyManagement.js';

	// State
	let submitting = false;
	let error = '';
	let success = '';
	let properties = [];
	let tenants = [];
	let categories = [];

	// Form data
	let formData = {
		title: '',
		description: '',
		priority: 'medium',
		status: 'pending',
		tenant: '',
		property: '',
		category: '',
		estimated_cost: '',
		reported_date: new Date().toISOString().split('T')[0],
		scheduled_date: '',
		notes: ''
	};

	$: user = $userStore;
	$: hasAccess =
		(user && ['owner', 'appraiser', 'data_entry'].includes(user.role)) || user?.is_superuser;

	onMount(async () => {
		if (!hasAccess) {
			goto('/dashboard');
			return;
		}
		await Promise.all([loadProperties(), loadTenants(), loadCategories()]);
	});

	async function loadProperties() {
		try {
			const response = await rentalPropertyAPI.getAll({ page_size: 100 });
			properties = response.data?.results || [];
		} catch (err) {
			console.error('Failed to load properties:', err);
		}
	}

	async function loadTenants() {
		try {
			const response = await tenantsAPI.getAll({ page_size: 100 });
			tenants = response.data?.results || [];
		} catch (err) {
			console.error('Failed to load tenants:', err);
		}
	}

	async function loadCategories() {
		try {
			const response = await maintenanceAPI.categories.getAll();
			categories = response.data?.results || [];
		} catch (err) {
			console.error('Failed to load categories:', err);
			// Use default categories if API fails
			categories = [
				{ id: 'plumbing', name: 'Plumbing' },
				{ id: 'electrical', name: 'Electrical' },
				{ id: 'hvac', name: 'HVAC' },
				{ id: 'appliances', name: 'Appliances' },
				{ id: 'general', name: 'General Maintenance' }
			];
		}
	}

	async function handleSubmit() {
		try {
			submitting = true;
			error = '';
			success = '';

			// Prepare form data
			const requestData = {
				...formData,
				estimated_cost: formData.estimated_cost ? parseFloat(formData.estimated_cost) : null,
				tenant: formData.tenant || null,
				property: formData.property || null,
				category: formData.category || null
			};

			const response = await maintenanceAPI.requests.create(requestData);

			if (response.data) {
				success = $t('maintenance.createSuccess');
				setTimeout(() => {
					goto('/property-management/maintenance');
				}, 1500);
			}
		} catch (err) {
			error = err.message || $t('maintenance.createError');
		} finally {
			submitting = false;
		}
	}

	function handleCancel() {
		goto('/property-management/maintenance');
	}

	function getPriorityColor(priority) {
		switch (priority) {
			case 'low':
				return 'text-gray-600';
			case 'medium':
				return 'text-blue-600';
			case 'high':
				return 'text-orange-600';
			case 'urgent':
				return 'text-red-600';
			default:
				return 'text-blue-600';
		}
	}
</script>

<svelte:head>
	<title>{$t('maintenance.create')} | {$t('app.name')}</title>
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
					{$t('maintenance.create')}
				</h1>
				<p class="mt-2 text-gray-600 dark:text-gray-400">
					{$t('maintenance.createDescription')}
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
				<!-- Basic Information -->
				<div class="p-8">
					<div class="mb-8">
						<h2
							class="font-sans text-xl font-semibold tracking-tight text-gray-900 dark:text-gray-100"
						>
							{$t('maintenance.basicInfo')}
						</h2>
						<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
							{$t('maintenance.basicInfoDesc')}
						</p>
					</div>

					<div class="space-y-6">
						<div>
							<label
								for="title"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('maintenance.title')} *
							</label>
							<input
								type="text"
								id="title"
								bind:value={formData.title}
								required
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
								placeholder={$t('maintenance.titlePlaceholder')}
							/>
						</div>

						<div>
							<label
								for="description"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('maintenance.description')} *
							</label>
							<textarea
								id="description"
								bind:value={formData.description}
								required
								rows="4"
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
								placeholder={$t('maintenance.descriptionPlaceholder')}
							></textarea>
						</div>

						<div class="grid grid-cols-1 gap-6 md:grid-cols-3">
							<div>
								<label
									for="priority"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('maintenance.priority')} *
								</label>
								<select
									id="priority"
									bind:value={formData.priority}
									required
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
								>
									<option value="low" class={getPriorityColor('low')}
										>{$t('maintenance.priority.low')}</option
									>
									<option value="medium" class={getPriorityColor('medium')}
										>{$t('maintenance.priority.medium')}</option
									>
									<option value="high" class={getPriorityColor('high')}
										>{$t('maintenance.priority.high')}</option
									>
									<option value="urgent" class={getPriorityColor('urgent')}
										>{$t('maintenance.priority.urgent')}</option
									>
								</select>
							</div>

							<div>
								<label
									for="status"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('maintenance.status')}
								</label>
								<select
									id="status"
									bind:value={formData.status}
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
								>
									<option value="pending">{$t('maintenance.status.pending')}</option>
									<option value="in-progress">{$t('maintenance.status.inProgress')}</option>
									<option value="completed">{$t('maintenance.status.completed')}</option>
									<option value="cancelled">{$t('maintenance.status.cancelled')}</option>
								</select>
							</div>

							<div>
								<label
									for="category"
									class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
								>
									{$t('maintenance.category')}
								</label>
								<select
									id="category"
									bind:value={formData.category}
									class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
								>
									<option value="">{$t('maintenance.selectCategory')}</option>
									{#each categories as category}
										<option value={category.id}>{category.name}</option>
									{/each}
								</select>
							</div>
						</div>
					</div>
				</div>

				<!-- Location and Assignment -->
				<div class="p-8">
					<div class="mb-8">
						<h2
							class="font-sans text-xl font-semibold tracking-tight text-gray-900 dark:text-gray-100"
						>
							{$t('maintenance.locationAssignment')}
						</h2>
						<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
							{$t('maintenance.locationAssignmentDesc')}
						</p>
					</div>

					<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
						<div>
							<label
								for="property"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('maintenance.property')}
							</label>
							<select
								id="property"
								bind:value={formData.property}
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
							>
								<option value="">{$t('maintenance.selectProperty')}</option>
								{#each properties as property}
									<option value={property.id}>{property.name} - {property.address}</option>
								{/each}
							</select>
						</div>

						<div>
							<label
								for="tenant"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('maintenance.tenant')}
							</label>
							<select
								id="tenant"
								bind:value={formData.tenant}
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
							>
								<option value="">{$t('maintenance.selectTenant')}</option>
								{#each tenants as tenant}
									<option value={tenant.id}>{tenant.name} - {tenant.email}</option>
								{/each}
							</select>
						</div>
					</div>
				</div>

				<!-- Scheduling and Budget -->
				<div class="p-8">
					<div class="mb-8">
						<h2
							class="font-sans text-xl font-semibold tracking-tight text-gray-900 dark:text-gray-100"
						>
							{$t('maintenance.schedulingBudget')}
						</h2>
						<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
							{$t('maintenance.schedulingBudgetDesc')}
						</p>
					</div>

					<div class="grid grid-cols-1 gap-6 md:grid-cols-3">
						<div>
							<label
								for="reported_date"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('maintenance.reportedDate')}
							</label>
							<input
								type="date"
								id="reported_date"
								bind:value={formData.reported_date}
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
							/>
						</div>

						<div>
							<label
								for="scheduled_date"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('maintenance.scheduledDate')}
							</label>
							<input
								type="date"
								id="scheduled_date"
								bind:value={formData.scheduled_date}
								class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
							/>
						</div>

						<div>
							<label
								for="estimated_cost"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('maintenance.estimatedCost')}
							</label>
							<div class="relative">
								<input
									type="number"
									id="estimated_cost"
									bind:value={formData.estimated_cost}
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
					</div>
				</div>

				<!-- Additional Notes -->
				<div class="p-8">
					<div class="mb-8">
						<h2
							class="font-sans text-xl font-semibold tracking-tight text-gray-900 dark:text-gray-100"
						>
							{$t('maintenance.additionalNotes')}
						</h2>
						<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
							{$t('maintenance.additionalNotesDesc')}
						</p>
					</div>

					<div>
						<label
							for="notes"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('maintenance.notes')}
						</label>
						<textarea
							id="notes"
							bind:value={formData.notes}
							rows="4"
							class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 font-sans tracking-tight text-gray-900 focus:border-indigo-500 focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
							placeholder={$t('maintenance.notesPlaceholder')}
						></textarea>
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
								{$t('maintenance.create')}
							{/if}
						</Button>
					</div>
				</div>
			</form>
		</div>
	</div>
{/if}
