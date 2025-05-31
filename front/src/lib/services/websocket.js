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
        if (this.callbacks.onConnect) this.callbacks.onConnect(event);
      },
      
      onAuctionUpdate: (auctionData) => {
        if (this.callbacks.onAuctionUpdate) this.callbacks.onAuctionUpdate(auctionData);
      },
      
      onNewBid: (bidData) => {
        if (this.callbacks.onNewBid) this.callbacks.onNewBid(bidData);
      },
      
      onStatusChange: (statusData) => {
        if (this.callbacks.onStatusChange) this.callbacks.onStatusChange(statusData);
      },
      
      onError: (error) => {
        if (this.callbacks.onError) this.callbacks.onError(error);
      },
      
      onClose: (event) => {
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