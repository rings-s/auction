<!-- src/lib/components/auction/AuctionCard.svelte -->
<script>
    import { onMount, onDestroy } from 'svelte';
    import { t, language } from '$lib/i18n';
    
    // تصدير المتغيرات التي ستستقبلها البطاقة
    export let auction = {
      id: '',
      uuid: '',
      title: '',
      status: 'active',
      status_display: '',
      start_date: '',
      end_date: '',
      current_bid: 0,
      starting_price: 0,
      min_bid_increment: 0,
      bid_count: 0,
      time_remaining: 0,
      featured_image_url: '',
      property_title: '',
      property_type: '',
      property_type_display: '',
      is_featured: false
    };
    
    // حالة المكون
    let timeLeft = auction.time_remaining || 0;
    let days = 0;
    let hours = 0;
    let minutes = 0;
    let seconds = 0;
    let intervalId;
    let isActive = auction.status === 'active';
    let isPending = auction.status === 'pending';
    let isEnded = ['closed', 'sold', 'cancelled'].includes(auction.status);
    
    // تنسيق السعر بالعملة
    function formatCurrency(amount) {
      return new Intl.NumberFormat($language === 'ar' ? 'ar-SA' : 'en-US', {
        style: 'currency',
        currency: 'SAR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(amount);
    }
    
    // تحديث المؤقت
    function updateTimer() {
      if (timeLeft <= 0) {
        clearInterval(intervalId);
        isActive = false;
        isEnded = true;
        return;
      }
      
      days = Math.floor(timeLeft / (60 * 60 * 24));
      hours = Math.floor((timeLeft % (60 * 60 * 24)) / (60 * 60));
      minutes = Math.floor((timeLeft % (60 * 60)) / 60);
      seconds = Math.floor(timeLeft % 60);
      
      timeLeft--;
    }
    
    // لون حالة المزاد
    function getStatusColor(status) {
      const colors = {
        'active': 'bg-status-success',
        'pending': 'bg-status-warning',
        'extended': 'bg-status-info',
        'closed': 'bg-cosmos-text-dim',
        'sold': 'bg-status-error',
        'cancelled': 'bg-status-error'
      };
      
      return colors[status] || 'bg-cosmos-text-dim';
    }
    
    // تنسيق لوقت المزاد المتبقي
    function getTimeDisplay() {
      if (isEnded) {
        return $t('auctions.ended');
      }
      
      if (isPending) {
        return $t('auctions.starts_in');
      }
      
      if (days > 0) {
        return `${days} ${$t('auctions.days')}`;
      }
      
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    // صورة افتراضية إذا لم تكن هناك صورة
    const fallbackImage = '/images/placeholders/auction-placeholder.jpg';
    
    onMount(() => {
      // بدء المؤقت
      updateTimer();
      intervalId = setInterval(updateTimer, 1000);
    });
    
    onDestroy(() => {
      // تنظيف المؤقت عند تدمير المكون
      clearInterval(intervalId);
    });
  </script>
  
  <a
    href={`/auctions/${auction.id}`}
    class="group relative w-full overflow-hidden rounded-xl bg-cosmos-bg-light bg-opacity-30 backdrop-blur-sm transition-transform duration-300 hover:-translate-y-1 hover:shadow-glow {auction.is_featured ? 'ring-2 ring-primary ring-opacity-60' : ''}"
  >
    <!-- صورة المزاد -->
    <div class="relative aspect-[4/3] w-full overflow-hidden rounded-t-xl">
      <img
        src={auction.featured_image_url || fallbackImage}
        alt={auction.title}
        class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
        loading="lazy"
      />
      
      <!-- شارة نوع العقار -->
      <div class="absolute top-3 {$language === 'ar' ? 'right-3' : 'left-3'} z-above">
        <span class="rounded-full bg-primary bg-opacity-80 px-3 py-1 text-xs text-white backdrop-blur-sm">
          {auction.property_type_display || $t(`properties.types.${auction.property_type}`)}
        </span>
      </div>
      
      <!-- شارة مميز -->
      {#if auction.is_featured}
        <div class="absolute top-3 {$language === 'ar' ? 'left-3' : 'right-3'} z-above">
          <span class="rounded-full bg-[#FFD700] px-3 py-1 text-xs text-cosmos-bg-dark">
            {$t('general.featured')}
          </span>
        </div>
      {/if}
      
      <!-- المؤقت -->
      <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-cosmos-bg-dark to-transparent p-4">
        <div class="flex items-center justify-between">
          <div>
            <span class={`rounded-full px-3 py-1 text-xs text-white ${getStatusColor(auction.status)}`}>
              {auction.status_display || $t(`auctions.status.${auction.status}`)}
            </span>
          </div>
          
          <div class="rounded-full bg-cosmos-bg-dark bg-opacity-50 px-3 py-1 backdrop-blur-sm">
            <span class="text-xs font-mono {isEnded ? 'text-status-error' : isActive ? 'text-status-success' : 'text-status-warning'}">
              {isActive ? $t('auctions.ends_in') : isPending ? $t('auctions.starts_in') : ''} {getTimeDisplay()}
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- معلومات المزاد -->
    <div class="p-4">
      <h3 class="mb-2 text-lg font-bold text-cosmos-text group-hover:text-primary-light">
        {auction.title}
      </h3>
      
      <p class="mb-3 text-sm text-cosmos-text-muted">
        {auction.property_title}
      </p>
      
      <!-- معلومات المزايدة -->
      <div class="mb-4 flex flex-wrap justify-between gap-3">
        <!-- السعر الحالي -->
        <div>
          <p class="text-xs text-cosmos-text-muted">
            {$t('auctions.current_bid')}
          </p>
          <p class="text-lg font-bold text-primary">
            {formatCurrency(auction.current_bid)}
          </p>
        </div>
        
        <!-- عدد المزايدات -->
        <div class="text-right">
          <p class="text-xs text-cosmos-text-muted">
            {$t('auctions.bid_count')}
          </p>
          <p class="text-lg font-bold text-cosmos-text">
            {auction.bid_count}
          </p>
        </div>
      </div>
      
      <!-- زر المزايدة -->
      <div class="flex items-center justify-between">
        <span class="text-sm text-cosmos-text-muted">
          {$t('auctions.min_increment')}: {formatCurrency(auction.min_bid_increment)}
        </span>
        
        <span class="rounded-full bg-primary bg-opacity-10 px-4 py-2 text-sm font-medium text-primary transition group-hover:bg-primary group-hover:text-white">
          {isActive ? $t('auctions.bid_now') : $t('general.view')}
        </span>
      </div>
    </div>
  </a>