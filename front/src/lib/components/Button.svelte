<!-- src/lib/components/Button.svelte -->
<script>
    // Props
    export let variant = 'primary'; // 'primary', 'secondary', 'outline', 'danger', 'success'
    export let size = 'default'; // 'small', 'default', 'large'
    export let type = 'button'; // 'button', 'submit', 'reset'
    export let disabled = false;
    export let loading = false;
    export let fullWidth = false;
    export let href = null; // If set, renders an <a> tag instead of button
    export let onClick = () => {}; // For regular buttons
    export let class_ = ''; // Custom class
    
    // Export "class" prop as "class_" because "class" is a reserved word
    export { class_ as class };
    
    // Define variant classes
    const variants = {
      primary: `bg-primary-600 hover:bg-primary-700 focus:ring-primary-500 text-white dark:bg-primary-500 dark:hover:bg-primary-600 dark:text-gray-900`,
      secondary: `bg-secondary-600 hover:bg-secondary-700 focus:ring-secondary-500 text-white dark:bg-secondary-500 dark:hover:bg-secondary-600 dark:text-gray-900`,
      outline: `bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:ring-primary-500`,
      danger: `bg-danger-600 hover:bg-danger-700 focus:ring-danger-500 text-white dark:bg-danger-500 dark:hover:bg-danger-600 dark:text-gray-900`,
      success: `bg-success-600 hover:bg-success-700 focus:ring-success-500 text-white dark:bg-success-500 dark:hover:bg-success-600 dark:text-gray-900`
    };
    
    // Define size classes
    const sizes = {
      small: 'px-2.5 py-1.5 text-xs',
      default: 'px-4 py-2 text-sm',
      large: 'px-6 py-3 text-base'
    };
    
    // Generate final class string
    $: buttonClass = `
      ${sizes[size] || sizes.default}
      ${variants[variant] || variants.primary}
      ${fullWidth ? 'w-full' : ''}
      font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2
      transition-colors duration-200
      ${disabled || loading ? 'opacity-50 cursor-not-allowed' : 'transform hover:-translate-y-0.5'}
      ${class_}
    `;
  </script>
  
  {#if href}
    <a
      {href}
      class={buttonClass}
      class:pointer-events-none={disabled}
      aria-disabled={disabled}
    >
      {#if loading}
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      {/if}
      <slot></slot>
    </a>
  {:else}
    <button
      {type}
      {disabled}
      on:click={onClick}
      class={buttonClass}
    >
      {#if loading}
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      {/if}
      <slot></slot>
    </button>
  {/if}