<script>
	/** @type {'polite' | 'assertive' | 'off'} */
	let politeness = $props('polite');
	/** @type {boolean} */
	let atomic = $props(false);
	/** @type {boolean} */
	let relevant = $props(true);
	/** @type {string} */
	let label = $props('');
	/** @type {string} */
	let className = $props('');

	let liveRegion = $state();
	let announcements = $state([]);
	let currentId = $state(0);

	$effect(() => {
		// Ensure the live region is available to screen readers
		if (liveRegion) {
			liveRegion.setAttribute('aria-live', politeness);
			if (atomic) liveRegion.setAttribute('aria-atomic', 'true');
			if (label) liveRegion.setAttribute('aria-label', label);
			if (relevant) liveRegion.setAttribute('aria-relevant', 'additions text');
		}
	});

	/**
	 * Announce a message to screen readers
	 * @param {string} message - The message to announce
	 * @param {number} [timeout=5000] - How long to keep the message (in ms)
	 */
	export function announce(message, timeout = 5000) {
		if (!message.trim()) return;

		const id = ++currentId;
		const announcement = { id, message, timestamp: Date.now() };

		announcements = [...announcements, announcement];

		// Remove the announcement after timeout
		if (timeout > 0) {
			setTimeout(() => {
				announcements = announcements.filter((a) => a.id !== id);
			}, timeout);
		}
	}

	/**
	 * Clear all announcements
	 */
	export function clear() {
		announcements = [];
	}

	/**
	 * Announce status updates (for form validation, loading states, etc.)
	 * @param {string} status - The status message
	 * @param {'success' | 'error' | 'warning' | 'info'} [type='info'] - Status type
	 */
	export function announceStatus(status, type = 'info') {
		const prefix = {
			success: 'Success: ',
			error: 'Error: ',
			warning: 'Warning: ',
			info: ''
		}[type];

		announce(prefix + status, type === 'error' ? 8000 : 5000);
	}

	/**
	 * Announce navigation changes
	 * @param {string} pageName - Name of the new page/section
	 */
	export function announceNavigation(pageName) {
		announce(`Navigated to ${pageName}`);
	}

	/**
	 * Announce loading states
	 * @param {boolean} isLoading - Whether something is loading
	 * @param {string} [context=''] - Context for what's loading
	 */
	export function announceLoading(isLoading, context = '') {
		if (isLoading) {
			announce(`Loading${context ? ' ' + context : ''}...`);
		} else {
			announce(`${context ? context + ' ' : ''}Loaded successfully`);
		}
	}
</script>

<div
	bind:this={liveRegion}
	class="live-region {className}"
	aria-live={politeness}
	aria-atomic={atomic.toString()}
	aria-relevant={relevant ? 'additions text' : 'all'}
	aria-label={label}
	role="status"
>
	{#each announcements as announcement (announcement.id)}
		<div class="announcement">
			{announcement.message}
		</div>
	{/each}

	<!-- Slot for static content that should also be announced -->
	<slot />
</div>

<style>
	.live-region {
		position: absolute;
		left: -10000px;
		width: 1px;
		height: 1px;
		overflow: hidden;
		clip: rect(0, 0, 0, 0);
		white-space: nowrap;
	}

	.announcement {
		/* Ensure each announcement is on its own line */
		display: block;
	}

	/* Alternative visible live region (for debugging or status displays) */
	.live-region.visible {
		position: static;
		left: auto;
		width: auto;
		height: auto;
		overflow: visible;
		clip: auto;
		white-space: normal;
		padding: 0.5rem;
		background: #f3f4f6;
		border-left: 4px solid #3b82f6;
		border-radius: 0.25rem;
		font-size: 0.875rem;
		color: #374151;
	}

	/* High contrast mode support */
	@media (prefers-contrast: high) {
		.live-region.visible {
			background: #fff;
			border-color: #000;
			color: #000;
		}
	}

	/* Dark mode support */
	@media (prefers-color-scheme: dark) {
		.live-region.visible {
			background: #374151;
			border-color: #60a5fa;
			color: #f9fafb;
		}
	}
</style>
