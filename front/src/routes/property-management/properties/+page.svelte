<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';
	import { userStore } from '$lib/stores/user.svelte.js';
	import PropertyList from '$lib/components/property-management/PropertyList.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';

	$: user = $userStore;

	// Check if user has permission to access property management
	$: hasAccess =
		(user && ['owner', 'appraiser', 'data_entry'].includes(user.role)) || user?.is_superuser;

	onMount(() => {
		if (!hasAccess) {
			goto('/dashboard');
			return;
		}
	});

	// Event handlers for the property list component
	function handleViewProperty(event) {
		goto(`/property-management/properties/${event.detail.property.id}`);
	}

	function handleEditProperty(event) {
		goto(`/property-management/properties/${event.detail.property.id}/edit`);
	}

	function handleViewTenants(event) {
		goto(`/property-management/tenants?property=${event.detail.property.id}`);
	}

	function handleViewMaintenance(event) {
		goto(`/property-management/maintenance?property=${event.detail.property.id}`);
	}

	function handleViewExpenses(event) {
		goto(`/property-management/expenses?property=${event.detail.property.id}`);
	}

	function handleCreateProperty() {
		goto('/property-management/properties/create');
	}
</script>

<svelte:head>
	<title
		>{$t('propertyManagement.properties')} | {$t('propertyManagement.title')} | {$t(
			'app.name'
		)}</title
	>
	<meta name="description" content={$t('propertyManagement.propertiesDescription')} />
</svelte:head>

<!-- Access Control -->
{#if !hasAccess}
	<div class="flex min-h-screen items-center justify-center">
		<Alert type="error" message={$t('errors.accessDenied')} />
	</div>
{:else}
	<div class="container mx-auto px-4 py-8">
		<!-- Breadcrumb -->
		<nav class="mb-6">
			<ol class="flex items-center space-x-2 text-sm text-gray-600">
				<li>
					<a href="/property-management" class="hover:text-blue-600"
						>{$t('propertyManagement.title')}</a
					>
				</li>
				<li class="flex items-center">
					<svg class="mx-1 h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
						<path
							fill-rule="evenodd"
							d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
							clip-rule="evenodd"
						/>
					</svg>
					<span class="font-medium text-gray-900">{$t('propertyManagement.properties')}</span>
				</li>
			</ol>
		</nav>

		<!-- Property Management List Component -->
		<PropertyList
			on:viewProperty={handleViewProperty}
			on:editProperty={handleEditProperty}
			on:createProperty={handleCreateProperty}
		/>
	</div>
{/if}
