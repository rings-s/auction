<!-- src/lib/components/Tabs.svelte -->
<script>
    import { onMount, createEventDispatcher } from 'svelte';
    
    // Props
    export let tabs = []; // Array of tab objects: {id, label, disabled, icon}
    export let activeTab = undefined; // Active tab ID
    export let variant = 'default'; // 'default', 'pills', 'underline', 'minimal'
    export let size = 'default'; // 'small', 'default', 'large'
    export let fullWidth = false; // Whether tabs should take full width
    export let centered = false; // Whether tabs should be centered
    export let vertical = false; // Whether tabs should be vertical
    export let iconPosition = 'left'; // 'left', 'right', 'top', 'none'
    export let allowNone = false; // Whether all tabs can be deselected
    export let class_ = ''; // Additional classes
    
    export { class_ as class };
    
    const dispatch = createEventDispatcher();
    
    // Set default activeTab if none provided
    onMount(() => {
      if (activeTab === undefined && tabs.length > 0) {
        activeTab = tabs[0].id;
      }
    });
    
    // Function to handle tab selection
    function selectTab(tab) {
      if (tab.disabled) return;
      
      // If allowing deselection and clicking on already active tab
      if (allowNone && tab.id === activeTab) {
        activeTab = undefined;
      } else {
        activeTab = tab.id;
      }
      
      dispatch('change', { id: activeTab });
    }
    
    // Style variants
    $: variantClass = {
      default: 'border-b border-gray-200 dark:border-gray-700',
      pills: 'space-x-1 md:space-x-2',
      underline: 'border-b border-gray-200 dark:border-gray-700',
      minimal: ''
    }[variant] || '';
    
    // Size variants
    $: sizeClass = {
      small: 'text-xs',
      default: 'text-sm',
      large: 'text-base'
    }[size] || 'text-sm';
    
    // Tab item styles based on variant, size, active state, and disabled state
    function getTabItemClass(tab) {
      const isActive = tab.id === activeTab;
      
      // Base classes by variant
      const baseVariantClass = {
        default: `px-4 py-2 font-medium rounded-t-lg ${
          isActive 
            ? 'text-primary-600 bg-white dark:bg-gray-800 dark:text-primary-400 border-primary-600 dark:border-primary-400 border-b-2'
            : 'text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:border-gray-600 border-transparent border-b-2'
        }`,
        
        pills: `px-3 py-1.5 font-medium rounded-full ${
          isActive 
            ? 'text-white bg-primary-600 dark:bg-primary-500 dark:text-gray-900 shadow-sm'
            : 'text-gray-600 bg-gray-100 hover:bg-gray-200 dark:text-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600'
        }`,
        
        underline: `px-4 py-2 font-medium ${
          isActive 
            ? 'text-primary-600 dark:text-primary-400 border-primary-600 dark:border-primary-400 border-b-2'
            : 'text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:border-gray-600 border-transparent border-b-2'
        }`,
        
        minimal: `px-3 py-1.5 font-medium ${
          isActive 
            ? 'text-primary-600 dark:text-primary-400'
            : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
        }`
      }[variant] || '';
      
      // Size adjustments - already in baseVariantClass
      
      // Disabled state
      const disabledClass = tab.disabled 
        ? 'opacity-50 cursor-not-allowed'
        : 'cursor-pointer';
      
      // Full width adjustment
      const widthClass = fullWidth && !vertical
        ? 'flex-1 text-center'
        : '';
      
      return `${baseVariantClass} ${disabledClass} ${widthClass} transition-all duration-200`;
    }
  </script>
  
  <div 
    class="tabs {vertical ? 'flex' : 'block'} {class_}"
    role="tablist"
    aria-orientation={vertical ? 'vertical' : 'horizontal'}
  >
    <div 
      class="
        {vertical ? 'flex flex-col space-y-1' : 'flex flex-wrap'}
        {variantClass}
        {sizeClass}
        {centered && !vertical ? 'justify-center' : ''}
        {fullWidth && !vertical ? 'w-full' : ''}
      "
    >
      {#each tabs as tab (tab.id)}
        <button
          type="button"
          role="tab"
          class={getTabItemClass(tab)}
          id={`tab-${tab.id}`}
          aria-selected={tab.id === activeTab ? 'true' : 'false'}
          aria-controls={`panel-${tab.id}`}
          tabindex={tab.id === activeTab ? 0 : -1}
          disabled={tab.disabled || false}
          on:click={() => selectTab(tab)}
        >
          {#if tab.icon && (iconPosition === 'left' || iconPosition === 'top')}
            <span 
              class={`
                ${iconPosition === 'left' ? 'mr-2 inline-block' : 'block mb-1 mx-auto'}
              `}
            >
              {@html tab.icon}
            </span>
          {/if}
          
          <span class={iconPosition === 'top' ? 'block' : 'inline'}>
            {tab.label}
          </span>
          
          {#if tab.icon && iconPosition === 'right'}
            <span class="ml-2 inline-block">
              {@html tab.icon}
            </span>
          {/if}
          
          {#if tab.count !== undefined}
            <span 
              class="
                ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium
                {tab.id === activeTab
                  ? 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200'
                  : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'}
              "
            >
              {tab.count}
            </span>
          {/if}
        </button>
      {/each}
    </div>
  </div>
  
  <style>
    .tabs {
      position: relative;
      --tab-transition: 200ms ease-in-out;
    }
    
    button[role="tab"] {
      position: relative;
      outline: none;
      white-space: nowrap;
      transition: var(--tab-transition);
    }
    
    /* Focus styles */
    button[role="tab"]:focus-visible {
      outline: 2px solid var(--color-primary-500);
      outline-offset: 2px;
    }
    
    /* For overflow tabs, add horizontal scrolling */
    @media (max-width: 768px) {
      .tabs:not(.vertical) .flex:not(.flex-col) {
        overflow-x: auto;
        scrollbar-width: none;  /* For Firefox */
        -ms-overflow-style: none;  /* For Internet Explorer and Edge */
        white-space: nowrap;
      }
      
      .tabs:not(.vertical) .flex:not(.flex-col)::-webkit-scrollbar {
        display: none;  /* For Chrome, Safari and Opera */
      }
    }
  </style>