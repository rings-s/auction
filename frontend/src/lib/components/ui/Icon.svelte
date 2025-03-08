<!-- src/lib/components/ui/Icon.svelte -->
<script>
    // Icon component to standardize icon usage across the application
    // Uses Lucide icons
  
    export let name = '';
    export let size = 'default'; // options: xs, sm, default, lg, xl
    export let strokeWidth = 2;
    
    // Allows passing additional Tailwind classes
    let className = '';
    export { className as class };
  
    // Size map
    const sizeMap = {
      xs: 'w-3 h-3',
      sm: 'w-4 h-4',
      default: 'w-5 h-5',
      lg: 'w-6 h-6',
      xl: 'w-8 h-8'
    };
  
    // Get size class or use default if invalid
    const sizeClass = sizeMap[size] || sizeMap.default;
  
    // Common class for all icons
    $: combinedClass = `inline-block ${sizeClass} ${className}`;
  </script>
  
  {#if name === 'plus'}
    <svg xmlns="http://www.w3.org/2000/svg" class={combinedClass} width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width={strokeWidth} stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 5v14M5 12h14"/>
    </svg>
  {:else if name === 'x-circle'}
    <svg xmlns="http://www.w3.org/2000/svg" class={combinedClass} width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width={strokeWidth} stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <path d="m15 9-6 6M9 9l6 6"/>
    </svg>
  {:else if name === 'search'}
    <svg xmlns="http://www.w3.org/2000/svg" class={combinedClass} width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width={strokeWidth} stroke-linecap="round" stroke-linejoin="round">
      <circle cx="11" cy="11" r="8"/>
      <path d="m21 21-4.3-4.3"/>
    </svg>
  {:else if name === 'alert-triangle'}
    <svg xmlns="http://www.w3.org/2000/svg" class={combinedClass} width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width={strokeWidth} stroke-linecap="round" stroke-linejoin="round">
      <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
      <path d="M12 9v4"/>
      <path d="M12 17h.01"/>
    </svg>
  {:else if name === 'refresh-cw'}
    <svg xmlns="http://www.w3.org/2000/svg" class={combinedClass} width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width={strokeWidth} stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 2v6h-6"/>
      <path d="M3 12a9 9 0 0 1 15-6.7L21 8"/>
      <path d="M3 22v-6h6"/>
      <path d="M21 12a9 9 0 0 1-15 6.7L3 16"/>
    </svg>
  {:else if name === 'package'}
    <svg xmlns="http://www.w3.org/2000/svg" class={combinedClass} width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width={strokeWidth} stroke-linecap="round" stroke-linejoin="round">
      <path d="M16.5 9.4 7.55 4.24"/>
      <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
      <path d="M3.29 7 12 12l8.71-5"/>
      <path d="M12 22V12"/>
    </svg>
  {:else if name === 'filter-x'}
    <svg xmlns="http://www.w3.org/2000/svg" class={combinedClass} width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width={strokeWidth} stroke-linecap="round" stroke-linejoin="round">
      <path d="M13.013 3H2l8 9.46V19l4 2v-8.54l.9-1.055"/>
      <path d="m22 3-5 5"/>
      <path d="m17 3 5 5"/>
    </svg>
  {:else if name === 'chevron-left'}
    <svg xmlns="http://www.w3.org/2000/svg" class={combinedClass} width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width={strokeWidth} stroke-linecap="round" stroke-linejoin="round">
      <path d="m15 18-6-6 6-6"/>
    </svg>
  {:else if name === 'chevron-right'}
    <svg xmlns="http://www.w3.org/2000/svg" class={combinedClass} width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width={strokeWidth} stroke-linecap="round" stroke-linejoin="round">
      <path d="m9 18 6-6-6-6"/>
    </svg>
  {:else}
    <!-- Fallback for unknown icons -->
    <span class={combinedClass}>
      <span class="sr-only">Icon</span>
    </span>
  {/if}