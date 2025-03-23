<script>
  export let size = "2rem"; // Default size
  export let color = "#3B82F6"; // Default color - blue-500
  export let text = "Loading..."; // Default text
  export let showText = true; // Whether to show text
  
  // Convert size to Tailwind classes if possible
  let sizeClass;
  if (size === "2rem") sizeClass = "w-8 h-8"; // 2rem = 32px = w-8
  else if (size === "1rem") sizeClass = "w-4 h-4";
  else if (size === "3rem") sizeClass = "w-12 h-12";
  else if (size === "4rem") sizeClass = "w-16 h-16";
  else sizeClass = ""; // Use inline style for custom sizes
  
  // Convert color to Tailwind classes if possible
  let borderColorClass;
  if (color === "#3B82F6") borderColorClass = "border-blue-500";
  else if (color === "#10B981") borderColorClass = "border-emerald-500";
  else if (color === "#EF4444") borderColorClass = "border-red-500";
  else if (color === "#F59E0B") borderColorClass = "border-amber-500";
  else if (color === "#6366F1") borderColorClass = "border-indigo-500";
  else borderColorClass = ""; // Use inline style for custom colors
</script>

<div class="flex flex-col items-center justify-center">
  <div 
    class="rounded-full border-4 border-t-transparent border-r-transparent animate-spin {sizeClass} {borderColorClass}"
    style={(!sizeClass ? `width: ${size}; height: ${size};` : '') + 
           (!borderColorClass ? `border-color: ${color} transparent transparent transparent;` : '')}
  ></div>
  
  {#if showText}
    <p class="mt-2 text-sm text-gray-500">{text}</p>
  {/if}
</div>