<!-- src/lib/components/LanguageSelector.svelte -->
<script>
	import { t, locale, LOCALES } from '$lib/i18n';
	import { onMount } from 'svelte';
	import { fly, scale } from 'svelte/transition';

	let isOpen = false;
	let selectedLocale = $locale;

	function toggleDropdown() {
		isOpen = !isOpen;
	}

	function changeLocale(newLocale) {
		locale.set(newLocale);
		localStorage.setItem('locale', newLocale);
		document.documentElement.lang = newLocale;
		document.documentElement.dir = newLocale === 'ar' ? 'rtl' : 'ltr';
		selectedLocale = newLocale;
		isOpen = false;
	}

	function handleClickOutside(event) {
		if (!event.target.closest('.language-selector')) {
			isOpen = false;
		}
	}

	onMount(() => {
		document.addEventListener('click', handleClickOutside);
		return () => {
			document.removeEventListener('click', handleClickOutside);
		};
	});

	$: currentLocaleInfo = LOCALES[selectedLocale] || LOCALES[$locale];
</script>

<div class="language-selector relative inline-block">
	<!-- Trigger Button -->
	<button
		on:click={toggleDropdown}
		class="group relative flex items-center space-x-2 overflow-hidden rounded-2xl border border-white/20 bg-white/10 px-3
           py-2.5 text-slate-600 backdrop-blur-xl
           transition-all duration-300 hover:scale-105
           hover:bg-white/20 hover:text-slate-900 hover:shadow-lg hover:shadow-cyan-500/20
           focus:ring-2 focus:ring-cyan-400/50
           focus:ring-offset-2 focus:ring-offset-transparent
           focus:outline-none active:scale-95
           dark:border-slate-700/50 dark:bg-slate-800/50 dark:text-slate-400 dark:hover:bg-slate-700/50 dark:hover:text-white"
		aria-expanded={isOpen}
		aria-haspopup="true"
	>
		<!-- Globe Icon -->
		<svg
			class="h-4 w-4 transition-transform duration-300 group-hover:scale-110"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
		>
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="2"
				d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"
			/>
		</svg>

		<!-- Current Language -->
		<span class="hidden text-sm font-medium sm:block">
			{currentLocaleInfo?.name || 'EN'}
		</span>

		<!-- Language Code (Mobile) -->
		<span class="text-xs font-bold uppercase sm:hidden">
			{selectedLocale}
		</span>

		<!-- Dropdown Arrow -->
		<svg
			class="h-3 w-3 transition-transform duration-300 {isOpen ? 'rotate-180' : ''}"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
		>
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
		</svg>

		<!-- Shimmer Effect -->
		<div
			class="absolute inset-0 -z-10 -translate-x-full transform bg-gradient-to-r from-transparent
                via-white/10 to-transparent transition-transform duration-1000 group-hover:translate-x-full"
		></div>
	</button>

	<!-- Dropdown Menu -->
	{#if isOpen}
		<div
			class="absolute top-full right-0 z-50 mt-2 min-w-[200px] origin-top-right"
			in:scale={{ duration: 300, start: 0.95 }}
			out:scale={{ duration: 200, start: 0.95 }}
		>
			<div
				class="overflow-hidden rounded-3xl border border-white/20
                  bg-white/90 shadow-2xl shadow-cyan-500/10
                  backdrop-blur-xl dark:border-slate-700/50
                  dark:bg-slate-800/90 dark:shadow-cyan-500/20"
			>
				<!-- Header -->
				<div
					class="border-b border-white/10 bg-gradient-to-r from-cyan-500/5 via-blue-500/5
                    to-purple-500/5 px-4 py-3 dark:border-slate-700/50"
				>
					<p class="text-sm font-semibold text-slate-800 dark:text-white">Select Language</p>
				</div>

				<!-- Language Options -->
				<div class="max-h-64 overflow-y-auto py-2">
					{#each Object.entries(LOCALES) as [code, localeInfo], index}
						<button
							on:click={() => changeLocale(code)}
							class="flex w-full items-center justify-between px-4 py-3 text-sm text-slate-700 transition-all
                     duration-200 hover:bg-white/50 hover:text-slate-900 dark:text-slate-300
                     dark:hover:bg-slate-700/50 dark:hover:text-white
                     {selectedLocale === code
								? 'bg-gradient-to-r from-cyan-500/10 via-blue-500/10 to-purple-500/10 font-semibold text-cyan-600 dark:text-cyan-400'
								: ''}
                     first:rounded-t-3xl last:rounded-b-3xl
                     focus:bg-white/50 focus:outline-none dark:focus:bg-slate-700/50"
							in:fly={{ x: -10, duration: 200, delay: index * 50 }}
						>
							<div class="flex items-center space-x-3">
								<!-- Flag or Language Indicator -->
								<div
									class="flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400 to-blue-500 text-xs font-bold text-white"
								>
									{code.toUpperCase()}
								</div>

								<!-- Language Name -->
								<span>{localeInfo.name}</span>

								<!-- Native Name -->
								{#if localeInfo.nativeName && localeInfo.nativeName !== localeInfo.name}
									<span class="text-xs text-slate-500 dark:text-slate-400">
										({localeInfo.nativeName})
									</span>
								{/if}
							</div>

							<!-- Selected Indicator -->
							{#if selectedLocale === code}
								<div class="flex items-center">
									<svg class="h-4 w-4 text-cyan-500" fill="currentColor" viewBox="0 0 20 20">
										<path
											fill-rule="evenodd"
											d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
											clip-rule="evenodd"
										/>
									</svg>
								</div>
							{/if}
						</button>
					{/each}
				</div>

				<!-- Footer -->
				<div
					class="border-t border-white/10 bg-gradient-to-r from-slate-50/50 to-slate-100/50
                    px-4 py-2 dark:border-slate-700/50 dark:from-slate-800/50 dark:to-slate-900/50"
				>
					<p class="text-center text-xs text-slate-500 dark:text-slate-400">
						{Object.keys(LOCALES).length} languages available
					</p>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	/* Custom scrollbar for dropdown */
	.language-selector ::-webkit-scrollbar {
		width: 4px;
	}

	.language-selector ::-webkit-scrollbar-track {
		background: rgba(0, 0, 0, 0.05);
		border-radius: 2px;
	}

	.language-selector ::-webkit-scrollbar-thumb {
		background: rgba(6, 182, 212, 0.3);
		border-radius: 2px;
	}

	.language-selector ::-webkit-scrollbar-thumb:hover {
		background: rgba(6, 182, 212, 0.5);
	}

	/* Dark mode scrollbar */
	:global(.dark) .language-selector ::-webkit-scrollbar-track {
		background: rgba(255, 255, 255, 0.05);
	}

	/* Accessibility improvements */
	@media (prefers-reduced-motion: reduce) {
		.language-selector * {
			animation-duration: 0.01ms !important;
			transition-duration: 0.01ms !important;
		}
	}

	/* High contrast mode */
	@media (prefers-contrast: high) {
		.language-selector button {
			border: 1px solid currentColor;
		}
	}
</style>
