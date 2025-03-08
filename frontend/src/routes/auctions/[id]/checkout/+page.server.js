// src/routes/auctions/[id]/checkout/+page.server.js
import { redirect } from '@sveltejs/kit';
import { api } from '$lib/server/api';

export async function load({ params, locals }) {
  const auctionId = params.id;
  
  // Check if user is authenticated
  if (!locals.user) {
    throw redirect(302, '/login?redirect=/auctions/' + auctionId + '/checkout');
  }
  
  try {
    // Fetch the auction to check whether this user is the winning bidder
    const auction = await api.auction.getById(auctionId);
    
    // Check if this is the winning bidder
    if (auction.winning_bidder !== locals.user.id) {
      throw redirect(302, '/auctions/' + auctionId);
    }
    
    // Check if payment has already been made
    if (auction.payment_status && auction.payment_status !== 'pending_payment') {
      throw redirect(302, '/auctions/won');
    }
    
    return {
      auction
    };
  } catch (error) {
    throw redirect(302, '/auctions');
  }
}
