/**
 * Accessibility utilities for better UX and compliance
 */

/**
 * Check if user prefers reduced motion
 * @returns {boolean}
 */
export function prefersReducedMotion() {
	if (typeof window === 'undefined') return false;
	return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/**
 * Check if user prefers high contrast
 * @returns {boolean}
 */
export function prefersHighContrast() {
	if (typeof window === 'undefined') return false;
	return window.matchMedia('(prefers-contrast: high)').matches;
}

/**
 * Check if user prefers dark mode
 * @returns {boolean}
 */
export function prefersDarkMode() {
	if (typeof window === 'undefined') return false;
	return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

/**
 * Generate a unique ID for accessibility attributes
 * @param {string} prefix - Prefix for the ID
 * @returns {string}
 */
export function generateId(prefix = 'element') {
	return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Get all focusable elements within a container
 * @param {HTMLElement} container - Container element to search within
 * @returns {HTMLElement[]}
 */
export function getFocusableElements(container) {
	if (!container) return [];

	const focusableSelectors = [
		'a[href]',
		'button:not([disabled])',
		'textarea:not([disabled])',
		'input:not([disabled])',
		'select:not([disabled])',
		'[tabindex]:not([tabindex="-1"])',
		'[contenteditable="true"]',
		'audio[controls]',
		'video[controls]',
		'iframe',
		'embed',
		'object',
		'summary'
	].join(', ');

	return Array.from(container.querySelectorAll(focusableSelectors)).filter((element) => {
		// Filter out hidden elements
		const style = window.getComputedStyle(element);
		return (
			element.offsetWidth > 0 &&
			element.offsetHeight > 0 &&
			style.visibility !== 'hidden' &&
			style.display !== 'none' &&
			!element.hasAttribute('inert')
		);
	});
}

/**
 * Trap focus within a container
 * @param {HTMLElement} container - Container to trap focus within
 * @param {boolean} returnFocus - Whether to return focus to previous element when done
 * @returns {Function} Cleanup function
 */
export function trapFocus(container, returnFocus = true) {
	if (!container) return () => {};

	const previouslyFocused = document.activeElement;
	const focusableElements = getFocusableElements(container);

	if (focusableElements.length === 0) return () => {};

	// Focus first element
	focusableElements[0].focus();

	function handleKeyDown(event) {
		if (event.key !== 'Tab') return;

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
		if (!container.contains(event.target)) {
			focusableElements[0].focus();
		}
	}

	document.addEventListener('keydown', handleKeyDown);
	document.addEventListener('focusin', handleFocusIn);

	return function cleanup() {
		document.removeEventListener('keydown', handleKeyDown);
		document.removeEventListener('focusin', handleFocusIn);

		if (returnFocus && previouslyFocused && previouslyFocused.focus) {
			previouslyFocused.focus();
		}
	};
}

/**
 * Announce a message to screen readers
 * @param {string} message - Message to announce
 * @param {'polite' | 'assertive'} priority - Announcement priority
 * @param {number} timeout - How long to keep the message (ms)
 */
export function announceToScreenReader(message, priority = 'polite', timeout = 5000) {
	if (!message.trim()) return;

	const announcement = document.createElement('div');
	announcement.setAttribute('aria-live', priority);
	announcement.setAttribute('aria-atomic', 'true');
	announcement.style.position = 'absolute';
	announcement.style.left = '-10000px';
	announcement.style.width = '1px';
	announcement.style.height = '1px';
	announcement.style.overflow = 'hidden';

	document.body.appendChild(announcement);

	// Small delay to ensure the element is ready
	setTimeout(() => {
		announcement.textContent = message;
	}, 100);

	// Remove after timeout
	setTimeout(() => {
		if (announcement.parentNode) {
			announcement.parentNode.removeChild(announcement);
		}
	}, timeout);
}

/**
 * Create a roving tabindex manager for navigation
 * @param {HTMLElement[]} elements - Elements to manage
 * @param {number} initialIndex - Initially active index
 * @returns {Object} Manager object with navigation methods
 */
export function createRovingTabIndex(elements, initialIndex = 0) {
	let currentIndex = Math.max(0, Math.min(initialIndex, elements.length - 1));

	function updateTabIndex() {
		elements.forEach((element, index) => {
			element.setAttribute('tabindex', index === currentIndex ? '0' : '-1');
		});
	}

	function focus() {
		if (elements[currentIndex]) {
			elements[currentIndex].focus();
		}
	}

	function next(wrap = true) {
		if (wrap) {
			currentIndex = (currentIndex + 1) % elements.length;
		} else {
			currentIndex = Math.min(currentIndex + 1, elements.length - 1);
		}
		updateTabIndex();
		focus();
	}

	function previous(wrap = true) {
		if (wrap) {
			currentIndex = (currentIndex - 1 + elements.length) % elements.length;
		} else {
			currentIndex = Math.max(currentIndex - 1, 0);
		}
		updateTabIndex();
		focus();
	}

	function first() {
		currentIndex = 0;
		updateTabIndex();
		focus();
	}

	function last() {
		currentIndex = elements.length - 1;
		updateTabIndex();
		focus();
	}

	function setCurrent(index) {
		if (index >= 0 && index < elements.length) {
			currentIndex = index;
			updateTabIndex();
		}
	}

	// Initialize
	updateTabIndex();

	return {
		next,
		previous,
		first,
		last,
		setCurrent,
		focus,
		get currentIndex() {
			return currentIndex;
		},
		get currentElement() {
			return elements[currentIndex];
		}
	};
}

/**
 * Check if an element is visible to screen readers
 * @param {HTMLElement} element - Element to check
 * @returns {boolean}
 */
export function isVisibleToScreenReader(element) {
	if (!element) return false;

	const style = window.getComputedStyle(element);

	return !(
		style.display === 'none' ||
		style.visibility === 'hidden' ||
		element.hasAttribute('aria-hidden') ||
		element.hasAttribute('inert') ||
		style.clip === 'rect(0px, 0px, 0px, 0px)' ||
		style.clipPath === 'inset(50%)'
	);
}

/**
 * Add keyboard navigation to a container
 * @param {HTMLElement} container - Container element
 * @param {Object} options - Navigation options
 * @returns {Function} Cleanup function
 */
export function addKeyboardNavigation(container, options = {}) {
	const {
		orientation = 'vertical', // 'vertical', 'horizontal', 'both'
		wrap = true,
		selector = 'button, a[href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
		onNavigate = () => {},
		onActivate = () => {}
	} = options;

	if (!container) return () => {};

	let elements = [];
	let currentIndex = 0;

	function updateElements() {
		elements = Array.from(container.querySelectorAll(selector)).filter((el) =>
			isVisibleToScreenReader(el)
		);

		if (elements.length > 0) {
			currentIndex = Math.max(0, Math.min(currentIndex, elements.length - 1));
		}
	}

	function handleKeyDown(event) {
		if (elements.length === 0) return;

		let newIndex = currentIndex;
		let handled = false;

		switch (event.key) {
			case 'ArrowDown':
				if (orientation === 'vertical' || orientation === 'both') {
					newIndex = wrap
						? (currentIndex + 1) % elements.length
						: Math.min(currentIndex + 1, elements.length - 1);
					handled = true;
				}
				break;

			case 'ArrowUp':
				if (orientation === 'vertical' || orientation === 'both') {
					newIndex = wrap
						? (currentIndex - 1 + elements.length) % elements.length
						: Math.max(currentIndex - 1, 0);
					handled = true;
				}
				break;

			case 'ArrowRight':
				if (orientation === 'horizontal' || orientation === 'both') {
					newIndex = wrap
						? (currentIndex + 1) % elements.length
						: Math.min(currentIndex + 1, elements.length - 1);
					handled = true;
				}
				break;

			case 'ArrowLeft':
				if (orientation === 'horizontal' || orientation === 'both') {
					newIndex = wrap
						? (currentIndex - 1 + elements.length) % elements.length
						: Math.max(currentIndex - 1, 0);
					handled = true;
				}
				break;

			case 'Home':
				newIndex = 0;
				handled = true;
				break;

			case 'End':
				newIndex = elements.length - 1;
				handled = true;
				break;

			case 'Enter':
			case ' ':
				onActivate(elements[currentIndex], currentIndex);
				handled = true;
				break;
		}

		if (handled) {
			event.preventDefault();
			event.stopPropagation();

			if (newIndex !== currentIndex) {
				currentIndex = newIndex;
				elements[currentIndex].focus();
				onNavigate(elements[currentIndex], currentIndex);
			}
		}
	}

	// Initial setup
	updateElements();

	// Add event listeners
	container.addEventListener('keydown', handleKeyDown);

	// Mutation observer to update elements when DOM changes
	const observer = new MutationObserver(updateElements);
	observer.observe(container, { childList: true, subtree: true });

	return function cleanup() {
		container.removeEventListener('keydown', handleKeyDown);
		observer.disconnect();
	};
}

/**
 * Utility to manage aria-expanded state
 * @param {HTMLElement} trigger - Trigger element
 * @param {HTMLElement} target - Target element to expand/collapse
 * @param {boolean} expanded - Whether target is expanded
 */
export function setAriaExpanded(trigger, target, expanded) {
	if (trigger) {
		trigger.setAttribute('aria-expanded', expanded.toString());
	}

	if (target) {
		target.setAttribute('aria-hidden', (!expanded).toString());
	}
}

/**
 * Utility to manage aria-selected state for option lists
 * @param {HTMLElement[]} options - Option elements
 * @param {number} selectedIndex - Index of selected option
 */
export function setAriaSelected(options, selectedIndex) {
	options.forEach((option, index) => {
		option.setAttribute('aria-selected', (index === selectedIndex).toString());
		option.setAttribute('tabindex', index === selectedIndex ? '0' : '-1');
	});
}

/**
 * Check if device is using touch input primarily
 * @returns {boolean}
 */
export function isPrimaryTouchDevice() {
	if (typeof window === 'undefined') return false;
	return window.matchMedia('(pointer: coarse)').matches;
}

/**
 * Get appropriate focus outline style based on user preferences
 * @returns {string} CSS outline value
 */
export function getFocusOutlineStyle() {
	if (prefersHighContrast()) {
		return '3px solid #ffff00'; // High contrast yellow
	}
	return '2px solid #3b82f6'; // Default blue
}

/**
 * Announce page navigation to screen readers
 * @param {string} pageName - Name of the new page
 * @param {string} [landmarkName] - Name of main landmark on page
 */
export function announcePageNavigation(pageName, landmarkName) {
	const message = landmarkName
		? `Navigated to ${pageName}, ${landmarkName}`
		: `Navigated to ${pageName}`;

	announceToScreenReader(message, 'assertive', 3000);
}

/**
 * Create accessible tooltip behavior
 * @param {HTMLElement} trigger - Element that triggers tooltip
 * @param {HTMLElement} tooltip - Tooltip element
 * @param {Object} options - Tooltip options
 * @returns {Function} Cleanup function
 */
export function createAccessibleTooltip(trigger, tooltip, options = {}) {
	const { hideOnEscape = true, hideOnClickOutside = true, delay = 300 } = options;

	if (!trigger || !tooltip) return () => {};

	let showTimeout;
	let hideTimeout;
	let isVisible = false;

	// Setup ARIA attributes
	const tooltipId = tooltip.id || generateId('tooltip');
	tooltip.id = tooltipId;
	trigger.setAttribute('aria-describedby', tooltipId);
	tooltip.setAttribute('role', 'tooltip');

	function show() {
		clearTimeout(hideTimeout);
		showTimeout = setTimeout(() => {
			tooltip.style.visibility = 'visible';
			tooltip.setAttribute('aria-hidden', 'false');
			isVisible = true;
		}, delay);
	}

	function hide() {
		clearTimeout(showTimeout);
		hideTimeout = setTimeout(() => {
			tooltip.style.visibility = 'hidden';
			tooltip.setAttribute('aria-hidden', 'true');
			isVisible = false;
		}, 100);
	}

	function handleKeyDown(event) {
		if (event.key === 'Escape' && hideOnEscape && isVisible) {
			hide();
			trigger.focus();
		}
	}

	function handleClickOutside(event) {
		if (
			hideOnClickOutside &&
			isVisible &&
			!trigger.contains(event.target) &&
			!tooltip.contains(event.target)
		) {
			hide();
		}
	}

	// Event listeners
	trigger.addEventListener('mouseenter', show);
	trigger.addEventListener('mouseleave', hide);
	trigger.addEventListener('focus', show);
	trigger.addEventListener('blur', hide);

	if (hideOnEscape) {
		document.addEventListener('keydown', handleKeyDown);
	}

	if (hideOnClickOutside) {
		document.addEventListener('click', handleClickOutside);
	}

	// Initial state
	hide();

	return function cleanup() {
		clearTimeout(showTimeout);
		clearTimeout(hideTimeout);

		trigger.removeEventListener('mouseenter', show);
		trigger.removeEventListener('mouseleave', hide);
		trigger.removeEventListener('focus', show);
		trigger.removeEventListener('blur', hide);

		if (hideOnEscape) {
			document.removeEventListener('keydown', handleKeyDown);
		}

		if (hideOnClickOutside) {
			document.removeEventListener('click', handleClickOutside);
		}
	};
}
