<!-- src/routes/+error.svelte -->
<script>
    import { page } from '$app/stores';
    import Button from '$lib/components/ui/Button.svelte';
    
    // Get error status and message
    $: status = $page.status || 404;
    $: message = $page.error?.message || "Page not found";
  </script>
  
  <div class="min-h-screen bg-white px-4 flex items-center justify-center">
    <div class="max-w-lg w-full text-center">
      <div class="bg-primary-blue/5 h-24 w-24 rounded-full mx-auto flex items-center justify-center mb-8">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-secondary-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      
      <h1 class="text-9xl font-extrabold text-gray-900 tracking-widest">{status}</h1>
      <p class="text-2xl text-gray-600 mt-4 mb-8">{message}</p>
      
      <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
        <Button 
          href="/" 
          variant="primary" 
          size="lg"
        >
          Go to Home
        </Button>
        <Button 
          href="/auctions" 
          variant="outline" 
          size="lg"
        >
          Browse Auctions
        </Button>
      </div>
      
      <div class="mt-12">
        <p class="text-sm text-gray-500">
          If you believe this is an error, please <a href="/contact" class="text-secondary-blue hover:underline">contact our support team</a>.
        </p>
      </div>
    </div>
  </div>