// src/lib/services/websocket.js
import { createAuctionWebSocket, sendBidThroughWebSocket } from '$lib/api/auction';

export class AuctionWebSocketService {
  constructor(auctionId) {
    this.auctionId = auctionId;
    this.socket = null;
    this.callbacks = {};
  }
  
  connect(callbacks = {}) {
    this.callbacks = callbacks;
    
    this.socket = createAuctionWebSocket(this.auctionId, {
      onOpen: (event) => {
        console.log('Auction WebSocket connected');
        if (this.callbacks.onConnect) this.callbacks.onConnect(event);
      },
      
      onAuctionUpdate: (auctionData) => {
        console.log('Auction updated:', auctionData);
        if (this.callbacks.onAuctionUpdate) this.callbacks.onAuctionUpdate(auctionData);
      },
      
      onNewBid: (bidData) => {
        console.log('New bid received:', bidData);
        if (this.callbacks.onNewBid) this.callbacks.onNewBid(bidData);
      },
      
      onStatusChange: (statusData) => {
        console.log('Auction status changed:', statusData);
        if (this.callbacks.onStatusChange) this.callbacks.onStatusChange(statusData);
      },
      
      onError: (error) => {
        console.error('WebSocket error:', error);
        if (this.callbacks.onError) this.callbacks.onError(error);
      },
      
      onClose: (event) => {
        console.log('WebSocket disconnected');
        if (this.callbacks.onClose) this.callbacks.onClose(event);
      }
    });
    
    return this.socket;
  }
  
  placeBid(bidAmount, maxBidAmount = null) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      sendBidThroughWebSocket(this.socket, this.auctionId, bidAmount, maxBidAmount);
    } else {
      throw new Error('WebSocket not connected');
    }
  }
  
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}