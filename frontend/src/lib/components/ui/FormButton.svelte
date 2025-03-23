<!-- src/lib/components/ui/FormButton.svelte -->
<script>
    export let type = 'button';
    export let variant = 'primary'; // primary, secondary, outline, ghost, link
    export let size = 'md'; // sm, md, lg
    export let disabled = false;
    export let loading = false;
    export let fullWidth = false;
    export let onClick = () => {};
    export let className = '';
    
    // Variants
    const variants = {
      primary: 'bg-primary hover:bg-primary-dark text-white border-transparent',
      secondary: 'bg-neutral-800 hover:bg-neutral-900 text-white border-transparent',
      outline: 'bg-transparent hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-800 dark:text-white border-neutral-300 dark:border-neutral-700',
      ghost: 'bg-transparent hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-800 dark:text-white border-transparent',
      danger: 'bg-error hover:bg-error/90 text-white border-transparent',
      link: 'bg-transparent hover:underline text-primary dark:text-primary-300 border-transparent px-0 py-0',
      success: 'bg-success hover:bg-success/90 text-white border-transparent',
    };
    
    // Sizes
    const sizes = {
      sm: 'text-xs py-1.5 px-3',
      md: 'text-sm py-2.5 px-4',
      lg: 'text-base py-3 px-6'
    };
    
    // Icon sizes based on button size
    const iconSizes = {
      sm: 'w-3.5 h-3.5',
      md: 'w-4 h-4',
      lg: 'w-5 h-5'
    };
  </script>
  
  <button
    {type}
    disabled={disabled || loading}
    on:click={onClick}
    class="relative inline-flex items-center justify-center rounded-xl font-medium border transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary/25 disabled:opacity-60 disabled:cursor-not-allowed
      {variants[variant]}
      {sizes[size]}
      {fullWidth ? 'w-full' : ''}
      {className}"
    on:click
  >
    {#if loading}
      <svg
        class="animate-spin {iconSizes[size]} mr-2"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        />
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    {/if}
    <slot />
  </button>