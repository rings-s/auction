<script>
	import { toastStore, removeToast } from '$lib/stores/toastStore.svelte.js';
	import { fly } from 'svelte/transition';

	// Basic styling, can be customized extensively with Tailwind CSS
	const typeClasses = {
		info: 'bg-blue-500',
		success: 'bg-green-500',
		warning: 'bg-yellow-500',
		error: 'bg-red-500'
	};
</script>

{#if toastStore.toasts.length > 0}
	<div class="fixed right-0 bottom-0 z-50 w-full max-w-sm space-y-2 p-4">
		{#each toastStore.toasts as toast (toast.id)}
			<div
				in:fly={{ y: 20, duration: 300 }}
				out:fly={{ y: 20, duration: 200 }}
				class="flex items-start justify-between rounded-md p-4 text-white shadow-lg {typeClasses[
					toast.type
				] || 'bg-gray-700'}"
				role="alert"
			>
				<p class="flex-grow pr-2">{toast.message}</p>
				<button
					on:click={() => removeToast(toast.id)}
					class="hover:bg-opacity-20 -mt-1 -mr-1 ml-2 rounded-full p-1 hover:bg-black focus:ring-2 focus:ring-white focus:outline-none"
					aria-label="Close"
				>
					&times;
				</button>
			</div>
		{/each}
	</div>
{/if}
