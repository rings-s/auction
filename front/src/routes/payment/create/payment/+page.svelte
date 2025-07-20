<!-- src/routes/create/payment/+page.svelte -->
<script>
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import { toast } from '$lib/stores/toastStore.svelte.js';
	import { createPayment } from '$lib/api/payment';
	import PaymentForm from '$lib/components/property-management/payments/PaymentForm.svelte';
	import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';

	// Breadcrumb items
	let breadcrumbItems = [
		{ label: $t('nav.home'), href: '/' },
		{ label: $t('nav.dashboard'), href: '/dashboard' },
		{ label: $t('payment.payments'), href: '/dashboard/payments' },
		{ label: $t('payment.add'), href: '/create/payment', active: true }
	];

	// Handle form submission
	async function handleSubmit(event) {
		try {
			const payment = await createPayment(event.detail);
			toast.success($t('payment.createSuccess'));
			goto('/dashboard/payments');
		} catch (error) {
			toast.error($t('payment.createError'));
		}
	}

	// Handle form cancel
	function handleCancel() {
		goto('/dashboard/payments');
	}
</script>

<svelte:head>
	<title>{$t('payment.add')} - {$t('app.name')}</title>
	<meta name="description" content={$t('payment.addDescription')} />
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<div class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
		<div class="space-y-6">
			<!-- Breadcrumb -->
			<Breadcrumb items={breadcrumbItems} />
			
			<!-- Page Header -->
			<div>
				<h1 class="text-2xl font-bold text-gray-900 dark:text-white">
					{$t('payment.add')}
				</h1>
				<p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
					{$t('payment.addDescription')}
				</p>
			</div>

			<!-- Payment Form -->
			<PaymentForm 
				on:submit={handleSubmit}
				on:cancel={handleCancel}
			/>
		</div>
	</div>
</div>