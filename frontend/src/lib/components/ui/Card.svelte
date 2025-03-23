<!-- src/lib/components/ui/Card.svelte -->
<script>
  /**
   * Card Component
   * A container component with various styles and configurations.
   */
    
  // Props
  export let title = undefined; // Optional card title
  export let subtitle = undefined; // Optional card subtitle
  export let hover = false; // Hover effects
  export let bordered = true; // Show border
  export let padding = true; // Add padding
  export let variant = 'default'; // default, glass
  export let elevation = 'md'; // none, sm, md, lg, xl
  export let clickable = false; // Makes the entire card clickable and adds focus styles
  
  // Generate CSS classes based on props
  $: hoverClass = hover ? 'hover:border-primary transition-all duration-200' : '';
  $: borderClass = bordered ? 'border border-cosmos-bg-light' : '';
  $: paddingClass = padding ? 'p-5' : '';
  
  // Variant classes
  $: variantClass = variant === 'glass' 
    ? 'bg-cosmos-bg-dark bg-opacity-40 backdrop-blur-lg' 
    : 'bg-cosmos-bg-dark';
  
  // Shadow elevation
  $: shadowClass = {
    'none': '',
    'sm': 'shadow-sm',
    'md': 'shadow-md',
    'lg': 'shadow-lg',
    'xl': 'shadow-xl'
  }[elevation] || 'shadow-md';
  
  // Clickable card classes
  $: clickableClass = clickable 
    ? 'cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-50' 
    : '';
</script>

<div 
  class="rounded-xl {shadowClass} {variantClass} {borderClass} {hoverClass} {paddingClass} {clickableClass}" 
  role={clickable ? 'button' : undefined}
  tabindex={clickable ? 0 : undefined}
  on:click={clickable ? (event) => { if ($$props.onClick) $$props.onClick(event); } : undefined}
  on:keydown={clickable ? (event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); if ($$props.onClick) $$props.onClick(event); } } : undefined}
  {...$$restProps}
>
  {#if title || subtitle}
    <div class="mb-4">
      {#if title}
        <h3 class="text-lg font-medium text-cosmos-text">{title}</h3>
      {/if}
      {#if subtitle}
        <p class="text-sm text-cosmos-text-muted mt-1">{subtitle}</p>
      {/if}
    </div>
  {/if}
  
  <slot />
  
  {#if $$slots.footer}
    <div class="mt-4 pt-4 border-t border-cosmos-bg-light">
      <slot name="footer" />
    </div>
  {/if}
</div>