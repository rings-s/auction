// +page.js
import { error } from '@sveltejs/kit';
import { fetchAuctionBySlug } from '$lib/api/auction';

/** @type {import('./$types').PageLoad} */
export async function load({ params }) {
  const { slug } = params;
  
  try {
    // Pre-load auction data for SEO and initial render
    const auction = await fetchAuctionBySlug(slug);
    
    return {
      auction,
      slug
    };
  } catch (err) {
    // Handle not found or other errors
    if (err.message.includes('404') || err.message.includes('not found')) {
      throw error(404, 'Auction not found');
    }
    
    // For other errors, let the page handle them
    return {
      auction: null,
      slug,
      error: err.message
    };
  }
}