<!-- src/lib/components/auction/VehicleDetails.svelte -->
<script>
    // Props
    export let data = {};
    
    // Format specifications in a readable way
    const specs = [
      { label: 'Make', value: data.make, icon: 'car' },
      { label: 'Model', value: data.model, icon: 'model' },
      { label: 'Year', value: data.year, icon: 'calendar' },
      { label: 'Mileage', value: data.mileage ? `${data.mileage.toLocaleString()} miles` : null, icon: 'mileage' },
      { label: 'Condition', value: data.condition, icon: 'condition' },
      { label: 'VIN', value: data.vin, icon: 'vin' },
      { label: 'Engine Type', value: data.engine_type, icon: 'engine' },
      { label: 'Transmission', value: data.transmission, icon: 'transmission' },
      { label: 'Fuel Type', value: data.fuel_type, icon: 'fuel' },
      { label: 'Color', value: data.color, icon: 'color' },
      { label: 'Registration Number', value: data.registration_number, icon: 'registration' },
    ].filter(spec => spec.value !== null && spec.value !== undefined);
    
    // Additional Information
    const additionalInfo = [
      { label: 'Service History', value: data.service_history, icon: 'service' },
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
        case 'car':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 16H9m10 0h3v-3.15a1 1 0 0 0-.84-.99L16 11l-2.7-3.6a1 1 0 0 0-.8-.4H5.24a2 2 0 0 0-1.8 1.1l-.8 1.63A6 6 0 0 0 2 12.42V16h2"></path><circle cx="6.5" cy="16.5" r="2.5"></circle><circle cx="16.5" cy="16.5" r="2.5"></circle></svg>`;
        case 'model':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9h16"></path><path d="M4 15h16"></path><path d="M10 3 8 21"></path><path d="m16 3-2 18"></path></svg>`;
        case 'calendar':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>`;
        case 'mileage':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v6l4 2"></path></svg>`;
        case 'condition':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 9v2"></path><path d="M12 13v.01"></path><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Z"></path></svg>`;
        case 'vin':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6H10a6 6 0 0 0-6 6v0a6 6 0 0 0 6 6h10"></path><path d="M14 16v-6"></path><path d="M18 16v-6"></path></svg>`;
        case 'engine':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 11V7a5 5 0 0 1 5-5h0a5 5 0 0 1 5 5v4"></path><path d="M2 15h20"></path><path d="M9 15v6"></path><path d="M15 15v6"></path><path d="M12 15v6"></path><path d="M3 11h18a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1v-2a1 1 0 0 1 1-1Z"></path></svg>`;
        case 'transmission':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="4"></circle><circle cx="18" cy="18" r="4"></circle><path d="M6 10v8"></path><path d="M18 14V6"></path><path d="m14 6-8 8"></path></svg>`;
        case 'fuel':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 22h12"></path><path d="M12 11c-.3-1-.8-1.5-2-1.5s-2.7.8-2.7 2.3c0 3.1 4.7 6.2 4.7 6.2"></path><path d="M12 11c.3-1 .8-1.5 2-1.5s2.7.8 2.7 2.3c0 3.1-4.7 6.2-4.7 6.2"></path><path d="M9 6.8a4 4 0 0 1 8 0c0 2.2-4 3.2-4 3.2"></path><path d="M13 6.8a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z"></path></svg>`;
        case 'color':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20a8 8 0 1 0 0-16 8 8 0 0 0 0 16Z"></path><path d="M12 14a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z"></path><path d="M12 2v2"></path><path d="M12 22v-2"></path><path d="m17 20.66-1-1.73"></path><path d="M11 10.27 7 3.34"></path><path d="m20.66 17-1.73-1"></path><path d="m3.34 7 1.73 1"></path><path d="M14 12h8"></path><path d="M2 12h2"></path><path d="m20.66 7-1.73 1"></path><path d="m3.34 17 1.73-1"></path><path d="m17 3.34-1 1.73"></path><path d="m11 13.73-4 6.93"></path></svg>`;
        case 'registration':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="5" width="16" height="14" rx="2"></rect><line x1="16" y1="2" x2="16" y2="8"></line><line x1="8" y1="2" x2="8" y2="8"></line><path d="M7 13h10"></path><path d="M7 17h8"></path></svg>`;
        case 'service':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>`;
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
    <h3 class="text-lg font-medium text-text-dark mb-4">Vehicle Specifications</h3>
    
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