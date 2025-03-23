// src/hooks.server.js
import { redirect } from '@sveltejs/kit';

// Routes that require authentication
const protectedRoutes = ['/profile'];

// Routes that should redirect to home if already authenticated
const authRoutes = [
	'/auth/login',
	'/auth/register',
	'/auth/reset-password',
	'/auth/reset-password-confirm'
];

// Verify if a route is protected
function isProtectedRoute(path) {
	return protectedRoutes.some((route) => path.startsWith(route));
}

// Verify if a route is an auth route
function isAuthRoute(path) {
	return authRoutes.some((route) => path.startsWith(route));
}

// Check if user is authenticated based on cookies
function isAuthenticated(cookies) {
	// Check for auth cookie
	return !!cookies.get('auth');
}

/** @type {import('@sveltejs/kit').Handle} */
export async function handle({ event, resolve }) {
	// Get path
	const path = event.url.pathname;

	// Handle API routes during SSR by returning 404
	// This prevents SSR from attempting to fetch API routes that only exist on the backend
	if (path.startsWith('/api/')) {
		console.log(`[SSR] Blocking API request to ${path}`);
		return new Response('Not found', { status: 404 });
	}

	// Check if user is authenticated
	const authenticated = isAuthenticated(event.cookies);

	// Handle protected routes
	if (isProtectedRoute(path) && !authenticated) {
		throw redirect(303, '/auth/login');
	}

	// Handle auth routes for already authenticated users
	if (isAuthRoute(path) && authenticated) {
		throw redirect(303, '/');
	}

	// Process the request
	const response = await resolve(event);

	return response;
}

/** @type {import('@sveltejs/kit').HandleServerError} */
export function handleError({ error, event }) {
	// Don't treat API 404s as real errors
	if (event.url.pathname.startsWith('/api/') && error.status === 404) {
		console.log(`[SSR] Expected 404 for API path: ${event.url.pathname}`);
		return {
			message: 'API not available during SSR',
			code: 'API_UNAVAILABLE'
		};
	}

	// Log other server errors
	console.error('Server error:', error, 'Path:', event.url.pathname);

	return {
		message: 'An unexpected error occurred',
		code: error?.code || 'UNKNOWN'
	};
}
