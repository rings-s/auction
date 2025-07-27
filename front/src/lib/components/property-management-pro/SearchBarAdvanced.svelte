<script>
	import { createEventDispatcher, onMount } from 'svelte';
	import { t } from '$lib/i18n';
	import Button from '$lib/components/ui/Button.svelte';

	const dispatch = createEventDispatcher();

	/** @type {string} */
	export let placeholder = '';
	/** @type {Array} */
	export let savedSearches = [];
	/** @type {boolean} */
	export let showSuggestions = true;

	let searchInput = '';
	let searchInputElement;
	let showDropdown = false;
	let showSavedSearches = false;
	let suggestions = [];
	let selectedSuggestionIndex = -1;
	let searchTimeout;

	// Sample suggestions - in real app, these would come from API
	const sampleSuggestions = [
		'villa in riyadh',
		'apartment near metro',
		'commercial space downtown',
		'warehouse for rent',
		'furnished apartment',
		'luxury villa with pool',
		'office space',
		'studio apartment'
	];

	onMount(() => {
		// Load recent searches from localStorage
		loadRecentSearches();
	});

	function loadRecentSearches() {
		try {
			const recent = localStorage.getItem('recent_property_searches');
			if (recent) {
				const recentSearches = JSON.parse(recent);
				suggestions = [...new Set([...recentSearches, ...sampleSuggestions])].slice(0, 8);
			} else {
				suggestions = sampleSuggestions;
			}
		} catch (e) {
			suggestions = sampleSuggestions;
		}
	}

	function saveRecentSearch(query) {
		if (!query.trim()) return;

		try {
			const recent = localStorage.getItem('recent_property_searches');
			let recentSearches = recent ? JSON.parse(recent) : [];

			// Add to beginning and remove duplicates
			recentSearches = [query, ...recentSearches.filter((s) => s !== query)].slice(0, 10);

			localStorage.setItem('recent_property_searches', JSON.stringify(recentSearches));
			loadRecentSearches();
		} catch (e) {
			console.warn('Failed to save recent search');
		}
	}

	function handleInput(event) {
		const query = event.target.value;
		searchInput = query;

		// Clear existing timeout
		clearTimeout(searchTimeout);

		// Show suggestions if there's input
		if (query.length > 0) {
			showDropdown = true;
			showSavedSearches = false;

			// Filter suggestions based on input
			suggestions = [...sampleSuggestions, ...savedSearches.map((s) => s.name)]
				.filter((s) => s.toLowerCase().includes(query.toLowerCase()))
				.slice(0, 6);
		} else {
			showDropdown = false;
		}

		// Debounce search
		searchTimeout = setTimeout(() => {
			dispatch('search', { query });
		}, 300);
	}

	function handleKeydown(event) {
		if (!showDropdown) return;

		switch (event.key) {
			case 'ArrowDown':
				event.preventDefault();
				selectedSuggestionIndex = Math.min(selectedSuggestionIndex + 1, suggestions.length - 1);
				break;
			case 'ArrowUp':
				event.preventDefault();
				selectedSuggestionIndex = Math.max(selectedSuggestionIndex - 1, -1);
				break;
			case 'Enter':
				event.preventDefault();
				if (selectedSuggestionIndex >= 0) {
					selectSuggestion(suggestions[selectedSuggestionIndex]);
				} else {
					performSearch();
				}
				break;
			case 'Escape':
				showDropdown = false;
				selectedSuggestionIndex = -1;
				searchInputElement.blur();
				break;
		}
	}

	function selectSuggestion(suggestion) {
		searchInput = suggestion;
		showDropdown = false;
		selectedSuggestionIndex = -1;
		saveRecentSearch(suggestion);
		dispatch('search', { query: suggestion });
	}

	function performSearch() {
		if (searchInput.trim()) {
			saveRecentSearch(searchInput.trim());
			dispatch('search', { query: searchInput.trim() });
		}
		showDropdown = false;
		selectedSuggestionIndex = -1;
	}

	function handleFocus() {
		if (searchInput.length === 0) {
			showSavedSearches = true;
			showDropdown = true;
		}
	}

	function handleBlur() {
		// Delay hiding dropdown to allow for clicks
		setTimeout(() => {
			showDropdown = false;
			showSavedSearches = false;
			selectedSuggestionIndex = -1;
		}, 200);
	}

	function handleSaveSearch() {
		if (searchInput.trim()) {
			dispatch('saveSearch', { query: searchInput.trim() });
		}
	}

	function handleLoadSavedSearch(search) {
		searchInput = search.query;
		showDropdown = false;
		dispatch('loadSavedSearch', search);
	}

	function clearSearch() {
		searchInput = '';
		dispatch('search', { query: '' });
		searchInputElement.focus();
	}
