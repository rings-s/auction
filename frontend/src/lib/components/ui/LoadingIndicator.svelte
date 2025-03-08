src/lib/components/ui/LoadingIndicator.svelte


<script>
    // Props with defaults
    export let size = 'md'; // 'sm', 'md', 'lg'
    export let color = 'primary'; // 'primary', 'secondary', 'gray', 'white'
    export let type = 'spinner'; // 'spinner', 'dots', 'pulse'
    export let text = ''; // Optional loading text
    export let textPosition = 'right'; // 'right', 'bottom', 'left', 'top'
    export let fullPage = false; // Whether to display as overlay covering the full page
    export let transparent = false; // Whether background should be transparent (when fullPage is true)
    export let inline = false; // Whether to display as an inline element (respects text flow)
    
    // Size mappings
    const sizeClasses = {
      sm: {
        spinner: 'h-4 w-4',
        dots: 'h-1.5 w-1.5 mx-0.5',
        pulse: 'h-3 w-3 mx-1',
        wrapper: 'text-sm',
      },
      md: {
        spinner: 'h-8 w-8',
        dots: 'h-2.5 w-2.5 mx-1',
        pulse: 'h-5 w-5 mx-1.5',
        wrapper: 'text-base',
      },
      lg: {
        spinner: 'h-12 w-12',
        dots: 'h-3.5 w-3.5 mx-1.5',
        pulse: 'h-7 w-7 mx-2',
        wrapper: 'text-lg',
      }
    };
    
    // Color mappings
    const colorClasses = {
      primary: 'text-primary-blue',
      secondary: 'text-secondary-blue',
      gray: 'text-gray-500',
      white: 'text-white',
    };
    
    // Get size class based on component type
    function getSizeClass() {
      return sizeClasses[size]?.[type] || sizeClasses.md[type];
    }
    
    // Get color class
    function getColorClass() {
      return colorClasses[color] || colorClasses.primary;
    }
    
    // Wrapper classes based on position
    function getWrapperClasses() {
      let classes = `${sizeClasses[size]?.wrapper || sizeClasses.md.wrapper} ${getColorClass()}`;
      
      if (fullPage) {
        // Full page overlay
        classes += ' fixed inset-0 flex items-center justify-center z-50';
        
        if (!transparent) {
          classes += ' bg-black bg-opacity-20';
        }
      } else if (inline) {
        // Inline display
        classes += ' inline-flex items-center';
      } else {
        // Normal block
        classes += ' flex items-center';
      }
      
      // Add gap and adjust direction based on text position
      if (text) {
        if (textPosition === 'bottom') {
          classes += ' flex-col gap-2';
        } else if (textPosition === 'top') {
          classes += ' flex-col-reverse gap-2'; 
        } else if (textPosition === 'left') {
          classes += ' flex-row-reverse gap-3';
        } else {
          // Default: right
          classes += ' flex-row gap-3';
        }
      }
      
      return classes;
    }
  </script>
  
  <div class={getWrapperClasses()} role="status" aria-live="polite">
    {#if type === 'spinner'}
      <svg 
        class={`animate-spin ${getSizeClass()}`} 
        xmlns="http://www.w3.org/2000/svg" 
        fill="none" 
        viewBox="0 0 24 24"
      >
        <circle 
          class="opacity-25" 
          cx="12" 
          cy="12" 
          r="10" 
          stroke="currentColor" 
          stroke-width="4"
        ></circle>
        <path 
          class="opacity-75" 
          fill="currentColor" 
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
    {:else if type === 'dots'}
      <div class="flex">
        {#each Array(3) as _, i}
          <div 
            class={`rounded-full ${getSizeClass()} animate-pulse`} 
            style={`background-color: currentColor; animation-delay: ${i * 150}ms;`}
          ></div>
        {/each}
      </div>
    {:else if type === 'pulse'}
      <div class="flex">
        {#each Array(3) as _, i}
          <div 
            class={`rounded-full ${getSizeClass()} animate-pulse`}
            style={`background-color: currentColor; animation-delay: ${i * 150}ms; opacity: ${0.6 + (i * 0.2)};`}
          ></div>
        {/each}
      </div>
    {/if}
    
    {#if text}
      <span>{text}</span>
    {/if}
    
    <!-- For screen readers -->
    <span class="sr-only">Loading{text ? `: ${text}` : ''}</span>
  </div>