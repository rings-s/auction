<!-- src/lib/components/documents/DocumentsList.svelte -->
<script>
    import { onMount, createEventDispatcher } from 'svelte';
    import { fade, slide } from 'svelte/transition';
    import { t, language } from '$lib/i18n';
    import { formatDate } from '$lib/utils/formatters';
    import { isAuthenticated, currentUser } from '$lib/stores/auth';
    import { toast } from '$lib/stores/toast';
    import { browser } from '$app/environment';
    import { api } from '$lib/services/api';
    
    // UI Components
    import Button from '$lib/components/ui/Button.svelte';
    import Badge from '$lib/components/ui/Badge.svelte';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    import Dropdown from '$lib/components/ui/Dropdown.svelte';
    import EmptyState from '$lib/components/ui/EmptyState.svelte';
    import Input from '$lib/components/ui/Input.svelte';
    import Select from '$lib/components/ui/Select.svelte';
    
    const dispatch = createEventDispatcher();
    
    // Props with defaults
    export let documents = [];
    export let loading = false;
    export let error = null;
    export let propertyId = null;
    export let filterEnabled = true;
    export let showActions = true;
    export let showUpload = false;
    export let maxHeight = null;
    export let emptyStateText = $t('documents.no_documents');
    
    // State variables
    let filteredDocuments = [];
    let searchQuery = '';
    let filterType = '';
    let filterStatus = '';
    let sortBy = 'created_at';
    let sortOrder = 'desc';
    let isFiltersOpen = false;
    let uploadModalOpen = false;
    let previewModalOpen = false;
    let activeDocument = null;
    let confirmDeleteModal = false;
    let documentToDelete = null;
    let refreshing = false;
    
    // Reactive state for RTL support
    $: isRTL = $language === 'ar';
    
    // Access rights check
    $: canEdit = $isAuthenticated && $currentUser && (
      $currentUser.isAdmin || ($currentUser.roles && 
      ($currentUser.roles.includes('agent') || $currentUser.roles.includes('admin')))
    );
    
    // Document types
    const documentTypes = [
      { value: '', label: $t('general.all') },
      { value: 'title_deed', label: $t('documents.types.title_deed') },
      { value: 'floor_plan', label: $t('documents.types.floor_plan') },
      { value: 'ownership_cert', label: $t('documents.types.ownership_cert') },
      { value: 'survey', label: $t('documents.types.survey') },
      { value: 'building_permit', label: $t('documents.types.building_permit') },
      { value: 'tax_document', label: $t('documents.types.tax_document') },
      { value: 'appraisal', label: $t('documents.types.appraisal') },
      { value: 'inspection', label: $t('documents.types.inspection') },
      { value: 'other', label: $t('documents.types.other') }
    ];
    
    // Verification statuses
    const verificationStatuses = [
      { value: '', label: $t('general.all') },
      { value: 'unverified', label: $t('documents.status.unverified') },
      { value: 'pending', label: $t('documents.status.pending') },
      { value: 'verified', label: $t('documents.status.verified') },
      { value: 'rejected', label: $t('documents.status.rejected') }
    ];
    
    // Sorting options
    const sortOptions = [
      { value: 'created_at', label: $t('documents.sort.upload_date') },
      { value: 'document_type', label: $t('documents.sort.document_type') },
      { value: 'verification_status', label: $t('documents.sort.verification_status') }
    ];
    
    // Filter and sort documents reactively
    $: {
      filteredDocuments = [...documents];
      
      // Apply search filter
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        filteredDocuments = filteredDocuments.filter(doc => 
          (doc.title && doc.title.toLowerCase().includes(query)) ||
          (doc.document_number && doc.document_number.toLowerCase().includes(query)) ||
          (doc.document_type_display && doc.document_type_display.toLowerCase().includes(query))
        );
      }
      
      // Apply document type filter
      if (filterType) {
        filteredDocuments = filteredDocuments.filter(doc => doc.document_type === filterType);
      }
      
      // Apply verification status filter
      if (filterStatus) {
        filteredDocuments = filteredDocuments.filter(doc => doc.verification_status === filterStatus);
      }
      
      // Apply sorting
      filteredDocuments = filteredDocuments.sort((a, b) => {
        let comparison = 0;
        
        switch (sortBy) {
          case 'created_at':
            comparison = new Date(a.created_at) - new Date(b.created_at);
            break;
          case 'document_type':
            comparison = a.document_type_display?.localeCompare(b.document_type_display) || 0;
            break;
          case 'verification_status':
            comparison = a.verification_status?.localeCompare(b.verification_status) || 0;
            break;
          default:
            comparison = new Date(a.created_at) - new Date(b.created_at);
        }
        
        return sortOrder === 'desc' ? -comparison : comparison;
      });
    }
    
    // Handle refresh documents
    async function refreshDocuments() {
      if (!propertyId || refreshing) return;
      
      refreshing = true;
      
      try {
        const response = await api.get(`/properties/${propertyId}/documents`);
        
        if (response?.data?.results) {
          dispatch('update', { documents: response.data.results });
        }
      } catch (err) {
        console.error('Failed to refresh documents:', err);
        toast.error($t('documents.refresh_error'));
      } finally {
        refreshing = false;
      }
    }
    
    // Handle document preview
    function previewDocument(document) {
      activeDocument = document;
      previewModalOpen = true;
    }
    
    // Handle document download
    function downloadDocument(document) {
      if (!document.main_file_url) {
        toast.error($t('documents.download_unavailable'));
        return;
      }
      
      // Create a temporary anchor element to download the file
      const link = document.createElement('a');
      link.href = document.main_file_url;
      link.target = '_blank';
      link.download = document.title || document.document_number || 'document';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast.success($t('documents.download_started'));
    }
    
    // Handle delete document request
    function confirmDelete(document) {
      documentToDelete = document;
      confirmDeleteModal = true;
    }
    
    // Handle document deletion
    async function deleteDocument() {
      if (!documentToDelete) {
        confirmDeleteModal = false;
        return;
      }
      
      try {
        await api.delete(`/documents/${documentToDelete.id}`);
        
        // Filter out the deleted document
        const updatedDocuments = documents.filter(doc => doc.id !== documentToDelete.id);
        dispatch('update', { documents: updatedDocuments });
        
        toast.success($t('documents.delete_success'));
      } catch (err) {
        console.error('Failed to delete document:', err);
        toast.error($t('documents.delete_error'));
      } finally {
        documentToDelete = null;
        confirmDeleteModal = false;
      }
    }
    
    // Handle upload modal
    function openUploadModal() {
      uploadModalOpen = true;
    }
    
    // Get badge type based on verification status
    function getBadgeType(status) {
      switch (status) {
        case 'verified':
          return 'success';
        case 'pending':
          return 'warning';
        case 'rejected':
          return 'error';
        default:
          return 'info';
      }
    }
    
    // Get document icon based on document type
    function getDocumentIcon(type) {
      switch (type) {
        case 'title_deed':
          return 'document-text';
        case 'floor_plan':
          return 'template';
        case 'ownership_cert':
          return 'certificate';
        case 'survey':
          return 'map';
        case 'building_permit':
          return 'clipboard-check';
        case 'tax_document':
          return 'cash';
        case 'appraisal':
          return 'chart-bar';
        case 'inspection':
          return 'clipboard-list';
        default:
          return 'document';
      }
    }
    
    // Reset filters
    function resetFilters() {
      searchQuery = '';
      filterType = '';
      filterStatus = '';
      sortBy = 'created_at';
      sortOrder = 'desc';
    }
    
    // Toggle filters panel visibility
    function toggleFilters() {
      isFiltersOpen = !isFiltersOpen;
    }
    
    // Format file size for display
    function formatFileSize(bytes) {
      if (!bytes || bytes === 0) return '0 Bytes';
      
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    onMount(() => {
      // If propertyId is provided and no documents were passed, fetch them
      if (propertyId && documents.length === 0 && !loading) {
        refreshDocuments();
      }
    });
  </script>
  
  <div class="documents-list-container" class:rtl={isRTL}>
    <!-- Header with filters -->
    {#if filterEnabled}
      <div class="mb-4 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div class="w-full md:w-auto">
          <Input
            type="search"
            placeholder={$t('documents.search_placeholder')}
            bind:value={searchQuery}
            icon="search"
            clearable={true}
            size="sm"
          />
        </div>
        
        <div class="flex flex-wrap items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            on:click={toggleFilters}
            class="mr-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
            </svg>
            {$t('documents.filters')}
            {#if filterType || filterStatus}
              <span class="ml-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-xs text-white">
                {(filterType ? 1 : 0) + (filterStatus ? 1 : 0)}
              </span>
            {/if}
          </Button>
          
          {#if refreshing}
            <Spinner size="sm" />
          {:else}
            <Button
              variant="ghost"
              size="sm"
              title={$t('documents.refresh')}
              on:click={refreshDocuments}
              disabled={!propertyId}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21.5 2v6h-6"></path>
                <path d="M2.5 22v-6h6"></path>
                <path d="M21.5 8c-1.333 1.667-4 3-8 3-3 0-6-1-8-3"></path>
                <path d="M2.5 16c1.333-1.667 4-3 8-3 3 0 6 1 8 3"></path>
              </svg>
            </Button>
          {/if}
          
          {#if showUpload && canEdit}
            <Button
              variant="primary"
              size="sm"
              on:click={openUploadModal}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
              </svg>
              {$t('documents.upload')}
            </Button>
          {/if}
        </div>
      </div>
    {/if}
    
    <!-- Advanced Filters Panel -->
    {#if isFiltersOpen}
      <div 
        class="mb-4 rounded-lg border border-neutral-200 bg-neutral-50 p-4 dark:border-neutral-700 dark:bg-neutral-800/50"
        transition:slide={{ duration: 200 }}
      >
        <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div>
            <label for="document-type-filter" class="mb-1 block text-sm font-medium">
              {$t('documents.document_type')}
            </label>
            <Select
              id="document-type-filter"
              bind:value={filterType}
              options={documentTypes}
              placeholder={$t('documents.select_type')}
            />
          </div>
          
          <div>
            <label for="verification-status-filter" class="mb-1 block text-sm font-medium">
              {$t('documents.verification_status')}
            </label>
            <Select
              id="verification-status-filter"
              bind:value={filterStatus}
              options={verificationStatuses}
              placeholder={$t('documents.select_status')}
            />
          </div>
          
          <div>
            <label for="sort-by-filter" class="mb-1 block text-sm font-medium">
              {$t('general.sort')}
            </label>
            <div class="flex items-center gap-2">
              <Select
                id="sort-by-filter"
                bind:value={sortBy}
                options={sortOptions}
                class="flex-1"
              />
              
              <Button
                variant="outline"
                size="sm"
                title={sortOrder === 'asc' ? $t('general.sort_ascending') : $t('general.sort_descending')}
                on:click={() => sortOrder = sortOrder === 'asc' ? 'desc' : 'asc'}
                class="!px-2"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" class:rotate-180={sortOrder === 'asc'} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <polyline points="19 12 12 19 5 12"></polyline>
                </svg>
              </Button>
            </div>
          </div>
        </div>
        
        <div class="mt-4 flex justify-end">
          <Button
            variant="ghost"
            size="sm"
            on:click={resetFilters}
          >
            {$t('general.reset')}
          </Button>
        </div>
      </div>
    {/if}
    
    <!-- Documents List -->
    <div class="documents-list" class:max-h-96={maxHeight} class:overflow-y-auto={maxHeight}>
      {#if loading}
        <div class="flex items-center justify-center py-8">
          <Spinner size="lg" text={$t('general.loading')} />
        </div>
      {:else if error}
        <div class="rounded-lg bg-error/10 p-4 text-error">
          <p class="font-medium">{$t('documents.error_loading')}</p>
          <p class="mt-1 text-sm">{error}</p>
        </div>
      {:else if filteredDocuments.length === 0}
        <EmptyState
          icon="document"
          title={$t('documents.no_documents_found')}
          message={emptyStateText}
          class="py-8"
        >
          {#if showUpload && canEdit}
            <Button
              variant="primary"
              on:click={openUploadModal}
              class="mt-4"
            >
              {$t('documents.upload_first')}
            </Button>
          {/if}
        </EmptyState>
      {:else}
        <div class="rounded-lg border border-neutral-200 dark:border-neutral-700 overflow-hidden">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-neutral-200 dark:divide-neutral-700">
              <thead class="bg-neutral-50 dark:bg-neutral-800">
                <tr>
                  <th scope="col" class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-neutral-500 dark:text-neutral-400">
                    {$t('documents.document')}
                  </th>
                  <th scope="col" class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-neutral-500 dark:text-neutral-400">
                    {$t('documents.document_type')}
                  </th>
                  <th scope="col" class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-neutral-500 dark:text-neutral-400">
                    {$t('documents.status')}
                  </th>
                  <th scope="col" class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-neutral-500 dark:text-neutral-400">
                    {$t('documents.uploaded')}
                  </th>
                  {#if showActions}
                    <th scope="col" class="relative px-4 py-3">
                      <span class="sr-only">{$t('general.actions')}</span>
                    </th>
                  {/if}
                </tr>
              </thead>
              <tbody class="divide-y divide-neutral-200 bg-white dark:divide-neutral-700 dark:bg-neutral-900">
                {#each filteredDocuments as document}
                  <tr class="hover:bg-neutral-50 dark:hover:bg-neutral-800/50">
                    <td class="whitespace-nowrap px-4 py-4">
                      <div class="flex items-center">
                        <div class="flex-shrink-0 h-10 w-10 rounded-lg bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center text-neutral-500 dark:text-neutral-400">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </div>
                        <div class="ml-4">
                          <div class="text-sm font-medium text-neutral-900 dark:text-white">
                            {document.title || document.document_number || $t('documents.untitled')}
                          </div>
                          <div class="text-xs text-neutral-500 dark:text-neutral-400">
                            {document.document_number}
                          </div>
                          {#if document.file_size}
                            <div class="text-xs text-neutral-500 dark:text-neutral-400 mt-1">
                              {formatFileSize(document.file_size)}
                            </div>
                          {/if}
                        </div>
                      </div>
                    </td>
                    <td class="whitespace-nowrap px-4 py-4">
                      <div class="text-sm text-neutral-900 dark:text-neutral-300">
                        {document.document_type_display}
                      </div>
                    </td>
                    <td class="whitespace-nowrap px-4 py-4">
                      <Badge 
                        type={getBadgeType(document.verification_status)}
                        size="sm"
                      >
                        {document.verification_status_display}
                      </Badge>
                      {#if document.is_expired}
                        <Badge 
                          type="error"
                          size="sm"
                          class="ml-2"
                        >
                          {$t('documents.expired')}
                        </Badge>
                      {/if}
                    </td>
                    <td class="whitespace-nowrap px-4 py-4 text-sm text-neutral-500 dark:text-neutral-400">
                      <div>
                        {formatDate(document.created_at)}
                      </div>
                      {#if document.uploaded_by}
                        <div class="text-xs mt-1">
                          {$t('documents.by')} {document.uploaded_by.full_name || document.uploaded_by.email}
                        </div>
                      {/if}
                    </td>
                    {#if showActions}
                      <td class="whitespace-nowrap px-4 py-4 text-right text-sm font-medium">
                        <div class="flex items-center justify-end space-x-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            title={$t('documents.preview')}
                            on:click={() => previewDocument(document)}
                            disabled={!document.main_file_url}
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                            </svg>
                          </Button>
                          
                          <Button
                            variant="ghost"
                            size="sm"
                            title={$t('documents.download')}
                            on:click={() => downloadDocument(document)}
                            disabled={!document.main_file_url}
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                            </svg>
                          </Button>
                          
                          {#if canEdit}
                            <Button
                              variant="ghost"
                              size="sm"
                              title={$t('general.delete')}
                              on:click={() => confirmDelete(document)}
                              class="text-error hover:text-error"
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </Button>
                          {/if}
                        </div>
                      </td>
                    {/if}
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      {/if}
    </div>
  </div>
  
  <!-- Document Preview Modal -->
  {#if previewModalOpen && activeDocument}
    <div 
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
      transition:fade={{ duration: 200 }}
      on:click|self={() => previewModalOpen = false}
    >
      <div 
        class="w-full max-w-4xl max-h-[90vh] bg-white dark:bg-neutral-900 rounded-lg shadow-xl overflow-hidden"
        transition:slide={{ duration: 250, y: 20 }}
      >
        <div class="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-700 px-6 py-4">
          <h3 class="text-lg font-semibold text-neutral-900 dark:text-white">
            {activeDocument.title || activeDocument.document_number || $t('documents.document_preview')}
          </h3>
          <button 
            type="button"
            class="rounded-full p-1 text-neutral-400 hover:bg-neutral-100 hover:text-neutral-500 dark:text-neutral-400 dark:hover:bg-neutral-800 dark:hover:text-neutral-300"
            on:click={() => previewModalOpen = false}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="h-[60vh] bg-neutral-100 dark:bg-neutral-800 overflow-hidden">
          {#if activeDocument.main_file_url}
            <iframe
              src={activeDocument.main_file_url}
              title={activeDocument.title || activeDocument.document_number || "Document preview"}
              class="w-full h-full border-0"
              sandbox="allow-scripts allow-same-origin"
            ></iframe>
          {:else}
            <div class="flex h-full items-center justify-center">
              <p class="text-neutral-500 dark:text-neutral-400">
                {$t('documents.preview_unavailable')}
              </p>
            </div>
          {/if}
        </div>
        
        <div class="border-t border-neutral-200 dark:border-neutral-700 px-6 py-4">
          <div class="flex flex-wrap items-center justify-between gap-4">
            <div>
              <Badge type={getBadgeType(activeDocument.verification_status)}>
                {activeDocument.verification_status_display}
              </Badge>
              <span class="ml-3 text-sm text-neutral-500 dark:text-neutral-400">
                {activeDocument.document_type_display}
              </span>
            </div>
            
            <div class="flex space-x-2">
              <Button
                variant="outline"
                on:click={() => previewModalOpen = false}
              >
                {$t('general.close')}
              </Button>
              
              <Button
                variant="primary"
                on:click={() => downloadDocument(activeDocument)}
                disabled={!activeDocument.main_file_url}
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                {$t('documents.download')}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  {/if}
  
  <!-- Document Delete Confirmation Modal -->
  {#if confirmDeleteModal && documentToDelete}
    <div 
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
      transition:fade={{ duration: 200 }}
      on:click|self={() => confirmDeleteModal = false}
    >
      <div 
        class="w-full max-w-md bg-white dark:bg-neutral-900 rounded-lg shadow-xl overflow-hidden"
        transition:slide={{ duration: 250, y: 20 }}
      >
        <div class="px-6 py-4">
          <div class="flex items-center text-error">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h3 class="text-lg font-semibold text-error">
              {$t('documents.confirm_delete')}
            </h3>
          </div>
          
          <p class="mt-4 text-neutral-700 dark:text-neutral-300">
            {$t('documents.delete_warning')} <strong>{documentToDelete.title || documentToDelete.document_number || $t('documents.this_document')}</strong>?
          </p>
          
          <p class="mt-2 text-sm text-neutral-500 dark:text-neutral-400">
            {$t('documents.delete_permanent')}
          </p>
        </div>
        
        <div class="bg-neutral-50 dark:bg-neutral-800 px-6 py-4 flex justify-end space-x-2">
          <Button
            variant="outline"
            on:click={() => confirmDeleteModal = false}
          >
            {$t('general.cancel')}
          </Button>
          
          <Button
            variant="error"
            on:click={deleteDocument}
          >
            {$t('general.delete')}
          </Button>
        </div>
      </div>
    </div>
  {/if}
  
  <style>
    /* RTL Support */
    .rtl {
      direction: rtl;
      text-align: right;
    }
    
    .rtl th,
    .rtl td {
      text-align: right;
    }
    
    .rtl .ml-4 {
      margin-left: 0;
      margin-right: 1rem;
    }
    
    .rtl .ml-2,
    .rtl .ml-3 {
      margin-left: 0;
      margin-right: 0.5rem;
    }
    
    .rtl .mr-1\.5,
    .rtl .mr-2 {
      margin-right: 0;
      margin-left: 0.5rem;
    }
    
    .rtl .space-x-2 > * + * {
      margin-left: 0;
      margin-right: 0.5rem;
    }
    
    /* Custom scrollbar for document list when height is limited */
    .documents-list::-webkit-scrollbar {
      width: 6px;
    }
    
    .documents-list::-webkit-scrollbar-track {
      @apply bg-neutral-100 dark:bg-neutral-800;
    }
    
    .documents-list::-webkit-scrollbar-thumb {
      @apply bg-neutral-300 dark:bg-neutral-600;
      border-radius: 3px;
    }
    
    .documents-list::-webkit-scrollbar-thumb:hover {
      @apply bg-neutral-400 dark:bg-neutral-500;
    }
  </style>