<!-- src/lib/components/profile/ProfileForm.svelte -->
<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { profileStore } from '$lib/stores/profileStore';
  import { notificationStore } from '$lib/stores/notificationStore';
  import Input from '$lib/components/ui/Input.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  
  const dispatch = createEventDispatcher();

  // Profile data with defaults (ensures the form always has valid data)
  export let userData = {
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    date_of_birth: '',
    bio: '',
    company_name: '',
    company_registration: '',
    tax_id: '',
    address: '',
  };
  
  // Form state
  let loading = false;
  let error = '';
  let success = '';
  let fieldErrors = {};
  
  // Make a deep copy of userData for form binding to avoid reference issues
  let formData = {};
  
  // When userData changes, update formData
  $: if (userData) {
    console.log('Updating formData with new userData:', userData);
    
    // Create a clean copy with all expected fields, using defaults for missing ones
    formData = {
      first_name: userData.first_name || '',
      last_name: userData.last_name || '',
      email: userData.email || '',
      phone_number: userData.phone_number || '',
      date_of_birth: userData.date_of_birth || '',
      bio: userData.bio || '',
      company_name: userData.company_name || '',
      company_registration: userData.company_registration || '',
      tax_id: userData.tax_id || '',
      address: userData.address || '',
    };
  }
  
  // Format date for API submission
  function formatDateForSubmission(dateString) {
    if (!dateString) return '';
    
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return dateString;
      
      return date.toISOString().split('T')[0]; // YYYY-MM-DD format
    } catch (e) {
      console.error('Date formatting error:', e);
      return dateString;
    }
  }
  
  // Handle form submission
  async function handleSubmit() {
    loading = true;
    error = '';
    success = '';
    fieldErrors = {};
    
    // Create a copy of formData for submission
    const submissionData = { ...formData };
    
    // Format date if present
    if (submissionData.date_of_birth) {
      submissionData.date_of_birth = formatDateForSubmission(submissionData.date_of_birth);
    }
    
    console.log('Submitting form with data:', submissionData);
    
    try {
      const updatedProfile = await profileStore.updateProfile(submissionData);
      
      success = 'Profile updated successfully';
      notificationStore.success(success);
      
      console.log('Profile updated successfully:', updatedProfile);
      
      // Emit success event with updated profile
      dispatch('success', updatedProfile);
      
    } catch (err) {
      console.error('Profile update error:', err);
      
      if (err.status === 400 && err.error) {
        // Handle field-specific validation errors
        if (typeof err.error === 'object') {
          fieldErrors = err.error;
          error = Object.values(err.error).join('. ');
        } else {
          error = err.error;
        }
      } else {
        // Handle general error
        error = err.error || 'Profile update failed. Please try again.';
      }
      
      notificationStore.error(error);
      
    } finally {
      loading = false;
    }
  }
  
  // Get field-specific error message
  function getFieldError(fieldName) {
    return fieldErrors[fieldName] || '';
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="space-y-8">
  {#if error}
    <Alert variant="error">{error}</Alert>
  {/if}
  
  {#if success}
    <Alert variant="success">{success}</Alert>
  {/if}
  
  <div class="bg-white shadow-sm rounded-lg p-6 border border-slate-100">
    <h3 class="text-lg font-medium text-slate-900 mb-6">Personal Information</h3>
    
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
      <Input
        type="text"
        id="first_name"
        name="first_name"
        label="First Name"
        bind:value={formData.first_name}
        required
        error={getFieldError('first_name')}
      />
      
      <Input
        type="text"
        id="last_name"
        name="last_name"
        label="Last Name"
        bind:value={formData.last_name}
        required
        error={getFieldError('last_name')}
      />
      
      <Input
        type="email"
        id="email"
        name="email"
        label="Email Address"
        value={formData.email}
        disabled={true}
        helper="Email address cannot be changed"
      />
      
      <Input
        type="tel"
        id="phone_number"
        name="phone_number"
        label="Phone Number"
        bind:value={formData.phone_number}
        placeholder="+1 (555) 123-4567"
        error={getFieldError('phone_number')}
      />
      
      <Input
        type="date"
        id="date_of_birth"
        name="date_of_birth"
        label="Date of Birth"
        bind:value={formData.date_of_birth}
        error={getFieldError('date_of_birth')}
      />
    </div>
  </div>
  
  <div class="bg-white shadow-sm rounded-lg p-6 border border-slate-100">
    <h3 class="text-lg font-medium text-slate-900 mb-6">Company Information</h3>
    
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
      <Input
        type="text"
        id="company_name"
        name="company_name"
        label="Company Name"
        bind:value={formData.company_name}
        error={getFieldError('company_name')}
      />
      
      <Input
        type="text"
        id="company_registration"
        name="company_registration"
        label="Company Registration"
        bind:value={formData.company_registration}
        error={getFieldError('company_registration')}
      />
      
      <Input
        type="text"
        id="tax_id"
        name="tax_id"
        label="Tax ID"
        bind:value={formData.tax_id}
        error={getFieldError('tax_id')}
      />
    </div>
    
    <div class="mt-6">
      <label for="address" class="block text-sm font-medium text-slate-700 mb-1">
        Address
      </label>
      <textarea
        id="address"
        name="address"
        rows="3"
        class="block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
        bind:value={formData.address}
      ></textarea>
      {#if getFieldError('address')}
        <p class="mt-1 text-sm text-red-600">{getFieldError('address')}</p>
      {/if}
    </div>
  </div>
  
  <div class="bg-white shadow-sm rounded-lg p-6 border border-slate-100">
    <h3 class="text-lg font-medium text-slate-900 mb-6">About</h3>
    
    <div>
      <label for="bio" class="block text-sm font-medium text-slate-700 mb-1">
        Bio
      </label>
      <textarea
        id="bio"
        name="bio"
        rows="4"
        class="block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
        bind:value={formData.bio}
        placeholder="Tell us about yourself or your business..."
      ></textarea>
      {#if getFieldError('bio')}
        <p class="mt-1 text-sm text-red-600">{getFieldError('bio')}</p>
      {/if}
    </div>
  </div>
  
  <div class="flex justify-end">
    <Button
      type="submit"
      variant="primary"
      size="lg"
      disabled={loading}
      loading={loading}
    >
      Save Changes
    </Button>
  </div>
</form>