<script>
	import { createEventDispatcher } from 'svelte';
	import { t } from '$lib/i18n';
	import FileUploader from '$lib/components/ui/FileUploader.svelte';

	const dispatch = createEventDispatcher();

	export let media = [];
	export let maxFiles = 10;
	export let accept = 'image/*,video/*';
	export let maxSize = 10 * 1024 * 1024; // 10MB
	export let title = $t('media.uploadTitle');
	export let description = $t('media.uploadDescription');

	function handleFilesSelected(event) {
		dispatch('filesSelected', {
			files: event.detail.files,
			media: event.detail.files.map((file) => ({
				file,
				type: file.type.startsWith('image/') ? 'image' : 'video',
				name: file.name,
				size: file.size,
				url: URL.createObjectURL(file)
			}))
		});
	}

	function handleFileRemoved(event) {
		dispatch('fileRemoved', event.detail);
	}

	function handleError(event) {
		dispatch('error', event.detail);
	}
</script>

<div class="space-y-4">
	<div>
		<h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
			{title}
		</h3>
		{#if description}
			<p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
				{description}
			</p>
		{/if}
	</div>

	<FileUploader
		files={media}
		{maxFiles}
		{accept}
		{maxSize}
		on:filesSelected={handleFilesSelected}
		on:fileRemoved={handleFileRemoved}
		on:error={handleError}
	/>
</div>
