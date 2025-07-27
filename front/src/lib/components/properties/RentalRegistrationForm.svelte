<!-- Rental Property Registration Form - Svelte 5 -->
<script>
	import { t } from '$lib/i18n';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import FormField from '$lib/components/ui/FormField.svelte';

	let { property, isOpen = false, onClose = () => {}, onSubmit = () => {} } = $props();

	// Svelte 5 runes for form state
	let formData = $state({
		monthly_rent: '',
		security_deposit: '',
		rental_type: 'monthly',
		management_fee_percentage: '0',
		utilities_included: false,
		parking_spaces: '0',
		furnished: false,
		pets_allowed: false,
		smoking_allowed: false,
		available_from: '',
		minimum_lease_period: '12',
		maximum_lease_period: '36',
		utilities_details: {
			electricity: false,
			water: false,
			internet: false,
			gas: false,
			heating: false,
			air_conditioning: false
		}
	});

	let isSubmitting = $state(false);
	let errors = $state({});

	// Derived computed values using Svelte 5 $derived
	const isFormValid = $derived(() => {
		return (
			formData.monthly_rent &&
			formData.security_deposit &&
			formData.available_from &&
			Object.keys(errors).length === 0
		);
	});

	const monthlyRentNumber = $derived(() => parseFloat(formData.monthly_rent) || 0);
	const annualIncome = $derived(() => monthlyRentNumber * 12);

	// Form validation using $effect
	$effect(() => {
		const newErrors = {};

		if (
			formData.monthly_rent &&
			(isNaN(parseFloat(formData.monthly_rent)) || parseFloat(formData.monthly_rent) <= 0)
		) {
			newErrors.monthly_rent = $t('property.rental.errors.invalidRent');
		}

		if (
			formData.security_deposit &&
			(isNaN(parseFloat(formData.security_deposit)) || parseFloat(formData.security_deposit) < 0)
		) {
			newErrors.security_deposit = $t('property.rental.errors.invalidDeposit');
		}

		if (
			formData.management_fee_percentage &&
			(parseFloat(formData.management_fee_percentage) < 0 ||
				parseFloat(formData.management_fee_percentage) > 100)
		) {
			newErrors.management_fee_percentage = $t('property.rental.errors.invalidFeePercentage');
		}

		errors = newErrors;
	});

	function formatCurrency(value) {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			maximumFractionDigits: 0
		}).format(value);
	}

	function handleUtilityChange(utility, checked) {
		formData.utilities_details = {
			...formData.utilities_details,
			[utility]: checked
		};
	}

	async function handleSubmit(e) {
		e.preventDefault();

		if (!isFormValid()) return;

		isSubmitting = true;

		try {
			const rentalData = {
				base_property: property.id,
				...formData,
				monthly_rent: parseFloat(formData.monthly_rent),
				security_deposit: parseFloat(formData.security_deposit),
				management_fee_percentage: parseFloat(formData.management_fee_percentage),
				parking_spaces: parseInt(formData.parking_spaces),
				minimum_lease_period: parseInt(formData.minimum_lease_period),
				maximum_lease_period: parseInt(formData.maximum_lease_period)
			};

			await onSubmit(rentalData);
			onClose();
		} catch (error) {
			console.error('Error creating rental property:', error);
		} finally {
			isSubmitting = false;
		}
	}

	function resetForm() {
		formData = {
			monthly_rent: '',
			security_deposit: '',
			rental_type: 'monthly',
			management_fee_percentage: '0',
			utilities_included: false,
			parking_spaces: '0',
			furnished: false,
			pets_allowed: false,
			smoking_allowed: false,
			available_from: '',
			minimum_lease_period: '12',
			maximum_lease_period: '36',
			utilities_details: {
				electricity: false,
				water: false,
				internet: false,
				gas: false,
				heating: false,
				air_conditioning: false
			}
		};
		errors = {};
	}

	// Reset form when modal opens
	$effect(() => {
		if (isOpen) {
			resetForm();
		}
	});
</script>

