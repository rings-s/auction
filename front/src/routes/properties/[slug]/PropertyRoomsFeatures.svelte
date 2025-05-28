<script>
    import { t } from '$lib/i18n';
    import { translateFeatures, translateAmenities, translateRoomType } from '$lib/i18n';
    import { slide, fade, scale } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';
  
    export let property;
  
    $: rooms = property.rooms || [];
    $: features = property.features || [];
    $: amenities = property.amenities || [];
  
    // Enhanced state management
    let expandedRooms = new Set();
    let searchQuery = '';
    let selectedFloor = 'all';
    let selectedRoomType = 'all';
    let showAllFeatures = false;
    let showAllAmenities = false;
  
    // Computed values
    $: uniqueFloors = [...new Set(rooms.map(room => room.floor).filter(Boolean))].sort((a, b) => a - b);
    $: uniqueRoomTypes = [...new Set(rooms.map(room => room.room_type).filter(Boolean))];
    
    $: filteredRooms = rooms.filter(room => {
      const matchesSearch = !searchQuery || 
        room.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        room.description?.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesFloor = selectedFloor === 'all' || room.floor == selectedFloor;
      const matchesType = selectedRoomType === 'all' || room.room_type === selectedRoomType;
      return matchesSearch && matchesFloor && matchesType;
    });
  
    $: displayedFeatures = showAllFeatures ? features : features.slice(0, 6);
    $: displayedAmenities = showAllAmenities ? amenities : amenities.slice(0, 6);
  
    // Room type icons mapping
    const roomTypeIcons = {
      bedroom: '🛏️',
      livingRoom: '🛋️',
      kitchen: '🍳',
      bathroom: '🚿',
      diningRoom: '🍽️',
      office: '💼',
      guestRoom: '🏨',
      masterBedroom: '👑',
      childrenRoom: '🧸',
      utilityRoom: '🧹',
      storageRoom: '📦',
      garage: '🚗',
      balcony: '🌿',
      terrace: '🌅',
      basement: '⬇️',
      attic: '⬆️',
      hallway: '🚪',
      entrance: '🚪',
      laundryRoom: '👕',
      other: '🏠'
    };
  
    // Feature icons mapping
    const featureIcons = {
      airConditioning: '❄️',
      heating: '🔥',
      parking: '🅿️',
      garage: '🚗',
      pool: '🏊',
      garden: '🌳',
      security: '🔒',
      elevator: '🛗',
      fireplace: '🔥',
      balcony: '🌿',
      terrace: '🌅',
      storage: '📦',
      furnished: '🛋️',
      petsAllowed: '🐕',
      wheelchairAccess: '♿',
      fiberInternet: '📶',
      solarPanels: '☀️',
      gym: '💪',
      laundryRoom: '👕'
    };
  
    // Functions
    function toggleRoom(roomId) {
      if (expandedRooms.has(roomId)) {
        expandedRooms.delete(roomId);
      } else {
        expandedRooms.add(roomId);
      }
      expandedRooms = expandedRooms; // Trigger reactivity
    }
  
    function getRoomIcon(roomType) {
      const mappedType = Object.keys(roomTypeIcons).find(key => 
        roomType?.toLowerCase().includes(key.toLowerCase())
      );
      return roomTypeIcons[mappedType] || roomTypeIcons.other;
    }
  
    function getFeatureIcon(feature) {
      const mappedFeature = Object.keys(featureIcons).find(key => 
        feature?.toLowerCase().includes(key.toLowerCase())
      );
      return featureIcons[mappedFeature] || '✓';
    }
  
    function clearFilters() {
      searchQuery = '';
      selectedFloor = 'all';
      selectedRoomType = 'all';
    }
  </script>
  
  <div class="space-y-6">
    <!-- Enhanced Header with Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
        <div>
          <h1 class="text-xl font-bold text-gray-900 dark:text-white">
            {$t('property.rooms')} & {$t('property.features')}
          </h1>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {rooms.length} {$t('property.rooms').toLowerCase()}, {features.length} {$t('property.features').toLowerCase()}, {amenities.length} {$t('property.amenities').toLowerCase()}
          </p>
        </div>
        
        <!-- Quick Stats -->
        <div class="flex items-center gap-4 text-sm">
          <div class="text-center">
            <div class="text-lg font-bold text-blue-600 dark:text-blue-400">{rooms.length}</div>
            <div class="text-xs text-gray-500">{$t('property.rooms')}</div>
          </div>
          <div class="text-center">
            <div class="text-lg font-bold text-green-600 dark:text-green-400">{features.length}</div>
            <div class="text-xs text-gray-500">{$t('property.features')}</div>
          </div>
          <div class="text-center">
            <div class="text-lg font-bold text-purple-600 dark:text-purple-400">{amenities.length}</div>
            <div class="text-xs text-gray-500">{$t('property.amenities')}</div>
          </div>
        </div>
      </div>
  
      <!-- Advanced Filters -->
      {#if rooms.length > 3}
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <!-- Search -->
          <div class="relative">
            <input
              type="text"
              bind:value={searchQuery}
              placeholder={$t('search.keyword')}
              class="w-full pl-8 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg 
                bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:outline-none
                placeholder-gray-400 dark:placeholder-gray-500"
            />
            <svg class="absolute left-2.5 top-2.5 w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
  
          <!-- Floor Filter -->
          {#if uniqueFloors.length > 1}
            <select
              bind:value={selectedFloor}
              class="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg 
                bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:outline-none"
            >
              <option value="all">{$t('search.all')} {$t('property.floors')}</option>
              {#each uniqueFloors as floor}
                <option value={floor}>{$t('property.floor')} {floor}</option>
              {/each}
            </select>
          {/if}
  
          <!-- Room Type Filter -->
          {#if uniqueRoomTypes.length > 1}
            <select
              bind:value={selectedRoomType}
              class="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg 
                bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:outline-none"
            >
              <option value="all">{$t('search.all')} Types</option>
              {#each uniqueRoomTypes as roomType}
                <option value={roomType}>{translateRoomType(roomType)}</option>
              {/each}
            </select>
          {/if}
  
          <!-- Clear Filters -->
          {#if searchQuery || selectedFloor !== 'all' || selectedRoomType !== 'all'}
            <button
              type="button"
              on:click={clearFilters}
              class="px-3 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 
                border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 
                transition-colors flex items-center justify-center gap-1"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              {$t('search.clear')}
            </button>
          {/if}
        </div>
      {/if}
    </div>
  
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <!-- Enhanced Rooms Section -->
      <div class="xl:col-span-2 space-y-4">
        {#if filteredRooms.length > 0}
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            {#each filteredRooms as room, index (room.id || index)}
              <div 
                class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 
                  hover:shadow-md hover:border-blue-300 dark:hover:border-blue-700 
                  transition-all duration-200 overflow-hidden group"
                in:scale={{ duration: 300, delay: index * 50, easing: quintOut }}
              >
                <!-- Room Header -->
                <div class="p-4 bg-gradient-to-r from-gray-50 to-blue-50 dark:from-gray-700 dark:to-blue-900/20">
                  <div class="flex items-start justify-between">
                    <div class="flex items-start gap-3">
                      <div class="w-10 h-10 bg-white dark:bg-gray-600 rounded-lg flex items-center justify-center text-lg shadow-sm">
                        {getRoomIcon(room.room_type)}
                      </div>
                      <div>
                        <h3 class="font-semibold text-gray-900 dark:text-white text-sm">
                          {room.name}
                        </h3>
                        <p class="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
                          {translateRoomType(room.room_type)}
                        </p>
                        <div class="flex items-center gap-2 mt-1">
                          <span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300">
                            {$t('property.floor')} {room.floor}
                          </span>
                          {#if room.area_sqm}
                            <span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300">
                              {room.area_sqm} {$t('property.sqm')}
                            </span>
                          {/if}
                        </div>
                      </div>
                    </div>
                    
                    <!-- Expand Button -->
                    <button
                      type="button"
                      on:click={() => toggleRoom(room.id || index)}
                      class="p-1.5 rounded-lg hover:bg-white/50 dark:hover:bg-gray-600/50 transition-colors
                        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
                      aria-label={expandedRooms.has(room.id || index) ? $t('common.collapse') : $t('common.expand')}
                    >
                      <svg 
                        class="w-4 h-4 text-gray-500 transition-transform duration-200 {expandedRooms.has(room.id || index) ? 'rotate-180' : ''}" 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                  </div>
                </div>
  
                <!-- Room Details -->
                <div class="p-4">
                  {#if room.description}
                    <p class="text-xs text-gray-600 dark:text-gray-300 mb-3 leading-relaxed">
                      {room.description}
                    </p>
                  {/if}
  
                  <!-- Room Features -->
                  {#if room.features && room.features.length > 0}
                    <div class="mb-3">
                      <h4 class="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                        {$t('property.roomFeatures')}
                      </h4>
                      <div class="flex flex-wrap gap-1">
                        {#each room.features.slice(0, expandedRooms.has(room.id || index) ? room.features.length : 3) as feature}
                          <span class="inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium 
                            bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 
                            border border-blue-200 dark:border-blue-800">
                            <span class="text-xs">{getFeatureIcon(feature)}</span>
                            {feature}
                          </span>
                        {/each}
                        {#if room.features.length > 3 && !expandedRooms.has(room.id || index)}
                          <span class="text-xs text-gray-500 dark:text-gray-400">
                            +{room.features.length - 3} more
                          </span>
                        {/if}
                      </div>
                    </div>
                  {/if}
  
                  <!-- Expanded Content -->
                  {#if expandedRooms.has(room.id || index)}
                    <div transition:slide={{ duration: 300, easing: quintOut }}>
                      <div class="pt-3 border-t border-gray-200 dark:border-gray-700">
                        <div class="grid grid-cols-2 gap-3 text-xs">
                          {#if room.length || room.width}
                            <div>
                              <span class="text-gray-500 dark:text-gray-400">Dimensions:</span>
                              <span class="font-medium text-gray-900 dark:text-white ml-1">
                                {room.length || '?'} × {room.width || '?'} m
                              </span>
                            </div>
                          {/if}
                          {#if room.windows}
                            <div>
                              <span class="text-gray-500 dark:text-gray-400">Windows:</span>
                              <span class="font-medium text-gray-900 dark:text-white ml-1">{room.windows}</span>
                            </div>
                          {/if}
                        </div>
                      </div>
                    </div>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        {:else if rooms.length > 0}
          <!-- No Results State -->
          <div class="text-center py-12 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
            <svg class="h-12 w-12 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No results found
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Try adjusting your filters
            </p>
            <button
              type="button"
              on:click={clearFilters}
              class="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              Clear filters
            </button>
          </div>
        {:else}
          <!-- Empty State -->
          <div class="text-center py-12 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
            <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center">
              <svg class="h-8 w-8 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
              {$t('property.noRooms')}
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              No rooms have been added to this property yet
            </p>
          </div>
        {/if}
      </div>
  
      <!-- Enhanced Features & Amenities Sidebar -->
      <div class="space-y-6">
        <!-- Property Features -->
        {#if features.length > 0}
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div class="p-4 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-b border-green-200 dark:border-green-800">
              <div class="flex items-center justify-between">
                <h2 class="font-bold text-green-900 dark:text-green-100 flex items-center gap-2">
                  <div class="w-6 h-6 bg-green-100 dark:bg-green-900/50 rounded-lg flex items-center justify-center">
                    <svg class="w-3 h-3 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  {$t('property.features')}
                </h2>
                <span class="text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 px-2 py-1 rounded-full">
                  {features.length}
                </span>
              </div>
            </div>
            
            <div class="p-4 space-y-2">
              {#each translateFeatures(displayedFeatures) as feature, index}
                <div 
                  class="flex items-center gap-3 p-2.5 bg-green-50 dark:bg-green-900/10 rounded-lg border border-green-100 dark:border-green-900/30 
                    hover:bg-green-100 dark:hover:bg-green-900/20 transition-colors"
                  in:scale={{ duration: 200, delay: index * 25 }}
                >
                  <div class="w-6 h-6 bg-green-100 dark:bg-green-900/50 rounded-md flex items-center justify-center">
                    <span class="text-sm">{getFeatureIcon(feature)}</span>
                  </div>
                  <span class="text-sm font-medium text-green-800 dark:text-green-200 flex-1">
                    {feature}
                  </span>
                </div>
              {/each}
              
              {#if features.length > 6}
                <button
                  type="button"
                  on:click={() => showAllFeatures = !showAllFeatures}
                  class="w-full p-2 text-sm text-green-700 dark:text-green-300 hover:text-green-800 dark:hover:text-green-200 
                    border border-green-200 dark:border-green-800 rounded-lg hover:bg-green-50 dark:hover:bg-green-900/20 
                    transition-colors flex items-center justify-center gap-1
                    focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-1"
                >
                  {showAllFeatures ? 'Show Less' : `Show More (${features.length - 6})`}
                  <svg class="w-3 h-3 transition-transform {showAllFeatures ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              {/if}
            </div>
          </div>
        {/if}
  
        <!-- Amenities -->
        {#if amenities.length > 0}
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div class="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-b border-blue-200 dark:border-blue-800">
              <div class="flex items-center justify-between">
                <h2 class="font-bold text-blue-900 dark:text-blue-100 flex items-center gap-2">
                  <div class="w-6 h-6 bg-blue-100 dark:bg-blue-900/50 rounded-lg flex items-center justify-center">
                    <svg class="w-3 h-3 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
                    </svg>
                  </div>
                  {$t('property.amenities')}
                </h2>
                <span class="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-1 rounded-full">
                  {amenities.length}
                </span>
              </div>
            </div>
            
            <div class="p-4 space-y-2">
              {#each translateAmenities(displayedAmenities) as amenity, index}
                <div 
                  class="flex items-center gap-3 p-2.5 bg-blue-50 dark:bg-blue-900/10 rounded-lg border border-blue-100 dark:border-blue-900/30 
                    hover:bg-blue-100 dark:hover:bg-blue-900/20 transition-colors"
                  in:scale={{ duration: 200, delay: index * 25 }}
                >
                  <div class="w-6 h-6 bg-blue-100 dark:bg-blue-900/50 rounded-md flex items-center justify-center">
                    <span class="text-sm">{getFeatureIcon(amenity)}</span>
                  </div>
                  <span class="text-sm font-medium text-blue-800 dark:text-blue-200 flex-1">
                    {amenity}
                  </span>
                </div>
              {/each}
              
              {#if amenities.length > 6}
                <button
                  type="button"
                  on:click={() => showAllAmenities = !showAllAmenities}
                  class="w-full p-2 text-sm text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 
                    border border-blue-200 dark:border-blue-800 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 
                    transition-colors flex items-center justify-center gap-1
                    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
                >
                  {showAllAmenities ? 'Show Less' : `Show More (${amenities.length - 6})`}
                  <svg class="w-3 h-3 transition-transform {showAllAmenities ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              {/if}
            </div>
          </div>
        {/if}
  
        <!-- Summary Card -->
        <div class="bg-gradient-to-br from-gray-50 to-slate-100 dark:from-gray-800 dark:to-slate-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
          <h3 class="font-semibold text-gray-900 dark:text-white mb-3 text-sm">
            Summary
          </h3>
          <div class="space-y-2 text-xs">
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-400">Total Rooms:</span>
              <span class="font-medium text-gray-900 dark:text-white">{rooms.length}</span>
            </div>
            {#if rooms.reduce((sum, room) => sum + (parseFloat(room.area_sqm) || 0), 0) > 0}
              <div class="flex justify-between">
                <span class="text-gray-600 dark:text-gray-400">Total Area:</span>
                <span class="font-medium text-gray-900 dark:text-white">
                  {rooms.reduce((sum, room) => sum + (parseFloat(room.area_sqm) || 0), 0).toFixed(1)} {$t('property.sqm')}
                </span>
              </div>
            {/if}
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-400">Features:</span>
              <span class="font-medium text-gray-900 dark:text-white">{features.length}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-400">Amenities:</span>
              <span class="font-medium text-gray-900 dark:text-white">{amenities.length}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <style>
    /* Enhanced animations */
    @keyframes slideInUp {
      from {
        opacity: 0;
        transform: translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
  
    /* Smooth hover transitions */
    .group:hover .group-hover\:scale-105 {
      transform: scale(1.05);
    }
  
    /* Custom scrollbar for mobile filters */
    .filter-container::-webkit-scrollbar {
      height: 4px;
    }
    
    .filter-container::-webkit-scrollbar-track {
      background: #f1f5f9;
    }
    
    .filter-container::-webkit-scrollbar-thumb {
      background: #cbd5e1;
      border-radius: 2px;
    }
  
    /* Animation delays for staggered entries */
    .stagger-animation:nth-child(1) { animation-delay: 0ms; }
    .stagger-animation:nth-child(2) { animation-delay: 50ms; }
    .stagger-animation:nth-child(3) { animation-delay: 100ms; }
    .stagger-animation:nth-child(4) { animation-delay: 150ms; }
  </style>