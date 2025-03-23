<!-- src/lib/components/ui/GlassCard.svelte -->
<script>
    export let padding = 'p-6';
    export let className = '';
  </script>
  
  <div class="relative backdrop-blur-lg rounded-2xl {padding} {className} 
    bg-surface-light dark:bg-surface-dark
    shadow-glass border border-white/10 dark:border-neutral-800/30">
    <slot />
  </div>