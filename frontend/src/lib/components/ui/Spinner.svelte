<!-- src/lib/components/ui/Spinner.svelte -->
<script>
  // Props
  export let size = 'md'; // sm, md, lg
  export let color = 'primary'; // primary, secondary, white, text
  
  // Compute size classes
  let sizeClass;
  
  switch (size) {
    case 'sm':
      sizeClass = 'h-4 w-4';
      break;
    case 'lg':
      sizeClass = 'h-8 w-8';
      break;
    case 'md':
    default:
      sizeClass = 'h-6 w-6';
      break;
  }
  
  // Compute color classes with our new color scheme
  let colorClass;
  
  switch (color) {
    case 'white':
      colorClass = 'text-white';
      break;
    case 'text':
      colorClass = 'text-text-medium';
      break;
    case 'secondary':
      colorClass = 'text-secondary-peach';
      break;
    case 'primary':
    default:
      colorClass = 'text-secondary-blue';
      break;
  }
</script>

<div class="flex justify-center items-center">
  <div class="spinner-container">
    <svg class="{sizeClass} {colorClass} animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
  </div>
</div>

<style>
.spinner-container {
  position: relative;
}

.spinner-container::after {
  content: '';
  position: absolute;
  top: -8px;
  left: -8px;
  right: -8px;
  bottom: -8px;
  border-radius: 50%;
  background: radial-gradient(
    circle,
    rgba(185, 220, 242, 0.2) 0%,
    rgba(246, 207, 190, 0.1) 70%,
    rgba(255, 255, 255, 0) 100%
  );
  opacity: 0;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(0.8);
    opacity: 0;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    transform: scale(1.2);
    opacity: 0;
  }
}
</style>