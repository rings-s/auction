<!-- src/lib/components/ui/Table.svelte -->
<script>
  /**
   * Table Component
   * A feature-rich, accessible table component with sorting, loading state, and customization.
   */
  import { onMount, createEventDispatcher } from 'svelte';
  import { language } from '$lib/i18n';
  import Spinner from './Spinner.svelte';
  
  const dispatch = createEventDispatcher();
  
  // Props
  export let headers = []; // Array of column headers { key, label, sortable, width, align }
  export let rows = []; // Array of row objects { id, cells: [{ key, value, render }], isHighlighted, highlightClass, clickable }
  export let compact = false; // Compact mode with less padding
  export let bordered = false; // Add borders to cells
  export let striped = false; // Add striped rows
  export let hoverable = true; // Highlight rows on hover
  export let sortable = false; // Enable sorting (requires sortable: true in headers)
  export let sortKey = null; // Currently sorted column key
  export let sortDirection = 'asc'; // Current sort direction (asc or desc)
  export let responsive = true; // Make table responsive
  export let emptyMessage = "No data to display"; // Message when no rows
  export let loading = false; // Loading state
  export let loadingRows = 3; // Number of loading placeholder rows
  export let caption = undefined; // Table caption
  export let stickyHeader = false; // Make header sticky
  export let maxHeight = undefined; // Max height for the table container
  export let zebra = false; // Alias for striped
  
  // Refs
  let tableElement;
  
  // Derived values
  $: isRTL = $language === 'ar';
  $: useStriped = striped || zebra;
  
  // Table style classes based on props
  $: tableClasses = [
    'w-full text-cosmos-text',
    bordered ? 'border border-cosmos-bg-light' : '',
  ].filter(Boolean).join(' ');
  
  // Header style classes
  $: headerClasses = [
    'bg-cosmos-bg-light bg-opacity-80 text-cosmos-text font-medium text-sm',
    compact ? 'px-3 py-2' : 'px-4 py-3',
    bordered ? 'border-b border-cosmos-bg-light' : '',
    stickyHeader ? 'sticky top-0 z-10' : '',
  ].filter(Boolean).join(' ');
  
  // TD style classes
  $: tdClasses = [
    compact ? 'px-3 py-2' : 'px-4 py-3',
    bordered ? 'border-b border-cosmos-bg-light' : '',
  ].filter(Boolean).join(' ');
  
  // Default cell renderer for when none is provided
  const defaultCellRenderer = (cell) => {
    return {
      component: 'span',
      props: {},
      content: cell.value !== undefined && cell.value !== null ? cell.value.toString() : ''
    };
  };
  
  // Component registry for rendering custom components
  const componentRegistry = {
    'div': (props, content, children) => `<div ${renderProps(props)}>${content || ''}${renderChildren(children)}</div>`,
    'span': (props, content) => `<span ${renderProps(props)}>${content || ''}</span>`,
    'p': (props, content) => `<p ${renderProps(props)}>${content || ''}</p>`,
    'strong': (props, content) => `<strong ${renderProps(props)}>${content || ''}</strong>`,
    'em': (props, content) => `<em ${renderProps(props)}>${content || ''}</em>`,
    'a': (props, content) => `<a ${renderProps(props)}>${content || ''}</a>`,
    'button': (props, content) => `<button ${renderProps(props)}>${content || ''}</button>`,
    'img': (props) => `<img ${renderProps(props)} alt="${props.alt || ''}" />`,
    'svg': (props, content) => `<svg ${renderProps(props)}>${content || ''}</svg>`,
    'badge': (props, content) => {
      const variantClass = {
        success: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
        error: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
        warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
        info: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
        default: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
      }[props.variant || 'default'];
      
      return `<span class="px-2 py-1 text-xs font-medium rounded-full ${variantClass} ${props.class || ''}">${content || ''}</span>`;
    }
  };
  
  // Helper to render props as HTML attributes
  function renderProps(props = {}) {
    return Object.entries(props)
      .map(([key, value]) => {
        if (key === 'class' && value) return `class="${value}"`;
        if (value === true) return key;
        if (value === false || value === null || value === undefined) return '';
        return `${key}="${value}"`;
      })
      .filter(Boolean)
      .join(' ');
  }
  
  // Helper to render child components
  function renderChildren(children) {
    if (!children) return '';
    if (!Array.isArray(children)) children = [children];
    
    return children
      .filter(Boolean)
      .map(child => {
        const renderer = componentRegistry[child.component];
        if (renderer) {
          return renderer(child.props, child.content, child.children);
        }
        return '';
      })
      .join('');
  }
  
  // Handle sort click
  function handleSortClick(header) {
    if (!header.sortable || !sortable) return;
    
    const newSortDirection = sortKey === header.key && sortDirection === 'asc' ? 'desc' : 'asc';
    
    dispatch('sort', {
      key: header.key,
      direction: newSortDirection
    });
  }
  
  // Handle row click
  function handleRowClick(row, event) {
    if (!row.clickable) return;
    
    // Only dispatch if the click wasn't on an interactive element
    const isInteractive = event.target.closest('a, button, input, select, textarea');
    if (!isInteractive) {
      dispatch('rowClick', { row });
    }
  }
  
  // Get cell HTML using the render function or default renderer
  function getCellHTML(cell) {
    const renderer = cell.render || defaultCellRenderer;
    const renderData = renderer(cell);
    
    if (!renderData) return '';
    
    if (typeof renderData === 'string') {
      return renderData;
    }
    
    const componentRenderer = componentRegistry[renderData.component];
    if (componentRenderer) {
      return componentRenderer(renderData.props, renderData.content, renderData.children);
    }
    
    return cell.value !== undefined && cell.value !== null ? cell.value.toString() : '';
  }
  
  onMount(() => {
    // Any initialization here
  });
