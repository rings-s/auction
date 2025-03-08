<!-- src/lib/components/ui/Avatar.svelte -->
<script>
    /**
     * Modern Avatar component with animations for the GUDIC platform
     */
    import { onMount } from 'svelte';
    
    // Props
    export let src = ''; // Image source URL
    export let alt = ''; // Alternative text for the image
    export let size = 'md'; // xs, sm, md, lg, xl
    export let shape = 'circle'; // circle, square, rounded
    export let initials = ''; // Initials to display when no image is available
    export let status = ''; // online, away, busy, offline
    export let variant = 'default'; // default, outline, solid
    export let bordered = false; // Whether to add a border
    export let backgroundColor = ''; // Custom background color
    export let color = ''; // Custom text color
    export let fallbackIcon = null; // Icon component to use as fallback
    export let loading = false; // Show loading state
    export let className = ''; // Additional CSS classes
    
    // Avatar group props
    export let group = false; // Whether this is part of a group component
    export let avatars = []; // Array of avatar objects for group mode
    export let max = Infinity; // Maximum avatars to show before count
    export let overlap = true; // Whether avatars should overlap
    
    // Internal state
    let imageLoaded = false;
    let imageError = false;
    let mounted = false;
    
    // Handle image load/error events
    function handleImageLoad() {
      imageLoaded = true;
    }
    
    function handleImageError() {
      imageError = true;
    }
    
    // Generate initials from string
    function generateInitials(name) {
      if (!name) return '';
      
      const names = name.split(' ');
      if (names.length === 1) {
        return names[0].charAt(0).toUpperCase();
      }
      
      return (names[0].charAt(0) + names[names.length - 1].charAt(0)).toUpperCase();
    }
    
    // Calculate background color from string (if not provided)
    function calculateBgColor(str) {
      if (!str) return 'bg-primary-blue/20';
      
      const colors = [
        'bg-primary-blue/20',
        'bg-primary-peach/20',
        'bg-secondary-blue/20',
        'bg-secondary-peach/20',
        'bg-success/20',
        'bg-warning/20',
        'bg-error/20',
      ];
      
      let hash = 0;
      for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
      }
      
      return colors[Math.abs(hash) % colors.length];
    }
    
    // Size classes mapping
    $: sizeClasses = {
      xs: 'h-6 w-6 text-xs',
      sm: 'h-8 w-8 text-xs',
      md: 'h-10 w-10 text-sm',
      lg: 'h-12 w-12 text-base',
      xl: 'h-16 w-16 text-lg'
    }[size] || 'h-10 w-10 text-sm';
    
    // Shape classes mapping
    $: shapeClasses = {
      circle: 'rounded-full',
      square: 'rounded-none',
      rounded: 'rounded-lg'
    }[shape] || 'rounded-full';
    
    // Variant classes mapping
    $: variantClasses = {
      default: 'bg-primary-blue/10 text-secondary-blue',
      outline: 'bg-white border-2 border-primary-blue/20 text-secondary-blue',
      solid: 'bg-secondary-blue text-white'
    }[variant] || 'bg-primary-blue/10 text-secondary-blue';
    
    // Status indicator classes
    $: statusClasses = {
      online: 'bg-success',
      away: 'bg-warning',
      busy: 'bg-error',
      offline: 'bg-neutral-400'
    }[status] || '';
    
    // Status indicator animation
    $: statusAnimation = status === 'online' ? 'animate-pulse' : '';
    
    // Calculate final classes
    $: avatarClasses = `
      inline-flex items-center justify-center overflow-hidden
      ${sizeClasses}
      ${shapeClasses}
      ${!src || imageError ? (backgroundColor || (variant !== 'default' ? variantClasses : calculateBgColor(initials || alt))) : ''}
      ${bordered ? 'border-2 border-white shadow-sm' : ''}
      ${loading ? 'animate-pulse' : ''}
      ${className}
    `;
    
    // Calculate text color
    $: textColorClass = color || (variant === 'solid' ? 'text-white' : 'text-secondary-blue');
    
    // Prepare display initials
    $: displayInitials = initials || generateInitials(alt);
    
    // Check if we should render the initials
    $: showInitials = (!src || imageError) && !fallbackIcon && displayInitials;
    
    // Check if we should render the fallback icon
    $: showFallbackIcon = (!src || imageError) && fallbackIcon && !displayInitials;
    
    // Calculate overlap offset based on size (for group mode)
    $: overlapOffset = {
      xs: overlap ? '-0.75rem' : '0.25rem',
      sm: overlap ? '-1rem' : '0.25rem',
      md: overlap ? '-1.25rem' : '0.5rem',
      lg: overlap ? '-1.5rem' : '0.5rem',
      xl: overlap ? '-2rem' : '0.75rem'
    }[size] || '-1.25rem';
    
    // Determine if we need to show the "+X" overflow indicator
    $: showOverflowCount = avatars.length > max;
    $: visibleAvatars = showOverflowCount ? avatars.slice(0, max) : avatars;
    $: overflowCount = avatars.length - max;
    
    // Track component mount status
    onMount(() => {
      mounted = true;
    });
  </script>
  
  {#if group}
    <!-- Avatar Group -->
    <div 
      class={`inline-flex items-center ${className}`} 
      style={overlap ? `--overlap: ${overlapOffset}` : ''}
    >
      {#each visibleAvatars as avatar, i}
        <div 
          style={i > 0 && overlap ? 'margin-left: var(--overlap);' : ''}
          class="relative z-0 transition-all duration-200 hover:z-10"
        >
          <svelte:self
            src={avatar.src}
            alt={avatar.alt}
            initials={avatar.initials}
            status={avatar.status}
            {size}
            {shape}
            bordered={bordered !== undefined ? bordered : true}
            {variant}
          />
        </div>
      {/each}
      
      {#if showOverflowCount}
        <div
          style={overlap ? 'margin-left: var(--overlap);' : ''}
          class="relative z-0 transition-all duration-200 hover:z-10"
        >
          <svelte:self
            {size}
            {shape}
            bordered={bordered !== undefined ? bordered : true}
            variant="solid"
            backgroundColor="bg-primary-blue"
            color="text-white"
            alt={`${overflowCount} more`}
            initials={`+${overflowCount}`}
          />
        </div>
      {/if}
    </div>
  {:else}
    <!-- Single Avatar -->
    <div class="relative inline-block">
      <div class={avatarClasses} role="img" aria-label={alt}>
        {#if src && !imageError}
          <img
            {src}
            {alt}
            class={`h-full w-full object-cover ${shapeClasses}`}
            on:load={handleImageLoad}
            on:error={handleImageError}
          />
        {:else if showInitials}
          <span class={`font-medium ${textColorClass}`}>{displayInitials}</span>
        {:else if showFallbackIcon}
          <svelte:component this={fallbackIcon} />
        {/if}
      </div>
      
      {#if status}
        <span 
          class={`absolute bottom-0 right-0 block rounded-full ${statusClasses} ${statusAnimation}`}
          style={`
            height: ${size === 'xs' ? '0.5rem' : size === 'sm' ? '0.625rem' : size === 'lg' ? '0.875rem' : size === 'xl' ? '1rem' : '0.75rem'};
            width: ${size === 'xs' ? '0.5rem' : size === 'sm' ? '0.625rem' : size === 'lg' ? '0.875rem' : size === 'xl' ? '1rem' : '0.75rem'};
            border: 2px solid white;
          `}
          title={`Status: ${status}`}
        ></span>
      {/if}
    </div>
  {/if}
  
  <style>
    /* Animations for avatar transitions */
    div[role="img"] {
      transition: all 0.3s ease;
    }
    
    div[role="img"]:hover {
      transform: scale(1.05);
    }
    
    /* Status indicator pulse animation */
    .animate-pulse {
      animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.7; }
    }
    
    /* Group hover effects */
    div:hover > div {
      transform: translateX(5px);
    }
    
    div > div:hover {
      transform: scale(1.1) !important;
    }
  </style>