<!-- src/lib/components/ui/Select.svelte -->
<script>
    /**
     * Select Component
     * A customizable select dropdown with support for option groups and multiple selection.
     */
    import { createEventDispatcher, onMount, tick } from 'svelte';
    import { fade } from 'svelte/transition';
    import { language } from '$lib/i18n';
    import Spinner from './Spinner.svelte';
    
    const dispatch = createEventDispatcher();
    
    // Props
    export let options = []; // Array of { value, label, disabled, group } objects
    export let groups = []; // Array of { id, label } objects for option groups
    export let value = ''; // Current value (string or array for multiple)
    export let name = ''; // Input name
    export let id = name || undefined; // Input ID, defaults to name
    export let label = undefined; // Input label
    export let placeholder = 'Select an option'; // Placeholder text
    export let disabled = false; // Disabled state
    export let readonly = false; // Readonly state
    export let required = false; // Required field
    export let error = undefined; // Error message
    export let helpText = undefined; // Help text below select
    export let loading = false; // Loading state
    export let searchable = false; // Enable search/filtering
    export let clearable = false; // Allow clearing selection
    export let multiple = false; // Allow multiple selections
    export let size = 'default'; // Size: sm, default, lg
    export let width = undefined; // Custom width
    export let maxHeight = '15rem'; // Max height of dropdown
    export let icon = undefined; // Custom icon component
    export let noOptionsMessage = 'No options available'; // Message when no options
    export let noResultsMessage = 'No results found'; // Message when search has no matches
    export let aria = {}; // Additional ARIA attributes
    
    // Internal state
    let open = false;
    let focused = false;
    let searchQuery = '';
    let highlightedIndex = -1;
    let selectElement;
    let dropdownElement;
    let searchInput;
    let optionsContainerElement;
    
    // RTL support
    $: isRTL = $language === 'ar';
    $: dir = isRTL ? 'rtl' : 'ltr';
    
    // Size classes
    $: sizeClasses = {
      sm: 'py-1.5 px-3 text-sm',
      default: 'py-2 px-4 text-base',
      lg: 'py-3 px-5 text-lg'
    }[size] || 'py-2 px-4 text-base';
    
    // Get current selection information
    $: selection = getSelection(value, options, multiple);
    
    // Filter and prepare options based on search query
    $: filteredOptions = options
      .filter(option => {
        if (!searchQuery) return true;
        return option.label.toLowerCase().includes(searchQuery.toLowerCase());
      })
      .map(option => ({
        ...option,
        // For ARIA and visual highlighting purposes
        highlighted: options[highlightedIndex] === option
      }));
    
    // Track if there are no options or no results for search
    $: hasNoOptions = options.length === 0;
    $: hasNoResults = searchQuery && filteredOptions.length === 0;
    
    // Group options by their group property
    $: groupedOptions = groupOptions(filteredOptions, groups);
    
    // Generate unique IDs for associated elements
    $: selectId = id || `select-${Math.random().toString(36).substring(2, 10)}`;
    $: listboxId = `${selectId}-listbox`;
    $: labelId = label ? `${selectId}-label` : undefined;
    $: errorId = error ? `${selectId}-error` : undefined;
    $: helpTextId = helpText ? `${selectId}-description` : undefined;
    
    // Calculate the aria-describedby attribute
    $: describedBy = [
      error && errorId ? errorId : null,
      helpText && helpTextId ? helpTextId : null,
    ].filter(Boolean).join(' ') || undefined;
    
    // Select button classes
    $: selectClasses = [
      "block w-full rounded-lg border transition-all duration-200 appearance-none",
      "bg-cosmos-bg text-cosmos-text",
      "border-cosmos-bg-light",
      "focus:outline-none",
      disabled || readonly ? "opacity-60 cursor-not-allowed" : "cursor-pointer",
      error ? "border-red-500 focus:border-red-500 focus:ring-red-500" : "focus:border-primary focus:ring-2 focus:ring-primary focus:ring-opacity-25",
      sizeClasses,
      "flex items-center justify-between"
    ].filter(Boolean).join(' ');
    
    // Dropdown container classes
    $: dropdownClasses = [
      "absolute mt-1 w-full rounded-lg",
      "bg-cosmos-bg shadow-lg border border-cosmos-bg-light",
      "z-50"
    ].filter(Boolean).join(' ');
    
    // Helper to get selection information
    function getSelection(value, options, isMultiple) {
      if (isMultiple) {
        // For multiple selection, return array of selected options
        const selectedValues = Array.isArray(value) ? value : [];
        return options.filter(option => selectedValues.includes(option.value));
      } else {
        // For single selection, return the selected option
        return options.find(option => option.value === value) || null;
      }
    }
    
    // Group options by their group property
    function groupOptions(options, groups) {
      if (!groups || groups.length === 0) {
        return { default: options };
      }
      
      const result = {};
      
      // Initialize groups
      groups.forEach(group => {
        result[group.id] = [];
      });
      
      // Add options to their groups
      options.forEach(option => {
        const groupId = option.group || 'default';
        if (!result[groupId]) {
          result[groupId] = [];
        }
        result[groupId].push(option);
      });
      
      return result;
    }
    
    // Toggle dropdown
    function toggleDropdown() {
      if (disabled || readonly) return;
      
      if (!open) {
        openDropdown();
      } else {
        closeDropdown();
      }
    }
    
    // Open dropdown
    async function openDropdown() {
      if (disabled || readonly) return;
      
      open = true;
      
      // Reset search and highlighted index
      searchQuery = '';
      highlightedIndex = -1;
      
      // Focus the search input if searchable
      await tick();
      if (searchable && searchInput) {
        searchInput.focus();
      }
      
      // Dispatch open event
      dispatch('open');
    }
    
    // Close dropdown
    function closeDropdown() {
      open = false;
      highlightedIndex = -1;
      
      // Focus the select button again
      if (selectElement) {
        selectElement.focus();
      }
      
      // Dispatch close event
      dispatch('close');
    }
    
    // Handle option selection
    function selectOption(option) {
      if (option.disabled) return;
      
      if (multiple) {
        // For multiple selection, toggle the option in the array
        const selectedValues = Array.isArray(value) ? [...value] : [];
        const index = selectedValues.indexOf(option.value);
        
        if (index === -1) {
          selectedValues.push(option.value);
        } else {
          selectedValues.splice(index, 1);
        }
        
        value = selectedValues;
      } else {
        // For single selection, set the value directly
        value = option.value;
        closeDropdown();
      }
      
      // Dispatch change event
      dispatch('change', { value });
    }
    
    // Clear selection
    function clearSelection(event) {
      event.stopPropagation();
      
      if (multiple) {
        value = [];
      } else {
        value = '';
      }
      
      // Dispatch change event
      dispatch('change', { value });
    }
    
    // Handle keyboard navigation
    function handleKeyDown(event) {
      if (disabled || readonly) return;
      
      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault();
          if (!open) {
            openDropdown();
          } else {
            // Navigate to next option
            highlightedIndex = Math.min(
              highlightedIndex + 1,
              filteredOptions.length - 1
            );
            scrollToHighlighted();
          }
          break;
          
        case 'ArrowUp':
          event.preventDefault();
          if (!open) {
            openDropdown();
          } else {
            // Navigate to previous option
            highlightedIndex = Math.max(highlightedIndex - 1, 0);
            scrollToHighlighted();
          }
          break;
          
        case 'Enter':
          event.preventDefault();
          if (!open) {
            openDropdown();
          } else if (highlightedIndex >= 0 && highlightedIndex < filteredOptions.length) {
            // Select the highlighted option
            selectOption(filteredOptions[highlightedIndex]);
          }
          break;
          
        case 'Escape':
          event.preventDefault();
          closeDropdown();
          break;
          
        case 'Tab':
          if (open) {
            closeDropdown();
          }
          break;
          
        default:
          // If searchable is enabled, the search input will handle typing
          // Otherwise, we could implement type-ahead search here
          break;
      }
    }
    
    // Scroll to the highlighted option
    function scrollToHighlighted() {
      if (!optionsContainerElement || highlightedIndex === -1) return;
      
      const highlightedOption = optionsContainerElement.querySelector('[data-highlighted="true"]');
      if (highlightedOption) {
        highlightedOption.scrollIntoView({
          block: 'nearest',
          inline: 'nearest'
        });
      }
    }
    
    // Check if an option is selected
    function isSelected(option) {
      if (multiple) {
        return Array.isArray(value) && value.includes(option.value);
      } else {
        return value === option.value;
      }
    }
    
    // Handle focus
    function handleFocus() {
      focused = true;
      dispatch('focus');
    }
    
    // Handle blur
    function handleBlur(event) {
      // Check if the related target is inside the component
      const isInsideComponent = 
        event.relatedTarget && 
        (event.relatedTarget === dropdownElement || 
         dropdownElement?.contains(event.relatedTarget));
      
      if (!isInsideComponent) {
        focused = false;
        
        // Close dropdown after a short delay to allow for clicking options
        setTimeout(() => {
          if (!focused) {
            closeDropdown();
          }
        }, 150);
        
        dispatch('blur');
      }
    }
    
    // Handle search input
    function handleSearch(event) {
      searchQuery = event.target.value;
      highlightedIndex = -1;
      dispatch('search', { query: searchQuery });
    }
    
    // Handle clicking outside the component
    function handleClickOutside(event) {
      if (open && 
          selectElement && 
          !selectElement.contains(event.target) && 
          dropdownElement && 
          !dropdownElement.contains(event.target)) {
        closeDropdown();
      }
    }
    
    // Format selected values for display
    function formatSelection() {
      if (multiple) {
        if (selection.length === 0) {
          return placeholder;
        } else if (selection.length === 1) {
          return selection[0].label;
        } else {
          return `${selection.length} items selected`;
        }
      } else {
        return selection ? selection.label : placeholder;
      }
    }
    
    onMount(() => {
      // Add document event listener for clicking outside
      document.addEventListener('mousedown', handleClickOutside);
      
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    });
  </script>
  
  <div class="relative" style={width ? `width: ${width}` : ''}>
    {#if label}
      <label 
        for={selectId} 
        id={labelId}
        class="block mb-1.5 text-sm font-medium text-cosmos-text"
      >
        {label} {#if required}<span class="text-error ml-0.5">*</span>{/if}
      </label>
    {/if}
    
    <!-- Select button -->
    <button
      bind:this={selectElement}
      type="button"
      id={selectId}
      aria-haspopup="listbox"
      aria-expanded={open}
      aria-controls={open ? listboxId : undefined}
      aria-labelledby={labelId}
      aria-describedby={describedBy}
      aria-invalid={error ? 'true' : 'false'}
      disabled={disabled || readonly}
      class={selectClasses}
      style={width ? `width: ${width}` : ''}
      on:click={toggleDropdown}
      on:keydown={handleKeyDown}
      on:focus={handleFocus}
      on:blur={handleBlur}
      {...aria}
    >
      <span class="flex-grow text-left overflow-hidden truncate" class:text-cosmos-text-muted={!selection || (Array.isArray(selection) && selection.length === 0)}>
        {#if loading}
          <Spinner size="sm" class="mr-2 inline-block" />
        {/if}
        
        {#if icon}
          <span class="mr-2">
            <svelte:component this={icon} size={18} />
          </span>
        {/if}
        
        {formatSelection()}
      </span>
      
      <div class="flex items-center ml-2">
        {#if clearable && ((multiple && value.length > 0) || (!multiple && value))}
          <button
            type="button"
            class="p-1 mr-1 text-cosmos-text-muted hover:text-cosmos-text"
            aria-label="Clear selection"
            on:click={clearSelection}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        {/if}
        
        <svg class={`h-5 w-5 text-cosmos-text-muted ${open ? 'transform rotate-180' : ''}`} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </div>
    </button>
    
    {#if error}
      <p id={errorId} class="mt-1.5 text-sm text-red-500">{error}</p>
    {:else if helpText}
      <p id={helpTextId} class="mt-1.5 text-sm text-cosmos-text-muted">{helpText}</p>
    {/if}
    
    <!-- Dropdown -->
    {#if open}
      <div 
        bind:this={dropdownElement}
        class={dropdownClasses}
        in:fade={{ duration: 150 }}
        dir={dir}
      >
        {#if searchable}
          <div class="p-2 border-b border-cosmos-bg-light">
            <input
              bind:this={searchInput}
              type="text"
              bind:value={searchQuery}
              placeholder="Search..."
              class="w-full p-2 text-sm rounded-md border border-cosmos-bg-light bg-cosmos-bg focus:outline-none focus:ring-1 focus:ring-primary"
              on:input={handleSearch}
              on:keydown={e => {
                // Prevent event bubbling for navigation keys
                if (['ArrowUp', 'ArrowDown', 'Enter', 'Escape'].includes(e.key)) {
                  e.stopPropagation();
                  handleKeyDown(e);
                }
              }}
            />
          </div>
        {/if}
        
        <div 
          id={listboxId}
          role="listbox"
          aria-multiselectable={multiple ? 'true' : undefined}
          tabindex="-1"
          class="py-1 max-h-[15rem] overflow-y-auto"
          style={maxHeight ? `max-height: ${maxHeight}` : ''}
          bind:this={optionsContainerElement}
          aria-activedescendant={highlightedIndex >= 0 && filteredOptions[highlightedIndex] ? `option-${filteredOptions[highlightedIndex].value}` : undefined}
        >
          {#if hasNoOptions}
            <div class="px-4 py-2 text-cosmos-text-muted text-sm">{noOptionsMessage}</div>
          {:else if hasNoResults}
            <div class="px-4 py-2 text-cosmos-text-muted text-sm">{noResultsMessage}</div>
          {:else}
            {#each Object.entries(groupedOptions) as [groupId, groupOptions]}
              {#if groupId !== 'default' && groups.length > 0}
                <!-- Group label -->
                <div class="px-3 py-1 text-xs font-semibold text-cosmos-text-muted">
                  {groups.find(g => g.id === groupId)?.label || groupId}
                </div>
              {/if}
              
              {#each groupOptions as option, index}
                <!-- Option item -->
                <div
                  id={`option-${option.value}`}
                  role="option"
                  class={`
                    px-4 py-2 cursor-pointer flex items-center
                    ${option.disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-cosmos-bg-light'}
                    ${isSelected(option) ? 'bg-primary bg-opacity-10 text-primary' : 'text-cosmos-text'}
                    ${option.highlighted ? 'bg-cosmos-bg-light' : ''}
                  `}
                  aria-selected={isSelected(option) ? 'true' : 'false'}
                  aria-disabled={option.disabled ? 'true' : undefined}
                  data-highlighted={option.highlighted ? 'true' : 'false'}
                  on:click={() => selectOption(option)}
                  on:mouseenter={() => { highlightedIndex = options.indexOf(option); }}
                >
                  {#if multiple}
                    <div class="mr-2 flex items-center justify-center">
                      {#if isSelected(option)}
                        <svg class="h-4 w-4 text-primary" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                        </svg>
                      {:else}
                        <div class="h-4 w-4 border border-cosmos-bg-light rounded"></div>
                      {/if}
                    </div>
                  {/if}
                  
                  <span class={option.class || ''}>
                    {#if option.icon}
                      <span class="mr-2">
                        <svelte:component this={option.icon} size={16} />
                      </span>
                    {/if}
                    {option.label}
                  </span>
                </div>
              {/each}
            {/each}
          {/if}
        </div>
      </div>
    {/if}
    
    <!-- Hidden native select for form submission -->
    {#if name}
      {#if multiple}
        <select 
          {name}
          hidden
          multiple
          {disabled}
          {required}
          aria-hidden="true"
        >
          {#each options as option}
            <option 
              value={option.value} 
              selected={Array.isArray(value) && value.includes(option.value)}
            >{option.label}</option>
          {/each}
        </select>
      {:else}
        <select 
          {name}
          hidden
          {disabled}
          {required}
          aria-hidden="true"
        >
          <option value="" disabled selected={!value}></option>
          {#each options as option}
            <option 
              value={option.value} 
              selected={value === option.value}
            >{option.label}</option>
          {/each}
        </select>
      {/if}
    {/if}
  </div>