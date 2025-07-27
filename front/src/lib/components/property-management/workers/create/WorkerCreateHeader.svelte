<!-- src/lib/components/property-management/workers/create/WorkerCreateHeader.svelte -->
<script>
	import { t, locale } from '$lib/i18n';

	let { currentStep, totalSteps, loading } = $props();
	let isRTL = $derived($locale === 'ar');

	// Calculate progress percentage
	let progress = $derived((currentStep / totalSteps) * 100);

	// Step titles
	let stepTitles = $derived([
		$t('worker.create.personalInfo'),
		$t('worker.create.employmentDetails'),
		$t('worker.create.skillsCategories'),
		$t('worker.create.documentsReview')
	]);

	// Get step status
	function getStepStatus(stepNumber) {
		if (stepNumber < currentStep) return 'completed';
		if (stepNumber === currentStep) return 'current';
		return 'upcoming';
	}

	// Get step icon
	function getStepIcon(stepNumber) {
		const status = getStepStatus(stepNumber);
		if (status === 'completed') {
			return `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
				<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
			</svg>`;
		}
		return stepNumber.toString();
	}
</script>

<div
	class="overflow-hidden rounded-t-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
	dir={isRTL ? 'rtl' : 'ltr'}
>
	<!-- Gradient Header -->
	<div class="bg-gradient-to-r from-orange-500 via-amber-500 to-yellow-600 p-8">
		<div class="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
			<div class="flex-1">
				<div class="mb-3 flex items-center">
					<div class="mr-3 rounded-full bg-white/20 p-2">
						<svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
							/>
						</svg>
					</div>
					<span
						class="inline-flex items-center rounded-full bg-white/20 px-3 py-1 text-sm font-medium text-white"
					>
						{$t('worker.title')}
					</span>
				</div>
				<h1 class="mb-2 text-3xl font-bold text-white lg:text-4xl">
					{$t('worker.create')}
				</h1>
				<p class="text-lg text-white/90">
					{$t('worker.createSubtitle')}
				</p>
			</div>

			<!-- Progress Circle -->
			<div class="flex flex-col items-center lg:items-end">
				<div class="relative mb-3 h-20 w-20">
					<svg class="h-20 w-20 -rotate-90 transform" viewBox="0 0 36 36">
						<circle
							cx="18"
							cy="18"
							r="15.915"
							fill="transparent"
							stroke="rgba(255,255,255,0.2)"
							stroke-width="2"
						/>
						<circle
							cx="18"
							cy="18"
							r="15.915"
							fill="transparent"
							stroke="white"
							stroke-width="2"
							stroke-dasharray="{progress} 100"
							stroke-linecap="round"
							class="transition-all duration-500 ease-out"
						/>
					</svg>
					<div class="absolute inset-0 flex items-center justify-center">
						<span class="text-sm font-bold text-white">
							{currentStep}/{totalSteps}
						</span>
					</div>
				</div>
				<p class="text-sm font-medium text-white/80">
					{Math.round(progress)}% {$t('common.complete')}
				</p>
			</div>
		</div>
	</div>

	<!-- Step Navigation -->
	<div class="border-b border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
		<nav class="flex justify-between">
			{#each Array(totalSteps) as _, index}
				{@const stepNumber = index + 1}
				{@const status = getStepStatus(stepNumber)}
				<div class="relative flex flex-1 flex-col items-center">
					<!-- Step Circle -->
					<div
						class="mb-2 flex h-10 w-10 items-center justify-center rounded-full text-sm font-medium transition-all duration-300
							{status === 'completed'
							? 'bg-gradient-to-r from-orange-500 to-amber-500 text-white shadow-lg'
							: status === 'current'
								? 'bg-gradient-to-r from-amber-500 to-yellow-500 text-white shadow-lg ring-4 ring-amber-200 dark:ring-amber-800'
								: 'bg-gray-200 text-gray-500 dark:bg-gray-600 dark:text-gray-400'}
							{loading && status === 'current' ? 'animate-pulse' : ''}"
					>
						{#if status === 'completed'}
							{@html getStepIcon(stepNumber)}
						{:else}
							{stepNumber}
						{/if}
					</div>

					<!-- Step Title -->
					<span
						class="px-2 text-center text-xs font-medium transition-colors duration-300
							{status === 'current'
							? 'text-amber-600 dark:text-amber-400'
							: status === 'completed'
								? 'text-orange-600 dark:text-orange-400'
								: 'text-gray-500 dark:text-gray-400'}"
					>
						{stepTitles[index]}
					</span>

					<!-- Connector Line -->
					{#if index < totalSteps - 1}
						<div
							class="absolute top-5 {isRTL
								? 'right-0'
								: 'left-0'} z-0 h-0.5 w-full transition-colors duration-300"
							style="margin-{isRTL ? 'right' : 'left'}: 50%; width: calc(100% - 2.5rem);"
						>
							<div
								class="h-full transition-all duration-500 ease-out
									{stepNumber < currentStep
									? 'bg-gradient-to-r from-orange-500 to-amber-500'
									: 'bg-gray-200 dark:bg-gray-600'}"
							></div>
						</div>
					{/if}
				</div>
			{/each}
		</nav>
	</div>

	<!-- Current Step Indicator -->
	<div
		class="bg-gradient-to-r from-orange-50 to-amber-50 p-4 dark:from-orange-900/20 dark:to-amber-900/20"
	>
		<div class="flex items-center justify-center">
			<div class="flex items-center space-x-3 text-sm">
				<div class="flex items-center">
					<svg class="mr-1 h-4 w-4 text-amber-500" fill="currentColor" viewBox="0 0 20 20">
						<path
							fill-rule="evenodd"
							d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
							clip-rule="evenodd"
						/>
					</svg>
					<span class="font-medium text-gray-700 dark:text-gray-300">
						{$t('worker.create.currentStep')}:
					</span>
				</div>
				<span class="font-semibold text-amber-600 dark:text-amber-400">
					{stepTitles[currentStep - 1]}
				</span>
			</div>
		</div>
	</div>
</div>

<style>
	/* Enhanced animations for step transitions */
	@keyframes step-pulse {
		0%,
		100% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.05);
		}
	}

	.animate-pulse {
		animation: step-pulse 2s ease-in-out infinite;
	}

	/* Gradient text animation */
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
		animation: gradient-shift 6s ease infinite;
	}

	/* Smooth transitions for all elements */
	* {
		transition: all 0.3s ease;
	}
</style>
