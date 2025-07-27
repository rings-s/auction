<!-- src/lib/components/ui/ThemeToggle.svelte -->
<script>
	import { theme } from '$lib/stores/theme.svelte.js';
	import { fade } from 'svelte/transition';

	function toggleTheme() {
		theme.update((t) => {
			const next = t === 'dark' ? 'light' : 'dark';
			if (typeof localStorage !== 'undefined') {
				localStorage.setItem('theme', next);
			}
			return next;
		});
	}
</script>

<button
	class="focus-visible:ring-primary-500 rounded-full border border-gray-200 bg-gray-100 p-2 shadow-md transition-all duration-500 hover:scale-110 hover:shadow-lg focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none dark:border-gray-700 dark:bg-gray-800"
	on:click={toggleTheme}
	aria-label="Toggle theme"
>
	{#if $theme === 'dark'}
		<div in:fade={{ duration: 300 }}>
			<!-- Moon icon (dark mode) -->
			<svg
				class="h-5 w-5 text-indigo-400"
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="currentColor"
			>
				<path
					d="M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.389 5.389 0 0 1-4.4 2.26 5.403 5.403 0 0 1-3.14-9.8c-.44-.06-.9-.1-1.36-.1z"
				/>
				<path
					d="M12 3a9 9 0 0 0-9 9h.07a7.49 7.49 0 0 1 4.51 1.5 7.457 7.457 0 0 1 3.74 3.74 7.49 7.49 0 0 1 1.5 4.51A9 9 0 0 0 12 3z"
					opacity="0.4"
				/>
			</svg>
		</div>
	{:else}
		<div in:fade={{ duration: 300 }}>
			<!-- Sun icon (light mode) -->
			<svg
				class="h-5 w-5 text-amber-400"
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="currentColor"
			>
				<circle cx="12" cy="12" r="4" />
				<path
					d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					fill="none"
				/>
			</svg>
		</div>
	{/if}
</button>
