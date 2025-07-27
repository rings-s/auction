<script>
	import { createEventDispatcher } from 'svelte';
	import { t } from '$lib/i18n';

	const dispatch = createEventDispatcher();

	export let locationData = {
		address: '',
		city: '',
		state: '',
		country: 'المملكة العربية السعودية',
		postal_code: '',
		latitude: null,
		longitude: null
	};
	export let errors = {};

	function handleLocationChange() {
		dispatch('locationChange', { locationData });
	}

	function handleAddressChange(field, value) {
		locationData[field] = value;
		handleLocationChange();
	}

	// City options for Saudi Arabia
	const saudiCities = [
		'الرياض',
		'جدة',
		'مكة المكرمة',
		'المدينة المنورة',
		'الدمام',
		'الخبر',
		'الظهران',
		'تبوك',
		'بريدة',
		'خميس مشيط',
		'حفر الباطن',
		'الطائف',
		'الجبيل',
		'الخرج',
		'ينبع',
		'الأحساء',
		'القطيف',
		'عرعر',
		'سكاكا',
		'جيزان',
		'نجران',
		'الباحة',
		'القنفذة'
	];
</script>

<div class="space-y-6">
	<div>
		<h3 class="mb-4 text-lg font-medium text-gray-900 dark:text-gray-100">
			{$t('property.location')}
		</h3>
		<p class="mb-6 text-sm text-gray-600 dark:text-gray-400">
			{$t('property.locationDescription')}
		</p>
	</div>

	<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
		<!-- Address -->
		<div class="md:col-span-2">
			<label for="address" class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
				{$t('property.address')} *
			</label>
			<input
				id="address"
				type="text"
				bind:value={locationData.address}
				on:input={() => handleAddressChange('address', locationData.address)}
				placeholder={$t('property.addressPlaceholder')}
				class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
					text-gray-900 transition-all duration-200
					focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
					dark:bg-gray-700 dark:text-gray-100
					{errors.address ? 'border-red-500 focus:ring-red-500' : ''}"
				required
			/>
			{#if errors.address}
				<p class="mt-2 text-sm text-red-600 dark:text-red-400">{errors.address}</p>
			{/if}
		</div>

		<!-- City -->
		<div>
			<label for="city" class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
				{$t('property.city')} *
			</label>
			<select
				id="city"
				bind:value={locationData.city}
				on:change={() => handleAddressChange('city', locationData.city)}
				class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
					text-gray-900 transition-all duration-200
					focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
					dark:bg-gray-700 dark:text-gray-100
					{errors.city ? 'border-red-500 focus:ring-red-500' : ''}"
				required
			>
				<option value="">{$t('property.selectCity')}</option>
				{#each saudiCities as city}
					<option value={city}>{city}</option>
				{/each}
			</select>
			{#if errors.city}
				<p class="mt-2 text-sm text-red-600 dark:text-red-400">{errors.city}</p>
			{/if}
		</div>

		<!-- State/Province -->
		<div>
			<label for="state" class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
				{$t('property.state')}
			</label>
			<input
				id="state"
				type="text"
				bind:value={locationData.state}
				on:input={() => handleAddressChange('state', locationData.state)}
				placeholder={$t('property.statePlaceholder')}
				class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
					text-gray-900 transition-all duration-200
					focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
					dark:bg-gray-700 dark:text-gray-100"
			/>
		</div>

		<!-- Country -->
		<div>
			<label for="country" class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
				{$t('property.country')}
			</label>
			<input
				id="country"
				type="text"
				bind:value={locationData.country}
				on:input={() => handleAddressChange('country', locationData.country)}
				class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
					text-gray-900 transition-all duration-200
					focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
					dark:bg-gray-700 dark:text-gray-100"
				readonly
			/>
		</div>

		<!-- Postal Code -->
		<div>
			<label
				for="postal_code"
				class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
			>
				{$t('property.postalCode')}
			</label>
			<input
				id="postal_code"
				type="text"
				bind:value={locationData.postal_code}
				on:input={() => handleAddressChange('postal_code', locationData.postal_code)}
				placeholder="12345"
				pattern="[0-9]{5}"
				class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
					text-gray-900 transition-all duration-200
					focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
					dark:bg-gray-700 dark:text-gray-100"
			/>
		</div>
	</div>

	<!-- Coordinates Section -->
	<div class="border-t border-gray-200 pt-6 dark:border-gray-700">
		<h4 class="text-md mb-4 font-medium text-gray-900 dark:text-gray-100">
			{$t('property.coordinates')} ({$t('property.optional')})
		</h4>

		<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
			<!-- Latitude -->
			<div>
				<label
					for="latitude"
					class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
				>
					{$t('property.latitude')}
				</label>
				<input
					id="latitude"
					type="number"
					step="any"
					bind:value={locationData.latitude}
					on:input={() => handleAddressChange('latitude', locationData.latitude)}
					placeholder="24.7136"
					class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
						text-gray-900 transition-all duration-200
						focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
						dark:bg-gray-700 dark:text-gray-100"
				/>
			</div>

			<!-- Longitude -->
			<div>
				<label
					for="longitude"
					class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
				>
					{$t('property.longitude')}
				</label>
				<input
					id="longitude"
					type="number"
					step="any"
					bind:value={locationData.longitude}
					on:input={() => handleAddressChange('longitude', locationData.longitude)}
					placeholder="46.6753"
					class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3
						text-gray-900 transition-all duration-200
						focus:border-transparent focus:ring-2 focus:ring-blue-500 dark:border-gray-600
						dark:bg-gray-700 dark:text-gray-100"
				/>
			</div>
		</div>

		<div class="mt-4 rounded-lg bg-blue-50 p-4 dark:bg-blue-900/20">
			<div class="flex items-start">
				<svg
					class="mt-0.5 mr-3 h-5 w-5 text-blue-600 dark:text-blue-400"
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
				<div class="text-sm text-blue-700 dark:text-blue-300">
					<p class="mb-1 font-medium">{$t('property.coordinatesHelp')}</p>
					<p>{$t('property.coordinatesDescription')}</p>
				</div>
			</div>
		</div>
	</div>
</div>
