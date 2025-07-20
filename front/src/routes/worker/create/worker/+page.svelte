<!-- src/routes/create/worker/+page.svelte -->
<script>
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import { toast } from '$lib/stores/toastStore.svelte.js';
	import { createWorker } from '$lib/api/worker';
	import WorkerForm from '$lib/components/property-management/workers/WorkerForm.svelte';
	import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';

	// Breadcrumb items
	let breadcrumbItems = [
		{ label: $t('nav.home'), href: '/' },
		{ label: $t('nav.dashboard'), href: '/dashboard' },
		{ label: $t('worker.workers'), href: '/dashboard/workers' },
		{ label: $t('worker.add'), href: '/create/worker', active: true }
	];

	// Handle form submission
	async function handleSubmit(event) {
		try {
			const worker = await createWorker(event.detail);
			toast.success($t('worker.createSuccess'));
			goto('/dashboard/workers');
		} catch (error) {
			toast.error($t('worker.createError'));
		}
	}

	// Handle form cancel
	function handleCancel() {
		goto('/dashboard/workers');
	}
</script>

<svelte:head>
	<title>{$t('worker.add')} - {$t('app.name')}</title>
	<meta name="description" content={$t('worker.addDescription')} />
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<div class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
		<div class="space-y-6">
			<!-- Breadcrumb -->
			<Breadcrumb items={breadcrumbItems} />
			
			<!-- Page Header -->
			<div>
				<h1 class="text-2xl font-bold text-gray-900 dark:text-white">
					{$t('worker.add')}
				</h1>
				<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
					{$t('worker.addDescription')}
				</p>
			</div>

			<!-- Worker Form -->
			<WorkerForm 
				on:submit={handleSubmit}
				on:cancel={handleCancel}
			/>
		</div>
	</div>
</div>