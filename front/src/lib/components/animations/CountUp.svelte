<script>
	import { tweened } from 'svelte/motion';
	import { cubicOut } from 'svelte/easing';

	/** @type {number} */
	let value = $props(0);
	/** @type {number} */
	let duration = $props(1000);
	/** @type {Function} */
	let easing = $props(cubicOut);
	/** @type {number} */
	let delay = $props(0);
	/** @type {boolean} */
	let once = $props(true);
	/** @type {string} */
	let format = $props('');
	/** @type {number} */
	let decimals = $props(0);
	/** @type {string} */
	let prefix = $props('');
	/** @type {string} */
	let suffix = $props('');
	/** @type {string} */
	let separator = $props(',');
	/** @type {number} */
	let threshold = $props(0.1);

	let element = $state();
	let hasAnimated = $state(false);

	const count = tweened(0, {
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
							count.set(value);
							hasAnimated = true;
						}, delay);
					} else if (!once && !entry.isIntersecting) {
						count.set(0, { duration: 0 });
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

	function formatNumber(num) {
		if (format === 'currency') {
			return new Intl.NumberFormat('en-US', {
				style: 'currency',
				currency: 'SAR',
				minimumFractionDigits: decimals,
				maximumFractionDigits: decimals
			}).format(num);
		}

		if (format === 'percent') {
			return new Intl.NumberFormat('en-US', {
				style: 'percent',
				minimumFractionDigits: decimals,
				maximumFractionDigits: decimals
			}).format(num / 100);
		}

		if (format === 'compact') {
			return new Intl.NumberFormat('en-US', {
				notation: 'compact',
				compactDisplay: 'short',
				minimumFractionDigits: decimals,
				maximumFractionDigits: decimals
			}).format(num);
		}

		// Default number formatting
		let formatted = num.toFixed(decimals);

		if (separator) {
			const parts = formatted.split('.');
			parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, separator);
			formatted = parts.join('.');
		}

		return `${prefix}${formatted}${suffix}`;
	}

	let displayValue = $derived(formatNumber($count));
</script>

<span bind:this={element} class="count-up inline-block font-mono tabular-nums">
	{displayValue}
</span>

<style>
	.count-up {
		font-variant-numeric: tabular-nums;
		will-change: contents;
	}
</style>
