<!-- src/lib/components/MediaUploader.svelte -->
<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { t, locale } from '$lib/i18n'; // Fixed import path
  
  export let maxFiles = 10;
  export let maxSize = 10 * 1024 * 1024; // 10MB
  export let allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
  export let disabled = false;
  export let uploading = false;
  export let progress = 0;
  export let multiple = true;

  const dispatch = createEventDispatcher();
  
  let files = [];
  let dragActive = false;
  let errors = [];
  let fileInput;
  let previewUrls = new Map();

  onMount(() => {
    return () => {
      // Cleanup preview URLs on component destroy
      previewUrls.forEach(url => URL.revokeObjectURL(url));
    };
  });

  function generatePreview(file) {
    if (file.type.startsWith('image/')) {
      try {
        const url = URL.createObjectURL(file);
        previewUrls.set(file, url);
        return url;
      } catch (err) {
        console.error('Error creating object URL for preview:', err);
        return null;
      }
    }
    return null;
  }

  function validateFile(file) {
    if (!allowedTypes.includes(file.type)) {
      return `${file.name}: ${$t('mediaUploader.invalidType')}`;
    }
    
    if (file.size > maxSize) {
      return `${file.name}: ${$t('mediaUploader.fileTooLarge', { size: Math.round(maxSize / 1024 / 1024) })}`;
    }
    
    return null;
  }

  function handleFiles(newFiles) {
    if (disabled || uploading) return;

    errors = [];
    const validFiles = [];

    for (const file of newFiles) {
      const error = validateFile(file);
      if (error) {
        errors.push(error);
      } else {
        validFiles.push(file);
        generatePreview(file);
      }
    }

    if (!multiple) {
      files = validFiles.slice(0, 1);
    } else if (files.length + validFiles.length > maxFiles) {
      errors.push($t('mediaUploader.tooManyFiles', { max: maxFiles }));
      files = [...files, ...validFiles.slice(0, maxFiles - files.length)];
    } else {
      files = [...files, ...validFiles];
    }

    dispatch('change', { files, errors });
  }

  function handleDrop(event) {
    event.preventDefault();
    dragActive = false;
    
    if (event.dataTransfer?.files) {
      handleFiles(Array.from(event.dataTransfer.files));
    }
  }

  function handleDragOver(event) {
    event.preventDefault();
    dragActive = true;
  }
  
  function handleDragLeave() {
    dragActive = false;
  }

  function removeFile(index) {
    const file = files[index];
    if (previewUrls.has(file)) {
      URL.revokeObjectURL(previewUrls.get(file));
      previewUrls.delete(file);
    }
    
    files = files.filter((_, i) => i !== index);
    dispatch('change', { files, errors });
  }
</script>

<div class="space-y-4">
  <!-- Drop Zone -->
  <div 
    class="relative border-2 border-dashed p-6 rounded-lg text-center
      {dragActive ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' : 'border-gray-300 dark:border-gray-600'}
      {disabled || uploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}"
    on:drop={handleDrop}
    on:dragover={handleDragOver}
    on:dragleave={handleDragLeave}
  >
    <input
      type="file"
      bind:this={fileInput}
      class="hidden"
      {multiple}
      accept={allowedTypes.join(',')}
      on:change={(e) => handleFiles(Array.from(e.target.files))}
      disabled={disabled || uploading}
    />

    {#if uploading}
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
          {$t('mediaUploader.uploading')} ({progress}%)
        </p>
      </div>
    {:else}
      <div class="text-center">
        <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
          <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
          {$t('mediaUploader.dragAndDrop')}
        </p>
        <button
          type="button"
          class="mt-2 inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          on:click={() => fileInput.click()} disabled={disabled || uploading}
          >
            {$t('mediaUploader.selectFiles')}
          </button>
        </div>
      {/if}
    </div>
  
    <!-- Errors -->
    {#if errors.length > 0}
      <div class="text-sm text-red-600 dark:text-red-400">
        {#each errors as error}
          <p>{error}</p>
        {/each}
      </div>
    {/if}
  
    <!-- Preview -->
    {#if files.length > 0}
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
        {#each files as file, index}
          <div class="relative group">
            <div class="aspect-w-3 aspect-h-2 rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800">
              {#if file.type.startsWith('image/')}
                <img
                  src={previewUrls.get(file)}
                  alt={file.name}
                  class="object-cover"
                />
              {:else}
                <div class="flex items-center justify-center h-full">
                  <svg class="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
              {/if}
            </div>
            
            <button
              type="button"
              class="absolute top-2 right-2 p-1 rounded-full bg-red-100 text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"
              on:click={() => removeFile(index)}
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400 truncate">
              {file.name}
            </p>
          </div>
        {/each}
      </div>
    {/if}
  </div>