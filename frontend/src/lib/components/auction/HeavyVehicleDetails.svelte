<!-- src/lib/components/auction/HeavyVehicleDetails.svelte -->
<script>
    // Props
    export let data = {};
    
    // Format specifications in a readable way
    const specs = [
      { label: 'Vehicle Type', value: data.vehicle_type, icon: 'vehicle-type' },
      { label: 'Make', value: data.make, icon: 'car' },
      { label: 'Model', value: data.model, icon: 'model' },
      { label: 'Year', value: data.year, icon: 'calendar' },
      { label: 'Load Capacity', value: data.load_capacity, icon: 'load' },
      { label: 'Operating Hours', value: data.operating_hours ? `${data.operating_hours} hours` : null, icon: 'hours' },
      { label: 'Engine Power', value: data.engine_power, icon: 'engine' },
      { label: 'Registration Number', value: data.registration_number, icon: 'registration' },
    ].filter(spec => spec.value !== null && spec.value !== undefined);
    
    // Additional Information
    const additionalInfo = [
      { label: 'Compliance Certificates', value: data.compliance_certificates, icon: 'certificate' },
      { label: 'Maintenance History', value: data.maintenance_history, icon: 'maintenance' },
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
        case 'vehicle-type':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5.3 15h13.4"></path><path d="M3 10h18l-3 8H6l-3-8Z"></path><path d="M6 4h5"></path><path d="M9 4v6"></path></svg>`;
        case 'car':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 16H9m10 0h3v-3.15a1 1 0 0 0-.84-.99L16 11l-2.7-3.6a1 1 0 0 0-.8-.4H5.24a2 2 0 0 0-1.8 1.1l-.8 1.63A6 6 0 0 0 2 12.42V16h2"></path><circle cx="6.5" cy="16.5" r="2.5"></circle><circle cx="16.5" cy="16.5" r="2.5"></circle></svg>`;
        case 'model':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9h16"></path><path d="M4 15h16"></path><path d="M10 3 8 21"></path><path d="m16 3-2 18"></path></svg>`;
        case 'calendar':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>`;
        case 'load':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v14a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7z"></path><circle cx="12" cy="7" r="3"></circle><path d="M8 14h8"></path><path d="M8 18h8"></path></svg>`;
        case 'hours':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>`;
        case 'engine':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"></rect><line x1="6" y1="12" x2="10" y2="12"></line><line x1="8" y1="10" x2="8" y2="14"></line><line x1="14" y1="12" x2="18" y2="12"></line></svg>`;
        case 'registration':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="5" width="16" height="14" rx="2"></rect><line x1="16" y1="2" x2="16" y2="8"></line><line x1="8" y1="2" x2="8" y2="8"></line><path d="M7 13h10"></path><path d="M7 17h8"></path></svg>`;
        case 'certificate':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>`;
        case 'maintenance':
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
    <h3 class="text-lg font-medium text-text-dark mb-4">Heavy Vehicle Specifications</h3>
    
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