<script>
	import { toastStore } from '$lib/stores/toastStore.svelte.js';
	import Toast from './Toast.svelte';

	let container = $state();

	// Use the toasts getter from the store directly
	let toasts = $derived(toastStore.toasts);

	function removeToast(id) {
		toastStore.remove(id);
	}
</script>

<!-- Toast Container -->
<div
	bind:this={container}
	class="toast-container pointer-events-none fixed top-4 right-4 z-100 space-y-3"
	aria-live="polite"
	aria-label="Notifications"
>
	{#each toasts as toast (toast.id)}
		<Toast {toast} onremove={() => removeToast(toast.id)} />
	{/each}
</div>

<style>
	.toast-container {
		max-width: 420px;
		width: 100%;
	}

	@media (max-width: 640px) {
		.toast-container {
			top: 1rem;
			right: 1rem;
			left: 1rem;
			max-width: none;
		}
	}
</style>
