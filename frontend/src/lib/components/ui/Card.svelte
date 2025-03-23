<!-- src/lib/components/ui/Card.svelte -->
<script>
    // Props
    export let title = undefined;
    export let subtitle = undefined;
    export let hover = false;
    export let bordered = true;
    export let padding = true;
    export let glass = false; // Glass effect with backdrop blur
  
    // Generate CSS classes based on props
    $: hoverClass = hover ? 'hover:border-primary transition-all duration-200' : '';
    $: borderClass = bordered ? 'border border-cosmos-bg-light' : '';
    $: paddingClass = padding ? 'p-5' : '';
    $: glassClass = glass ? 'bg-cosmos-bg-dark bg-opacity-40 backdrop-blur-lg' : 'bg-cosmos-bg-dark';
  </script>
  
  <div class="rounded-xl shadow-xl {glassClass} {borderClass} {hoverClass} {paddingClass}" {...$$restProps}>
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