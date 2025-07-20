<script>
	/** @type {number} */
	let delay = $props(0);
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

	let element = $state();
	let isVisible = $state(false);
	let hasAnimated = $state(false);

	$effect(() => {
		if (typeof window === 'undefined' || !element) return;

		const observer = new IntersectionObserver(
			(entries) => {
				entries.forEach((entry) => {
					if (entry.isIntersecting && (!once || !hasAnimated)) {
						setTimeout(() => {
							isVisible = true;
							hasAnimated = true;
						}, delay);
					} else if (!once && !entry.isIntersecting) {
						isVisible = false;
					}
				});
			},
			{
				threshold,
				rootMargin: '50px 0px -50px 0px'
			}
		);

		observer.observe(element);

		return () => {
			observer.disconnect();
		};
	});

	let animationStyle = $derived(`
        transition: all ${duration}ms ${easing};
        transform: translateY(${isVisible ? '0' : '30px'});
        opacity: ${isVisible ? '1' : '0'};
    `);
</script>

<div bind:this={element} class="fade-in-up {className}" style={animationStyle}>
	<slot />
</div>

<style>
	.fade-in-up {
		will-change: transform, opacity;
	}
</style>
