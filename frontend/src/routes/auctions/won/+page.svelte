<!-- src/routes/auctions/won/+page.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { goto } from '$app/navigation';
  import { fade, fly, scale, slide } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import { browser } from '$app/environment';
  import { isAuthenticated, user } from '$lib/stores/authStore';
  import { notificationStore } from '$lib/stores/notificationStore';
  import { api } from '$lib/api';
  import { formatCurrency, formatDate } from '$lib/utils/formatters';
  
  // Create a local formatTimeAgo function if not exported from formatters.js
  function formatTimeAgo(date) {
    if (!date) return 'Unknown date';
    
    try {
      const now = new Date();
      const pastDate = new Date(date);
      
      if (isNaN(pastDate.getTime())) {
        return 'Invalid date';
      }
      
      const secondsAgo = Math.floor((now - pastDate) / 1000);
      
      if (secondsAgo < 60) {
        return 'just now';
      } else if (secondsAgo < 3600) {
        const minutes = Math.floor(secondsAgo / 60);
        return `${minutes} ${minutes === 1 ? 'minute' : 'minutes'} ago`;
      } else if (secondsAgo < 86400) {
        const hours = Math.floor(secondsAgo / 3600);
        return `${hours} ${hours === 1 ? 'hour' : 'hours'} ago`;
      } else if (secondsAgo < 2592000) {
        const days = Math.floor(secondsAgo / 86400);
        return `${days} ${days === 1 ? 'day' : 'days'} ago`;
      } else if (secondsAgo < 31536000) {
        const months = Math.floor(secondsAgo / 2592000);
        return `${months} ${months === 1 ? 'month' : 'months'} ago`;
      } else {
        const years = Math.floor(secondsAgo / 31536000);
        return `${years} ${years === 1 ? 'year' : 'years'} ago`;
      }
    } catch (error) {
      console.error('Error formatting time ago:', error);
      return 'Unknown date';
    }
  }
  
  // UI Components
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import ProgressIndicator from '$lib/components/ui/ProgressIndicator.svelte';
  import EmptyState from '$lib/components/ui/EmptyState.svelte';
  import FilterDropdown from '$lib/components/ui/FilterDropdown.svelte';
  import SlideOver from '$lib/components/ui/SlideOver.svelte';
  
  // Data states
  let wonAuctions = [];
  let filteredAuctions = [];
  let loading = true;
  let error = null;
  let retryCount = 0;
  
  // UI states
  let selectedAuction = null;
  let isDetailOpen = false;
  let activeTab = 'all';
  let currentSort = 'end_date';
  let sortDirection = 'desc';
  let searchQuery = '';
  let filterStatus = 'all';
  let isFilterMenuOpen = false;
  let skeletonCount = 3;
  
  // Filter options
  const statusOptions = [
    { value: 'all', label: 'All statuses' },
    { value: 'pending_payment', label: 'Pending payment' },
    { value: 'paid', label: 'Paid' },
    { value: 'shipping', label: 'Shipping' },
    { value: 'completed', label: 'Completed' }
  ];
  
  const sortOptions = [
    { value: 'end_date', label: 'End date' },
    { value: 'price', label: 'Price' },
    { value: 'title', label: 'Title' }
  ];
  
  const tabs = [
    { id: 'all', label: 'All' },
    { id: 'pending_payment', label: 'Pending Payment' },
    { id: 'paid', label: 'Paid' },
    { id: 'completed', label: 'Completed' }
  ];
  
  // Calculate payment deadline with robust date handling
  function getPaymentDeadline(endDate) {
    if (!endDate) return new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString();
    
    try {
      const endDateTime = new Date(endDate);
      
      // Check if the date is valid
      if (isNaN(endDateTime.getTime())) {
        console.warn('Invalid end date:', endDate);
        return new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString();
      }
      
      const deadline = new Date(endDateTime);
      deadline.setDate(deadline.getDate() + 3); // 3 days to pay
      return deadline.toISOString();
    } catch (error) {
      console.error('Error calculating payment deadline:', error);
      // Fallback to 3 days from now
      return new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString();
    }
  }
  
  // Calculate time remaining until payment deadline with improved error handling
  function getTimeRemaining(deadline) {
    try {
      const now = new Date();
      const deadlineDate = new Date(deadline);
      
      // Check if the date is valid
      if (isNaN(deadlineDate.getTime())) {
        console.warn('Invalid deadline date:', deadline);
        return { expired: true, text: 'Expired', percentage: 0 };
      }
      
      const diff = deadlineDate - now;
      
      if (diff <= 0) return { expired: true, text: 'Expired', percentage: 0 };
      
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      
      if (days > 0) {
        return { 
          expired: false, 
          text: `${days}d ${hours}h remaining`,
          percentage: Math.max(0, Math.min(100, (days / 3) * 100))
        };
      } else if (hours > 0) {
        return { 
          expired: false, 
          text: `${hours}h ${minutes}m remaining`,
          percentage: Math.max(0, Math.min(25, (hours / 24) * 100))
        };
      } else {
        return { 
          expired: false, 
          text: `${minutes}m remaining`,
          percentage: 5
        };
      }
    } catch (error) {
      console.error('Error calculating time remaining:', error);
      return { expired: true, text: 'Error', percentage: 0 };
    }
  }
  
  // Determine progress step based on status
  function getProgressStep(status) {
    switch(status) {
      case 'pending_payment': return 1;
      case 'paid': return 2;
      case 'shipping': return 3;
      case 'completed': return 4;
      default: return 0;
    }
  }
  
  // Get appropriate status badge
  function getStatusBadge(status) {
    switch(status) {
      case 'pending_payment': 
        return { variant: 'warning', icon: 'clock', label: 'Payment due' };
      case 'paid': 
        return { variant: 'success', icon: 'credit-card', label: 'Paid' };
      case 'shipping': 
        return { variant: 'info', icon: 'truck', label: 'Shipping' };
      case 'completed': 
        return { variant: 'success', icon: 'check-circle', label: 'Completed' };
      default: 
        return { variant: 'default', icon: 'circle', label: status };
    }
  }
  
  // Mock data for development when API endpoint is not available
  const mockWonAuctions = [
    {
      id: 'mock-1',
      title: 'Vintage Arabic Coffee Set',
      description: 'Beautiful handcrafted Arabic coffee set with intricate designs.',
      end_time: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      payment_status: 'pending_payment',
      current_price: 450,
      winning_bid: { amount: 450 },
      currency: 'SAR',
      image_url: 'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=774&q=80',
      seller_details: {
        name: 'Amir Ahmed',
        location: 'Riyadh'
      },
      transaction_id: 'mock-tr-1'
    },
    {
      id: 'mock-2',
      title: 'Antique Bedouin Carpet',
      description: 'Authentic Bedouin carpet with traditional patterns in excellent condition.',
      end_time: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      payment_status: 'paid',
      current_price: 1200,
      winning_bid: { amount: 1200 },
      currency: 'SAR',
      image_url: 'https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?ixlib=rb-1.2.1&auto=format&fit=crop&w=774&q=80',
      seller_details: {
        name: 'Fatima Al-Saud',
        location: 'Jeddah'
      },
      transaction_id: 'mock-tr-2'
    },
    {
      id: 'mock-3',
      title: 'Vintage Pearl Necklace',
      description: 'Elegant pearl necklace from the 1950s, perfect condition with original clasp.',
      end_time: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
      payment_status: 'completed',
      current_price: 3500,
      winning_bid: { amount: 3500 },
      currency: 'SAR',
      image_url: 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?ixlib=rb-1.2.1&auto=format&fit=crop&w=774&q=80',
      seller_details: {
        name: 'Layla Mansour',
        location: 'Dammam'
      },
      transaction_id: 'mock-tr-3'
    },
    {
      id: 'mock-4',
      title: 'Traditional Ornate Dagger',
      description: 'Decorative dagger with silver handle and embossed sheath. Great historical piece.',
      end_time: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      payment_status: 'shipping',
      current_price: 850,
      winning_bid: { amount: 850 },
      currency: 'SAR',
      image_url: 'https://images.unsplash.com/photo-1576866206061-27874c600568?ixlib=rb-1.2.1&auto=format&fit=crop&w=774&q=80',
      seller_details: {
        name: 'Omar Al-Farsi',
        location: 'Medina'
      },
      transaction_id: 'mock-tr-4'
    }
  ];

  // Load won auctions data with alternative approaches
  async function loadWonAuctions() {
    if (!$isAuthenticated) {
      goto('/login?redirect=/auctions/won');
      return;
    }
    
    try {
      loading = true;
      error = null;
      
      // First approach: Try using the direct won auctions endpoint
      try {
        const response = await api.auction.listWon();
        
        if (response && typeof response === 'object' && response.results) {
          wonAuctions = response.results || [];
          console.log('Using direct won auctions endpoint data');
        } else {
          throw new Error('Invalid response format from won auctions endpoint');
        }
      } catch (directError) {
        console.warn('Won auctions endpoint unavailable, trying alternative approach:', directError);
        
        // Second approach: Try to use the bids endpoint to get user's winning bids
        try {
          const bidsResponse = await api.bid.listUserBids({ 
            params: { 
              status: 'won',  // This assumes your API supports filtering by status
              is_winner: true // Alternative parameter that might be supported
            }
          });
          
          if (bidsResponse && Array.isArray(bidsResponse.results)) {
            console.log('Using user bids endpoint to get winning bids');
            
            // Extract auction IDs from winning bids
            const auctionIds = [...new Set(bidsResponse.results
              .filter(bid => bid.is_winner || bid.status === 'won')
              .map(bid => bid.auction_id || bid.auction))];
            
            if (auctionIds.length > 0) {
              // Fetch full auction details for each winning bid
              const auctionsData = await Promise.all(
                auctionIds.map(async (auctionId) => {
                  try {
                    return await api.auction.getById(auctionId);
                  } catch (error) {
                    console.warn(`Failed to fetch auction ${auctionId}:`, error);
                    return null;
                  }
                })
              );
              
              // Combine auction data with bid data
              wonAuctions = auctionsData
                .filter(auction => auction !== null)
                .map(auction => {
                  const matchingBid = bidsResponse.results.find(
                    bid => (bid.auction_id || bid.auction) === auction.id
                  );
                  
                  return {
                    ...auction,
                    winning_bid: {
                      amount: matchingBid?.amount || auction.current_price
                    },
                    payment_status: auction.payment_status || 'pending_payment'
                  };
                });
            } else {
              throw new Error('No winning bids found');
            }
          } else {
            throw new Error('Invalid response format from bids endpoint');
          }
        } catch (bidsError) {
          console.warn('Could not get winning bids, trying auction list endpoint:', bidsError);
          
          // Third approach: Try to get all auctions and filter for ones where user is winner
          try {
                          const allAuctionsResponse = await api.auction.list({
              params: {
                status: 'ended',
                user_is_winner: true  // This parameter might be supported by your API
              }
            });
            
            if (allAuctionsResponse && Array.isArray(allAuctionsResponse.results)) {
              console.log('Using filtered auction list to get won auctions');
              console.log('Raw auction data from API:', JSON.stringify(allAuctionsResponse.results));
              
              // IMPORTANT: The backend already filtered for you, so just use all results
              wonAuctions = allAuctionsResponse.results;
              
              // The user_is_winner=true parameter has already filtered for won auctions 
              // But just in case, let's add a safety check
              if (wonAuctions.length === 0) {
                // Try to see if we can manually identify won auctions based on bidder_id
                const userId = $user?.id;
                console.log('Trying to identify won auctions manually for user ID:', userId);
                
                wonAuctions = allAuctionsResponse.results.filter(auction => {
                  const userWon = 
                    auction.user_is_winner === true || 
                    auction.winner === userId || 
                    auction.winner_id === userId || 
                    auction.winning_bidder === userId ||
                    (auction.current_highest_bid && auction.current_highest_bid.bidder_id === userId);
                  return userWon;
                });
              }
              
              console.log('Filtered won auctions before processing:', JSON.stringify(wonAuctions));
              
              // Add payment_status if missing
              wonAuctions = wonAuctions.map(auction => {
                return {
                  ...auction,
                  payment_status: auction.payment_status || 'pending_payment'
                };
              });
            } else {
              throw new Error('Invalid response format from auction list endpoint');
            }
          } catch (auctionListError) {
            console.warn('All API approaches failed, using mock data:', auctionListError);
            wonAuctions = [...mockWonAuctions];
          }
        }
      }
      
      // Process auction data to ensure consistent structure
      if (wonAuctions.length > 0) {
        console.log(`Processing ${wonAuctions.length} won auctions`);
        
        wonAuctions = wonAuctions.map(auction => {
          try {
            console.log('Processing auction:', auction.id || 'unknown');
            
            // Ensure all required properties have fallback values
            const safeAuction = {
              id: auction.id || `temp-${Date.now()}`,
              end_time: auction.end_time || auction.endTime || auction.end_date || new Date().toISOString(),
              status: auction.status || 'ENDED',
              payment_status: auction.payment_status || 'pending_payment',
              title: auction.title || auction.name || 'Untitled Auction',
              description: auction.description || 'No description available',
              current_price: auction.current_price || auction.currentPrice || auction.final_price || (auction.current_highest_bid ? auction.current_highest_bid.amount : 0) || 0,
              winning_bid: auction.winning_bid || { 
                amount: auction.winning_bid_amount || auction.current_highest_bid?.amount || auction.current_price || 0
              },
              currency: auction.currency || 'SAR',
              image_url: auction.image_url || auction.imageUrl || auction.image || auction.main_image || auction.thumbnail || 'https://via.placeholder.com/400x300',
              seller_details: auction.seller_details || {
                name: (auction.seller_details?.first_name ? `${auction.seller_details.first_name} ${auction.seller_details.last_name || ''}` : null) || 
                      auction.seller_name || auction.seller?.name || auction.seller || 'Unknown Seller',
                location: auction.seller_details?.location || auction.seller_location || auction.seller?.location || 'Location not specified'
              },
              transaction_id: auction.transaction_id || auction.transactionId || `temp-tr-${auction.id}`,
            };
            
            // Add seller name if not present but first_name and last_name are
            if (auction.seller_details && 
                auction.seller_details.first_name && 
                !safeAuction.seller_details.name) {
              safeAuction.seller_details.name = `${auction.seller_details.first_name} ${auction.seller_details.last_name || ''}`;
            }
            
            const result = {
              ...safeAuction,
              paymentDeadline: getPaymentDeadline(safeAuction.end_time),
              timeRemaining: getTimeRemaining(getPaymentDeadline(safeAuction.end_time)),
              progress: getProgressStep(safeAuction.payment_status),
              statusBadge: getStatusBadge(safeAuction.payment_status)
            };
            
            return result;
          } catch (processError) {
            console.error('Error processing auction:', processError, auction);
            // Return a minimal valid auction object
            return {
              id: auction.id || `temp-${Date.now()}`,
              title: auction.title || 'Auction Data Error',
              description: auction.description || 'No description available',
              end_time: new Date().toISOString(),
              payment_status: 'pending_payment',
              current_price: auction.current_price || (auction.current_highest_bid ? auction.current_highest_bid.amount : 0) || 0,
              winning_bid: { amount: auction.current_highest_bid?.amount || auction.current_price || 0 },
              currency: auction.currency || 'SAR',
              seller_details: { 
                name: (auction.seller_details?.first_name ? `${auction.seller_details.first_name} ${auction.seller_details.last_name || ''}` : 'Unknown Seller'), 
                location: 'Location not specified' 
              },
              image_url: auction.image_url || auction.main_image || 'https://via.placeholder.com/400x300',
              paymentDeadline: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
              timeRemaining: { expired: false, text: 'Error', percentage: 0 },
              progress: 0,
              statusBadge: { variant: 'default', icon: 'circle', label: 'Error' },
              transaction_id: `temp-tr-${auction.id || Date.now()}`
            };
          }
        });
      } else {
        console.warn('No won auctions to process');
      }
      
      console.log('Processed auctions before applying filters:', JSON.stringify(wonAuctions));
      
      applyFilters();
      retryCount = 0;
      loading = false;
    } catch (err) {
      console.error('Error loading won auctions:', err);
      
      if (retryCount < 2) {
        retryCount++;
        setTimeout(() => loadWonAuctions(), 1000 * retryCount);
        return;
      }
      
      // Last resort - use mock data
      try {
        wonAuctions = [...mockWonAuctions].map(auction => ({
          ...auction,
          paymentDeadline: getPaymentDeadline(auction.end_time),
          timeRemaining: getTimeRemaining(getPaymentDeadline(auction.end_time)),
          progress: getProgressStep(auction.payment_status),
          statusBadge: getStatusBadge(auction.payment_status)
        }));
        applyFilters();
        loading = false;
      } catch (finalError) {
        error = `Failed to load your won auctions: ${err.message || 'Unknown error'}`;
        loading = false;
        notificationStore.error(error);
      }
    }
  }
  
  // Apply filters and sorting with improved type checking and error handling
  function applyFilters() {
    try {
      console.log('Starting to apply filters on', wonAuctions.length, 'auctions');
      let filtered = [...wonAuctions];
      
      // Apply status filter with type checking
      if (filterStatus && filterStatus !== 'all') {
        console.log('Filtering by status:', filterStatus);
        filtered = filtered.filter(auction => 
          auction && auction.payment_status === filterStatus
        );
        console.log('After status filter:', filtered.length, 'auctions remain');
      }
      
      // Apply tab filter with type checking
      if (activeTab && activeTab !== 'all') {
        console.log('Filtering by tab:', activeTab);
        filtered = filtered.filter(auction => 
          auction && auction.payment_status === activeTab
        );
        console.log('After tab filter:', filtered.length, 'auctions remain');
      }
      
      // Apply search with null checks and better type handling
      if (searchQuery && searchQuery.trim()) {
        console.log('Filtering by search:', searchQuery);
        const query = searchQuery.toLowerCase().trim();
        filtered = filtered.filter(auction => {
          if (!auction) return false;
          
          const titleMatch = auction.title && 
            typeof auction.title === 'string' && 
            auction.title.toLowerCase().includes(query);
            
          const sellerMatch = auction.seller_details && 
            auction.seller_details.name && 
            typeof auction.seller_details.name === 'string' && 
            auction.seller_details.name.toLowerCase().includes(query);
            
          return titleMatch || sellerMatch;
        });
        console.log('After search filter:', filtered.length, 'auctions remain');
      }
      
      // Apply sorting with safe type conversions and error handling
      filtered.sort((a, b) => {
        if (!a || !b) return 0;
        
        let valueA, valueB;
        
        try {
          switch (currentSort) {
            case 'price':
              valueA = parseFloat(a.winning_bid?.amount) || parseFloat(a.current_price) || 0;
              valueB = parseFloat(b.winning_bid?.amount) || parseFloat(b.current_price) || 0;
              break;
            case 'title':
              valueA = (a.title || '').toLowerCase();
              valueB = (b.title || '').toLowerCase();
              return sortDirection === 'asc' 
                ? valueA.localeCompare(valueB) 
                : valueB.localeCompare(valueA);
            case 'end_date':
            default:
              valueA = a.end_time ? new Date(a.end_time).getTime() : 0;
              valueB = b.end_time ? new Date(b.end_time).getTime() : 0;
          }
          
          // Handle NaN cases
          if (isNaN(valueA)) valueA = 0;
          if (isNaN(valueB)) valueB = 0;
          
          return sortDirection === 'asc' ? valueA - valueB : valueB - valueA;
        } catch (error) {
          console.error('Error during sort comparison:', error);
          return 0;
        }
      });
      
      filteredAuctions = filtered;
      console.log('Final filtered auctions count:', filteredAuctions.length);
      console.log('First auction in filtered list:', filteredAuctions[0] ? JSON.stringify(filteredAuctions[0]) : 'none');
    } catch (error) {
      console.error('Error applying filters:', error);
      filteredAuctions = wonAuctions; // Fallback to unfiltered list
      notificationStore.error('Error applying filters');
    }
  }
  
  // Handle filter changes
  function handleFilterChange() {
    applyFilters();
  }
  
  // Handle tab change
  function setActiveTab(tabId) {
    activeTab = tabId;
    applyFilters();
  }
  
  // Show auction detail with improved error handling
  function showAuctionDetail(auction) {
    if (!auction) {
      console.warn('Attempted to show details for undefined auction');
      return;
    }
    
    try {
      // Create a deep copy to avoid reference issues
      selectedAuction = JSON.parse(JSON.stringify(auction));
      
      // Ensure all required fields exist to prevent UI errors
      selectedAuction = {
        id: auction.id || `temp-${Date.now()}`,
        title: auction.title || 'Untitled Auction',
        image_url: auction.image_url || 'https://via.placeholder.com/600x400?text=No+Image',
        description: auction.description || 'No description provided.',
        end_time: auction.end_time || new Date().toISOString(),
        payment_status: auction.payment_status || 'pending_payment',
        winning_bid: auction.winning_bid || { amount: auction.current_price || 0 },
        current_price: auction.current_price || 0,
        currency: auction.currency || 'SAR',
        seller: auction.seller || 'unknown',
        seller_details: auction.seller_details || { 
          name: 'Unknown Seller', 
          location: 'Location not specified' 
        },
        ...auction
      };
      
      isDetailOpen = true;
    } catch (error) {
      console.error('Error showing auction detail:', error);
      notificationStore.error('Error showing auction details');
    }
  }
  
  // Go to checkout
  function goToCheckout(auctionId) {
    if (isBrowser()) {
      goto(`/auctions/${auctionId}/checkout`);
    }
  }
  
  // Toggle filter menu
  function toggleFilterMenu(e) {
    if (e) e.stopPropagation(); // Prevent document click from immediately closing
    isFilterMenuOpen = !isFilterMenuOpen;
  }
  
  // Close filter menu when clicking outside
  function handleClickOutside(event) {
    if (isFilterMenuOpen && isBrowser()) {
      isFilterMenuOpen = false;
    }
  }
  
  // Check if this is the browser environment
  function isBrowser() {
    return typeof window !== 'undefined';
  }

  // Initialize on mount
  onMount(() => {
    loadWonAuctions();
    
    // Only add event listeners in browser environment
    if (browser && isBrowser()) {
      // Add event listener for clicks outside the filter menu
      document.addEventListener('click', handleClickOutside);
    }
  });
  
  // Clean up on destroy
  onDestroy(() => {
    if (browser && isBrowser()) {
      document.removeEventListener('click', handleClickOutside);
    }
  });
