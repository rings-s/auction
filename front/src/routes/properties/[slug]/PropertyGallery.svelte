<script>
    import { t } from '$lib/i18n';
    import Gallery from '$lib/components/ui/Gallery.svelte';
    import Tabs from '$lib/components/ui/Tabs.svelte';
  
    export let property;
  
    let activeGalleryTab = 'photos';
  
    // Organize media by type
    $: mediaByType = organizeMediaByType(property.media || []);
    $: galleryTabs = createGalleryTabs(mediaByType);
  
    function organizeMediaByType(media) {
      const organized = {
        photos: [],
        videos: [],
        documents: [],
        other: []
      };
  
      media.forEach(item => {
        const type = item.media_type || 'other';
        switch (type) {
          case 'image':
            organized.photos.push({
              url: item.url || item.file,
              alt: item.name || property.title,
              caption: item.name,
              ...item
            });
            break;
          case 'video':
            organized.videos.push(item);
            break;
          case 'document':
            organized.documents.push(item);
            break;
          default:
            organized.other.push(item);
        }
      });
  
      return organized;
    }
  
    function createGalleryTabs(mediaByType) {
      const tabs = [];
      
      if (mediaByType.photos.length > 0) {
        tabs.push({
          id: 'photos',
          label: `${$t('property.galleryTabs.photos')} (${mediaByType.photos.length})`,
          count: mediaByType.photos.length
        });
      }
      
      if (mediaByType.videos.length > 0) {
        tabs.push({
          id: 'videos',
          label: `${$t('property.galleryTabs.videos')} (${mediaByType.videos.length})`,
          count: mediaByType.videos.length
        });
      }
      
      if (mediaByType.documents.length > 0) {
        tabs.push({
          id: 'documents',
          label: `${$t('property.galleryTabs.documents')} (${mediaByType.documents.length})`,
          count: mediaByType.documents.length
        });
      }
      
      if (mediaByType.other.length > 0) {
        tabs.push({
          id: 'other',
          label: `${$t('property.galleryTabs.otherFiles')} (${mediaByType.other.length})`,
          count: mediaByType.other.length
        });
      }
  
      return tabs;
    }
  
    function downloadFile(item) {
      const link = document.createElement('a');
      link.href = item.url || item.file;
      link.download = item.name || 'download';
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  </script>
  
  <div class="space-y-6">
    {#if galleryTabs.length > 0}
      <!-- Gallery Tabs -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <!-- Tab Navigation -->
        <div class="border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <Tabs
            tabs={galleryTabs}
            bind:activeTab={activeGalleryTab}
            variant="pills"
            size="small"
          />
        </div>
  
        <!-- Tab Content -->
        <div class="p-6">
          {#if activeGalleryTab === 'photos' && mediaByType.photos.length > 0}
            <Gallery
              images={mediaByType.photos}
              showThumbnails={true}
              autoPlay={false}
            />
            
          {:else if activeGalleryTab === 'videos' && mediaByType.videos.length > 0}
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {#each mediaByType.videos as video}
                <div class="bg-gray-50 dark:bg-gray-700 rounded-xl overflow-hidden">
                  <div class="aspect-w-16 aspect-h-9 bg-gray-200 dark:bg-gray-600">
                    <!-- Video player would go here -->
                    <div class="flex items-center justify-center">
                      <svg class="h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1.586a1 1 0 01.707.293l2.414 2.414a1 1 0 00.707.293H15M9 10a1 1 0 01-1-1V5a1 1 0 011-1h12a1 1 0 011 1v4a1 1 0 01-1 1M9 10L6.5 7.5" />
                      </svg>
                    </div>
                  </div>
                  <div class="p-4">
                    <h3 class="font-medium text-gray-900 dark:text-white">
                      {video.name || $t('property.media.untitled')}
                    </h3>
                  </div>
                </div>
              {/each}
            </div>
            
          {:else if activeGalleryTab === 'documents' && mediaByType.documents.length > 0}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              {#each mediaByType.documents as doc}
                <div class="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-xl border border-gray-200 dark:border-gray-600">
                  <div class="w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="font-medium text-gray-900 dark:text-white truncate">
                      {doc.name || $t('property.pdfDocument')}
                    </h3>
                    <p class="text-sm text-gray-500 dark:text-gray-400">
                      {$t('property.document')}
                    </p>
                  </div>
                  <button
                    type="button"
                    class="px-3 py-2 text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 border border-primary-200 dark:border-primary-800 rounded-lg hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors"
                    on:click={() => downloadFile(doc)}
                  >
                    {$t('property.downloadPdf')}
                  </button>
                </div>
              {/each}
            </div>
            
          {:else if activeGalleryTab === 'other' && mediaByType.other.length > 0}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              {#each mediaByType.other as file}
                <div class="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-xl border border-gray-200 dark:border-gray-600">
                  <div class="w-12 h-12 bg-gray-100 dark:bg-gray-600 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="font-medium text-gray-900 dark:text-white truncate">
                      {file.name || $t('property.file')}
                    </h3>
                    <p class="text-sm text-gray-500 dark:text-gray-400">
                      {$t('property.file')}
                    </p>
                  </div>
                  <button
                    type="button"
                    class="px-3 py-2 text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 border border-primary-200 dark:border-primary-800 rounded-lg hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors"
                    on:click={() => downloadFile(file)}
                  >
                    {$t('property.downloadFile')}
                  </button>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      </div>
    {:else}
      <!-- No Media Available -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-12">
        <div class="text-center">
          <svg class="h-16 w-16 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {$t('property.noImages')}
          </h3>
          <p class="text-gray-500 dark:text-gray-400">
            {$t('property.noImagesInfo')}
          </p>
        </div>
      </div>
    {/if}
  </div>