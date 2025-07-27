<!-- src/lib/components/ui/Gallery.svelte -->
<script>
	import { createEventDispatcher } from 'svelte';

	export let images = [];
	export let fallbackImage = null;
	export let alt = '';
	export let showThumbnails = true;
	export let autoPlay = false;
	export let interval = 5000;

	const dispatch = createEventDispatcher();

	let currentIndex = 0;
	let showModal = false;
	let intervalId = null;

	$: hasImages = images && images.length > 0;
	$: displayImages = hasImages ? images : fallbackImage ? [{ url: fallbackImage, alt }] : [];

	function nextImage() {
		if (displayImages.length > 1) {
			currentIndex = (currentIndex + 1) % displayImages.length;
		}
	}

	function prevImage() {
		if (displayImages.length > 1) {
			currentIndex = currentIndex === 0 ? displayImages.length - 1 : currentIndex - 1;
		}
	}

	function goToImage(index) {
		currentIndex = index;
	}

	function openModal(index = currentIndex) {
		currentIndex = index;
		showModal = true;
		dispatch('modalOpen', { index });
	}

	function closeModal() {
		showModal = false;
		dispatch('modalClose');
	}

	function startAutoPlay() {
		if (autoPlay && displayImages.length > 1) {
			intervalId = setInterval(nextImage, interval);
		}
	}

	function stopAutoPlay() {
		if (intervalId) {
			clearInterval(intervalId);
			intervalId = null;
		}
	}

	$: if (autoPlay) {
		startAutoPlay();
	} else {
		stopAutoPlay();
	}

	// Handle keyboard navigation
	function handleKeydown(event) {
		if (!showModal) return;

		switch (event.key) {
			case 'ArrowLeft':
				prevImage();
				break;
			case 'ArrowRight':
				nextImage();
				break;
			case 'Escape':
				closeModal();
				break;
		}
	}
</script>

<svelte:window on:keydown={handleKeydown} />

