<!-- src/lib/components/RoomManager.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';
  import { t } from '$lib/i18n/i18n';
  import TagSelector from './TagSelector.svelte';
  
  export let rooms = [];
  export let availableFeatures = [];
  
  const dispatch = createEventDispatcher();
  
  // Default new room
  let newRoom = createEmptyRoom();
  
  const roomTypes = [
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
      id: Date.now(), // Temporary ID for client-side tracking
      name: '',
      room_type: 'bedroom',
      floor: 1,
      area_sqm: '',
      description: '',
      features: []
    };
  }
  
  function addRoom() {
    // Validate required fields
    if (!newRoom.name) {
      return;
    }
    
    // Format numeric fields
    if (newRoom.area_sqm) {
      newRoom.area_sqm = parseFloat(newRoom.area_sqm);
    }
    
    if (newRoom.floor) {
      newRoom.floor = parseInt(newRoom.floor);
    }
    
    // Add room to list
    rooms = [...rooms, { ...newRoom }];
    
    // Reset form for next room
    newRoom = createEmptyRoom();
    
    // Notify parent component
    dispatch('change', rooms);
  }
  
  function removeRoom(index) {
    rooms = rooms.filter((_, i) => i !== index);
    dispatch('change', rooms);
  }
  
  function handleRoomFeaturesChange(event) {
    newRoom.features = event.detail;
  }
</script>

<div class="space-y-8">
  <!-- Add Room Form -->
  <div class="bg-gray-50 dark:bg-gray-700 p-6 rounded-md">
    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">{$t('property.addRoom')}</h3>
    
    <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
      <!-- Room Name and Type -->
      <div class="sm:col-span-3">
        <label for="room_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('property.roomName')} *
        </label>
        <div class="mt-1">
          <input
            type="text"
            id="room_name"
            bind:value={newRoom.name}
            required
            class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
          />
        </div>
      </div>

      <div class="sm:col-span-3">
        <label for="room_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('property.roomType')}
        </label>
        <div class="mt-1">
          <select
            id="room_type"
            bind:value={newRoom.room_type}
            class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
          >
            {#each roomTypes as type}
              <option value={type.value}>{$t(type.label)}</option>
            {/each}
          </select>
        </div>
      </div>

      <!-- Floor and Area -->
      <div class="sm:col-span-3">
        <label for="room_floor" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('property.floor')}
        </label>
        <div class="mt-1">
          <input
            type="number"
            id="room_floor"
            bind:value={newRoom.floor}
            min="0"
            step="1"
            class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
          />
        </div>
      </div>

      <div class="sm:col-span-3">
        <label for="room_area" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('property.area')} ({$t('property.sqm')})
        </label>
        <div class="mt-1">
          <input
            type="number"
            id="room_area"
            bind:value={newRoom.area_sqm}
            min="0"
            step="0.01"
            class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
          />
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

      <!-- Room Features -->
      <div class="sm:col-span-6">
        <TagSelector
          tags={availableFeatures}
          selectedTags={newRoom.features}
          title={$t('property.roomFeatures')}
          on:change={handleRoomFeaturesChange}
        />
      </div>

      <!-- Add Button -->
      <div class="sm:col-span-6 flex justify-end">
        <button
          type="button"
          on:click={addRoom}
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" />
          </svg>
          {$t('property.addRoom')}
        </button>
      </div>
    </div>
  </div>

  <!-- Room List -->
  {#if rooms.length > 0}
    <div>
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">{$t('property.roomList')}</h3>
      
      <div class="bg-white dark:bg-gray-800 overflow-hidden shadow-md rounded-lg divide-y divide-gray-200 dark:divide-gray-700">
        {#each rooms as room, index}
          <div class="p-4 sm:p-6">
            <div class="flex items-start justify-between">
              <div>
                <h4 class="text-lg font-medium text-gray-900 dark:text-white flex items-center">
                  <span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200 mr-2">
                    {index + 1}
                  </span>
                  {room.name}
                  <span class="ml-2 text-sm font-normal text-gray-500 dark:text-gray-400">
                    ({$t(roomTypes.find(type => type.value === room.room_type)?.label || 'property.roomTypes.other')})
                  </span>
                </h4>
                
                <div class="mt-2 grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span class="font-medium text-gray-500 dark:text-gray-400">{$t('property.floor')}:</span>
                    <span class="ml-1 text-gray-900 dark:text-white">{room.floor}</span>
                  </div>
                  
                  {#if room.area_sqm}
                    <div>
                      <span class="font-medium text-gray-500 dark:text-gray-400">{$t('property.area')}:</span>
                      <span class="ml-1 text-gray-900 dark:text-white">{room.area_sqm} {$t('property.sqm')}</span>
                    </div>
                  {/if}
                </div>
                
                {#if room.description}
                  <p class="mt-2 text-sm text-gray-600 dark:text-gray-300">{room.description}</p>
                {/if}
                
                {#if room.features && room.features.length > 0}
                  <div class="mt-3">
                    <TagSelector tags={room.features} selectedTags={room.features} readonly={true} />
                  </div>
                {/if}
              </div>
              
              <button
                type="button"
                on:click={() => removeRoom(index)}
                class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 inline-flex items-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                <span class="ml-1 sr-only">{$t('property.remove')}</span>
              </button>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {:else}
    <div class="text-center py-10 bg-gray-50 dark:bg-gray-700 rounded-lg">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 dark:text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
      </svg>
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">{$t('property.noRooms')}</h3>
      <p class="text-gray-500 dark:text-gray-400">{$t('property.addRoomHelp')}</p>
    </div>
  {/if}
</div>