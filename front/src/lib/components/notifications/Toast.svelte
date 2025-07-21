<script>
	import { t } from '$lib/i18n';
	import Button from '$lib/components/ui/Button.svelte';

	/** @type {Object} */
	let toast = $props();

	// Event handlers
	let onremove = $props();


	let toastElement = $state();
	let isVisible = $state(false);
	let isRemoving = $state(false);
	let progressWidth = $state(100);
	let progressInterval = $state();

	const typeConfig = {
		success: {
			icon: '✅',
			iconClass: 'text-green-600',
			bgClass: 'bg-green-50 border-green-200',
			progressClass: 'bg-green-500'
		},
		error: {
			icon: '❌',
			iconClass: 'text-red-600',
			bgClass: 'bg-red-50 border-red-200',
			progressClass: 'bg-red-500'
		},
		warning: {
			icon: '⚠️',
			iconClass: 'text-yellow-600',
			bgClass: 'bg-yellow-50 border-yellow-200',
			progressClass: 'bg-yellow-500'
		},
		info: {
			icon: 'ℹ️',
			iconClass: 'text-blue-600',
			bgClass: 'bg-blue-50 border-blue-200',
			progressClass: 'bg-blue-500'
		}
	};

	let config = $derived(typeConfig[toast.type] || typeConfig.info);
	let duration = $derived(toast.duration || 5000);
	let isPersistent = $derived(toast.persistent);

	$effect(() => {
		// Animate in
		requestAnimationFrame(() => {
			isVisible = true;
		});

		// Start progress bar if not persistent
		if (!isPersistent && duration > 0) {
			startProgress();

			// Auto remove after duration
			setTimeout(() => {
				handleRemove();
			}, duration);
		}

		return () => {
			if (progressInterval) {
				clearInterval(progressInterval);
			}
		};
	});

	function startProgress() {
		const interval = 50; // Update every 50ms
		const step = (interval / duration) * 100;

		progressInterval = setInterval(() => {
			progressWidth -= step;
			if (progressWidth <= 0) {
				progressWidth = 0;
				clearInterval(progressInterval);
			}
		}, interval);
	}

	function pauseProgress() {
		if (progressInterval) {
			clearInterval(progressInterval);
		}
	}

	function resumeProgress() {
		if (!isPersistent && progressWidth > 0) {
			startProgress();
		}
	}

	function handleRemove() {
		if (isRemoving) return;

		isRemoving = true;
		isVisible = false;

		// Wait for exit animation to complete
		setTimeout(() => {
			onremove?.();
		}, 300);
	}

	function handleAction() {
		if (toast.action?.callback) {
			toast.action.callback();
		}
		handleRemove();
	}
</script>

<div
	bind:this={toastElement}
	class="toast pointer-events-auto transform transition-all duration-300 ease-out {isVisible &&
	!isRemoving
		? 'translate-x-0 scale-100 opacity-100'
		: 'translate-x-full scale-95 opacity-0'}"
	class:animate-toast-enter={isVisible && !isRemoving}
	class:animate-toast-exit={isRemoving}
	on:mouseenter={pauseProgress}
	on:mouseleave={resumeProgress}
	role="alert"
	aria-live={toast.type === 'error' ? 'assertive' : 'polite'}
>
	<div
		class="rounded-2xl border-2 bg-white shadow-xl {config.bgClass} overflow-hidden backdrop-blur-sm"
	>
		<!-- Progress bar -->
		{#if !isPersistent && duration > 0}
			<div class="h-1 bg-gray-200">
				<div
					class="h-full {config.progressClass} transition-all duration-75 ease-out"
					style="width: {progressWidth}%"
				></div>
			</div>
		{/if}

		<div class="p-4">
			<div class="flex items-start gap-3">
				<!-- Icon -->
				<div class="mt-0.5 flex-shrink-0">
					<span class="text-xl {config.iconClass}">{config.icon}</span>
				</div>

				<!-- Content -->
				<div class="min-w-0 flex-1">
					{#if toast.title}
						<h4 class="mb-1 text-sm font-semibold text-gray-900">
							{toast.title}
						</h4>
					{/if}

					<p class="text-sm leading-relaxed text-gray-700">
						{toast.message}
					</p>

					<!-- Action button -->
					{#if toast.action}
						<div class="mt-3">
							<Button
								variant="ghost"
								size="sm"
								className="text-xs font-medium {config.iconClass} hover:bg-white/50"
								on:click={handleAction}
							>
								{toast.action.label}
							</Button>
						</div>
					{/if}
				</div>

				<!-- Close button -->
				<button
					type="button"
					class="flex-shrink-0 rounded-full p-1 text-gray-400 transition-all duration-200 hover:bg-white/50 hover:text-gray-600"
					on:click={handleRemove}
					aria-label={$t('common.close')}
				>
					<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						/>
					</svg>
				</button>
			</div>
		</div>
	</div>
</div>

<style>
	.toast {
		max-width: 420px;
		width: 100%;
	}

	@media (max-width: 640px) {
		.toast {
			max-width: none;
		}
	}
</style>