<Modal bind:isOpen title={$t('property.rental.createTitle')} size="large" {onClose}>
	<form onsubmit={handleSubmit} class="space-y-6">
		<!-- Property Info Header -->
		<div class="rounded-lg bg-gray-50 p-4 dark:bg-gray-800">
			<h3 class="font-medium text-gray-900 dark:text-white">{property?.title}</h3>
			<p class="text-sm text-gray-600 dark:text-gray-400">{property?.location?.address}</p>
		</div>

		<!-- Basic Rental Information -->
		<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
			<FormField label={$t('property.rental.monthlyRent')} required error={errors.monthly_rent}>
				<input
					type="number"
					step="0.01"
					min="0"
					bind:value={formData.monthly_rent}
					class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
					placeholder="0.00"
					required
				/>
			</FormField>

			<FormField
				label={$t('property.rental.securityDeposit')}
				required
				error={errors.security_deposit}
			>
				<input
					type="number"
					step="0.01"
					min="0"
					bind:value={formData.security_deposit}
					class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
					placeholder="0.00"
					required
				/>
			</FormField>

			<FormField label={$t('property.rental.rentalType')}>
				<select
					bind:value={formData.rental_type}
					class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
				>
					<option value="monthly">{$t('property.rental.types.monthly')}</option>
					<option value="yearly">{$t('property.rental.types.yearly')}</option>
					<option value="weekly">{$t('property.rental.types.weekly')}</option>
					<option value="daily">{$t('property.rental.types.daily')}</option>
				</select>
			</FormField>

			<FormField
				label={$t('property.rental.managementFee')}
				error={errors.management_fee_percentage}
			>
				<div class="relative">
					<input
						type="number"
						step="0.1"
						min="0"
						max="100"
						bind:value={formData.management_fee_percentage}
						class="block w-full rounded-md border-gray-300 pr-8 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
						placeholder="0.0"
					/>
					<span class="absolute top-1/2 right-3 -translate-y-1/2 text-gray-500">%</span>
				</div>
			</FormField>
		</div>

		<!-- Income Projection -->
		{#if monthlyRentNumber > 0}
			<div
				class="rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-900/20"
			>
				<h4 class="font-medium text-blue-900 dark:text-blue-100">
					{$t('property.rental.incomeProjection')}
				</h4>
				<div class="mt-2 grid grid-cols-2 gap-4 text-sm">
					<div>
						<span class="text-blue-700 dark:text-blue-300"
							>{$t('property.rental.monthlyIncome')}:
						</span>
						<span class="font-semibold text-blue-900 dark:text-blue-100"
							>{formatCurrency(monthlyRentNumber)}</span
						>
					</div>
					<div>
						<span class="text-blue-700 dark:text-blue-300"
							>{$t('property.rental.annualIncome')}:
						</span>
						<span class="font-semibold text-blue-900 dark:text-blue-100"
							>{formatCurrency(annualIncome)}</span
						>
					</div>
				</div>
			</div>
		{/if}

		<!-- Property Features -->
		<div class="space-y-4">
			<h4 class="font-medium text-gray-900 dark:text-white">{$t('property.rental.features')}</h4>

			<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
				<FormField label={$t('property.rental.parkingSpaces')}>
					<input
						type="number"
						min="0"
						bind:value={formData.parking_spaces}
						class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
					/>
				</FormField>

				<FormField label={$t('property.rental.availableFrom')}>
					<input
						type="date"
						bind:value={formData.available_from}
						class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
						required
					/>
				</FormField>
			</div>

			<!-- Boolean Features -->
			<div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
				<label class="flex items-center space-x-2">
					<input
						type="checkbox"
						bind:checked={formData.furnished}
						class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
					/>
					<span class="text-sm text-gray-700 dark:text-gray-300"
						>{$t('property.rental.furnished')}</span
					>
				</label>

				<label class="flex items-center space-x-2">
					<input
						type="checkbox"
						bind:checked={formData.pets_allowed}
						class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
					/>
					<span class="text-sm text-gray-700 dark:text-gray-300"
						>{$t('property.rental.petsAllowed')}</span
					>
				</label>

				<label class="flex items-center space-x-2">
					<input
						type="checkbox"
						bind:checked={formData.smoking_allowed}
						class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
					/>
					<span class="text-sm text-gray-700 dark:text-gray-300"
						>{$t('property.rental.smokingAllowed')}</span
					>
				</label>

				<label class="flex items-center space-x-2">
					<input
						type="checkbox"
						bind:checked={formData.utilities_included}
						class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
					/>
					<span class="text-sm text-gray-700 dark:text-gray-300"
						>{$t('property.rental.utilitiesIncluded')}</span
					>
				</label>
			</div>
		</div>

		<!-- Utilities Details -->
		{#if formData.utilities_included}
			<div class="space-y-4">
				<h4 class="font-medium text-gray-900 dark:text-white">
					{$t('property.rental.utilitiesDetails')}
				</h4>
				<div class="grid grid-cols-2 gap-4 md:grid-cols-3">
					{#each Object.keys(formData.utilities_details) as utility}
						<label class="flex items-center space-x-2">
							<input
								type="checkbox"
								checked={formData.utilities_details[utility]}
								onchange={(e) => handleUtilityChange(utility, e.target.checked)}
								class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
							/>
							<span class="text-sm text-gray-700 dark:text-gray-300">
								{$t(`property.rental.utilities.${utility}`)}
							</span>
						</label>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Lease Terms -->
		<div class="space-y-4">
			<h4 class="font-medium text-gray-900 dark:text-white">{$t('property.rental.leaseTerms')}</h4>
			<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
				<FormField label={$t('property.rental.minimumLease')}>
					<div class="relative">
						<input
							type="number"
							min="1"
							bind:value={formData.minimum_lease_period}
							class="block w-full rounded-md border-gray-300 pr-16 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
						/>
						<span class="absolute top-1/2 right-3 -translate-y-1/2 text-gray-500"
							>{$t('property.rental.months')}</span
						>
					</div>
				</FormField>

				<FormField label={$t('property.rental.maximumLease')}>
					<div class="relative">
						<input
							type="number"
							min="1"
							bind:value={formData.maximum_lease_period}
							class="block w-full rounded-md border-gray-300 pr-16 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
						/>
						<span class="absolute top-1/2 right-3 -translate-y-1/2 text-gray-500"
							>{$t('property.rental.months')}</span
						>
					</div>
				</FormField>
			</div>
		</div>
	</form>

	<!-- Modal Footer -->
	<div slot="footer" class="flex justify-end space-x-3">
		<Button variant="secondary" onclick={onClose}>
			{$t('common.cancel')}
		</Button>
		<Button
			variant="primary"
			disabled={!isFormValid() || isSubmitting}
			loading={isSubmitting}
			onclick={handleSubmit}
		>
			{$t('property.rental.createProperty')}
		</Button>
	</div>
</Modal>
