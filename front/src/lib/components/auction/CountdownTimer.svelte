<!-- src/lib/components/CountdownTimer.svelte -->
<script>
    import { onMount, onDestroy } from 'svelte';
    import { t } from '../../../../../i18n';
    
    export let endDate;
    export let onEnd = () => {};
    export let variant = 'primary';
    
    let timeRemaining = { days: 0, hours: 0, minutes: 0, seconds: 0 };
    let timer;
    let isExpired = false;
    
    function updateTimeRemaining() {
      const end = new Date(endDate);
      const now = new Date();
      const diff = end - now;
      
      if (diff <= 0) {
        timeRemaining = { days: 0, hours: 0, minutes: 0, seconds: 0 };
        clearInterval(timer);
        isExpired = true;
        onEnd();
        return;
      }
      
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);
      
      timeRemaining = { days, hours, minutes, seconds };
    }
    
    onMount(() => {
      updateTimeRemaining();
      timer = setInterval(updateTimeRemaining, 1000);
    });
    
    onDestroy(() => {
      if (timer) clearInterval(timer);
    });
    
    // Background classes based on variant
    $: bgClass = variant === 'primary' 
      ? 'bg-primary-50 dark:bg-primary-900/20' 
      : 'bg-gray-50 dark:bg-gray-700';
      
    // Text classes based on variant
    $: textClass = variant === 'primary'
      ? 'text-primary-600 dark:text-primary-400'
      : 'text-gray-900 dark:text-white';
  </script>
  
  <div class={`grid grid-cols-4 gap-2 text-center ${bgClass} rounded-lg p-3`}>
    <div>
      <span class={`block text-2xl font-bold ${textClass}`}>{timeRemaining.days}</span>
      <span class="text-xs text-gray-500 dark:text-gray-400">{$t('auction.days')}</span>
    </div>
    <div>
      <span class={`block text-2xl font-bold ${textClass}`}>{timeRemaining.hours}</span>
      <span class="text-xs text-gray-500 dark:text-gray-400">{$t('auction.hours')}</span>
    </div>
    <div>
      <span class={`block text-2xl font-bold ${textClass}`}>{timeRemaining.minutes}</span>
      <span class="text-xs text-gray-500 dark:text-gray-400">{$t('auction.minutes')}</span>
    </div>
    <div>
      <span class={`block text-2xl font-bold ${textClass}`}>{timeRemaining.seconds}</span>
      <span class="text-xs text-gray-500 dark:text-gray-400">{$t('auction.seconds')}</span>
    </div>
  </div>