<div class="gallery-container">
	{#if displayImages.length > 0}
		<!-- Main Image Display -->
		<div
			class="aspect-w-16 aspect-h-9 relative overflow-hidden rounded-lg bg-gray-200 dark:bg-gray-700"
		>
			<button
				type="button"
				class="h-full w-full cursor-pointer focus:ring-2 focus:ring-blue-500 focus:outline-none"
				on:click={() => openModal(currentIndex)}
				aria-label="View full-size image"
			>
				<img
					src={displayImages[currentIndex].url}
					alt={displayImages[currentIndex].alt || alt}
					class="h-full w-full object-cover transition-transform duration-300 hover:scale-105"
				/>
			</button>

			<!-- Navigation Arrows (only show if multiple images) -->
			{#if displayImages.length > 1}
				<button
					class="bg-opacity-50 hover:bg-opacity-75 absolute top-1/2 left-2 -translate-y-1/2 transform rounded-full bg-black p-2 text-white transition-opacity"
					on:click|stopPropagation={prevImage}
					aria-label="Previous image"
				>
					<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M15 19l-7-7 7-7"
						/>
					</svg>
				</button>

				<button
					class="bg-opacity-50 hover:bg-opacity-75 absolute top-1/2 right-2 -translate-y-1/2 transform rounded-full bg-black p-2 text-white transition-opacity"
					on:click|stopPropagation={nextImage}
					aria-label="Next image"
				>
					<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 5l7 7-7 7"
						/>
					</svg>
				</button>

				<!-- Image Counter -->
				<div
					class="bg-opacity-50 absolute right-2 bottom-2 rounded bg-black px-2 py-1 text-sm text-white"
				>
					{currentIndex + 1} / {displayImages.length}
				</div>
			{/if}

			<!-- Expand Button -->
			<button
				class="bg-opacity-50 hover:bg-opacity-75 absolute top-2 right-2 rounded-full bg-black p-2 text-white transition-opacity"
				on:click|stopPropagation={() => openModal(currentIndex)}
				aria-label="Expand image"
			>
				<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
					/>
				</svg>
			</button>
		</div>

		<!-- Thumbnails -->
		{#if showThumbnails && displayImages.length > 1}
			<div class="mt-4 flex space-x-2 overflow-x-auto pb-2">
				{#each displayImages as image, index}
					<button
						class="h-20 w-20 flex-shrink-0 overflow-hidden rounded-lg border-2 transition-all duration-200 {index ===
						currentIndex
							? 'border-primary-500 ring-primary-200 ring-2'
							: 'border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600'}"
						on:click={() => goToImage(index)}
						aria-label="View image {index + 1}"
					>
						<img
							src={image.url}
							alt={image.alt || `Thumbnail ${index + 1}`}
							class="h-full w-full object-cover"
						/>
					</button>
				{/each}
			</div>
		{/if}
	{:else}
		<!-- No Images Placeholder -->
		<div
			class="aspect-w-16 aspect-h-9 flex items-center justify-center rounded-lg bg-gray-200 dark:bg-gray-700"
		>
			<div class="text-center">
				<svg
					class="mx-auto mb-4 h-16 w-16 text-gray-400 dark:text-gray-500"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
					/>
				</svg>
				<p class="text-gray-500 dark:text-gray-400">No images available</p>
			</div>
		</div>
	{/if}
</div>

<!-- Full Screen Modal -->
{#if showModal}
	<div class="insets-0 bg-opacity-90 fixed z-50 flex items-center justify-center bg-black p-4">
		<div class="relative max-h-full max-w-7xl">
			<!-- Close Button -->
			<button
				class="bg-opacity-50 hover:bg-opacity-75 absolute top-4 right-4 z-10 rounded-full bg-black p-2 text-white transition-opacity"
				on:click={closeModal}
				aria-label="Close modal"
			>
				<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M6 18L18 6M6 6l12 12"
					/>
				</svg>
			</button>

			<!-- Main Image -->
			<div class="relative">
				<img
					src={displayImages[currentIndex].url}
					alt={displayImages[currentIndex].alt || alt}
					class="max-h-[90vh] max-w-full object-contain"
				/>

				<!-- Navigation Arrows (only show if multiple images) -->
				{#if displayImages.length > 1}
					<button
						class="bg-opacity-50 hover:bg-opacity-75 absolute top-1/2 left-4 -translate-y-1/2 transform rounded-full bg-black p-3 text-white transition-opacity"
						on:click={prevImage}
						aria-label="Previous image"
					>
						<svg class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M15 19l-7-7 7-7"
							/>
						</svg>
					</button>

					<button
						class="bg-opacity-50 hover:bg-opacity-75 absolute top-1/2 right-4 -translate-y-1/2 transform rounded-full bg-black p-3 text-white transition-opacity"
						on:click={nextImage}
						aria-label="Next image"
					>
						<svg class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 5l7 7-7 7"
							/>
						</svg>
					</button>
				{/if}
			</div>

			<!-- Image Info -->
			{#if displayImages[currentIndex].caption}
				<div class="mt-4 text-center">
					<p class="text-lg text-white">{displayImages[currentIndex].caption}</p>
				</div>
			{/if}

			<!-- Thumbnail Navigation -->
			{#if showThumbnails && displayImages.length > 1}
				<div class="mt-6 flex justify-center space-x-2 overflow-x-auto pb-2">
					{#each displayImages as image, index}
						<button
							class="h-16 w-16 flex-shrink-0 overflow-hidden rounded-lg border-2 transition-all duration-200 {index ===
							currentIndex
								? 'ring-opacity-50 border-white ring-2 ring-white'
								: 'border-gray-400 hover:border-white'}"
							on:click={() => goToImage(index)}
							aria-label="View image {index + 1}"
						>
							<img
								src={image.url}
								alt={image.alt || `Thumbnail ${index + 1}`}
								class="h-full w-full object-cover"
							/>
						</button>
					{/each}
				</div>
			{/if}
		</div>
	</div>
{/if}

<style>
	.gallery-container {
		@apply w-full;
	}

	.insets-0 {
		top: 0;
		right: 0;
		bottom: 0;
		left: 0;
	}
</style>
