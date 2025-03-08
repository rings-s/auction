<!-- src/lib/components/auction/MachineryDetails.svelte -->
<script>
    // Props
    export let data = {};
    
    // Format specifications in a readable way
    const specs = [
      { label: 'Machine Type', value: data.machine_type, icon: 'machine' },
      { label: 'Manufacturer', value: data.manufacturer, icon: 'manufacturer' },
      { label: 'Model Number', value: data.model_number, icon: 'model' },
      { label: 'Year Manufactured', value: data.year_manufactured, icon: 'calendar' },
      { label: 'Operating Hours', value: data.operating_hours ? `${data.operating_hours} hours` : null, icon: 'hours' },
      { label: 'Power Requirements', value: data.power_requirements, icon: 'power' },
      { label: 'Dimensions', value: data.dimensions, icon: 'dimensions' },
      { label: 'Weight', value: data.weight, icon: 'weight' },
      { label: 'Capacity', value: data.capacity, icon: 'capacity' },
    ].filter(spec => spec.value !== null && spec.value !== undefined);
    
    // Additional Information
    const additionalInfo = [
      { label: 'Maintenance History', value: data.maintenance_history, icon: 'maintenance' },
      { label: 'Safety Certificates', value: data.safety_certificates, icon: 'safety' },
      { label: 'Technical Specifications', value: data.technical_specifications, icon: 'technical' },
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
        case 'machine':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="2" x2="9" y2="4"></line><line x1="15" y1="2" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="22"></line><line x1="15" y1="20" x2="15" y2="22"></line><line x1="20" y1="9" x2="22" y2="9"></line><line x1="20" y1="14" x2="22" y2="14"></line><line x1="2" y1="9" x2="4" y2="9"></line><line x1="2" y1="14" x2="4" y2="14"></line></svg>`;
        case 'manufacturer':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 20a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8l-7 5V8l-7 5V4a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"></path><circle cx="10" cy="10" r="2"></circle></svg>`;
        case 'model':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9h16"></path><path d="M4 15h16"></path><path d="M10 3 8 21"></path><path d="m16 3-2 18"></path></svg>`;
        case 'calendar':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>`;
        case 'hours':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>`;
        case 'power':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 7V4c0-1.1-.9-2-2-2H8c-1.1 0-2 .9-2 2v3"></path><path d="M18 14v3c0 1.1-.9 2-2 2H8c-1.1 0-2-.9-2-2v-3"></path><rect x="2" y="7" width="20" height="7" rx="2"></rect></svg>`;
        case 'dimensions':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 6H3"></path><path d="M21 12H3"></path><path d="M21 18H3"></path><path d="M18 3v18"></path><path d="M12 3v18"></path><path d="M6 3v18"></path></svg>`;
        case 'weight':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="3"></circle><path d="M6.5 8a2 2 0 0 0-1.905 1.46L2.1 18.5A2 2 0 0 0 4 21h16a2 2 0 0 0 1.925-2.54L19.4 9.5A2 2 0 0 0 17.48 8Z"></path></svg>`;
        case 'capacity':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7V5c0-1.1.9-2 2-2h2"></path><path d="M19 7V5c0-1.1-.9-2-2-2h-2"></path><path d="M21 19V6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v13"></path><path d="M3 17a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2"></path></svg>`;
        case 'maintenance':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>`;
        case 'safety':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>`;
        case 'technical':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><line x1="10" y1="9" x2="8" y2="9"></line></svg>`;
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
    <h3 class="text-lg font-medium text-text-dark mb-4">Machinery Specifications</h3>
    
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