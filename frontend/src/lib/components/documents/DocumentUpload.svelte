<!-- src/lib/components/documents/DocumentUpload.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    import { fade, fly } from 'svelte/transition';
    import { t, language } from '$lib/i18n';
    import { toast } from '$lib/stores/toast';
    import { api } from '$lib/services/api';
    
    // UI Components
    import Button from '$lib/components/ui/Button.svelte';
    import Input from '$lib/components/ui/Input.svelte';
    import Select from '$lib/components/ui/Select.svelte';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    
    const dispatch = createEventDispatcher();
    
    // Props
    export let propertyId = null;
    export let isOpen = false;
    export let maxFileSize = 10; // In MB
    export let allowedFileTypes = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xls', 'xlsx'];
    
    // State
    let files = [];
    let documentTitle = '';
    let documentType = '';
    let documentDescription = '';
    let expiryDate = '';
    let uploading = false;
    let uploadProgress = 0;
    let dragActive = false;
    let errors = {};
    
    // Reactive state for RTL support
    $: isRTL = $language === 'ar';
    
    // Document types options
    const documentTypes = [
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
    
    // Reset form
    function resetForm() {
      files = [];
      documentTitle = '';
      documentType = '';
      documentDescription = '';
      expiryDate = '';
      uploading = false;
      uploadProgress = 0;
      errors = {};
    }
    
    // Close modal
    function close() {
      isOpen = false;
      resetForm();
    }
    
    // Handle drag events
    function handleDragEnter(e) {
      e.preventDefault();
      e.stopPropagation();
      dragActive = true;
    }
    
    function handleDragLeave(e) {
      e.preventDefault();
      e.stopPropagation();
      dragActive = false;
    }
    
    function handleDragOver(e) {
      e.preventDefault();
      e.stopPropagation();
      dragActive = true;
    }
    
    function handleDrop(e) {
      e.preventDefault();
      e.stopPropagation();
      dragActive = false;
      
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFiles(e.dataTransfer.files);
      }
    }
    
    // Handle file input change
    function handleFileChange(e) {
      if (e.target.files && e.target.files.length > 0) {
        handleFiles(e.target.files);
      }
    }
    
    // Process selected files
    function handleFiles(fileList) {
      const newFiles = Array.from(fileList);
      
      // Validate file types and sizes
      const validFiles = newFiles.filter(file => {
        const extension = file.name.split('.').pop().toLowerCase();
        const isValidType = allowedFileTypes.includes(extension);
        const isValidSize = file.size <= maxFileSize * 1024 * 1024; // Convert MB to bytes
        
        if (!isValidType) {
          toast.error($t('documents.error_file_type', { filename: file.name }));
          return false;
        }
        
        if (!isValidSize) {
          toast.error($t('documents.error_file_size', { 
            filename: file.name, 
            maxSize: maxFileSize 
          }));
          return false;
        }
        
        return true;
      });
      
      if (validFiles.length > 0) {
        files = validFiles;
        
        // If no title is set, use the file name as the default title
        if (!documentTitle && files.length === 1) {
          documentTitle = files[0].name.split('.')[0];
        }
      }
    }
    
    // Remove selected file
    function removeFile(index) {
      files = files.filter((_, i) => i !== index);
    }
    
    // Format file size for display
    function formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Validate form
    function validateForm() {
      errors = {};
      let isValid = true;
      
      if (!documentTitle.trim()) {
        errors.title = $t('documents.error_title_required');
        isValid = false;
      }
      
      if (!documentType) {
        errors.type = $t('documents.error_type_required');
        isValid = false;
      }
      
      if (files.length === 0) {
        errors.files = $t('documents.error_file_required');
        isValid = false;
      }
      
      return isValid;
    }
    
    // Handle form submission
    async function handleSubmit() {
      if (!validateForm()) {
        return;
      }
      
      uploading = true;
      uploadProgress = 0;
      
      try {
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('title', documentTitle);
        formData.append('document_type', documentType);
        
        if (documentDescription) {
          formData.append('description', documentDescription);
        }
        
        if (expiryDate) {
          formData.append('expiry_date', expiryDate);
        }
        
        if (propertyId) {
          formData.append('related_property', propertyId);
        }
        
        // Append files
        for (let i = 0; i < files.length; i++) {
          formData.append('file', files[i]);
        }
        
        // Upload with progress tracking
        const response = await api.post('/documents/', formData, {
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            uploadProgress = percentCompleted;
          }
        });
        
        if (response?.data?.document) {
          toast.success($t('documents.upload_success'));
          dispatch('upload', { document: response.data.document });
          close();
        } else {
          throw new Error('Invalid response format');
        }
      } catch (err) {
        console.error('Document upload failed:', err);
        toast.error($t('documents.upload_error'));
        
        // Handle specific error messages from API
        if (err.response?.data?.errors) {
          errors = { ...errors, ...err.response.data.errors };
        }
      } finally {
        uploading = false;
      }
    }
  </script>
  
  {#if isOpen}
    <div 
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
      transition:fade={{ duration: 200 }}
      on:click|self={close}
    >
      <div 
        class="w-full max-w-2xl bg-white dark:bg-neutral-900 rounded-lg shadow-xl overflow-hidden"
        transition:fly={{ duration: 250, y: 20 }}
        class:rtl={isRTL}
      >
        <div class="px-6 py-4 border-b border-neutral-200 dark:border-neutral-700">
          <h3 class="text-lg font-semibold text-neutral-900 dark:text-white">
            {$t('documents.upload_document')}
          </h3>
        </div>
        
        <div class="p-6">
          <form on:submit|preventDefault={handleSubmit}>
            <!-- Document Title -->
            <div class="mb-4">
              <Input
                type="text"
                label={$t('documents.document_title')}
                placeholder={$t('documents.title_placeholder')}
                bind:value={documentTitle}
                error={errors.title}
                required
              />
            </div>
            
            <!-- Document Type -->
            <div class="mb-4">
              <Select
                label={$t('documents.document_type')}
                placeholder={$t('documents.select_type')}
                options={documentTypes}
                bind:value={documentType}
                error={errors.type}
                required
              />
            </div>
            
            <!-- Description (Optional) -->
            <div class="mb-4">
              <label for="document-description" class="mb-1 block text-sm font-medium text-neutral-700 dark:text-neutral-300">
                {$t('documents.description')} <span class="text-neutral-400">({$t('general.optional')})</span>
              </label>
              <textarea
                id="document-description"
                class="w-full rounded-md border border-neutral-300 bg-white px-3 py-2 text-neutral-900 placeholder-neutral-400 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary dark:border-neutral-700 dark:bg-neutral-800 dark:text-white dark:placeholder-neutral-500"
                rows="3"
                placeholder={$t('documents.description_placeholder')}
                bind:value={documentDescription}
              ></textarea>
            </div>
            
            <!-- Expiry Date (Optional) -->
            <div class="mb-4">
              <Input
                type="date"
                label={$t('documents.expiry_date')}
                helperText={$t('documents.expiry_date_helper')}
                bind:value={expiryDate}
              />
            </div>
            
            <!-- File Upload Area -->
            <div class="mb-4">
              <label class="mb-1 block text-sm font-medium text-neutral-700 dark:text-neutral-300">
                {$t('documents.upload_files')}*
              </label>
              
              <!-- Drag & Drop Area -->
              <div 
                class="border-2 border-dashed rounded-lg p-4 text-center transition-colors"
                class:border-neutral-300={!dragActive && files.length === 0 && !errors.files}
                class:dark:border-neutral-700={!dragActive && files.length === 0 && !errors.files}
                class:border-primary={dragActive && !errors.files}
                class:dark:border-primary={dragActive && !errors.files}
                class:border-error={errors.files}
                class:dark:border-error={errors.files}
                class:bg-neutral-50={dragActive && !errors.files}
                class:dark:bg-neutral-800/50={dragActive && !errors.files}
                on:dragenter={handleDragEnter}
                on:dragleave={handleDragLeave}
                on:dragover={handleDragOver}
                on:drop={handleDrop}
              >
                {#if files.length === 0}
                  <div class="py-8">
                    <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    
                    <p class="mt-3 text-sm text-neutral-600 dark:text-neutral-400">
                      {$t('documents.drag_drop')}
                    </p>
                    
                    <div class="mt-3">
                      <label for="file-upload" class="cursor-pointer rounded-md bg-white px-4 py-2 text-sm font-medium text-primary hover:bg-neutral-50 dark:bg-neutral-800 dark:hover:bg-neutral-700">
                        {$t('documents.select_files')}
                      </label>
                      <input 
                        id="file-upload" 
                        name="file-upload" 
                        type="file" 
                        class="sr-only" 
                        accept={allowedFileTypes.map(type => `.${type}`).join(',')}
                        on:change={handleFileChange}
                        multiple={false}
                      />
                    </div>
                    
                    <p class="mt-2 text-xs text-neutral-500 dark:text-neutral-500">
                      {$t('documents.allowed_types')}: {allowedFileTypes.join(', ')}
                    </p>
                    <p class="text-xs text-neutral-500 dark:text-neutral-500">
                      {$t('documents.max_size')}: {maxFileSize} MB
                    </p>
                  </div>
                {:else}
                  <!-- Selected Files List -->
                  <ul class="divide-y divide-neutral-200 dark:divide-neutral-700">
                    {#each files as file, i}
                      <li class="flex items-center justify-between py-3 first:pt-0 last:pb-0">
                        <div class="flex items-center">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          <div class="ml-3 text-left">
                            <p class="text-sm font-medium text-neutral-900 dark:text-white">
                              {file.name}
                            </p>
                            <p class="text-xs text-neutral-500 dark:text-neutral-400">
                              {formatFileSize(file.size)}
                            </p>
                          </div>
                        </div>
                        <button 
                          type="button"
                          class="rounded-full p-1 text-neutral-400 hover:bg-neutral-100 hover:text-neutral-500 dark:text-neutral-400 dark:hover:bg-neutral-800 dark:hover:text-neutral-300"
                          on:click={() => removeFile(i)}
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </li>
                    {/each}
                  </ul>
                  
                  <!-- Add more files button -->
                  <div class="mt-4">
                    <label for="additional-files" class="cursor-pointer inline-flex items-center text-sm font-medium text-primary hover:text-primary-dark">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                      </svg>
                      {$t('documents.add_more_files')}
                    </label>
                    <input 
                      id="additional-files" 
                      type="file" 
                      class="sr-only" 
                      accept={allowedFileTypes.map(type => `.${type}`).join(',')}
                      on:change={handleFileChange}
                      multiple={false}
                    />
                  </div>
                {/if}
              </div>
              
              {#if errors.files}
                <p class="mt-1 text-sm text-error">{errors.files}</p>
              {/if}
            </div>
            
            {#if uploading}
              <!-- Upload Progress -->
              <div class="mb-4">
                <div class="flex items-center justify-between mb-1">
                  <span class="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                    {$t('documents.uploading')}
                  </span>
                  <span class="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                    {uploadProgress}%
                  </span>
                </div>
                <div class="w-full bg-neutral-200 rounded-full h-2.5 dark:bg-neutral-700">
                  <div class="bg-primary h-2.5 rounded-full" style="width: {uploadProgress}%"></div>
                </div>
              </div>
            {/if}
            
            <!-- Form Buttons -->
            <div class="mt-6 flex justify-end space-x-3">
              <Button
                variant="outline"
                type="button"
                on:click={close}
                disabled={uploading}
              >
                {$t('general.cancel')}
              </Button>
              
              <Button
                variant="primary"
                type="submit"
                loading={uploading}
                disabled={uploading}
              >
                {uploading ? $t('documents.uploading') : $t('documents.upload')}
              </Button>
            </div>
          </form>
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
    
    .rtl .ml-3 {
      margin-left: 0;
      margin-right: 0.75rem;
    }
    
    .rtl .mr-1 {
      margin-right: 0;
      margin-left: 0.25rem;
    }
    
    .rtl .space-x-3 > * + * {
      margin-left: 0;
      margin-right: 0.75rem;
    }
    
    .rtl label,
    .rtl input,
    .rtl textarea {
      text-align: right;
    }
  </style>