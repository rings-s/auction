<script>
	/** @type {string} */
	let href = $props('#main-content');
	/** @type {string} */
	let label = $props('Skip to main content');
	/** @type {string} */
	let className = $props('');
</script>

<a
	{href}
	class="skip-link {className}"
	on:click={(e) => {
		// Focus the target element after navigation
		setTimeout(() => {
			const target = document.querySelector(href);
			if (target) {
				target.focus();
				target.scrollIntoView({ behavior: 'smooth', block: 'start' });
			}
		}, 100);
	}}
>
	{label}
</a>

<style>
	.skip-link {
		position: absolute;
		top: -100px;
		left: 0;
		background: #000;
		color: #fff;
		padding: 0.75rem 1rem;
		border-radius: 0 0 0.5rem 0;
		text-decoration: none;
		font-weight: 600;
		z-index: 10000;
		transition: top 200ms ease-out;
		border: 2px solid #fff;
	}

	.skip-link:focus {
		top: 0;
		outline: 3px solid #3b82f6;
		outline-offset: 2px;
	}

	.skip-link:hover {
		background: #1f2937;
	}

	/* High contrast mode support */
	@media (prefers-contrast: high) {
		.skip-link {
			background: #000;
			color: #fff;
			border: 3px solid #fff;
		}

		.skip-link:focus {
			outline: 5px solid #ff0;
			outline-offset: 3px;
		}
	}

	/* Reduced motion support */
	@media (prefers-reduced-motion: reduce) {
		.skip-link {
			transition: none;
		}
	}
</style>
