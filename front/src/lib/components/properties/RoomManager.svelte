<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { t, locale } from '$lib/i18n';
  import { fly, fade, slide, scale } from 'svelte/transition';
  import { quintOut, elasticOut } from 'svelte/easing';
  import TagSelector from '$lib/components/ui/TagSelector.svelte';
  import { clickOutside } from '$lib/actions/clickOutside';
  
  export let rooms = [];
  export let availableFeatures = [];
  export const propertyType = ''; // External reference only - can affect room type suggestions
  
  const dispatch = createEventDispatcher();
  
  let newRoom = createEmptyRoom();
  let isAddingRoom = false;
  let selectedRoomIndex = null;
  let errorMessage = '';
  let successMessage = '';
  let animationDuration = 300;
  
  let touched = {
    name: false,
    room_type: false
  };
  
  $: roomTypes = [
    { value: 'bedroom', label: 'property.roomTypes.bedroom' },
    { value: 'bathroom', label: 'property.roomTypes.bathroom' },
    { value: 'kitchen', label: 'property.roomTypes.kitchen' },
    { value: 'living', label: 'property.roomTypes.living' },
    { value: 'dining', label: 'property.roomTypes.dining' },
    { value: 'office', label: 'property.roomTypes.office' },
    { value: 'storage', label: 'property.roomTypes.storage' },
    { value: 'other', label: 'property.roomTypes.other' }
  ];
  
  function createEmptyRoom() {
    return {
      id: `temp-${Date.now()}`,
      name: '',
      room_type: 'bedroom',
      floor: 1,
      area_sqm: '',
      description: '',
      features: [],
      has_window: false,
      has_bathroom: false
    };
  }
  
  function validateRoom(room) {
    let errors = {};
    
    if (!room.name.trim()) {
      errors.name = $t('validation.roomNameRequired');
    }
    
    if (!room.room_type) {
      errors.room_type = $t('validation.roomTypeRequired');
    }
    
    if (room.area_sqm && isNaN(parseFloat(room.area_sqm))) {
      errors.area_sqm = $t('validation.invalidAreaFormat');
    }
    
    return {
      valid: Object.keys(errors).length === 0,
      errors
    };
  }
  
  function addRoom() {
    touched = {
      name: true,
      room_type: true
    };
    
    const { valid, errors } = validateRoom(newRoom);
    if (!valid) {
      errorMessage = Object.values(errors)[0];
      setTimeout(() => {
        errorMessage = '';
      }, 5000);
      return;
    }
    
    if (newRoom.area_sqm) {
      newRoom.area_sqm = parseFloat(newRoom.area_sqm);
    }
    
    if (newRoom.floor) {
      newRoom.floor = parseInt(newRoom.floor);
    }
    
    rooms = [...rooms, { ...newRoom }];
    
    successMessage = $t('property.roomAdded');
    setTimeout(() => {
      successMessage = '';
    }, 3000);
    
    newRoom = createEmptyRoom();
    touched = { name: false, room_type: false };
    isAddingRoom = false;
    
    dispatch('change', rooms);
  }
  
  function removeRoom(index) {
    selectedRoomIndex = index;
    setTimeout(() => {
      rooms = rooms.filter((_, i) => i !== index);
      dispatch('change', rooms);
      selectedRoomIndex = null;
    }, 300);
  }
  
  function handleRoomFeaturesChange(event) {
    newRoom.features = event.detail;
  }
  
  function cancelAddRoom() {
    newRoom = createEmptyRoom();
    touched = { name: false, room_type: false };
    isAddingRoom = false;
  }
  
  function showAddRoomForm() {
    isAddingRoom = true;
    setTimeout(() => {
      document.getElementById('room_name')?.focus();
    }, 100);
  }

  function handleKeydown(event) {
    if (event.key === 'Escape') {
      cancelAddRoom();
    }
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<div class="room-manager">
  <div class="flex flex-col md:flex-row md:items-center justify-between mb-6">
    <div>
      <h3 class="text-xl font-bold text-gray-900 dark:text-white">
        {$t('property.roomList')}
      </h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        {$t('property.roomsDesc')}
      </p>
    </div>
    
    {#if !isAddingRoom}
      <button
        type="button"
        on:click={showAddRoomForm}
        class="mt-4 md:mt-0 inline-flex items-center px-4 py-2.5 border border-transparent rounded-md shadow-sm text-sm font-medium bg-gradient-to-r from-primary-500 to-primary-600 text-white hover:from-primary-600 hover:to-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all duration-300 transform hover:scale-105"
        in:fade={{ duration: animationDuration }}
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" />
        </svg>
        {$t('property.addRoom')}
      </button>
    {/if}
  </div>

  <!-- Error/Success Messages -->
  {#if errorMessage}
    <div 
      class="mb-4 p-4 border-l-4 border-red-400 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 rounded-md shadow-sm"
      in:slide={{ duration: animationDuration, easing: quintOut }}
      out:slide={{ duration: animationDuration }}
    >
      <div class="flex">
        <svg class="h-5 w-5 text-red-400 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        <p>{errorMessage}</p>
      </div>
    </div>
  {/if}
  
  {#if successMessage}
    <div 
      class="mb-4 p-4 border-l-4 border-green-400 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 rounded-md shadow-sm"
      in:slide={{ duration: animationDuration, easing: quintOut }}
      out:slide={{ duration: animationDuration }}
    >
      <div class="flex">
        <svg class="h-5 w-5 text-green-400 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <p>{successMessage}</p>
      </div>
    </div>
  {/if}

  <!-- Add Room Form -->
  {#if isAddingRoom}
    <div 
      class="mb-8 bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-750 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-700"
      in:fly={{ y: -20, duration: animationDuration, easing: quintOut }}
      out:fly={{ y: -20, duration: animationDuration }}
      use:clickOutside on:clickoutside={cancelAddRoom}
    >
      <div class="flex justify-between items-center mb-4">
        <h4 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-primary-500" viewBox="0 0 20 20" fill="currentColor">
            <path d="M11 17a1 1 0 001.447.894l4-2A1 1 0 0017 15V9.236a1 1 0 00-1.447-.894l-4 2a1 1 0 00-.553.894V17zM15.211 6.276a1 1 0 000-1.788l-4.764-2.382a1 1 0 00-.894 0L4.789 4.488a1 1 0 000 1.788l4.764 2.382a1 1 0 00.894 0l4.764-2.382zM4.447 8.342A1 1 0 003 9.236V15a1 1 0 00.553.894l4 2A1 1 0 009 17v-5.764a1 1 0 00-.553-.894l-4-2z" />
          </svg>
          {$t('property.addRoom')}
        </h4>
        <button 
          type="button" 
          on:click={cancelAddRoom}
          class="text-gray-400 hover:text-gray-500 dark:text-gray-500 dark:hover:text-gray-400 transition-colors duration-200"
          aria-label={$t('common.cancel')}
        >
          <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>

      <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
        <!-- Room Name and Type -->
        <div class="sm:col-span-3">
          <label for="room_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('property.roomName')} *
          </label>
          <div class="mt-1 relative">
            <input
              type="text"
              id="room_name"
              bind:value={newRoom.name}
              on:blur={() => touched.name = true}
              required
              class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
              class:border-red-500={touched.name && !newRoom.name.trim()}
            />
            {#if touched.name && !newRoom.name.trim()}
              <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
              </div>
              <p class="mt-1 text-sm text-red-600 dark:text-red-500">{$t('validation.roomNameRequired')}</p>
            {/if}
          </div>
        </div>

        <div class="sm:col-span-3">
          <label for="room_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('property.roomType')} *
          </label>
          <div class="mt-1">
            <select
              id="room_type"
              bind:value={newRoom.room_type}
              on:change={() => touched.room_type = true}
              class="mt-1 block w-full py-2 px-3 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:text-white"
            >
              {#each roomTypes as type}
                <option value={type.value}>{$t(type.label)}</option>
              {/each}
            </select>
            {#if touched.room_type && !newRoom.room_type}
              <p class="mt-1 text-sm text-red-600 dark:text-red-500">{$t('validation.roomTypeRequired')}</p>
            {/if}
          </div>
        </div>

        <!-- Floor and Area -->
        <div class="sm:col-span-3">
          <label for="room_floor" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('property.floor')}
          </label>
          <div class="mt-1">
            <div class="flex rounded-md shadow-sm">
              <input
                type="number"
                id="room_floor"
                bind:value={newRoom.floor}
                min="0"
                step="1"
                class="flex-1 shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
              />
              <span class="hidden sm:inline-flex items-center px-3 rounded-r-md border border-l-0 border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-400 sm:text-sm">
                {$t('property.level')}
              </span>
            </div>
          </div>
        </div>

        <div class="sm:col-span-3">
          <label for="room_area" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('property.area')}
          </label>
          <div class="mt-1">
            <div class="flex rounded-md shadow-sm">
              <input
                type="number"
                id="room_area"
                bind:value={newRoom.area_sqm}
                min="0"
                step="0.01"
                class="flex-1 shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
              />
              <span class="inline-flex items-center px-3 rounded-r-md border border-l-0 border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-400 sm:text-sm">
                {$t('property.sqm')}
              </span>
            </div>
          </div>
        </div>

        <!-- Description -->
        <div class="sm:col-span-6">
          <label for="room_description" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {$t('property.description')}
          </label>
          <div class="mt-1">
            <textarea
              id="room_description"
              bind:value={newRoom.description}
              rows="3"
              class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
            ></textarea>
          </div>
        </div>

        <!-- Additional Toggles -->
        <div class="sm:col-span-6">
          <div class="flex flex-col sm:flex-row sm:space-x-6 space-y-3 sm:space-y-0">
            <div class="flex items-center">
              <input
                id="has_window"
                type="checkbox"
                bind:checked={newRoom.has_window}
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 dark:border-gray-700 rounded dark:bg-gray-800"
              />
              <label for="has_window" class="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                {$t('property.hasWindow')}
              </label>
            </div>

            <div class="flex items-center">
              <input
                id="has_bathroom"
                type="checkbox"
                bind:checked={newRoom.has_bathroom}
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 dark:border-gray-700 rounded dark:bg-gray-800"
              />
              <label for="has_bathroom" class="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                {$t('property.hasBathroom')}
              </label>
            </div>
          </div>
        </div>

        <!-- Room Features -->
        <div class="sm:col-span-6">
          <TagSelector
            tags={availableFeatures}
            selectedTags={newRoom.features}
            title={$t('property.roomFeatures')}
            on:change={handleRoomFeaturesChange}
            variant="pill"
            size="small"
          />
        </div>

        <!-- Form Actions -->
        <div class="sm:col-span-6 flex flex-col-reverse sm:flex-row sm:justify-end gap-3">
          <button
            type="button"
            on:click={cancelAddRoom}
            class="inline-flex justify-center items-center py-2 px-4 border border-gray-300 dark:border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-300"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
            {$t('common.cancel')}
          </button>
          
          <button
            type="button"
            on:click={addRoom}
            class="inline-flex justify-center items-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all duration-300 transform hover:translate-y-[-1px]"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
            </svg>
            {$t('property.addRoom')}
          </button>
        </div>
      </div>
    </div>
  {/if}

  <!-- Room List -->
  {#if rooms.length > 0}
    <div class="space-y-4">
      {#each rooms as room, index}
        <div 
          class="bg-white dark:bg-gray-800 border dark:border-gray-700 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-all duration-300 transform hover:translate-y-[-2px]"
          class:border-red-500={selectedRoomIndex === index}
          class:scale-95={selectedRoomIndex === index}
          in:fly={{ y: 20, duration: animationDuration, delay: index * 50 }}
          out:scale={{ duration: animationDuration, start: 1, opacity: 0 }}
        >
          <div class="p-5">
            <div class="flex flex-col sm:flex-row sm:items-start justify-between">
              <div class="flex-grow">
                <div class="flex items-center">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200">
                    {$t(roomTypes.find(type => type.value === room.room_type)?.label || 'property.roomTypes.other')}
                  </span>
                  
                  <span class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
                    {$t('property.floor')} {room.floor}
                  </span>
                  
                  {#if room.has_window}
                    <span class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm3 1h6v4H7V5zm6 6H7v2h6v-2z" clip-rule="evenodd" />
                      </svg>
                      {$t('property.hasWindow')}
                    </span>
                  {/if}
                  
                  {#if room.has_bathroom}
                    <span class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M5 2a2 2 0 00-2 2v14l3.5-2 3.5 2 3.5-2 3.5 2V4a2 2 0 00-2-2H5zm4.707 3.707a1 1 0 00-1.414-1.414l-3 3a1 1 0 00-.03 1.383l2.26 2.626a1 1 0 001.538-.125l4-5a1 1 0 00-1.538-1.255L8.59 7.6z" clip-rule="evenodd" />
                    </span>
                  {/if}
                </div>
                
                <h4 class="mt-2 text-lg font-semibold text-gray-900 dark:text-white">
                  {room.name}
                </h4>
                
                {#if room.area_sqm}
                  <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    {$t('property.area')}: {room.area_sqm} {$t('property.sqm')}
                  </p>
                {/if}
                
                {#if room.description}
                  <p class="mt-2 text-sm text-gray-600 dark:text-gray-300">
                    {room.description}
                  </p>
                {/if}
                
                {#if room.features && room.features.length > 0}
                  <div class="mt-3">
                    <h5 class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">
                      {$t('property.features')}
                    </h5>
                    <div class="flex flex-wrap gap-1.5">
                      {#each room.features as feature}
                        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-secondary-100 text-secondary-800 dark:bg-secondary-900 dark:text-secondary-200">
                          {feature}
                        </span>
                      {/each}
                    </div>
                  </div>
                {/if}
              </div>
              
              <div class="mt-4 sm:mt-0 flex-shrink-0">
                <button
                  type="button"
                  on:click={() => removeRoom(index)}
                  class="inline-flex items-center p-2 border border-transparent rounded-full shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-all duration-300 hover:scale-110"
                  aria-label="{$t('property.remove')} {room.name}"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {:else}
    <div class="text-center py-10 bg-gray-50 dark:bg-gray-700 rounded-lg transform transition-all duration-300 hover:scale-[1.01]">
      <div class="inline-flex items-center justify-center w-16 h-16 mb-4 rounded-full bg-primary-100 dark:bg-primary-900 text-primary-500 dark:text-primary-300">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">{$t('property.noRooms')}</h3>
      <p class="text-gray-500 dark:text-gray-400">{$t('property.addRoomHelp')}</p>
      
      <button
        type="button"
        on:click={showAddRoomForm}
        class="mt-6 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all duration-300 transform hover:translate-y-[-2px]"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
        </svg>
        {$t('property.startAddingRooms')}
      </button>
    </div>
  {/if}
</div>

<style>
  .room-manager {
    --primary-gradient: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-600));
    --secondary-gradient: linear-gradient(135deg, var(--color-secondary-500), var(--color-secondary-600));
  }
  
  :global(.dark) .room-manager {
    --primary-gradient: linear-gradient(135deg, var(--color-primary-600), var(--color-primary-700));
    --secondary-gradient: linear-gradient(135deg, var(--color-secondary-600), var(--color-secondary-700));
  }
  
  :global(.room-manager input:focus),
  :global(.room-manager select:focus),
  :global(.room-manager textarea:focus) {
    box-shadow: 0 0 0 2px rgba(167, 139, 250, 0.2);
    border-color: var(--color-primary-500);
  }
  
  :global(.room-manager .room-card:hover) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
</style>