<script>
	import { createEventDispatcher } from 'svelte';
	import { getTranslation } from '$lib/i18n/index.js';
	import { formatCurrency } from '$lib/utils/currency.js';
	import Button from '$lib/components/ui/Button.svelte';

	const dispatch = createEventDispatcher();

	/** @type {Object} */
	export let request;
	/** @type {string} */
	export let variant = 'default'; // 'default', 'compact', 'dashboard'
	/** @type {boolean} */
	export let showActions = true;
	/** @type {boolean} */
	export let loading = false;

	$: t = getTranslation;
	$: property = request?.property;
	$: category = request?.category;
	$: requestedBy = request?.requested_by;
	$: assignedTo = request?.assigned_to;

	function handleViewDetails() {
		dispatch('view', { request });
	}

	function handleEdit() {
		dispatch('edit', { request });
	}

	function handleAssign() {
		dispatch('assign', { request });
	}

	function handleComplete() {
		dispatch('complete', { request });
	}

	function handleViewProperty() {
		dispatch('viewProperty', { request, property });
	}

	function getPriorityBadgeClass(priority) {
		switch (priority) {
			case 'low':
				return 'bg-green-100 text-green-800 border-green-200';
			case 'medium':
				return 'bg-yellow-100 text-yellow-800 border-yellow-200';
			case 'high':
				return 'bg-orange-100 text-orange-800 border-orange-200';
			case 'urgent':
				return 'bg-red-100 text-red-800 border-red-200';
			default:
				return 'bg-gray-100 text-gray-800 border-gray-200';
		}
	}

	function getStatusBadgeClass(status) {
		switch (status) {
			case 'pending':
				return 'bg-yellow-100 text-yellow-800 border-yellow-200';
			case 'in_progress':
				return 'bg-blue-100 text-blue-800 border-blue-200';
			case 'completed':
				return 'bg-green-100 text-green-800 border-green-200';
			case 'cancelled':
				return 'bg-red-100 text-red-800 border-red-200';
			case 'on_hold':
				return 'bg-gray-100 text-gray-800 border-gray-200';
			default:
				return 'bg-gray-100 text-gray-800 border-gray-200';
		}
	}

	function getCategoryIcon(categoryName) {
		const iconMap = {
			plumbing: '🔧',
			electrical: '⚡',
			hvac: '❄️',
			appliances: '🏠',
			structural: '🏗️',
			painting: '🎨',
			flooring: '🪟',
			exterior: '🌿',
			security: '🔒',
			cleaning: '🧹',
			other: '🔨'
		};
		return iconMap[categoryName?.toLowerCase()] || '🔨';
	}

	function formatDateAgo(dateString) {
		if (!dateString) return '';
		const date = new Date(dateString);
		const now = new Date();
		const diffTime = Math.abs(now - date);
		const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

		if (diffDays === 0) {
			const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
			if (diffHours === 0) {
				const diffMinutes = Math.floor(diffTime / (1000 * 60));
				return diffMinutes <= 1
					? $t('common.justNow')
					: $t('common.minutesAgo', { count: diffMinutes });
			}
			return diffHours === 1 ? $t('common.hourAgo') : $t('common.hoursAgo', { count: diffHours });
		} else if (diffDays === 1) {
			return $t('common.yesterday');
		} else if (diffDays < 7) {
			return $t('common.daysAgo', { count: diffDays });
		} else {
			return date.toLocaleDateString();
		}
	}

	function getInitials(firstName, lastName) {
		return `${firstName?.charAt(0) || ''}${lastName?.charAt(0) || ''}`.toUpperCase();
	}
</script>

<div
	class="rounded-lg border border-gray-200 bg-white shadow-sm transition-all duration-200 hover:border-gray-300 hover:shadow-md"
