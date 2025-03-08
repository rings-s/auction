<!-- src/lib/components/documents/DocumentManagementComponent.svelte -->
<script>
    import { onMount } from 'svelte';
    import { api } from '$lib/api';
    import Button from '$lib/components/ui/Button.svelte';
    import Spinner from '$lib/components/ui/Spinner.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import { formatDate } from '$lib/utils/formatters';
    import { notificationStore } from '$lib/stores/notificationStore';
    
    // Props
    export let auctionId = null; // Auction ID to associate documents with
    export let canEdit = false; // Whether the user can edit documents
    export let canVerify = false; // Whether the user can verify documents (admin)
    export let readOnly = false; // Read-only mode (no upload/edit)
    export let showHeader = true;
    export let title = "Auction Documents";
  
    // State
    let documents = [];
    let loading = true;
    let error = null;
    let showUploadForm = false;
    let uploadingDocument = false;
    
    // Upload form state
    let documentFile = null;
    let documentTitle = '';
    let documentType = 'GENERAL';
    let documentDescription = '';
    
    // Document types
    const documentTypes = [
      { value: 'GENERAL', label: 'General Document' },
      { value: 'CERTIFICATE', label: 'Certificate' },
      { value: 'LEGAL', label: 'Legal Document' },
      { value: 'PROOF_OF_OWNERSHIP', label: 'Proof of Ownership' },
      { value: 'INSPECTION', label: 'Inspection Report' },
      { value: 'HISTORY', label: 'History Report' },
      { value: 'CONTRACT', label: 'Contract' },
      { value: 'INVOICE', label: 'Invoice' },
      { value: 'OTHER', label: 'Other' }
    ];
    
    // Verification status options
    const verificationStatuses = [
      { value: 'PENDING', label: 'Pending Verification', color: 'bg-yellow-100 text-yellow-800' },
      { value: 'VERIFIED', label: 'Verified', color: 'bg-green-100 text-green-800' },
      { value: 'REJECTED', label: 'Rejected', color: 'bg-red-100 text-red-800' }
    ];
    
    // Load documents
    async function loadDocuments() {
      if (!auctionId) {
        documents = [];
        loading = false;
        return;
      }
      
      try {
        loading = true;
        error = null;
        
        const response = await api.document.list({
          params: { auction: auctionId }
        });
        
        if (response && response.results) {
          documents = response.results;
        } else {
          documents = [];
        }
        
        loading = false;
      } catch (err) {
        console.error('Error loading documents:', err);
        error = 'Failed to load documents';
        loading = false;
      }
    }
    
    // Handle file selection
    function handleFileChange(event) {
      const file = event.target.files[0];
      if (file) {
        documentFile = file;
        // Set default title if empty
        if (!documentTitle) {
          documentTitle = file.name.split('.')[0];
        }
      }
    }
    
    // Reset form
    function resetForm() {
      documentFile = null;
      documentTitle = '';
      documentType = 'GENERAL';
      documentDescription = '';
      showUploadForm = false;
    }
    
    // Upload document
    async function uploadDocument() {
      if (!documentFile || !documentTitle || !auctionId) {
        notificationStore.error('Please provide a file and title');
        return;
      }
      
      try {
        uploadingDocument = true;
        
        const formData = new FormData();
        formData.append('auction', auctionId);
        formData.append('file', documentFile);
        formData.append('title', documentTitle);
        formData.append('document_type', documentType);
        
        if (documentDescription) {
          formData.append('description', documentDescription);
        }
        
        await api.document.create(formData);
        
        notificationStore.success('Document uploaded successfully');
        resetForm();
        loadDocuments();
      } catch (err) {
        console.error('Error uploading document:', err);
        notificationStore.error('Failed to upload document');
      } finally {
        uploadingDocument = false;
      }
    }
    
    // Delete document
    async function deleteDocument(documentId) {
      if (!confirm('Are you sure you want to delete this document?')) {
        return;
      }
      
      try {
        await api.document.delete(documentId);
        notificationStore.success('Document deleted successfully');
        loadDocuments();
      } catch (err) {
        console.error('Error deleting document:', err);
        notificationStore.error('Failed to delete document');
      }
    }
    
    // Update verification status
    async function updateVerificationStatus(document, status) {
      try {
        await api.document.update(document.id, {
          verification_status: status
        });
        
        notificationStore.success(`Document marked as ${status.toLowerCase()}`);
        loadDocuments();
      } catch (err) {
        console.error('Error updating document verification:', err);
        notificationStore.error('Failed to update document verification status');
      }
    }
    
    // Get document type label
    function getDocumentTypeLabel(type) {
      const docType = documentTypes.find(dt => dt.value === type);
      return docType ? docType.label : type;
    }
    
    // Get verification status badge
    function getVerificationBadge(status) {
      const verStatus = verificationStatuses.find(vs => vs.value === status);
      return verStatus || { value: status, label: status, color: 'bg-gray-100 text-gray-800' };
    }
    
    // Get icon for document type
    function getDocumentIcon(type) {
      switch (type) {
        case 'CERTIFICATE':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>`;
        case 'LEGAL':
        case 'CONTRACT':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
          </svg>`;
        case 'PROOF_OF_OWNERSHIP':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path d="M9 2a2 2 0 00-2 2v8a2 2 0 002 2h6a2 2 0 002-2V6.414A2 2 0 0016.414 5L14 2.586A2 2 0 0012.586 2H9z" />
            <path d="M3 8a2 2 0 012-2v10h8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z" />
          </svg>`;
        case 'INSPECTION':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path d="M9 9a2 2 0 114 0 2 2 0 01-4 0z" />
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a4 4 0 00-3.446 6.032l-2.261 2.26a1 1 0 101.414 1.415l2.261-2.261A4 4 0 1011 5z" clip-rule="evenodd" />
          </svg>`;
        case 'HISTORY':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
          </svg>`;
        case 'INVOICE':
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5 2a2 2 0 00-2 2v14l3.5-2 3.5 2 3.5-2 3.5 2V4a2 2 0 00-2-2H5zm4.707 3.707a1 1 0 00-1.414-1.414l-3 3a1 1 0 000 1.414l3 3a1 1 0 001.414-1.414L8.414 9H10a3 3 0 013 3v1a1 1 0 102 0v-1a5 5 0 00-5-5H8.414l1.293-1.293z" clip-rule="evenodd" />
          </svg>`;
        default:
          return `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd" />
          </svg>`;
      }
    }
    
    // Initialize on mount
    onMount(() => {
      loadDocuments();
    });
  </script>
  
  <div class="bg-white rounded-lg border border-primary-blue/20 overflow-hidden">
    {#if showHeader}
      <div class="px-5 py-4 border-b border-primary-blue/10 bg-gradient-to-r from-primary-blue/5 to-primary-peach/5 flex justify-between items-center">
        <h3 class="text-lg font-medium text-text-dark">{title}</h3>
        
        {#if canEdit && !readOnly}
          <Button 
            variant="outline" 
            size="sm"
            on:click={() => showUploadForm = !showUploadForm}
          >
            {showUploadForm ? 'Cancel' : 'Upload Document'}
          </Button>
        {/if}
      </div>
    {/if}
    
    {#if showUploadForm && !readOnly}
      <div class="p-5 bg-neutral-50 border-b border-primary-blue/10">
        <h4 class="text-md font-medium text-text-dark mb-4">Upload New Document</h4>
        
        <div class="space-y-4">
          <!-- File input -->
          <div>
            <label for="document-file" class="block text-sm font-medium text-text-dark mb-1">
              Document File <span class="text-red-500">*</span>
            </label>
            <input
              type="file"
              id="document-file"
              on:change={handleFileChange}
              class="block w-full text-sm text-text-dark file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-primary-blue/10 file:text-secondary-blue hover:file:bg-primary-blue/20 cursor-pointer"
            />
            <p class="mt-1 text-xs text-text-medium">
              Accepted formats: PDF, DOC, DOCX, JPG, PNG (max 10MB)
            </p>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Document title -->
            <div>
              <label for="document-title" class="block text-sm font-medium text-text-dark mb-1">
                Document Title <span class="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="document-title"
                bind:value={documentTitle}
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
                placeholder="Enter document title"
              />
            </div>
            
            <!-- Document type -->
            <div>
              <label for="document-type" class="block text-sm font-medium text-text-dark mb-1">
                Document Type
              </label>
              <select
                id="document-type"
                bind:value={documentType}
                class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
              >
                {#each documentTypes as docType}
                  <option value={docType.value}>{docType.label}</option>
                {/each}
              </select>
            </div>
          </div>
          
          <!-- Description -->
          <div>
            <label for="document-description" class="block text-sm font-medium text-text-dark mb-1">
              Description
            </label>
            <textarea
              id="document-description"
              bind:value={documentDescription}
              rows="3"
              class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-blue focus:border-primary-blue"
              placeholder="Optional document description"
            ></textarea>
          </div>
          
          <!-- Submit button -->
          <div class="flex justify-end">
            <Button 
              variant="primary" 
              size="md"
              on:click={uploadDocument}
              disabled={!documentFile || !documentTitle || uploadingDocument}
              loading={uploadingDocument}
            >
              Upload Document
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
            <Button variant="outline" size="sm" on:click={loadDocuments}>
              Try Again
            </Button>
          </div>
        </Alert>
      </div>
    {:else if documents.length === 0}
      <div class="p-5 text-center py-8 text-text-medium">
        <p>No documents available {canEdit && !readOnly ? 'yet' : ''}</p>
        {#if canEdit && !readOnly && !showUploadForm}
          <Button 
            variant="outline" 
            size="sm"
            class="mt-2"
            on:click={() => showUploadForm = true}
          >
            Upload Document
          </Button>
        {/if}
      </div>
    {:else}
      <div class="p-5">
        <div class="grid grid-cols-1 gap-4">
          {#each documents as document}
            <div class="bg-white border border-primary-blue/10 rounded-lg hover:shadow-sm transition-shadow p-4">
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                <div class="flex items-start">
                  <div class="flex-shrink-0 h-10 w-10 rounded-lg bg-primary-blue/10 flex items-center justify-center text-secondary-blue">
                    {@html getDocumentIcon(document.document_type)}
                  </div>
                  <div class="ml-3">
                    <h4 class="text-sm font-medium text-text-dark">
                      {document.title}
                    </h4>
                    <p class="text-xs text-text-medium">
                      {getDocumentTypeLabel(document.document_type)} • {formatDate(document.created_at)}
                    </p>
                  </div>
                </div>
                
                <div class="flex mt-2 sm:mt-0">
                  <span class={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getVerificationBadge(document.verification_status).color}`}>
                    {getVerificationBadge(document.verification_status).label}
                  </span>
                  
                  <div class="ml-4 flex-shrink-0 flex">
                    <Button 
                      href={document.file} 
                      variant="outline" 
                      size="xs"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      View
                    </Button>
                    
                    {#if canEdit && !readOnly}
                      <Button 
                        variant="outline" 
                        size="xs"
                        class="ml-2 text-red-600 hover:bg-red-50 transition-colors duration-200"
                        on:click={() => deleteDocument(document.id)}
                      >
                        Delete
                      </Button>
                    {/if}
                  </div>
                </div>
              </div>
              
              {#if document.description}
                <div class="mt-3 text-sm text-text-medium">
                  {document.description}
                </div>
              {/if}
              
              {#if canVerify && document.verification_status === 'PENDING'}
                <div class="mt-3 pt-3 border-t border-primary-blue/10 flex justify-end space-x-2">
                  <Button 
                    variant="outline" 
                    size="xs"
                    class="text-green-600 hover:bg-green-50"
                    on:click={() => updateVerificationStatus(document, 'VERIFIED')}
                  >
                    Verify
                  </Button>
                  
                  <Button 
                    variant="outline" 
                    size="xs"
                    class="text-red-600 hover:bg-red-50"
                    on:click={() => updateVerificationStatus(document, 'REJECTED')}
                  >
                    Reject
                  </Button>
                </div>
              {/if}
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </div>