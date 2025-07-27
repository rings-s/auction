<!-- src/lib/components/ui/StepIndicator.svelte -->
<script>
	import { t } from '$lib/i18n';

	// Props
	export let steps = [];
	export let currentStep = 0;
	export let completedSteps = [];
	export let errorSteps = [];
	export let variant = 'horizontal'; // 'horizontal' | 'vertical'
	export let showLabels = true;
	export let showDescription = false;
	export let size = 'medium'; // 'small' | 'medium' | 'large'

	// Reactive values
	$: totalSteps = steps.length;

	function getStepStatus(index) {
		if (completedSteps.includes(index)) return 'completed';
		if (errorSteps.includes(index)) return 'error';
		if (index === currentStep) return 'current';
		if (index < currentStep) return 'completed';
		return 'upcoming';
	}

	function getStepNumber(index) {
		const status = getStepStatus(index);
		if (status === 'completed') {
			return '<svg class="w-full h-full" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>';
		}
		if (status === 'error') {
			return '<svg class="w-full h-full" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>';
		}
		return index + 1;
	}

	function getStepClasses(index) {
		const status = getStepStatus(index);
		const baseClasses = 'flex items-center justify-center rounded-full font-semibold';
		
		const sizeClasses = {
			small: 'w-6 h-6 text-xs',
			medium: 'w-8 h-8 text-sm',
			large: 'w-10 h-10 text-base'
		};

		const statusClasses = {
			completed: 'bg-green-600 text-white',
			current: 'bg-primary-600 text-white ring-2 ring-primary-600 ring-offset-2 ring-offset-white',
			error: 'bg-red-600 text-white',
			upcoming: 'bg-gray-200 text-gray-500 dark:bg-gray-700 dark:text-gray-400'
		};

		return `${baseClasses} ${sizeClasses[size]} ${statusClasses[status]}`;
	}

	function getConnectorClasses(index) {
		const status = getStepStatus(index);
		const nextStatus = index < totalSteps - 1 ? getStepStatus(index + 1) : 'upcoming';
		
		if (status === 'completed' || status === 'current') {
			return 'bg-primary-600';
		}
		
		return 'bg-gray-200 dark:bg-gray-700';
	}
</script>

{#if variant === 'horizontal'}
	<!-- Horizontal Step Indicator -->
	<nav aria-label="Progress" class="flex items-center justify-center">
		<ol role="list" class="flex items-center space-x-4">
			{#each steps as step, index}
				<li class="flex items-center">
					<!-- Step Circle -->
					<div class="relative flex items-center">
						<div class={getStepClasses(index)}>
							{@html getStepNumber(index)}
						</div>
						
						{#if showLabels}
							<div class="absolute top-full mt-2 min-w-max">
								<div class="text-center">
									<p class="text-sm font-medium text-gray-900 dark:text-gray-100">
										{step.label}
									</p>
									{#if showDescription && step.description}
										<p class="text-xs text-gray-500 dark:text-gray-400">
											{step.description}
										</p>
									{/if}
								</div>
							</div>
						{/if}
					</div>

					<!-- Connector Line -->
					{#if index < totalSteps - 1}
						<div class="flex-1 h-0.5 mx-4 {getConnectorClasses(index)}"></div>
					{/if}
				</li>
			{/each}
		</ol>
	</nav>
{:else}
	<!-- Vertical Step Indicator -->
	<nav aria-label="Progress">
		<ol role="list" class="space-y-6">
			{#each steps as step, index}
				<li class="flex items-start">
					<!-- Step Circle -->
					<div class="flex-shrink-0 relative">
						<div class={getStepClasses(index)}>
							{@html getStepNumber(index)}
						</div>
						
						<!-- Connector Line -->
						{#if index < totalSteps - 1}
							<div class="absolute top-8 left-1/2 transform -translate-x-1/2 w-0.5 h-6 {getConnectorClasses(index)}"></div>
						{/if}
					</div>

					{#if showLabels}
						<div class="ml-4 min-w-0 flex-1">
							<p class="text-sm font-medium text-gray-900 dark:text-gray-100">
								{step.label}
							</p>
							{#if showDescription && step.description}
								<p class="text-sm text-gray-500 dark:text-gray-400">
									{step.description}
								</p>
							{/if}
						</div>
					{/if}
				</li>
			{/each}
		</ol>
	</nav>
{/if}

<style>
	/* Ensure proper spacing for mobile */
	@media (max-width: 640px) {
		nav ol {
			gap: 0.5rem;
		}
		
		.absolute.top-full {
			position: static;
			transform: none;
			margin-top: 0.5rem;
		}
	}
</style>