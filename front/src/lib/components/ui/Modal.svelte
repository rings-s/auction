<!-- src/lib/components/Modal.svelte -->
<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { fade, fly } from 'svelte/transition';

	let {
		show = $bindable(false),
		title = null,
		maxWidth = 'md',
		closeOnEscape = true,
		closeOnClickOutside = true,
		onClose = () => {},
		children
	} = $props();

	type MaxWidthKey =
		| 'sm'
		| 'md'
		| 'lg'
		| 'xl'
		| '2xl'
		| '3xl'
		| '4xl'
		| '5xl'
		| '6xl'
		| '7xl'
		| 'full';

	let modal = $state<HTMLDivElement | null>(null);

	function close() {
		show = false;
		onClose();
	}

	// Tailwind classes for different max-widths
	const maxWidthClasses: Record<MaxWidthKey, string> = {
		sm: 'max-w-sm',
		md: 'max-w-md',
		lg: 'max-w-lg',
		xl: 'max-w-xl',
		'2xl': 'max-w-2xl',
		'3xl': 'max-w-3xl',
		'4xl': 'max-w-4xl',
		'5xl': 'max-w-5xl',
		'6xl': 'max-w-6xl',
		'7xl': 'max-w-7xl',
		full: 'max-w-full'
	};

	let modalClass = $derived(
		`w-full ${maxWidthClasses[maxWidth as MaxWidthKey] || maxWidthClasses.md} mx-auto`
	);

	function handleKeydown(e: KeyboardEvent) {
		if (closeOnEscape && e.key === 'Escape' && show) {
			close();
		}
	}

	function handleClickOutside(e: MouseEvent) {
		if (closeOnClickOutside && modal && !modal.contains(e.target as Node) && show) {
			close();
		}
	}

	onMount(() => {
		document.addEventListener('keydown', handleKeydown);
		return () => {
			document.removeEventListener('keydown', handleKeydown);
		};
	});
</script>

<!-- Trap focus inside the modal when it's open -->
<svelte:window on:keydown={handleKeydown} />

{#if show}
	<div
		class="fixed inset-0 z-50 overflow-y-auto"
		aria-labelledby={title ? 'modal-title' : undefined}
		role="dialog"
		aria-modal="true"
		transition:fade={{ duration: 200 }}
	>
		<!-- Background overlay -->
		<div
			class="bg-opacity-75 dark:bg-opacity-75 fixed inset-0 bg-gray-700 transition-opacity dark:bg-gray-900"
			onclick={handleClickOutside}
			role="button"
			tabindex="-1"
			onkeydown={(e) => {
				if (e.key === 'Enter' || e.key === ' ') {
					e.preventDefault();
					if (closeOnClickOutside) close();
				}
			}}
		></div>

		<!-- Modal container -->
		<div class="relative z-50 flex min-h-screen items-center justify-center p-4 text-center sm:p-0">
			<!-- Modal panel -->
			<div
				bind:this={modal}
				class={modalClass}
				transition:fly={{ y: 30, duration: 300 }}
				style="position: relative; z-index: 60;"
			>
				<div
					class="relative z-50 transform overflow-hidden rounded-lg bg-gray-50 shadow-xl transition-all dark:bg-gray-800"
				>
					{#if title}
						<div class="border-b border-gray-300 px-6 py-4 dark:border-gray-600">
							<h3 class="text-lg font-medium text-gray-700 dark:text-gray-100" id="modal-title">
								{title}
							</h3>
						</div>
					{/if}

					<!-- Modal content -->
					{@render children?.()}

					<!-- Close button in top right corner -->
					<button
						type="button"
						class="absolute top-3 right-3 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
						onclick={close}
						aria-label="Close"
					>
						<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}
