// /src/lib/stores/profileStore.js
import { writable } from 'svelte/store';
import { api } from '$lib/api';
import { authStore } from './authStore';
import { notificationStore } from './notificationStore';

// Initialize profile store
function createProfileStore() {
  const { subscribe, set, update } = writable({
    loading: false,
    updating: false,
    profile: null,
    publicProfile: null,
    error: null,
    sellerProfile: null,
    buyerProfile: null
  });

  return {
    subscribe,
    
    /**
     * Load the current user's profile from the API
     */
    getProfile: async () => {
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        console.log('Fetching profile data from API');
        const response = await api.profile.getProfile();
        
        console.log('Profile data received:', response);
        
        // Update profile store with received data
        update(state => ({ 
          ...state, 
          profile: response,
          loading: false 
        }));
        
        // Update auth store with latest user data to keep in sync
        authStore.updateUserProfile(response);
        
        return response;
      } catch (error) {
        console.error('Error loading profile:', error);
        update(state => ({ 
          ...state, 
          loading: false, 
          error: error.error || 'Failed to load profile' 
        }));
        
        notificationStore.error('Failed to load your profile');
        throw error;
      }
    },
    
    /**
     * Update the current user's profile
     * @param {Object} profileData - User profile data to update
     */
    updateProfile: async (profileData) => {
      update(state => ({ ...state, updating: true, error: null }));
      
      try {
        console.log('Updating profile with data:', profileData);
        
        // Create a new object with only the fields we want to update
        const formattedData = {
          first_name: profileData.first_name,
          last_name: profileData.last_name,
          phone_number: profileData.phone_number,
          date_of_birth: profileData.date_of_birth,
          bio: profileData.bio,
          company_name: profileData.company_name,
          company_registration: profileData.company_registration,
          tax_id: profileData.tax_id,
          address: profileData.address
        };
        
        // If avatar is included and it's a File object, handle it separately
        if (profileData.avatar && profileData.avatar instanceof File) {
          const formData = new FormData();
          formData.append('avatar', profileData.avatar);
          
          console.log('Uploading avatar separately');
          // Use a separate API call to update avatar
          await api.profile.updateAvatar(formData);
        }
        
        // Update profile data
        console.log('Sending profile update request to API');
        const response = await api.profile.updateProfile(formattedData);
        
        console.log('Profile update response:', response);
        
        // Update profile in store
        update(state => ({ 
          ...state, 
          profile: response,
          updating: false 
        }));
        
        // Update auth store with latest user data
        authStore.updateUserProfile(response);
        
        notificationStore.success('Profile updated successfully');
        return response;
      } catch (error) {
        console.error('Error updating profile:', error);
        update(state => ({ 
          ...state, 
          updating: false, 
          error: error.error || 'Failed to update profile' 
        }));
        
        notificationStore.error(error.error || 'Failed to update your profile');
        throw error;
      }
    },
    
    /**
     * Update user avatar
     * @param {FormData} formData - FormData with avatar file
     */
    updateAvatar: async (formData) => {
      update(state => ({ ...state, updating: true, error: null }));
      
      try {
        console.log('Uploading avatar');
        const response = await api.profile.updateAvatar(formData);
        
        console.log('Avatar upload response:', response);
        
        // Update profile in store if response includes user data
        if (response && response.user) {
          update(state => ({ 
            ...state, 
            profile: response.user,
            updating: false 
          }));
          
          // Update auth store with latest user data
          authStore.updateUserProfile(response.user);
        } else {
          // Just update the updating state if no user data returned
          update(state => ({ ...state, updating: false }));
        }
        
        notificationStore.success('Avatar updated successfully');
        return response;
      } catch (error) {
        console.error('Error updating avatar:', error);
        update(state => ({ 
          ...state, 
          updating: false, 
          error: error.error || 'Failed to update avatar' 
        }));
        
        notificationStore.error(error.error || 'Failed to update avatar');
        throw error;
      }
    },
    
    /**
     * Get a user's public profile by ID
     * @param {string} userId - User ID
     */
    getPublicProfile: async (userId) => {
      update(state => ({ ...state, loading: true, error: null }));
      
      try {
        const response = await api.profile.getPublicProfile(userId);
        
        update(state => ({ 
          ...state, 
          publicProfile: response,
          loading: false 
        }));
        
        return response;
      } catch (error) {
        console.error('Error loading public profile:', error);
        update(state => ({ 
          ...state, 
          loading: false, 
          error: error.error || 'Failed to load user profile' 
        }));
        
        notificationStore.error('Failed to load user profile');
        throw error;
      }
    },
    
    /**
     * Update user password
     * @param {string} currentPassword - Current password
     * @param {string} newPassword - New password
     * @param {string} confirmPassword - Confirm new password
     */
    updatePassword: async (currentPassword, newPassword, confirmPassword) => {
      update(state => ({ ...state, updating: true, error: null }));
      
      try {
        await api.auth.changePassword(currentPassword, newPassword, confirmPassword);
        
        update(state => ({ ...state, updating: false }));
        
        notificationStore.success('Password updated successfully');
        return true;
      } catch (error) {
        console.error('Error updating password:', error);
        update(state => ({ 
          ...state, 
          updating: false, 
          error: error.error || 'Failed to update password' 
        }));
        
        notificationStore.error(error.error || 'Failed to update password');
        throw error;
      }
    },
    
    /**
     * Clear error state
     */
    clearError: () => {
      update(state => ({ ...state, error: null }));
    },
    
    /**
     * Reset the store state
     */
    reset: () => {
      set({
        loading: false,
        updating: false,
        profile: null,
        publicProfile: null,
        error: null,
        sellerProfile: null,
        buyerProfile: null
      });
    }
  };
}

// Create and export the profile store
export const profileStore = createProfileStore();