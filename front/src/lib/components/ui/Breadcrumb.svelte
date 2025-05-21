<!-- src/lib/components/Breadcrumb.svelte -->
<script>
    export let items = [];
    export let class_ = '';
    
    // Get the "class" prop as "class_" because "class" is a reserved word in JavaScript
    export { class_ as class };
  </script>
  
  <nav class="flex {class_}" aria-label="Breadcrumb">
    <ol class="flex items-center space-x-2">
      {#each items as item, index (item.href)}
        <li>
          {#if index > 0}
            <div class="flex items-center">
              <svg class="h-5 w-5 flex-shrink-0 text-gray-400 dark:text-gray-600" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path d="M5.555 17.776l8-16 .894.448-8 16-.894-.448z" />
              </svg>
            </div>
          {/if}
          
          <div class="flex items-center">
            {#if item.active}
              <span class="ml-2 text-sm font-medium text-gray-500 dark:text-gray-400" aria-current="page">
                {item.label}
              </span>
            {:else}
              <a 
                href={item.href} 
                class="ml-2 text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300"
              >
                {item.label}
              </a>
            {/if}
          </div>
        </li>
      {/each}
    </ol>
  </nav>