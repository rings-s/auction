<!-- src/lib/components/auth/ProfileForm.svelte -->
<script>
  import { t, language } from '$lib/i18n';
  import { createEventDispatcher } from 'svelte';
  import { currentUser } from '$lib/stores/auth';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import { api } from '$lib/services/api';
  
  const dispatch = createEventDispatcher();
  
  // Form data - initialize with current user data
  let firstName = $currentUser?.firstName || '';
  let lastName = $currentUser?.lastName || '';
  let phoneNumber = $currentUser?.phone_number || '';
  let bio = $currentUser?.bio || '';
  let address = $currentUser?.address || '';
  let city = $currentUser?.city || '';
  let country = $currentUser?.country || '';
  
  // Avatar
  let avatar = $currentUser?.avatar || null;
  let avatarPreview = avatar;
  let avatarFile = null;
  
  // Form state
  let loading = false;
  let error = null;
  let success = false;
  let formSubmitted = false;
  
  // Validation errors
  let errors = {
    firstName: null,
    lastName: null,
    phoneNumber: null
  };
  
  // Validate form
  function validate() {
    errors = {
      firstName: !firstName ? $t('auth.errors.name_required') : null,
      lastName: !lastName ? $t('auth.errors.name_required') : null,
      phoneNumber: !phoneNumber ? $t('auth.errors.phone_required') : null
    };
    
    return !Object.values(errors).some(error => error);
  }
  
  // Handle avatar change
  function handleAvatarChange(event) {
    const file = event.target.files[0];
    
    if (!file) return;
    
    // Check file size (max 2MB)
    if (file.size > 2 * 1024 * 1024) {
      error = $t('auth.errors.avatar_too_large');
      return;
    }
    
    // Check file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (!validTypes.includes(file.type)) {
      error = $t('auth.errors.avatar_invalid_type');
      return;
    }
    
    avatarFile = file;
    
    // Create preview URL
    const reader = new FileReader();
    reader.onload = (e) => {
      avatarPreview = e.target.result;
    };
    reader.readAsDataURL(file);
  }
  
  // Handle form submission
  async function handleSubmit() {
    formSubmitted = true;
    
    if (!validate()) {
      return;
    }
    
    loading = true;
    error = null;
    success = false;
    
    try {
      // Update user profile
      const userData = {
        first_name: firstName,
        last_name: lastName,
        phone_number: phoneNumber,
        bio,
        address,
        city,
        country
      };
      
      const response = await api.patch('accounts/profile/', userData);
      
      // Upload avatar if changed
      if (avatarFile) {
        const formData = new FormData();
        formData.append('avatar', avatarFile);
        
        await api.upload('accounts/profile/avatar/', avatarFile);
      }
      
      success = true;
      dispatch('success');
    } catch (e) {
      error = e.message || $t('system_messages.error_occurred');
    } finally {
      loading = false;
    }
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="space-y-4" novalidate>
  {#if error}
    <Alert type="error" dismissible={true}>{error}</Alert>
  {/if}
  
  {#if success}
    <Alert type="success" dismissible={true}>
      {$t('auth.profile_updated')}
    </Alert>
  {/if}
  
  <!-- Avatar -->
  <div class="flex justify-center mb-6">
    <div class="relative">
      <div class="h-24 w-24 rounded-full overflow-hidden bg-cosmos-bg-light">
        {#if avatarPreview}
          <img src={avatarPreview} alt={$t('auth.avatar')} class="h-full w-full object-cover" />
        {:else}
          <div class="flex h-full w-full items-center justify-center bg-primary-dark text-white text-3xl font-bold">
            {firstName ? firstName[0] : ''}
            {lastName ? lastName[0] : ''}
          </div>
        {/if}
      </div>
      
      <label
        for="avatar-upload"
        class="absolute bottom-0 right-0 bg-cosmos-bg border border-cosmos-bg-light rounded-full p-1.5 cursor-pointer hover:bg-cosmos-bg-light transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-cosmos-text" viewBox="0 0 20 20" fill="currentColor">
          <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
        </svg>
      </label>
      
      <input
        id="avatar-upload"
        type="file"
        accept="image/jpeg,image/png,image/gif"
        class="hidden"
        on:change={handleAvatarChange}
      />
    </div>
  </div>
  
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div>
      <Input
        type="text"
        name="firstName"
        bind:value={firstName}
        placeholder={$t('auth.first_name')}
        label={$t('auth.first_name')}
        error={formSubmitted && errors.firstName}
        required={true}
        dir={$language === 'ar' ? 'rtl' : 'ltr'}
      />
    </div>
    
    <div>
      <Input
        type="text"
        name="lastName"
        bind:value={lastName}
        placeholder={$t('auth.last_name')}
        label={$t('auth.last_name')}
        error={formSubmitted && errors.lastName}
        required={true}
        dir={$language === 'ar' ? 'rtl' : 'ltr'}
      />
    </div>
  </div>
  
  <div>
    <Input
      type="tel"
      name="phoneNumber"
      bind:value={phoneNumber}
      placeholder={$t('auth.phone_number')}
      label={$t('auth.phone_number')}
      error={formSubmitted && errors.phoneNumber}
      required={true}
      dir="ltr"
    />
  </div>
  
  <div>
    <label for="bio" class="block text-sm font-medium text-cosmos-text mb-1">
      {$t('auth.bio')}
    </label>
    <textarea
      id="bio"
      name="bio"
      bind:value={bio}
      rows="4"
      class="py-2 px-4 block w-full rounded-lg border transition-all
            bg-cosmos-bg text-cosmos-text
            border-cosmos-bg-light focus:border-primary
            focus:ring focus:ring-primary focus:ring-opacity-25
            placeholder-cosmos-text-muted"
      dir={$language === 'ar' ? 'rtl' : 'ltr'}
      placeholder={$t('auth.bio_placeholder')}
    ></textarea>
  </div>
  
  <div>
    <Input
      type="text"
      name="address"
      bind:value={address}
      placeholder={$t('auth.address')}
      label={$t('auth.address')}
      dir={$language === 'ar' ? 'rtl' : 'ltr'}
    />
  </div>
  
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div>
      <Input
        type="text"
        name="city"
        bind:value={city}
        placeholder={$t('auth.city')}
        label={$t('auth.city')}
        dir={$language === 'ar' ? 'rtl' : 'ltr'}
      />
    </div>
    
    <div>
      <Input
        type="text"
        name="country"
        bind:value={country}
        placeholder={$t('auth.country')}
        label={$t('auth.country')}
        dir={$language === 'ar' ? 'rtl' : 'ltr'}
      />
    </div>
  </div>
  
  <div>
    <Button
      type="submit"
      variant="primary"
      fullWidth={true}
      loading={loading}
      disabled={loading}
    >
      {$t('auth.update_profile')}
    </Button>
  </div>
</form>