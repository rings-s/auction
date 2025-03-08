<!-- src/lib/components/contracts/ContractManagementComponent.svelte -->
<script>
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import Button from '$lib/components/ui/Button.svelte';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import { formatDate, formatCurrency } from '$lib/utils/formatters';
    import { notificationStore } from '$lib/stores/notificationStore';
    import { user } from '$lib/stores/authStore';
    
    // Props
    export let auctionId = null; // Auction ID for contract
    export let showHeader = true;
    export let title = "Contract Management";
    export let readOnly = false;
    export let viewMode = 'list'; // 'list' or 'detail'
    export let contractId = null; // For detail view of a specific contract
    
    // State
    let contracts = [];
    let currentContract = null;
    let loading = true;
    let error = null;
    let creating = false;
    let signing = false;
    let currentTerms = null;
    let showContractForm = false;
    
    // Contract form state
    let formData = {
      contract_type: 'SALE',
      contract_value: 0,
      deposit_amount: 0,
      start_date: '',
      end_date: '',
      buyer_notes: '',
      seller_notes: ''
    };
    
    // Contract status options (for display)
    const contractStatusOptions = {
      'DRAFT': { label: 'Draft', color: 'bg-yellow-100 text-yellow-800' },
      'PENDING_SELLER': { label: 'Pending Seller', color: 'bg-blue-100 text-blue-800' },
      'PENDING_BUYER': { label: 'Pending Buyer', color: 'bg-blue-100 text-blue-800' },
      'SIGNED': { label: 'Signed', color: 'bg-green-100 text-green-800' },
      'CANCELLED': { label: 'Cancelled', color: 'bg-red-100 text-red-800' },
      'COMPLETED': { label: 'Completed', color: 'bg-green-100 text-green-800' },
      'EXPIRED': { label: 'Expired', color: 'bg-gray-100 text-gray-800' }
    };
    
    // Contract type options
    const contractTypes = [
      { value: 'SALE', label: 'Sale Contract' },
      { value: 'SERVICE', label: 'Service Contract' },
      { value: 'LEASE', label: 'Lease Contract' },
      { value: 'ESCROW', label: 'Escrow Agreement' }
    ];
    
    // Load contracts
    async function loadContracts() {
      try {
        loading = true;
        error = null;
        
        let params = {};
        if (auctionId) {
          params.auction = auctionId;
        }
        
        const response = await api.contract.list({
          params
        });
        
        if (response && response.results) {
          contracts = response.results;
          
          // If in detail view and contractId is set, load the specific contract
          if (viewMode === 'detail' && contractId) {
            setCurrentContract(contractId);
          }
        } else {
          contracts = [];
        }
        
        loading = false;
      } catch (err) {
        console.error('Error loading contracts:', err);
        error = 'Failed to load contracts';
        loading = false;
      }
    }
    
    // Set current contract for detail view
    async function setCurrentContract(id) {
      try {
        loading = true;
        
        // First check if we already have this contract in the list
        let contract = contracts.find(c => c.id === id);
        
        // If not, fetch it
        if (!contract) {
          const response = await api.contract.getById(id);
          if (response) {
            contract = response;
          }
        }
        
        if (contract) {
          currentContract = contract;
          // Load contract terms
          await loadContractTerms(contract.id);
        } else {
          error = 'Contract not found';
        }
        
        loading = false;
      } catch (err) {
        console.error('Error loading contract details:', err);
        error = 'Failed to load contract details';
        loading = false;
      }
    }
    
    // Load contract terms
    async function loadContractTerms(id) {
      try {
        const response = await api.contract.getTerms(id);
        
        if (response && response.results) {
          currentTerms = response.results;
        } else {
          currentTerms = null;
        }
      } catch (err) {
        console.error('Error loading contract terms:', err);
        notificationStore.error('Failed to load contract terms');
      }
    }
    
    // Create new contract
    async function createContract() {
      if (!auctionId) {
        notificationStore.error('No auction specified for this contract');
        return;
      }
      
      try {
        creating = true;
        
        // Validate form data
        if (!formData.contract_type) {
          throw new Error('Contract type is required');
        }
        
        if (formData.contract_value <= 0) {
          throw new Error('Contract value must be greater than zero');
        }
        
        if (formData.deposit_amount < 0) {
          throw new Error('Deposit amount cannot be negative');
        }
        
        if (formData.deposit_amount > formData.contract_value) {
          throw new Error('Deposit amount cannot exceed contract value');
        }
        
        if (!formData.start_date) {
          throw new Error('Start date is required');
        }
        
        if (formData.end_date && new Date(formData.end_date) <= new Date(formData.start_date)) {
          throw new Error('End date must be after start date');
        }
        
        // Prepare contract data
        const contractData = {
          auction: auctionId,
          contract_type: formData.contract_type,
          contract_value: formData.contract_value,
          deposit_amount: formData.deposit_amount,
          start_date: formData.start_date,
          end_date: formData.end_date || null,
          status: 'DRAFT'
        };
        
        // Create contract
        const response = await api.contract.create(contractData);
        
        if (response && response.id) {
          notificationStore.success('Contract created successfully');
          
          // Create initial terms if buyer or seller notes provided
          if (formData.buyer_notes || formData.seller_notes) {
            try {
              const termsData = [];
              
              if (formData.buyer_notes) {
                termsData.push({
                  contract: response.id,
                  terms_type: 'BUYER_TERMS',
                  terms_content: formData.buyer_notes,
                  revision_reason: 'Initial terms'
                });
              }
              
              if (formData.seller_notes) {
                termsData.push({
                  contract: response.id,
                  terms_type: 'SELLER_TERMS',
                  terms_content: formData.seller_notes,
                  revision_reason: 'Initial terms'
                });
              }
              
              // Create terms (one by one)
              for (const terms of termsData) {
                await api.contract.createTerms(terms);
              }
            } catch (termsErr) {
              console.error('Error creating contract terms:', termsErr);
              notificationStore.error('Contract created but failed to add terms');
            }
          }
          
          // Reset form and refresh contracts
          resetForm();
          loadContracts();
          
          // Set to detail view of the new contract
          viewMode = 'detail';
          contractId = response.id;
          currentContract = response;
        }
      } catch (err) {
        console.error('Error creating contract:', err);
        notificationStore.error(err.message || 'Failed to create contract');
      } finally {
        creating = false;
      }
    }
    
    // Reset form
    function resetForm() {
      formData = {
        contract_type: 'SALE',
        contract_value: 0,
        deposit_amount: 0,
        start_date: new Date().toISOString().slice(0, 16),
        end_date: '',
        buyer_notes: '',
        seller_notes: ''
      };
      showContractForm = false;
    }
    
    // Sign contract
    async function signContract() {
      if (!currentContract || !currentContract.id) {
        return;
      }
      
      try {
        signing = true;
        
        // Determine if current user is buyer or seller
        const isSeller = currentContract.seller === $user?.id;
        const isBuyer = currentContract.buyer === $user?.id;
        
        if (!isSeller && !isBuyer) {
          throw new Error('You are not authorized to sign this contract');
        }
        
        // Create signature data
        const signatureData = {
          contract: currentContract.id,
          document_type: 'SIGNATURE',
          title: `${isSeller ? 'Seller' : 'Buyer'} Signature`,
          description: `Signed by ${$user?.first_name} ${$user?.last_name}`,
          typed_signature: `${$user?.first_name} ${$user?.last_name}`,
          signer_role: isSeller ? 'SELLER' : 'BUYER'
        };
        
        // Create signature document
        await api.document.create(signatureData);
        
        // Update contract status
        let updatedStatus;
        
        if (isSeller) {
          updatedStatus = 'PENDING_BUYER';
        } else {
          // If both have signed, mark as SIGNED
          if (currentContract.seller_signature_date) {
            updatedStatus = 'SIGNED';
          } else {
            updatedStatus = 'PENDING_SELLER';
          }
        }
        
        await api.contract.update(currentContract.id, {
          status: updatedStatus,
          [isSeller ? 'seller_signature_date' : 'buyer_signature_date']: new Date().toISOString()
        });
        
        notificationStore.success('Contract signed successfully');
        
        // Reload contract
        setCurrentContract(currentContract.id);
      } catch (err) {
        console.error('Error signing contract:', err);
        notificationStore.error(err.message || 'Failed to sign contract');
      } finally {
        signing = false;
      }
    }
    
    // Cancel contract
    async function cancelContract() {
      if (!currentContract || !currentContract.id) {
        return;
      }
      
      if (!confirm('Are you sure you want to cancel this contract?')) {
        return;
      }
      
      try {
        await api.contract.update(currentContract.id, {
          status: 'CANCELLED'
        });
        
        notificationStore.success('Contract cancelled successfully');
        
        // Reload contract
        setCurrentContract(currentContract.id);
      } catch (err) {
        console.error('Error cancelling contract:', err);
        notificationStore.error('Failed to cancel contract');
      }
    }
    
    // Format contract status for display
    function getContractStatusDisplay(status) {
      return contractStatusOptions[status] || { label: status, color: 'bg-gray-100 text-gray-800' };
    }
    
    // Check if user can sign contract
    function canSignContract(contract) {
      if (!contract || !$user) return false;
      
      const isSeller = contract.seller === $user.id;
      const isBuyer = contract.buyer === $user.id;
      
      if (!isSeller && !isBuyer) return false;
      
      // Check if user has already signed
      if (isSeller && contract.seller_signature_date) return false;
      if (isBuyer && contract.buyer_signature_date) return false;
      
      // Check contract status
      if (contract.status === 'CANCELLED' || contract.status === 'EXPIRED') return false;
      
      return true;
    }
    
    // Check if contract has all signatures
    function isFullySigned(contract) {
      return contract.seller_signature_date && contract.buyer_signature_date;
    }
    
    // Initialize
    onMount(() => {
      // Set default start date to today
      formData.start_date = new Date().toISOString().slice(0, 16);
      
      // Load contracts based on params
      if (auctionId || viewMode === 'detail' && contractId) {
        loadContracts();
      }
    });
    
    // Watch for changes to contractId
    $: if (contractId && viewMode === 'detail') {
      setCurrentContract(contractId);
    }
  </script>
  
  <div class="bg-white rounded-lg border border-primary-blue/20 overflow-hidden">
    {#if showHeader}
      <div class="px-5 py-4 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5 flex justify-between items-center">
        <h3 class="text-lg font-medium text-text-dark">{title}</h3>
        
        <div class="flex space-x-2">
          {#if viewMode === 'detail' && currentContract}
            <Button 
              variant="outline" 
              size="sm"
              on:click={() => { viewMode = 'list'; currentContract = null; }}
            >
              Back to List
            </Button>
          {:else if auctionId && !readOnly}
            <Button 
              variant="outline" 
              size="sm"
              on:click={() => showContractForm = !showContractForm}
            >
              {showContractForm ? 'Cancel' : 'Create Contract'}
            </Button>
          {/if}
        </div>
      </div>
    {/if}
    
    {#if showContractForm && !readOnly}
      <div class="p-5 bg-neutral-50 border-b border-primary-blue/10">
        <h4 class="text-md font-medium text-text-dark mb-4">Create New Contract</h4>
        
        <div class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Contract Type -->
            <div>
              <label for="contract-type" class="block text-sm font-medium text-text-dark mb-1">
                Contract Type <span class="text-red-500">*</span>
              </label>
              <select
                id="contract-type"
                bind:value={formData.contract_type}
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
              >
                {#each contractTypes as contractType}
                  <option value={contractType.value}>{contractType.label}</option>
                {/each}
              </select>
            </div>
            
            <!-- Contract Value -->
            <div>
              <label for="contract-value" class="block text-sm font-medium text-text-dark mb-1">
                Contract Value <span class="text-red-500">*</span>
              </label>
              <div class="relative rounded-md">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span class="text-gray-500 sm:text-sm">$</span>
                </div>
                <input
                  type="number"
                  id="contract-value"
                  bind:value={formData.contract_value}
                  min="0"
                  step="0.01"
                  class="block w-full pl-7 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                  placeholder="0.00"
                />
              </div>
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Deposit Amount -->
            <div>
              <label for="deposit-amount" class="block text-sm font-medium text-text-dark mb-1">
                Deposit Amount
              </label>
              <div class="relative rounded-md">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span class="text-gray-500 sm:text-sm">$</span>
                </div>
                <input
                  type="number"
                  id="deposit-amount"
                  bind:value={formData.deposit_amount}
                  min="0"
                  step="0.01"
                  class="block w-full pl-7 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                  placeholder="0.00"
                />
              </div>
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Start Date -->
            <div>
              <label for="start-date" class="block text-sm font-medium text-text-dark mb-1">
                Start Date <span class="text-red-500">*</span>
              </label>
              <input
                type="datetime-local"
                id="start-date"
                bind:value={formData.start_date}
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
              />
            </div>
            
            <!-- End Date -->
            <div>
              <label for="end-date" class="block text-sm font-medium text-text-dark mb-1">
                End Date
              </label>
              <input
                type="datetime-local"
                id="end-date"
                bind:value={formData.end_date}
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
              />
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Buyer Notes -->
            <div>
              <label for="buyer-notes" class="block text-sm font-medium text-text-dark mb-1">
                Buyer Terms
              </label>
              <textarea
                id="buyer-notes"
                bind:value={formData.buyer_notes}
                rows="4"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                placeholder="Terms for the buyer (optional)"
              ></textarea>
            </div>
            
            <!-- Seller Notes -->
            <div>
              <label for="seller-notes" class="block text-sm font-medium text-text-dark mb-1">
                Seller Terms
              </label>
              <textarea
                id="seller-notes"
                bind:value={formData.seller_notes}
                rows="4"
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                placeholder="Terms for the seller (optional)"
              ></textarea>
            </div>
          </div>
          
          <!-- Submit button -->
          <div class="flex justify-end">
            <Button 
              variant="primary" 
              size="md"
              on:click={createContract}
              disabled={creating || !formData.contract_type || formData.contract_value <= 0 || !formData.start_date}
              loading={creating}
            >
              Create Contract
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
            <Button variant="outline" size="sm" on:click={loadContracts}>
              Try Again
            </Button>
          </div>
        </Alert>
      </div>
    {:else if viewMode === 'list'}
      {#if contracts.length === 0}
        <div class="p-5 text-center py-8 text-text-medium">
          <p>No contracts available {!readOnly ? 'yet' : ''}</p>
          {#if auctionId && !readOnly && !showContractForm}
            <Button 
              variant="outline" 
              size="sm"
              class="mt-2"
              on:click={() => showContractForm = true}
            >
              Create Contract
            </Button>
          {/if}
        </div>
      {:else}
        <div class="p-5">
          <div class="grid grid-cols-1 gap-4">
            {#each contracts as contract}
              <div class="bg-white border border-primary-blue/10 rounded-lg hover:shadow-sm transition-shadow p-4">
                <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <div class="flex items-center">
                      <h4 class="text-md font-medium text-text-dark">
                        {contractTypes.find(ct => ct.value === contract.contract_type)?.label || contract.contract_type}
                      </h4>
                      <span class={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getContractStatusDisplay(contract.status).color}`}>
                        {getContractStatusDisplay(contract.status).label}
                      </span>
                    </div>
                    <p class="text-sm text-text-medium mt-1">
                      Contract #{contract.contract_number} • Created on {formatDate(contract.created_at)}
                    </p>
                  </div>
                  
                  <div class="mt-2 sm:mt-0 flex items-center">
                    <div class="text-right mr-4">
                      <div class="text-sm font-medium text-text-dark">Value</div>
                      <div class="text-md font-semibold text-secondary-blue">
                        {formatCurrency(contract.contract_value)}
                      </div>
                    </div>
                    
                    <Button 
                      variant="outline" 
                      size="sm"
                      on:click={() => {
                        viewMode = 'detail';
                        contractId = contract.id;
                        currentContract = contract;
                      }}
                    >
                      View Details
                    </Button>
                  </div>
                </div>
                
                <!-- Signature status -->
                {#if contract.status !== 'DRAFT' && contract.status !== 'CANCELLED'}
                  <div class="mt-3 pt-3 border-t border-primary-blue/10">
                    <div class="flex justify-between items-center text-sm">
                      <div class="flex items-center">
                        <span class="text-text-medium">Seller:</span>
                        <span class="ml-1 font-medium {contract.seller_signature_date ? 'text-green-600' : 'text-yellow-600'}">
                          {contract.seller_signature_date ? 'Signed' : 'Pending'}
                        </span>
                        {#if contract.seller_signature_date}
                          <span class="ml-1 text-text-medium text-xs">
                            ({formatDate(contract.seller_signature_date)})
                          </span>
                        {/if}
                      </div>
                      
                      <div class="flex items-center">
                        <span class="text-text-medium">Buyer:</span>
                        <span class="ml-1 font-medium {contract.buyer_signature_date ? 'text-green-600' : 'text-yellow-600'}">
                          {contract.buyer_signature_date ? 'Signed' : 'Pending'}
                        </span>
                        {#if contract.buyer_signature_date}
                          <span class="ml-1 text-text-medium text-xs">
                            ({formatDate(contract.buyer_signature_date)})
                          </span>
                        {/if}
                      </div>
                    </div>
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        </div>
      {/if}
    {:else if viewMode === 'detail' && currentContract}
      <!-- Contract Detail View -->
      <div class="p-5">
        <div class="border border-primary-blue/10 rounded-lg overflow-hidden">
          <!-- Contract Header -->
          <div class="bg-primary-blue/5 p-4 border-b border-primary-blue/10">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
              <div>
                <div class="flex items-center">
                  <h3 class="text-lg font-medium text-text-dark">
                    {contractTypes.find(ct => ct.value === currentContract.contract_type)?.label || currentContract.contract_type}
                  </h3>
                  <span class={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getContractStatusDisplay(currentContract.status).color}`}>
                    {getContractStatusDisplay(currentContract.status).label}
                  </span>
                </div>
                <p class="text-sm text-text-medium mt-1">
                  Contract #{currentContract.contract_number}
                </p>
              </div>
              
              <!-- Action buttons -->
              <div class="mt-2 sm:mt-0 flex space-x-2">
                {#if canSignContract(currentContract) && !readOnly}
                  <Button 
                    variant="primary" 
                    size="sm"
                    on:click={signContract}
                    disabled={signing}
                    loading={signing}
                  >
                    Sign Contract
                  </Button>
                {/if}
                
                {#if (currentContract.seller === $user?.id || currentContract.buyer === $user?.id) && !isFullySigned(currentContract) && !readOnly}
                  <Button 
                    variant="outline" 
                    size="sm"
                    class="text-red-600 hover:bg-red-50"
                    on:click={cancelContract}
                  >
                    Cancel
                  </Button>
                {/if}
              </div>
            </div>
          </div>
          
          <!-- Contract Body -->
          <div class="p-4">
            <!-- Contract details grid -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-x-6 gap-y-4">
              <div>
                <div class="text-sm font-medium text-text-medium">Contract Value</div>
                <div class="mt-1 text-md font-semibold text-text-dark">
                  {formatCurrency(currentContract.contract_value)}
                </div>
              </div>
              
              <div>
                <div class="text-sm font-medium text-text-medium">Deposit Amount</div>
                <div class="mt-1 text-md font-semibold text-text-dark">
                  {formatCurrency(currentContract.deposit_amount || 0)}
                </div>
              </div>
              
              <div>
                <div class="text-sm font-medium text-text-medium">Duration</div>
                <div class="mt-1 text-md text-text-dark">
                  {formatDate(currentContract.start_date)} 
                  {#if currentContract.end_date}
                    to {formatDate(currentContract.end_date)}
                  {/if}
                </div>
              </div>
              
              <div>
                <div class="text-sm font-medium text-text-medium">Seller</div>
                <div class="mt-1 text-md text-text-dark">
                  {currentContract.seller_details?.first_name} {currentContract.seller_details?.last_name}
                </div>
              </div>
              
              <div>
                <div class="text-sm font-medium text-text-medium">Buyer</div>
                <div class="mt-1 text-md text-text-dark">
                  {currentContract.buyer_details?.first_name} {currentContract.buyer_details?.last_name}
                </div>
              </div>
              
              <div>
                <div class="text-sm font-medium text-text-medium">Created</div>
                <div class="mt-1 text-md text-text-dark">
                  {formatDate(currentContract.created_at)}
                </div>
              </div>
            </div>
            
            <!-- Signature Status -->
            <div class="mt-6 pt-5 border-t border-primary-blue/10">
              <h4 class="text-md font-medium text-text-dark mb-3">Signature Status</h4>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="bg-primary-blue/5 rounded-lg p-3">
                  <div class="flex justify-between items-center">
                    <div>
                      <span class="text-sm font-medium text-text-dark">Seller Signature</span>
                      <div class="text-sm text-text-medium">
                        {currentContract.seller_details?.first_name} {currentContract.seller_details?.last_name}
                      </div>
                    </div>
                    
                    <div>
                      {#if currentContract.seller_signature_date}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Signed on {formatDate(currentContract.seller_signature_date)}
                        </span>
                      {:else}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          Awaiting Signature
                        </span>
                      {/if}
                    </div>
                  </div>
                </div>
                
                <div class="bg-primary-blue/5 rounded-lg p-3">
                  <div class="flex justify-between items-center">
                    <div>
                      <span class="text-sm font-medium text-text-dark">Buyer Signature</span>
                      <div class="text-sm text-text-medium">
                        {currentContract.buyer_details?.first_name} {currentContract.buyer_details?.last_name}
                      </div>
                    </div>
                    
                    <div>
                      {#if currentContract.buyer_signature_date}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Signed on {formatDate(currentContract.buyer_signature_date)}
                        </span>
                      {:else}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          Awaiting Signature
                        </span>
                      {/if}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Contract Terms -->
            {#if currentTerms}
              <div class="mt-6 pt-5 border-t border-primary-blue/10">
                <h4 class="text-md font-medium text-text-dark mb-3">Contract Terms</h4>
                
                <div class="space-y-4">
                  {#each currentTerms as term}
                    <div class="bg-white border border-primary-blue/10 rounded-lg p-4">
                      <div class="flex justify-between items-center mb-2">
                        <h5 class="text-sm font-medium text-text-dark">
                          {term.terms_type.replace('_', ' ')}
                        </h5>
                        <span class="text-xs text-text-medium">
                          Version {term.version_number}
                        </span>
                      </div>
                      <div class="text-sm text-text-medium whitespace-pre-wrap">
                        {term.terms_content}
                      </div>
                      {#if term.revised_by_details}
                        <div class="mt-2 text-xs text-text-medium">
                          Last revised by {term.revised_by_details.first_name} {term.revised_by_details.last_name} on {formatDate(term.created_at)}
                        </div>
                      {/if}
                    </div>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
        </div>
      </div>
    {/if}
  </div>