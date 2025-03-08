<!-- src/lib/components/ui/TabGroup.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    
    // Props
    export let tabs = []; // Array of {id, label, icon (optional), count (optional)}
    export let activeTab = '';
    export let variant = 'underline'; // underline, pills, boxed, default
    export let fullWidth = false;
    export let centered = false;
    
    // Event dispatcher
    const dispatch = createEventDispatcher();
    
    // Handle tab change
    function setActiveTab(tabId) {
      activeTab = tabId;
      dispatch('tabChange', { tabId });
      
      if (typeof onTabChange === 'function') {
        onTabChange(tabId);
      }
    }
    
    // Setup tab change callback function
    export let onTabChange = null;
    
    // Determine if a tab is active
    $: isActive = (tabId) => activeTab === tabId;
    
    // Determine tab styles based on variant
    $: variantStyles = getVariantStyles(variant);
    
    function getVariantStyles(variant) {
      switch (variant) {
        case 'pills':
          return {
            tabList: 'space-x-2 border-b-0',
            tab: 'px-4 py-2 rounded-full text-sm font-medium transition-colors',
            active: 'bg-primary-blue/20 text-secondary-blue',
            inactive: 'text-text-medium hover:text-text-dark hover:bg-neutral-100'
          };
        case 'boxed':
          return {
            tabList: 'border-b border-primary-blue/20',
            tab: 'px-4 py-2 text-sm font-medium transition-colors rounded-t-lg',
            active: 'bg-white text-secondary-blue border border-primary-blue/20 border-b-white',
            inactive: 'text-text-medium hover:text-text-dark bg-primary-blue/5 hover:bg-primary-blue/10 border border-transparent'
          };
        case 'default':
          return {
            tabList: 'border-b border-primary-blue/20',
            tab: 'px-4 py-2 text-sm font-medium transition-colors',
            active: 'text-secondary-blue border-b-2 border-secondary-blue',
            inactive: 'text-text-medium hover:text-text-dark border-b-2 border-transparent'
          };
        case 'underline':
        default:
          return {
            tabList: 'border-b border-primary-blue/20',
            tab: 'px-4 py-2 text-sm font-medium transition-colors border-b-2 border-transparent -mb-px',
            active: 'text-secondary-blue border-b-2 border-secondary-blue',
            inactive: 'text-text-medium hover:text-text-dark hover:border-primary-blue/30'
          };
      }
    }
    
    // Tab width class
    $: widthClass = fullWidth ? 'w-full' : '';
    
    // Alignment class
    $: alignmentClass = centered ? 'justify-center' : 'justify-start';
  </script>
  
  <div class="tabs-container">
    <!-- Tab list -->
    <div class="{variantStyles.tabList} {alignmentClass} flex overflow-x-auto scrollbar-hide">
      {#each tabs as tab (tab.id)}
        <button
          class="tab-button {variantStyles.tab} {isActive(tab.id) ? variantStyles.active : variantStyles.inactive} {widthClass}"
          aria-selected={isActive(tab.id)}
          role="tab"
          id={`tab-${tab.id}`}
          on:click={() => setActiveTab(tab.id)}
        >
          {#if tab.icon}
            <span class="tab-icon mr-2">
              {#if typeof tab.icon === 'string'}
                {@html tab.icon}
              {:else}
                <svelte:component this={tab.icon} />
              {/if}
            </span>
          {/if}
          <span>{tab.label}</span>
          
          {#if tab.count !== undefined}
            <span class="ml-2 px-1.5 py-0.5 text-xs rounded-full bg-primary-blue/20 text-secondary-blue">
              {tab.count}
            </span>
          {/if}
        </button>
      {/each}
    </div>
  </div>
  
  <style>
    /* Hide scrollbar for tab list */
    .scrollbar-hide {
      -ms-overflow-style: none;  /* IE and Edge */
      scrollbar-width: none;  /* Firefox */
    }
    
    .scrollbar-hide::-webkit-scrollbar {
      display: none; /* Chrome, Safari, Opera */
    }
    
    /* Tab transition effects */
    .tab-button {
      position: relative;
      overflow: hidden;
    }
    
    .tab-button::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 50%;
      transform: translateX(-50%);
      width: 0;
      height: 2px;
      background-color: var(--secondary-blue);
      transition: width 0.3s ease;
    }
    
    .tab-button:hover::after {
      width: 60%;
    }
    
    /* Active tab glow effect */
    .tab-button[aria-selected="true"] {
      position: relative;
    }
    
    .tab-button[aria-selected="true"]::before {
      content: '';
      position: absolute;
      bottom: -2px;
      left: 50%;
      transform: translateX(-50%);
      width: 30%;
      height: 2px;
      background-color: var(--secondary-blue);
      filter: blur(4px);
      opacity: 0.6;
    }
  </style>