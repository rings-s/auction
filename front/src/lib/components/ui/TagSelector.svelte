<!-- src/lib/components/TagSelector.svelte -->
<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { slide } from 'svelte/transition';
  
  export let tags = [];
  export let selectedTags = [];
  export let title = '';
  export let readonly = false;
  export let maxHeight = '200px';
  export let searchable = true;
  export let placeholder = 'Search tags...';
  export let size = 'default'; // 'small', 'default', 'large'
  export let variant = 'default'; // 'default', 'rounded', 'pill'
  
  const dispatch = createEventDispatcher();
  
  let searchQuery = '';
  let container;
  let isExpanded = false;
  let hoveredTag = null;
  let searchInputId = `tag-search-${Math.random().toString(36).slice(2)}`;
  
  $: filteredTags = searchQuery 
    ? tags.filter(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    : tags;
    
  $: hasSelectedTags = selectedTags.length > 0;

  const sizeClasses = {
    small: 'px-2 py-1 text-xs',
    default: 'px-3 py-1.5 text-sm',
    large: 'px-4 py-2 text-base'
  };

  const variantClasses = {
    default: 'rounded-md',
    rounded: 'rounded-lg',
    pill: 'rounded-full'
  };

  function toggleTag(tag) {
    if (readonly) return;
    
    if (selectedTags.includes(tag)) {
      selectedTags = selectedTags.filter(t => t !== tag);
    } else {
      selectedTags = [...selectedTags, tag];
    }
    
    dispatch('change', selectedTags);
  }

  function handleKeydown(event, tag) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      toggleTag(tag);
    }
  }

  function clearSelection() {
    if (!readonly) {
      selectedTags = [];
      dispatch('change', selectedTags);
    }
  }

  onMount(() => {
    const handleClickOutside = (event) => {
      if (container && !container.contains(event.target)) {
        isExpanded = false;
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  });
</script>

<div 
  class="tag-selector space-y-2" 
  bind:this={container}
  class:is-expanded={isExpanded}
  role="region"
  aria-label={title || 'Tag selector'}
>
  {#if title}
    <div class="flex justify-between items-center">
      <label for={searchInputId} class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {title}
        {#if hasSelectedTags}
          <span class="ml-2 text-xs text-gray-500 dark:text-gray-400" aria-live="polite">
            ({selectedTags.length} selected)
          </span>
        {/if}
      </label>

      {#if hasSelectedTags && !readonly}
        <button
          type="button"
          on:click={clearSelection}
          class="text-xs text-gray-500 hover:text-danger-500 dark:text-gray-400 dark:hover:text-danger-400 transition-colors duration-200"
          aria-label="Clear all selected tags"
        >
          Clear all
        </button>
      {/if}
    </div>
  {/if}

  {#if searchable && !readonly}
    <div class="relative">
      <input
        type="text"
        id={searchInputId}
        bind:value={searchQuery}
        {placeholder}
        class="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:focus:border-primary-500 text-sm"
        on:focus={() => isExpanded = true}
        aria-label={placeholder}
        role="combobox"
        aria-expanded={isExpanded}
        aria-controls="tag-list"
        aria-autocomplete="list"
      />
      {#if searchQuery}
        <button
          type="button"
          class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          on:click={() => searchQuery = ''}
          aria-label="Clear search"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      {/if}
    </div>
  {/if}

  <div 
    id="tag-list"
    class="flex flex-wrap gap-2 {searchable ? 'max-h-[' + maxHeight + '] overflow-y-auto' : ''}"
    class:p-2={searchable}
    role="listbox"
    aria-multiselectable="true"
    aria-label="Available tags"
  >
    {#each filteredTags as tag (tag)}
      <div
        class={`
          group relative flex items-center transition-all duration-200 
          ${sizeClasses[size]} 
          ${variantClasses[variant]}
          ${selectedTags.includes(tag) 
            ? 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200 ring-2 ring-primary-300 dark:ring-primary-700 shadow-sm' 
            : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 hover:shadow-md'}
          ${readonly ? 'cursor-default opacity-75' : 'cursor-pointer'}
          ${hoveredTag === tag ? 'scale-105' : ''}
        `}
      >
        <button
          type="button"
          on:click={() => toggleTag(tag)}
          on:keydown={(e) => handleKeydown(e, tag)}
          disabled={readonly}
          on:mouseenter={() => hoveredTag = tag}
          on:mouseleave={() => hoveredTag = null}
          role="option"
          aria-selected={selectedTags.includes(tag)}
          class="flex items-center gap-1.5 w-full h-full"
        >
          {#if selectedTags.includes(tag)}
            <svg 
              class="w-4 h-4 text-primary-600 dark:text-primary-400" 
              xmlns="http://www.w3.org/2000/svg" 
              viewBox="0 0 20 20" 
              fill="currentColor"
              aria-hidden="true"
            >
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          {/if}
          {tag}
          
          {#if !readonly && selectedTags.includes(tag)}
            <span 
              class="ml-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
              aria-label={`Remove ${tag} tag`}
            >
              <svg class="w-4 h-4 text-gray-400 hover:text-danger-500 dark:text-gray-500 dark:hover:text-danger-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </span>
          {/if}
        </button>
      </div>
    {/each}

    {#if filteredTags.length === 0}
      <div 
        class="w-full text-center py-4 text-sm text-gray-500 dark:text-gray-400"
        role="status"
      >
        No tags found
      </div>
    {/if}
  </div>
</div>

<style>
  .tag-selector {
    --tag-transition: 200ms ease-in-out;
  }

  .tag-selector button {
    transform-origin: center;
    backface-visibility: hidden;
  }

  .tag-selector button:focus-visible {
    outline: 2px solid var(--color-primary-500);
    outline-offset: 2px;
  }

  /* Custom scrollbar */
  .tag-selector div {
    scrollbar-width: thin;
    scrollbar-color: var(--color-gray-300) transparent;
  }

  .tag-selector div::-webkit-scrollbar {
    width: 6px;
  }

  .tag-selector div::-webkit-scrollbar-track {
    background: transparent;
  }

  .tag-selector div::-webkit-scrollbar-thumb {
    background-color: var(--color-gray-300);
    border-radius: 3px;
  }

  .tag-selector div::-webkit-scrollbar-thumb:hover {
    background-color: var(--color-gray-400);
  }

  /* Dark mode scrollbar */
  :global(.dark) .tag-selector div {
    scrollbar-color: var(--color-gray-600) transparent;
  }

  :global(.dark) .tag-selector div::-webkit-scrollbar-thumb {
    background-color: var(--color-gray-600);
  }

  :global(.dark) .tag-selector div::-webkit-scrollbar-thumb:hover {
    background-color: var(--color-gray-500);
  }
</style>