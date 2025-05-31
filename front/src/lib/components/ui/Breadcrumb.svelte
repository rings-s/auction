<!-- src/lib/components/ui/Breadcrumb.svelte -->
<script>
  import { fly } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  
  export let items = [];
  export let class_ = '';
  export let size = 'default'; // 'small', 'default', 'large'
  export let showHome = true; // Whether to show a home icon for the first item
  
  // Get the "class" prop as "class_" because "class" is a reserved word in JavaScript
  export { class_ as class };
  
  // Determine text size based on the size prop
  $: textSize = {
    'small': 'text-xs',
    'default': 'text-sm',
    'large': 'text-base'
  }[size] || 'text-sm';
  
  // Determine spacing based on the size prop
  $: spacing = {
    'small': 'space-x-1 md:space-x-2',
    'default': 'space-x-2 md:space-x-3',
    'large': 'space-x-3 md:space-x-4'
  }[size] || 'space-x-2 md:space-x-3';
  
  // Determine icon size based on the size prop
  $: iconSize = {
    'small': 'h-3 w-3',
    'default': 'h-4 w-4',
    'large': 'h-5 w-5'
  }[size] || 'h-4 w-4';
</script>

<nav 
  class="relative flex w-full items-center overflow-x-auto py-3 px-1 scrollbar-none {class_}" 
  aria-label="Breadcrumb"
  transition:fly={{ y: -10, duration: 200, easing: quintOut }}
>
  <ol class="inline-flex w-full flex-nowrap items-center {spacing}">
    {#each items as item, index (item.href)}
      <li class="flex items-center whitespace-nowrap">
        {#if index > 0}
          <div class="mx-1.5 flex items-center text-gray-300 dark:text-gray-600" aria-hidden="true">
            <svg class="{iconSize}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </div>
        {/if}
        
        {#if index === 0 && showHome}
          <!-- Home icon for first item -->
          <div class="{index === 0 ? '' : 'ml-1.5'} mr-1 text-gray-500 dark:text-gray-400">
            <svg class="{iconSize}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
          </div>
        {/if}
        
        {#if item.active}
          <span 
            class="{textSize} font-medium text-gray-800 dark:text-gray-200" 
            aria-current="page"
          >
            {item.label}
          </span>
        {:else}
          <a 
            href={item.href} 
            class="{textSize} group relative font-medium text-primary-600 dark:text-primary-400 hover:text-primary-800 dark:hover:text-primary-300 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 rounded-md px-1 py-0.5"
          >
            <span class="relative z-10">{item.label}</span>
            <span class="absolute bottom-0 left-0 h-0.5 w-0 bg-primary-500 transition-all duration-200 group-hover:w-full"></span>
          </a>
        {/if}
      </li>
    {/each}
  </ol>
</nav>

<style>
  /* Hide scrollbar for webkit browsers */
  .scrollbar-none::-webkit-scrollbar {
    display: none;
  }
  
  /* Hide scrollbar for Firefox */
  .scrollbar-none {
    scrollbar-width: none;
  }
</style>