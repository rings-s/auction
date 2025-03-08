<!-- src/routes/typography-demo.svelte -->
<script>
    import { onMount } from 'svelte';
    
    // Form state
    let formData = {
      name: '',
      email: '',
      inquiry: ''
    };
    
    // Handle form input changes
    function handleChange(field, event) {
      formData[field] = event.target.value;
    }
  </script>
  
  <div class="w-full max-w-6xl mx-auto p-8">
    <!-- Header - using layout typography -->
    <header class="mb-12 text-center">
      <h1 class="text-4xl font-medium mb-3 text-text-dark">Typography Contrast Demo</h1>
      <p class="text-text-medium text-lg max-w-2xl mx-auto">
        This demo showcases the visual contrast between <span class="font-semibold">layout typography</span> (like this text) and <span class="component-text font-semibold text-component-text-dark">component typography</span> used in interactive elements.
      </p>
    </header>
    
    <!-- Main content with cards showing the contrast -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
      <!-- Layout Typography Card -->
      <div class="card p-6">
        <h2 class="text-2xl font-medium mb-4 text-text-dark">Layout Typography</h2>
        <p class="mb-4">Layout typography uses <span class="font-semibold">Inter</span> font, which has a clean, neutral appearance ideal for content and reading.</p>
        
        <h3 class="text-xl font-medium mb-2 text-text-dark">Characteristics:</h3>
        <ul class="list-disc pl-5 mb-6 text-text-medium">
          <li class="mb-1">Neutral and balanced</li>
          <li class="mb-1">Slightly tighter letter-spacing</li>
          <li class="mb-1">Focus on readability for longer text</li>
          <li class="mb-1">Softer, more neutral color scheme</li>
        </ul>
        
        <div class="bg-gray-50 p-4 rounded-lg">
          <p class="mb-2 font-medium">Sample text:</p>
          <p class="text-text-dark">Primary Text - crisp and clear</p>
          <p class="text-text-medium">Secondary Text - supporting content</p>
          <p class="text-text-light">Tertiary Text - less important info</p>
        </div>
      </div>
      
      <!-- Component Typography Card -->
      <div class="card p-6">
        <h2 class="component-heading text-2xl mb-4">Component Typography</h2>
        <p class="component-body mb-4">Component typography uses <span class="font-semibold">Outfit</span> font, which has a more distinctive character that helps UI elements stand out.</p>
        
        <h3 class="component-heading text-xl mb-2">Characteristics:</h3>
        <ul class="list-disc pl-5 mb-6 component-body">
          <li class="mb-1">More distinctive letter forms</li>
          <li class="mb-1">Slightly wider letter-spacing</li>
          <li class="mb-1">Bolder weight for interactive elements</li>
          <li class="mb-1">Stronger, more vibrant color palette</li>
        </ul>
        
        <div class="bg-gray-50 p-4 rounded-lg">
          <p class="mb-2 font-semibold component-text">Sample text:</p>
          <p class="component-text text-component-text-dark">Primary Text - distinctive and clear</p>
          <p class="component-text text-component-text-light">Secondary Text - supporting elements</p>
          <p class="component-text text-component-primary">Action Text - for interactive elements</p>
        </div>
      </div>
    </div>
    
    <!-- Interactive Components Demo -->
    <div class="card p-8 mb-12">
      <h2 class="text-2xl font-medium mb-6 text-text-dark text-center">Interactive Components</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <!-- Form Section - shows component typography in action -->
        <div class="space-y-6">
          <div class="form-group">
            <label class="form-label block mb-2" for="name">Name</label>
            <input 
              type="text"
              id="name"
              bind:value={formData.name}
              on:input={(e) => handleChange('name', e)}
              class="form-input component-text w-full px-4 py-2 rounded-lg border border-neutral-200 focus:border-component-primary focus:ring-2 focus:ring-component-primary/20 outline-none"
              placeholder="Enter your name"
            />
          </div>
          
          <div class="form-group">
            <label class="form-label block mb-2" for="email">Email</label>
            <input 
              type="email"
              id="email"
              bind:value={formData.email}
              on:input={(e) => handleChange('email', e)}
              class="form-input component-text w-full px-4 py-2 rounded-lg border border-neutral-200 focus:border-component-primary focus:ring-2 focus:ring-component-primary/20 outline-none"
              placeholder="Enter your email"
            />
          </div>
          
          <div class="form-group">
            <label class="form-label block mb-2" for="inquiry">Message</label>
            <textarea 
              id="inquiry"
              bind:value={formData.inquiry}
              on:input={(e) => handleChange('inquiry', e)}
              class="form-input component-text w-full px-4 py-2 rounded-lg border border-neutral-200 focus:border-component-primary focus:ring-2 focus:ring-component-primary/20 outline-none"
              rows={4}
              placeholder="Enter your message"
            ></textarea>
          </div>
          
          <div class="flex space-x-4">
            <button class="btn btn-primary px-6 py-2 rounded-lg component-text bg-gradient-to-r from-component-primary to-component-secondary text-white font-semibold uppercase text-sm tracking-wider shadow-md hover:shadow-lg transition-all">
              Submit
            </button>
            
            <button class="btn btn-outline px-6 py-2 rounded-lg component-text border-2 border-component-primary text-component-primary font-semibold uppercase text-sm tracking-wider hover:bg-component-primary/5 transition-all">
              Cancel
            </button>
          </div>
        </div>
        
        <!-- Component Samples -->
        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-medium mb-3">Button Variants</h3>
            <div class="flex flex-wrap gap-3">
              <button class="btn btn-primary px-4 py-2 rounded-lg component-text bg-gradient-to-r from-component-primary to-component-secondary text-white font-semibold uppercase text-sm tracking-wider shadow-md hover:shadow-lg transition-all">
                Primary
              </button>
              <button class="btn btn-outline px-4 py-2 rounded-lg component-text border-2 border-component-primary text-component-primary font-semibold uppercase text-sm tracking-wider hover:bg-component-primary/5 transition-all">
                Outline
              </button>
              <button class="btn btn-white px-4 py-2 rounded-lg component-text bg-white text-component-primary shadow-md font-semibold uppercase text-sm tracking-wider hover:shadow-lg transition-all">
                White
              </button>
              <button class="btn btn-glass px-4 py-2 rounded-lg component-text bg-white/20 backdrop-blur-lg text-component-primary border border-white/30 font-semibold uppercase text-sm tracking-wider hover:bg-white/30 transition-all">
                Glass
              </button>
            </div>
          </div>
          
          <div>
            <h3 class="text-lg font-medium mb-3">Badges</h3>
            <div class="flex flex-wrap gap-3">
              <span class="badge badge-primary inline-flex items-center px-2.5 py-0.5 rounded-full text-xs component-text font-semibold bg-component-primary/10 text-component-primary">
                New
              </span>
              <span class="badge badge-success inline-flex items-center px-2.5 py-0.5 rounded-full text-xs component-text font-semibold bg-success/20 text-success">
                Approved
              </span>
              <span class="badge badge-warning inline-flex items-center px-2.5 py-0.5 rounded-full text-xs component-text font-semibold bg-warning/20 text-warning">
                Pending
              </span>
              <span class="badge badge-error inline-flex items-center px-2.5 py-0.5 rounded-full text-xs component-text font-semibold bg-error/20 text-error">
                Rejected
              </span>
            </div>
          </div>
          
          <div>
            <h3 class="text-lg font-medium mb-3">Alert</h3>
            <div class="bg-component-primary/10 border-l-4 border-component-primary p-4 rounded-r-lg">
              <div class="flex">
                <div class="flex-shrink-0 text-component-primary">
                  <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="ml-3">
                  <h3 class="component-text text-component-primary font-semibold text-sm">Information</h3>
                  <div class="component-text text-component-text-dark text-sm mt-1">
                    This alert demonstrates component typography that stands out against regular text.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Typography Comparison Table -->
    <div class="card p-8">
      <h2 class="text-2xl font-medium mb-6 text-text-dark text-center">Side by Side Comparison</h2>
      
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="text-left border-b border-gray-200">
              <th class="pb-3 font-medium text-text-dark">Element</th>
              <th class="pb-3 font-medium text-text-dark">Layout Typography</th>
              <th class="pb-3 font-medium text-text-dark">Component Typography</th>
            </tr>
          </thead>
          <tbody>
            <tr class="border-b border-gray-200">
              <td class="py-4 font-medium">Headers</td>
              <td class="py-4">
                <h4 class="text-lg font-medium text-text-dark">This is a heading</h4>
              </td>
              <td class="py-4">
                <h4 class="component-heading text-lg">This is a heading</h4>
              </td>
            </tr>
            <tr class="border-b border-gray-200">
              <td class="py-4 font-medium">Body text</td>
              <td class="py-4">
                <p class="text-text-medium">This is regular body text that uses the layout typography style.</p>
              </td>
              <td class="py-4">
                <p class="component-body">This is body text that uses the component typography style.</p>
              </td>
            </tr>
            <tr class="border-b border-gray-200">
              <td class="py-4 font-medium">Button text</td>
              <td class="py-4">
                <span class="px-4 py-2 bg-neutral-100 rounded-lg text-text-dark">Button Text</span>
              </td>
              <td class="py-4">
                <span class="px-4 py-2 bg-component-primary text-white rounded-lg component-text font-semibold uppercase text-sm tracking-wider">Button Text</span>
              </td>
            </tr>
            <tr class="border-b border-gray-200">
              <td class="py-4 font-medium">Labels</td>
              <td class="py-4">
                <label class="text-text-dark font-medium">Form Label</label>
              </td>
              <td class="py-4">
                <label class="form-label component-text font-medium text-component-text-dark">Form Label</label>
              </td>
            </tr>
            <tr>
              <td class="py-4 font-medium">Links</td>
              <td class="py-4">
                <a href="#" class="text-text-dark underline">Regular link</a>
              </td>
              <td class="py-4">
                <a href="#" class="component-text text-component-primary font-medium">Component link</a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
  
  <style>
    /* Any additional component-specific styles can go here */
    :global(html) {
      scroll-behavior: smooth;
    }
    
    /* Ensure Outfit font is applied to component text */
    :global(.component-text),
    :global(.component-heading),
    :global(.component-body) {
      font-family: 'Outfit', sans-serif;
    }
  </style>