<script>
	import { createEventDispatcher, onMount } from 'svelte';
	import { t, locale } from '$lib/i18n';

	export let maxFiles = 10;
	export let maxSize = 10 * 1024 * 1024; // 10MB
	export let allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
	export let disabled = false;
	export let uploading = false;
	export let progress = 0;
	export let multiple = true;

	const dispatch = createEventDispatcher();

	let files = [];
	let dragActive = false;
	let errors = [];
	let fileInput;
	let previewUrls = new Map();

	onMount(() => {
		return () => {
			// Cleanup preview URLs on component destroy
			previewUrls.forEach((url) => URL.revokeObjectURL(url));
		};
	});

	function generatePreview(file) {
		if (file.type.startsWith('image/')) {
			try {
				const url = URL.createObjectURL(file);
				previewUrls.set(file, url);
				return url;
			} catch (err) {
				return null;
			}
		}
		return null;
	}

	function validateFile(file) {
		if (!allowedTypes.includes(file.type)) {
			return `${file.name}: ${$t('mediaUploader.invalidType')}`;
		}

		if (file.size > maxSize) {
			return `${file.name}: ${$t('mediaUploader.fileTooLarge', { size: Math.round(maxSize / 1024 / 1024) })}`;
		}

		return null;
	}

	function handleFiles(newFiles) {
		if (disabled || uploading) return;

		errors = [];
		const validFiles = [];

		for (const file of newFiles) {
			const error = validateFile(file);
			if (error) {
				errors.push(error);
			} else {
				validFiles.push(file);
				generatePreview(file);
			}
		}

		if (!multiple) {
			files = validFiles.slice(0, 1);
		} else if (files.length + validFiles.length > maxFiles) {
			errors.push($t('mediaUploader.tooManyFiles', { max: maxFiles }));
			files = [...files, ...validFiles.slice(0, maxFiles - files.length)];
		} else {
			files = [...files, ...validFiles];
		}

		dispatch('change', { files, errors });
	}

	function handleDrop(event) {
		event.preventDefault();
		dragActive = false;

		if (event.dataTransfer?.files) {
			handleFiles(Array.from(event.dataTransfer.files));
		}
	}

	function handleDragOver(event) {
		event.preventDefault();
		dragActive = true;
	}

	function handleDragLeave() {
		dragActive = false;
	}

	function removeFile(index) {
		const file = files[index];
		if (previewUrls.has(file)) {
			URL.revokeObjectURL(previewUrls.get(file));
			previewUrls.delete(file);
		}

		files = files.filter((_, i) => i !== index);
		dispatch('change', { files, errors });
	}
</script>

<div class="space-y-4">
	<!-- Drop Zone -->
	<div
		class="relative rounded-lg border-2 border-dashed p-6 text-center
      {dragActive
			? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
			: 'border-neutral-300 dark:border-neutral-600'}
      {disabled || uploading ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}"
		on:drop={handleDrop}
		on:dragover={handleDragOver}
		on:dragleave={handleDragLeave}
		on:keydown={(e) => {
			if (e.key === 'Enter' || e.key === ' ') {
				e.preventDefault();
				fileInput.click();
			}
		}}
		role="button"
		tabindex="0"
		aria-label={$t('mediaUploader.dropZone')}
	>
		<input
			type="file"
			bind:this={fileInput}
			class="hidden"
			{multiple}
			accept={allowedTypes.join(',')}
			on:change={(e) => handleFiles(Array.from(e.target.files))}
			disabled={disabled || uploading}
		/>

		{#if uploading}
			<div class="text-center">
				<div
					class="border-primary-500 inline-block h-8 w-8 animate-spin rounded-full border-b-2"
				></div>
				<p class="mt-2 text-sm text-neutral-500 dark:text-neutral-400">
					{$t('mediaUploader.uploading')} ({progress}%)
				</p>
			</div>
		{:else}
			<div class="text-center">
				<svg
					class="mx-auto h-12 w-12 text-neutral-400"
					stroke="currentColor"
					fill="none"
					viewBox="0 0 48 48"
				>
					<path
						d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
					/>
				</svg>
				<p class="mt-2 text-sm text-neutral-500 dark:text-neutral-400">
					{$t('mediaUploader.dragAndDrop')}
				</p>
				<button
					type="button"
					class="focus:ring-primary-500 mt-2 inline-flex items-center rounded-md border border-neutral-300 bg-white px-4 py-2 text-sm font-medium text-neutral-700 shadow-sm hover:bg-neutral-50 focus:ring-2 focus:ring-offset-2 focus:outline-none"
					on:click={() => fileInput.click()}
					disabled={disabled || uploading}
				>
					{$t('mediaUploader.selectFiles')}
				</button>
			</div>
		{/if}
	</div>

	<!-- Errors -->
	{#if errors.length > 0}
		<div class="text-danger-600 dark:text-danger-400 text-sm">
			{#each errors as error}
				<p>{error}</p>
			{/each}
		</div>
	{/if}

	<!-- Preview -->
	{#if files.length > 0}
		<div class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
			{#each files as file, index}
				<div class="group relative">
					<div
						class="aspect-w-3 aspect-h-2 overflow-hidden rounded-lg bg-neutral-100 dark:bg-neutral-800"
					>
						{#if file.type.startsWith('image/')}
							<img src={previewUrls.get(file)} alt={file.name} class="object-cover" />
						{:else}
							<div class="flex h-full items-center justify-center">
								<svg
									class="h-8 w-8 text-neutral-400"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
									/>
								</svg>
							</div>
						{/if}
					</div>

					<button
						type="button"
						class="bg-danger-100 text-danger-600 absolute top-2 right-2 rounded-full p-1 opacity-0 transition-opacity group-hover:opacity-100"
						on:click={() => removeFile(index)}
						aria-label={$t('mediaUploader.removeFile', { name: file.name })}
					>
						<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</button>

					<p class="mt-1 truncate text-xs text-neutral-500 dark:text-neutral-400">
						{file.name}
					</p>
				</div>
			{/each}
		</div>
	{/if}
</div>
