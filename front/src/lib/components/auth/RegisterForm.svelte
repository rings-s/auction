<script>
    import { createEventDispatcher } from 'svelte';
    import { t } from '$lib/i18n/i18n';
    import { fly } from 'svelte/transition';
    import { toast } from '$lib/stores/toastStore';
    
    export let loading = false;
    
    const dispatch = createEventDispatcher();
    
    let formData = {
      email: '',
      password: '',
      confirm_password: '',
      first_name: '',
      last_name: '',
      phone_number: '',
      date_of_birth: '',
      role: 'user'
    };
    
    let showPassword = false;
    let showConfirmPassword = false;
    let errors = {};
    let touched = {};
    
    // Password strength calculation
    $: passwordStrength = calculatePasswordStrength(formData.password);
    
    function calculatePasswordStrength(pwd) {
      if (!pwd) return 0;
      let score = 0;
      if (pwd.length >= 8) score += 25;
      if (pwd.length >= 12) score += 25;
      if (/[a-z]/.test(pwd)) score += 12.5;
      if (/[A-Z]/.test(pwd)) score += 12.5;
      if (/[0-9]/.test(pwd)) score += 12.5;
      if (/[^A-Za-z0-9]/.test(pwd)) score += 12.5;
      return Math.min(100, score);
    }
    
    $: strengthColor = 
      passwordStrength === 0 ? 'bg-gray-200 dark:bg-gray-700' :
      passwordStrength < 30 ? 'bg-red-500' :
      passwordStrength < 60 ? 'bg-yellow-500' :
      passwordStrength < 80 ? 'bg-blue-500' : 'bg-green-500';
    
    $: strengthLabel = 
      passwordStrength === 0 ? '' :
      passwordStrength < 30 ? $t('auth.passwordStrength.weak') :
      passwordStrength < 60 ? $t('auth.passwordStrength.fair') :
      passwordStrength < 80 ? $t('auth.passwordStrength.good') : $t('auth.passwordStrength.strong');
    
    // Validation
    function validateField(field, value) {
      switch (field) {
        case 'email':
          if (!value) return $t('auth.validation.emailRequired');
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (!emailRegex.test(value)) return $t('auth.validation.emailInvalid');
          return '';
        
        case 'password':
          if (!value) return $t('auth.validation.passwordRequired');
          if (value.length < 8) return $t('auth.validation.passwordMinLength');
          return '';
        
        case 'confirm_password':
          if (!value) return $t('auth.validation.passwordRequired');
          if (value !== formData.password) return $t('auth.validation.passwordMismatch');
          return '';
        
        case 'first_name':
          if (!value) return $t('auth.validation.firstNameRequired');
          return '';
        
        case 'last_name':
          if (!value) return $t('auth.validation.lastNameRequired');
          return '';
        
        default:
          return '';
      }
    }
    
    function handleBlur(field) {
      touched[field] = true;
      errors[field] = validateField(field, formData[field]);
    }
    
    function handleInput(field) {
      if (touched[field]) {
        errors[field] = validateField(field, formData[field]);
      }
      // Re-validate confirm password if password changes
      if (field === 'password' && touched.confirm_password) {
        errors.confirm_password = validateField('confirm_password', formData.confirm_password);
      }
    }
    
    async function handleSubmit() {
      // Mark all fields as touched
      Object.keys(formData).forEach(field => {
        touched[field] = true;
        errors[field] = validateField(field, formData[field]);
      });
      
      // Check if form is valid
      const hasErrors = Object.values(errors).some(error => error);
      if (hasErrors) {
        toast.error($t('error.validationFailed'));
        return;
      }
      
      dispatch('submit', formData);
    }
  </script>
  
  <form on:submit|preventDefault={handleSubmit} class="space-y-5">
    <!-- Name Fields -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div class="space-y-1">
        <label for="first_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('auth.firstName')} <span class="text-red-500">*</span>
        </label>
        <input
          id="first_name"
          type="text"
          bind:value={formData.first_name}
          on:blur={() => handleBlur('first_name')}
          on:input={() => handleInput('first_name')}
          required
          class="
            appearance-none block w-full px-3 py-2.5
            border {errors.first_name && touched.first_name ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'}
            rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-500
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
            text-gray-900 dark:text-white bg-white dark:bg-gray-800
            transition-all duration-200
          "
        />
        {#if errors.first_name && touched.first_name}
          <p class="text-sm text-red-600 dark:text-red-400" in:fly={{ y: -5, duration: 200 }}>
            {errors.first_name}
          </p>
        {/if}
      </div>
  
      <div class="space-y-1">
        <label for="last_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('auth.lastName')} <span class="text-red-500">*</span>
        </label>
        <input
          id="last_name"
          type="text"
          bind:value={formData.last_name}
          on:blur={() => handleBlur('last_name')}
          on:input={() => handleInput('last_name')}
          required
          class="
            appearance-none block w-full px-3 py-2.5
            border {errors.last_name && touched.last_name ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'}
            rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-500
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
            text-gray-900 dark:text-white bg-white dark:bg-gray-800
            transition-all duration-200
          "
        />
        {#if errors.last_name && touched.last_name}
          <p class="text-sm text-red-600 dark:text-red-400" in:fly={{ y: -5, duration: 200 }}>
            {errors.last_name}
          </p>
        {/if}
      </div>
    </div>
  
    <!-- Email -->
    <div class="space-y-1">
      <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {$t('auth.email')} <span class="text-red-500">*</span>
      </label>
      <div class="relative">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <input
          id="email"
          type="email"
          bind:value={formData.email}
          on:blur={() => handleBlur('email')}
          on:input={() => handleInput('email')}
          required
          class="
            appearance-none block w-full pl-10 pr-3 py-2.5
            border {errors.email && touched.email ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'}
            rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-500
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
            text-gray-900 dark:text-white bg-white dark:bg-gray-800
            transition-all duration-200
          "
        />
      </div>
      {#if errors.email && touched.email}
        <p class="text-sm text-red-600 dark:text-red-400" in:fly={{ y: -5, duration: 200 }}>
          {errors.email}
        </p>
      {/if}
    </div>
  
    <!-- Phone and Date of Birth -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div class="space-y-1">
        <label for="phone_number" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('auth.phoneNumber')}
        </label>
        <input
          id="phone_number"
          type="tel"
          bind:value={formData.phone_number}
          class="
            appearance-none block w-full px-3 py-2.5
            border border-gray-300 dark:border-gray-600
            rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-500
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
            text-gray-900 dark:text-white bg-white dark:bg-gray-800
            transition-all duration-200
          "
        />
      </div>
  
      <div class="space-y-1">
        <label for="date_of_birth" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          {$t('auth.dateOfBirth')}
        </label>
        <input
          id="date_of_birth"
          type="date"
          bind:value={formData.date_of_birth}
          class="
            appearance-none block w-full px-3 py-2.5
            border border-gray-300 dark:border-gray-600
            rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-500
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
            text-gray-900 dark:text-white bg-white dark:bg-gray-800
            transition-all duration-200
          "
        />
      </div>
    </div>
  
    <!-- User Role -->
    <div class="space-y-1">
      <label for="role" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {$t('auth.userRole')}
      </label>
      <select
        id="role"
        bind:value={formData.role}
        class="
          appearance-none block w-full px-3 py-2.5
          border border-gray-300 dark:border-gray-600
          rounded-lg shadow-sm
          focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
          text-gray-900 dark:text-white bg-white dark:bg-gray-800
          transition-all duration-200
        "
      >
        <option value="user">{$t('auth.roleUser')}</option>
        <option value="owner">{$t('auth.roleOwner')}</option>
        <option value="appraiser">{$t('auth.roleAppraiser')}</option>
        <option value="data_entry">{$t('auth.roleDataEntry')}</option>
      </select>
      <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
        {$t('auth.roleHelp')}
      </p>
    </div>
  
    <!-- Password -->
    <div class="space-y-1">
      <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {$t('auth.password')} <span class="text-red-500">*</span>
      </label>
      <div class="relative">
        <input
          id="password"
          type={showPassword ? 'text' : 'password'}
          bind:value={formData.password}
          on:blur={() => handleBlur('password')}
          on:input={() => handleInput('password')}
          required
          class="
            appearance-none block w-full pr-10 px-3 py-2.5
            border {errors.password && touched.password ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'}
            rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-500
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
            text-gray-900 dark:text-white bg-white dark:bg-gray-800
            transition-all duration-200
          "
        />
        <button
          type="button"
          on:click={() => showPassword = !showPassword}
          class="absolute inset-y-0 right-0 pr-3 flex items-center"
        >
          {#if showPassword}
            <svg class="h-5 w-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
            </svg>
          {:else}
            <svg class="h-5 w-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          {/if}
        </button>
      </div>
      {#if errors.password && touched.password}
        <p class="text-sm text-red-600 dark:text-red-400" in:fly={{ y: -5, duration: 200 }}>
          {errors.password}
        </p>
      {/if}
      
      <!-- Password Strength Indicator -->
      {#if formData.password}
        <div class="mt-2">
          <div class="flex items-center justify-between mb-1">
            <span class="text-xs font-medium text-gray-700 dark:text-gray-300">
              {$t('auth.passwordStrength.label')}
            </span>
            <span class="text-xs font-medium {passwordStrength < 30 ? 'text-red-600' : passwordStrength < 60 ? 'text-yellow-600' : passwordStrength < 80 ? 'text-blue-600' : 'text-green-600'}">
              {strengthLabel}
            </span>
          </div>
          <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
            <div 
              class="h-full transition-all duration-300 ease-out {strengthColor}"
              style="width: {passwordStrength}%"
            ></div>
          </div>
        </div>
      {/if}
    </div>
  
    <!-- Confirm Password -->
    <div class="space-y-1">
      <label for="confirm_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {$t('auth.confirmPassword')} <span class="text-red-500">*</span>
      </label>
      <div class="relative">
        <input
          id="confirm_password"
          type={showConfirmPassword ? 'text' : 'password'}
          bind:value={formData.confirm_password}
          on:blur={() => handleBlur('confirm_password')}
          on:input={() => handleInput('confirm_password')}
          required
          class="
            appearance-none block w-full pr-10 px-3 py-2.5
            border {errors.confirm_password && touched.confirm_password ? 'border-red-300 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'}
            rounded-lg shadow-sm placeholder-gray-400 dark:placeholder-gray-500
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
            text-gray-900 dark:text-white bg-white dark:bg-gray-800
            transition-all duration-200
          "
        />
        <button
          type="button"
          on:click={() => showConfirmPassword = !showConfirmPassword}
          class="absolute inset-y-0 right-0 pr-3 flex items-center"
        >
          {#if showConfirmPassword}
            <svg class="h-5 w-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
            </svg>
          {:else}
            <svg class="h-5 w-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          {/if}
        </button>
      </div>
      {#if errors.confirm_password && touched.confirm_password}
        <p class="text-sm text-red-600 dark:text-red-400" in:fly={{ y: -5, duration: 200 }}>
          {errors.confirm_password}
        </p>
      {/if}
    </div>
  
    <!-- Submit Button -->
    <button
      type="submit"
      disabled={loading}
      class="
        relative w-full flex justify-center py-3 px-4 
        border border-transparent text-sm font-medium rounded-lg 
        text-white bg-primary-600 hover:bg-primary-700 
        focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 
        disabled:opacity-50 disabled:cursor-not-allowed
        transform transition-all duration-200 hover:scale-[1.02]
      "
    >
      {#if loading}
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      {/if}
      {$t('auth.register')}
    </button>
  </form>