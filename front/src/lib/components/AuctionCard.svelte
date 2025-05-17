<!-- src/lib/components/AuctionCard.svelte -->
<script>
    import { t } from '$lib/i18n/i18n';
    import { onMount, onDestroy } from 'svelte';
    
    export let auction;
    
    let timeRemaining = { days: 0, hours: 0, minutes: 0, seconds: 0 };
    let interval;
    
    function updateTimeRemaining() {
      const endDate = new Date(auction.end_date);
      const now = new Date();
      const diff = endDate - now;
      
      if (diff <= 0) {
        timeRemaining = { days: 0, hours: 0, minutes: 0, seconds: 0 };
        clearInterval(interval);
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
      interval = setInterval(updateTimeRemaining, 1000);
      
      return () => {
        clearInterval(interval);
      };
    });
    
    onDestroy(() => {
      if (interval) clearInterval(interval);
    });
  </script>
  
  <a 
    href={`/auctions/${auction.slug}`} 
    class="block h-full group"
  >
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden transition-shadow duration-300 hover:shadow-lg h-full flex flex-col">
      <div class="relative h-56">
        <img 
          src={auction.related_property?.main_image || '/images/auction-placeholder.jpg'} 
          alt={auction.title}
          class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
        <div class="absolute top-0 right-0 m-2">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium 
            {auction.status === 'live' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 
            auction.status === 'scheduled' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' : 
            auction.status === 'ended' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' : 
            'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'}"
          >
            {auction.status === 'live' ? $t('auction.statusLive') : 
             auction.status === 'scheduled' ? $t('auction.statusScheduled') : 
             auction.status === 'ended' ? $t('auction.statusEnded') : 
             auction.status === 'completed' ? $t('auction.statusCompleted') : 
             $t('auction.statusDraft')}
          </span>
        </div>
        {#if auction.is_featured}
          <div class="absolute top-0 left-0 m-2">
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200">
              {$t('auction.featured')}
            </span>
          </div>
        {/if}
        <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-4">
          <h3 class="text-lg font-semibold text-white truncate">{auction.title}</h3>
          <p class="text-sm text-gray-200">{auction.related_property?.city || ''}, {auction.related_property?.state || ''}</p>
        </div>
      </div>
      
      <div class="p-4 flex-grow">
        <div class="mb-3">
          <span class="inline-block bg-gray-100 dark:bg-gray-700 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 dark:text-gray-300">
            {auction.auction_type === 'sealed' ? $t('auction.typeSealed') :
             auction.auction_type === 'reserve' ? $t('auction.typeReserve') :
             $t('auction.typeNoReserve')}
          </span>
        </div>
        
        <div class="mb-3">
          <p class="text-sm text-gray-500 dark:text-gray-400">{$t('auction.currentBid')}</p>
          <p class="text-xl font-bold text-gray-900 dark:text-white">
            ${auction.current_bid ? auction.current_bid.toLocaleString() : auction.starting_bid.toLocaleString()}
          </p>
        </div>
        
        <p class="text-gray-600 dark:text-gray-300 line-clamp-2 text-sm mb-3">{auction.description}</p>
        
        {#if auction.status === 'live' || auction.status === 'scheduled'}
          <div class="bg-gray-100 dark:bg-gray-700 rounded-lg p-2 mb-3">
            <p class="text-xs text-center text-gray-500 dark:text-gray-400 mb-1">{$t('auction.timeRemaining')}</p>
            <div class="grid grid-cols-4 gap-1 text-center">
              <div>
                <span class="block text-lg font-bold text-gray-900 dark:text-white">{timeRemaining.days}</span>
                <span class="text-xs text-gray-500 dark:text-gray-400">{$t('auction.days')}</span>
              </div>
              <div>
                <span class="block text-lg font-bold text-gray-900 dark:text-white">{timeRemaining.hours}</span>
                <span class="text-xs text-gray-500 dark:text-gray-400">{$t('auction.hours')}</span>
              </div>
              <div>
                <span class="block text-lg font-bold text-gray-900 dark:text-white">{timeRemaining.minutes}</span>
                <span class="text-xs text-gray-500 dark:text-gray-400">{$t('auction.minutes')}</span>
              </div>
              <div>
                <span class="block text-lg font-bold text-gray-900 dark:text-white">{timeRemaining.seconds}</span>
                <span class="text-xs text-gray-500 dark:text-gray-400">{$t('auction.seconds')}</span>
              </div>
            </div>
          </div>
        {/if}
      </div>
      
      <div class="border-t border-gray-200 dark:border-gray-700 p-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
            </svg>
            {auction.bid_count} {$t('auction.bids')}
          </div>
          <span class="inline-flex items-center text-sm text-primary-600 dark:text-primary-400 font-medium">
            {$t('auction.viewDetails')}
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </span>
        </div>
      </div>
    </div>
</a>