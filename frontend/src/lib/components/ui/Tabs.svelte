<!-- src/lib/components/ui/Tabs.svelte -->
<script>
    /**
     * Tabs Component
     * Creates a tabbed interface with support for different variants.
     */
    import { createEventDispatcher, setContext, onMount } from 'svelte';
    
    const dispatch = createEventDispatcher();
    
    // Props
    export let tabs = []; // Array of tab objects: { id, label, icon, disabled }
    export let activeTab = tabs.length > 0 ? tabs[0].id : null; // Active tab ID
    export let variant = 'default'; // default, pills, underline, minimal
    export let fullWidth = false; // Tabs take full container width
    export let size = 'default'; // sm, default, lg
    export let align = 'left'; // left, center, right
    export let ariaLabel = "Tabs"; // Accessibility label
    
    let tabsElement;
    let initialized = false;
    
    // Size classes
    $: sizeClasses = {
      sm: 'text-sm',
      default: 'text-base',
      lg: 'text-lg'
    }[size] || 'text-base';
    
    // Alignment classes
    $: alignClasses = {
      left: 'justify-start',
      center: 'justify-center',
      right: 'justify-end'
    }[align] || 'justify-start';
    
    // Tab list classes based on variant
    $: tabListClasses = [
      'flex border-b border-cosmos-bg-light',
      alignClasses,
      variant === 'underline' ? 'border-b border-cosmos-bg-light' : '',
      variant === 'pills' ? 'border-none space-x-1 rtl:space-x-reverse' : '',
      variant === 'minimal' ? 'border-none' : '',
    ].filter(Boolean).join(' ');
    
    // Function to set active tab
    function setActiveTab(tabId) {
      if (activeTab !== tabId) {
        activeTab = tabId;
        dispatch('change', { tabId });
      }
    }
    
    // Set tab context for child components
    setContext('tabs', {
      registerPanel: (panel) => {
        // Handle panel registration logic
        return {
          activeTab,
          setActiveTab
        };
      }
    });
    
    // Get tab button classes based on state and variant
    function getTabClasses(tab) {
      const isActive = activeTab === tab.id;
      const isDisabled = tab.disabled;
      
      // Base classes for all variants
      const baseClasses = [
        'inline-flex items-center py-3 px-4 font-medium',
        sizeClasses, 
        isDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
        fullWidth ? 'flex-grow text-center justify-center' : '',
      ];
      
      // Variant-specific classes
      if (variant === 'default') {
        baseClasses.push(
          'border-b-2 -mb-[2px]',
          isActive 
            ? 'text-primary border-primary' 
            : 'text-cosmos-text-muted border-transparent hover:text-cosmos-text hover:border-cosmos-text-muted'
        );
      } else if (variant === 'pills') {
        baseClasses.push(
          'rounded-lg',
          isActive 
            ? 'bg-primary text-white' 
            : 'text-cosmos-text-muted hover:text-cosmos-text hover:bg-cosmos-bg-light'
        );
      } else if (variant === 'underline') {
        baseClasses.push(
          'border-b-2 -mb-[2px]',
          isActive 
            ? 'text-primary border-primary' 
            : 'text-cosmos-text-muted border-transparent hover:text-cosmos-text'
        );
      } else if (variant === 'minimal') {
        baseClasses.push(
          isActive 
            ? 'text-primary' 
            : 'text-cosmos-text-muted hover:text-cosmos-text'
        );
      }
      
      return baseClasses.filter(Boolean).join(' ');
    }
    
    onMount(() => {
      initialized = true;
    });
  </script>
  
  <div class="w-full" {...$$restProps}>
    <div class="tabs-header" role="tablist" aria-label={ariaLabel} bind:this={tabsElement}>
      <div class={tabListClasses}>
        {#each tabs as tab, i}
          <button
            type="button"
            role="tab"
            class={getTabClasses(tab)}
            id={`tab-${tab.id}`}
            aria-selected={activeTab === tab.id ? 'true' : 'false'}
            aria-controls={`tabpanel-${tab.id}`}
            tabindex={activeTab === tab.id ? 0 : -1}
            disabled={tab.disabled}
            on:click={() => !tab.disabled && setActiveTab(tab.id)}
            on:keydown={(e) => {
              // Handle keyboard navigation
              if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                e.preventDefault();
                const dir = e.key === 'ArrowLeft' ? -1 : 1;
                const enabledTabs = tabs.filter(t => !t.disabled);
                const currentIndex = enabledTabs.findIndex(t => t.id === activeTab);
                if (currentIndex !== -1) {
                  const nextIndex = (currentIndex + dir + enabledTabs.length) % enabledTabs.length;
                  setActiveTab(enabledTabs[nextIndex].id);
                  document.getElementById(`tab-${enabledTabs[nextIndex].id}`)?.focus();
                }
              }
            }}
          >
            {#if tab.icon}
              <span class="mr-2 rtl:mr-0 rtl:ml-2">
                <svelte:component this={tab.icon} size={16} />
              </span>
            {/if}
            {tab.label}
          </button>
        {/each}
      </div>
    </div>
    
    <div class="tabs-content">
      <slot {activeTab} />
    </div>
  </div>