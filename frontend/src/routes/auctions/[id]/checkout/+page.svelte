<!-- src/routes/auctions/[id]/checkout/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { fade, fly } from 'svelte/transition';
  import { isAuthenticated, user } from '$lib/stores/authStore';
  import { notificationStore } from '$lib/stores/notificationStore';
  import { api } from '$lib/api';
  import { formatCurrency, formatDate } from '$lib/utils/formatters';
  
  // UI Components
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  
  // Get the auction ID from the URL
  const auctionId = $page.params.id;
  
  // State
  let auction = null;
  let loading = true;
  let error = null;
  let shippingInfo = null;
  let paymentMethods = [];
  let selectedPaymentMethod = null;
  let loadingPaymentMethods = false;
  let processingPayment = false;
  let paymentSuccess = false;
  let transactionId = null;
  let showAddPaymentModal = false;
  let newCardDetails = {
    cardNumber: '',
    cardHolder: '',
    expiryMonth: '',
    expiryYear: '',
    cvv: ''
  };
  let saveNewCard = true;
  let newCardErrors = {};
  let addingCard = false;
  let loadingAddresses = false;
  let showAddAddressModal = false;
  let addresses = [];
  let selectedShippingAddress = null;
  let selectedBillingAddress = null;
  let useSameAddress = true;
  let newAddress = {
    fullName: '',
    addressLine1: '',
    addressLine2: '',
    city: '',
    state: '',
    postalCode: '',
    country: '',
    phoneNumber: '',
    isDefault: false
  };
  let newAddressErrors = {};
  let addingAddress = false;
  
  // Form validation - optimize with computed property
  $: isFormValid = selectedPaymentMethod && selectedShippingAddress && (useSameAddress || selectedBillingAddress);
  
  // Calculate payment deadline
  function getPaymentDeadline(endDate) {
    if (!endDate) return new Date();
    
    try {
      const endDateTime = new Date(endDate);
      const deadline = new Date(endDateTime);
      deadline.setDate(deadline.getDate() + 3); // 3 days to pay
      return deadline;
    } catch (error) {
      console.error('Error calculating payment deadline:', error);
      return new Date();
    }
  }
  
  // Check if payment deadline has passed
  function isPaymentDeadlinePassed(deadline) {
    return new Date() > new Date(deadline);
  }
  
  // Format credit card number with spaces
  function formatCardNumber(cardNumber) {
    if (!cardNumber) return '';
    return cardNumber.replace(/\s/g, '').replace(/(.{4})/g, '$1 ').trim();
  }
  
  // Get masked card number for display
  function getMaskedCardNumber(cardNumber) {
    if (!cardNumber) return '';
    const lastFour = cardNumber.slice(-4);
    return `•••• •••• •••• ${lastFour}`;
  }
  
  // Calculate order summary - optimized with memoization
  let orderSummary = { subtotal: 0, shipping: 0, tax: 0, total: 0, currency: 'USD' };
  
  $: if (auction) {
    const subtotal = parseFloat(auction.winning_bid?.amount || auction.current_price || 0);
    const shippingCost = parseFloat(auction.shipping_cost || 0);
    const taxRate = 0.05;
    const tax = subtotal * taxRate;
    const total = subtotal + shippingCost + tax;
    
    orderSummary = {
      subtotal,
      shipping: shippingCost,
      tax,
      total,
      currency: auction.currency || 'SAR'
    };
  }
  
  // Load auction details
  async function loadAuctionDetails() {
    try {
      loading = true;
      error = null;
      
      // Call the API to get auction details
      const response = await api.auction.getById(auctionId);
      
      if (!response) {
        throw new Error('Failed to load auction details');
      }
      
      // Check if this is the winning bidder
      const isWinner = $user && response.winning_bidder === $user.id;
      if (!isWinner) {
        notificationStore.error('You are not the winning bidder for this auction');
        goto(`/auctions/${auctionId}`);
        return;
      }
      
      // Check if payment has already been made
      if (response.payment_status && response.payment_status !== 'pending_payment') {
        notificationStore.info('Payment has already been made for this auction');
        goto(`/auctions/won`);
        return;
      }
      
      auction = response;
      
      // Check if payment deadline has passed
      const paymentDeadline = getPaymentDeadline(auction.end_time);
      if (isPaymentDeadlinePassed(paymentDeadline)) {
        error = 'Payment deadline has passed for this auction. Please contact customer support.';
      }
      
      // Parse shipping info if available
      if (auction.shipping_info) {
        if (typeof auction.shipping_info === 'string') {
          try {
            shippingInfo = JSON.parse(auction.shipping_info);
          } catch (e) {
            console.error('Error parsing shipping info:', e);
            shippingInfo = null;
          }
        } else {
          shippingInfo = auction.shipping_info;
        }
      }
      
      // Load payment methods and addresses in parallel for better performance
      await Promise.all([
        loadPaymentMethods(),
        loadUserAddresses()
      ]);
      
      loading = false;
    } catch (err) {
      console.error('Error loading auction details:', err);
      error = err.error || 'Failed to load auction details. Please try again.';
      loading = false;
      notificationStore.error(error);
    }
  }
  
  // Load user's payment methods
  async function loadPaymentMethods() {
    try {
      loadingPaymentMethods = true;
      
      const response = await api.payment.list();
      paymentMethods = response.results || [];
      
      // Select default payment method if available
      if (paymentMethods.length > 0) {
        const defaultMethod = paymentMethods.find(method => method.is_default) || paymentMethods[0];
        selectedPaymentMethod = defaultMethod.id;
      }
      
      loadingPaymentMethods = false;
    } catch (err) {
      console.error('Error loading payment methods:', err);
      loadingPaymentMethods = false;
      notificationStore.error('Failed to load payment methods');
    }
  }
  
  // Load user's addresses
  async function loadUserAddresses() {
    try {
      loadingAddresses = true;
      
      const response = await api.profile.getAddresses();
      addresses = response.results || [];
      
      // Select default addresses if available
      if (addresses.length > 0) {
        const defaultAddress = addresses.find(address => address.is_default) || addresses[0];
        selectedShippingAddress = defaultAddress.id;
        selectedBillingAddress = defaultAddress.id;
      }
      
      loadingAddresses = false;
    } catch (err) {
      console.error('Error loading addresses:', err);
      loadingAddresses = false;
      notificationStore.error('Failed to load addresses');
    }
  }
  
  // Add new payment method
  async function addPaymentMethod() {
    // Validate card details
    newCardErrors = validateCardDetails(newCardDetails);
    if (Object.keys(newCardErrors).length > 0) {
      return;
    }
    
    try {
      addingCard = true;
      
      // Format data for API
      const paymentData = {
        card_number: newCardDetails.cardNumber.replace(/\s/g, ''),
        card_holder: newCardDetails.cardHolder,
        expiry_month: newCardDetails.expiryMonth,
        expiry_year: newCardDetails.expiryYear,
        cvv: newCardDetails.cvv,
        save_card: saveNewCard,
        is_default: paymentMethods.length === 0
      };
      
      const response = await api.payment.add(paymentData);
      
      // Add to local list and select it
      paymentMethods = [...paymentMethods, response];
      selectedPaymentMethod = response.id;
      
      // Reset form and close modal
      newCardDetails = {
        cardNumber: '',
        cardHolder: '',
        expiryMonth: '',
        expiryYear: '',
        cvv: ''
      };
      newCardErrors = {};
      showAddPaymentModal = false;
      
      notificationStore.success('Payment method added successfully');
    } catch (err) {
      console.error('Error adding payment method:', err);
      notificationStore.error('Failed to add payment method');
    } finally {
      addingCard = false;
    }
  }
  
  // Validate card details
  function validateCardDetails(card) {
    const errors = {};
    
    // Card number (remove spaces when validating)
    const cardNum = card.cardNumber.replace(/\s/g, '');
    if (!cardNum) {
      errors.cardNumber = 'Card number is required';
    } else if (!/^\d{16}$/.test(cardNum)) {
      errors.cardNumber = 'Invalid card number';
    }
    
    // Card holder
    if (!card.cardHolder) {
      errors.cardHolder = 'Cardholder name is required';
    }
    
    // Expiry month
    if (!card.expiryMonth) {
      errors.expiryMonth = 'Required';
    } else if (parseInt(card.expiryMonth) < 1 || parseInt(card.expiryMonth) > 12) {
      errors.expiryMonth = 'Invalid';
    }
    
    // Expiry year
    const currentYear = new Date().getFullYear() % 100; // Get last 2 digits
    if (!card.expiryYear) {
      errors.expiryYear = 'Required';
    } else if (parseInt(card.expiryYear) < currentYear) {
      errors.expiryYear = 'Invalid';
    }
    
    // CVV
    if (!card.cvv) {
      errors.cvv = 'Required';
    } else if (!/^\d{3,4}$/.test(card.cvv)) {
      errors.cvv = 'Invalid';
    }
    
    return errors;
  }
  
  // Add new address
  async function addAddress() {
    // Validate address
    newAddressErrors = validateAddress(newAddress);
    if (Object.keys(newAddressErrors).length > 0) {
      return;
    }
    
    try {
      addingAddress = true;
      
      const response = await api.profile.addAddress(newAddress);
      
      // Add to local list and select it
      addresses = [...addresses, response];
      selectedShippingAddress = response.id;
      if (useSameAddress) {
        selectedBillingAddress = response.id;
      }
      
      // Reset form and close modal
      newAddress = {
        fullName: '',
        addressLine1: '',
        addressLine2: '',
        city: '',
        state: '',
        postalCode: '',
        country: '',
        phoneNumber: '',
        isDefault: false
      };
      newAddressErrors = {};
      showAddAddressModal = false;
      
      notificationStore.success('Address added successfully');
    } catch (err) {
      console.error('Error adding address:', err);
      notificationStore.error('Failed to add address');
    } finally {
      addingAddress = false;
    }
  }
  
  // Validate address
  function validateAddress(address) {
    const errors = {};
    
    if (!address.fullName) errors.fullName = 'Full name is required';
    if (!address.addressLine1) errors.addressLine1 = 'Address line 1 is required';
    if (!address.city) errors.city = 'City is required';
    if (!address.state) errors.state = 'State/Province is required';
    if (!address.postalCode) errors.postalCode = 'Postal code is required';
    if (!address.country) errors.country = 'Country is required';
    if (!address.phoneNumber) errors.phoneNumber = 'Phone number is required';
    
    return errors;
  }
  
  // Process payment with improved error handling
  async function processPayment() {
    if (!isFormValid) {
      notificationStore.error('Please complete all required fields');
      return;
    }
    
    try {
      processingPayment = true;
      
      const paymentData = {
        auction_id: auctionId,
        payment_method_id: selectedPaymentMethod,
        shipping_address_id: selectedShippingAddress,
        billing_address_id: useSameAddress ? selectedShippingAddress : selectedBillingAddress,
        amount: orderSummary.total,
        currency: auction.currency || 'SAR'
      };
      
      // Create transaction
      const response = await api.auction.createTransaction(auctionId, paymentData);
      
      // Update success state
      transactionId = response.id;
      paymentSuccess = true;
      processingPayment = false;
      
      // Show success notification
      notificationStore.success('Payment processed successfully!');
      
      // Automatically redirect to transaction details page after a delay
      setTimeout(() => {
        goto(`/transactions/${transactionId}`);
      }, 3000);
    } catch (err) {
      console.error('Error processing payment:', err);
      processingPayment = false;
      notificationStore.error(err.error || 'Failed to process payment. Please try again.');
    }
  }
  
  // Get address display string
  function getAddressDisplay(addressId) {
    if (!addressId || !addresses.length) return 'No address selected';
    
    const address = addresses.find(a => a.id === addressId);
    if (!address) return 'Unknown address';
    
    return `${address.fullName}, ${address.addressLine1}, ${address.city}, ${address.state}, ${address.postalCode}, ${address.country}`;
  }
  
  // Handle useSameAddress toggle
  function handleSameAddressToggle() {
    useSameAddress = !useSameAddress;
    if (useSameAddress) {
      selectedBillingAddress = selectedShippingAddress;
    }
  }
  
  // Initialization
  onMount(() => {
    if (!$isAuthenticated) {
      goto('/login?redirect=/auctions/' + auctionId + '/checkout');
      return;
    }
    
    loadAuctionDetails();
  });