</script>

<svelte:head>
  <title>My Won Auctions | GUDIC</title>
  <meta name="description" content="View and manage the auctions you've won" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <!-- Header with animated welcome -->
  <div class="mb-8" in:fly={{ y: -20, duration: 500 }}>
    <h1 class="text-3xl font-bold text-text-dark flex items-center">
      <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-blue to-secondary-blue">
        Won Auctions
      </span>
      {#if !loading && filteredAuctions.length > 0}
        <span class="ml-3 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-blue/10 text-secondary-blue">
          {filteredAuctions.length} {filteredAuctions.length === 1 ? 'auction' : 'auctions'}
        </span>
      {/if}
    </h1>
    <p class="mt-2 text-text-medium max-w-3xl">
      Manage auctions you've won. Complete payment or track shipping status. Payment is typically due within 3 days of auction end.
    </p>
  </div>
  
  <!-- Control bar -->
  <div class="flex flex-col md:flex-row gap-4 justify-between mb-6" in:fade={{ delay: 200, duration: 400 }}>
    <!-- Tabs -->
    <div class="flex space-x-2 overflow-x-auto pb-1 hide-scrollbar">
      {#each tabs as tab}
        <button
          class="px-4 py-2 rounded-full text-sm font-medium transition-colors whitespace-nowrap
            {activeTab === tab.id 
              ? 'bg-primary-blue text-white shadow-md' 
              : 'bg-white hover:bg-slate-50 text-text-medium border border-slate-200'}"
          on:click={() => setActiveTab(tab.id)}
        >
          {tab.label}
          {#if tab.id !== 'all' && wonAuctions.filter(a => a.payment_status === tab.id).length > 0}
            <span class="ml-1 inline-flex items-center justify-center w-5 h-5 rounded-full text-xs bg-white text-primary-blue">
              {wonAuctions.filter(a => a.payment_status === tab.id).length}
            </span>
          {/if}
        </button>
      {/each}
    </div>
    
    <!-- Filter controls -->
    <div class="flex flex-wrap gap-2">
      <!-- Search -->
      <div class="relative">
        <input
          type="text"
          placeholder="Search auctions..."
          bind:value={searchQuery}
          on:input={handleFilterChange}
          class="pl-9 pr-3 py-2 w-full md:w-64 bg-white border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-primary-blue/30 focus:border-primary-blue"
        />
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>
      
      <!-- Sort -->
      <div class="relative">
        <button 
          class="flex items-center space-x-1 px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm hover:bg-slate-50 transition-colors"
          on:click={(e) => toggleFilterMenu(e)}
          aria-label={`Sort by ${sortOptions.find(o => o.value === currentSort)?.label}`}
        >
          <span>{sortOptions.find(o => o.value === currentSort)?.label}</span>
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            class="h-4 w-4 transition-transform duration-200" 
            class:rotate-180={sortDirection === 'asc'}
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        
        <div class="absolute top-full right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-slate-200 z-10 overflow-hidden"
             class:hidden={!isFilterMenuOpen}
        >
          {#each sortOptions as option}
            <button
              class="w-full px-4 py-2 text-left text-sm hover:bg-slate-50 transition-colors"
              class:font-medium={currentSort === option.value}
              on:click={(e) => {
                e.stopPropagation();
                currentSort = option.value;
                isFilterMenuOpen = false;
                handleFilterChange();
              }}
            >
              {option.label}
            </button>
          {/each}
          
          <!-- Sort direction toggle -->
          <div class="border-t border-slate-200 mt-1">
            <button
              class="w-full px-4 py-2 text-left text-sm hover:bg-slate-50 transition-colors flex items-center"
              on:click={(e) => {
                e.stopPropagation();
                sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
                isFilterMenuOpen = false;
                handleFilterChange();
              }}
            >
              <span>Sort {sortDirection === 'asc' ? 'Ascending' : 'Descending'}</span>
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                class="h-4 w-4 ml-2" 
                class:rotate-180={sortDirection === 'asc'}
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Refresh -->
      <button 
        class="p-2 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
        on:click={loadWonAuctions}
        disabled={loading}
        aria-label="Refresh auction list"
      >
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          class="h-5 w-5 text-slate-600" 
          class:animate-spin={loading}
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </button>
    </div>
  </div>
  
  <!-- Content section -->
  <div class="space-y-6">
    <!-- Loading state with skeletons -->
    {#if loading}
      <div class="space-y-4" in:fade={{ duration: 300 }}>
        {#each Array(skeletonCount) as _, i}
          <div class="bg-white rounded-xl border border-slate-200 overflow-hidden animate-pulse">
            <div class="grid sm:grid-cols-4 gap-4 p-6">
              <!-- Image skeleton -->
              <div class="sm:col-span-1">
                <div class="h-32 bg-slate-200 rounded-lg"></div>
              </div>
              
              <!-- Content skeleton -->
              <div class="sm:col-span-3 flex flex-col justify-between space-y-4">
                <div>
                  <!-- Title and badge -->
                  <div class="flex justify-between">
                    <div class="h-6 bg-slate-200 rounded w-3/4"></div>
                    <div class="h-6 bg-slate-200 rounded-full w-20"></div>
                  </div>
                  
                  <!-- Description -->
                  <div class="h-4 bg-slate-200 rounded w-1/2 mt-3"></div>
                  <div class="h-4 bg-slate-200 rounded w-1/3 mt-2"></div>
                </div>
                
                <!-- Price and button -->
                <div class="flex justify-between items-center">
                  <div class="h-8 bg-slate-200 rounded w-24"></div>
                  <div class="h-10 bg-slate-200 rounded-lg w-32"></div>
                </div>
              </div>
            </div>
          </div>
        {/each}
      </div>
    
    <!-- Error state -->
    {:else if error}
      <Alert variant="error" class="my-8">
        <div class="flex flex-col items-center p-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-red-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p class="font-medium mb-2">{error}</p>
          <Button 
            variant="primary" 
            size="sm" 
            on:click={loadWonAuctions}
          >
            Try Again
          </Button>
        </div>
      </Alert>
    
    <!-- Empty state -->
    {:else if filteredAuctions.length === 0}
      <div class="bg-white rounded-xl border border-slate-200 p-12" in:fade={{ duration: 300 }}>
        <div class="flex flex-col items-center max-w-md mx-auto text-center">
          <div class="w-20 h-20 rounded-full bg-primary-blue/10 flex items-center justify-center mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-primary-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 class="text-xl font-semibold text-text-dark mb-2">No auctions found</h2>
          <p class="text-text-medium mb-6">
            {#if searchQuery}
              No auctions match your search criteria. Try adjusting your filters or search terms.
            {:else if activeTab !== 'all'}
              You don't have any auctions with the "{tabs.find(t => t.id === activeTab)?.label}" status.
            {:else}
              You haven't won any auctions yet. Keep bidding to win!
            {/if}
          </p>
          <div class="flex flex-wrap gap-3 justify-center">
            {#if searchQuery || activeTab !== 'all'}
              <Button 
                variant="outline" 
                size="sm"
                on:click={() => {
                  searchQuery = '';
                  activeTab = 'all';
                  handleFilterChange();
                }}
              >
                Clear Filters
              </Button>
            {/if}
            <a 
              href="/auctions" 
              class="inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-md border border-primary-blue bg-primary-blue text-white hover:bg-primary-blue/90 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-blue/30"
            >
              Browse Auctions
            </a>
          </div>
        </div>
      </div>
    
    <!-- Content - Auction cards -->
    {:else}
      <div class="space-y-4">
        {#each filteredAuctions as auction, i (auction.id)}
          <div 
            class="bg-white rounded-xl border border-slate-200 overflow-hidden hover:shadow-md transition-all duration-300 transform hover:-translate-y-1"
            in:fly={{ y: 20, delay: i * 100, duration: 400, easing: quintOut }}
          >
            <div class="grid sm:grid-cols-4 gap-6 p-6">
              <!-- Image -->
              <div class="sm:col-span-1">
                <div class="relative h-40 sm:h-32 overflow-hidden rounded-lg bg-slate-100 group">
                  {#if auction.image_url}
                    <img 
                      src={auction.image_url} 
                      alt={auction.title} 
                      class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                    />
                  {:else}
                    <div class="flex items-center justify-center h-full bg-primary-blue/10 text-primary-blue">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                  {/if}
                  
                  <!-- Status badge overlaid -->
                  <div class="absolute top-2 left-2">
                    <div 
                      class="flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium
                      {auction.payment_status === 'pending_payment' 
                        ? 'bg-amber-100 text-amber-800' 
                        : auction.payment_status === 'paid' 
                          ? 'bg-emerald-100 text-emerald-800'
                          : auction.payment_status === 'shipping'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-green-100 text-green-800'}"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        {#if auction.payment_status === 'pending_payment'}
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        {:else if auction.payment_status === 'paid'}
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                        {:else if auction.payment_status === 'shipping'}
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                        {:else}
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        {/if}
                      </svg>
                      <span>{auction.statusBadge.label}</span>
                    </div>
                  </div>
                </div>
                
                <!-- Won date -->
                <div class="mt-2 text-xs text-text-medium flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  Won {formatTimeAgo(auction.end_time)}
                </div>
              </div>
              
              <!-- Auction details -->
              <div class="sm:col-span-3 flex flex-col h-full justify-between">
                <!-- Upper section: title and seller -->
                <div>
                  <h3 class="text-lg font-semibold text-text-dark mb-1">
                    <a 
                      href={`/auctions/${auction.id}`} 
                      class="hover:text-primary-blue transition-colors"
                    >
                      {auction.title}
                    </a>
                  </h3>
                  
                  <p class="text-sm text-text-medium mb-3">
                    Seller: {auction.seller_details?.name || 'Unknown seller'}
                  </p>
                  
                  <!-- Progress bar for status -->
                  <div class="mb-4">
                    <div class="flex justify-between text-xs text-text-medium mb-1">
                      <span>Won</span>
                      <span>Payment</span>
                      <span>Shipping</span>
                      <span>Completed</span>
                    </div>
                    
                    <div class="relative h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div 
                        class="absolute left-0 top-0 h-full rounded-full
                        {auction.payment_status === 'pending_payment' 
                          ? 'bg-amber-400 w-1/4' 
                          : auction.payment_status === 'paid' 
                            ? 'bg-emerald-400 w-2/4' 
                            : auction.payment_status === 'shipping' 
                              ? 'bg-blue-400 w-3/4' 
                              : 'bg-green-400 w-full'}"
                      ></div>
                    </div>
                  </div>
                </div>
                
                <!-- Bottom section: price, deadline and action buttons -->
                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                  <!-- Price info -->
                  <div>
                    <div class="text-lg font-bold text-secondary-blue">
                      {formatCurrency(auction.winning_bid?.amount || auction.current_price, auction.currency)}
                    </div>
                    
                    <!-- Payment deadline for pending items -->
                    {#if auction.payment_status === 'pending_payment'}
                      <div class="text-xs flex items-center mt-1 font-medium
                        {auction.timeRemaining.expired ? 'text-red-600' : 'text-amber-600'}"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {auction.timeRemaining.text}
                      </div>
                    {/if}
                  </div>
                  
                  <!-- Action buttons -->
                  <div class="flex space-x-2">
                    <a
                      href="#"
                      class="inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-md border border-slate-200 bg-white text-text-dark hover:bg-slate-50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-blue/30"
                      on:click|preventDefault={() => showAuctionDetail(auction)}
                    >
                      View Details
                    </a>
                    
                    {#if auction.payment_status === 'pending_payment'}
                      <a
                        href={`/auctions/${auction.id}/checkout`}
                        class="inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-md border border-primary-blue bg-primary-blue text-black hover:bg-primary-blue/90 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-blue/30"
                      >
                        Complete Payment
                      </a>
                    {:else if auction.payment_status === 'paid' || auction.payment_status === 'shipping'}
                      <a
                        class="inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-md border border-slate-200 bg-white text-text-dark hover:bg-slate-50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-blue/30"
                        href={`/transactions/${auction.transaction_id}`}
                      >
                        Track Order
                      </a>
                    {:else if auction.payment_status === 'completed'}
                      <a
                        class="inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-md border border-slate-200 bg-white text-text-dark hover:bg-slate-50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-blue/30"
                        href={`/feedback/${auction.id}/create`}
                      >
                        Leave Feedback
                      </a>
                    {/if}
                  </div>
                </div>
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>

<!-- Slide-over panel for auction details -->
{#if isDetailOpen && selectedAuction}
  <button 
    type="button"
    class="fixed inset-0 bg-slate-900/50 z-50 backdrop-blur-sm transition-opacity duration-300 border-none appearance-none cursor-default"
    in:fade={{ duration: 200 }}
    on:click={() => isDetailOpen = false}
    on:keydown={(e) => e.key === 'Escape' && (isDetailOpen = false)}
    aria-label="Close details panel"
  ></button>
  <div 
    class="fixed inset-y-0 right-0 w-full max-w-lg bg-white shadow-xl overflow-y-auto z-50"
    role="dialog"
    tabindex="-1"
    in:fly={{ x: 300, duration: 300, easing: quintOut }}
  >
    <!-- Header -->
    <div class="sticky top-0 z-10 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
      <h3 class="text-lg font-semibold text-text-dark">Auction Details</h3>
      <button 
        class="p-2 rounded-full hover:bg-slate-100 transition-colors"
        on:click={() => isDetailOpen = false}
        aria-label="Close auction details panel"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
    
    <div class="p-6 space-y-6">
      <!-- Image gallery -->
      <div class="relative aspect-w-16 aspect-h-9">
        <img 
          src={selectedAuction.image_url || 'https://via.placeholder.com/800x450?text=No+Image'} 
          alt={selectedAuction.title}
          class="object-cover rounded-lg w-full h-full"
        />
      </div>
      
      <!-- Title and price -->
      <div>
        <div class="flex justify-between items-start">
          <h2 class="text-xl font-bold text-text-dark">{selectedAuction.title}</h2>
          <div 
            class="flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium
            {selectedAuction.payment_status === 'pending_payment' 
              ? 'bg-amber-100 text-amber-800' 
              : selectedAuction.payment_status === 'paid' 
                ? 'bg-emerald-100 text-emerald-800'
                : selectedAuction.payment_status === 'shipping'
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-green-100 text-green-800'}"
          >
            {selectedAuction.statusBadge.label}
          </div>
        </div>
        
        <div class="mt-2 text-2xl font-bold text-secondary-blue">
          {formatCurrency(selectedAuction.winning_bid?.amount || selectedAuction.current_price, selectedAuction.currency)}
        </div>
        
        <div class="mt-1 text-sm text-text-medium">
          Auction ended on {formatDate(selectedAuction.end_time)}
        </div>
      </div>
      
      <!-- Seller information -->
      <div class="bg-slate-50 rounded-lg p-4">
        <div class="font-medium text-text-dark mb-2">Seller Information</div>
        <div class="flex items-center">
          <div class="h-10 w-10 rounded-full bg-slate-200 flex items-center justify-center mr-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div>
            <div class="text-sm font-medium text-text-dark">
              {selectedAuction.seller_details?.name || 'Anonymous Seller'}
            </div>
            <div class="text-xs text-text-medium">
              {selectedAuction.seller_details?.location || 'Location not specified'}
            </div>
          </div>
        </div>
        <a
          class="inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-md border border-slate-200 bg-white text-text-dark hover:bg-slate-50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-blue/30 w-full mt-3"
          href={`/messages/${selectedAuction.seller}`}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          Contact Seller
        </a>
      </div>
      
      <!-- Item description -->
      <div>
        <h3 class="font-medium text-text-dark mb-2">Description</h3>
        <p class="text-text-medium text-sm whitespace-pre-line">
          {selectedAuction.description || 'No description provided.'}
        </p>
      </div>
      
      <!-- Timeline -->
      <div>
        <h3 class="font-medium text-text-dark mb-2">Status Timeline</h3>
        <div class="relative pl-6 pb-2">
          <div class="absolute top-0 left-2 h-full w-0.5 bg-slate-200"></div>
          
          <!-- Won auction -->
          <div class="relative mb-4">
            <div class="absolute -left-6 flex items-center justify-center w-4 h-4 rounded-full border-2 border-primary-blue bg-white"></div>
            <div class="font-medium text-sm text-text-dark">Won auction</div>
            <div class="text-xs text-text-medium">{formatDate(selectedAuction.end_time)}</div>
          </div>
          
          <!-- Payment due -->
          <div class="relative mb-4">
            <div 
              class="absolute -left-6 flex items-center justify-center w-4 h-4 rounded-full
              {selectedAuction.payment_status === 'pending_payment' 
                ? 'border-2 border-amber-500 bg-white' 
                : 'border-0 bg-amber-500'}"
            >
              {#if selectedAuction.payment_status !== 'pending_payment'}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-white" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              {/if}
            </div>
            <div class="font-medium text-sm text-text-dark">
              {selectedAuction.payment_status === 'pending_payment' ? 'Payment due' : 'Payment completed'}
            </div>
            <div class="text-xs text-text-medium">
              {selectedAuction.payment_status === 'pending_payment' 
                ? `Due by ${formatDate(selectedAuction.paymentDeadline)}` 
                : 'Payment processed'}
            </div>
          </div>
          
          <!-- Shipping -->
          <div class="relative mb-4">
            <div 
              class="absolute -left-6 flex items-center justify-center w-4 h-4 rounded-full
              {selectedAuction.payment_status === 'shipping' || selectedAuction.payment_status === 'completed'
                ? 'border-0 bg-blue-500'
                : 'border-2 border-slate-300 bg-white'}"
            >
              {#if selectedAuction.payment_status === 'shipping' || selectedAuction.payment_status === 'completed'}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-white" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              {/if}
            </div>
            <div 
              class="font-medium text-sm"
              class:text-text-dark={selectedAuction.payment_status === 'shipping' || selectedAuction.payment_status === 'completed'}
              class:text-slate-400={selectedAuction.payment_status === 'pending_payment' || selectedAuction.payment_status === 'paid'}
            >
              Shipping
            </div>
            <div class="text-xs text-text-medium">
              {selectedAuction.payment_status === 'shipping'
                ? 'Item is on its way to you'
                : selectedAuction.payment_status === 'completed'
                  ? 'Item has been shipped'
                  : 'Will start after payment'}
            </div>
          </div>
          
          <!-- Completed -->
          <div class="relative">
            <div 
              class="absolute -left-6 flex items-center justify-center w-4 h-4 rounded-full
              {selectedAuction.payment_status === 'completed'
                ? 'border-0 bg-green-500'
                : 'border-2 border-slate-300 bg-white'}"
            >
              {#if selectedAuction.payment_status === 'completed'}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-white" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              {/if}
            </div>
            <div 
              class="font-medium text-sm" 
              class:text-text-dark={selectedAuction.payment_status === 'completed'}
              class:text-slate-400={selectedAuction.payment_status !== 'completed'}
            >
              Completed
            </div>
            <div class="text-xs text-text-medium">
              {selectedAuction.payment_status === 'completed'
                ? 'Transaction complete'
                : 'Waiting for delivery confirmation'}
            </div>
          </div>
        </div>
      </div>
      
      <!-- Action buttons -->
      <div class="flex space-x-3">
        <a
          href={`/auctions/${selectedAuction.id}`}
          class="flex-1 inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-md border border-slate-200 bg-white text-text-dark hover:bg-slate-50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-blue/30"
        >
          View Auction
        </a>
        
        {#if selectedAuction.payment_status === 'pending_payment'}
          <a
            href={`/auctions/${selectedAuction.id}/checkout`}
            class="flex-1 inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-md border border-primary-blue bg-primary-blue text-black hover:bg-primary-blue/90 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-blue/30"
          >
            Complete Payment
          </a>
        {:else if selectedAuction.payment_status === 'paid' || selectedAuction.payment_status === 'shipping'}
          <a
            class="flex-1 inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-md border border-primary-blue bg-primary-blue text-white hover:bg-primary-blue/90 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-blue/30"
            href={`/transactions/${selectedAuction.transaction_id}`}
          >
            Track Order
          </a>
        {:else if selectedAuction.payment_status === 'completed'}
          <a
            class="flex-1 inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-md border border-primary-blue bg-primary-blue text-white hover:bg-primary-blue/90 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-blue/30"
            href={`/feedback/${selectedAuction.id}/create`}
          >
            Leave Feedback
          </a>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  /* Hide scrollbar but allow scrolling */
  .hide-scrollbar {
    -ms-overflow-style: none;  /* IE and Edge */
    scrollbar-width: none;  /* Firefox */
  }
  .hide-scrollbar::-webkit-scrollbar {
    display: none;  /* Chrome, Safari and Opera */
  }
  
  /* Aspect ratio container */
  .aspect-w-16 {
    position: relative;
    padding-bottom: 56.25%;
  }
  
  .aspect-w-16 > * {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    height: 100%;
    width: 100%;
  }
  
  .aspect-h-9 {
    /* This class is used together with aspect-w-16 */
    /* No additional styles needed as the aspect ratio is handled by aspect-w-16 */
  }
  
  /* Animation for skeleton loading */
  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: .5;
    }
  }
  
  .animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
</style>