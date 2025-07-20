// front/src/lib/utils/silentFetch.js
/**
 * Silent fetch utility to prevent browser console logs
 * This wraps the native fetch API to prevent "Fetch finished loading" messages
 * from appearing in the browser console.
 */

// Create a module-scoped variable to store the original fetch
let originalFetch = null;
let originalConsole = null;

/**
 * Install the silent fetch wrapper to prevent console logs
 */
export function installSilentFetch() {
	// Only run in browser environment
	if (typeof window === 'undefined' || !window.fetch) {
		return;
	}

	// Store original fetch and console if we haven't already
	if (!originalFetch) {
		originalFetch = window.fetch;
		originalConsole = window.console;

		// Create a filtered console that suppresses fetch logs
		const filteredConsole = { ...originalConsole };
		const originalLog = originalConsole.log;
		const originalInfo = originalConsole.info;
		const originalWarn = originalConsole.warn;

		// Filter out fetch-related logs
		filteredConsole.log = function (...args) {
			const message = args.join(' ');
			if (
				!message.includes('Fetch finished loading') &&
				!message.includes('GET "http') &&
				!message.includes('POST "http') &&
				!message.includes('PUT "http') &&
				!message.includes('DELETE "http') &&
				!message.includes('PATCH "http')
			) {
				originalLog.apply(this, args);
			}
		};

		filteredConsole.info = function (...args) {
			const message = args.join(' ');
			if (
				!message.includes('Fetch finished loading') &&
				!message.includes('GET "http') &&
				!message.includes('POST "http')
			) {
				originalInfo.apply(this, args);
			}
		};

		filteredConsole.warn = function (...args) {
			const message = args.join(' ');
			if (!message.includes('Fetch finished loading')) {
				originalWarn.apply(this, args);
			}
		};

		// Replace global console
		window.console = filteredConsole;

		// Replace the global fetch with our silent version
		window.fetch = function (input, init) {
			// Disable network logging temporarily
			const originalConsoleLog = console.log;
			const originalConsoleInfo = console.info;

			// Temporarily suppress console during fetch
			console.log = () => {};
			console.info = () => {};

			const fetchPromise = originalFetch(input, init);

			// Restore console after a brief delay
			setTimeout(() => {
				console.log = originalConsoleLog;
				console.info = originalConsoleInfo;
			}, 100);

			return fetchPromise;
		};
	}
}

/**
 * Restore the original fetch function and console
 */
export function restoreOriginalFetch() {
	if (typeof window !== 'undefined') {
		if (originalFetch) {
			window.fetch = originalFetch;
			originalFetch = null;
		}
		if (originalConsole) {
			window.console = originalConsole;
			originalConsole = null;
		}
	}
}

/**
 * Check if silent fetch is installed
 */
export function isSilentFetchInstalled() {
	return originalFetch !== null;
}
