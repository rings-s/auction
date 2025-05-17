<script>
  import { theme } from '$lib/stores/theme';
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';

  // Ensure dark class is applied to <html>
  function applyTheme(t) {
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('dark', t === 'dark');
    }
  }

  onMount(() => {
    const saved = localStorage.getItem('theme');
    let initial;
    if (saved === 'dark' || saved === 'light') {
      initial = saved;
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      initial = 'dark';
    } else {
      initial = 'light';
    }
    theme.set(initial);
    applyTheme(initial);

    // Reactively update <html> class on theme change
    const unsubscribe = theme.subscribe(t => {
      applyTheme(t);
    });
    return unsubscribe;
  });

  function toggleTheme() {
    theme.update(t => {
      const next = t === 'dark' ? 'light' : 'dark';
      localStorage.setItem('theme', next);
      applyTheme(next);
      return next;
    });
  }
</script>

<button
  class="p-2 rounded-full bg-gray-100 dark:bg-gray-800 shadow-md hover:shadow-lg border border-gray-200 dark:border-gray-700 transition-all duration-500 hover:scale-110 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
  on:click={toggleTheme}
  aria-label="Toggle theme"
>
  {#if $theme === 'dark'}
    <div in:fade={{ duration: 300 }}>
      <!-- Moon icon (dark mode) -->
      <svg class="w-5 h-5 text-indigo-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.389 5.389 0 0 1-4.4 2.26 5.403 5.403 0 0 1-3.14-9.8c-.44-.06-.9-.1-1.36-.1z"/>
        <path d="M12 3a9 9 0 0 0-9 9h.07a7.49 7.49 0 0 1 4.51 1.5 7.457 7.457 0 0 1 3.74 3.74 7.49 7.49 0 0 1 1.5 4.51A9 9 0 0 0 12 3z" opacity="0.4"/>
      </svg>
    </div>
  {:else}
    <div in:fade={{ duration: 300 }}>
      <!-- Sun icon (light mode) -->
      <svg class="w-5 h-5 text-amber-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" 
          stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none" />
      </svg>
    </div>
  {/if}
</button>