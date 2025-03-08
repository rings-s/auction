<!-- src/lib/components/auction/PropertyDetails.svelte -->
<script>
    // Props
    export let data = {};
    
    // Format specifications in a readable way
    const specs = [
      { label: 'Property Type', value: data.property_type, icon: 'home' },
      { label: 'Size', value: data.size_sqm ? `${data.size_sqm} sqm` : null, icon: 'area' },
      { label: 'Location', value: data.location, icon: 'map-pin' },
      { label: 'Address', value: data.address, icon: 'address' },
      { label: 'Bedrooms', value: data.bedrooms, icon: 'bed' },
      { label: 'Bathrooms', value: data.bathrooms, icon: 'bath' },
      { label: 'Year Built', value: data.year_built, icon: 'calendar' },
      { label: 'Condition', value: data.property_condition, icon: 'condition' },
    ].filter(spec => spec.value !== null && spec.value !== undefined);
    
    // Additional Information
    const additionalInfo = [
      { label: 'Zoning Information', value: data.zoning_info, icon: 'zoning' },
      { label: 'Legal Description', value: data.legal_description, icon: 'legal' },
      { label: 'Historical Value', value: data.historical_value, icon: 'history' },
    ].filter(info => info.value !== null && info.value !== undefined);
    
    // Get icon SVG based on type
    function getIconSvg(type) {
      switch (type) {
        case 'home':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>`;
        case 'area':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"></rect><path d="M3 9h18"></path><path d="M9 21V9"></path></svg>`;
        case 'map-pin':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a8 8 0 0 0-8 8c0 5.4 8 12 8 12s8-6.6 8-12a8 8 0 0 0-8-8Z"></path><circle cx="12" cy="10" r="3"></circle></svg>`;
        case 'address':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9h18v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9Z"></path><path d="m3 9 2.45-4.9A2 2 0 0 1 7.24 3h9.52a2 2 0 0 1 1.8 1.1L21 9"></path><path d="M12 3v6"></path></svg>`;
        case 'bed':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 4v16"></path><path d="M2 8h18a2 2 0 0 1 2 2v10"></path><path d="M2 17h20"></path><path d="M6 8v9"></path></svg>`;
        case 'bath':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6 6.5 3.5a1.5 1.5 0 0 0-1-.5C4.683 3 4 3.683 4 4.5V17a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5"></path><line x1="10" y1="5" x2="8" y2="7"></line><line x1="2" y1="12" x2="22" y2="12"></line><line x1="7" y1="19" x2="7" y2="21"></line><line x1="17" y1="19" x2="17" y2="21"></line></svg>`;
        case 'calendar':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>`;
        case 'condition':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16.2 3.8a2.7 2.7 0 0 0-3.81 0l-.4.38-.4-.4a2.7 2.7 0 0 0-3.82 0C6.73 4.85 6.67 6.64 8 8l4 4 4-4c1.33-1.36 1.27-3.15.2-4.2z"></path><path d="M8 8a2.83 2.83 0 0 1-.64-3.2 3 3 0 0 1 .64-.8L8 4"></path><path d="m16 8-.8-.8a3 3 0 0 0 .8-.8 2.83 2.83 0 0 0 0-2.4"></path><path d="M12 12.5V20"></path><path d="M8 15h8"></path></svg>`;
        case 'zoning':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>`;
        case 'legal':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m17 8-4 8-4-8"></path><path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"></path></svg>`;
        case 'history':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>`;
        default:
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
      }
    }
  </script>
  
  <div>
    <h3 class="text-lg font-medium text-text-dark mb-4">Property Specifications</h3>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4 mb-6">
      {#each specs as spec}
        <div class="flex items-start">
          <div class="mr-3 mt-0.5 text-secondary-blue">
            {@html getIconSvg(spec.icon)}
          </div>
          <div>
            <div class="text-sm font-medium text-text-dark">{spec.label}</div>
            <div class="text-sm text-text-medium">{spec.value}</div>
          </div>
        </div>
      {/each}
    </div>
    
    {#if additionalInfo.some(info => info.value)}
      <h3 class="text-lg font-medium text-text-dark mb-4 mt-8">Additional Information</h3>
      
      <div class="space-y-4">
        {#each additionalInfo as info}
          {#if info.value}
            <div class="bg-primary-blue/5 rounded-lg p-4">
              <div class="flex items-center mb-2">
                <div class="mr-2 text-secondary-blue">
                  {@html getIconSvg(info.icon)}
                </div>
                <div class="text-sm font-medium text-text-dark">{info.label}</div>
              </div>
              <div class="text-sm text-text-medium pl-7">{info.value}</div>
            </div>
          {/if}
        {/each}
      </div>
    {/if}
  </div>