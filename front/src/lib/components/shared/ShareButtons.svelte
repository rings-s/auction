<!-- src/lib/components/shared/ShareButtons.svelte -->
<script>
	import { t, locale } from '$lib/i18n';
	import { onMount, createEventDispatcher } from 'svelte';
	import { browser } from '$app/environment';
	import { fade, scale, fly } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';

	// Props
	export let url = '';
	export let title = '';
	export let description = '';
	export let variant = 'default'; // 'default', 'compact', 'large', 'minimal', 'pills'
	export let extraClass = '';
	export let showLabels = false;
	export let orientation = 'horizontal'; // 'horizontal', 'vertical'
	export let platforms = ['facebook', 'twitter', 'linkedin', 'whatsapp', 'email', 'copy']; // Customizable platforms
	export let trackSharing = false; // Analytics tracking
	export let hideNativeShare = false; // Option to hide native share

	// State
	let fullUrl = '';
	let showTooltip = false;
	let tooltipMessage = '';
	let isShareOpen = false;
	let supportsNativeShare = false;
	let mounted = false;
	let shareContainer;

	// Event dispatcher
	const dispatch = createEventDispatcher();

	// Reactive values
	$: isRTL = $locale === 'ar';
	$: containerClasses = getContainerClasses();
	$: buttonClasses = getButtonClasses();
	$: iconSizes = getIconSizes();

	// Platform configurations
	const platformConfig = {
		facebook: {
			name: 'Facebook',
			icon: 'facebook',
			color: 'text-blue-600 hover:text-blue-700',
			bgColor: 'hover:bg-blue-50 dark:hover:bg-blue-900/20',
			action: shareOnFacebook
		},
		twitter: {
			name: 'Twitter',
			icon: 'twitter',
			color: 'text-sky-500 hover:text-sky-600',
			bgColor: 'hover:bg-sky-50 dark:hover:bg-sky-900/20',
			action: shareOnTwitter
		},
		linkedin: {
			name: 'LinkedIn',
			icon: 'linkedin',
			color: 'text-blue-700 hover:text-blue-800',
			bgColor: 'hover:bg-blue-50 dark:hover:bg-blue-900/20',
			action: shareOnLinkedIn
		},
		whatsapp: {
			name: 'WhatsApp',
			icon: 'whatsapp',
			color: 'text-green-500 hover:text-green-600',
			bgColor: 'hover:bg-green-50 dark:hover:bg-green-900/20',
			action: shareOnWhatsApp
		},
		email: {
			name: 'Email',
			icon: 'email',
			color: 'text-gray-600 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300',
			bgColor: 'hover:bg-gray-50 dark:hover:bg-gray-700',
			action: shareByEmail
		},
		copy: {
			name: 'Copy Link',
			icon: 'link',
			color: 'text-gray-600 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300',
			bgColor: 'hover:bg-gray-50 dark:hover:bg-gray-700',
			action: copyToClipboard
		}
	};

	// Dynamic classes based on variant
	function getContainerClasses() {
		const baseClasses = 'flex items-center';
		const orientationClasses =
			orientation === 'vertical' ? 'flex-col space-y-2' : 'flex-row space-x-2';
		const variantClasses = {
			default: 'gap-2',
			compact: 'gap-1',
			large: 'gap-3',
			minimal: 'gap-1',
			pills: 'gap-2'
		};

		return `${baseClasses} ${orientationClasses} ${variantClasses[variant]} ${extraClass}`;
	}

	function getButtonClasses() {
		const baseClasses =
			'relative transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500';
		const variantClasses = {
			default: 'p-2 rounded-lg',
			compact: 'p-1.5 rounded-md',
			large: 'p-3 rounded-xl',
			minimal: 'p-1 rounded',
			pills: 'px-3 py-2 rounded-full border border-gray-200 dark:border-gray-700'
		};

		return `${baseClasses} ${variantClasses[variant]}`;
	}

	function getIconSizes() {
		return {
			default: 'h-5 w-5',
			compact: 'h-4 w-4',
			large: 'h-6 w-6',
			minimal: 'h-4 w-4',
			pills: 'h-4 w-4'
		};
	}

	onMount(() => {
		mounted = true;

		// Get the full URL including domain
		if (browser) {
			const origin = window.location.origin;
			fullUrl = url.startsWith('http') ? url : `${origin}${url.startsWith('/') ? '' : '/'}${url}`;

			// Check for native share support
			supportsNativeShare = 'share' in navigator && !hideNativeShare;
		}
	});

	// Sharing functions with enhanced error handling and analytics
	async function shareOnFacebook() {
		const shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(fullUrl)}`;
		await openShareWindow(shareUrl, 'facebook-share', 'width=580,height=296');
		trackShare('facebook');
	}

	async function shareOnTwitter() {
		const text = description || title;
		const shareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(fullUrl)}&text=${encodeURIComponent(text)}`;
		await openShareWindow(shareUrl, 'twitter-share', 'width=550,height=235');
		trackShare('twitter');
	}

	async function shareOnLinkedIn() {
		const shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(fullUrl)}`;
		await openShareWindow(shareUrl, 'linkedin-share', 'width=750,height=450');
		trackShare('linkedin');
	}

	async function shareOnWhatsApp() {
		const shareText = `${title}\n\n${description || ''}\n\n${fullUrl}`.trim();
		const shareUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(shareText)}`;

		// Use different approach for mobile vs desktop
		if (isMobile()) {
			window.location.href = shareUrl;
		} else {
			await openShareWindow(shareUrl, 'whatsapp-share', 'width=400,height=600');
		}
		trackShare('whatsapp');
	}

	async function shareByEmail() {
		const subject = encodeURIComponent(title);
		const body = encodeURIComponent(`${description || title}\n\n${fullUrl}`);
		window.location.href = `mailto:?subject=${subject}&body=${body}`;
		trackShare('email');
	}

	async function copyToClipboard() {
		try {
			if (navigator.clipboard && window.isSecureContext) {
				await navigator.clipboard.writeText(fullUrl);
			} else {
				// Fallback for older browsers
				const textArea = document.createElement('textarea');
				textArea.value = fullUrl;
				textArea.style.position = 'fixed';
				textArea.style.left = '-999999px';
				textArea.style.top = '-999999px';
				document.body.appendChild(textArea);
				textArea.focus();
				textArea.select();
				document.execCommand('copy');
				textArea.remove();
			}

			showTooltipMessage($t('common.linkCopied'));
			trackShare('copy');
		} catch (err) {
			showTooltipMessage('Failed to copy link');
		}
	}

	async function shareNatively() {
		if (!supportsNativeShare) return;

		try {
			await navigator.share({
				title,
				text: description,
				url: fullUrl
			});
			trackShare('native');
		} catch (err) {
			if (err.name !== 'AbortError') {
				// Error handled silently
			}
		}
	}

	// Helper functions
	function openShareWindow(url, name, features) {
		return new Promise((resolve) => {
			const shareWindow = window.open(url, name, features);

			// Check if popup was blocked
			if (!shareWindow || shareWindow.closed || typeof shareWindow.closed === 'undefined') {
				// Fallback: open in same tab
				window.open(url, '_blank');
			}

			resolve();
		});
	}

	function isMobile() {
		return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
			navigator.userAgent
		);
	}

	function showTooltipMessage(message) {
		tooltipMessage = message;
		showTooltip = true;
		setTimeout(() => {
			showTooltip = false;
		}, 2000);
	}

	function trackShare(platform) {
		if (trackSharing) {
			dispatch('share', {
				platform,
				url: fullUrl,
				title,
				timestamp: new Date().toISOString()
			});

			// Optional: Google Analytics, Plausible, etc.
			if (typeof gtag !== 'undefined') {
				gtag('event', 'share', {
					method: platform,
					content_type: 'property',
					item_id: url
				});
			}
		}
	}

	function toggleShareMenu() {
		isShareOpen = !isShareOpen;
	}

	function handleKeydown(event, action) {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			action();
		}
	}

	// Close share menu when clicking outside
	function handleClickOutside(event) {
		if (shareContainer && !shareContainer.contains(event.target)) {
			isShareOpen = false;
		}
	}

	$: if (browser && isShareOpen) {
		document.addEventListener('click', handleClickOutside);
	} else if (browser) {
		document.removeEventListener('click', handleClickOutside);
	}
