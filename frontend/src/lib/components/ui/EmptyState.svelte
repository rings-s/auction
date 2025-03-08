<!-- src/lib/components/ui/EmptyState.svelte -->
<script>
    /**
     * Modern EmptyState component with animations for the GUDIC platform
     * Used to show visual feedback when content is empty or unavailable
     */
    import { fade, fly } from 'svelte/transition';
    import Button from './Button.svelte';
    import Icon from './Icon.svelte';
    
    // Props
    export let title = 'No items found';
    export let description = 'There are no items to display at this time.';
    export let icon = 'package'; // Default icon or custom component
    export let iconBgColor = 'bg-primary-blue/10';
    export let iconColor = 'text-primary-blue';
    export let iconSize = 'lg'; // sm, md, lg, xl
    export let image = ''; // Optional image URL instead of icon
    export let primaryAction = null; // { label: string, onClick: function, href?: string, variant?: string }
    export let secondaryAction = null; // { label: string, onClick: function, href?: string, variant?: string }
    export let size = 'md'; // sm, md, lg
    export let centered = true;
    export let animated = true;
    export let customClass = '';
    
    // Size classes for container
    $: sizeClasses = {
      sm: 'py-6 px-4 max-w-sm',
      md: 'py-8 px-6 max-w-md',
      lg: 'py-12 px-8 max-w-lg',
    }[size] || 'py-8 px-6 max-w-md';
    
    // Size classes for icon
    $: iconSizeClasses = {
      sm: 'w-12 h-12',
      md: 'w-16 h-16',
      lg: 'w-20 h-20',
      xl: 'w-24 h-24',
    }[iconSize] || 'w-16 h-16';
    
    // Icon inner size classes
    $: iconInnerSizeClasses = {
      sm: 'w-6 h-6',
      md: 'w-8 h-8',
      lg: 'w-10 h-10',
      xl: 'w-12 h-12',
    }[iconSize] || 'w-8 h-8';
    
    // Text size classes based on overall size
    $: titleSizeClasses = {
      sm: 'text-lg',
      md: 'text-xl',
      lg: 'text-2xl',
    }[size] || 'text-xl';
    
    $: descriptionSizeClasses = {
      sm: 'text-sm',
      md: 'text-base',
      lg: 'text-lg',
    }[size] || 'text-base';
    
    // Combined classes
    $: containerClasses = `
      ${sizeClasses}
      ${centered ? 'mx-auto text-center' : 'text-left'}
      ${customClass}
    `;
  </script>
  
  <div class={containerClasses}>
    <!-- Icon or image -->
    <div class="flex justify-center mb-6">
      {#if image}
        <div 
          class="overflow-hidden rounded-lg"
          class:animate-float={animated}
          in:fade={{ delay: 100, duration: 400 }}
        >
          <img 
            src={image} 
            alt={title} 
            class="object-cover max-w-full"
            style="max-height: 180px;"
          />
        </div>
      {:else}
        <div 
          class="{iconBgColor} {iconSizeClasses} rounded-full flex items-center justify-center"
          class:animate-float={animated}
          in:fade={{ delay: 100, duration: 400 }}
        >
          {#if typeof icon === 'string'}
            <Icon name={icon} class="{iconColor} {iconInnerSizeClasses}" />
          {:else}
            <svelte:component this={icon} class="{iconColor} {iconInnerSizeClasses}" />
          {/if}
        </div>
      {/if}
    </div>
    
    <!-- Title and description -->
    <div in:fly={{ y: 10, delay: 200, duration: 300 }}>
      {#if title}
        <h3 class="{titleSizeClasses} font-semibold text-text-dark mb-2">{title}</h3>
      {/if}
      
      {#if description}
        <p class="{descriptionSizeClasses} text-text-medium mb-6 max-w-prose mx-auto">{description}</p>
      {/if}
    </div>
    
    <!-- Action buttons -->
    {#if primaryAction || secondaryAction}
      <div 
        class="flex {centered ? 'justify-center' : 'justify-start'} space-x-3 mt-2"
        in:fly={{ y: 10, delay: 300, duration: 300 }}
      >
        {#if secondaryAction}
          <Button
            variant={secondaryAction.variant || 'outline'}
            size={size === 'lg' ? 'md' : size === 'sm' ? 'xs' : 'sm'}
            href={secondaryAction.href}
            on:click={secondaryAction.onClick}
          >
            {secondaryAction.label}
          </Button>
        {/if}
        
        {#if primaryAction}
          <Button
            variant={primaryAction.variant || 'primary'}
            size={size === 'lg' ? 'md' : size === 'sm' ? 'xs' : 'sm'}
            href={primaryAction.href}
            on:click={primaryAction.onClick}
          >
            {primaryAction.label}
          </Button>
        {/if}
      </div>
    {/if}
  </div>
  
  <style>
    /* Gentle floating animation for icon/image */
    .animate-float {
      animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
      0% {
        transform: translateY(0px);
      }
      50% {
        transform: translateY(-10px);
      }
      100% {
        transform: translateY(0px);
      }
    }
    
    /* Subtle shadow for 3D effect */
    img, div[class*="rounded-full"] {
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
      transition: all 0.3s ease;
    }
    
    /* Hover effect */
    div:hover > img, 
    div:hover > div[class*="rounded-full"] {
      transform: translateY(-5px);
      box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
    }
  </style>