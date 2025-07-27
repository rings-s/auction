<!-- src/lib/components/ui/MultiSelect.svelte -->
<script>
	import { createEventDispatcher } from 'svelte';
	import { t, locale } from '$lib/i18n';

	let {
		options = [],
		selected = [],
		placeholder = $t('common.selectOptions'),
		disabled = false,
		error = null,
		maxSelections = null,
		searchable = true,
		className = ''
	} = $props();

	const dispatch = createEventDispatcher();
	let isRTL = $derived($locale === 'ar');

	// State
	let isOpen = false;
	let searchQuery = '';
	let dropdownRef;
	let inputRef;

	// Filtered options based on search
	let filteredOptions = $derived(() => {
		if (!searchQuery) return options;

		return options.filter((option) => {
			const label = typeof option === 'string' ? option : option.label;
			return label.toLowerCase().includes(searchQuery.toLowerCase());
		});
	});

	// Selected items display
	let selectedItems = $derived(() => {
		return selected.map((selectedValue) => {
			const option = options.find((opt) => {
				const value = typeof opt === 'string' ? opt : opt.value;
				return value === selectedValue;
			});

			if (option) {
				return typeof option === 'string' ? { label: option, value: option } : option;
			}

			return { label: selectedValue, value: selectedValue };
		});
	});

	// Handle option selection
	function handleOptionClick(option) {
		const value = typeof option === 'string' ? option : option.value;

		if (selected.includes(value)) {
			// Remove if already selected
			const newSelected = selected.filter((item) => item !== value);
			dispatch('change', newSelected);
		} else {
			// Add if not selected and within limit
			if (maxSelections && selected.length >= maxSelections) {
				return;
			}

			const newSelected = [...selected, value];
			dispatch('change', newSelected);
		}

		// Clear search after selection
		searchQuery = '';

		// Keep dropdown open for multiple selections
		if (searchable) {
			inputRef?.focus();
		}
	}

	// Remove selected item
	function removeItem(value) {
		const newSelected = selected.filter((item) => item !== value);
		dispatch('change', newSelected);
	}

	// Handle dropdown toggle
	function toggleDropdown() {
		if (disabled) return;

		isOpen = !isOpen;

		if (isOpen && searchable) {
			setTimeout(() => inputRef?.focus(), 10);
		}
	}

	// Handle click outside
	function handleClickOutside(event) {
		if (dropdownRef && !dropdownRef.contains(event.target)) {
			isOpen = false;
			searchQuery = '';
		}
	}

	// Handle escape key
	function handleKeydown(event) {
		if (event.key === 'Escape') {
			isOpen = false;
			searchQuery = '';
		}
	}

	// Get option display
	function getOptionDisplay(option) {
		return typeof option === 'string' ? option : option.label;
	}

	function getOptionValue(option) {
		return typeof option === 'string' ? option : option.value;
	}

	// Check if option is selected
	function isOptionSelected(option) {
		const value = getOptionValue(option);
		return selected.includes(value);
	}
</script>

<svelte:window on:click={handleClickOutside} on:keydown={handleKeydown} />

