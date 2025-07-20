<script>
	/** @type {number} */
	let staggerDelay = $props(100);
	/** @type {number} */
	let initialDelay = $props(0);
	/** @type {number} */
	let duration = $props(400);
	/** @type {string} */
	let easing = $props('ease-out');
	/** @type {boolean} */
	let once = $props(true);
	/** @type {string} */
	let className = $props('');
	/** @type {number} */
	let threshold = $props(0.1);
	/** @type {Array} */
	let items = $props([]);

	let container = $state();
	let isVisible = $state(false);
	let hasAnimated = $state(false);
	let itemElements = $state([]);

	$effect(() => {
		if (typeof window === 'undefined' || !container) return;

		// Get all child elements
		itemElements = Array.from(container.children);

		const observer = new IntersectionObserver(
			(entries) => {
				entries.forEach((entry) => {
					if (entry.isIntersecting && (!once || !hasAnimated)) {
						setTimeout(() => {
							animateItems();
							hasAnimated = true;
						}, initialDelay);
					} else if (!once && !entry.isIntersecting) {
						resetItems();
					}
				});
			},
			{
				threshold,
				rootMargin: '50px 0px -50px 0px'
			}
		);

		observer.observe(container);

		return () => {
			observer.disconnect();
		};
	});

	// Set initial styles when items change
	$effect(() => {
		if (itemElements.length > 0) {
			setInitialStyles();
		}
	});

	function animateItems() {
		itemElements.forEach((item, index) => {
			setTimeout(() => {
				item.style.transform = 'translateY(0)';
				item.style.opacity = '1';
			}, index * staggerDelay);
		});
		isVisible = true;
	}

	function resetItems() {
		itemElements.forEach((item) => {
			item.style.transform = 'translateY(30px)';
			item.style.opacity = '0';
		});
		isVisible = false;
	}

	function setInitialStyles() {
		if (itemElements.length === 0) return;

		itemElements.forEach((item) => {
			item.style.transition = `all ${duration}ms ${easing}`;
			item.style.transform = 'translateY(30px)';
			item.style.opacity = '0';
			item.style.willChange = 'transform, opacity';
		});
	}
</script>

<div
	bind:this={container}
	class="staggered-list {className}"
	on:click
	on:keydown
	role="presentation"
>
	<slot />
</div>

<style>
	.staggered-list {
		/* Container styles if needed */
	}
</style>
