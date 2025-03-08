<!-- src/lib/components/auction/FactoryDetails.svelte -->
<script>
    // Props
    export let data = {};
    
    // Format specifications in a readable way
    const specs = [
      { label: 'Total Area', value: data.total_area_sqm ? `${data.total_area_sqm.toLocaleString()} sqm` : null, icon: 'area' },
      { label: 'Built-Up Area', value: data.built_up_area_sqm ? `${data.built_up_area_sqm.toLocaleString()} sqm` : null, icon: 'building' },
      { label: 'Location', value: data.location, icon: 'map-pin' },
      { label: 'Address', value: data.address, icon: 'address' },
      { label: 'Production Capacity', value: data.production_capacity, icon: 'production' },
      { label: 'Power Capacity', value: data.power_capacity, icon: 'power' },
      { label: 'Water Supply', value: data.water_supply, icon: 'water' },
    ].filter(spec => spec.value !== null && spec.value !== undefined);
    
    // Additional Information
    const additionalInfo = [
      { label: 'Waste Management', value: data.waste_management, icon: 'waste' },
      { label: 'Environmental Certificates', value: data.environmental_certificates, icon: 'certificate' },
      { label: 'Infrastructure Details', value: data.infrastructure_details, icon: 'infrastructure' },
      { label: 'Utility Connections', value: data.utility_connections, icon: 'utility' },
    ].filter(info => info.value !== null && info.value !== undefined);
    
    // Try to parse JSON data if it's a string
    additionalInfo.forEach(info => {
      if (typeof info.value === 'string') {
        try {
          const parsed = JSON.parse(info.value);
          info.value = parsed;
        } catch (e) {
          // Not JSON, keep as is
        }
      }
    });
    
    // Get icon SVG based on type
    function getIconSvg(type) {
      switch (type) {
        case 'area':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"></rect><path d="M3 9h18"></path><path d="M9 21V9"></path></svg>`;
        case 'building':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><path d="M9 22v-4h6v4"></path><path d="M8 6h.01"></path><path d="M16 6h.01"></path><path d="M12 6h.01"></path><path d="M12 10h.01"></path><path d="M12 14h.01"></path><path d="M16 10h.01"></path><path d="M16 14h.01"></path><path d="M8 10h.01"></path><path d="M8 14h.01"></path></svg>`;
        case 'map-pin':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a8 8 0 0 0-8 8c0 5.4 8 12 8 12s8-6.6 8-12a8 8 0 0 0-8-8Z"></path><circle cx="12" cy="10" r="3"></circle></svg>`;
        case 'address':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9h18v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9Z"></path><path d="m3 9 2.45-4.9A2 2 0 0 1 7.24 3h9.52a2 2 0 0 1 1.8 1.1L21 9"></path><path d="M12 3v6"></path></svg>`;
        case 'production':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12.5h20"></path><path d="M18 20V6.5a1 1 0 0 0-1-1h-3.5a1 1 0 0 0-1 1V20"></path><path d="M10.5 20V6.5a1 1 0 0 0-1-1H6a1 1 0 0 0-1 1V20"></path></svg>`;
        case 'power':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 7V4c0-1.1-.9-2-2-2H8c-1.1 0-2 .9-2 2v3"></path><path d="M18 14v3c0 1.1-.9 2-2 2H8c-1.1 0-2-.9-2-2v-3"></path><rect x="2" y="7" width="20" height="7" rx="2"></rect></svg>`;
        case 'water':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22a7 7 0 0 0 7-7c0-3.5-3.5-8-7-11-3.5 3-7 7.5-7 11a7 7 0 0 0 7 7Z"></path></svg>`;
        case 'waste':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"></path><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>`;
        case 'certificate':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>`;
        case 'infrastructure':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9z"></path><path d="M21 9V6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v3"></path></svg>`;
        case 'utility':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9"></path><path d="M13 2v7h7"></path><circle cx="11.5" cy="14.5" r="2.5"></circle><path d="M13.5 12c1.5-1 4-1 4 2.5"></path></svg>`;
        default:
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
      }
    }
    
    // Function to render complex values
    function renderValue(value) {
      if (typeof value === 'object' && value !== null) {
        if (Array.isArray(value)) {
          return `<ul class="list-disc pl-5 space-y-1">
            ${value.map(item => `<li>${typeof item === 'object' ? JSON.stringify(item) : item}</li>`).join('')}
          </ul>`;
        } else {
          return `<dl class="grid grid-cols-2 gap-x-4 gap-y-1">
            ${Object.entries(value).map(([k, v]) => `
              <dt class="font-medium">${k}:</dt>
              <dd>${typeof v === 'object' ? JSON.stringify(v) : v}</dd>
            `).join('')}
          </dl>`;
        }
      }
      return value;
    }
  </script>
  
  <div>
    <h3 class="text-lg font-medium text-text-dark mb-4">Factory Specifications</h3>
    
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
              <div class="text-sm text-text-medium pl-7">
                {#if typeof info.value === 'string'}
                  {info.value}
                {:else}
                  {@html renderValue(info.value)}
                {/if}
              </div>
            </div>
          {/if}
        {/each}
      </div>
    {/if}
  </div>