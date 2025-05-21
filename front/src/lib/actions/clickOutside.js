// src/lib/actions/clickOutside.js
/**
 * Svelte action to detect clicks outside an element
 * @param {HTMLElement} node - The element to detect clicks outside of
 * @param {Function} callback - Function to call when a click outside is detected
 */
export function clickOutside(node, callback) {
  const handleClick = event => {
    if (node && !node.contains(event.target) && !event.defaultPrevented) {
      if (typeof callback === 'function') {
        callback();
      } else {
        node.dispatchEvent(
          new CustomEvent('clickoutside', {
            detail: { node }
          })
        );
      }
    }
  };

  document.addEventListener('click', handleClick, true);
  
  return {
    destroy() {
      document.removeEventListener('click', handleClick, true);
    }
  };
}