>
	<div class="p-4">
		<!-- Header with Priority and Status -->
		<div class="mb-3 flex items-start justify-between">
			<div class="flex items-center gap-2">
				<!-- Category Icon -->
				<span class="text-2xl">{getCategoryIcon(category?.name)}</span>

				<!-- Priority Badge -->
				<span
					class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium {getPriorityBadgeClass(
						request.priority
					)}"
				>
					{$t(`maintenance.priority.${request.priority}`)}
				</span>
			</div>

			<!-- Status Badge -->
			<span
				class="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium {getStatusBadgeClass(
					request.status
				)}"
			>
				{$t(`maintenance.status.${request.status}`)}
			</span>
		</div>

		<!-- Request Title and Description -->
		<div class="mb-3">
			<h3 class="mb-1 line-clamp-1 text-lg font-semibold text-gray-900">
				{request.title || $t('maintenance.untitledRequest')}
			</h3>
			{#if request.description}
				<p class="line-clamp-2 text-sm text-gray-600">
					{request.description}
				</p>
			{/if}
		</div>

		<!-- Property Information -->
		{#if property}
			<div class="mb-3 rounded-lg bg-gray-50 p-3">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-900">{property.title}</p>
						<p class="text-xs text-gray-600">📍 {property.address}</p>
					</div>
					<Button variant="ghost" size="sm" on:click={handleViewProperty}>
						{$t('property.view')}
					</Button>
				</div>
			</div>
		{/if}

		<!-- Request Details Grid -->
		<div class="mb-4 grid grid-cols-2 gap-3 text-sm">
			<!-- Category -->
			<div>
				<p class="text-gray-600">{$t('maintenance.category')}</p>
				<p class="font-medium">{category?.name || $t('common.uncategorized')}</p>
			</div>

			<!-- Reported Date -->
			<div>
				<p class="text-gray-600">{$t('maintenance.reportedDate')}</p>
				<p class="font-medium">{formatDateAgo(request.reported_date)}</p>
			</div>

			<!-- Estimated Cost -->
			{#if request.estimated_cost}
				<div>
					<p class="text-gray-600">{$t('maintenance.estimatedCost')}</p>
					<p class="font-medium">{formatCurrency(request.estimated_cost)}</p>
				</div>
			{/if}

			<!-- Actual Cost -->
			{#if request.actual_cost}
				<div>
					<p class="text-gray-600">{$t('maintenance.actualCost')}</p>
					<p class="font-medium text-green-600">{formatCurrency(request.actual_cost)}</p>
				</div>
			{/if}
		</div>

		<!-- People Involved -->
		<div class="mb-4 flex items-center gap-4 text-sm">
			<!-- Requested By -->
			{#if requestedBy}
				<div class="flex items-center gap-2">
					<div
						class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-xs font-semibold text-white"
					>
						{getInitials(requestedBy.first_name, requestedBy.last_name)}
					</div>
					<div>
						<p class="text-gray-600">{$t('maintenance.requestedBy')}</p>
						<p class="font-medium">{requestedBy.first_name} {requestedBy.last_name}</p>
					</div>
				</div>
			{/if}

			<!-- Assigned To -->
			{#if assignedTo}
				<div class="flex items-center gap-2">
					<div
						class="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-green-500 to-teal-600 text-xs font-semibold text-white"
					>
						{getInitials(assignedTo.first_name, assignedTo.last_name)}
					</div>
					<div>
						<p class="text-gray-600">{$t('maintenance.assignedTo')}</p>
						<p class="font-medium">{assignedTo.first_name} {assignedTo.last_name}</p>
					</div>
				</div>
			{:else}
				<div class="rounded bg-orange-50 px-2 py-1 text-xs text-orange-600">
					{$t('maintenance.unassigned')}
				</div>
			{/if}
		</div>

		<!-- Emergency Badge -->
		{#if request.is_emergency}
			<div class="mb-4 rounded-lg border border-red-200 bg-red-50 p-2">
				<div class="flex items-center gap-2">
					<span class="text-red-600">🚨</span>
					<span class="text-sm font-medium text-red-800">{$t('maintenance.emergencyRequest')}</span>
				</div>
			</div>
		{/if}

		<!-- Notes -->
		{#if request.notes && request.notes.trim()}
			<div class="mb-4 rounded border-l-4 border-yellow-400 bg-yellow-50 p-2">
				<p class="text-sm text-yellow-800">
					<strong>{$t('common.notes')}:</strong>
					{request.notes}
				</p>
			</div>
		{/if}

		<!-- Completion Date -->
		{#if request.status === 'completed' && request.completed_date}
			<div class="mb-4 rounded border-l-4 border-green-400 bg-green-50 p-2">
				<p class="text-sm text-green-800">
					<strong>{$t('maintenance.completedOn')}:</strong>
					{new Date(request.completed_date).toLocaleDateString()}
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

				{#if request.status !== 'completed' && request.status !== 'cancelled'}
					{#if !assignedTo}
						<Button variant="ghost" size="sm" on:click={handleAssign}>
							👷 {$t('maintenance.assign')}
						</Button>
					{/if}

					{#if request.status === 'in_progress'}
						<Button variant="success" size="sm" on:click={handleComplete}>
							✅ {$t('maintenance.markComplete')}
						</Button>
					{/if}
				{/if}
			</div>
		{/if}
	</div>
</div>

<style>
	.line-clamp-1 {
		display: -webkit-box;
		-webkit-line-clamp: 1;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
</style>
