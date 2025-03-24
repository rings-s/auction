<!-- src/lib/components/ui/EmptyState.svelte -->
<script>
    /**
     * EmptyState Component
     * Displays a placeholder when content is not available.
     */
    
    // Props
    export let title = "No data available"; // Title text
    export let description = ""; // Description text
    export let icon = "default"; // Icon to display: default, folder, document, image, search, error, custom
    export let size = "md"; // sm, md, lg
    export let rounded = true; // Add rounded corners
    export let bordered = false; // Add border
    export let shadow = false; // Add shadow
    export let padding = true; // Add padding
    export let alignment = "center"; // center, left, right
    export let actionText = ""; // Primary action button text
    export let secondaryActionText = ""; // Secondary action button text
    export let actionVariant = "primary"; // Button variant: primary, secondary, outline, link
    export let onAction = () => {}; // Primary action callback
    export let onSecondaryAction = () => {}; // Secondary action callback
    
    // Size classes
    $: sizeClasses = {
      sm: {
        container: "py-6",
        icon: "w-12 h-12",
        title: "text-base",
        description: "text-sm"
      },
      md: {
        container: "py-10",
        icon: "w-16 h-16",
        title: "text-lg",
        description: "text-base"
      },
      lg: {
        container: "py-16",
        icon: "w-24 h-24",
        title: "text-xl",
        description: "text-lg"
      }
    }[size] || sizeClasses.md;
    
    // Alignment classes
    $: alignmentClasses = {
      center: "items-center text-center",
      left: "items-start text-left",
      right: "items-end text-right"
    }[alignment] || "items-center text-center";
    
    // Container classes
    $: containerClasses = [
      "flex flex-col",
      alignmentClasses,
      padding ? "px-4" : "",
      rounded ? "rounded-xl" : "",
      bordered ? "border border-neutral-200 dark:border-neutral-700" : "",
      shadow ? "shadow-md" : "",
      sizeClasses.container
    ].filter(Boolean).join(" ");
    
    // Get icon based on type
    function getIcon(type) {
      switch (type) {
        case "folder":
          return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                  </svg>`;
        case "document":
          return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                  </svg>`;
        case "image":
          return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    <circle cx="8.5" cy="8.5" r="1.5"></circle>
                    <polyline points="21 15 16 10 5 21"></polyline>
                  </svg>`;
        case "search":
          return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                  </svg>`;
        case "error":
          return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                  </svg>`;
        case "default":
        default:
          return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="16" x2="12" y2="12"></line>
                    <line x1="12" y1="8" x2="12.01" y2="8"></line>
                  </svg>`;
      }
    }
    
    // Button variants
    const buttonVariants = {
      primary: "bg-primary text-white hover:bg-primary-dark",
      secondary: "bg-neutral-200 dark:bg-neutral-700 text-neutral-800 dark:text-white hover:bg-neutral-300 dark:hover:bg-neutral-600",
      outline: "bg-transparent border border-primary text-primary hover:bg-primary hover:text-white",
      link: "bg-transparent text-primary hover:underline px-0 py-0"
    };
  </script>
  
  <div class={containerClasses} {...$$restProps}>
    <!-- Icon -->
    {#if icon === "custom"}
      <div class={`${sizeClasses.icon} text-neutral-400 dark:text-neutral-500 mb-4 ${alignment === "center" ? "mx-auto" : ""}`}>
        <slot name="icon"></slot>
      </div>
    {:else}
      <div class={`${sizeClasses.icon} text-neutral-400 dark:text-neutral-500 mb-4 ${alignment === "center" ? "mx-auto" : ""}`}>
        {@html getIcon(icon)}
      </div>
    {/if}
    
    <!-- Title -->
    <h3 class={`font-medium ${sizeClasses.title} text-neutral-800 dark:text-white mb-2`}>
      {title}
    </h3>
    
    <!-- Description -->
    {#if description}
      <p class={`${sizeClasses.description} text-neutral-600 dark:text-neutral-400 mb-6 max-w-md ${alignment === "center" ? "mx-auto" : ""}`}>
        {description}
      </p>
    {/if}
    
    <!-- Content slot -->
    <slot></slot>
    
    <!-- Actions -->
    {#if actionText || secondaryActionText || $$slots.actions}
      <div class={`mt-6 flex gap-4 ${alignment === "center" ? "justify-center" : alignment === "right" ? "justify-end" : ""}`}>
        {#if $$slots.actions}
          <slot name="actions"></slot>
        {:else}
          {#if actionText}
            <button 
              type="button" 
              class={`px-4 py-2 rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary ${buttonVariants[actionVariant]}`}
              on:click={onAction}
            >
              {actionText}
            </button>
          {/if}
          
          {#if secondaryActionText}
            <button 
              type="button" 
              class="px-4 py-2 rounded-md text-sm font-medium text-neutral-700 dark:text-neutral-300 bg-white dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-600 hover:bg-neutral-50 dark:hover:bg-neutral-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
              on:click={onSecondaryAction}
            >
              {secondaryActionText}
            </button>
          {/if}
        {/if}
      </div>
    {/if}
  </div>