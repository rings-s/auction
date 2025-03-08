// src/lib/utils/routeProtection.js
import { get } from 'svelte/store';
import { isAuthenticated, primaryRole } from '$lib/stores/authStore';
import { goto } from '$app/navigation';
import { notificationStore } from '$lib/stores/notificationStore';

/**
 * Validates if the current user has the required roles
 * @param {Array<string>} allowedRoles - Array of role codes that are allowed
 * @returns {boolean} - Whether the user has permission
 */
export function hasRequiredRole(allowedRoles) {
  const authenticated = get(isAuthenticated);
  const userRole = get(primaryRole);
  
  if (!authenticated) return false;
  if (!userRole) return false;
  
  return allowedRoles.includes(userRole.code);
}

/**
 * Protects a route for specific roles
 * @param {Array<string>} allowedRoles - Array of role codes that are allowed
 * @param {string} redirectPath - Where to redirect if unauthorized
 * @param {string} message - Notification message to show if unauthorized
 */
export function protectRoute(allowedRoles, redirectPath = '/dashboard', message = 'You do not have permission to access this page') {
  const hasPermission = hasRequiredRole(allowedRoles);
  
  if (!hasPermission) {
    notificationStore.error(message);
    goto(redirectPath);
    return false;
  }
  
  return true;
}

/**
 * Seller-specific route protection 
 */
export function protectSellerRoute() {
  return protectRoute(
    ['seller', 'admin'], 
    '/dashboard', 
    'Only sellers can access this page'
  );
}

/**
 * Buyer-specific route protection
 */
export function protectBuyerRoute() {
  return protectRoute(
    ['buyer', 'seller', 'admin'], 
    '/dashboard', 
    'You must be logged in to access this page'
  );
}

/**
 * Admin-specific route protection
 */
export function protectAdminRoute() {
  return protectRoute(
    ['admin'], 
    '/dashboard', 
    'Only administrators can access this page'
  );
}