</script>

<div class="search-bar-advanced relative">
	<!-- Search Input -->
	<div class="relative">
		<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
			<svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
				/>
			</svg>
		</div>

		<input
			bind:this={searchInputElement}
			bind:value={searchInput}
			type="text"
			{placeholder}
			class="w-full rounded-2xl border border-gray-300 py-3 pr-20 pl-12 text-gray-900 placeholder-gray-500 transition-all duration-200 focus:border-transparent focus:ring-2 focus:ring-blue-500 focus:outline-none"
			on:input={handleInput}
			on:keydown={handleKeydown}
			on:focus={handleFocus}
			on:blur={handleBlur}
			autocomplete="off"
		/>

		<!-- Clear and Save Buttons -->
		<div class="absolute inset-y-0 right-0 flex items-center gap-1 pr-3">
			{#if searchInput}
				<button
					type="button"
					class="rounded-full p-1.5 text-gray-400 transition-all duration-200 hover:bg-gray-100 hover:text-gray-600"
					on:click={clearSearch}
					title={$t('common.clear')}
				>
					<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						/>
					</svg>
				</button>

				<button
					type="button"
					class="rounded-full p-1.5 text-blue-500 transition-all duration-200 hover:bg-blue-50 hover:text-blue-700"
					on:click={handleSaveSearch}
					title={$t('search.saveSearch')}
				>
					<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
						/>
					</svg>
				</button>
			{/if}
		</div>
	</div>

	<!-- Dropdown -->
	{#if showDropdown}
		<div
			class="absolute top-full right-0 left-0 z-50 mt-2 max-h-80 overflow-y-auto rounded-2xl border border-gray-200 bg-white shadow-xl"
		>
			{#if showSavedSearches && savedSearches.length > 0}
				<!-- Saved Searches -->
				<div class="border-b border-gray-100 p-3">
					<h4 class="mb-2 flex items-center gap-2 text-sm font-medium text-gray-700">
						<span>⭐</span>
						{$t('search.savedSearches')}
					</h4>
					<div class="space-y-1">
						{#each savedSearches.slice(0, 3) as search}
							<button
								type="button"
								class="group flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-sm text-gray-700 transition-all duration-200 hover:bg-blue-50 hover:text-blue-700"
								on:click={() => handleLoadSavedSearch(search)}
							>
								<span class="flex items-center gap-2">
									<span class="text-blue-500">💾</span>
									{search.name}
								</span>
								<span class="text-xs text-gray-400 group-hover:text-blue-500">
									{new Date(search.createdAt).toLocaleDateString()}
								</span>
							</button>
						{/each}
					</div>
				</div>
			{/if}

			{#if suggestions.length > 0}
				<!-- Suggestions -->
				<div class="p-3">
					<h4 class="mb-2 flex items-center gap-2 text-sm font-medium text-gray-700">
						<span>💡</span>
						{showSavedSearches ? $t('search.suggestions') : $t('search.recentSearches')}
					</h4>
					<div class="space-y-1">
						{#each suggestions as suggestion, index}
							<button
								type="button"
								class="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm transition-all duration-200 {selectedSuggestionIndex ===
								index
									? 'bg-blue-100 text-blue-700'
									: 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'}"
								on:click={() => selectSuggestion(suggestion)}
							>
								<svg
									class="h-4 w-4 text-gray-400"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
									/>
								</svg>
								{suggestion}
							</button>
						{/each}
					</div>
				</div>
			{/if}

			<!-- Quick Actions -->
			<div class="border-t border-gray-100 bg-gray-50 p-3">
				<div class="flex items-center justify-between text-xs text-gray-500">
					<span>{$t('search.quickTips')}</span>
					<div class="flex items-center gap-2">
						<kbd class="rounded border border-gray-200 bg-white px-2 py-1 text-xs">↑↓</kbd>
						<span>{$t('search.navigate')}</span>
						<kbd class="rounded border border-gray-200 bg-white px-2 py-1 text-xs">Enter</kbd>
						<span>{$t('search.select')}</span>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	/* Custom scrollbar for dropdown */
	.search-bar-advanced :global(.overflow-y-auto::-webkit-scrollbar) {
		width: 6px;
	}

	.search-bar-advanced :global(.overflow-y-auto::-webkit-scrollbar-track) {
		background: #f1f5f9;
		border-radius: 3px;
	}

	.search-bar-advanced :global(.overflow-y-auto::-webkit-scrollbar-thumb) {
		background: #cbd5e1;
		border-radius: 3px;
	}

	.search-bar-advanced :global(.overflow-y-auto::-webkit-scrollbar-thumb:hover) {
		background: #94a3b8;
	}

	kbd {
		font-family: inherit;
	}
</style>
