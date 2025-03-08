<!-- src/routes/profile/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { browser } from '$app/environment';
  import { isAuthenticated, authStore } from '$lib/stores/authStore';
  import { profileStore } from '$lib/stores/profileStore';
  import { notificationStore } from '$lib/stores/notificationStore';
  import ProfileForm from '$lib/components/profile/ProfileForm.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  
  // Profile data with default values
  let profile = null;
  let loading = true;
  let error = null;
  let hasLoadedInitially = false;
  
  // Active tab
  let activeTab = 'profile'; // 'profile', 'security', 'preferences'
  
  // Password change form
  let currentPassword = '';
  let newPassword = '';
  let confirmPassword = '';
  let passwordLoading = false;
  let passwordError = '';
  let passwordSuccess = '';
  
  // File upload state
  let avatarFile = null;
  let isUploadingAvatar = false;
  
  onMount(async () => {
    if (!browser) return;
    
    // Check if user is authenticated
    if (!$isAuthenticated) {
      goto('/login?redirect=/profile');
      return;
    }
    
    loadProfileData();
  });
  
  // Improved profile loading with better error handling
  async function loadProfileData(isRetry = false) {
    try {
      if (!isRetry) {
        loading = true;
        error = null;
      }
      
      console.log('Loading profile data...');
      
      // Load profile data
      const profileData = await profileStore.getProfile();
      
      console.log('Profile data loaded:', profileData);
      
      // Ensure profile has all expected fields
      profile = {
        ...profileData,
        // Add default values for any missing fields
        first_name: profileData.first_name || '',
        last_name: profileData.last_name || '',
        email: profileData.email || '',
        phone_number: profileData.phone_number || '',
        date_of_birth: profileData.date_of_birth || '',
        bio: profileData.bio || '',
        company_name: profileData.company_name || '',
        company_registration: profileData.company_registration || '',
        tax_id: profileData.tax_id || '',
        address: profileData.address || '',
      };
      
      loading = false;
      hasLoadedInitially = true;
    } catch (err) {
      console.error('Failed to load profile:', err);
      
      if (!isRetry) {
        // If this is the first try, attempt one retry
        setTimeout(() => {
          loadProfileData(true);
        }, 1000);
      } else {
        // This was already a retry, show the error
        error = err.error || 'Failed to load profile data. Please try again.';
        notificationStore.error(error);
        loading = false;
        hasLoadedInitially = true;
        
        // Set default profile as fallback
        profile = {
          first_name: '',
          last_name: '',
          email: $authStore?.user?.email || '',
          phone_number: '',
          date_of_birth: '',
          bio: '',
          company_name: '',
          company_registration: '',
          tax_id: '',
          address: '',
          roles: []
        };
      }
    }
  }
  
  function setActiveTab(tab) {
    activeTab = tab;
    
    // Reset form states when switching tabs
    if (tab === 'security') {
      currentPassword = '';
      newPassword = '';
      confirmPassword = '';
      passwordError = '';
      passwordSuccess = '';
    }
  }
  
  // Improved password update handling
  async function handleChangePassword() {
    passwordError = '';
    passwordSuccess = '';
    
    // Validate inputs
    if (!currentPassword || !newPassword || !confirmPassword) {
      passwordError = 'All fields are required';
      return;
    }
    
    if (newPassword !== confirmPassword) {
      passwordError = 'Passwords do not match';
      return;
    }
    
    if (newPassword.length < 8) {
      passwordError = 'Password must be at least 8 characters long';
      return;
    }
    
    passwordLoading = true;
    
    try {
      await profileStore.updatePassword(currentPassword, newPassword, confirmPassword);
      
      passwordSuccess = 'Password changed successfully';
      notificationStore.success(passwordSuccess);
      
      // Reset form
      currentPassword = '';
      newPassword = '';
      confirmPassword = '';
      
    } catch (err) {
      console.error('Password change error:', err);
      
      if (err.status === 400) {
        if (err.code === 'invalid_password') {
          passwordError = 'Current password is incorrect';
        } else if (err.code === 'invalid_new_password') {
          passwordError = err.error || 'New password does not meet requirements';
        } else {
          passwordError = err.error || 'Password validation failed';
        }
      } else {
        passwordError = err.error || 'Failed to change password. Please try again.';
      }
      
      notificationStore.error(passwordError);
    } finally {
      passwordLoading = false;
    }
  }
  
  function handleProfileUpdate(event) {
    console.log('Profile updated event received:', event.detail);
    profile = event.detail;
  }
  
  function handleAvatarChange(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (!validTypes.includes(file.type)) {
      notificationStore.error('Please select a valid image file (JPEG, PNG, or GIF)');
      return;
    }
    
    // Validate file size (max 2MB)
    if (file.size > 2 * 1024 * 1024) {
      notificationStore.error('Image size should be less than 2MB');
      return;
    }
    
    avatarFile = file;
    uploadAvatar();
  }
  
  async function uploadAvatar() {
    if (!avatarFile) return;
    
    isUploadingAvatar = true;
    
    try {
      const formData = new FormData();
      formData.append('avatar', avatarFile);
      
      // Call API to upload avatar using the profileStore
      await profileStore.updateAvatar(formData);
      
      // Reload profile to get updated avatar URL
      await loadProfileData();
      
      notificationStore.success('Avatar updated successfully');
      
    } catch (err) {
      console.error('Avatar upload error:', err);
      notificationStore.error('Failed to upload avatar. Please try again.');
    } finally {
      isUploadingAvatar = false;
      avatarFile = null;
    }
  }

  // Format date helper
  function formatDate(date) {
    if (!date) return 'N/A';
    try {
      return new Date(date).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return 'N/A';
    }
  }
