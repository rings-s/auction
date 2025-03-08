// src/routes/auctions/create/+page.server.js
import { redirect } from '@sveltejs/kit';

export function load({ locals }) {
  // Check if user is authenticated and is a seller
  if (!locals.user) {
    throw redirect(302, '/login?redirect=/auctions/create');
  }
  
  // Check if the user has the seller role
  if (!locals.user.roles.includes('seller') && !locals.user.roles.includes('admin')) {
    throw redirect(302, '/dashboard');
  }
  
  return {
    // Return any preloaded data if needed
  };
}
