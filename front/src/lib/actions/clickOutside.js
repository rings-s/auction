// src/lib/actions/clickOutside.js
/**
 * Svelte action to detect clicks outside an element
 */
export function clickOutside(node) {
    const handleClick = event => {
      if (node && !node.contains(event.target) && !event.defaultPrevented) {
        node.dispatchEvent(
          new CustomEvent('clickoutside', {
            detail: { node }
          })
        );
      }
    };
  
    document.addEventListener('click', handleClick, true);
    
    return {
      destroy() {
        document.removeEventListener('click', handleClick, true);
      }
    };
  }