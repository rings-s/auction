<!-- src/lib/components/ui/ToastContainer.svelte -->
<script>
	import { onMount } from 'svelte';
	import { fade, fly } from 'svelte/transition';
	import { toast } from '$lib/stores/toast';

	let toasts = [];

	// Subscribe to toast store changes
	onMount(() => {
		const unsubscribe = toast.subscribe((value) => {
			toasts = value;
		});

		return unsubscribe;
	});

	// Dismiss a toast
	function dismiss(id) {
		toast.dismiss(id);
	}

	// Get icon based on toast type
	function getIcon(type) {
		switch (type) {
			case 'success':
				return `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>`;
			case 'error':
				return `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>`;
			case 'warning':
				return `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>`;
			case 'info':
			default:
				return `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>`;
		}
	}

	// Get background color class based on type
	function getBackgroundColor(type) {
		switch (type) {
			case 'success':
				return 'bg-status-success';
			case 'error':
				return 'bg-status-error';
			case 'warning':
				return 'bg-status-warning';
			case 'info':
			default:
				return 'bg-status-info';
		}
	}
</script>

<div class="fixed right-0 bottom-0 z-50 m-4 max-w-sm space-y-4 p-4">
	{#each toasts as { id, message, type, dismissible } (id)}
		<div
			in:fly={{ y: 50, duration: 300 }}
			out:fade={{ duration: 200 }}
			class="bg-cosmos-bg-light flex items-center overflow-hidden rounded-lg p-4 shadow-lg"
		>
			<div
				class={`mr-3 w-1.5 flex-shrink-0 self-stretch rounded-l-lg ${getBackgroundColor(type)}`}
			></div>
			<div class="mr-3 flex-shrink-0">
				{@html getIcon(type)}
			</div>
			<div class="text-cosmos-text mr-2 flex-grow">
				{message}
			</div>
			{#if dismissible}
				<button
					class="text-cosmos-text-muted hover:text-cosmos-text flex-shrink-0 transition"
					on:click={() => dismiss(id)}
					aria-label="Dismiss"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="h-5 w-5"
						viewBox="0 0 20 20"
						fill="currentColor"
					>
						<path
							fill-rule="evenodd"
							d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
							clip-rule="evenodd"
						/>
					</svg>
				</button>
			{/if}
		</div>
	{/each}
</div>
