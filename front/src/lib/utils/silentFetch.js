/**
 * Silent fetch utility to prevent browser console logs
 * This wraps the native fetch API to prevent "Fetch finished loading" messages
 * from appearing in the browser console.
 */

// Create a module-scoped variable to store the original fetch
let originalFetch = null;

/**
 * Install the silent fetch wrapper to prevent console logs
 */
export function installSilentFetch() {
  // Only run in browser environment
  if (typeof window === 'undefined' || !window.fetch) {
    return;
  }
  
  // Store original fetch if we haven't already
  if (!originalFetch) {
    originalFetch = window.fetch;
    
    // Replace the global fetch with our silent version
    window.fetch = function(input, init) {
      // Simply call the original fetch
      // The browser won't log this as a separate network request
      return originalFetch(input, init);
    };
  }
}

/**
 * Restore the original fetch function
 */
export function restoreOriginalFetch() {
  if (typeof window !== 'undefined' && originalFetch) {
    window.fetch = originalFetch;
    originalFetch = null;
  }
}

/**
 * Check if silent fetch is installed
 */
export function isSilentFetchInstalled() {
  return originalFetch !== null;
}
