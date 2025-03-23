<!-- src/lib/components/auth/AuthBackground.svelte -->
<script>
  import { onMount } from 'svelte';
  
  let mounted = false;
  
  onMount(() => {
    mounted = true;
  });
</script>

<div class="fixed top-0 left-0 right-0 bottom-0 -z-10 bg-gradient-to-br from-black to-neutral-900 overflow-hidden">
  <!-- Animated floating shapes -->
  <div class="absolute inset-0">
    <!-- Minimalist glowing circle -->
    <div class="absolute top-1/4 left-1/3 w-64 h-64 opacity-10">
      <div class="w-full h-full rounded-full border border-primary/30 animate-pulse-slow"></div>
      <div class="absolute inset-4 rounded-full border border-primary/20 animate-pulse-slow animation-delay-300"></div>
      <div class="absolute inset-8 rounded-full border border-primary/10 animate-pulse-slow animation-delay-600"></div>
    </div>
    
    <!-- Minimalist grid lines -->
    <div class="absolute inset-0 grid-pattern opacity-5"></div>
    
    <!-- Floating geometric shapes -->
    <div class="absolute top-2/3 left-1/4 w-16 h-16 border border-white/10 rotate-45 animate-float-slow"></div>
    <div class="absolute bottom-1/3 right-1/4 w-24 h-24 border border-white/5 rounded-full animate-float-slow animation-delay-700"></div>
    <div class="absolute top-1/3 right-1/3 w-20 h-20 border border-primary/10 animate-float-slow animation-delay-1400"></div>
    
    <!-- Soft glow effect -->
    <div class="absolute top-1/4 left-1/5 w-48 h-48 rounded-full bg-primary/5 blur-3xl animate-glow-pulse"></div>
    <div class="absolute bottom-1/4 right-1/5 w-64 h-64 rounded-full bg-primary/3 blur-3xl animate-glow-pulse animation-delay-1000"></div>
  </div>
  
  <!-- Subtle gradient overlay -->
  <div class="absolute inset-0 backdrop-blur-[2px] bg-gradient-to-t from-black/40 to-transparent"></div>
</div>

<style>
  /* Custom animations */
  @keyframes float-slow {
    0% { transform: translateY(0) rotate(0); }
    50% { transform: translateY(-10px) rotate(5deg); }
    100% { transform: translateY(0) rotate(0); }
  }
  
  @keyframes pulse-slow {
    0% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.05); opacity: 1; }
    100% { transform: scale(1); opacity: 0.5; }
  }
  
  @keyframes glow-pulse {
    0% { opacity: 0.3; }
    50% { opacity: 0.6; }
    100% { opacity: 0.3; }
  }
  
  /* Animation classes */
  .animate-float-slow {
    animation: float-slow 10s ease-in-out infinite;
  }
  
  .animate-pulse-slow {
    animation: pulse-slow 8s ease-in-out infinite;
  }
  
  .animate-glow-pulse {
    animation: glow-pulse 12s ease-in-out infinite;
  }
  
  .animation-delay-300 {
    animation-delay: 0.3s;
  }
  
  .animation-delay-600 {
    animation-delay: 0.6s;
  }
  
  .animation-delay-700 {
    animation-delay: 0.7s;
  }
  
  .animation-delay-1000 {
    animation-delay: 1s;
  }
  
  .animation-delay-1400 {
    animation-delay: 1.4s;
  }
  
  /* Grid pattern */
  .grid-pattern {
    background-image: 
      linear-gradient(to right, rgba(255, 255, 255, 0.05) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
    background-size: 40px 40px;
    background-position: center;
  }
</style>