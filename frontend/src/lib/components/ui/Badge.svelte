<!-- src/lib/components/ui/Badge.svelte -->
<script>
  /**
   * Badge Component
   * Displays a status badge with various styles and sizes.
   */
    
  // Props
  export let value = ""; // Badge text content
  export let variant = "primary"; // Badge style: primary, success, error, warning, info, gray
  export let size = "md"; // Badge size: sm, md, lg
  export let rounded = "full"; // rounded-md, rounded-lg, rounded-full
  export let filled = true; // true = solid background, false = light background with border
  export let icon = null; // Optional icon component
  export let ariaLabel = undefined; // Accessibility label
  
  // Class maps for different variants
  const variantClasses = {
    primary: filled 
      ? "bg-primary text-white" 
      : "bg-primary bg-opacity-10 text-primary border border-primary border-opacity-25",
    success: filled 
      ? "bg-status-success text-white" 
      : "bg-status-success bg-opacity-10 text-status-success border border-status-success border-opacity-25",
    error: filled 
      ? "bg-status-error text-white" 
      : "bg-status-error bg-opacity-10 text-status-error border border-status-error border-opacity-25",
    warning: filled 
      ? "bg-status-warning text-white" 
      : "bg-status-warning bg-opacity-10 text-status-warning border border-status-warning border-opacity-25",
    info: filled 
      ? "bg-status-info text-white" 
      : "bg-status-info bg-opacity-10 text-status-info border border-status-info border-opacity-25",
    gray: filled 
      ? "bg-cosmos-text-dim text-white" 
      : "bg-cosmos-text-dim bg-opacity-10 text-cosmos-text-dim border border-cosmos-text-dim border-opacity-25"
  };
  
  // Size classes
  const sizeClasses = {
    sm: "text-xs px-2 py-0.5 font-medium",
    md: "text-sm px-2.5 py-1 font-medium",
    lg: "text-sm px-3 py-1.5 font-semibold"
  };
  
  // Rounded classes
  const roundedClasses = {
    full: "rounded-full",
    lg: "rounded-lg",
    md: "rounded-md",
    none: ""
  };
  
  // Compute final classes
  $: classes = [
    "inline-flex items-center justify-center whitespace-nowrap",
    variantClasses[variant] || variantClasses.primary,
    sizeClasses[size] || sizeClasses.md,
    roundedClasses[rounded] || roundedClasses.full
  ].filter(Boolean).join(' ');
</script>

<span 
  class={classes} 
  aria-label={ariaLabel}
  {...$$restProps}
>
  {#if icon}
    <span class="mr-1">{icon}</span>
  {/if}
  <slot>{value}</slot>
</span>