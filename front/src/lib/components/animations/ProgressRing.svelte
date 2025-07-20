<script>
	import { tweened } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';

	/** @type {number} */
	let progress = $props(0);
	/** @type {number} */
	let size = $props(120);
	/** @type {number} */
	let strokeWidth = $props(8);
	/** @type {string} */
	let color = $props('#3b82f6');
	/** @type {string} */
	let backgroundColor = $props('#e5e7eb');
	/** @type {number} */
	let duration = $props(1000);
	/** @type {Function} */
	let easing = $props(cubicOut);
	/** @type {number} */
	let delay = $props(0);
	/** @type {boolean} */
	let once = $props(true);
	/** @type {boolean} */
	let showText = $props(true);
	/** @type {string} */
	let textColor = $props('#374151');
	/** @type {number} */
	let threshold = $props(0.1);

	let element = $state();
	let hasAnimated = $state(false);

	const animatedProgress = tweened(0, {
		duration,
		easing
	});

	$effect(() => {
		if (typeof window === 'undefined' || !element) return;

		const observer = new IntersectionObserver(
			(entries) => {
				entries.forEach((entry) => {
					if (entry.isIntersecting && (!once || !hasAnimated)) {
						setTimeout(() => {
							animatedProgress.set(progress);
							hasAnimated = true;
						}, delay);
					} else if (!once && !entry.isIntersecting) {
						animatedProgress.set(0, { duration: 0 });
					}
				});
			},
			{
				threshold,
				rootMargin: '20px'
			}
		);

		observer.observe(element);

		return () => {
			observer.disconnect();
		};
	});

	// Calculate circle properties
	let radius = $derived((size - strokeWidth) / 2);
	let circumference = $derived(2 * Math.PI * radius);
	let offset = $derived(circumference - ($animatedProgress / 100) * circumference);
	let center = $derived(size / 2);
</script>

<div
	bind:this={element}
	class="progress-ring relative inline-flex items-center justify-center"
	style="width: {size}px; height: {size}px;"
>
	<svg width={size} height={size} viewBox="0 0 {size} {size}" class="-rotate-90 transform">
		<!-- Background circle -->
		<circle
			cx={center}
			cy={center}
			r={radius}
			stroke={backgroundColor}
			stroke-width={strokeWidth}
			fill="transparent"
			class="opacity-20"
		/>

		<!-- Progress circle -->
		<circle
			cx={center}
			cy={center}
			r={radius}
			stroke={color}
			stroke-width={strokeWidth}
			fill="transparent"
			stroke-dasharray={circumference}
			stroke-dashoffset={offset}
			stroke-linecap="round"
			class="transition-all duration-75 ease-out"
			style="filter: drop-shadow(0 0 6px {color}40);"
		/>
	</svg>

	{#if showText}
		<div class="absolute inset-0 flex items-center justify-center" style="color: {textColor};">
			<span class="text-lg font-semibold tabular-nums">
				{Math.round($animatedProgress)}%
			</span>
		</div>
	{/if}

	<slot />
</div>

<style>
	.progress-ring {
		will-change: transform;
	}
</style>