</script>

<div
	bind:this={shareContainer}
	class={containerClasses}
	role="group"
	aria-label={$t('common.shareOptions')}
>
	<!-- Native Share Button (if supported and not hidden) -->
	{#if supportsNativeShare && mounted}
		<button
			type="button"
			class="{buttonClasses} bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 hover:bg-primary-100 dark:hover:bg-primary-900/30"
			on:click={shareNatively}
			on:keydown={(e) => handleKeydown(e, shareNatively)}
			aria-label={$t('common.share')}
			title={$t('common.share')}
			transition:scale={{ duration: 200, easing: quintOut }}
		>
			<svg
				class={iconSizes[variant]}
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
				aria-hidden="true"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"
				/>
			</svg>
			{#if showLabels}
				<span class="ml-2 text-sm font-medium">{$t('common.share')}</span>
			{/if}
		</button>
	{/if}

	<!-- Individual Platform Buttons -->
	{#each platforms as platform, index (platform)}
		{#if platformConfig[platform]}
			{@const config = platformConfig[platform]}
			<button
				type="button"
				class="{buttonClasses} {config.bgColor} {config.color}"
				on:click={config.action}
				on:keydown={(e) => handleKeydown(e, config.action)}
				aria-label={$t(`share.${platform}`) || config.name}
				title={$t(`share.${platform}`) || config.name}
				in:scale={{ duration: 200, delay: index * 50, easing: quintOut }}
			>
				<!-- Platform Icons -->
				{#if config.icon === 'facebook'}
					<svg
						class={iconSizes[variant]}
						fill="currentColor"
						viewBox="0 0 24 24"
						aria-hidden="true"
					>
						<path
							fill-rule="evenodd"
							d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z"
							clip-rule="evenodd"
						/>
					</svg>
				{:else if config.icon === 'twitter'}
					<svg
						class={iconSizes[variant]}
						fill="currentColor"
						viewBox="0 0 24 24"
						aria-hidden="true"
					>
						<path
							d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84"
						/>
					</svg>
				{:else if config.icon === 'linkedin'}
					<svg
						class={iconSizes[variant]}
						fill="currentColor"
						viewBox="0 0 24 24"
						aria-hidden="true"
					>
						<path
							d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"
						/>
					</svg>
				{:else if config.icon === 'whatsapp'}
					<svg
						class={iconSizes[variant]}
						fill="currentColor"
						viewBox="0 0 24 24"
						aria-hidden="true"
					>
						<path
							d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"
						/>
					</svg>
				{:else if config.icon === 'email'}
					<svg
						class={iconSizes[variant]}
						fill="currentColor"
						viewBox="0 0 24 24"
						aria-hidden="true"
					>
						<path
							d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"
						/>
					</svg>
				{:else if config.icon === 'link'}
					<svg
						class={iconSizes[variant]}
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
						aria-hidden="true"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
						/>
					</svg>
				{/if}

				{#if showLabels}
					<span class="{isRTL ? 'mr-2' : 'ml-2'} text-sm font-medium">
						{$t(`share.${platform}`) || config.name}
					</span>
				{/if}
			</button>
		{/if}
	{/each}

	<!-- Tooltip for copy feedback -->
	{#if showTooltip}
		<div
			class="absolute {orientation === 'vertical' ? 'left-full ml-2' : 'bottom-full mb-2'} 
        left-1/2 z-50 -translate-x-1/2 transform rounded-lg
        bg-gray-900 px-3 py-2 text-sm
        whitespace-nowrap text-white shadow-lg dark:bg-gray-100 dark:text-gray-900"
			role="tooltip"
			transition:fly={{ y: -10, duration: 200 }}
		>
			{tooltipMessage}
			<div
				class="absolute {orientation === 'vertical'
					? 'top-1/2 left-0 h-2 w-2 -translate-x-1 -translate-y-1/2 rotate-45 transform'
					: 'top-full left-1/2 h-2 w-2 -translate-x-1/2 rotate-45 transform'} 
        bg-gray-900 dark:bg-gray-100"
			></div>
		</div>
	{/if}
</div>

<style>
	/* Enhanced focus styles for better accessibility */
	button:focus-visible {
		outline: 2px solid rgb(59 130 246);
		outline-offset: 2px;
	}

	/* Smooth hover animations */
	button {
		transform-origin: center;
	}

	button:hover {
		transform: scale(1.05);
	}

	button:active {
		transform: scale(0.95);
	}

	/* High contrast mode support */
	@media (prefers-contrast: high) {
		button {
			border: 2px solid currentColor;
		}
	}

	/* Reduced motion support */
	@media (prefers-reduced-motion: reduce) {
		button {
			transition: none;
			transform: none;
		}

		button:hover,
		button:active {
			transform: none;
		}
	}

	/* RTL support */
	:global(.rtl) button {
		direction: rtl;
	}

	/* Custom scrollbar for horizontal overflow on mobile */
	@media (max-width: 640px) {
		.flex-row {
			overflow-x: auto;
			scrollbar-width: none;
			-ms-overflow-style: none;
		}

		.flex-row::-webkit-scrollbar {
			display: none;
		}
	}
</style>
