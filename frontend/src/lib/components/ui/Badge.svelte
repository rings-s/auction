<!-- src/lib/components/ui/Badge.svelte -->
<script>
  // Props
  export let variant = 'default'; // default, primary, success, warning, error, info, light
  export let size = 'md'; // sm, md, lg
  export let pill = false;
  
  // Compute variant classes based on our new design system colors
  let variantClasses;
  
  switch (variant) {
    case 'primary':
      variantClasses = 'bg-primary-blue/30 text-secondary-blue';
      break;
    case 'success':
      variantClasses = 'bg-success/20 text-success';
      break;
    case 'warning':
      variantClasses = 'bg-warning/20 text-warning';
      break;
    case 'error':
      variantClasses = 'bg-error/20 text-error';
      break;
    case 'info':
      variantClasses = 'bg-secondary-blue/20 text-secondary-blue';
      break;
    case 'light':
      variantClasses = 'bg-white/70 text-text-dark border border-white/50 backdrop-blur-sm';
      break;
    default:
      variantClasses = 'bg-neutral-100 text-text-medium';
  }
  
  // Compute size classes
  let sizeClasses;
  
  switch (size) {
    case 'sm':
      sizeClasses = 'px-1.5 py-0.5 text-xs';
      break;
    case 'lg':
      sizeClasses = 'px-3 py-1 text-sm';
      break;
    case 'md':
    default:
      sizeClasses = 'px-2.5 py-0.5 text-xs';
  }
  
  // Combined classes
  $: classes = `
    inline-flex items-center font-medium
    ${variantClasses}
    ${sizeClasses}
    ${pill ? 'rounded-full' : 'rounded-md'}
    ${$$props.class || ''}
  `.trim();
</script>

<span class={classes}>
  <slot />
</span>

<style>
/* Add subtle shadow for depth */
span {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

/* Subtle hover effect */
span:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>