<!-- src/lib/components/ui/Breadcrumb.svelte -->
<script>
    /**
     * Breadcrumb Component
     * Displays a navigation breadcrumb trail with home icon support.
     */
    import { language } from '$lib/i18n';
    
    // Props
    export let items = []; // Array of breadcrumb items { label, href, active }
    export let showHomeIcon = true; // Display home icon for first item
    export let separator = "/"; // Breadcrumb separator
    export let ariaLabel = "Breadcrumb"; // Accessibility label
    
    // Check RTL for separator direction
    $: isRTL = $language === 'ar';
  </script>
  
  <nav aria-label={ariaLabel} class="flex" {...$$restProps}>
    <ol class="inline-flex items-center space-x-1 md:space-x-2 rtl:space-x-reverse">
      {#each items as item, i}
        <li class="inline-flex items-center">
          {#if i > 0}
            <span class="mx-1.5 text-cosmos-text-muted" aria-hidden="true">
              {separator}
            </span>
          {/if}
          
          {#if item.href && !item.active}
            <a 
              href={item.href} 
              class={`inline-flex items-center text-sm font-medium transition-colors 
                    ${item.active ? 'text-cosmos-text cursor-default' : 'text-cosmos-text-muted hover:text-primary'}`}
              aria-current={item.active ? 'page' : undefined}
            >
              {#if i === 0 && showHomeIcon}
                <svg class="w-4 h-4 mr-2 rtl:mr-0 rtl:ml-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path>
                </svg>
              {/if}
              {item.label}
            </a>
          {:else}
            <span 
              class={`inline-flex items-center text-sm font-medium 
                    ${item.active ? 'text-cosmos-text' : 'text-cosmos-text-muted'}`}
              aria-current={item.active ? 'page' : undefined}
            >
              {#if i === 0 && showHomeIcon}
                <svg class="w-4 h-4 mr-2 rtl:mr-0 rtl:ml-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path>
                </svg>
              {/if}
              {item.label}
            </span>
          {/if}
        </li>
      {/each}
    </ol>
  </nav>