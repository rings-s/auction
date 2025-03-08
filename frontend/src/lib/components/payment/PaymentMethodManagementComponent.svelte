<!-- src/lib/components/payment/PaymentMethodManagementComponent.svelte -->
<script>
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import Button from '$lib/components/ui/Button.svelte';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import { formatDate } from '$lib/utils/formatters';
    import { notificationStore } from '$lib/stores/notificationStore';
    
    // Props
    export let showHeader = true;
    export let title = "Payment Methods";
    export let showAddButton = true;
    export let readOnly = false;
    export let compact = false;
    export let selectable = false;
    export let selectedMethod = null;
    
    // Event dispatch
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    
    // State
    let paymentMethods = [];
    let loading = true;
    let error = null;
    let showAddForm = false;
    let selectedType = 'CREDIT_CARD';
    let isDefault = false;
    let processing = false;
    let editingMethodId = null;
    
    // Form data
    let creditCardData = {
      cardNumber: '',
      cardHolder: '',
      expiryMonth: '',
      expiryYear: '',
      cvv: '',
      billingAddress: {
        street: '',
        city: '',
        state: '',
        zipCode: '',
        country: 'United States'
      }
    };
    
    let bankAccountData = {
      bankName: '',
      accountNumber: '',
      routingNumber: '',
      accountType: 'CHECKING',
      accountHolder: '',
      billingAddress: {
        street: '',
        city: '',
        state: '',
        zipCode: '',
        country: 'United States'
      }
    };
    
    let paypalData = {
      email: ''
    };
    
    // Available payment method types
    const paymentMethodTypes = [
      { value: 'CREDIT_CARD', label: 'Credit/Debit Card' },
      { value: 'BANK_TRANSFER', label: 'Bank Account' },
      { value: 'PAYPAL', label: 'PayPal' }
    ];
    
    // Available account types for bank accounts
    const accountTypes = [
      { value: 'CHECKING', label: 'Checking Account' },
      { value: 'SAVINGS', label: 'Savings Account' },
      { value: 'BUSINESS', label: 'Business Account' }
    ];
    
    // Available credit card types
    const creditCardTypes = [
      { value: 'VISA', label: 'Visa' },
      { value: 'MASTERCARD', label: 'Mastercard' },
      { value: 'AMEX', label: 'American Express' },
      { value: 'DISCOVER', label: 'Discover' }
    ];
    
    // Available countries
    const countries = [
      'United States',
      'Canada',
      'United Kingdom',
      'Australia',
      'Germany',
      'France',
      'Japan'
    ];
    
    // Expiry year options (current year + 20 years)
    const currentYear = new Date().getFullYear();
    const expiryYears = Array.from({ length: 21 }, (_, i) => (currentYear + i).toString());
    
    // Expiry month options
    const expiryMonths = Array.from({ length: 12 }, (_, i) => (i + 1).toString().padStart(2, '0'));
    
    // Load payment methods
    async function loadPaymentMethods() {
      try {
        loading = true;
        error = null;
        
        const response = await api.payment_method.list();
        
        if (response && response.results) {
          paymentMethods = response.results;
        } else {
          paymentMethods = [];
        }
        
        loading = false;
      } catch (err) {
        console.error('Error loading payment methods:', err);
        error = 'Failed to load payment methods';
        loading = false;
      }
    }
    
    // Reset form
    function resetForm() {
      selectedType = 'CREDIT_CARD';
      isDefault = false;
      editingMethodId = null;
      
      creditCardData = {
        cardNumber: '',
        cardHolder: '',
        expiryMonth: '',
        expiryYear: '',
        cvv: '',
        billingAddress: {
          street: '',
          city: '',
          state: '',
          zipCode: '',
          country: 'United States'
        }
      };
      
      bankAccountData = {
        bankName: '',
        accountNumber: '',
        routingNumber: '',
        accountType: 'CHECKING',
        accountHolder: '',
        billingAddress: {
          street: '',
          city: '',
          state: '',
          zipCode: '',
          country: 'United States'
        }
      };
      
      paypalData = {
        email: ''
      };
      
      showAddForm = false;
    }
    
    // Show edit form for a payment method
    function editPaymentMethod(method) {
      editingMethodId = method.id;
      selectedType = method.method_type;
      isDefault = method.is_default;
      
      // Pre-fill form data based on method type
      if (method.method_type === 'CREDIT_CARD') {
        const details = method.details || {};
        
        creditCardData = {
          cardNumber: details.cardNumber || `**** **** **** ${details.last4 || ''}`,
          cardHolder: details.cardHolder || '',
          expiryMonth: details.expiryMonth || '',
          expiryYear: details.expiryYear || '',
          cvv: '',
          billingAddress: details.billingAddress || {
            street: '',
            city: '',
            state: '',
            zipCode: '',
            country: 'United States'
          }
        };
      } else if (method.method_type === 'BANK_TRANSFER') {
        const details = method.details || {};
        
        bankAccountData = {
          bankName: details.bankName || '',
          accountNumber: details.accountNumber || `******${details.last4 || ''}`,
          routingNumber: details.routingNumber || `******${details.routing_last4 || ''}`,
          accountType: details.accountType || 'CHECKING',
          accountHolder: details.accountHolder || '',
          billingAddress: details.billingAddress || {
            street: '',
            city: '',
            state: '',
            zipCode: '',
            country: 'United States'
          }
        };
      } else if (method.method_type === 'PAYPAL') {
        paypalData = {
          email: method.details?.email || ''
        };
      }
      
      showAddForm = true;
    }
    
    // Get form validation errors
    function getValidationErrors() {
      const errors = [];
      
      if (selectedType === 'CREDIT_CARD') {
        if (!editingMethodId && !creditCardData.cardNumber) {
          errors.push('Card number is required');
        }
        if (!creditCardData.cardHolder) {
          errors.push('Cardholder name is required');
        }
        if (!creditCardData.expiryMonth) {
          errors.push('Expiration month is required');
        }
        if (!creditCardData.expiryYear) {
          errors.push('Expiration year is required');
        }
        if (!editingMethodId && !creditCardData.cvv) {
          errors.push('CVV is required');
        }
      } else if (selectedType === 'BANK_TRANSFER') {
        if (!bankAccountData.bankName) {
          errors.push('Bank name is required');
        }
        if (!editingMethodId && !bankAccountData.accountNumber) {
          errors.push('Account number is required');
        }
        if (!editingMethodId && !bankAccountData.routingNumber) {
          errors.push('Routing number is required');
        }
        if (!bankAccountData.accountHolder) {
          errors.push('Account holder name is required');
        }
      } else if (selectedType === 'PAYPAL') {
        if (!paypalData.email) {
          errors.push('PayPal email is required');
        } else if (!/^\S+@\S+\.\S+$/.test(paypalData.email)) {
          errors.push('Invalid email format');
        }
      }
      
      return errors;
    }
    
    // Save payment method
    async function savePaymentMethod() {
      const errors = getValidationErrors();
      
      if (errors.length > 0) {
        notificationStore.error(errors[0]);
        return;
      }
      
      try {
        processing = true;
        
        // Prepare payment method data based on type
        let methodData = {
          method_type: selectedType,
          is_default: isDefault,
          details: {}
        };
        
        if (selectedType === 'CREDIT_CARD') {
          methodData.details = {
            cardHolder: creditCardData.cardHolder,
            expiryMonth: creditCardData.expiryMonth,
            expiryYear: creditCardData.expiryYear,
            billingAddress: creditCardData.billingAddress
          };
          
          // Only include card number and CVV for new payment methods
          if (!editingMethodId) {
            methodData.details.cardNumber = creditCardData.cardNumber;
            methodData.details.cvv = creditCardData.cvv;
          }
        } else if (selectedType === 'BANK_TRANSFER') {
          methodData.details = {
            bankName: bankAccountData.bankName,
            accountType: bankAccountData.accountType,
            accountHolder: bankAccountData.accountHolder,
            billingAddress: bankAccountData.billingAddress
          };
          
          // Only include account/routing numbers for new payment methods
          if (!editingMethodId) {
            methodData.details.accountNumber = bankAccountData.accountNumber;
            methodData.details.routingNumber = bankAccountData.routingNumber;
          }
        } else if (selectedType === 'PAYPAL') {
          methodData.details = {
            email: paypalData.email
          };
        }
        
        // Create or update payment method
        if (editingMethodId) {
          await api.payment_method.update(editingMethodId, methodData);
          notificationStore.success('Payment method updated successfully');
        } else {
          await api.payment_method.create(methodData);
          notificationStore.success('Payment method added successfully');
        }
        
        // Reset form and reload payment methods
        resetForm();
        loadPaymentMethods();
      } catch (err) {
        console.error('Error saving payment method:', err);
        notificationStore.error(err.message || 'Failed to save payment method');
      } finally {
        processing = false;
      }
    }
    
    // Delete payment method
    async function deletePaymentMethod(id) {
      if (!confirm('Are you sure you want to remove this payment method?')) {
        return;
      }
      
      try {
        await api.payment_method.delete(id);
        
        notificationStore.success('Payment method removed successfully');
        loadPaymentMethods();
      } catch (err) {
        console.error('Error deleting payment method:', err);
        notificationStore.error('Failed to remove payment method');
      }
    }
    
    // Set as default payment method
    async function setAsDefault(id) {
      try {
        await api.payment_method.update(id, {
          is_default: true
        });
        
        notificationStore.success('Default payment method updated');
        loadPaymentMethods();
      } catch (err) {
        console.error('Error setting default payment method:', err);
        notificationStore.error('Failed to update default payment method');
      }
    }
    
    // Handle payment method selection
    function selectPaymentMethod(method) {
      if (!selectable) return;
      
      selectedMethod = method;
      dispatch('select', method);
    }
    
    // Get payment method icon
    function getPaymentMethodIcon(type) {
      switch (type) {
        case 'CREDIT_CARD':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
          </svg>`;
        case 'BANK_TRANSFER':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
          </svg>`;
        case 'PAYPAL':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2z" />
          </svg>`;
        default:
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>`;
      }
    }
    
    // Get payment method display name
    function getPaymentMethodDisplayName(method) {
      if (method.method_type === 'CREDIT_CARD') {
        return `${method.details?.cardHolder || 'Credit Card'} •••• ${method.details?.last4 || ''}`;
      } else if (method.method_type === 'BANK_TRANSFER') {
        return `${method.details?.bankName || 'Bank Account'} •••• ${method.details?.last4 || ''}`;
      } else if (method.method_type === 'PAYPAL') {
        return method.details?.email || 'PayPal Account';
      }
      return 'Payment Method';
    }
    
    // Initialize on mount
    onMount(() => {
      loadPaymentMethods();
    });
  </script>
  
  <div class="bg-white rounded-lg border border-primary-blue/20 overflow-hidden">
    {#if showHeader}
      <div class="px-5 py-4 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5 flex justify-between items-center">
        <h3 class="text-lg font-medium text-text-dark">{title}</h3>
        
        {#if showAddButton && !readOnly}
          <Button 
            variant="outline" 
            size="sm"
            on:click={() => {
              showAddForm = !showAddForm;
              editingMethodId = null;
            }}
          >
            {showAddForm ? 'Cancel' : 'Add Payment Method'}
          </Button>
        {/if}
      </div>
    {/if}
    
    {#if showAddForm && !readOnly}
      <div class="p-5 bg-neutral-50 border-b border-primary-blue/10">
        <h4 class="text-md font-medium text-text-dark mb-4">
          {editingMethodId ? 'Edit Payment Method' : 'Add Payment Method'}
        </h4>
        
        <div class="space-y-6">
          <!-- Payment Method Type -->
          <div>
            <label class="block text-sm font-medium text-text-dark mb-2">Payment Method Type</label>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {#each paymentMethodTypes as methodType}
                <div>
                  <input 
                    type="radio" 
                    id={`payment-type-${methodType.value}`} 
                    name="payment-type"
                    bind:group={selectedType} 
                    value={methodType.value}
                    class="sr-only peer"
                    disabled={editingMethodId}
                  />
                  <label 
                    for={`payment-type-${methodType.value}`}
                    class="flex items-center p-3 border rounded-lg cursor-pointer transition-colors peer-checked:border-secondary-blue peer-checked:bg-secondary-blue/5 peer-disabled:opacity-70 peer-disabled:cursor-not-allowed"
                  >
                    <div class="mr-3 text-secondary-blue flex-shrink-0">
                      {@html getPaymentMethodIcon(methodType.value)}
                    </div>
                    <span class="text-sm font-medium text-text-dark">{methodType.label}</span>
                  </label>
                </div>
              {/each}
            </div>
          </div>
          
          <!-- Credit Card Form -->
          {#if selectedType === 'CREDIT_CARD'}
            <div class="space-y-4">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Card Number -->
                <div>
                  <label for="card-number" class="block text-sm font-medium text-text-dark mb-1">
                    Card Number {!editingMethodId ? <span class="text-red-500">*</span> : ''}
                  </label>
                  <input
                    type="text"
                    id="card-number"
                    bind:value={creditCardData.cardNumber}
                    placeholder="**** **** **** ****"
                    class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                    disabled={editingMethodId}
                  />
                </div>
                
                <!-- Cardholder Name -->
                <div>
                  <label for="card-holder" class="block text-sm font-medium text-text-dark mb-1">
                    Cardholder Name <span class="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    id="card-holder"
                    bind:value={creditCardData.cardHolder}
                    placeholder="John Doe"
                    class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                  />
                </div>
              </div>
              
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <!-- Expiry Month -->
                <div>
                  <label for="expiry-month" class="block text-sm font-medium text-text-dark mb-1">
                    Expiry Month <span class="text-red-500">*</span>
                  </label>
                  <select
                    id="expiry-month"
                    bind:value={creditCardData.expiryMonth}
                    class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                  >
                    <option value="">Month</option>
                    {#each expiryMonths as month}
                      <option value={month}>{month}</option>
                    {/each}
                  </select>
                </div>
                
                <!-- Expiry Year -->
                <div>
                  <label for="expiry-year" class="block text-sm font-medium text-text-dark mb-1">
                    Expiry Year <span class="text-red-500">*</span>
                  </label>
                  <select
                    id="expiry-year"
                    bind:value={creditCardData.expiryYear}
                    class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                  >
                    <option value="">Year</option>
                    {#each expiryYears as year}
                      <option value={year}>{year}</option>
                    {/each}
                  </select>
                </div>
                
                <!-- CVV -->
                <div class="sm:col-span-2">
                  <label for="cvv" class="block text-sm font-medium text-text-dark mb-1">
                    Security Code (CVV) {!editingMethodId ? <span class="text-red-500">*</span> : ''}
                  </label>
                  <input
                    type="password"
                    id="cvv"
                    bind:value={creditCardData.cvv}
                    placeholder="***"
                    maxlength="4"
                    class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                    disabled={editingMethodId}
                  />
                </div>
              </div>
              
              <!-- Billing Address to be added here if needed -->
            </div>
          
          <!-- Bank Account Form -->
          {:else if selectedType === 'BANK_TRANSFER'}
            <div class="space-y-4">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Bank Name -->
                <div>
                  <label for="bank-name" class="block text-sm font-medium text-text-dark mb-1">
                    Bank Name <span class="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    id="bank-name"
                    bind:value={bankAccountData.bankName}
                    placeholder="Bank of America"
                    class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                  />
                </div>
                
                <!-- Account Type -->
                <div>
                  <label for="account-type" class="block text-sm font-medium text-text-dark mb-1">
                    Account Type
                  </label>
                  <select
                    id="account-type"
                    bind:value={bankAccountData.accountType}
                    class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                  >
                    {#each accountTypes as type}
                      <option value={type.value}>{type.label}</option>
                    {/each}
                  </select>
                </div>
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Account Number -->
                <div>
                  <label for="account-number" class="block text-sm font-medium text-text-dark mb-1">
                    Account Number {!editingMethodId ? <span class="text-red-500">*</span> : ''}
                  </label>
                  <input
                    type="text"
                    id="account-number"
                    bind:value={bankAccountData.accountNumber}
                    placeholder="**** **** **** ****"
                    class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                    disabled={editingMethodId}
                  />
                </div>
                
                <!-- Routing Number -->
                <div>
                  <label for="routing-number" class="block text-sm font-medium text-text-dark mb-1">
                    Routing Number {!editingMethodId ? <span class="text-red-500">*</span> : ''}
                  </label>
                  <input
                    type="text"
                    id="routing-number"
                    bind:value={bankAccountData.routingNumber}
                    placeholder="*********"
                    class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                    disabled={editingMethodId}
                  />
                </div>
              </div>
              
              <!-- Account Holder -->
              <div>
                <label for="account-holder" class="block text-sm font-medium text-text-dark mb-1">
                  Account Holder Name <span class="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="account-holder"
                  bind:value={bankAccountData.accountHolder}
                  placeholder="John Doe"
                  class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                />
              </div>
              
              <!-- Billing Address to be added here if needed -->
            </div>
          
          <!-- PayPal Form -->
          {:else if selectedType === 'PAYPAL'}
            <div class="space-y-4">
              <!-- PayPal Email -->
              <div>
                <label for="paypal-email" class="block text-sm font-medium text-text-dark mb-1">
                  PayPal Email <span class="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  id="paypal-email"
                  bind:value={paypalData.email}
                  placeholder="your.email@example.com"
                  class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                />
              </div>
            </div>
          {/if}
          
          <!-- Set as Default -->
          <div class="flex items-center">
            <input
              id="default-payment-method"
              type="checkbox"
              bind:checked={isDefault}
              class="h-4 w-4 text-secondary-blue focus:ring-secondary-blue border-gray-300 rounded"
            />
            <label for="default-payment-method" class="ml-2 block text-sm text-text-medium">
              Set as default payment method
            </label>
          </div>
          
          <!-- Submit button -->
          <div class="flex justify-end">
            <Button 
              variant="primary" 
              size="md"
              on:click={savePaymentMethod}
              disabled={processing}
              loading={processing}
            >
              {editingMethodId ? 'Update' : 'Save'} Payment Method
            </Button>
          </div>
        </div>
      </div>
    {/if}
    
    {#if loading}
      <div class="flex justify-center items-center py-6">
        <Spinner size="md" />
      </div>
    {:else if error}
      <div class="p-5">
        <Alert variant="error">
          {error}
          <div class="mt-2">
            <Button variant="outline" size="sm" on:click={loadPaymentMethods}>
              Try Again
            </Button>
          </div>
        </Alert>
      </div>
    {:else if paymentMethods.length === 0}
      <div class="p-5 text-center py-8 text-text-medium">
        <p>No payment methods added yet</p>
        {#if showAddButton && !readOnly && !showAddForm}
          <Button 
            variant="outline" 
            size="sm"
            class="mt-2"
            on:click={() => showAddForm = true}
          >
            Add Payment Method
          </Button>
        {/if}
      </div>
    {:else if compact}
      <!-- Compact View -->
      <div class="p-5 space-y-3">
        {#each paymentMethods as method}
          <div 
            class="flex items-center justify-between p-3 border rounded-lg hover:bg-neutral-50 transition-colors {selectable ? 'cursor-pointer' : ''} {selectable && selectedMethod?.id === method.id ? 'border-secondary-blue bg-secondary-blue/5' : 'border-gray-200'}"
            on:click={() => selectPaymentMethod(method)}
          >
            <div class="flex items-center">
              <div class="text-secondary-blue flex-shrink-0 mr-3">
                {@html getPaymentMethodIcon(method.method_type)}
              </div>
              <div>
                <div class="text-sm font-medium text-text-dark">
                  {getPaymentMethodDisplayName(method)}
                </div>
                <div class="text-xs text-text-medium">
                  {paymentMethodTypes.find(t => t.value === method.method_type)?.label}
                  {#if method.is_default}
                    <span class="ml-2 px-1.5 py-0.5 rounded-sm bg-green-100 text-green-800 text-xs">Default</span>
                  {/if}
                </div>
              </div>
            </div>
            
            {#if !readOnly}
              <div class="flex space-x-2">
                <button 
                  type="button"
                  class="text-secondary-blue hover:text-secondary-blue/80 p-1"
                  on:click|stopPropagation={() => editPaymentMethod(method)}
                  title="Edit"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                  </svg>
                </button>
                <button 
                  type="button"
                  class="text-red-600 hover:text-red-500 p-1"
                  on:click|stopPropagation={() => deletePaymentMethod(method.id)}
                  title="Delete"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                  </svg>
                </button>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {:else}
      <!-- Full View -->
      <div class="p-5">
        <div class="overflow-x-auto border border-primary-blue/10 rounded-lg">
          <table class="min-w-full divide-y divide-primary-blue/10">
            <thead class="bg-primary-blue/5">
              <tr>
                {#if selectable}
                  <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-text-medium tracking-wider w-10">
                    Select
                  </th>
                {/if}
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-text-medium tracking-wider">
                  Payment Method
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-text-medium tracking-wider">
                  Type
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-text-medium tracking-wider">
                  Added On
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-text-medium tracking-wider">
                  Status
                </th>
                {#if !readOnly}
                  <th scope="col" class="px-4 py-3 text-right text-xs font-medium text-text-medium tracking-wider">
                    Actions
                  </th>
                {/if}
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-primary-blue/10">
              {#each paymentMethods as method}
                <tr class="hover:bg-neutral-50 {selectable && selectedMethod?.id === method.id ? 'bg-secondary-blue/5' : ''}">
                  {#if selectable}
                    <td class="px-4 py-4 whitespace-nowrap">
                      <input
                        type="radio"
                        name="selected-method"
                        class="h-4 w-4 text-secondary-blue focus:ring-secondary-blue border-gray-300"
                        checked={selectedMethod?.id === method.id}
                        on:change={() => selectPaymentMethod(method)}
                      />
                    </td>
                  {/if}
                  <td class="px-4 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="flex-shrink-0 h-10 w-10 rounded-full bg-primary-blue/10 flex items-center justify-center text-secondary-blue">
                        {@html getPaymentMethodIcon(method.method_type)}
                      </div>
                      <div class="ml-4">
                        <div class="text-sm font-medium text-text-dark">
                          {getPaymentMethodDisplayName(method)}
                        </div>
                        {#if method.is_default}
                          <span class="px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            Default
                          </span>
                        {/if}
                      </div>
                    </div>
                  </td>
                  <td class="px-4 py-4 whitespace-nowrap text-sm text-text-medium">
                    {paymentMethodTypes.find(t => t.value === method.method_type)?.label}
                  </td>
                  <td class="px-4 py-4 whitespace-nowrap text-sm text-text-medium">
                    {formatDate(method.created_at)}
                  </td>
                  <td class="px-4 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-medium rounded-full bg-green-100 text-green-800">
                      Active
                    </span>
                  </td>
                  {#if !readOnly}
                    <td class="px-4 py-4 whitespace-nowrap text-right text-sm font-medium">
                      {#if !method.is_default}
                        <Button 
                          variant="outline" 
                          size="xs"
                          on:click={() => setAsDefault(method.id)}
                        >
                          Set Default
                        </Button>
                      {/if}
                      
                      <Button 
                        variant="outline" 
                        size="xs"
                        class="ml-2"
                        on:click={() => editPaymentMethod(method)}
                      >
                        Edit
                      </Button>
                      
                      <Button 
                        variant="outline" 
                        size="xs"
                        class="ml-2 text-red-600 hover:bg-red-50"
                        on:click={() => deletePaymentMethod(method.id)}
                      >
                        Delete
                      </Button>
                    </td>
                  {/if}
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    {/if}
  </div>