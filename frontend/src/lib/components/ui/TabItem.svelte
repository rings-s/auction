<!-- src/lib/components/ui/TabItem.svelte -->
<script>
    /**
     * TabItem Component
     * Individual tab panel to be used with the Tabs component.
     */
    import { getContext, onMount } from 'svelte';
    
    // Props
    export let id; // Tab panel ID (must match ID in tabs array)
    export let keepAlive = false; // Keep DOM content when inactive
    export let lazyLoad = true; // Only render content when tab becomes active at least once
    export let padding = true; // Add padding to tab panel
    
    // Get tabs context info
    const { activeTab } = getContext('tabs');
    
    // Track if this tab has ever been active
    let hasBeenActive = false;
    
    // Check if panel should be visible
    $: isActive = $activeTab === id;
    $: hasBeenActive = hasBeenActive || isActive;
    $: shouldRender = keepAlive || isActive;
    $: shouldShowContent = (!lazyLoad || hasBeenActive) && shouldRender;
  
    // CSS classes
    $: panelClasses = [
      padding ? 'py-4' : '',
      isActive ? 'block' : 'hidden',
    ].filter(Boolean).join(' ');
    
    // Handle transition between tabs
    $: if (isActive) {
      hasBeenActive = true;
    }
    
    onMount(() => {
      if (isActive) {
        hasBeenActive = true;
      }
    });
  </script>
  
  <div
    id={`tabpanel-${id}`}
    role="tabpanel"
    aria-labelledby={`tab-${id}`}
    tabindex="0"
    class={panelClasses}
    hidden={!isActive}
  >
    {#if shouldShowContent}
      <slot />
    {/if}
  </div>