</script>

<svelte:head>
  <title>Complete Purchase | GUDIC</title>
  <meta name="description" content="Complete your auction purchase" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <!-- Loading state -->
  {#if loading}
    <div class="flex flex-col items-center justify-center py-12" in:fade={{ duration: 300 }}>
      <Spinner size="lg" />
      <p class="mt-4 text-text-medium">Loading checkout details...</p>
    </div>
  
  <!-- Error state -->
  {:else if error}
    <Alert variant="error" class="my-8">
      <div class="flex flex-col items-center p-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-red-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="font-medium mb-2">{error}</p>
        {#if error.includes('deadline')}
          <a 
            href="/auctions/won"
            class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-blue hover:bg-primary-blue-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
          >
            Return to Won Auctions
          </a>
        {:else}
          <Button 
            variant="primary" 
            size="sm" 
            on:click={loadAuctionDetails}
          >
            Try Again
          </Button>
        {/if}
      </div>
    </Alert>
  
  <!-- Payment Success state -->
  {:else if paymentSuccess}
    <div class="bg-white rounded-xl border border-primary-blue/20 p-8 text-center" in:fly={{ y: 20, duration: 300 }}>
      <div class="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </div>
      
      <h2 class="text-2xl font-bold text-text-dark mb-2">Payment Successful!</h2>
      <p class="text-text-medium mb-6">
        Thank you for your purchase. Your transaction has been processed successfully.
      </p>
      
      <div class="max-w-md mx-auto mb-6 bg-slate-50 rounded-lg p-4 text-left">
        <div class="flex justify-between py-1">
          <span class="text-text-medium">Transaction ID:</span>
          <span class="text-text-dark font-medium">{transactionId}</span>
        </div>
        <div class="flex justify-between py-1">
          <span class="text-text-medium">Amount:</span>
          <span class="text-text-dark font-medium">{formatCurrency(orderSummary.total, auction.currency)}</span>
        </div>
        <div class="flex justify-between py-1">
          <span class="text-text-medium">Date:</span>
          <span class="text-text-dark font-medium">{formatDate(new Date())}</span>
        </div>
      </div>
      
      <p class="text-text-medium mb-6">
        You will be redirected to your transaction details page shortly...
      </p>
      
      <div class="flex flex-wrap gap-3 justify-center">
        <a 
          href="/auctions/won"
          class="inline-flex items-center justify-center px-4 py-2 border border-primary-blue text-sm font-medium rounded-md text-primary-blue bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
        >
          My Won Auctions
        </a>
        <a 
          href={`/transactions/${transactionId}`}
          class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-blue hover:bg-primary-blue-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
        >
          View Transaction Details
        </a>
      </div>
    </div>
  
  <!-- Checkout content -->
  {:else if auction}
    <div class="mb-6" in:fade={{ duration: 200 }}>
      <div class="flex items-center gap-2 mb-2">
        <a href="/auctions/won" class="text-text-medium hover:text-text-dark transition-colors flex items-center gap-1">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Won Auctions
        </a>
      </div>
      <h1 class="text-3xl font-bold text-text-dark">Complete Your Purchase</h1>
    </div>
    
    <!-- Checkout layout with optimized structure -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8" in:fade={{ duration: 300, delay: 100 }}>
      <!-- Left column: Payment and shipping -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Auction details card -->
        <div class="bg-white rounded-xl border border-primary-blue/20 overflow-hidden">
          <div class="px-5 py-4 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
            <h3 class="text-lg font-medium text-text-dark">Auction Details</h3>
          </div>
          
          <div class="p-5">
            <div class="flex gap-6">
              <!-- Image -->
              <div class="flex-shrink-0 w-24 h-24 sm:w-32 sm:h-32 bg-slate-100 rounded-lg overflow-hidden">
                {#if auction.image_url || auction.main_image}
                  <img 
                    src={auction.image_url || auction.main_image} 
                    alt={auction.title} 
                    class="w-full h-full object-cover"
                    on:error={(e) => e.target.src = 'https://via.placeholder.com/400x400?text=No+Image'}
                  />
                {:else}
                  <div class="flex items-center justify-center h-full bg-primary-blue/10 text-primary-blue">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                {/if}
              </div>
              
              <!-- Details -->
              <div class="flex-1">
                <h4 class="font-medium text-text-dark">{auction.title}</h4>
                <p class="text-sm text-text-medium mb-2">
                  Seller: {auction.seller_details?.name || 'Unknown seller'}
                </p>
                
                <div class="flex flex-wrap gap-y-1 mt-3">
                  <div class="w-full sm:w-1/2 text-sm">
                    <span class="text-text-medium">Auction won on:</span>
                    <span class="text-text-dark ml-1">{formatDate(auction.end_time)}</span>
                  </div>
                  <div class="w-full sm:w-1/2 text-sm">
                    <span class="text-text-medium">Payment deadline:</span>
                    <span class="text-text-dark ml-1">{formatDate(getPaymentDeadline(auction.end_time))}</span>
                  </div>
                  <div class="w-full text-sm">
                    <span class="text-text-medium">Your winning bid:</span>
                    <span class="text-secondary-blue font-medium ml-1">{formatCurrency(auction.winning_bid?.amount || auction.current_price, auction.currency)}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Payment method section -->
        <div class="bg-white rounded-xl border border-primary-blue/20 overflow-hidden">
          <div class="px-5 py-4 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
            <h3 class="text-lg font-medium text-text-dark">Payment Method</h3>
          </div>
          
          <div class="p-5">
            {#if loadingPaymentMethods}
              <div class="flex justify-center py-4">
                <Spinner size="md" />
              </div>
            {:else if paymentMethods.length === 0}
              <div class="text-center py-4">
                <p class="text-text-medium mb-4">No payment methods found. Please add a payment method to continue.</p>
                <Button 
                  variant="primary" 
                  size="sm"
                  on:click={() => showAddPaymentModal = true}
                >
                  Add Payment Method
                </Button>
              </div>
            {:else}
              <div class="space-y-3">
                {#each paymentMethods as method}
                  <label 
                    class="flex items-center p-3 border rounded-lg cursor-pointer transition-colors hover:bg-slate-50 {selectedPaymentMethod === method.id ? 'border-primary-blue bg-primary-blue/5' : 'border-slate-200'}"
                  >
                    <input 
                      type="radio" 
                      name="payment-method" 
                      value={method.id} 
                      bind:group={selectedPaymentMethod} 
                      class="h-4 w-4 text-primary-blue border-slate-300 focus:ring-primary-blue"
                    />
                    <div class="ml-3 flex-1">
                      <div class="flex items-center">
                        <span class="font-medium text-text-dark">{method.card_brand || 'Card'}</span>
                        {#if method.is_default}
                          <span class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">Default</span>
                        {/if}
                      </div>
                      <div class="text-sm text-text-medium">{getMaskedCardNumber(method.card_number)}</div>
                      <div class="text-xs text-text-medium">Expires {method.expiry_month}/{method.expiry_year}</div>
                    </div>
                  </label>
                {/each}
                
                <div class="pt-2">
                  <Button 
                    variant="outline" 
                    size="sm"
                    on:click={() => showAddPaymentModal = true}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    Add New Payment Method
                  </Button>
                </div>
              </div>
            {/if}
          </div>
        </div>
        
        <!-- Shipping address section -->
        <div class="bg-white rounded-xl border border-primary-blue/20 overflow-hidden">
          <div class="px-5 py-4 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
            <h3 class="text-lg font-medium text-text-dark">Shipping Address</h3>
          </div>
          
          <div class="p-5">
            {#if loadingAddresses}
              <div class="flex justify-center py-4">
                <Spinner size="md" />
              </div>
            {:else if addresses.length === 0}
              <div class="text-center py-4">
                <p class="text-text-medium mb-4">No addresses found. Please add a shipping address to continue.</p>
                <Button 
                  variant="primary" 
                  size="sm"
                  on:click={() => showAddAddressModal = true}
                >
                  Add Address
                </Button>
              </div>
            {:else}
              <div class="space-y-3">
                {#each addresses as address}
                  <label 
                    class="flex items-center p-3 border rounded-lg cursor-pointer transition-colors hover:bg-slate-50 {selectedShippingAddress === address.id ? 'border-primary-blue bg-primary-blue/5' : 'border-slate-200'}"
                  >
                    <input 
                      type="radio" 
                      name="shipping-address" 
                      value={address.id} 
                      bind:group={selectedShippingAddress} 
                      class="h-4 w-4 text-primary-blue border-slate-300 focus:ring-primary-blue"
                      on:change={() => {
                        if (useSameAddress) {
                          selectedBillingAddress = selectedShippingAddress;
                        }
                      }}
                    />
                    <div class="ml-3 flex-1">
                      <div class="flex items-center">
                        <span class="font-medium text-text-dark">{address.fullName}</span>
                        {#if address.isDefault}
                          <span class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">Default</span>
                        {/if}
                      </div>
                      <div class="text-sm text-text-medium">
                        {address.addressLine1}
                        {#if address.addressLine2}
                          , {address.addressLine2}
                        {/if}
                      </div>
                      <div class="text-sm text-text-medium">
                        {address.city}, {address.state}, {address.postalCode}
                      </div>
                      <div class="text-sm text-text-medium">
                        {address.country}
                      </div>
                      <div class="text-xs text-text-medium mt-1">
                        {address.phoneNumber}
                      </div>
                    </div>
                  </label>
                {/each}
                
                <div class="pt-2">
                  <Button 
                    variant="outline" 
                    size="sm"
                    on:click={() => showAddAddressModal = true}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    Add New Address
                  </Button>
                </div>
              </div>
              
              <!-- Same billing address checkbox -->
              <div class="mt-4 flex items-center">
                <input 
                  id="same-address" 
                  type="checkbox" 
                  bind:checked={useSameAddress} 
                  on:change={handleSameAddressToggle}
                  class="h-4 w-4 text-primary-blue border-slate-300 rounded focus:ring-primary-blue"
                />
                <label for="same-address" class="ml-2 text-sm text-text-dark">
                  Use same address for billing
                </label>
              </div>
            {/if}
          </div>
        </div>
        
        <!-- Billing address section (if different) -->
        {#if !useSameAddress}
          <div class="bg-white rounded-xl border border-primary-blue/20 overflow-hidden transition-all" in:fade={{ duration: 200 }}>
            <div class="px-5 py-4 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
              <h3 class="text-lg font-medium text-text-dark">Billing Address</h3>
            </div>
            
            <div class="p-5">
              {#if loadingAddresses}
                <div class="flex justify-center py-4">
                  <Spinner size="md" />
                </div>
              {:else if addresses.length === 0}
                <div class="text-center py-4">
                  <p class="text-text-medium mb-4">No addresses found. Please add a billing address to continue.</p>
                  <Button 
                    variant="primary" 
                    size="sm"
                    on:click={() => showAddAddressModal = true}
                  >
                    Add Address
                  </Button>
                </div>
              {:else}
                <div class="space-y-3">
                  {#each addresses as address}
                    <label 
                      class="flex items-center p-3 border rounded-lg cursor-pointer transition-colors hover:bg-slate-50 {selectedBillingAddress === address.id ? 'border-primary-blue bg-primary-blue/5' : 'border-slate-200'}"
                    >
                      <input 
                        type="radio" 
                        name="billing-address" 
                        value={address.id} 
                        bind:group={selectedBillingAddress} 
                        class="h-4 w-4 text-primary-blue border-slate-300 focus:ring-primary-blue"
                      />
                      <div class="ml-3 flex-1">
                        <div class="flex items-center">
                          <span class="font-medium text-text-dark">{address.fullName}</span>
                          {#if address.isDefault}
                            <span class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">Default</span>
                          {/if}
                        </div>
                        <div class="text-sm text-text-medium">
                          {address.addressLine1}
                          {#if address.addressLine2}
                            , {address.addressLine2}
                          {/if}
                        </div>
                        <div class="text-sm text-text-medium">
                          {address.city}, {address.state}, {address.postalCode}
                        </div>
                        <div class="text-sm text-text-medium">
                          {address.country}
                        </div>
                        <div class="text-xs text-text-medium mt-1">
                          {address.phoneNumber}
                        </div>
                      </div>
                    </label>
                  {/each}
                </div>
              {/if}
            </div>
          </div>
        {/if}
      </div>
      
      <!-- Right column: Order summary and checkout button -->
      <div class="space-y-6">
        <!-- Order summary -->
        <div class="bg-white rounded-xl border border-primary-blue/20 overflow-hidden sticky top-6">
          <div class="px-5 py-4 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5">
            <h3 class="text-lg font-medium text-text-dark">Order Summary</h3>
          </div>
          
          <div class="p-5">
            <div class="space-y-3">
              <div class="flex justify-between py-1">
                <span class="text-text-medium">Subtotal</span>
                <span class="text-text-dark font-medium">{formatCurrency(orderSummary.subtotal, orderSummary.currency)}</span>
              </div>
              
              <div class="flex justify-between py-1">
                <span class="text-text-medium">Shipping</span>
                <span class="text-text-dark font-medium">{formatCurrency(orderSummary.shipping, orderSummary.currency)}</span>
              </div>
              
              <div class="flex justify-between py-1">
                <span class="text-text-medium">Tax</span>
                <span class="text-text-dark font-medium">{formatCurrency(orderSummary.tax, orderSummary.currency)}</span>
              </div>
              
              <div class="border-t border-primary-blue/10 pt-3 mt-2">
                <div class="flex justify-between">
                  <span class="text-text-dark font-medium">Total</span>
                  <span class="text-secondary-blue font-bold text-lg">{formatCurrency(orderSummary.total, orderSummary.currency)}</span>
                </div>
              </div>
            </div>
            
            <div class="mt-5">
              <Button
                variant="primary"
                fullWidth={true}
                on:click={processPayment}
                disabled={processingPayment || !isFormValid}
              >
                {#if processingPayment}
                  <Spinner size="sm" class="mr-2" />
                  Processing...
                {:else}
                  Complete Purchase
                {/if}
              </Button>
              
              <p class="text-xs text-text-medium text-center mt-2">
                By completing your purchase you agree to our Terms of Service and Privacy Policy.
              </p>
            </div>
          </div>
        </div>
        
        <!-- Payment security notice -->
        <div class="bg-white rounded-xl border border-primary-blue/20 overflow-hidden p-4">
          <div class="flex items-start">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-500 mr-2 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <div>
              <h4 class="text-sm font-medium text-text-dark">Secure Payment</h4>
              <p class="text-xs text-text-medium mt-1">
                All payments are secure and encrypted. We never store your full credit card details.
              </p>
            </div>
          </div>
        </div>
        
        <!-- Need help -->
        <div class="bg-white rounded-xl border border-primary-blue/20 overflow-hidden p-4">
          <h4 class="text-sm font-medium text-text-dark mb-2">Need help?</h4>
          <p class="text-xs text-text-medium mb-3">
            If you have questions about your purchase or payment, our customer support team is here to help.
          </p>
          <a
            href="/support"
            class="inline-flex items-center justify-center w-full px-3 py-2 border border-primary-blue text-sm font-medium rounded-md text-primary-blue bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-blue"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            Contact Support
          </a>
        </div>
      </div>
    </div>
  {/if}
</div>

<!-- Add Payment Method Modal -->
<Modal
  bind:open={showAddPaymentModal}
  title="Add Payment Method"
  size="md"
>
  <div class="py-2">
    <!-- Card form -->
    <div class="space-y-4">
      <!-- Card Number -->
      <div>
        <label for="card-number" class="block text-sm font-medium text-text-dark mb-1">
          Card Number <span class="text-secondary-blue">*</span>
        </label>
        <input
          id="card-number"
          type="text"
          bind:value={newCardDetails.cardNumber}
          on:input={(e) => newCardDetails.cardNumber = formatCardNumber(e.target.value)}
          placeholder="1234 5678 9012 3456"
          maxlength="19"
          class="block w-full px-3 py-2 border border-primary-blue/30 focus:ring-secondary-blue focus:border-secondary-blue rounded-md"
          class:border-red-500={newCardErrors.cardNumber}
        />
        {#if newCardErrors.cardNumber}
          <p class="text-red-500 text-xs mt-1">{newCardErrors.cardNumber}</p>
        {/if}
      </div>
      
      <!-- Cardholder Name -->
      <div>
        <label for="card-holder" class="block text-sm font-medium text-text-dark mb-1">
          Cardholder Name <span class="text-secondary-blue">*</span>
        </label>
        <input
          id="card-holder"
          type="text"
          bind:value={newCardDetails.cardHolder}
          placeholder="John Smith"
          class="block w-full px-3 py-2 border border-primary-blue/30 focus:ring-secondary-blue focus:border-secondary-blue rounded-md"
          class:border-red-500={newCardErrors.cardHolder}
        />
        {#if newCardErrors.cardHolder}
          <p class="text-red-500 text-xs mt-1">{newCardErrors.cardHolder}</p>
        {/if}
      </div>
      
      <!-- Expiry and CVV -->
      <div class="grid grid-cols-3 gap-4">
        <div>
          <label for="expiry-month" class="block text-sm font-medium text-text-dark mb-1">
            Month <span class="text-secondary-blue">*</span>
          </label>
          <select
            id="expiry-month"
            bind:value={newCardDetails.expiryMonth}
            class="block w-full px-3 py-2 border border-primary-blue/30 focus:ring-secondary-blue focus:border-secondary-blue rounded-md"
            class:border-red-500={newCardErrors.expiryMonth}
          >
            <option value="">MM</option>
            {#each Array(12) as _, i}
              <option value={String(i + 1).padStart(2, '0')}>{String(i + 1).padStart(2, '0')}</option>
            {/each}
          </select>
          {#if newCardErrors.expiryMonth}
            <p class="text-red-500 text-xs mt-1">{newCardErrors.expiryMonth}</p>
          {/if}
        </div>
        
        <div>
          <label for="expiry-year" class="block text-sm font-medium text-text-dark mb-1">
            Year <span class="text-secondary-blue">*</span>
          </label>
          <select
            id="expiry-year"
            bind:value={newCardDetails.expiryYear}
            class="block w-full px-3 py-2 border border-primary-blue/30 focus:ring-secondary-blue focus:border-secondary-blue rounded-md"
            class:border-red-500={newCardErrors.expiryYear}
          >
            <option value="">YY</option>
            {#each Array(10) as _, i}
              {@const year = new Date().getFullYear() % 100 + i}
              <option value={year}>{year}</option>
            {/each}
          </select>
          {#if newCardErrors.expiryYear}
            <p class="text-red-500 text-xs mt-1">{newCardErrors.expiryYear}</p>
          {/if}
        </div>
        
        <div>
          <label for="cvv" class="block text-sm font-medium text-text-dark mb-1">
            CVV <span class="text-secondary-blue">*</span>
          </label>
          <input
            id="cvv"
            type="text"
            bind:value={newCardDetails.cvv}
            placeholder="123"
            maxlength="4"
            class="block w-full px-3 py-2 border border-primary-blue/30 focus:ring-secondary-blue focus:border-secondary-blue rounded-md"
            class:border-red-500={newCardErrors.cvv}
          />
          {#if newCardErrors.cvv}
            <p class="text-red-500 text-xs mt-1">{newCardErrors.cvv}</p>
          {/if}
        </div>
      </div>
      
      <!-- Save card toggle -->
      <div class="flex items-center">
        <input
          id="save-card"
          type="checkbox"
          bind:checked={saveNewCard}
          class="h-4 w-4 text-primary-blue border-slate-300 rounded focus:ring-primary-blue"
        />
        <label for="save-card" class="ml-2 text-sm text-text-dark">
          Save this card for future purchases
        </label>
      </div>
    </div>
  </div>
  
  <div slot="footer" class="flex justify-end space-x-3">
    <Button
      variant="outline"
      on:click={() => showAddPaymentModal = false}
      disabled={addingCard}
    >
      Cancel
    </Button>
    <Button
      variant="primary"
      on:click={addPaymentMethod}
      disabled={addingCard}
    >
      {#if addingCard}
        <Spinner size="sm" class="mr-2" />
        Adding...
      {:else}
        Add Payment Method
      {/if}
    </Button>
  </div>
</Modal>

<!-- Add Address Modal -->
<Modal
  bind:open={showAddAddressModal}
  title="Add Address"
  size="lg"
>
  <div class="py-2">
    <!-- Address form -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Full Name -->
      <div class="md:col-span-2">
        <label for="full-name" class="block text-sm font-medium text-text-dark mb-1">
          Full Name <span class="text-secondary-blue">*</span>
        </label>
        <input
          id="full-name"
          type="text"
          bind:value={newAddress.fullName}
          placeholder="John Smith"
          class="block w-full px-3 py-2 border border-primary-blue/30 focus:ring-secondary-blue focus:border-secondary-blue rounded-md"
          class:border-red-500={newAddressErrors.fullName}
        />
        {#if newAddressErrors.fullName}
          <p class="text-red-500 text-xs mt-1">{newAddressErrors.fullName}</p>
        {/if}
      </div>
      
      <!-- Address Line 1 -->
      <div class="md:col-span-2">
        <label for="address-line-1" class="block text-sm font-medium text-text-dark mb-1">
          Address Line 1 <span class="text-secondary-blue">*</span>
        </label>
        <input
          id="address-line-1"
          type="text"
          bind:value={newAddress.addressLine1}
          placeholder="123 Main St"
          class="block w-full px-3 py-2 border border-primary-blue/30 focus:ring-secondary-blue focus:border-secondary-blue rounded-md"
          class:border-red-500={newAddressErrors.addressLine1}
        />
        {#if newAddressErrors.addressLine1}
          <p class="text-red-500 text-xs mt-1">{newAddressErrors.addressLine1}</p>
        {/if}
      </div>
      
      <!-- Address Line 2 -->
      <div class="md:col-span-2">
        <label for="address-line-2" class="block text-sm font-medium text-text-dark mb-1">
          Address Line 2 <span class="text-text-medium">(Optional)</span>
        </label>
        <input
          id="address-line-2"
          type="text"
          bind:value={newAddress.addressLine2}
          placeholder="Apt 4B"
          class="block w-full px-3 py-2 border border-primary-blue/30 focus:ring-secondary-blue focus:border-secondary-blue rounded-md"
        />
      </div>
      
      <!-- City -->
      <div>
        <label for="city" class="block text-sm font-medium text-text-dark mb-1">
          City <span class="text-secondary-blue">*</span>
        </label>
        <input
          id="city"
          type="text"
          bind:value={newAddress.city}
          placeholder="New York"
          class="block w-full px-3 py-2 border border-primary-blue/30 focus:ring-secondary-blue focus:border-secondary-blue rounded-md"
          class:border-red-500={newAddressErrors.city}
        />
        {#if newAddressErrors.city}
          <p class="text-red-500 text-xs mt-1">{newAddressErrors.city}</p>
        {/if}
      </div>
      
      <!-- State/Province -->
      <div>
        <label for="state" class="block text-sm font-medium text-text-dark mb-1">
          State/Province <span class="text-secondary-blue">*</span>
        </label>
        <input
          id="state"
          type="text"
          bind:value={newAddress.state}
          placeholder="NY"
          class="block w-full px-3 py-2 border border-primary-blue/30 focus:ring-secondary-blue focus:border-secondary-blue rounded-md"
          class:border-red-500={newAddressErrors.state}
        />
        {#if newAddressErrors.state}
          <p class="text-red-500 text-xs mt-1">{newAddressErrors.state}</p>
        {/if}
      </div>
      
      <!-- Postal Code -->
      <div>
        <label for="postal-code" class="block text-sm font-medium text-text-dark mb-1">
          Postal Code <span class="text-secondary-blue">*</span>
        </label>
        <input
          id="postal-code"
          type="text"
          bind:value={newAddress.postalCode}
          placeholder="10001"
          class="block w-full px-3 py-2 border border-primary-blue/30 focus:ring-secondary-blue focus:border-secondary-blue rounded-md"
          class:border-red-500={newAddressErrors.postalCode}
        />
        {#if newAddressErrors.postalCode}
          <p class="text-red-500 text-xs mt-1">{newAddressErrors.postalCode}</p>
        {/if}
      </div>
      
      <!-- Country -->
      <div>
        <label for="country" class="block text-sm font-medium text-text-dark mb-1">
          Country <span class="text-secondary-blue">*</span>
        </label>
        <input
          id="country"
          type="text"
          bind:value={newAddress.country}
          placeholder="United States"
          class="block w-full px-3 py-2 border border-primary-blue/30 focus:ring-secondary-blue focus:border-secondary-blue rounded-md"
          class:border-red-500={newAddressErrors.country}
        />
        {#if newAddressErrors.country}
          <p class="text-red-500 text-xs mt-1">{newAddressErrors.country}</p>
        {/if}
      </div>
      
      <!-- Phone Number -->
      <div class="md:col-span-2">
        <label for="phone-number" class="block text-sm font-medium text-text-dark mb-1">
          Phone Number <span class="text-secondary-blue">*</span>
        </label>
        <input
          id="phone-number"
          type="tel"
          bind:value={newAddress.phoneNumber}
          placeholder="+1 (555) 123-4567"
          class="block w-full px-3 py-2 border border-primary-blue/30 focus:ring-secondary-blue focus:border-secondary-blue rounded-md"
          class:border-red-500={newAddressErrors.phoneNumber}
        />
        {#if newAddressErrors.phoneNumber}
          <p class="text-red-500 text-xs mt-1">{newAddressErrors.phoneNumber}</p>
        {/if}
      </div>
      
      <!-- Default Address toggle -->
      <div class="md:col-span-2">
        <div class="flex items-center">
          <input
            id="default-address"
            type="checkbox"
            bind:checked={newAddress.isDefault}
            class="h-4 w-4 text-primary-blue border-slate-300 rounded focus:ring-primary-blue"
          />
          <label for="default-address" class="ml-2 text-sm text-text-dark">
            Set as default address
          </label>
        </div>
      </div>
    </div>
  </div>
  
  <div slot="footer" class="flex justify-end space-x-3">
    <Button
      variant="outline"
      on:click={() => showAddAddressModal = false}
      disabled={addingAddress}
    >
      Cancel
    </Button>
    <Button
      variant="primary"
      on:click={addAddress}
      disabled={addingAddress}
    >
      {#if addingAddress}
        <Spinner size="sm" class="mr-2" />
        Adding...
      {:else}
        Add Address
      {/if}
    </Button>
  </div>
</Modal>