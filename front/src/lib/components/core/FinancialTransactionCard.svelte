<!-- src/lib/components/core/FinancialTransactionCard.svelte -->
<script>
  import { fly } from 'svelte/transition';
  import Button from '$lib/components/ui/Button.svelte';
  
  export let transaction;
  export let onEdit = () => {};
  export let onView = () => {};
  export let onDelete = () => {};
  export let index = 0;

  function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  }

  function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }).format(new Date(date));
  }

  function getStatusColor(status) {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
      completed: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
      failed: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
      overdue: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
    };
    return colors[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
  }

  function getTransactionIcon(type) {
    const icons = {
      rent_payment: 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z',
      security_deposit: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z',
      maintenance_cost: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z',
      auction_payment: 'M7 4V2a1 1 0 011-1h4a1 1 0 011 1v2m-6 0h6m-6 0v16a1 1 0 001 1h4a1 1 0 001-1V4M7 4H3a1 1 0 00-1 1v2a1 1 0 001 1h4M7 4v16',
      commission: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
      utility_bill: 'M13 10V3L4 14h7v7l9-11h-7z',
      insurance: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
      tax_payment: 'M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z',
      other: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
    };
    return icons[type] || icons.other;
  }
</script>

<div
  class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-all duration-200 p-6"
  in:fly={{ y: 20, duration: 300, delay: index * 50 }}
>
  <div class="flex items-start justify-between">
    <div class="flex items-start space-x-4">
      <!-- Transaction Icon -->
      <div class="flex-shrink-0">
        <div class="w-12 h-12 bg-primary-100 dark:bg-primary-900/20 rounded-lg flex items-center justify-center">
          <svg class="w-6 h-6 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={getTransactionIcon(transaction.transaction_type)} />
          </svg>
        </div>
      </div>

      <!-- Transaction Details -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center space-x-2 mb-1">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white truncate">
            {transaction.description}
          </h3>
          {#if transaction.status}
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getStatusColor(transaction.status)}">
              {transaction.status_display || transaction.status}
            </span>
          {/if}
          {#if transaction.is_overdue}
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400">
              Overdue
            </span>
          {/if}
        </div>

        <div class="text-sm text-gray-500 dark:text-gray-400 space-y-1">
          <div class="flex items-center space-x-4">
            <span class="font-medium">
              {transaction.transaction_type_display || transaction.transaction_type}
            </span>
            {#if transaction.reference_number}
              <span>Ref: {transaction.reference_number}</span>
            {/if}
          </div>

          <div class="flex items-center space-x-4">
            {#if transaction.payer_info}
              <span>From: {transaction.payer_info.full_name || transaction.payer_info.email}</span>
            {/if}
            {#if transaction.payee_info}
              <span>To: {transaction.payee_info.full_name || transaction.payee_info.email}</span>
            {/if}
          </div>

          {#if transaction.property_info}
            <div class="flex items-center space-x-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
              </svg>
              <span>{transaction.property_info.title}</span>
            </div>
          {/if}

          <div class="flex items-center space-x-4">
            <span>Created: {formatDate(transaction.created_at)}</span>
            {#if transaction.due_date}
              <span>Due: {formatDate(transaction.due_date)}</span>
            {/if}
            {#if transaction.paid_date}
              <span>Paid: {formatDate(transaction.paid_date)}</span>
            {/if}
          </div>
        </div>
      </div>
    </div>

    <!-- Amount and Actions -->
    <div class="flex flex-col items-end space-y-3">
      <div class="text-right">
        <div class="text-2xl font-bold text-gray-900 dark:text-white">
          {formatCurrency(transaction.amount)}
        </div>
        {#if transaction.transaction_id}
          <div class="text-xs text-gray-500 dark:text-gray-400">
            ID: {transaction.transaction_id.split('-')[0]}...
          </div>
        {/if}
      </div>

      <div class="flex items-center space-x-2">
        <Button
          size="sm"
          variant="outline"
          onclick={() => onView(transaction)}
        >
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          View
        </Button>
        
        <Button
          size="sm"
          variant="outline"
          onclick={() => onEdit(transaction)}
        >
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          Edit
        </Button>

        {#if transaction.status === 'pending'}
          <Button
            size="sm"
            onclick={() => onEdit({ ...transaction, status: 'completed' })}
          >
            Mark Paid
          </Button>
        {/if}
      </div>
    </div>
  </div>

  <!-- Notes Section -->
  {#if transaction.notes}
    <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <div class="text-sm text-gray-600 dark:text-gray-400">
        <span class="font-medium">Notes:</span> {transaction.notes}
      </div>
    </div>
  {/if}
</div>