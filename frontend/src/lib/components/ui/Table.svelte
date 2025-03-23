<!-- src/lib/components/common/Table.svelte -->
<script>
    /**
     * Table Component
     * Reusable and configurable table with support for custom cell rendering.
     */
    import { onMount, createEventDispatcher } from 'svelte';
    import { language } from '$lib/i18n';
    
    // Props
    export let headers = []; // Array of column headers { key, label, sortable, width }
    export let rows = []; // Array of row objects { id, cells: [{ key, value, render }], isHighlighted, highlightClass }
    export let compact = false; // Compact mode with less padding
    export let bordered = false; // Add borders to cells
    export let striped = false; // Add striped rows
    export let hoverable = true; // Highlight rows on hover
    export let sortable = false; // Enable sorting (requires sortable: true in headers)
    export let sortKey = null; // Currently sorted column key
    export let sortDirection = 'asc'; // Current sort direction (asc or desc)
    export let responsive = true; // Make table responsive
    export let emptyMessage = "لا توجد بيانات لعرضها"; // Message when no rows
    export let loading = false; // Loading state
    export let loadingRows = 3; // Number of loading placeholder rows
    
    // Event dispatcher for sorting and row click events
    const dispatch = createEventDispatcher();
    
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
      'img': (props) => `<img ${renderProps(props)} />`,
      'svg': (props, content) => `<svg ${renderProps(props)}>${content || ''}</svg>`,
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
      if (!header.sortable) return;
      
      const newSortDirection = sortKey === header.key && sortDirection === 'asc' ? 'desc' : 'asc';
      
      dispatch('sort', {
        key: header.key,
        direction: newSortDirection
      });
    }
    
    // Handle row click
    function handleRowClick(row, event) {
      // Only dispatch if the click wasn't on an interactive element
      const isInteractive = event.target.closest('a, button, input, select, textarea');
      if (!isInteractive) {
        dispatch('rowClick', { row });
      }
    }
    
    // Gets cell HTML using the render function or default renderer
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
    
    // Table style classes based on props
    $: tableClasses = `w-full text-cosmos-text ${bordered ? 'border border-cosmos-bg-light' : ''}`;
    
    // Header style classes
    $: headerClasses = `bg-cosmos-bg-light bg-opacity-80 text-cosmos-text font-medium text-sm ${
      compact ? 'px-3 py-2' : 'px-4 py-3'
    } ${bordered ? 'border-b border-cosmos-bg-light' : ''}`;
    
    // TD style classes
    $: tdClasses = `${compact ? 'px-3 py-2' : 'px-4 py-3'} ${
      bordered ? 'border-b border-cosmos-bg-light' : ''
    }`;
    
    // RTL direction check
    let isRTL;
    onMount(() => {
      isRTL = $language === 'ar' || document.dir === 'rtl';
    });
  </script>
  
  <div class={responsive ? 'w-full overflow-x-auto' : ''} {...$$restProps}>
    <table class={tableClasses}>
      {#if headers.length > 0}
        <thead>
          <tr>
            {#each headers as header (header.key)}
              <th 
                class={`${headerClasses} ${header.sortable ? 'cursor-pointer select-none' : ''}`}
                style={header.width ? `width: ${header.width}` : ''}
                on:click={() => header.sortable && handleSortClick(header)}
              >
                <div class="flex items-center">
                  <span>{header.label}</span>
                  {#if header.sortable}
                    <span class="ml-1">
                      {#if sortKey === header.key}
                        <!-- Sort direction indicator -->
                        <svg 
                          class="h-4 w-4 {sortDirection === 'desc' ? 'transform rotate-180' : ''}" 
                          fill="none" 
                          stroke="currentColor" 
                          viewBox="0 0 24 24" 
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
              class={`${hoverable ? 'hover:bg-cosmos-bg-light hover:bg-opacity-40' : ''} 
                    ${striped && rowIndex % 2 === 1 ? 'bg-cosmos-bg-light bg-opacity-10' : ''}
                    ${row.isHighlighted ? row.highlightClass || 'bg-primary bg-opacity-5' : ''}
                    transition-colors duration-150`}
              on:click={(e) => handleRowClick(row, e)}
            >
              {#each row.cells as cell (cell.key)}
                <td class={tdClasses}>
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