<!-- src/lib/components/ui/ShareButton.svelte -->
<script>
    import { onMount } from 'svelte';
    import { notificationStore } from '$lib/stores/notificationStore';
    import Button from './Button.svelte';
    import Icon from './Icon.svelte';
    import Modal from './Modal.svelte';
    
    // Props
    export let title = '';
    export let text = '';
    export let url = '';
    export let variant = 'outline'; // Button variant (outline, primary, etc.)
    export let size = 'sm'; // Button size
    export let showLabel = false; // Whether to show "Share" text on button
    
    // State
    let isOpen = false;
    let fullUrl = '';
    let canShare = false;
    let isUrlCopied = false;
    
    // Share options
    const shareOptions = [
      {
        id: 'facebook',
        name: 'Facebook',
        icon: '<svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor"><path d="M9.198 21.5h4v-8.01h3.604l.396-3.98h-4V7.5a1 1 0 011-1h3v-4h-3a5 5 0 00-5 5v2.01h-2l-.396 3.98h2.396v8.01z"></path></svg>',
        bgColor: 'bg-blue-600',
        getUrl: () => `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(fullUrl)}`
      },
      {
        id: 'twitter',
        name: 'Twitter',
        icon: '<svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor"><path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/></svg>',
        bgColor: 'bg-sky-500',
        getUrl: () => `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(fullUrl)}`
      },
      {
        id: 'linkedin',
        name: 'LinkedIn',
        icon: '<svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>',
        bgColor: 'bg-blue-700',
        getUrl: () => `https://www.linkedin.com/shareArticle?mini=true&url=${encodeURIComponent(fullUrl)}&title=${encodeURIComponent(title)}&summary=${encodeURIComponent(text)}`
      },
      {
        id: 'whatsapp',
        name: 'WhatsApp',
        icon: '<svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>',
        bgColor: 'bg-green-600',
        getUrl: () => `https://api.whatsapp.com/send?text=${encodeURIComponent(`${title} ${fullUrl}`)}`
      },
      {
        id: 'telegram',
        name: 'Telegram',
        icon: '<svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.88 6.504-1.243 8.635-.162.95-.45 1.268-.734 1.3-.626.065-1.104-.42-1.714-.825-.958-.63-1.504-1.02-2.435-1.636-1.07-.73-.376-1.13.234-1.785.16-.172 2.937-2.683 2.986-2.91.01-.042.02-.195-.07-.275-.09-.08-.216-.053-.31-.033-.135.03-2.254 1.425-6.357 4.19-.603.405-1.147.602-1.634.591-.538-.015-1.572-.235-2.342-.43-.981-.248-1.783-.377-1.717-.794.035-.22.453-.451 1.254-.69 4.918-2.142 8.203-3.55 9.855-4.23 4.687-1.92 5.658-2.253 6.292-2.264" /></svg>',
        bgColor: 'bg-blue-500',
        getUrl: () => `https://telegram.me/share/url?url=${encodeURIComponent(fullUrl)}&text=${encodeURIComponent(title)}`
      },
      {
        id: 'email',
        name: 'Email',
        icon: '<svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>',
        bgColor: 'bg-gray-600',
        getUrl: () => `mailto:?subject=${encodeURIComponent(title)}&body=${encodeURIComponent(`${text} ${fullUrl}`)}`
      }
    ];
    
    // Handle opening the share modal
    function openShareModal() {
      isOpen = true;
    }
    
    // Handle closing the share modal
    function closeShareModal() {
      isOpen = false;
      isUrlCopied = false;
    }
    
    // Copy URL to clipboard
    async function copyUrl() {
      try {
        await navigator.clipboard.writeText(fullUrl);
        isUrlCopied = true;
        notificationStore.success('URL copied to clipboard');
        
        // Reset copy status after 3 seconds
        setTimeout(() => {
          isUrlCopied = false;
        }, 3000);
      } catch (err) {
        console.error('Failed to copy URL:', err);
        notificationStore.error('Failed to copy URL');
      }
    }
    
    // Handle native share if available
    async function nativeShare() {
      try {
        await navigator.share({
          title,
          text,
          url: fullUrl
        });
        notificationStore.success('Shared successfully');
        closeShareModal();
      } catch (err) {
        console.error('Error sharing:', err);
        // User probably canceled, no need to show error
      }
    }
    
    // Share via platform
    function shareTo(platform) {
      const option = shareOptions.find(o => o.id === platform);
      if (option) {
        window.open(option.getUrl(), '_blank', 'noopener,noreferrer');
        notificationStore.info(`Shared to ${option.name}`);
      }
    }
    
    onMount(() => {
      // Construct the full URL
      const baseUrl = window.location.origin;
      fullUrl = url.startsWith('http') ? url : `${baseUrl}${url}`;
      
      // Check if Web Share API is available
      canShare = !!navigator.share;
    });
  </script>
  
  <Button
    {variant}
    {size}
    on:click={openShareModal}
    aria-label="Share this content"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="w-4 h-4 {showLabel ? 'mr-2' : ''}"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" />
      <polyline points="16 6 12 2 8 6" />
      <line x1="12" y1="2" x2="12" y2="15" />
    </svg>
    {#if showLabel}
      Share
    {/if}
  </Button>
  
  <Modal
    open={isOpen}
    title="Share this content"
    on:close={closeShareModal}
    size="md"
  >
    <!-- Title and description -->
    <div class="mb-5">
      <h3 class="text-lg font-medium text-text-dark mb-1">{title}</h3>
      {#if text}
        <p class="text-sm text-text-medium">{text}</p>
      {/if}
    </div>
    
    <!-- Native share button (if available) -->
    {#if canShare}
      <Button
        variant="primary"
        fullWidth={true}
        class="mb-5"
        on:click={nativeShare}
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="18" cy="5" r="3" />
          <circle cx="6" cy="12" r="3" />
          <circle cx="18" cy="19" r="3" />
          <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
          <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
        </svg>
        Share using device
      </Button>
    {/if}
    
    <!-- Copy link section -->
    <div class="flex items-center mb-5 space-x-2">
      <div class="flex-grow bg-primary-blue/10 rounded-lg p-2 text-sm text-text-medium truncate">
        {fullUrl}
      </div>
      <Button
        variant={isUrlCopied ? 'primary' : 'outline'}
        size="sm"
        on:click={copyUrl}
      >
        {#if isUrlCopied}
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12" />
          </svg>
          Copied
        {:else}
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
            <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
          </svg>
          Copy
        {/if}
      </Button>
    </div>
    
    <!-- Social share options -->
    <div class="grid grid-cols-3 gap-3">
      {#each shareOptions as option}
        <button
          class="flex flex-col items-center justify-center p-3 rounded-xl transition-all duration-200
            text-white {option.bgColor} hover:opacity-90 transform hover:scale-105"
          on:click={() => shareTo(option.id)}
        >
          <div class="mb-2">
            {@html option.icon}
          </div>
          <span class="text-xs font-medium">{option.name}</span>
        </button>
      {/each}
    </div>
  </Modal>