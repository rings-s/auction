<!-- src/lib/components/ui/Dropdown.svelte -->
<script>
    import { createEventDispatcher, onMount, onDestroy } from 'svelte';
    import { fade } from 'svelte/transition';
  
    // Props with defaults
    export let items = []; // Array of items to display in dropdown
    export let value = null; // Current selected value
    export let placeholder = 'Select an option'; // Placeholder text
    export let label = ''; // Optional label above dropdown
    export let name = ''; // Form name
    export let id = ''; // Element ID
    export let disabled = false; // Whether dropdown is disabled
    export let required = false; // Whether dropdown is required in a form
    export let error = ''; // Error message
    export let fullWidth = false; // Whether dropdown should take full width
    export let size = 'md'; // xs, sm, md, lg
    export let variant = 'default'; // default, outline, underline
    export let align = 'left'; // Dropdown menu alignment: left, right
    export let allowSearch = false; // Allow filtering/searching items
    export let noResultsText = 'No results found'; // Text to show when no results match search
    export let customClass = ''; // Additional classes to apply
  
    // Internal state
    let isOpen = false;
    let searchValue = '';
    let filteredItems = [];
    let selectedItem = null;
    let dropdownRef;
    let inputRef;
    let menuRef;
    let highlightedIndex = -1;
  
    const dispatch = createEventDispatcher();
  
    // Apply size classes
    $: sizeClasses = {
      'xs': 'text-xs px-2 py-1',
      'sm': 'text-sm px-3 py-1.5',
      'md': 'text-base px-4 py-2',
      'lg': 'text-lg px-5 py-2.5'
    }[size] || 'text-base px-4 py-2';
  
    // Apply variant classes
    $: variantClasses = {
      'default': 'bg-white border border-primary-blue-200 focus:border-primary-blue focus:ring-2 focus:ring-primary-blue-200 rounded-md shadow-sm',
      'outline': 'bg-transparent border border-primary-blue-300 focus:border-primary-blue focus:ring-2 focus:ring-primary-blue-200 rounded-md',
      'underline': 'bg-transparent border-b border-primary-blue-200 focus:border-primary-blue focus:ring-0 rounded-none'
    }[variant] || 'bg-white border border-primary-blue-200 focus:border-primary-blue focus:ring-2 focus:ring-primary-blue-200 rounded-md shadow-sm';
  
    // Compute dropdown alignmnent
    $: alignClasses = align === 'right' ? 'right-0' : 'left-0';
  
    // Set width class
    $: widthClass = fullWidth ? 'w-full' : '';
  
    // When items prop changes, update filtered items
    $: {
      if (allowSearch && isOpen) {
        // Filter items based on search
        const searchTerm = searchValue.toLowerCase();
        filteredItems = items.filter(item => {
          const label = typeof item === 'object' ? (item.label || '').toLowerCase() : String(item).toLowerCase();
          return label.includes(searchTerm);
        });
      } else {
        // No filtering
        filteredItems = [...items];
      }
    }
  
    // Find selected item from value
    $: {
      if (value !== null && items.length > 0) {
        // If items are objects with value/label
        if (typeof items[0] === 'object' && 'value' in items[0]) {
          selectedItem = items.find(item => item.value === value) || null;
        } else {
          // If items are simple values
          selectedItem = value;
        }
      } else {
        selectedItem = null;
      }
    }
  
    // Get display text for current value
    $: displayText = getDisplayText();
  
    function getDisplayText() {
      if (selectedItem === null) return placeholder;
      
      if (typeof selectedItem === 'object' && 'label' in selectedItem) {
        return selectedItem.label;
      }
      
      return String(selectedItem);
    }
  
    // Handle click outside dropdown
    function handleClickOutside(event) {
      if (dropdownRef && !dropdownRef.contains(event.target)) {
        isOpen = false;
      }
    }
  
    // Handle item selection
    function selectItem(item) {
      const newValue = typeof item === 'object' && 'value' in item ? item.value : item;
      
      // Update selected value
      value = newValue;
      selectedItem = item;
      
      // Close dropdown
      isOpen = false;
      searchValue = '';
      
      // Dispatch change event
      dispatch('change', { value: newValue, item });
    }
  
    // Toggle dropdown
    function toggleDropdown() {
      if (!disabled) {
        isOpen = !isOpen;
        
        // If opening and search is enabled, focus the search input
        if (isOpen && allowSearch && inputRef) {
          setTimeout(() => {
            if (inputRef) inputRef.focus();
          }, 0);
        }
        
        // Reset search value when opening
        if (isOpen) {
          searchValue = '';
          highlightedIndex = -1;
        }
      }
    }
  
    // Handle keyboard navigation
    function handleKeydown(event) {
      if (!isOpen && (event.key === 'ArrowDown' || event.key === 'Enter' || event.key === ' ')) {
        // Open dropdown
        event.preventDefault();
        isOpen = true;
      } else if (isOpen) {
        switch (event.key) {
          case 'Escape':
            // Close dropdown
            event.preventDefault();
            isOpen = false;
            break;
            
          case 'ArrowDown':
            // Highlight next item
            event.preventDefault();
            if (highlightedIndex < filteredItems.length - 1) {
              highlightedIndex++;
              scrollHighlightedIntoView();
            }
            break;
            
          case 'ArrowUp':
            // Highlight previous item
            event.preventDefault();
            if (highlightedIndex > 0) {
              highlightedIndex--;
              scrollHighlightedIntoView();
            }
            break;
            
          case 'Enter':
            // Select highlighted item
            if (highlightedIndex >= 0 && highlightedIndex < filteredItems.length) {
              event.preventDefault();
              selectItem(filteredItems[highlightedIndex]);
            }
            break;
        }
      }
    }
  
    // Scroll highlighted item into view
    function scrollHighlightedIntoView() {
      setTimeout(() => {
        if (menuRef) {
          const highlightedEl = menuRef.querySelector(`[data-index="${highlightedIndex}"]`);
          if (highlightedEl) {
            highlightedEl.scrollIntoView({ block: 'nearest' });
          }
        }
      }, 0);
    }
  
    // Add event listeners on mount
    onMount(() => {
      document.addEventListener('click', handleClickOutside);
    });
  
    // Remove event listeners on destroy
    onDestroy(() => {
      document.removeEventListener('click', handleClickOutside);
    });
  </script>
  
  <div class="relative {widthClass} {customClass}" bind:this={dropdownRef}>
    <!-- Label -->
    {#if label}
      <label 
        for={id || name} 
        class="block text-sm font-medium text-text-dark mb-1"
      >
        {label}
        {#if required}
          <span class="text-red-500 ml-1">*</span>
        {/if}
      </label>
    {/if}
    
    <!-- Dropdown trigger -->
    <button
      type="button"
      class="{sizeClasses} {variantClasses} {widthClass} relative flex items-center justify-between cursor-pointer focus:outline-none transition-colors duration-200
        {isOpen ? 'ring-2 ring-primary-blue-200' : ''}
        {disabled ? 'opacity-60 cursor-not-allowed bg-gray-100' : 'hover:bg-gray-50'}
        {error ? 'border-red-500 focus:ring-red-200 focus:border-red-500' : ''}"
      id={id || name}
      aria-haspopup="listbox"
      aria-expanded={isOpen}
      on:click={toggleDropdown}
      on:keydown={handleKeydown}
      disabled={disabled}
      tabindex="0"
    >
      <span class="block truncate {!selectedItem ? 'text-text-light' : ''}">{displayText}</span>
      
      <svg 
        class="h-5 w-5 text-text-medium transition-transform duration-200 transform {isOpen ? 'rotate-180' : ''}" 
        xmlns="http://www.w3.org/2000/svg" 
        viewBox="0 0 20 20" 
        fill="currentColor" 
        aria-hidden="true"
      >
        <path 
          fill-rule="evenodd" 
          d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" 
          clip-rule="evenodd" 
        />
      </svg>
    </button>
    
    <!-- Error message -->
    {#if error}
      <p class="mt-1 text-sm text-red-600">{error}</p>
    {/if}
    
    <!-- Dropdown menu -->
    {#if isOpen}
      <div 
        class="absolute z-50 mt-1 {widthClass} {alignClasses} bg-white border border-primary-blue-200 rounded-md shadow-lg max-h-60 overflow-auto focus:outline-none"
        role="listbox"
        bind:this={menuRef}
        transition:fade={{ duration: 100 }}
      >
        <!-- Search input -->
        {#if allowSearch}
          <div class="sticky top-0 bg-white p-2 border-b border-primary-blue-100">
            <input
              type="text"
              bind:value={searchValue}
              placeholder="Search..."
              class="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-primary-blue focus:border-primary-blue"
              bind:this={inputRef}
            />
          </div>
        {/if}
        
        <!-- Items list -->
        <ul class="py-1">
          {#if filteredItems.length === 0}
            <li class="px-4 py-2 text-sm text-text-medium">{noResultsText}</li>
          {:else}
            {#each filteredItems as item, i}
              <!-- svelte-ignore a11y-click-events-have-key-events -->
              <li
                class="px-4 py-2 text-sm cursor-pointer hover:bg-primary-blue-50 flex items-center justify-between
                  {highlightedIndex === i ? 'bg-primary-blue-50' : ''}
                  {typeof item === 'object' && item.value === value ? 'bg-primary-blue-100 text-primary-blue font-medium' : ''}
                  {typeof item !== 'object' && item === value ? 'bg-primary-blue-100 text-primary-blue font-medium' : ''}"
                role="option"
                aria-selected={typeof item === 'object' ? item.value === value : item === value}
                on:click={() => selectItem(item)}
                on:mouseover={() => highlightedIndex = i}
                data-index={i}
              >
                <span class="truncate">
                  {typeof item === 'object' && 'label' in item ? item.label : item}
                </span>
                
                {#if (typeof item === 'object' && item.value === value) || (typeof item !== 'object' && item === value)}
                  <svg 
                    class="h-4 w-4 text-primary-blue" 
                    xmlns="http://www.w3.org/2000/svg" 
                    viewBox="0 0 20 20" 
                    fill="currentColor"
                  >
                    <path 
                      fill-rule="evenodd" 
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" 
                      clip-rule="evenodd" 
                    />
                  </svg>
                {/if}
              </li>
            {/each}
          {/if}
        </ul>
      </div>
    {/if}
    
    <!-- Hidden form field for form submission -->
    {#if name}
      <input 
        type="hidden" 
        {name} 
        value={value !== null ? value : ''} 
        {required}
      />
    {/if}
  </div>