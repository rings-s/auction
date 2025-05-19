<!-- src/lib/components/ShareButtons.svelte -->
<script>
    import { t } from '$lib/i18n/i18n';
    import { onMount } from 'svelte';
    
    export let url = '';
    export let title = '';
    export let description = '';
    export let variant = 'default'; // 'default', 'compact', 'large'
    
    let fullUrl = '';
    let showTooltip = false;
    
    // Button classes based on variant
    const buttonClasses = {
      default: 'p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700',
      compact: 'p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700',
      large: 'p-3 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700'
    };
    
    // Icon sizes based on variant
    const iconSizes = {
      default: 'h-5 w-5',
      compact: 'h-4 w-4',
      large: 'h-6 w-6'
    };
    
    onMount(() => {
      // Get the full URL including domain
      const origin = window.location.origin;
      fullUrl = url.startsWith('http') ? url : `${origin}${url.startsWith('/') ? '' : '/'}${url}`;
    });
    
    function shareOnFacebook() {
      const shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(fullUrl)}`;
      window.open(shareUrl, 'facebook-share', 'width=580,height=296');
    }
    
    function shareOnTwitter() {
      const shareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(fullUrl)}&text=${encodeURIComponent(title)}`;
      window.open(shareUrl, 'twitter-share', 'width=550,height=235');
    }
    
    function shareOnLinkedIn() {
      const shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(fullUrl)}`;
      window.open(shareUrl, 'linkedin-share', 'width=750,height=450');
    }
    
    function shareByEmail() {
      const subject = encodeURIComponent(title);
      const body = encodeURIComponent(`${description || title}\n\n${fullUrl}`);
      window.location.href = `mailto:?subject=${subject}&body=${body}`;
    }
    
    async function copyToClipboard() {
      try {
        await navigator.clipboard.writeText(fullUrl);
        showTooltip = true;
        setTimeout(() => {
          showTooltip = false;
        }, 2000);
      } catch (err) {
        console.error('Failed to copy: ', err);
      }
    }
  </script>
  
  <div class="flex items-center space-x-2">
    <button
      type="button"
      class={buttonClasses[variant]}
      on:click={shareOnFacebook}
      aria-label={$t('share.facebook')}
      title={$t('share.facebook')}
    >
      <svg class={`${iconSizes[variant]} text-blue-600`} fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path fill-rule="evenodd" d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" clip-rule="evenodd" />
      </svg>
    </button>
    
    <button
      type="button"
      class={buttonClasses[variant]}
      on:click={shareOnTwitter}
      aria-label={$t('share.twitter')}
      title={$t('share.twitter')}
    >
      <svg class={`${iconSizes[variant]} text-blue-400`} fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
      </svg>
    </button>
    
    <button
      type="button"
      class={buttonClasses[variant]}
      on:click={shareOnLinkedIn}
      aria-label={$t('share.linkedin')}
      title={$t('share.linkedin')}
    >
      <svg class={`${iconSizes[variant]} text-blue-700`} fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/>
      </svg>
    </button>
    
    <button
      type="button"
      class={buttonClasses[variant]}
      on:click={shareByEmail}
      aria-label={$t('share.email')}
      title={$t('share.email')}
    >
      <svg class={`${iconSizes[variant]} text-gray-500 dark:text-gray-400`} fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
      </svg>
    </button>
    
    <div class="relative">
      <button
        type="button"
        class={buttonClasses[variant]}
        on:click={copyToClipboard}
        aria-label={$t('share.copyLink')}
        title={$t('share.copyLink')}
      >
        <svg class={`${iconSizes[variant]} text-gray-500 dark:text-gray-400`} fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M13.0605 8.11071L14.4747 6.69647C15.8457 5.32544 18.0718 5.32544 19.4428 6.69647C20.8139 8.06749 20.8139 10.2936 19.4428 11.6646L18.0286 13.0789M13.0605 8.11071L14.1213 7.04996M13.0605 8.11071C13.0605 8.11071 11.4393 9.73191 8.19723 12.9739M6.7825 16.3887L5.36827 17.8029C3.99724 19.174 1.77112 19.174 0.400098 17.8029C-0.970924 16.4319 -0.970924 14.2058 0.400098 12.8348L1.81433 11.4205M6.7825 16.3887L5.72175 17.4494M6.7825 16.3887C6.7825 16.3887 8.4037 14.7675 11.6458 11.5255M7.82837 10.3753L13.6241 16.171M11.6458 11.5255L12.7065 10.4647M11.6458 11.5255L10.585 12.5863M8.19723 12.9739L7.13648 14.0347M8.19723 12.9739L9.25797 11.9132"/>
        </svg>
      </button>
      
      {#if showTooltip}
        <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 -translate-y-1 px-2 py-1 bg-gray-800 text-white text-xs rounded shadow-lg whitespace-nowrap">
          {$t('share.linkCopied')}
          <div class="absolute top-full left-1/2 transform -translate-x-1/2 w-2 h-2 rotate-45 bg-gray-800"></div>
        </div>
      {/if}
    </div>
  </div>