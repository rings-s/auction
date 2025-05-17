<!-- src/routes/profile/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { fetchUserProfile, updateUserProfile, changePassword, logout } from '$lib/api/auth';
    import { t } from '$lib/i18n/i18n';
    import { user } from '$lib/stores/user';
  
    let loading = true;
    let savingProfile = false;
    let changingPassword = false;
    let activeTab = 'profile';
    let error = '';
    let success = '';
  
    // Form data
    let profileData = {
      first_name: '',
      last_name: '',
      phone_number: '',
      date_of_birth: '',
      bio: '',
      company_name: '',
      company_registration: '',
      tax_id: '',
      address: '',
      city: '',
      state: '',
      postal_code: '',
      country: '',
      license_number: '',
      license_expiry: '',
      preferred_locations: '',
      property_preferences: ''
    };
  
    let passwordData = {
      current_password: '',
      new_password: '',
      confirm_password: ''
    };
  
    onMount(async () => {
      try {
        // Check if user is logged in
        if (!$user) {
          const userData = await fetchUserProfile();
          if (!userData) {
            goto('/login');
            return;
          }
        }
  
        // Populate form with user data
        if ($user) {
          Object.keys(profileData).forEach(key => {
            if ($user[key] !== undefined) {
              profileData[key] = $user[key];
            }
          });
        }
      } catch (err) {
        console.error('Error loading profile:', err);
        error = err.message || $t('error.profileLoadFailed');
        goto('/login');
      } finally {
        loading = false;
      }
    });
  
    async function handleUpdateProfile() {
      try {
        savingProfile = true;
        error = '';
        success = '';
        
        const updatedUser = await updateUserProfile(profileData);
        success = $t('profile.updateSuccess');
      } catch (err) {
        console.error('Error updating profile:', err);
        error = err.message || $t('error.profileUpdateFailed');
      } finally {
        savingProfile = false;
      }
    }
  
    async function handleChangePassword() {
      try {
        changingPassword = true;
        error = '';
        success = '';
        
        // Validate passwords
        if (passwordData.new_password !== passwordData.confirm_password) {
          throw new Error($t('error.passwordMismatch'));
        }
        
        await changePassword(
          passwordData.current_password,
          passwordData.new_password,
          passwordData.confirm_password
        );
        
        success = $t('profile.passwordChangeSuccess');
        
        // Clear form
        passwordData = {
          current_password: '',
          new_password: '',
          confirm_password: ''
        };
      } catch (err) {
        console.error('Error changing password:', err);
        error = err.message || $t('error.passwordChangeFailed');
      } finally {
        changingPassword = false;
      }
    }
  
    function handleLogout() {
      logout();
      goto('/login');
    }
  
    function setActiveTab(tab) {
      activeTab = tab;
      error = '';
      success = '';
    }
  </script>
  
  <svelte:head>
    <title>{$t('profile.myProfile')} | Real Estate Platform</title>
  </svelte:head>
  
  <div class="bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {#if loading}
        <div class="flex justify-center py-24">
          <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      {:else if $user}
        <div class="md:flex md:items-center md:justify-between mb-8">
          <div class="flex-1 min-w-0">
            <h1 class="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl sm:truncate">
              {$t('profile.myProfile')}
            </h1>
          </div>
          <div class="mt-4 flex md:mt-0 md:ml-4">
            <button
              type="button"
              on:click={handleLogout}
              class="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              {$t('auth.logOut')}
            </button>
          </div>
        </div>
  
        <!-- Profile info -->
        <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg mb-8">
          <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
            <div>
              <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                {$t('profile.personalInfo')}
              </h3>
              <p class="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
                {$t('profile.personalDetails')}
              </p>
            </div>
            <div class="flex items-center space-x-2">
              {#if $user.avatar_url}
                <img class="h-16 w-16 rounded-full" src={$user.avatar_url} alt={$user.first_name} />
              {:else}
                <div class="h-16 w-16 rounded-full bg-primary-500 flex items-center justify-center text-white text-xl font-medium">
                  {($user.first_name?.[0] || '') + ($user.last_name?.[0] || '')}
                </div>
              {/if}
            </div>
          </div>
          <div class="border-t border-gray-200 dark:border-gray-700">
            <dl>
              <div class="bg-gray-50 dark:bg-gray-900/30 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {$t('auth.fullName')}
                </dt>
                <dd class="mt-1 text-sm text-gray-900 dark:text-white sm:mt-0 sm:col-span-2">
                  {$user.first_name} {$user.last_name}
                </dd>
              </div>
              <div class="bg-white dark:bg-gray-800 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {$t('auth.email')}
                </dt>
                <dd class="mt-1 text-sm text-gray-900 dark:text-white sm:mt-0 sm:col-span-2">
                  {$user.email}
                </dd>
              </div>
              <div class="bg-gray-50 dark:bg-gray-900/30 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {$t('auth.phoneNumber')}
                </dt>
                <dd class="mt-1 text-sm text-gray-900 dark:text-white sm:mt-0 sm:col-span-2">
                  {$user.phone_number || $t('profile.notProvided')}
                </dd>
              </div>
              <div class="bg-white dark:bg-gray-800 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {$t('profile.memberSince')}
                </dt>
                <dd class="mt-1 text-sm text-gray-900 dark:text-white sm:mt-0 sm:col-span-2">
                  {new Date($user.date_joined).toLocaleDateString()}
                </dd>
              </div>
            </dl>
          </div>
        </div>
  
        <!-- Tabs -->
        <div class="mb-6">
          <div class="sm:hidden">
            <label for="tabs" class="sr-only">Select a tab</label>
            <select
              id="tabs"
              name="tabs"
              bind:value={activeTab}
              on:change={e => setActiveTab(e.target.value)}
              class="block w-full rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white focus:border-primary-500 focus:ring-primary-500"
            >
              <option value="profile">{$t('profile.editProfile')}</option>
              <option value="password">{$t('profile.changePassword')}</option>
            </select>
          </div>
          <div class="hidden sm:block">
            <div class="border-b border-gray-200 dark:border-gray-700">
              <nav class="-mb-px flex space-x-8" aria-label="Tabs">
                <button
                  on:click={() => setActiveTab('profile')}
                  class={`${
                    activeTab === 'profile'
                      ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                      : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                >
                  {$t('profile.editProfile')}
                </button>
                <button
                  on:click={() => setActiveTab('password')}
                  class={`${
                    activeTab === 'password'
                      ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                      : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                >
                  {$t('profile.changePassword')}
                </button>
              </nav>
            </div>
          </div>
        </div>
  
        {#if error}
          <div class="rounded-md bg-red-50 dark:bg-red-900/30 p-4 mb-6">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800 dark:text-red-200">
                  {error}
                </h3>
              </div>
            </div>
          </div>
        {/if}
  
        {#if success}
          <div class="rounded-md bg-green-50 dark:bg-green-900/30 p-4 mb-6">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-green-800 dark:text-green-200">
                  {success}
                </h3>
              </div>
            </div>
          </div>
        {/if}
  
        {#if activeTab === 'profile'}
          <!-- Edit Profile Form -->
          <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <form on:submit|preventDefault={handleUpdateProfile}>
                <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                  <!-- Personal Information -->
                  <div class="sm:col-span-6">
                    <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">{$t('profile.personalInfo')}</h3>
                    <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{$t('profile.personalInfoDesc')}</p>
                  </div>
  
                  <!-- First name and Last name -->
                  <div class="sm:col-span-3">
                    <label for="first_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('auth.firstName')}
                    </label>
                    <input
                      type="text"
                      id="first_name"
                      bind:value={profileData.first_name}
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    />
                  </div>
  
                  <div class="sm:col-span-3">
                    <label for="last_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('auth.lastName')}
                    </label>
                    <input
                      type="text"
                      id="last_name"
                      bind:value={profileData.last_name}
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    />
                  </div>
  
                  <!-- Phone number and Date of birth -->
                  <div class="sm:col-span-3">
                    <label for="phone_number" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('auth.phoneNumber')}
                    </label>
                    <input
                      type="tel"
                      id="phone_number"
                      bind:value={profileData.phone_number}
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    />
                  </div>
  
                  <div class="sm:col-span-3">
                    <label for="date_of_birth" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('auth.dateOfBirth')}
                    </label>
                    <input
                      type="date"
                      id="date_of_birth"
                      bind:value={profileData.date_of_birth}
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    />
                  </div>
  
                  <!-- Bio -->
                  <div class="sm:col-span-6">
                    <label for="bio" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('profile.bio')}
                    </label>
                    <textarea
                      id="bio"
                      bind:value={profileData.bio}
                      rows="3"
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    ></textarea>
                  </div>
  
                  <!-- Company Information -->
                  <div class="sm:col-span-6 border-t border-gray-200 dark:border-gray-700 pt-5">
                    <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">{$t('profile.companyInfo')}</h3>
                    <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{$t('profile.companyInfoDesc')}</p>
                  </div>
  
                  <!-- Company name and Registration -->
                  <div class="sm:col-span-3">
                    <label for="company_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('profile.companyName')}
                    </label>
                    <input
                      type="text"
                      id="company_name"
                      bind:value={profileData.company_name}
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    />
                  </div>
  
                  <div class="sm:col-span-3">
                    <label for="company_registration" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('profile.companyRegistration')}
                    </label>
                    <input
                      type="text"
                      id="company_registration"
                      bind:value={profileData.company_registration}
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    />
                  </div>
  
                  <!-- Tax ID -->
                  <div class="sm:col-span-3">
                    <label for="tax_id" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('profile.taxId')}
                    </label>
                    <input
                      type="text"
                      id="tax_id"
                      bind:value={profileData.tax_id}
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    />
                  </div>
  
                  <!-- License number and expiry -->
                  <div class="sm:col-span-3">
                    <label for="license_number" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('profile.licenseNumber')}
                    </label>
                    <input
                      type="text"
                      id="license_number"
                      bind:value={profileData.license_number}
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    />
                  </div>
  
                  <div class="sm:col-span-3">
                    <label for="license_expiry" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('profile.licenseExpiry')}
                    </label>
                    <input
                      type="date"
                      id="license_expiry"
                      bind:value={profileData.license_expiry}
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    />
                  </div>
  
                  <!-- Address Information -->
                  <div class="sm:col-span-6 border-t border-gray-200 dark:border-gray-700 pt-5">
                    <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">{$t('profile.addressInfo')}</h3>
                    <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{$t('profile.addressInfoDesc')}</p>
                  </div>
  
                  <!-- Address -->
                  <div class="sm:col-span-6">
                    <label for="address" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('profile.address')}
                    </label>
                    <input
                      type="text"
                      id="address"
                      bind:value={profileData.address}
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    />
                  </div>
  
                  <!-- City and State -->
                  <div class="sm:col-span-3">
                    <label for="city" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('profile.city')}
                    </label>
                    <input
                      type="text"
                      id="city"
                      bind:value={profileData.city}
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    />
                  </div>
  
                  <div class="sm:col-span-3">
                    <label for="state" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('profile.state')}
                    </label>
                    <input
                      type="text"
                      id="state"
                      bind:value={profileData.state}
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    />
                  </div>
  
                  <!-- Postal code and Country -->
                  <div class="sm:col-span-3">
                    <label for="postal_code" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('profile.postalCode')}
                    </label>
                    <input
                      type="text"
                      id="postal_code"
                      bind:value={profileData.postal_code}
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    />
                  </div>
  
                  <div class="sm:col-span-3">
                    <label for="country" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('profile.country')}
                    </label>
                    <input
                      type="text"
                      id="country"
                      bind:value={profileData.country}
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    />
                  </div>
  
                  <!-- Preferences -->
                  <div class="sm:col-span-6 border-t border-gray-200 dark:border-gray-700 pt-5">
                    <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">{$t('profile.preferenceInfo')}</h3>
                    <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{$t('profile.preferenceInfoDesc')}</p>
                  </div>
  
                  <!-- Preferred locations -->
                  <div class="sm:col-span-6">
                    <label for="preferred_locations" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('profile.preferredLocations')} 
                      <span class="font-normal text-gray-500 dark:text-gray-400">({$t('profile.commaSeparated')})</span>
                    </label>
                    <input
                      type="text"
                      id="preferred_locations"
                      bind:value={profileData.preferred_locations}
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    />
                  </div>
  
                  <!-- Property preferences -->
                  <div class="sm:col-span-6">
                    <label for="property_preferences" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('profile.propertyPreferences')}
                      <span class="font-normal text-gray-500 dark:text-gray-400">({$t('profile.commaSeparated')})</span>
                    </label>
                    <input
                      type="text"
                      id="property_preferences"
                      bind:value={profileData.property_preferences}
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    />
                  </div>
                </div>
  
                <div class="pt-5">
                  <div class="flex justify-end">
                    <button
                      type="button"
                      on:click={() => goto('/')}
                      class="bg-white dark:bg-gray-800 py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      {$t('auth.cancel')}
                    </button>
                    <button
                      type="submit"
                      disabled={savingProfile}
                      class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {#if savingProfile}
                        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                      {/if}
                      {$t('auth.update')}
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        {:else if activeTab === 'password'}
          <!-- Change Password Form -->
          <div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <form on:submit|preventDefault={handleChangePassword}>
                <div class="space-y-6">
                  <div>
                    <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">{$t('profile.changePassword')}</h3>
                    <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{$t('profile.changePasswordDesc')}</p>
                  </div>
  
                  <div>
                    <label for="current_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('profile.currentPassword')}
                    </label>
                    <input
                      type="password"
                      id="current_password"
                      bind:value={passwordData.current_password}
                      required
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    />
                  </div>
  
                  <div>
                    <label for="new_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('profile.newPassword')}
                    </label>
                    <input
                      type="password"
                      id="new_password"
                      bind:value={passwordData.new_password}
                      required
                      minlength="8"
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    />
                  </div>
  
                  <div>
                    <label for="confirm_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {$t('profile.confirmNewPassword')}
                    </label>
                    <input
                      type="password"
                      id="confirm_password"
                      bind:value={passwordData.confirm_password}
                      required
                      minlength="8"
                      class="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 dark:border-gray-700 rounded-md dark:bg-gray-800 dark:text-white"
                    />
                  </div>
  
                  <div class="flex justify-end">
                    <button
                      type="button"
                      on:click={() => setActiveTab('profile')}
                      class="bg-white dark:bg-gray-800 py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      {$t('auth.cancel')}
                    </button>
                    <button
                      type="submit"
                      disabled={changingPassword}
                      class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {#if changingPassword}
                        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                      {/if}
                      {$t('profile.changePassword')}
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        {/if}
      {/if}
    </div>
  </div>