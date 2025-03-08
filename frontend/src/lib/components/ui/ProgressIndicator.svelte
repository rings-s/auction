<!-- src/lib/components/ui/ProgressIndicator.svelte -->
<script>
    // Props with defaults
    export let color = 'primary-blue';  // primary-blue, primary-peach, success, warning, error
    export let size = 'md';             // xs, sm, md, lg, xl
    export let thickness = 'normal';    // thin, normal, thick
    export let label = '';              // Optional label
    export let showLabel = false;       // Whether to show the label
    export let value = undefined;       // Set between 0-100 for determinate progress
    export let min = 0;                 // Minimum value
    export let max = 100;               // Maximum value
    export let className = '';          // Additional CSS classes
    
    // Computed styles
    $: sizeMap = {
      'xs': 'h-1 w-16',
      'sm': 'h-1.5 w-24',
      'md': 'h-2 w-32',
      'lg': 'h-2.5 w-40',
      'xl': 'h-3 w-48'
    };
    
    $: thicknessMap = {
      'thin': 'border',
      'normal': 'border-2',
      'thick': 'border-4'
    };
    
    $: colorMap = {
      'primary-blue': 'bg-primary-blue-100 text-primary-blue',
      'primary-peach': 'bg-primary-peach-100 text-primary-peach',
      'success': 'bg-green-100 text-green-600',
      'warning': 'bg-yellow-100 text-yellow-600',
      'error': 'bg-red-100 text-red-600'
    };
    
    $: progressColorMap = {
      'primary-blue': 'bg-primary-blue',
      'primary-peach': 'bg-primary-peach',
      'success': 'bg-green-600',
      'warning': 'bg-yellow-500',
      'error': 'bg-red-600'
    };
    
    // Calculate width percentage for progress bar
    $: progressValue = typeof value === 'number' ? Math.max(min, Math.min(max, value)) : null;
    $: progressPercent = progressValue !== null ? ((progressValue - min) / (max - min)) * 100 : null;
    
    // Is this a determinate or indeterminate progress indicator?
    $: isDeterminate = progressValue !== null;
    
    // Compute animation class
    $: animationClass = isDeterminate ? '' : 'animate-indeterminate';
  </script>
  
  <div class="flex flex-col items-center {className}">
    <div class="relative overflow-hidden rounded-full {sizeMap[size]} {colorMap[color]}">
      {#if isDeterminate}
        <!-- Determinate progress bar -->
        <div 
          class="{progressColorMap[color]} h-full rounded-full transition-all duration-300 ease-out"
          style="width: {progressPercent}%"
        ></div>
      {:else}
        <!-- Indeterminate progress bar -->
        <div 
          class="{progressColorMap[color]} h-full rounded-full {animationClass}"
          style="width: 30%"
        ></div>
      {/if}
    </div>
    
    {#if showLabel && label}
      <div class="mt-2 text-sm font-medium {colorMap[color].split(' ')[1]}">
        {label}
        {#if isDeterminate}
          ({progressValue}/{max})
        {/if}
      </div>
    {/if}
  </div>
  
  <style>
    /* Animation for indeterminate progress */
    .animate-indeterminate {
      animation: indeterminate 1.5s infinite ease-in-out;
    }
    
    @keyframes indeterminate {
      0% {
        transform: translateX(-100%);
      }
      100% {
        transform: translateX(400%);
      }
    }
  </style>