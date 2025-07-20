<script>
	/** @type {Array<HTMLElement>} */
	let items = $props([]);
	/** @type {number} */
	let activeIndex = $props(0);
	/** @type {string} */
	let orientation = $props('vertical'); // 'vertical', 'horizontal', 'both'
	/** @type {boolean} */
	let wrap = $props(true);
	/** @type {boolean} */
	let autoFocus = $props(false);
	/** @type {string} */
	let role = $props('listbox');
	/** @type {string} */
	let className = $props('');

	// Event handlers
	let onchange = $props();
	let onactivate = $props();

	let container = $state();
	let navigationItems = $state([]);

	$effect(() => {
		updateNavigationItems();

		if (autoFocus && navigationItems.length > 0) {
			focusItem(activeIndex);
		}
	});

	$effect(() => {
		if (items.length > 0) {
			updateNavigationItems();
		}
	});

	$effect(() => {
		if (activeIndex >= 0 && navigationItems.length > 0) {
			focusItem(activeIndex);
		}
	});

	function updateNavigationItems() {
		if (!container) return;

		// If items array is provided, use it; otherwise find focusable children
		if (items.length > 0) {
			navigationItems = items;
		} else {
			const focusableSelectors = [
				'button:not([disabled])',
				'a[href]',
				'input:not([disabled])',
				'select:not([disabled])',
				'textarea:not([disabled])',
				'[tabindex]:not([tabindex="-1"])'
			].join(', ');

			navigationItems = Array.from(container.querySelectorAll(focusableSelectors)).filter(
				(el) => el.offsetWidth > 0 && el.offsetHeight > 0
			);
		}

		// Set up ARIA attributes
		setupAriaAttributes();
	}

	function setupAriaAttributes() {
		if (!container || navigationItems.length === 0) return;

		// Set container attributes
		container.setAttribute('role', role);
		container.setAttribute('aria-activedescendant', navigationItems[activeIndex]?.id || '');

		// Set item attributes
		navigationItems.forEach((item, index) => {
			if (!item.id) {
				item.id = `nav-item-${Math.random().toString(36).substr(2, 9)}`;
			}

			item.setAttribute('role', role === 'listbox' ? 'option' : 'menuitem');
			item.setAttribute('aria-selected', (index === activeIndex).toString());

			// Make items focusable but not tabbable (except active item)
			item.setAttribute('tabindex', index === activeIndex ? '0' : '-1');
		});
	}

	function focusItem(index) {
		if (index < 0 || index >= navigationItems.length) return;

		// Update tabindex
		navigationItems.forEach((item, i) => {
			item.setAttribute('tabindex', i === index ? '0' : '-1');
			item.setAttribute('aria-selected', (i === index).toString());
		});

		// Focus the item
		navigationItems[index].focus();

		// Update container aria-activedescendant
		if (container) {
			container.setAttribute('aria-activedescendant', navigationItems[index].id);
		}

		dispatch('navigate', { index, item: navigationItems[index] });
	}

	function handleKeydown(event) {
		if (navigationItems.length === 0) return;

		let newIndex = activeIndex;
		let handled = false;

		switch (event.key) {
			case 'ArrowDown':
				if (orientation === 'vertical' || orientation === 'both') {
					newIndex = wrap
						? (activeIndex + 1) % navigationItems.length
						: Math.min(activeIndex + 1, navigationItems.length - 1);
					handled = true;
				}
				break;

			case 'ArrowUp':
				if (orientation === 'vertical' || orientation === 'both') {
					newIndex = wrap
						? (activeIndex - 1 + navigationItems.length) % navigationItems.length
						: Math.max(activeIndex - 1, 0);
					handled = true;
				}
				break;

			case 'ArrowRight':
				if (orientation === 'horizontal' || orientation === 'both') {
					newIndex = wrap
						? (activeIndex + 1) % navigationItems.length
						: Math.min(activeIndex + 1, navigationItems.length - 1);
					handled = true;
				}
				break;

			case 'ArrowLeft':
				if (orientation === 'horizontal' || orientation === 'both') {
					newIndex = wrap
						? (activeIndex - 1 + navigationItems.length) % navigationItems.length
						: Math.max(activeIndex - 1, 0);
					handled = true;
				}
				break;

			case 'Home':
				newIndex = 0;
				handled = true;
				break;

			case 'End':
				newIndex = navigationItems.length - 1;
				handled = true;
				break;

			case 'Enter':
			case ' ':
				dispatch('activate', { index: activeIndex, item: navigationItems[activeIndex] });
				handled = true;
				break;

			case 'Escape':
				dispatch('escape');
				handled = true;
				break;
		}

		if (handled) {
			event.preventDefault();
			event.stopPropagation();

			if (newIndex !== activeIndex) {
				activeIndex = newIndex;
				focusItem(activeIndex);
			}
		}
	}

	function handleFocus(event) {
		// When an item receives focus, update the active index
		const focusedIndex = navigationItems.indexOf(event.target);
		if (focusedIndex !== -1 && focusedIndex !== activeIndex) {
			activeIndex = focusedIndex;
			setupAriaAttributes();
		}
	}

	// Public methods for external control
	export function next() {
		const newIndex = wrap
			? (activeIndex + 1) % navigationItems.length
			: Math.min(activeIndex + 1, navigationItems.length - 1);
		if (newIndex !== activeIndex) {
			activeIndex = newIndex;
			focusItem(activeIndex);
		}
	}

	export function previous() {
		const newIndex = wrap
			? (activeIndex - 1 + navigationItems.length) % navigationItems.length
			: Math.max(activeIndex - 1, 0);
		if (newIndex !== activeIndex) {
			activeIndex = newIndex;
			focusItem(activeIndex);
		}
	}

	export function first() {
		if (activeIndex !== 0) {
			activeIndex = 0;
			focusItem(activeIndex);
		}
	}

	export function last() {
		const lastIndex = navigationItems.length - 1;
		if (activeIndex !== lastIndex) {
			activeIndex = lastIndex;
			focusItem(activeIndex);
		}
	}

	export function activate() {
		if (navigationItems[activeIndex]) {
			dispatch('activate', { index: activeIndex, item: navigationItems[activeIndex] });
		}
	}
</script>

<div
	bind:this={container}
	class="keyboard-navigation {className}"
	on:keydown={handleKeydown}
	on:focusin={handleFocus}
	{role}
	tabindex="-1"
>
	<slot {navigationItems} {activeIndex} {focusItem} />
</div>

<style>
	.keyboard-navigation {
		/* Ensure the container can receive focus for keyboard navigation */
		outline: none;
	}

	.keyboard-navigation:focus-within {
		/* Visual indicator when navigation is active */
		outline: 2px solid #3b82f6;
		outline-offset: 2px;
	}

	/* High contrast mode support */
	@media (prefers-contrast: high) {
		.keyboard-navigation:focus-within {
			outline: 3px solid #000;
			outline-offset: 3px;
		}
	}

	/* Reduced motion support */
	@media (prefers-reduced-motion: reduce) {
		.keyboard-navigation {
			scroll-behavior: auto;
		}
	}
</style>
