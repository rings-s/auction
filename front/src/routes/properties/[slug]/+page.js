import { getPropertyBySlug } from '$lib/api/property.js';
import { error } from '@sveltejs/kit';

export async function load({ params }) {
  try {
    const property = await getPropertyBySlug(params.slug);
    
    if (!property) {
      throw error(404, 'Property not found');
    }

    return {
      property
    };
  } catch (err) {
    console.error('Error loading property:', err);
    throw error(404, 'Property not found');
  }
}