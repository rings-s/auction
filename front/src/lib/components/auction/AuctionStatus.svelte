<!-- src/lib/components/AuctionStatus.svelte -->
<script>
  import { t } from '$lib/i18n';
    
  export let status = '';
  export let isCompact = false;
  
  function getStatusClasses(status) {
    const baseClasses = isCompact 
      ? 'inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium' 
      : 'inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium';
    
    const statusClasses = {
      live: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      scheduled: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      ended: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      completed: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      draft: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
      // Bid statuses
      pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      accepted: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      rejected: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      outbid: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      winning: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
    };
    
    return `${baseClasses} ${statusClasses[status] || statusClasses.draft}`;
  }
    
  function getStatusLabel(status) {
    const statusLabels = {
      live: $t('auction.statusLive'),
      scheduled: $t('auction.statusScheduled'),
      ended: $t('auction.statusEnded'),
      completed: $t('auction.statusCompleted'),
      draft: $t('auction.statusDraft'),
      // Bid statuses
      pending: $t('auction.pending'),
      accepted: $t('auction.accepted'),
      rejected: $t('auction.rejected'),
      outbid: $t('auction.outbid'),
      winning: $t('auction.winning')
    };
    
    return statusLabels[status] || status;
  }
  </script>
  
  <span class={getStatusClasses(status)}>
    {getStatusLabel(status)}
  </span>