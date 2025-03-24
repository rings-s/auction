<!-- src/lib/components/ui/TabGroup.svelte -->
<script>
    /**
     * TabGroup Component
     * A comprehensive tabbed interface with multiple variants and accessibility features.
     */
    import { createEventDispatcher, setContext, onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import { fade, fly } from 'svelte/transition';
    
    const dispatch = createEventDispatcher();
    
    // Props
    export let tabs = []; // Array of tab objects: { id, label, icon, disabled, badge }
    export let activeTab = tabs.length > 0 ? tabs[0].id : null; // Active tab ID
    export let variant = 'underline'; // underline, pills, enclosed, soft, bordered
    export let size = 'md'; // sm, md, lg
    export let fullWidth = false; // Tabs take full width
    export let align = 'left'; // left, center, right, justify
    export let orientation = 'horizontal'; // horizontal, vertical
    export let contentAnimation = 'fade'; // fade, slide, none
    export let allowClosableTabs = false; // Allow tabs to be closed
    export let id = 'tab-group-' + Math.random().toString(36).substring(2, 9); // Unique ID
    export let ariaLabel = 'Tabs'; // ARIA label
    
    // Local state
    let contentContainer;
    let activeTabElement;
    let indicatorStyle = '';
    let tabListRef;
    
    // Create a reactive store for the active tab
    const activeTabStore = writable(activeTab);
    
    // Update store when activeTab prop changes
    $: activeTabStore.set(activeTab);
    
    // Size classes for tabs
    $: sizeClasses = {
      sm: 'text-sm py-1.5 px-3',
      md: 'text-base py-2 px-4',
      lg: 'text-lg py-2.5 px-5'
    }[size] || 'text-base py-2 px-4';
    
    // Align classes
    $: alignClasses = {
      left: 'justify-start',
      center: 'justify-center',
      right: 'justify-end',
      justify: 'justify-between'
    }[align] || 'justify-start';
    
    // Orientation classes
    $: orientationClasses = orientation === 'vertical' 
      ? 'flex-col' 
      : 'flex-row';
    
    // Tab list class based on variant and orientation
    $: tabListClasses = [
      'flex flex-wrap gap-1',
      orientationClasses,
      orientation === 'horizontal' ? alignClasses : '',
      variant === 'underline' ? 'border-b border-neutral-200 dark:border-neutral-700' : '',
      variant === 'bordered' ? 'border-b border-neutral-200 dark:border-neutral-700' : '',
      variant === 'enclosed' ? 'border-b border-neutral-200 dark:border-neutral-700' : '',
      fullWidth && orientation === 'horizontal' ? 'w-full' : '',
      fullWidth && orientation === 'vertical' ? 'h-full' : ''
    ].filter(Boolean).join(' ');
    
    // Tab item classes based on variant, state, and orientation
    function getTabClasses(tab) {
      const isActive = tab.id === activeTab;
      const disabled = tab.disabled;
      
      const baseClasses = [
        'relative flex items-center transition-all whitespace-nowrap',
        sizeClasses,
        disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer',
        isActive ? 'font-medium' : '',
        fullWidth && orientation === 'horizontal' ? 'flex-grow text-center justify-center' : '',
        fullWidth && orientation === 'vertical' ? 'w-full' : ''
      ];
      
      // Variant-specific styles
      if (variant === 'underline') {
        baseClasses.push(
          isActive 
            ? 'text-primary border-b-2 border-primary -mb-px' 
            : 'text-neutral-600 dark:text-neutral-400 border-b-2 border-transparent hover:text-neutral-900 dark:hover:text-white hover:border-neutral-300 dark:hover:border-neutral-700'
        );
      } else if (variant === 'pills') {
        baseClasses.push(
          isActive 
            ? 'bg-primary text-white rounded-md shadow-sm' 
            : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-md'
        );
      } else if (variant === 'enclosed') {
        baseClasses.push(
          isActive 
            ? 'bg-white dark:bg-neutral-800 border-t border-l border-r rounded-t-md text-neutral-900 dark:text-white border-neutral-200 dark:border-neutral-700 -mb-px' 
            : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white'
        );
      } else if (variant === 'soft') {
        baseClasses.push(
          isActive 
            ? 'bg-primary/10 text-primary rounded-md' 
            : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-md'
        );
      } else if (variant === 'bordered') {
        baseClasses.push(
          isActive 
            ? 'border border-neutral-200 dark:border-neutral-700 rounded-t-md -mb-px bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white' 
            : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white'
        );
      }
      
      return baseClasses.filter(Boolean).join(' ');
    }
    
    // Set context for child components (Tab)
    setContext('tabs', {
      activeTab: activeTabStore,
      registerTab: (id, element) => {
        // Logic to register a tab
        return {
          unregister: () => {
            // Logic to unregister a tab
          }
        };
      }
    });
    
    // Set active tab
    function setActiveTab(tabId, tab) {
      if (tab.disabled) return;
      
      if (activeTab !== tabId) {
        activeTab = tabId;
        activeTabStore.set(tabId);
        dispatch('change', { tabId, tab });
        
        updateIndicator();
      }
    }
    
    // Handle close tab
    function closeTab(event, tabId, tab) {
      event.stopPropagation();
      dispatch('close', { tabId, tab });
    }
    
    // Handle keyboard navigation
    function handleKeydown(event, tabIndex) {
      // Only handle navigation keys
      if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(event.key)) return;
      
      event.preventDefault();
      
      const enabledTabs = tabs.filter(t => !t.disabled);
      const currentIndex = enabledTabs.findIndex(t => t.id === activeTab);
      
      let nextIndex;
      
      if (orientation === 'horizontal') {
        if (event.key === 'ArrowLeft') {
          nextIndex = currentIndex > 0 ? currentIndex - 1 : enabledTabs.length - 1;
        } else if (event.key === 'ArrowRight') {
          nextIndex = currentIndex < enabledTabs.length - 1 ? currentIndex + 1 : 0;
        } else if (event.key === 'Home') {
          nextIndex = 0;
        } else if (event.key === 'End') {
          nextIndex = enabledTabs.length - 1;
        }
      } else {
        if (event.key === 'ArrowUp') {
          nextIndex = currentIndex > 0 ? currentIndex - 1 : enabledTabs.length - 1;
        } else if (event.key === 'ArrowDown') {
          nextIndex = currentIndex < enabledTabs.length - 1 ? currentIndex + 1 : 0;
        } else if (event.key === 'Home') {
          nextIndex = 0;
        } else if (event.key === 'End') {
          nextIndex = enabledTabs.length - 1;
        }
      }
      
      if (nextIndex !== undefined && enabledTabs[nextIndex]) {
        setActiveTab(enabledTabs[nextIndex].id, enabledTabs[nextIndex]);
        // Focus the new active tab
        document.getElementById(`tab-${enabledTabs[nextIndex].id}`)?.focus();
      }
    }
    
    // Update the indicator position
    function updateIndicator() {
      if (variant !== 'underline' || !activeTabElement || !tabListRef) return;
      
      if (orientation === 'horizontal') {
        const tabRect = activeTabElement.getBoundingClientRect();
        const listRect = tabListRef.getBoundingClientRect();
        
        indicatorStyle = `
          width: ${tabRect.width}px;
          transform: translateX(${tabRect.left - listRect.left}px);
        `;
      } else {
        const tabRect = activeTabElement.getBoundingClientRect();
        const listRect = tabListRef.getBoundingClientRect();
        
        indicatorStyle = `
          height: ${tabRect.height}px;
          transform: translateY(${tabRect.top - listRect.top}px);
        `;
      }
    }
    
    // Keep track of the active tab element
    function setActiveTabElement(element) {
      activeTabElement = element;
      updateIndicator();
    }
    
    onMount(() => {
      updateIndicator();
      
      // Add resize listener to update indicator on window resize
      const handleResize = () => {
        updateIndicator();
      };
      
      window.addEventListener('resize', handleResize);
      
      return () => {
        window.removeEventListener('resize', handleResize);
      };
    });
  </script>
  
  <div class={`tab-group ${orientation === 'vertical' ? 'flex' : ''}`} id={id} {...$$restProps}>
    <!-- Tab navigation -->
    <div 
      class={`tab-nav ${orientation === 'vertical' ? 'flex-shrink-0' : 'w-full'}`}
      role="tablist"
      aria-label={ariaLabel}
      bind:this={tabListRef}
    >
      <div class={tabListClasses}>
        {#each tabs as tab, i}
          <button
            type="button"
            id={`tab-${tab.id}`}
            class={getTabClasses(tab)}
            role="tab"
            aria-selected={tab.id === activeTab ? 'true' : 'false'}
            aria-controls={`tabpanel-${tab.id}`}
            tabindex={tab.id === activeTab ? 0 : -1}
            disabled={tab.disabled}
            on:click={() => setActiveTab(tab.id, tab)}
            on:keydown={(e) => handleKeydown(e, i)}
            use:setActiveTabElement={tab.id === activeTab}
          >
            {#if tab.icon}
              <span class={`${tab.label ? 'mr-2' : ''}`}>
                <svelte:component this={tab.icon} size={16} />
              </span>
            {/if}
            
            {tab.label}
            
            {#if tab.badge}
              <span class="ml-2 inline-flex items-center rounded-full bg-primary-50 px-2 py-1 text-xs font-medium text-primary-700 dark:bg-primary-900/30 dark:text-primary-400">
                {tab.badge}
              </span>
            {/if}
            
            {#if allowClosableTabs && !tab.disabled && !tab.permanent}
              <button
                type="button"
                class="ml-2 text-neutral-400 hover:text-neutral-700 dark:hover:text-white"
                aria-label={`Close ${tab.label} tab`}
                on:click={(e) => closeTab(e, tab.id, tab)}
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="h-4 w-4">
                  <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
                </svg>
              </button>
            {/if}
          </button>
        {/each}
        
        {#if variant === 'underline' && orientation === 'horizontal'}
          <div 
            class="absolute bottom-0 left-0 h-0.5 bg-primary transition-all duration-200"
            style={indicatorStyle}
            aria-hidden="true"
          ></div>
        {/if}
        
        {#if variant === 'underline' && orientation === 'vertical'}
          <div 
            class="absolute right-0 top-0 w-0.5 bg-primary transition-all duration-200"
            style={indicatorStyle}
            aria-hidden="true"
          ></div>
        {/if}
      </div>
    </div>
    
    <!-- Tab content -->
    <div 
      class={`tab-content mt-2 ${orientation === 'vertical' ? 'flex-grow ml-4' : ''}`}
      bind:this={contentContainer}
    >
      {#each tabs as tab}
        <div
          id={`tabpanel-${tab.id}`}
          role="tabpanel"
          aria-labelledby={`tab-${tab.id}`}
          class="outline-none"
          tabindex="0"
          hidden={tab.id !== activeTab}
        >
          {#if tab.id === activeTab}
            {#if contentAnimation === 'fade'}
              <div in:fade={{ duration: 150 }}>
                <slot name={tab.id} {tab}></slot>
              </div>
            {:else if contentAnimation === 'slide'}
              <div in:fly={{ y: 5, duration: 150 }}>
                <slot name={tab.id} {tab}></slot>
              </div>
            {:else}
              <slot name={tab.id} {tab}></slot>
            {/if}
          {/if}
        </div>
      {/each}
    </div>
  </div>