<div class="relative {className}" dir={isRTL ? 'rtl' : 'ltr'} bind:this={dropdownRef}>
	<!-- Main Button/Input -->
	<div
		class="min-h-[2.75rem] w-full cursor-pointer rounded-lg border bg-white px-3 py-2 text-gray-900 transition-all duration-200 dark:bg-gray-700 dark:text-white
			{error
			? 'border-red-500 ring-1 ring-red-500'
			: disabled
				? 'cursor-not-allowed border-gray-200 bg-gray-100 dark:border-gray-600 dark:bg-gray-600'
				: isOpen
					? 'ring-opacity-20 border-blue-500 ring-2 ring-blue-500'
					: 'border-gray-300 hover:border-gray-400 dark:border-gray-600 dark:hover:border-gray-500'}"
		on:click={toggleDropdown}
		role="button"
		tabindex="0"
		aria-haspopup="listbox"
		aria-expanded={isOpen}
	>
		<div class="flex min-h-[1.5rem] flex-wrap items-center gap-1">
			<!-- Selected Items -->
			{#each selectedItems as item (item.value)}
				<span
					class="inline-flex items-center gap-1 rounded-md bg-blue-100 px-2 py-1 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200"
				>
					{item.label}
					{#if !disabled}
						<button
							type="button"
							class="ml-1 text-blue-600 hover:text-blue-800 dark:text-blue-300 dark:hover:text-blue-100"
							on:click|stopPropagation={() => removeItem(item.value)}
							aria-label={$t('common.remove')}
						>
							<svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					{/if}
				</span>
			{/each}

			<!-- Search Input or Placeholder -->
			<div class="min-w-[100px] flex-1">
				{#if searchable && isOpen}
					<input
						bind:this={inputRef}
						bind:value={searchQuery}
						type="text"
						class="w-full bg-transparent text-sm placeholder-gray-500 outline-none dark:placeholder-gray-400"
						placeholder={$t('common.search')}
						{disabled}
					/>
				{:else if selectedItems.length === 0}
					<span class="text-sm text-gray-500 dark:text-gray-400">
						{placeholder}
					</span>
				{/if}
			</div>

			<!-- Arrow Icon -->
			<div class="ml-2 flex-shrink-0">
				<svg
					class="h-4 w-4 text-gray-400 transition-transform duration-200 {isOpen
						? 'rotate-180'
						: ''}"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M19 9l-7 7-7-7"
					/>
				</svg>
			</div>
		</div>
	</div>

	<!-- Selection Info -->
	{#if maxSelections && selected.length > 0}
		<div class="mt-1 text-xs text-gray-500 dark:text-gray-400">
			{selected.length} / {maxSelections}
			{$t('common.selected')}
		</div>
	{/if}

	<!-- Error Message -->
	{#if error}
		<p class="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>
	{/if}

	<!-- Dropdown -->
	{#if isOpen && !disabled}
		<div
			class="absolute z-50 mt-1 max-h-60 w-full overflow-auto rounded-lg border border-gray-200 bg-white shadow-lg dark:border-gray-600 dark:bg-gray-700"
		>
			{#if filteredOptions.length === 0}
				<div class="px-3 py-2 text-sm text-gray-500 dark:text-gray-400">
					{searchQuery ? $t('common.noResults') : $t('common.noOptions')}
				</div>
			{:else}
				{#each filteredOptions as option (getOptionValue(option))}
					{@const isSelected = isOptionSelected(option)}
					{@const isDisabled = maxSelections && !isSelected && selected.length >= maxSelections}
					<button
						type="button"
						class="flex w-full items-center justify-between px-3 py-2 text-left text-sm transition-colors duration-150 hover:bg-gray-100 dark:hover:bg-gray-600
							{isSelected
							? 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
							: 'text-gray-900 dark:text-white'}
							{isDisabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}"
						on:click={() => !isDisabled && handleOptionClick(option)}
						disabled={isDisabled}
					>
						<span>{getOptionDisplay(option)}</span>
						{#if isSelected}
							<svg
								class="h-4 w-4 text-blue-600 dark:text-blue-400"
								fill="currentColor"
								viewBox="0 0 20 20"
							>
								<path
									fill-rule="evenodd"
									d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
									clip-rule="evenodd"
								/>
							</svg>
						{/if}
					</button>
				{/each}
			{/if}
		</div>
	{/if}
</div>

<style>
	/* Custom scrollbar for dropdown */
	.overflow-auto::-webkit-scrollbar {
		width: 6px;
	}

	.overflow-auto::-webkit-scrollbar-track {
		background: transparent;
	}

	.overflow-auto::-webkit-scrollbar-thumb {
		background-color: rgba(156, 163, 175, 0.5);
		border-radius: 3px;
	}

	.overflow-auto::-webkit-scrollbar-thumb:hover {
		background-color: rgba(156, 163, 175, 0.7);
	}

	/* Dark mode scrollbar */
	.dark .overflow-auto::-webkit-scrollbar-thumb {
		background-color: rgba(75, 85, 99, 0.5);
	}

	.dark .overflow-auto::-webkit-scrollbar-thumb:hover {
		background-color: rgba(75, 85, 99, 0.7);
	}
</style>
