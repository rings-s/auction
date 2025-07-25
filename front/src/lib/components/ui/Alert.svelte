<!-- src/lib/components/Alert.svelte -->
<script>
	/** @type {'info' | 'success' | 'warning' | 'error'} */
	export let type = 'info'; // 'info', 'success', 'warning', 'error'
	export let title = '';
	export let message = '';
	/** @type {{label: string, href?: string, onClick?: () => void} | null} */
	export let action = null; // Optional action button {label, href, onClick}
	export let dismissible = false;
	export let class_ = '';

	export { class_ as class };

	let visible = true;

	// Define styles for different alert types
	const alertStyles = {
		info: {
			bg: 'bg-gray-100', // Uses var(--color-gray-100)
			text: 'text-gray-700', // Uses var(--color-gray-700)
			icon: 'text-gray-500' // Uses var(--color-gray-500)
		},
		success: {
			bg: 'bg-success-100', // Uses var(--color-success-100)
			text: 'text-success-700', // Uses var(--color-success-700)
			icon: 'text-success-500' // Uses var(--color-success-500)
		},
		warning: {
			bg: 'bg-warning-100', // Uses var(--color-warning-100)
			text: 'text-warning-700', // Uses var(--color-warning-700)
			icon: 'text-warning-500' // Uses var(--color-warning-500)
		},
		error: {
			bg: 'bg-danger-100', // Uses var(--color-danger-100)
			text: 'text-danger-700', // Uses var(--color-danger-700)
			icon: 'text-danger-500' // Uses var(--color-danger-500)
		}
	};

	// Default to info if type is invalid
	$: styles = alertStyles[type] || alertStyles.info;

	// Get icon for alert type
	/** @param {'info' | 'success' | 'warning' | 'error'} type */
	function getIcon(type) {
		switch (type) {
			case 'success':
				return `<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />`;
			case 'warning':
				return `<path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />`;
			case 'error':
				return `<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />`;
			case 'info':
			default:
				return `<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />`;
		}
	}

	function dismiss() {
		visible = false;
	}
</script>

{#if visible}
	<div class="rounded-md p-4 {styles.bg} {class_}">
		<div class="flex">
			<div class="flex-shrink-0">
				<svg
					class="h-5 w-5 {styles.icon}"
					viewBox="0 0 20 20"
					fill="currentColor"
					aria-hidden="true"
				>
					{@html getIcon(type)}
				</svg>
			</div>
			<div class="ml-3 flex-1">
				{#if title}
					<h3 class="text-sm font-medium {styles.text}">
						{title}
					</h3>
				{/if}

				{#if message}
					<div class="mt-2 text-sm {styles.text}">
						<p>{message}</p>
					</div>
				{/if}

				{#if action}
					<div class="mt-4">
						{#if action.href}
							<a
								href={action.href}
								class="text-sm font-medium {styles.text} hover:underline focus:underline focus:outline-none"
							>
								{action.label}
							</a>
						{:else}
							<button
								type="button"
								on:click={action.onClick}
								class="text-sm font-medium {styles.text} hover:underline focus:underline focus:outline-none"
							>
								{action.label}
							</button>
						{/if}
					</div>
				{/if}
			</div>

			{#if dismissible}
				<div class="ml-auto pl-3">
					<div class="-mx-1.5 -my-1.5">
						<button
							type="button"
							on:click={dismiss}
							class="inline-flex rounded-md p-1.5 {styles.icon} hover:bg-opacity-10 focus:outline-none"
							aria-label="Dismiss"
						>
							<svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
								<path
									fill-rule="evenodd"
									d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
									clip-rule="evenodd"
								></path>
							</svg>
						</button>
					</div>
				</div>
			{/if}
		</div>
	</div>
{/if}
