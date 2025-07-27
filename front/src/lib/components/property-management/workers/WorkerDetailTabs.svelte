<script>
	import { t } from '$lib/i18n';
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	export let worker = null;
	export let workHistory = [];
	export let loading = false;

	let activeTab = 'overview';

	function handleTabChange(tab) {
		activeTab = tab;
		dispatch('tabChange', { tab });
	}

	function formatDate(dateString) {
		if (!dateString) return '-';
		return new Date(dateString).toLocaleDateString();
	}

	function formatCurrency(amount) {
		if (!amount) return '0 SAR';
		return `${amount.toLocaleString()} SAR`;
	}
</script>

{#if loading}
	<div class="animate-pulse space-y-4">
		<div class="h-10 rounded bg-gray-200 dark:bg-gray-700"></div>
		<div class="h-64 rounded bg-gray-200 dark:bg-gray-700"></div>
	</div>
{:else if worker}
	<!-- Tab Navigation -->
	<div class="border-b border-gray-200 dark:border-gray-700">
		<nav class="flex space-x-8">
			<button
				class="border-b-2 px-1 py-4 text-sm font-medium transition-colors duration-200 {activeTab ===
				'overview'
					? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
					: 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}"
				on:click={() => handleTabChange('overview')}
			>
				{$t('worker.overview')}
			</button>

			<button
				class="border-b-2 px-1 py-4 text-sm font-medium transition-colors duration-200 {activeTab ===
				'work-history'
					? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
					: 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}"
				on:click={() => handleTabChange('work-history')}
			>
				{$t('worker.workHistory')}
			</button>

			<button
				class="border-b-2 px-1 py-4 text-sm font-medium transition-colors duration-200 {activeTab ===
				'performance'
					? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
					: 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}"
				on:click={() => handleTabChange('performance')}
			>
				{$t('worker.performance')}
			</button>
		</nav>
	</div>

	<!-- Tab Content -->
	<div class="mt-6">
		{#if activeTab === 'overview'}
			<div class="grid grid-cols-1 gap-8 lg:grid-cols-2">
				<!-- Personal Information -->
				<div
					class="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800"
				>
					<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
						{$t('worker.personalInfo')}
					</h3>
					<dl class="space-y-3">
						<div>
							<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
								{$t('worker.name')}
							</dt>
							<dd class="text-sm text-gray-900 dark:text-gray-100">{worker.name || '-'}</dd>
						</div>
						<div>
							<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
								{$t('worker.email')}
							</dt>
							<dd class="text-sm text-gray-900 dark:text-gray-100">{worker.email || '-'}</dd>
						</div>
						<div>
							<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
								{$t('worker.phone')}
							</dt>
							<dd class="text-sm text-gray-900 dark:text-gray-100">{worker.phone || '-'}</dd>
						</div>
						<div>
							<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
								{$t('worker.category')}
							</dt>
							<dd class="text-sm text-gray-900 dark:text-gray-100">{worker.category || '-'}</dd>
						</div>
						<div>
							<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
								{$t('worker.status')}
							</dt>
							<dd class="text-sm">
								<span
									class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium
									{worker.is_active
										? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
										: 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'}"
								>
									{worker.is_active ? $t('worker.active') : $t('worker.inactive')}
								</span>
							</dd>
						</div>
					</dl>
				</div>

				<!-- Professional Information -->
				<div
					class="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800"
				>
					<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
						{$t('worker.professionalInfo')}
					</h3>
					<dl class="space-y-3">
						<div>
							<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
								{$t('worker.experience')}
							</dt>
							<dd class="text-sm text-gray-900 dark:text-gray-100">
								{worker.experience_years || 0}
								{$t('worker.years')}
							</dd>
						</div>
						<div>
							<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
								{$t('worker.hourlyRate')}
							</dt>
							<dd class="text-sm text-gray-900 dark:text-gray-100">
								{formatCurrency(worker.hourly_rate)}
							</dd>
						</div>
						<div>
							<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
								{$t('worker.rating')}
							</dt>
							<dd class="text-sm text-gray-900 dark:text-gray-100">
								{#if worker.rating}
									<div class="flex items-center">
										<span class="text-yellow-400">★</span>
										<span class="ml-1">{worker.rating}/5</span>
									</div>
								{:else}
									{$t('worker.noRating')}
								{/if}
							</dd>
						</div>
						{#if worker.specializations?.length}
							<div>
								<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
									{$t('worker.specializations')}
								</dt>
								<dd class="text-sm text-gray-900 dark:text-gray-100">
									<div class="mt-1 flex flex-wrap gap-1">
										{#each worker.specializations as specialization}
											<span
												class="inline-flex items-center rounded-md bg-blue-100 px-2 py-1 text-xs font-medium text-blue-800 dark:bg-blue-800 dark:text-blue-100"
											>
												{specialization}
											</span>
										{/each}
									</div>
								</dd>
							</div>
						{/if}
					</dl>
				</div>
			</div>
		{:else if activeTab === 'work-history'}
			<div class="rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
				{#if workHistory?.length}
					<div class="divide-y divide-gray-200 dark:divide-gray-700">
						{#each workHistory as work}
							<div class="p-6">
								<div class="flex items-start justify-between">
									<div>
										<h4 class="text-lg font-medium text-gray-900 dark:text-gray-100">
											{work.title || work.description}
										</h4>
										<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
											{work.property?.name || '-'}
										</p>
										<p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
											{formatDate(work.start_date)} - {formatDate(work.end_date)}
										</p>
									</div>
									<div class="text-right">
										<p class="text-lg font-semibold text-gray-900 dark:text-gray-100">
											{formatCurrency(work.cost)}
										</p>
										<span
											class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium
											{work.status === 'completed'
												? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
												: work.status === 'in-progress'
													? 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100'
													: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100'}"
										>
											{$t(`maintenance.status.${work.status}`)}
										</span>
									</div>
								</div>
							</div>
						{/each}
					</div>
				{:else}
					<div class="p-8 text-center">
						<div class="mb-4 text-4xl">📋</div>
						<h3 class="mb-2 text-lg font-medium text-gray-900 dark:text-gray-100">
							{$t('worker.noWorkHistory')}
						</h3>
						<p class="text-gray-600 dark:text-gray-400">
							{$t('worker.noWorkHistoryDesc')}
						</p>
					</div>
				{/if}
			</div>
		{:else if activeTab === 'performance'}
			<div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
				<!-- Performance Metrics -->
				<div
					class="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800"
				>
					<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
						{$t('worker.performanceMetrics')}
					</h3>
					<div class="space-y-4">
						<div>
							<div class="mb-1 flex items-center justify-between">
								<span class="text-sm font-medium text-gray-700 dark:text-gray-300"
									>{$t('worker.completionRate')}</span
								>
								<span class="text-sm text-gray-600 dark:text-gray-400">85%</span>
							</div>
							<div class="h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
								<div class="h-2 rounded-full bg-green-500" style="width: 85%"></div>
							</div>
						</div>
						<div>
							<div class="mb-1 flex items-center justify-between">
								<span class="text-sm font-medium text-gray-700 dark:text-gray-300"
									>{$t('worker.onTimeDelivery')}</span
								>
								<span class="text-sm text-gray-600 dark:text-gray-400">92%</span>
							</div>
							<div class="h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
								<div class="h-2 rounded-full bg-blue-500" style="width: 92%"></div>
							</div>
						</div>
						<div>
							<div class="mb-1 flex items-center justify-between">
								<span class="text-sm font-medium text-gray-700 dark:text-gray-300"
									>{$t('worker.qualityScore')}</span
								>
								<span class="text-sm text-gray-600 dark:text-gray-400">4.2/5</span>
							</div>
							<div class="h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
								<div class="h-2 rounded-full bg-yellow-500" style="width: 84%"></div>
							</div>
						</div>
					</div>
				</div>

				<!-- Recent Reviews -->
				<div
					class="rounded-lg border border-gray-200 bg-white p-6 lg:col-span-2 dark:border-gray-700 dark:bg-gray-800"
				>
					<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
						{$t('worker.recentReviews')}
					</h3>
					<div class="space-y-4">
						<div class="border-b border-gray-200 pb-4 dark:border-gray-700">
							<div class="mb-2 flex items-center">
								<div class="flex text-yellow-400">
									<span>★★★★★</span>
								</div>
								<span class="ml-2 text-sm text-gray-600 dark:text-gray-400">
									{formatDate('2024-01-15')}
								</span>
							</div>
							<p class="text-sm text-gray-900 dark:text-gray-100">
								{$t('worker.sampleReview1')}
							</p>
						</div>
						<div class="border-b border-gray-200 pb-4 dark:border-gray-700">
							<div class="mb-2 flex items-center">
								<div class="flex text-yellow-400">
									<span>★★★★☆</span>
								</div>
								<span class="ml-2 text-sm text-gray-600 dark:text-gray-400">
									{formatDate('2024-01-10')}
								</span>
							</div>
							<p class="text-sm text-gray-900 dark:text-gray-100">
								{$t('worker.sampleReview2')}
							</p>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
{:else}
	<div class="py-8 text-center">
		<p class="text-gray-500 dark:text-gray-400">{$t('worker.workerNotFound')}</p>
	</div>
{/if}
