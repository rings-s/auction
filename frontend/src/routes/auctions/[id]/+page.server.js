// src/routes/auctions/[id]/+page.server.js
export async function load({ params }) {
    const auctionId = params.id;
    
    try {
      const auction = await api.auction.getById(auctionId);
      
      return {
        auction,
        meta: {
          title: auction.title + ' | GUDIC Auctions',
          description: auction.description.substring(0, 160),
          image: auction.image_url || auction.main_image || null
        }
      };
    } catch (error) {
      return {
        status: 404,
        error: 'Auction not found'
      };
    }
  }