</script>

<div class="bg-slate-50 min-h-screen pb-12">
  <!-- Header banner -->
  <div class="bg-gradient-to-r from-blue-600 to-indigo-700 h-48">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-full flex items-end">
      <h1 class="text-3xl font-bold text-white pb-6">
        My Profile
      </h1>
    </div>
  </div>
  
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-12">
    <!-- Profile card -->
    <div class="mb-8 bg-white rounded-xl shadow-sm p-6 border border-slate-100 transition-all duration-200 hover:shadow">
      <div class="sm:flex sm:items-center sm:justify-between">
        <div class="sm:flex sm:space-x-5">
          <div class="flex-shrink-0 relative group">
            {#if profile}
              <img
                class="h-20 w-20 rounded-full border-4 border-white shadow-md object-cover"
                src={profile.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent((profile.first_name || '') + '+' + (profile.last_name || ''))}&background=6366F1&color=fff&size=200`}
                alt={`${profile.first_name} ${profile.last_name}`}
              />
            {:else}
              <div class="h-20 w-20 rounded-full border-4 border-white shadow-md bg-gray-200 animate-pulse"></div>
            {/if}
            
            <!-- Avatar upload overlay -->
            {#if !loading && !error}
              <label 
                class="absolute inset-0 flex items-center justify-center rounded-full bg-black bg-opacity-50 text-white opacity-0 group-hover:opacity-100 cursor-pointer transition-opacity duration-200"
                for="avatar-upload"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </label>
              
              <input 
                id="avatar-upload" 
                type="file" 
                accept="image/*" 
                class="hidden" 
                on:change={handleAvatarChange}
                disabled={isUploadingAvatar}
              />
            {/if}
            
            {#if isUploadingAvatar}
              <div class="absolute inset-0 flex items-center justify-center rounded-full bg-black bg-opacity-50">
                <div class="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              </div>
            {/if}
          </div>
          
          <div class="mt-4 sm:mt-0 sm:pt-1 text-center sm:text-left">
            <p class="text-xl font-bold text-slate-900 sm:text-2xl">
              {#if loading}
                <span class="inline-block w-32 h-6 bg-slate-200 animate-pulse rounded"></span>
              {:else if profile}
                {profile.first_name || ''} {profile.last_name || ''}
              {:else}
                <span class="text-gray-400">No profile data</span>
              {/if}
            </p>
            <p class="text-sm font-medium text-slate-600">
              {#if loading}
                <span class="inline-block w-40 h-4 bg-slate-200 animate-pulse rounded mt-2"></span>
              {:else if profile}
                {profile.email || ''}
              {/if}
            </p>
            
            <div class="mt-2 flex flex-wrap gap-2">
              {#if loading}
                <span class="inline-block w-16 h-5 bg-slate-200 animate-pulse rounded-full"></span>
                <span class="inline-block w-20 h-5 bg-slate-200 animate-pulse rounded-full"></span>
              {:else if profile?.roles && profile.roles.length > 0}
                {#each profile.roles as role}
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                    {role.name}
                  </span>
                {/each}
              {/if}
            </div>
          </div>
        </div>
        
        <div class="mt-5 flex justify-center sm:mt-0">
          {#if loading}
            <div class="w-32 h-10 bg-slate-200 animate-pulse rounded-md"></div>
          {:else}
            <label for="avatar-upload" class="inline-flex items-center justify-center px-4 py-2 border border-slate-300 rounded-md shadow-sm text-sm font-medium text-slate-700 bg-white hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 cursor-pointer transition-colors duration-200">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Change Avatar
            </label>
          {/if}
        </div>
      </div>
    </div>
    
    <!-- Tabs -->
    <div class="mb-8">
      <div class="border-b border-slate-200">
        <nav class="-mb-px flex space-x-8" aria-label="Tabs">
          <button
            class={`
              py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200
              ${activeTab === 'profile'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'}
            `}
            on:click={() => setActiveTab('profile')}
          >
            Profile
          </button>
          
          <button
            class={`
              py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200
              ${activeTab === 'security'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'}
            `}
            on:click={() => setActiveTab('security')}
          >
            Security
          </button>
          
          <button
            class={`
              py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200
              ${activeTab === 'preferences'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'}
            `}
            on:click={() => setActiveTab('preferences')}
          >
            Preferences
          </button>
        </nav>
      </div>
    </div>
    
    {#if loading && !hasLoadedInitially}
      <div class="text-center py-12">
        <Spinner size="lg" />
        <p class="mt-2 text-slate-600">Loading profile...</p>
      </div>
    {:else if error}
      <div class="py-6">
        <Alert variant="error">
          {error}
          <div class="mt-4 text-right">
            <Button 
              variant="outline" 
              size="sm" 
              on:click={() => loadProfileData()}
            >
              Retry
            </Button>
          </div>
        </Alert>
      </div>
    {:else}
      {#if activeTab === 'profile'}
        <!-- Debug info -->
        {#if false} <!-- Set to true when debugging -->
          <div class="bg-gray-100 p-4 mb-6 rounded text-xs overflow-auto max-h-40">
            <pre>{JSON.stringify(profile, null, 2)}</pre>
          </div>
        {/if}
        
        <!-- Only render the form if we have profile data -->
        {#if profile}
          <ProfileForm userData={profile} on:success={handleProfileUpdate} />
        {:else}
          <div class="text-center py-8">
            <p>No profile data available. Please try refreshing the page.</p>
            <Button variant="primary" class="mt-4" on:click={loadProfileData}>
              Refresh Profile
            </Button>
          </div>
        {/if}
      {:else if activeTab === 'security'}
        <div class="space-y-8">
          <!-- Password change -->
          <div class="bg-white shadow-sm rounded-lg p-6 border border-slate-100 transition-all duration-200 hover:shadow">
            <h3 class="text-lg font-medium text-slate-900 mb-6">Change Password</h3>
            
            {#if passwordError}
              <Alert variant="error" class="mb-4">{passwordError}</Alert>
            {/if}
            
            {#if passwordSuccess}
              <Alert variant="success" class="mb-4">{passwordSuccess}</Alert>
            {/if}
            
            <div class="space-y-6">
              <div>
                <label for="current-password" class="block text-sm font-medium text-slate-700 mb-1">
                  Current Password
                </label>
                <input
                  type="password"
                  id="current-password"
                  name="current_password"
                  bind:value={currentPassword}
                  class="block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  required
                />
              </div>
              
              <div>
                <label for="new-password" class="block text-sm font-medium text-slate-700 mb-1">
                  New Password
                </label>
                <input
                  type="password"
                  id="new-password"
                  name="new_password"
                  bind:value={newPassword}
                  class="block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  required
                />
                <p class="mt-1 text-xs text-slate-500">
                  Password must be at least 8 characters long
                </p>
              </div>
              
              <div>
                <label for="confirm-password" class="block text-sm font-medium text-slate-700 mb-1">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  id="confirm-password"
                  name="confirm_password"
                  bind:value={confirmPassword}
                  class="block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  required
                />
              </div>
              
              <div>
                <Button
                  type="button"
                  variant="primary"
                  on:click={handleChangePassword}
                  disabled={passwordLoading}
                  loading={passwordLoading}
                >
                  Update Password
                </Button>
              </div>
            </div>
          </div>
          
          <!-- Two-factor authentication -->
          <div class="bg-white shadow-sm rounded-lg p-6 border border-slate-100 transition-all duration-200 hover:shadow">
            <h3 class="text-lg font-medium text-slate-900 mb-6">Two-Factor Authentication</h3>
            <p class="text-slate-600 mb-4">
              Add an extra layer of security to your account by enabling two-factor authentication.
            </p>
            
            <Button variant="outline">
              Enable Two-Factor Authentication
            </Button>
          </div>
          
          <!-- Sessions -->
          <div class="bg-white shadow-sm rounded-lg p-6 border border-slate-100 transition-all duration-200 hover:shadow">
            <h3 class="text-lg font-medium text-slate-900 mb-6">Sessions</h3>
            <p class="text-slate-600 mb-4">
              Manage your active sessions and sign out from other devices.
            </p>
            
            <div class="border-t border-slate-200 mt-4 pt-4">
              <div class="flex items-center justify-between py-3">
                <div class="flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-slate-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 2a4 4 0 00-4 4v1H5a1 1 0 00-.994.89l-1 9A1 1 0 004 18h12a1 1 0 00.994-1.11l-1-9A1 1 0 0015 7h-1V6a4 4 0 00-4-4zm2 5V6a2 2 0 10-4 0v1h4zm-6 3a1 1 0 112 0 1 1 0 01-2 0zm7-1a1 1 0 100 2 1 1 0 000-2z" clip-rule="evenodd" />
                  </svg>
                  <div class="ml-3">
                    <p class="text-sm font-medium text-slate-900">Current Session</p>
                    <p class="text-xs text-slate-500">Started {formatDate(new Date())}</p>
                  </div>
                </div>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Active
                </span>
              </div>
            </div>
            
            <div class="mt-4">
              <Button variant="outline" class="text-red-600 border-red-600 hover:bg-red-50 transition-colors duration-200">
                <span class="flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  Sign Out From All Devices
                </span>
              </Button>
            </div>
          </div>
        </div>
      {:else if activeTab === 'preferences'}
        <div class="space-y-8">
          <!-- Notification preferences -->
          <div class="bg-white shadow-sm rounded-lg p-6 border border-slate-100 transition-all duration-200 hover:shadow">
            <h3 class="text-lg font-medium text-slate-900 mb-6">Notification Preferences</h3>
            
            <div class="space-y-5">
              <div class="flex items-start">
                <div class="flex-shrink-0 mt-0.5">
                  <input
                    id="email-notifications"
                    name="email-notifications"
                    type="checkbox"
                    class="h-4 w-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500"
                    checked
                  />
                </div>
                <div class="ml-3 text-sm">
                  <label for="email-notifications" class="font-medium text-slate-700">Email Notifications</label>
                  <p class="text-slate-500">Receive email notifications for auction updates, bids, and messages.</p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 mt-0.5">
                  <input
                    id="browser-notifications"
                    name="browser-notifications"
                    type="checkbox"
                    class="h-4 w-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500"
                    checked
                  />
                </div>
                <div class="ml-3 text-sm">
                  <label for="browser-notifications" class="font-medium text-slate-700">Browser Notifications</label>
                  <p class="text-slate-500">Receive browser notifications when you're outbid or when an auction ends.</p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 mt-0.5">
                  <input
                    id="newsletter"
                    name="newsletter"
                    type="checkbox"
                    class="h-4 w-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500"
                  />
                </div>
                <div class="ml-3 text-sm">
                  <label for="newsletter" class="font-medium text-slate-700">Newsletter</label>
                  <p class="text-slate-500">Receive our monthly newsletter with platform updates and featured auctions.</p>
                </div>
              </div>
            </div>
            
            <div class="mt-6">
              <Button variant="primary">
                Save Preferences
              </Button>
            </div>
          </div>
          
          <!-- Language and region -->
          <div class="bg-white shadow-sm rounded-lg p-6 border border-slate-100 transition-all duration-200 hover:shadow">
            <h3 class="text-lg font-medium text-slate-900 mb-6">Language and Region</h3>
            
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label for="language" class="block text-sm font-medium text-slate-700 mb-1">
                  Language
                </label>
                <select
                  id="language"
                  name="language"
                  class="block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="en">English</option>
                  <option value="ar">Arabic</option>
    
                </select>
              </div>
              
              <div>
                <label for="timezone" class="block text-sm font-medium text-slate-700 mb-1">
                  Timezone
                </label>
                <select
                  id="timezone"
                  name="timezone"
                  class="block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                  <option value="UTC">UTC</option>
                  <option value="America/New_York">Eastern Time (ET)</option>
                  <option value="America/Chicago">Central Time (CT)</option>
                  <option value="America/Denver">Mountain Time (MT)</option>
                  <option value="America/Los_Angeles">Pacific Time (PT)</option>
                </select>
              </div>
              
              <div>
                <label for="currency" class="block text-sm font-medium text-slate-700 mb-1">
                  Preferred Currency
                </label>
                <select
                  id="currency"
                  name="currency"
                  class="block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="SAR">Saudi RIYAL   (SAR)</option>
                  <option value="EUR">Euro (EUR)</option>
                  <option value="GBP">British Pound (GBP)</option>
                  <option value="USD">US Dollar (USD)</option>

                </select>
              </div>
            </div>
            
            <div class="mt-6">
              <Button variant="primary">
                Save Preferences
              </Button>
            </div>
          </div>
        </div>
      {/if}
    {/if}
  </div>
</div>

<style>
  /* Custom button styles */
  :global(.btn-outline-red) {
    @apply text-red-600 border-red-300 hover:bg-red-50;
  }

  /* Animation for skeleton loading */
  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }

  .animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }

  /* Animation for loading spinner */
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .animate-spin {
    animation: spin 1s linear infinite;
  }
</style>