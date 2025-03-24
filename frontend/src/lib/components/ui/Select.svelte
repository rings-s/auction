<!-- src/lib/components/ui/Select.svelte -->
<script>
  /**
   * Select Component
   * A flexible select dropdown with advanced features like search, multi-select, and option groups.
   */
  import { createEventDispatcher, onMount, tick } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  
  const dispatch = createEventDispatcher();
  
  // Props
  export let value = ''; // Current value (string or array for multiple)
  export let options = []; // Array of option objects: { value, label, disabled, group, icon }
  export let groups = []; // Array of option group objects: { id, label }
  export let name = ''; // Input name
  export let id = name || `select-${Math.random().toString(36).substring(2, 9)}`; // Input ID
  export let label = ''; // Label text
  export let placeholder = 'Select an option'; // Placeholder text
  export let disabled = false; // Disabled state
  export let readonly = false; // Read-only state
  export let required = false; // Required field
  export let error = ''; // Error message
  export let helpText = ''; // Help text
  export let loading = false; // Loading state
  export let clearable = false; // Show clear button
  export let searchable = false; // Enable search
  export let multiple = false; // Allow multiple selections
  export let size = 'md'; // sm, md, lg
  export let variant = 'outline'; // outline, filled, flushed, unstyled
  export let rounded = 'md'; // none, sm, md, lg, full
  export let leadingIcon = undefined; // Icon component to show at the start
  export let noOptionsMessage = 'No options available'; // Message when no options
  export let noResultsMessage = 'No results found'; // Message when search has no matches
  export let closeOnSelect = !multiple; // Close dropdown when an option is selected
  export let maxHeight = '15rem'; // Max height of dropdown
  export let tabIndex = 0; // Tab index
  export let creatable = false; // Allow creating new options
  export let createOptionLabel = 'Create'; // Label for create option
  export let onCreate = undefined; // Function to call when creating a new option
  export let maxItems = undefined; // Maximum number of selectable items (multiple mode)
  export let formatSelectedText = undefined; // Function to format selected text display
  export let customOptionRenderer = undefined; // Custom function to render options
  
  // Local state
  let open = false;
  let searchQuery = '';
  let highlightedIndex = -1;
  let containerElement;
  let inputElement;
  let dropdownElement;
  let optionsListElement;
  let isTouched = false;
  let isComposing = false; // For IME composition
  
  // Store original tab index before disabling
  let originalTabIndex = tabIndex;
  
  // Size classes
  $: sizeClasses = {
    sm: 'h-8 text-sm',
    md: 'h-10 text-base',
    lg: 'h-12 text-lg'
  }[size] || 'h-10 text-base';
  
  // Text size based on container size
  $: textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  }[size] || 'text-base';
  
  // Padding classes based on icon
  $: paddingClasses = leadingIcon
    ? size === 'sm' ? 'pl-8 pr-3' : size === 'lg' ? 'pl-12 pr-4' : 'pl-10 pr-4'
    : size === 'sm' ? 'px-3' : size === 'lg' ? 'px-5' : 'px-4';
  
  // Border radius classes
  $: roundedClasses = {
    none: 'rounded-none',
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    full: 'rounded-full'
  }[rounded] || 'rounded-md';
  
  // Get variant classes
  $: variantClasses = {
    outline: `border border-neutral-300 dark:border-neutral-700 bg-transparent ${open ? 'border-primary ring-2 ring-primary/20' : ''}`,
    filled: `border border-transparent bg-neutral-100 dark:bg-neutral-800 ${open ? 'border-primary ring-2 ring-primary/20' : ''}`,
    flushed: `border-b border-neutral-300 dark:border-neutral-700 rounded-none ${open ? 'border-primary' : ''}`,
    unstyled: 'border-none shadow-none'
  }[variant] || 'border border-neutral-300 dark:border-neutral-700 bg-transparent';
  
  // Container classes
  $: containerClasses = [
    'relative w-full transition-colors duration-200',
    disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer',
    error ? 'border-error' : '',
  ].filter(Boolean).join(' ');
  
  // Dropdown trigger classes
  $: triggerClasses = [
    'flex w-full items-center justify-between',
    sizeClasses,
    roundedClasses,
    variantClasses,
    paddingClasses,
    disabled ? 'bg-neutral-50 dark:bg-neutral-900 cursor-not-allowed' : 'cursor-pointer',
    error ? 'border-error focus:ring-error/20 focus:border-error' : ''
  ].filter(Boolean).join(' ');
  
  // Normalized value for internal use
  $: internalValue = multiple ? (Array.isArray(value) ? value : []) : value;
  
  // Get selected option(s)
  $: selectedOptions = multiple
    ? options.filter(option => internalValue.includes(option.value))
    : options.find(option => option.value === internalValue);
  
  // Filter options based on search query
  $: filteredOptions = options
    .filter(option => {
      if (!searchQuery) return true;
      return option.label.toLowerCase().includes(searchQuery.toLowerCase());
    })
    .map((option, index) => ({
      ...option,
      highlighted: index === highlightedIndex
    }));
  
  // Group options by their group property
  $: groupedOptions = prepareGroupedOptions(filteredOptions);
  
  // Track if there are no options or no results for search
  $: hasNoOptions = options.length === 0;
  $: hasNoResults = searchQuery && filteredOptions.length === 0;
  
  // Check if "create option" should be shown
  $: showCreateOption = creatable && 
                      searchQuery && 
                      filteredOptions.length === 0 && 
                      !options.some(opt => opt.label.toLowerCase() === searchQuery.toLowerCase());
  
  // Format display text for selected value(s)
  $: displayText = formatDisplayText(selectedOptions, internalValue, placeholder);
  
  // Check if the max number of items is reached
  $: maxItemsReached = multiple && maxItems && internalValue.length >= maxItems;
  
  // Group options by their group property
  function prepareGroupedOptions(options) {
    if (!groups || groups.length === 0) {
      return { default: options };
    }
    
    const result = {};
    
    // Initialize groups
    groups.forEach(group => {
      result[group.id] = [];
    });
    
    // Add a default group for items without a group
    result.default = [];
    
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
  
  // Format the display text for the select button
  function formatDisplayText(selected, currentValue, placeholder) {
    if (formatSelectedText && (selected || (multiple && currentValue.length > 0))) {
      return formatSelectedText(selected, currentValue);
    }
    
    if (multiple) {
      if (!Array.isArray(currentValue) || currentValue.length === 0) {
        return placeholder;
      }
      
      if (currentValue.length === 1) {
        const option = options.find(opt => opt.value === currentValue[0]);
        return option ? option.label : placeholder;
      }
      
      return `${currentValue.length} item${currentValue.length !== 1 ? 's' : ''} selected`;
    } else {
      if (!selected) return placeholder;
      return selected.label;
    }
  }
  
  // Toggle dropdown open/closed
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
    searchQuery = '';
    highlightedIndex = -1;
    
    // Focus search input if searchable
    await tick();
    if (searchable && inputElement) {
      inputElement.focus();
    }
    
    dispatch('open');
  }
  
  // Close dropdown
  function closeDropdown() {
    if (!open) return;
    
    open = false;
    searchQuery = '';
    
    // Restore focus to container
    if (containerElement) {
      containerElement.focus();
    }
    
    dispatch('close');
  }
  
  // Handle selecting an option
  function selectOption(option) {
    if (option.disabled) return;
    
    if (multiple) {
      // Toggle selection for multi-select
      const index = internalValue.indexOf(option.value);
      if (index === -1) {
        // Check max items constraint
        if (maxItems && internalValue.length >= maxItems) {
          dispatch('maxItems', { max: maxItems });
          return;
        }
        
        value = [...internalValue, option.value];
      } else {
        value = [...internalValue.slice(0, index), ...internalValue.slice(index + 1)];
      }
    } else {
      // Single select
      value = option.value;
    }
    
    isTouched = true;
    dispatch('change', { value });
    
    if (closeOnSelect && !multiple) {
      closeDropdown();
    }
  }
  
  // Handle creating a new option
  function createOption() {
    if (!searchQuery || !creatable) return;
    
    // Call the onCreate handler if provided
    if (onCreate) {
      const newOption = onCreate(searchQuery);
      if (newOption) {
        if (multiple) {
          value = [...internalValue, newOption.value];
        } else {
          value = newOption.value;
        }
        
        dispatch('change', { value });
        dispatch('create', { option: newOption });
        
        if (closeOnSelect) {
          closeDropdown();
        }
      }
    } else {
      // Default behavior: create a simple option with value = label
      const newOption = { value: searchQuery, label: searchQuery };
      options = [...options, newOption];
      
      if (multiple) {
        value = [...internalValue, newOption.value];
      } else {
        value = newOption.value;
      }
      
      dispatch('change', { value });
      dispatch('create', { option: newOption });
      
      if (closeOnSelect) {
        closeDropdown();
      }
    }
    
    searchQuery = '';
  }
  
  // Clear the selection
  function clearSelection() {
    value = multiple ? [] : '';
    isTouched = true;
    dispatch('change', { value });
    dispatch('clear');
  }
  
  // Handle keyboard navigation
  function handleKeydown(event) {
    if (disabled || readonly || isComposing) return;
    
    // Don't handle keypresses during IME composition
    if (event.isComposing) return;
    
    switch (event.key) {
      case 'Enter':
        if (open) {
          event.preventDefault();
          
          if (showCreateOption) {
            createOption();
            return;
          }
          
          if (highlightedIndex >= 0 && highlightedIndex < filteredOptions.length) {
            selectOption(filteredOptions[highlightedIndex]);
          }
        } else {
          toggleDropdown();
        }
        break;
        
      case ' ': // Space key
        if (!searchable || !open) {
          event.preventDefault();
          toggleDropdown();
        }
        break;
        
      case 'ArrowDown':
        if (open) {
          event.preventDefault();
          if (filteredOptions.length > 0) {
            highlightedIndex = (highlightedIndex + 1) % filteredOptions.length;
            scrollToHighlighted();
          }
        } else {
          toggleDropdown();
        }
        break;
        
      case 'ArrowUp':
        if (open) {
          event.preventDefault();
          if (filteredOptions.length > 0) {
            highlightedIndex = (highlightedIndex - 1 + filteredOptions.length) % filteredOptions.length;
            scrollToHighlighted();
          }
        } else {
          toggleDropdown();
        }
        break;
        
      case 'Escape':
        if (open) {
          event.preventDefault();
          closeDropdown();
        }
        break;
        
      case 'Tab':
        if (open) {
          closeDropdown();
        }
        break;
        
      case 'Backspace':
        if (multiple && internalValue.length > 0 && !searchQuery && open) {
          // Remove the last selected item when pressing backspace
          const newValue = [...internalValue];
          newValue.pop();
          value = newValue;
          dispatch('change', { value });
        }
        break;
    }
  }
  
  // Handle search input
  function handleSearch(event) {
    searchQuery = event.target.value;
    highlightedIndex = -1;
    dispatch('search', { query: searchQuery });
  }
  
  // Scroll to highlighted option
  function scrollToHighlighted() {
    if (!optionsListElement || highlightedIndex === -1) return;
    
    const highlightedOption = optionsListElement.querySelector('[data-highlighted="true"]');
    if (highlightedOption) {
      highlightedOption.scrollIntoView({
        block: 'nearest',
        inline: 'nearest'
      });
    }
  }
  
  // Handle click outside to close dropdown
  function handleClickOutside(event) {
    if (!containerElement) return;
    
    if (open && 
        !containerElement.contains(event.target) &&
        (!dropdownElement || !dropdownElement.contains(event.target))) {
      closeDropdown();
    }
  }
  
  // Handle composition events for IME input
  function handleCompositionStart() {
    isComposing = true;
  }
  
  function handleCompositionEnd() {
    isComposing = false;
  }
  
  // Check if an option is selected
  function isSelected(option) {
    if (multiple) {
      return internalValue.includes(option.value);
    } else {
      return option.value === internalValue;
    }
  }
  
  // Remove a specific selected item (for multi-select tags)
  function removeItem(itemValue, event) {
    if (event) {
      event.stopPropagation();
    }
    
    if (multiple) {
      const index = internalValue.indexOf(itemValue);
      if (index !== -1) {
        const newValue = [...internalValue.slice(0, index), ...internalValue.slice(index + 1)];
        value = newValue;
        dispatch('change', { value });
      }
    }
  }
  
  // Focus handling
  function handleFocus() {
    dispatch('focus');
  }
  
  function handleBlur() {
    if (!open) {
      isTouched = true;
      dispatch('blur');
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

<div class="w-full mb-4" bind:this={containerElement}>
  {#if label}
    <label 
      for={id} 
      class="block mb-1.5 text-sm font-medium text-neutral-700 dark:text-neutral-200"
    >
      {label} {#if required}<span class="text-error">*</span>{/if}
    </label>
  {/if}
  
  <div class={containerClasses}>
    <!-- Main select button/control -->
    <div
      {id}
      class={triggerClasses}
      tabindex={disabled ? -1 : originalTabIndex}
      role="combobox"
      aria-controls={`${id}-listbox`}
      aria-expanded={open}
      aria-haspopup="listbox"
      aria-disabled={disabled}
      aria-readonly={readonly}
      aria-required={required}
      aria-invalid={!!error}
      aria-label={label}
      on:click={toggleDropdown}
      on:keydown={handleKeydown}
      on:focus={handleFocus}
      on:blur={handleBlur}
      data-error={!!error}
    >
      <!-- Leading icon -->
      {#if leadingIcon}
        <div class={`absolute left-0 flex items-center justify-center pointer-events-none text-neutral-500 dark:text-neutral-400 
          ${size === 'sm' ? 'w-8' : size === 'lg' ? 'w-12' : 'w-10'}`}>
          <svelte:component this={leadingIcon} size={size === 'sm' ? 16 : size === 'lg' ? 24 : 20} />
        </div>
      {/if}
      
      <!-- Display selected value(s) or placeholder -->
      <div class="flex-grow overflow-hidden flex items-center">
        {#if multiple && Array.isArray(internalValue) && internalValue.length > 0}
          <div class="flex flex-wrap gap-1 max-w-full overflow-hidden">
            {#each internalValue as itemValue, i (itemValue)}
              {#if i < 3 || !open}
                {@const option = options.find(opt => opt.value === itemValue)}
                {#if option}
                  <div class="inline-flex items-center py-0.5 px-2 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-800 dark:text-primary-200 text-sm">
                    {#if option.icon}
                      <svelte:component this={option.icon} size={14} class="mr-1" />
                    {/if}
                    <span class="truncate max-w-[100px]">{option.label}</span>
                    <button
                      type="button"
                      class="ml-1 focus:outline-none text-primary-600 dark:text-primary-400 hover:text-primary-800 dark:hover:text-primary-200"
                      aria-label={`Remove ${option.label}`}
                      on:click={(e) => removeItem(itemValue, e)}
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </div>
                {/if}
              {:else if i === 3 && !open}
                <div class="inline-flex items-center py-0.5 px-2 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 text-sm">
                  +{internalValue.length - 3} more
                </div>
              {/if}
            {/each}
          </div>
        {:else}
          <div class={`truncate ${!selectedOptions ? 'text-neutral-500 dark:text-neutral-400' : ''}`}>
            {displayText}
          </div>
        {/if}
      </div>
      
      <div class="flex items-center ml-2">
        {#if loading}
          <div class="mr-2 animate-spin h-4 w-4 border-2 border-neutral-500 border-t-transparent rounded-full"></div>
        {/if}
        
        {#if clearable && (multiple ? internalValue.length > 0 : internalValue) && !disabled && !readonly}
          <button
            type="button"
            class="p-1 text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-300 focus:outline-none"
            aria-label="Clear selection"
            on:click|stopPropagation={clearSelection}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        {/if}
        
        <div class="pointer-events-none ml-1">
          <svg xmlns="http://www.w3.org/2000/svg" class={`h-5 w-5 text-neutral-400 transition-transform duration-200 ${open ? 'transform rotate-180' : ''}`} viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>
    </div>
    
    <!-- Dropdown menu -->
    {#if open}
      <div
        bind:this={dropdownElement}
        class="absolute z-50 mt-1 w-full bg-white dark:bg-neutral-800 shadow-lg rounded-md border border-neutral-200 dark:border-neutral-700 overflow-hidden"
        transition:fly={{ duration: 150, y: 8 }}
      >
        {#if searchable}
          <div class="p-2 border-b border-neutral-200 dark:border-neutral-700">
            <div class="relative">
              <input
                type="text"
                bind:this={inputElement}
                bind:value={searchQuery}
                placeholder="Search..."
                class="w-full h-9 px-3 py-2 text-sm bg-neutral-50 dark:bg-neutral-700 border border-neutral-200 dark:border-neutral-600 rounded-md focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
                on:input={handleSearch}
                on:keydown={handleKeydown}
                on:compositionstart={handleCompositionStart}
                on:compositionend={handleCompositionEnd}
              />
              {#if searchQuery}
                <button
                  type="button"
                  class="absolute right-2 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-300"
                  on:click={() => { searchQuery = ''; }}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </button>
              {:else}
                <div class="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
                  </svg>
                </div>
              {/if}
            </div>
          </div>
        {/if}
        
        <!-- Options list -->
        <div
          id={`${id}-listbox`}
          bind:this={optionsListElement}
          role="listbox"
          aria-multiselectable={multiple ? 'true' : undefined}
          class="max-h-60 overflow-y-auto p-1"
          style={maxHeight ? `max-height: ${maxHeight}` : ''}
          aria-activedescendant={highlightedIndex >= 0 ? `${id}-option-${highlightedIndex}` : undefined}
          tabindex="-1"
        >
          {#if hasNoOptions}
            <div class="px-3 py-2 text-sm text-neutral-500 dark:text-neutral-400">
              {noOptionsMessage}
            </div>
          {:else if hasNoResults}
            <div class="px-3 py-2 text-sm text-neutral-500 dark:text-neutral-400">
              {noResultsMessage}
            </div>
          {:else}
            {#each Object.entries(groupedOptions) as [groupId, groupOptions]}
              {#if groupId !== 'default' && groups.length > 0 && groupOptions.length > 0}
                <div class="px-3 py-1 text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                  {groups.find(g => g.id === groupId)?.label || groupId}
                </div>
              {/if}
              
              {#each groupOptions as option, index}
                {#if customOptionRenderer}
                  {@const renderedOption = customOptionRenderer(option, {
                    selected: isSelected(option),
                    highlighted: option.highlighted,
                    disabled: option.disabled,
                    handleSelect: () => selectOption(option)
                  })}
                  
                  <!-- Custom option rendering -->
                  <div 
                    id={`${id}-option-${option.highlighted ? highlightedIndex : index}`}
                    role="option"
                    aria-selected={isSelected(option) ? 'true' : 'false'}
                    aria-disabled={option.disabled ? 'true' : 'false'}
                    data-highlighted={option.highlighted ? 'true' : 'false'}
                    on:click={() => !option.disabled && selectOption(option)}
                    on:mouseenter={() => { highlightedIndex = filteredOptions.indexOf(option); }}
                  >
                    {@html renderedOption}
                  </div>
                {:else}
                  <!-- Default option rendering -->
                  <div
                    id={`${id}-option-${option.highlighted ? highlightedIndex : index}`}
                    role="option"
                    class={`px-3 py-2 text-sm flex items-center cursor-pointer rounded-md ${option.highlighted ? 'bg-neutral-100 dark:bg-neutral-700' : ''} 
                      ${isSelected(option) ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300' : 'text-neutral-700 dark:text-neutral-200'} 
                      ${option.disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-neutral-100 dark:hover:bg-neutral-700'}`}
                    aria-selected={isSelected(option) ? 'true' : 'false'}
                    aria-disabled={option.disabled ? 'true' : 'false'}
                    data-highlighted={option.highlighted ? 'true' : 'false'}
                    on:click={() => !option.disabled && selectOption(option)}
                    on:mouseenter={() => { highlightedIndex = filteredOptions.indexOf(option); }}
                  >
                    {#if multiple}
                      <div class="mr-2 flex items-center justify-center h-5 w-5">
                        {#if isSelected(option)}
                          <svg class="h-5 w-5 text-primary-600 dark:text-primary-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                          </svg>
                        {/if}
                      </div>
                    {/if}
                    
                    {#if option.icon}
                      <div class="mr-2 text-neutral-500 dark:text-neutral-400">
                        <svelte:component this={option.icon} size={18} />
                      </div>
                    {/if}
                    
                    <span class="truncate">{option.label}</span>
                    
                    {#if maxItemsReached && multiple && !isSelected(option)}
                      <span class="ml-auto text-xs text-neutral-500 dark:text-neutral-400">Max items reached</span>
                    {/if}
                  </div>
                {/if}
              {/each}
            {/each}
          {/if}
          
          {#if showCreateOption}
            <div
              role="option"
              class="px-3 py-2 text-sm flex items-center cursor-pointer rounded-md bg-neutral-50 dark:bg-neutral-750 hover:bg-neutral-100 dark:hover:bg-neutral-700 text-primary-700 dark:text-primary-300"
              on:click={createOption}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" />
              </svg>
              {createOptionLabel} "{searchQuery}"
            </div>
          {/if}
        </div>
      </div>
    {/if}
    
    {#if error}
      <p id={`${id}-error`} class="mt-1.5 text-sm text-error">
        {error}
      </p>
    {:else if helpText}
      <p id={`${id}-helptext`} class="mt-1.5 text-sm text-neutral-500 dark:text-neutral-400">
        {helpText}
      </p>
    {/if}
  </div>
  
  <!-- Hidden native select for form submission -->
  {#if name}
    {#if multiple}
      <select {name} multiple hidden disabled={disabled} required={required}>
        {#each options as option}
          <option 
            value={option.value} 
            selected={Array.isArray(internalValue) && internalValue.includes(option.value)}
          >{option.label}</option>
        {/each}
      </select>
    {:else}
      <select {name} hidden disabled={disabled} required={required}>
        <option value="" disabled selected={!internalValue}></option>
        {#each options as option}
          <option 
            value={option.value} 
            selected={internalValue === option.value}
          >{option.label}</option>
        {/each}
      </select>
    {/if}
  {/if}
</div>