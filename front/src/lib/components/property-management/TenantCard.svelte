<script>
	import { createEventDispatcher } from 'svelte';
	import { t } from '$lib/i18n';
	import { formatCurrency } from '$lib/utils/currency.js';
	import Button from '$lib/components/ui/Button.svelte';

	const dispatch = createEventDispatcher();

	/** @type {Object} */
	export let tenant;
	/** @type {string} */
	export let variant = 'default'; // 'default', 'compact', 'dashboard'
	/** @type {boolean} */
	export let showActions = true;
	/** @type {boolean} */
	export let loading = false;

	$: user = tenant?.user;
	$: activeLease = tenant?.active_lease;
	$: status = tenant?.status || 'active';

	function handleViewDetails() {
		dispatch('view', { tenant });
	}

	function handleEdit() {
		dispatch('edit', { tenant });
	}

	function handleViewLeases() {
		dispatch('viewLeases', { tenant });
	}

	function handleContact() {
		dispatch('contact', { tenant });
	}

	function handleViewPayments() {
		dispatch('viewPayments', { tenant });
	}

	function getStatusBadgeClass(status) {
		switch (status) {
			case 'active':
				return 'bg-green-100 text-green-800 border-green-200';
			case 'inactive':
				return 'bg-gray-100 text-gray-800 border-gray-200';
			case 'suspended':
				return 'bg-red-100 text-red-800 border-red-200';
			case 'pending':
				return 'bg-yellow-100 text-yellow-800 border-yellow-200';
			default:
				return 'bg-gray-100 text-gray-800 border-gray-200';
		}
	}

	function formatPhoneNumber(phone) {
		if (!phone) return '';
		// Format phone number for display
		return phone.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3');
	}

	function getInitials(firstName, lastName) {
		return `${firstName?.charAt(0) || ''}${lastName?.charAt(0) || ''}`.toUpperCase();
	}

	function calculateDaysRemaining(leaseEndDate) {
		if (!leaseEndDate) return null;
		const today = new Date();
		const endDate = new Date(leaseEndDate);
		const diffTime = endDate - today;
		const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
		return diffDays;
	}

	$: daysRemaining = activeLease ? calculateDaysRemaining(activeLease.end_date) : null;
</script>

<div
	class="rounded-lg border border-gray-200 bg-white shadow-sm transition-all duration-200 hover:border-gray-300 hover:shadow-md"
>
	<div class="p-4">
		<!-- Header with Avatar and Status -->
		<div class="mb-4 flex items-start justify-between">
			<div class="flex items-center gap-3">
				<!-- Avatar -->
				<div class="relative">
					{#if user?.avatar}
						<img
							src={user.avatar}
							alt="{user.first_name} {user.last_name}"
							class="h-12 w-12 rounded-full object-cover"
						/>
					{:else}
						<div
							class="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 font-semibold text-white"
						>
							{getInitials(user?.first_name, user?.last_name)}
						</div>
					{/if}

					<!-- Online Status Indicator (if available) -->
					<div
						class="absolute -right-1 -bottom-1 h-4 w-4 rounded-full border-2 border-white bg-green-400"
					></div>
				</div>

				<!-- Name and Basic Info -->
				<div>
					<h3 class="text-lg font-semibold text-gray-900">
						{user?.first_name || ''}
						{user?.last_name || ''}
					</h3>
					<p class="text-sm text-gray-600">
						{user?.email || ''}
					</p>
					{#if user?.phone_number}
						<p class="text-sm text-gray-500">
							📞 {formatPhoneNumber(user.phone_number)}
						</p>
					{/if}
				</div>
			</div>

			<!-- Status Badge -->
			<span
				class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium {getStatusBadgeClass(
					status
				)}"
			>
				{$t(`tenant.status.${status}`)}
			</span>
		</div>

		<!-- Tenant Details -->
		<div class="mb-4 space-y-3">
			<!-- Current Lease Info -->
			{#if activeLease}
				<div class="rounded-lg bg-blue-50 p-3">
					<div class="mb-2 flex items-center justify-between">
						<h4 class="text-sm font-medium text-blue-900">{$t('tenant.currentLease')}</h4>
						{#if daysRemaining !== null}
							<span class="text-xs text-blue-700">
								{#if daysRemaining > 0}
									{daysRemaining} {$t('common.daysRemaining')}
								{:else if daysRemaining === 0}
									{$t('lease.expiresToday')}
								{:else}
									{$t('lease.expired')} {Math.abs(daysRemaining)} {$t('common.daysAgo')}
								{/if}
							</span>
						{/if}
					</div>

					<div class="grid grid-cols-2 gap-2 text-sm">
						<div>
							<p class="font-medium text-blue-700">{$t('lease.property')}</p>
							<p class="truncate text-blue-800">{activeLease.property?.title || ''}</p>
						</div>
						<div>
							<p class="font-medium text-blue-700">{$t('lease.monthlyRent')}</p>
							<p class="font-bold text-blue-800">{formatCurrency(activeLease.monthly_rent || 0)}</p>
						</div>
					</div>
				</div>
			{:else}
				<div class="rounded-lg bg-gray-50 p-3 text-center">
					<p class="text-sm text-gray-600">{$t('tenant.noActiveLease')}</p>
				</div>
			{/if}

			<!-- Additional Tenant Info -->
			<div class="grid grid-cols-2 gap-3 text-sm">
				{#if tenant.move_in_date}
					<div>
						<p class="text-gray-600">{$t('tenant.moveInDate')}</p>
						<p class="font-medium">{new Date(tenant.move_in_date).toLocaleDateString()}</p>
					</div>
				{/if}

				{#if tenant.emergency_contact_name}
					<div>
						<p class="text-gray-600">{$t('tenant.emergencyContact')}</p>
						<p class="truncate font-medium">{tenant.emergency_contact_name}</p>
					</div>
				{/if}

				{#if tenant.national_id}
					<div>
						<p class="text-gray-600">{$t('tenant.nationalId')}</p>
						<p class="font-medium">****{tenant.national_id.slice(-4)}</p>
					</div>
				{/if}

				{#if tenant.credit_score}
					<div>
						<p class="text-gray-600">{$t('tenant.creditScore')}</p>
						<p class="font-medium">{tenant.credit_score}/850</p>
					</div>
				{/if}
			</div>
		</div>

		<!-- Notes (if any) -->
		{#if tenant.notes && tenant.notes.trim()}
			<div class="mb-4 rounded border-l-4 border-yellow-400 bg-yellow-50 p-2">
				<p class="text-sm text-yellow-800">
					<strong>{$t('common.notes')}:</strong>
					{tenant.notes}
				</p>
			</div>
		{/if}

		<!-- Action Buttons -->
		{#if showActions}
			<div class="flex flex-wrap gap-2">
				<Button variant="primary" size="sm" {loading} on:click={handleViewDetails}>
					{$t('common.viewDetails')}
				</Button>

				<Button variant="outline" size="sm" on:click={handleEdit}>
					{$t('common.edit')}
				</Button>

				<Button variant="ghost" size="sm" on:click={handleContact}>
					📧 {$t('common.contact')}
				</Button>

				<Button variant="ghost" size="sm" on:click={handleViewLeases}>
					📄 {$t('tenant.leases')}
				</Button>

				<Button variant="ghost" size="sm" on:click={handleViewPayments}>
					💰 {$t('tenant.payments')}
				</Button>
			</div>
		{/if}
	</div>
</div>
