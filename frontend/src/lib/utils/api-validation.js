// api-validation.js
export function validateAuctionData(data) {
    if (!data || typeof data !== 'object') {
      console.error('Invalid auction data format:', data);
      return false;
    }
    
    const requiredFields = ['id', 'title', 'current_price', 'end_time', 'status'];
    const missingFields = requiredFields.filter(field => !(field in data));
    
    if (missingFields.length > 0) {
      console.error('Missing required fields in auction data:', missingFields);
      return false;
    }
    
    return true;
  }