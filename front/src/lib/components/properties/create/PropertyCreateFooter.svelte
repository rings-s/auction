<!-- src/lib/components/properties/create/PropertyCreateFooter.svelte -->
<script>
    import { t } from '$lib/i18n';
    
    export let currentStep;
    export let totalSteps;
    export let loading;
    export let uploadingMedia;
    export let uploadProgress;
    export let onNext;
    export let onPrev;
    export let onSubmit;
  </script>
  
  <div class="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-6 py-4 rounded-b-xl">
    <!-- Form Navigation -->
    <div class="flex justify-between items-center">
      <button
        type="button"
        on:click={onPrev}
        disabled={currentStep === 1 || loading}
        class="inline-flex items-center py-2 px-4 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 border border-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600 dark:border-gray-600 disabled:opacity-50 transition-all duration-200 transform hover:-translate-x-1"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
        </svg>
        {$t('common.previous')}
      </button>
      
      {#if currentStep < totalSteps}
        <button
          type="button"
          on:click={onNext}
          class="btn-modern-primary ml-3 inline-flex items-center py-2 px-4 rounded-md shadow-sm text-sm font-medium transition-all duration-200 transform hover:translate-x-1"
        >
          {$t('common.next')}
          <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </button>
      {:else}
        <button
          type="button"
          on:click={onSubmit}
          disabled={loading || uploadingMedia}
          class="btn-modern-primary ml-3 inline-flex items-center py-2 px-4 rounded-md shadow-sm text-sm font-medium disabled:opacity-50 transition-all duration-200"
        >
          {#if loading || uploadingMedia}
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {uploadingMedia ? `${$t('mediaUploader.uploading')} (${uploadProgress}%)` : $t('common.processing')}
          {:else}
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            {$t('property.create')}
          {/if}
        </button>
      {/if}
    </div>
  </div>