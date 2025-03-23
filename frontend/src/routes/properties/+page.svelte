<!-- routes/properties/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { t } from '$lib/i18n';
    import { fade } from 'svelte/transition';
    import { browser } from '$app/environment';
    
    // UI Components
    import PropertyGrid from '$lib/components/properties/PropertyGrid.svelte';
    import Alert from '$lib/components/ui/Alert.svelte';
    import LoadingIndicator from '$lib/components/ui/LoadingIndicator.svelte';
    
    // State
    let loading = true;
    let initialFilters = {};
    let title = $t('properties.all_properties');
    
    // Handle URL parameters to initialize filters
    onMount(() => {
        if (browser && $page.url.searchParams) {
            // Extract filter parameters from URL
            const params = $page.url.searchParams;
            
            initialFilters = {
                property_type: params.get('property_type') || '',
                status: params.get('status') || '',
                city: params.get('city') || '',
                district: params.get('district') || '',
                bedrooms: params.get('bedrooms') || '',
                bathrooms: params.get('bathrooms') || '',
                min_price: params.get('min_price') || '',
                max_price: params.get('max_price') || '',
                min_area: params.get('min_area') || '',
                max_area: params.get('max_area') || '',
                sort_by: params.get('sort_by') || 'created_at',
                order: params.get('order') || 'desc'
            };
            
            // Set title based on filters
            if (initialFilters.property_type) {
                // Translate property type from key to display name
                const propertyTypes = {
                    'land': $t('properties.types.land'),
                    'apartment': $t('properties.types.apartment'), 
                    'villa': $t('properties.types.villa'),
                    'commercial': $t('properties.types.commercial'),
                    'building': $t('properties.types.building'),
                    'farm': $t('properties.types.farm'),
                    'industrial': $t('properties.types.industrial'),
                    'office': $t('properties.types.office'),
                    'retail': $t('properties.types.retail'),
                    'mixed_use': $t('properties.types.mixed_use')
                };
                
                title = propertyTypes[initialFilters.property_type] || $t('properties.all_properties');
                
                if (initialFilters.city) {
                    title += ` ${$t('properties.in')} ${initialFilters.city}`;
                }
            } else if (initialFilters.city) {
                title = `${$t('properties.properties_in')} ${initialFilters.city}`;
            }
        }
        
        loading = false;
    });
</script>

<svelte:head>
    <title>{title} | {$t('site.name')}</title>
    <meta name="description" content={$t('properties.meta_description')} />
</svelte:head>

<div class="min-h-screen bg-cosmos-bg pb-12">
    <!-- Hero Section -->
    <div class="bg-gradient-to-b from-cosmos-bg-dark to-cosmos-bg py-12">
        <div class="container mx-auto px-4">
            <div class="max-w-2xl">
                <h1 class="text-3xl font-bold text-cosmos-text md:text-4xl">{title}</h1>
                <p class="mt-2 text-cosmos-text-muted">
                    {$t('properties.browse_description')}
                </p>
            </div>
        </div>
    </div>
    
    <!-- Main Content -->
    <div class="container mx-auto px-4 py-8">
        {#if loading}
            <div class="flex justify-center py-12">
                <LoadingIndicator size="lg" />
            </div>
        {:else}
            <div in:fade={{ duration: 300 }}>
                <PropertyGrid 
                    {initialFilters}
                    showFilters={true}
                    title=""
                />
            </div>
        {/if}
    </div>
    
    <!-- Feature Callout -->
    <div class="container mx-auto mt-8 px-4">
        <div class="rounded-xl bg-cosmos-bg-light bg-opacity-10 p-8 backdrop-blur-sm">
            <div class="grid grid-cols-1 gap-8 md:grid-cols-3">
                <div class="text-center">
                    <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary bg-opacity-10">
                        <svg class="h-8 w-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </div>
                    <h3 class="mt-4 text-lg font-medium text-cosmos-text">{$t('properties.feature.search_title')}</h3>
                    <p class="mt-2 text-cosmos-text-muted">{$t('properties.feature.search_description')}</p>
                </div>
                
                <div class="text-center">
                    <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary bg-opacity-10">
                        <svg class="h-8 w-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
                        </svg>
                    </div>
                    <h3 class="mt-4 text-lg font-medium text-cosmos-text">{$t('properties.feature.compare_title')}</h3>
                    <p class="mt-2 text-cosmos-text-muted">{$t('properties.feature.compare_description')}</p>
                </div>
                
                <div class="text-center">
                    <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary bg-opacity-10">
                        <svg class="h-8 w-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                        </svg>
                    </div>
                    <h3 class="mt-4 text-lg font-medium text-cosmos-text">{$t('properties.feature.auction_title')}</h3>
                    <p class="mt-2 text-cosmos-text-muted">{$t('properties.feature.auction_description')}</p>
                </div>
            </div>
        </div>
    </div>
</div>