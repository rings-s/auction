<!-- src/lib/components/ui/ToastContainer.svelte -->
<script>
	/**
	 * Toast Container Component
	 * Manages displaying multiple Toast notifications with proper positioning.
	 */
	import { onMount } from 'svelte';
	import Toast from './Toast.svelte';
	import { toast } from '$lib/stores/toast';
	
	// Props
	export let position = 'bottom-right'; // Position: top-right, top-left, bottom-right, bottom-left, top-center, bottom-center
	export let maxToasts = 5; // Maximum number of toasts to show at once
	export let gap = 'gap-3'; // Gap between toasts
	export let containerWidth = 'max-w-sm'; // Width of the container
	export let zIndex = 'z-50'; // z-index of the container
	
	let toasts = [];
	
	// Subscribe to toast store changes
	onMount(() => {
	  const unsubscribe = toast.subscribe((value) => {
		toasts = value.slice(0, maxToasts);
	  });
	  
	  return unsubscribe;
	});
	
	// Dismiss a toast
	function dismissToast(event) {
	  const { id } = event.detail;
	  toast.dismiss(id);
	}
	
	// Generate position classes
	$: positionClasses = {
	  'top-right': 'top-0 right-0',
	  'top-left': 'top-0 left-0',
	  'bottom-right': 'bottom-0 right-0',
	  'bottom-left': 'bottom-0 left-0',
	  'top-center': 'top-0 left-1/2 transform -translate-x-1/2',
	  'bottom-center': 'bottom-0 left-1/2 transform -translate-x-1/2'
	}[position] || 'bottom-0 right-0';
	
	// Determine flex direction
	$: flexDirection = position.startsWith('top') ? 'flex-col' : 'flex-col-reverse';
  </script>
  
  <div 
	class="fixed m-4 p-4 {containerWidth} {positionClasses} {zIndex} pointer-events-none"
	role="region" 
	aria-label="Notifications"
  >
	<div class="flex {flexDirection} {gap} overflow-hidden">
	  {#each toasts as toast (toast.id)}
		<div class="pointer-events-auto w-full">
		  <Toast
			id={toast.id}
			type={toast.type}
			message={toast.message}
			title={toast.title}
			dismissible={toast.dismissible}
			duration={toast.duration}
			showIcon={toast.showIcon}
			on:dismiss={dismissToast}
		  />
		</div>
	  {/each}
	</div>
  </div>