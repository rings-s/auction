<script>
	/** @type {boolean} */
	let active = $props(false);
	/** @type {boolean} */
	let restoreFocus = $props(true);
	/** @type {string} */
	let className = $props('');

	// Event handlers
	let onfocusEscape = $props();
	let onescape = $props();

	let container = $state();
	let previousActiveElement = $state();
	let focusableElements = $state([]);

	$effect(() => {
		if (active) {
			trapFocus();
		} else if (restoreFocus && previousActiveElement) {
			previousActiveElement.focus();
			previousActiveElement = null;
		}

		return () => {
			if (restoreFocus && previousActiveElement) {
				previousActiveElement.focus();
			}
		};
	});

	function trapFocus() {
		if (!container) return;

		// Store the previously focused element
		previousActiveElement = document.activeElement;

		// Get all focusable elements
		updateFocusableElements();

		// Focus the first focusable element
		if (focusableElements.length > 0) {
			focusableElements[0].focus();
		}

		// Add event listeners
		document.addEventListener('keydown', handleKeydown);
		document.addEventListener('focusin', handleFocusIn);

		return () => {
			document.removeEventListener('keydown', handleKeydown);
			document.removeEventListener('focusin', handleFocusIn);
		};
	}

	function updateFocusableElements() {
		if (!container) return;

		const focusableSelectors = [
			'a[href]',
			'button:not([disabled])',
			'textarea:not([disabled])',
			'input:not([disabled])',
			'select:not([disabled])',
			'[tabindex]:not([tabindex="-1"])',
			'[contenteditable="true"]'
		].join(', ');

		focusableElements = Array.from(container.querySelectorAll(focusableSelectors)).filter((el) => {
			// Filter out hidden elements
			return (
				el.offsetWidth > 0 && el.offsetHeight > 0 && getComputedStyle(el).visibility !== 'hidden'
			);
		});
	}

	function handleKeydown(event) {
		if (!active || event.key !== 'Tab') return;

		updateFocusableElements();

		if (focusableElements.length === 0) {
			event.preventDefault();
			return;
		}

		const firstElement = focusableElements[0];
		const lastElement = focusableElements[focusableElements.length - 1];

		if (event.shiftKey) {
			// Shift + Tab
			if (document.activeElement === firstElement) {
				event.preventDefault();
				lastElement.focus();
			}
		} else {
			// Tab
			if (document.activeElement === lastElement) {
				event.preventDefault();
				firstElement.focus();
			}
		}
	}

	function handleFocusIn(event) {
		if (!active || !container) return;

		// If focus moves outside the container, bring it back
		if (!container.contains(event.target)) {
			event.preventDefault();

			updateFocusableElements();

			if (focusableElements.length > 0) {
				focusableElements[0].focus();
			}

			onfocusEscape?.({ target: event.target });
		}
	}

	function handleEscape(event) {
		if (event.key === 'Escape') {
			onescape?.();
		}
	}
</script>

<div bind:this={container} class="focus-trap {className}" on:keydown={handleEscape} role="none">
	<slot />
</div>

<style>
	.focus-trap {
		isolation: isolate;
	}

	/* Ensure focus trap doesn't interfere with layout */
	.focus-trap:focus {
		outline: none;
	}
</style>