</script>

<div 
  class={responsive ? 'w-full overflow-x-auto' : ''} 
  style={maxHeight ? `max-height: ${maxHeight}; overflow-y: auto;` : ''}
  {...$$restProps}
>
  <table class={tableClasses} bind:this={tableElement}>
    {#if caption}
      <caption class="sr-only">{caption}</caption>
    {/if}
    
    {#if headers.length > 0}
      <thead>
        <tr>
          {#each headers as header (header.key)}
            <th 
              class={`${headerClasses} ${header.sortable && sortable ? 'cursor-pointer select-none' : ''} ${header.align ? `text-${header.align}` : ''}`}
              style={header.width ? `width: ${header.width}` : ''}
              scope="col"
              on:click={() => handleSortClick(header)}
              on:keydown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  handleSortClick(header);
                }
              }}
              tabindex={header.sortable && sortable ? 0 : undefined}
              role={header.sortable && sortable ? 'button' : undefined}
              aria-sort={sortable && sortKey === header.key ? sortDirection : undefined}
            >
              <div class="flex items-center">
                <span>{header.label}</span>
                {#if header.sortable && sortable}
                  <span class="ml-1">
                    {#if sortKey === header.key}
                      <!-- Sort direction indicator -->
                      <svg 
                        class="h-4 w-4 {sortDirection === 'desc' ? 'transform rotate-180' : ''}" 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24" 
                        aria-hidden="true"
                      >
                        <path 
                          stroke-linecap="round" 
                          stroke-linejoin="round" 
                          stroke-width="2" 
                          d="M5 15l7-7 7 7"
                        />
                      </svg>
                    {:else}
                      <!-- Sortable indicator -->
                      <svg 
                        class="h-4 w-4 text-cosmos-text-dim opacity-40" 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                        aria-hidden="true"
                      >
                        <path 
                          stroke-linecap="round" 
                          stroke-linejoin="round" 
                          stroke-width="2" 
                          d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"
                        />
                      </svg>
                    {/if}
                  </span>
                {/if}
              </div>
            </th>
          {/each}
        </tr>
      </thead>
    {/if}
    
    <tbody>
      {#if loading}
        <!-- Loading skeleton -->
        {#each Array(loadingRows) as _, i}
          <tr class="animate-pulse">
            {#each headers as header (header.key)}
              <td class={tdClasses}>
                <div class="h-4 w-3/4 rounded bg-cosmos-bg-light"></div>
              </td>
            {/each}
          </tr>
        {/each}
      {:else if rows.length === 0}
        <!-- Empty state -->
        <tr>
          <td 
            class="py-8 text-center text-cosmos-text-muted" 
            colspan={headers.length || 1}
          >
            <slot name="empty">
              {emptyMessage}
            </slot>
          </td>
        </tr>
      {:else}
        <!-- Data rows -->
        {#each rows as row, rowIndex (row.id || rowIndex)}
          <tr 
            class={[
              hoverable ? 'hover:bg-cosmos-bg-light hover:bg-opacity-40' : '',
              useStriped && rowIndex % 2 === 1 ? 'bg-cosmos-bg-light bg-opacity-10' : '',
              row.isHighlighted ? row.highlightClass || 'bg-primary bg-opacity-5' : '',
              row.clickable ? 'cursor-pointer' : '',
              'transition-colors duration-150'
            ].filter(Boolean).join(' ')}
            on:click={(e) => handleRowClick(row, e)}
            on:keydown={(e) => {
              if (row.clickable && (e.key === 'Enter' || e.key === ' ')) {
                e.preventDefault();
                handleRowClick(row, e);
              }
            }}
            tabindex={row.clickable ? 0 : undefined}
            role={row.clickable ? 'button' : undefined}
          >
            {#each row.cells as cell, cellIndex (cell.key)}
              <td 
                class={`${tdClasses} ${cell.align ? `text-${cell.align}` : ''}`}
                role={cellIndex === 0 ? 'rowheader' : undefined}
                scope={cellIndex === 0 ? 'row' : undefined}
              >
                <!-- svelte-ignore security-manual-escape -->
                {@html getCellHTML(cell)}
              </td>
            {/each}
          </tr>
        {/each}
      {/if}
    </tbody>
  </table>
</div>