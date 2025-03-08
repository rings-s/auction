<!-- src/lib/components/ui/Tabs.svelte -->
<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import { fade } from 'svelte/transition';
  
  // Props
  export let tabs = [];
  export let activeTab = '';
  export let variant = 'default'; // default, pills, underline, boxed
  export let fullWidth = false;
  export let centered = false;
  export let tabClass = '';
  export let contentClass = '';
  export let minHeight = ''; // Optional min-height for tab content to reduce layout shift
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // Initialize active tab if not provided
  onMount(() => {
    if (!activeTab && tabs.length > 0) {
      activeTab = tabs[0].id;
    }
  });
  
  // Switch active tab
  function setActiveTab(tabId) {
    activeTab = tabId;
    dispatch('tabChange', { tabId });
  }
  
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
      case 'underline':
        return {
          tabList: 'border-b border-primary-blue/20',
          tab: 'px-4 py-2 text-sm font-medium transition-colors border-b-2 border-transparent -mb-px',
          active: 'text-secondary-blue border-b-2 border-secondary-blue',
          inactive: 'text-text-medium hover:text-text-dark hover:border-primary-blue/30'
        };
      case 'boxed':
        return {
          tabList: 'border-b border-primary-blue/20',
          tab: 'px-4 py-2 text-sm font-medium transition-colors rounded-t-lg',
          active: 'bg-white text-secondary-blue border border-primary-blue/20 border-b-white',
          inactive: 'text-text-medium hover:text-text-dark bg-primary-blue/5 hover:bg-primary-blue/10 border border-transparent'
        };
      case 'default':
      default:
        return {
          tabList: 'border-b border-primary-blue/20',
          tab: 'px-4 py-2 text-sm font-medium transition-colors',
          active: 'text-secondary-blue border-b-2 border-secondary-blue',
          inactive: 'text-text-medium hover:text-text-dark border-b-2 border-transparent'
        };
    }
  }
  
  // Tab width class
  $: widthClass = fullWidth ? 'w-full' : '';
  
  // Alignment class
  $: alignmentClass = centered ? 'justify-center' : 'justify-start';
  
  // Generate content style including min-height if provided
  $: contentStyle = minHeight ? `min-height: ${minHeight};` : '';
</script>

<div class="tabs-container" class:overflow-hidden={variant === 'boxed'} class:rounded-lg={variant === 'boxed'}>
<!-- Tab list -->
<div class="tab-list {variantStyles.tabList} {alignmentClass} flex overflow-x-auto scrollbar-hide" role="tablist">
  {#each tabs as tab, index (tab.id)}
    <button
      class="tab-button {variantStyles.tab} {isActive(tab.id) ? variantStyles.active : variantStyles.inactive} {widthClass} {tabClass}"
      aria-selected={isActive(tab.id)}
      role="tab"
      id={`tab-${tab.id}`}
      aria-controls={`tabpanel-${tab.id}`}
      tabindex={isActive(tab.id) ? 0 : -1}
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

<!-- Tab content with min-height to prevent layout shift -->
<div class="tab-content {contentClass}" style={contentStyle}>
  {#key activeTab}
    <div
      role="tabpanel"
      id={`tabpanel-${activeTab}`}
      aria-labelledby={`tab-${activeTab}`}
      tabindex="0"
      in:fade={{ duration: 150 }}
    >
      <slot />
    </div>
  {/key}
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

/* Add transition for smoother content fade */
.tab-content {
  position: relative;
}
</style>