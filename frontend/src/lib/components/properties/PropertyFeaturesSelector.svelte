<!-- src/lib/components/properties/PropertyFeaturesSelector.svelte -->
<script>
    import { createEventDispatcher, onMount } from 'svelte';
    import { fade, slide, scale } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';
    import { t } from '$lib/i18n';
    
    // UI Components
    import Button from '$lib/components/ui/Button.svelte';
    import Input from '$lib/components/ui/Input.svelte';
    import Switch from '$lib/components/ui/Switch.svelte';
    
    const dispatch = createEventDispatcher();
    
    // Component props
    export let selectedFeatures = {}; // Object of selected features
    export let categories = []; // Custom feature categories
    export let maxCustomFeatures = 10; // Maximum number of custom features
    export let searchEnabled = true; // Enable search
    export let allowCustomFeatures = true; // Allow adding custom features
    export let variant = 'default'; // default, glass, outline, minimal
    export let expandedByDefault = false; // All categories expanded by default
    export let compact = false; // Compact display mode
    export let disabled = false; // Disable all inputs
    
    // Internal state
    let search = '';
    let customFeatureText = '';
    let expandedCategories = {};
    let customFeatures = [];
    let hoveredFeature = null;
    
    // Default feature categories if none provided
    const defaultCategories = [
      {
        id: 'indoor',
        name: 'Indoor Features',
        icon: 'home',
        features: [
          { id: 'air_conditioning', name: 'Air Conditioning' },
          { id: 'heating', name: 'Heating System' },
          { id: 'furnished', name: 'Furnished' },
          { id: 'fireplace', name: 'Fireplace' },
          { id: 'walk_in_closet', name: 'Walk-in Closet' },
          { id: 'smart_home', name: 'Smart Home Features' },
          { id: 'high_ceilings', name: 'High Ceilings' },
          { id: 'storage_room', name: 'Storage Room' }
        ]
      },
      {
        id: 'outdoor',
        name: 'Outdoor Features',
        icon: 'sun',
        features: [
          { id: 'backyard', name: 'Backyard' },
          { id: 'patio', name: 'Patio/Deck' },
          { id: 'garage', name: 'Garage' },
          { id: 'parking', name: 'Parking' },
          { id: 'outdoor_grill', name: 'Outdoor Grill' },
          { id: 'privacy_fence', name: 'Privacy Fence' }
        ]
      },
      {
        id: 'community',
        name: 'Community Features',
        icon: 'users',
        features: [
          { id: 'gym', name: 'Gym/Fitness Center' },
          { id: 'community_pool', name: 'Community Pool' },
          { id: 'security', name: 'Security Guard/Gate' },
          { id: 'playground', name: 'Playground' },
          { id: 'clubhouse', name: 'Clubhouse' },
          { id: 'tennis_court', name: 'Tennis Courts' }
        ]
      },
      {
        id: 'accessibility',
        name: 'Accessibility Features',
        icon: 'accessibility',
        features: [
          { id: 'wheelchair_accessible', name: 'Wheelchair Accessible' },
          { id: 'no_stairs', name: 'No Stairs to Entry' },
          { id: 'wide_doorway', name: 'Wide Doorways' },
          { id: 'accessible_bathroom', name: 'Accessible Bathroom' }
        ]
      }
    ];
    
    // Use provided categories or default ones
    $: effectiveCategories = categories.length > 0 ? categories : defaultCategories;
    
    // Container variant classes based on the style prop
    $: containerClasses = {
      'default': 'bg-white dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-700',
      'glass': 'bg-surface-glass dark:bg-neutral-800/30 backdrop-blur-sm border border-neutral-200/30 dark:border-neutral-700/30 shadow-glass-sm',
      'outline': 'bg-transparent border border-neutral-300 dark:border-neutral-700',
      'minimal': 'bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800'
    }[variant] || 'bg-white dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-700';
    
    // Helper to get feature icon
    function getIconSvg(icon) {
      switch (icon) {
        case 'home':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
          </svg>`;
        case 'sun':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd" />
          </svg>`;
        case 'users':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
          </svg>`;
        case 'accessibility':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>`;
        case 'plus':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
          </svg>`;
        default:
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clip-rule="evenodd" />
          </svg>`;
      }
    }
    
    // Initialize expanded categories
    function initializeExpandedCategories() {
      let expanded = {};
      effectiveCategories.forEach(category => {
        expanded[category.id] = expandedByDefault;
      });
      expandedCategories = expanded;
    }
    
    // Toggle category expansion
    function toggleCategory(categoryId) {
      expandedCategories = {
        ...expandedCategories,
        [categoryId]: !expandedCategories[categoryId]
      };
    }
    
    // Add a custom feature
    function addCustomFeature() {
      if (!customFeatureText.trim() || disabled) return;
      
      // Check if we've hit the max number of custom features
      if (customFeatures.length >= maxCustomFeatures) {
        return;
      }
      
      // Generate a unique ID for the custom feature
      const id = `custom_${Date.now()}`;
      
      // Add to custom features
      customFeatures = [
        ...customFeatures,
        { id, name: customFeatureText.trim() }
      ];
      
      // Set as selected
      selectedFeatures = {
        ...selectedFeatures,
        [id]: true
      };
      
      // Clear input
      customFeatureText = '';
      
      // Update parent component
      dispatchUpdate();
    }
    
    // Remove a custom feature
    function removeCustomFeature(id) {
      customFeatures = customFeatures.filter(feature => feature.id !== id);
      
      // Remove from selected features
      const { [id]: removed, ...rest } = selectedFeatures;
      selectedFeatures = rest;
      
      // Update parent component
      dispatchUpdate();
    }
    
    // Handle feature toggle
    function toggleFeature(feature) {
      if (disabled) return;
      
      selectedFeatures = {
        ...selectedFeatures,
        [feature.id]: !selectedFeatures[feature.id]
      };
      
      dispatchUpdate();
    }
    
    // Dispatch update event
    function dispatchUpdate() {
      dispatch('update', { 
        features: selectedFeatures,
        customFeatures: customFeatures
      });
    }
    
    // Filter features based on search
    $: filteredCategories = effectiveCategories.map(category => {
      if (!search) return category;
      
      const filteredFeatures = category.features.filter(feature => 
        feature.name.toLowerCase().includes(search.toLowerCase())
      );
      
      return {
        ...category,
        features: filteredFeatures
      };
    }).filter(category => category.features.length > 0);
    
    // Check if any category has matches (for empty state)
    $: hasMatches = filteredCategories.some(category => category.features.length > 0);
    
    // Track number of selected features
    $: selectedFeaturesCount = Object.values(selectedFeatures).filter(Boolean).length;
    
    // Initialize
    onMount(() => {
      initializeExpandedCategories();
    });
  </script>
  
  <div class="property-features-selector w-full">
    <!-- Search and controls -->
    {#if searchEnabled || allowCustomFeatures}
      <div class="mb-4 flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3">
        {#if searchEnabled}
          <div class="w-full sm:flex-1">
            <Input
              type="search"
              placeholder={t('features.search_features') || 'Search features...'}
              bind:value={search}
              disabled={disabled}
              rounded="lg"
              leadingIcon="search"
            />
          </div>
        {/if}
        
        {#if allowCustomFeatures}
          <div class="w-full sm:flex-1 flex space-x-2">
            <div class="flex-1">
              <Input
                type="text"
                placeholder={t('features.custom_feature') || 'Add custom feature...'}
                bind:value={customFeatureText}
                disabled={disabled || customFeatures.length >= maxCustomFeatures}
                rounded="lg"
                on:keydown={(e) => e.key === 'Enter' && addCustomFeature()}
              />
            </div>
            <Button
              variant="primary"
              size="md"
              disabled={!customFeatureText.trim() || disabled || customFeatures.length >= maxCustomFeatures}
              on:click={addCustomFeature}
              rounded="lg"
              aria-label={t('features.add_custom_feature') || 'Add custom feature'}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
              </svg>
            </Button>
          </div>
        {/if}
      </div>
    {/if}
    
    <!-- Info banner for search results -->
    {#if search && filteredCategories.length > 0}
      <div class="mb-4 py-2 px-4 bg-info/10 dark:bg-info/5 border border-info/20 rounded-lg">
        <p class="text-sm text-neutral-700 dark:text-neutral-300">
          {t('features.search_results', { count: filteredCategories.reduce((acc, category) => acc + category.features.length, 0) }) || 
            `Found ${filteredCategories.reduce((acc, category) => acc + category.features.length, 0)} matches for "${search}"`}
        </p>
      </div>
    {/if}
    
    <!-- Show custom features as pills -->
    {#if customFeatures.length > 0}
      <div class="mb-4">
        <h3 class="text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
          {t('features.custom_features') || 'Custom Features'}
        </h3>
        <div class="flex flex-wrap gap-2">
          {#each customFeatures as feature (feature.id)}
            <div 
              class="inline-flex items-center rounded-full px-3 py-1 text-sm
                {selectedFeatures[feature.id] ? 
                  'bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-300' : 
                  'bg-neutral-100 text-neutral-700 dark:bg-neutral-800 dark:text-neutral-300'}"
              in:scale={{ duration: 200, start: 0.8, opacity: 0 }}
              out:scale={{ duration: 200, start: 0.8, opacity: 0 }}
            >
              <span>{feature.name}</span>
              <button 
                class="ml-1 text-neutral-500 hover:text-error dark:text-neutral-400 dark:hover:text-error"
                on:click={() => removeCustomFeature(feature.id)}
                disabled={disabled}
                aria-label={t('features.remove_feature') || 'Remove feature'}
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          {/each}
        </div>
      </div>
    {/if}
    
    <!-- Features categories -->
    <div class={compact ? 'space-y-2' : 'space-y-4'}>
      {#each filteredCategories as category (category.id)}
        <div class={`${containerClasses} rounded-lg overflow-hidden`}>
          <!-- Category header with toggle -->
          <button
            class="w-full px-4 py-3 flex items-center justify-between bg-neutral-50 dark:bg-neutral-900/50 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors duration-200"
            on:click={() => toggleCategory(category.id)}
            aria-expanded={expandedCategories[category.id]}
            aria-controls={`category-${category.id}-content`}
          >
            <div class="flex items-center">
              {#if category.icon}
                <div class="mr-3 text-primary-600 dark:text-primary-400">
                  {@html getIconSvg(category.icon)}
                </div>
              {/if}
              <h3 class="font-medium text-neutral-800 dark:text-neutral-200">{category.name}</h3>
              
              <!-- Counter badge for selected features in this category -->
              {#if Object.entries(selectedFeatures).filter(([key, value]) => value && category.features.some(f => f.id === key)).length > 0}
                <span 
                  class="ml-2 px-2 py-0.5 text-xs rounded-full bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-300"
                  in:scale={{ duration: 200, start: 0.8 }}
                >
                  {Object.entries(selectedFeatures).filter(([key, value]) => value && category.features.some(f => f.id === key)).length}
                </span>
              {/if}
            </div>
            <span class="text-neutral-500 dark:text-neutral-400 transition-transform duration-200" style={expandedCategories[category.id] ? 'transform: rotate(180deg)' : ''}>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </span>
          </button>
          
          <!-- Category content -->
          {#if expandedCategories[category.id]}
            <div 
              id={`category-${category.id}-content`}
              class="px-4 py-3"
              transition:slide={{ duration: 200, easing: quintOut }}
            >
              <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-x-4 gap-y-2">
                {#each category.features as feature (feature.id)}
                  <div 
                    class="feature-item flex items-center py-1.5 px-2 rounded-md
                      {hoveredFeature === feature.id ? 'bg-neutral-100 dark:bg-neutral-800' : ''}
                      transition-colors duration-100"
                    on:mouseenter={() => hoveredFeature = feature.id}
                    on:mouseleave={() => hoveredFeature = null}
                  >
                    <Switch 
                      checked={!!selectedFeatures[feature.id]}
                      on:change={() => toggleFeature(feature)}
                      label={feature.name}
                      disabled={disabled}
                      size={compact ? 'sm' : 'md'}
                    />
                  </div>
                {/each}
              </div>
            </div>
          {/if}
        </div>
      {/each}
    </div>
    
    <!-- Empty state when no search results found -->
    {#if search && !hasMatches}
      <div class="py-8 px-4 text-center rounded-lg bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
        <div class="mb-4 text-neutral-400 dark:text-neutral-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <h3 class="text-lg font-medium text-neutral-700 dark:text-neutral-300">
          {t('features.no_results') || 'No matching features found'}
        </h3>
        <p class="mt-2 text-sm text-neutral-500 dark:text-neutral-400">
          {t('features.try_different_search') || 'Try a different search term or add a custom feature'}
        </p>
        
        {#if allowCustomFeatures}
          <div class="mt-4 flex justify-center">
            <Button
              variant="outline"
              color="primary"
              size="sm"
              on:click={() => { customFeatureText = search; addCustomFeature(); }}
              disabled={!search.trim() || disabled || customFeatures.length >= maxCustomFeatures}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
              </svg>
              {t('features.add_as_custom') || 'Add as custom feature'}
            </Button>
          </div>
        {/if}
      </div>
    {/if}
    
    <!-- Summary of selected features -->
    {#if selectedFeaturesCount > 0}
      <div class="mt-4 pt-3 border-t border-neutral-200 dark:border-neutral-800">
        <p class="text-sm text-neutral-700 dark:text-neutral-300">
          {t('features.selected_count', { count: selectedFeaturesCount }) || 
          `${selectedFeaturesCount} feature${selectedFeaturesCount !== 1 ? 's' : ''} selected`}
        </p>
      </div>
    {/if}
  </div>