<!-- src/lib/components/ui/FileUploader.svelte -->
<script>
	import { createEventDispatcher } from 'svelte';
	import { t, locale } from '$lib/i18n';

	let {
		files = [],
		acceptedTypes = '*',
		maxFiles = 10,
		maxSize = 10 * 1024 * 1024, // 10MB default
		multiple = true,
		preview = false,
		disabled = false,
		className = ''
	} = $props();

	const dispatch = createEventDispatcher();
	let isRTL = $derived($locale === 'ar');

	// State
	let isDragOver = false;
	let fileInputRef;
	let error = '';

	// Format file size
	function formatFileSize(bytes) {
		if (bytes === 0) return '0 Bytes';
		const k = 1024;
		const sizes = ['Bytes', 'KB', 'MB', 'GB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
	}

	// Validate file
	function validateFile(file) {
		// Check file type
		if (acceptedTypes !== '*') {
			const acceptedArray = acceptedTypes.split(',').map((type) => type.trim());
			const isValidType = acceptedArray.some((type) => {
				if (type.endsWith('/*')) {
					return file.type.startsWith(type.slice(0, -1));
				}
				return file.type === type;
			});

			if (!isValidType) {
				return $t('fileUploader.invalidType');
			}
		}

		// Check file size
		if (file.size > maxSize) {
			return $t('fileUploader.fileTooLarge', { maxSize: formatFileSize(maxSize) });
		}

		return null;
	}

	// Handle file selection
	function handleFiles(newFiles) {
		error = '';
		const fileArray = Array.from(newFiles);

		// Check max files limit
		if (!multiple && fileArray.length > 1) {
			error = $t('fileUploader.singleFileOnly');
			return;
		}

		if (files.length + fileArray.length > maxFiles) {
			error = $t('fileUploader.tooManyFiles', { maxFiles });
			return;
		}

		// Validate each file
		const validFiles = [];
		for (const file of fileArray) {
			const validationError = validateFile(file);
			if (validationError) {
				error = validationError;
				return;
			}
			validFiles.push(file);
		}

		// Add to files array
		const updatedFiles = multiple ? [...files, ...validFiles] : validFiles;
		dispatch('change', updatedFiles);
	}

	// Handle file input change
	function handleFileInputChange(event) {
		if (event.target.files.length > 0) {
			handleFiles(event.target.files);
		}
		// Reset input so the same file can be selected again
		event.target.value = '';
	}

	// Handle drag and drop
	function handleDrop(event) {
		event.preventDefault();
		isDragOver = false;

		if (disabled) return;

		if (event.dataTransfer.files.length > 0) {
			handleFiles(event.dataTransfer.files);
		}
	}

	function handleDragOver(event) {
		event.preventDefault();
		if (!disabled) {
			isDragOver = true;
		}
	}

	function handleDragLeave(event) {
		event.preventDefault();
		// Check if we're actually leaving the drop zone
		if (!event.currentTarget.contains(event.relatedTarget)) {
			isDragOver = false;
		}
	}

	// Remove file
	function removeFile(index) {
		const updatedFiles = files.filter((_, i) => i !== index);
		dispatch('change', updatedFiles);
	}

	// Trigger file input
	function triggerFileInput() {
		if (!disabled) {
			fileInputRef?.click();
		}
	}

	// Get file icon based on type
	function getFileIcon(file) {
		if (file.type.startsWith('image/')) {
			return `<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
			</svg>`;
		} else if (file.type === 'application/pdf') {
			return `<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
			</svg>`;
		}

		return `<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
		</svg>`;
	}

	// Create preview URL for images
	function createPreviewUrl(file) {
		if (file.type.startsWith('image/')) {
			return URL.createObjectURL(file);
		}
		return null;
	}
</script>

<div class="space-y-4 {className}" dir={isRTL ? 'rtl' : 'ltr'}>
	<!-- File Input -->
	<input
		bind:this={fileInputRef}
		type="file"
		accept={acceptedTypes}
		{multiple}
		{disabled}
		class="hidden"
		on:change={handleFileInputChange}
	/>

	<!-- Drop Zone -->
	<div
		class="relative cursor-pointer rounded-lg border-2 border-dashed p-6 text-center transition-all duration-200
			{isDragOver
			? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
			: disabled
				? 'cursor-not-allowed border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800'
				: 'border-gray-300 hover:border-gray-400 hover:bg-gray-50 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-800/50'}"
		on:drop={handleDrop}
		on:dragover={handleDragOver}
		on:dragleave={handleDragLeave}
		on:click={triggerFileInput}
		role="button"
		tabindex="0"
		aria-label={$t('fileUploader.clickToUpload')}
	>
		<div class="flex flex-col items-center justify-center space-y-3">
			<!-- Upload Icon -->
			<div class="rounded-full bg-gray-100 p-3 dark:bg-gray-700">
				<svg
					class="h-8 w-8 text-gray-500 dark:text-gray-400"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
					/>
				</svg>
			</div>

			<!-- Upload Text -->
			<div>
				<p class="text-sm font-medium text-gray-900 dark:text-white">
					{isDragOver ? $t('fileUploader.dropFiles') : $t('fileUploader.clickToUpload')}
				</p>
				<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
					{$t('fileUploader.orDragDrop')}
				</p>
			</div>

			<!-- File Info -->
			<div class="space-y-1 text-xs text-gray-500 dark:text-gray-400">
				{#if acceptedTypes !== '*'}
					<p>{$t('fileUploader.acceptedTypes')}: {acceptedTypes}</p>
				{/if}
				<p>{$t('fileUploader.maxSize')}: {formatFileSize(maxSize)}</p>
				{#if multiple}
					<p>{$t('fileUploader.maxFiles')}: {maxFiles}</p>
				{/if}
			</div>
		</div>
	</div>

	<!-- Error Message -->
	{#if error}
		<div
			class="flex items-center rounded-lg border border-red-200 bg-red-50 p-3 dark:border-red-800 dark:bg-red-900/20"
		>
			<svg class="mr-2 h-5 w-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
				/>
			</svg>
			<p class="text-sm text-red-700 dark:text-red-300">{error}</p>
		</div>
	{/if}

	<!-- File List -->
	{#if files.length > 0}
		<div class="space-y-2">
			<h4 class="text-sm font-medium text-gray-900 dark:text-white">
				{$t('fileUploader.uploadedFiles')} ({files.length}/{maxFiles})
			</h4>

			<div
				class="grid grid-cols-1 {preview && files.some((f) => f.type.startsWith('image/'))
					? 'md:grid-cols-2 lg:grid-cols-3'
					: ''} gap-3"
			>
				{#each files as file, index (file.name + file.size)}
					<div
						class="flex items-center rounded-lg border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-800"
					>
						{#if preview && file.type.startsWith('image/')}
							<!-- Image Preview -->
							<div class="mr-3 flex-shrink-0">
								<img
									src={createPreviewUrl(file)}
									alt={file.name}
									class="h-12 w-12 rounded-lg border border-gray-200 object-cover dark:border-gray-600"
								/>
							</div>
						{:else}
							<!-- File Icon -->
							<div class="mr-3 flex-shrink-0 text-gray-500 dark:text-gray-400">
								{@html getFileIcon(file)}
							</div>
						{/if}

						<!-- File Info -->
						<div class="min-w-0 flex-1">
							<p class="truncate text-sm font-medium text-gray-900 dark:text-white">
								{file.name}
							</p>
							<p class="text-xs text-gray-500 dark:text-gray-400">
								{formatFileSize(file.size)}
							</p>
						</div>

						<!-- Remove Button -->
						{#if !disabled}
							<button
								type="button"
								class="ml-2 flex-shrink-0 p-1 text-gray-400 transition-colors duration-150 hover:text-red-500 dark:hover:text-red-400"
								on:click={() => removeFile(index)}
								aria-label={$t('fileUploader.removeFile')}
							>
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M6 18L18 6M6 6l12 12"
									/>
								</svg>
							</button>
						{/if}
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>

<style>
	/* Smooth transitions for drag states */
	.transition-all {
		transition: all 0.2s ease-in-out;
	}

	/* Image preview hover effects */
	img {
		transition: transform 0.2s ease-in-out;
	}

	img:hover {
		transform: scale(1.05);
	}
</style>
