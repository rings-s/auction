<!-- src/lib/components/properties/PropertyMediaUploader.svelte -->
<script>
    import { createEventDispatcher } from 'svelte';
    import { t, language } from '$lib/i18n';
    import { toast } from '$lib/stores/toast';
    
    // UI Components
    import Button from '$lib/components/ui/Button.svelte';
    import Card from '$lib/components/ui/Card.svelte';
    
    const dispatch = createEventDispatcher();
    
    // Props
    export let images = []; // Array of image files or URLs
    export let mainImage = null; // Index of main image or URL
    export let maxImages = 10;
    export let maxFileSize = 5; // In MB
    export let allowedFileTypes = ['jpg', 'jpeg', 'png', 'webp'];
    
    // State
    let dragActive = false;
    let imagePreviews = [];
    let isRTL = false;
    
    // Reactive state for RTL support
    $: isRTL = $language === 'ar';
    
    // Update image previews whenever images change
    $: {
      updateImagePreviews();
    }
    
    // Generate image previews
    function updateImagePreviews() {
      // Clear previous previews
      imagePreviews = [];
      
      // Create preview for each image
      if (images && images.length > 0) {
        images.forEach((image, index) => {
          let previewUrl;
          
          if (typeof image === 'string') {
            // Image is a URL
            previewUrl = image;
          } else if (image instanceof File) {
            // Image is a File object
            previewUrl = URL.createObjectURL(image);
          }
          
          if (previewUrl) {
            imagePreviews.push({
              url: previewUrl,
              isMain: mainImage === index || mainImage === image
            });
          }
        });
      }
    }
    
    // Handle file selection
    function handleFileSelect(event) {
      if (event.target.files && event.target.files.length > 0) {
        handleFiles(event.target.files);
      }
    }
    
    // Handle drag and drop
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
    
    // Process the files
    function handleFiles(fileList) {
      const newFiles = Array.from(fileList);
      
      // Check if max images limit is reached
      if (images.length + newFiles.length > maxImages) {
        toast.error($t('properties.media.max_images_error', { max: maxImages }));
        return;
      }
      
      // Validate files
      const validFiles = newFiles.filter(file => {
        // Check file type
        const extension = file.name.split('.').pop().toLowerCase();
        if (!allowedFileTypes.includes(extension)) {
          toast.error($t('properties.media.invalid_type_error', { filename: file.name }));
          return false;
        }
        
        // Check file size
        const fileSizeMB = file.size / (1024 * 1024);
        if (fileSizeMB > maxFileSize) {
          toast.error($t('properties.media.file_too_large_error', { 
            filename: file.name,
            size: fileSizeMB.toFixed(2),
            max: maxFileSize
          }));
          return false;
        }
        
        return true;
      });
      
      // Add valid files to images array
      if (validFiles.length > 0) {
        images = [...images, ...validFiles];
        
        // Set the first image as main if none is selected
        if (mainImage === null && images.length > 0) {
          mainImage = 0;
        }
        
        // Update parent component
        dispatch('update', { images, mainImage });
      }
    }
    
    // Set an image as the main image
    function setMainImage(index) {
      mainImage = index;
      updateImagePreviews();
      dispatch('update', { images, mainImage });
    }
    
    // Remove an image
    function removeImage(index) {
      // Remove the image from the array
      images = images.filter((_, i) => i !== index);
      
      // Update main image index if needed
      if (mainImage === index) {
        mainImage = images.length > 0 ? 0 : null;
      } else if (mainImage > index) {
        mainImage--;
      }
      
      // Update parent component
      dispatch('update', { images, mainImage });
    }
    
    // Reorder images by drag and drop
    function moveImage(fromIndex, toIndex) {
      if (fromIndex === toIndex) return;
      
      const newImages = [...images];
      const [movedItem] = newImages.splice(fromIndex, 1);
      newImages.splice(toIndex, 0, movedItem);
      
      // Update main image index if needed
      if (mainImage === fromIndex) {
        mainImage = toIndex;
      } else if (mainImage > fromIndex && mainImage <= toIndex) {
        mainImage--;
      } else if (mainImage < fromIndex && mainImage >= toIndex) {
        mainImage++;
      }
      
      images = newImages;
      dispatch('update', { images, mainImage });
    }
    
    // Format file size
    function formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
  </script>
  
  <div class="property-media-uploader" class:rtl={isRTL}>
    <div class="mb-4">
      <h3 class="text-lg font-medium text-neutral-900 dark:text-white">
        {$t('properties.media.images')} 
        {#if images.length > 0}
          <span class="text-sm font-normal text-neutral-500 dark:text-neutral-400">
            ({images.length}/{maxImages})
          </span>
        {/if}
      </h3>
      <p class="text-sm text-neutral-600 dark:text-neutral-400">
        {$t('properties.media.images_description')}
      </p>
    </div>
    
    <!-- Image Upload Area -->
    {#if images.length < maxImages}
      <div
        class="border-2 border-dashed rounded-lg transition-colors mb-6"
        class:border-neutral-300={!dragActive}
        class:dark:border-neutral-700={!dragActive}
        class:border-primary={dragActive}
        class:dark:border-primary={dragActive}
        class:bg-neutral-50={dragActive}
        class:dark:bg-neutral-800/50={dragActive}
        on:dragenter={handleDragEnter}
        on:dragleave={handleDragLeave}
        on:dragover={handleDragOver}
        on:drop={handleDrop}
      >
        <div class="p-8 text-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          
          <p class="mt-3 text-sm text-neutral-600 dark:text-neutral-400">
            {$t('properties.media.drag_drop')}
          </p>
          
          <div class="mt-4">
            <label for="property-image-upload" class="cursor-pointer rounded-md bg-white px-4 py-2 text-sm font-medium text-primary hover:bg-neutral-50 dark:bg-neutral-800 dark:hover:bg-neutral-700">
              {$t('properties.media.select_images')}
            </label>
            <input 
              id="property-image-upload" 
              name="property-image-upload" 
              type="file" 
              class="sr-only" 
              accept={allowedFileTypes.map(type => `.${type}`).join(',')}
              on:change={handleFileSelect}
              multiple
            />
          </div>
          
          <p class="mt-2 text-xs text-neutral-500 dark:text-neutral-500">
            {$t('properties.media.allowed_types')}: {allowedFileTypes.join(', ')}
          </p>
          <p class="text-xs text-neutral-500 dark:text-neutral-500">
            {$t('properties.media.max_size')}: {maxFileSize} MB
          </p>
        </div>
      </div>
    {/if}
    
    <!-- Image Gallery -->
    {#if imagePreviews.length > 0}
      <div class="image-gallery mt-4">
        <div class="mb-4 flex justify-between items-center">
          <h4 class="font-medium text-neutral-900 dark:text-white">
            {$t('properties.media.uploaded_images')}
          </h4>
          
          <p class="text-sm text-neutral-500 dark:text-neutral-400">
            {$t('properties.media.main_image_note')}
          </p>
        </div>
        
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {#each imagePreviews as preview, index}
            <Card class="relative overflow-hidden group">
              <div 
                class="aspect-w-3 aspect-h-2 w-full overflow-hidden bg-neutral-200 dark:bg-neutral-800"
                class:ring-2={preview.isMain}
                class:ring-primary={preview.isMain}
                class:ring-offset-2={preview.isMain}
              >
                <img 
                  src={preview.url} 
                  alt={$t('properties.media.property_image', { number: index + 1 })}
                  class="w-full h-full object-cover"
                />
                
                {#if preview.isMain}
                  <div class="absolute top-2 left-2 bg-primary text-white text-xs px-2 py-1 rounded-md">
                    {$t('properties.media.main')}
                  </div>
                {/if}
                
                <!-- Image Controls Overlay -->
                <div class="absolute inset-0 bg-black bg-opacity-40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                  {#if !preview.isMain}
                    <Button
                      variant="primary"
                      size="sm"
                      title={$t('properties.media.set_as_main')}
                      on:click={() => setMainImage(index)}
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="m9 12 2 2 4-4" />
                        <circle cx="12" cy="12" r="10" />
                      </svg>
                    </Button>
                  {/if}
                  
                  <Button
                    variant="error"
                    size="sm"
                    title={$t('properties.media.remove_image')}
                    on:click={() => removeImage(index)}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M3 6h18" />
                      <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
                      <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
                      <line x1="10" y1="11" x2="10" y2="17" />
                      <line x1="14" y1="11" x2="14" y2="17" />
                    </svg>
                  </Button>
                </div>
              </div>
              
              <div class="p-2 text-xs text-neutral-600 dark:text-neutral-400 truncate">
                {#if images[index] instanceof File}
                  {images[index].name} ({formatFileSize(images[index].size)})
                {:else}
                  {$t('properties.media.image')} {index + 1}
                {/if}
              </div>
            </Card>
          {/each}
        </div>
      </div>
    {/if}
  </div>
  
  <style>
    /* RTL support */
    .rtl {
      direction: rtl;
      text-align: right;
    }
    
    /* Image aspect ratio utility */
    .aspect-w-3 {
      position: relative;
      padding-bottom: calc(2 / 3 * 100%);
    }
    
    .aspect-h-2 > * {
      position: absolute;
      height: 100%;
      width: 100%;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
    }
  </style>