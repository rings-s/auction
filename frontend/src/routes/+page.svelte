<script>
	import { onMount } from 'svelte';
	import PropertyCard from '$lib/components/properties/PropertyCard.svelte';
	import AuctionCard from '$lib/components/auctions/AuctionCard.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import propertiesService from '$lib/services/property';
	import auctionsService from '$lib/services/auction';

	// State
	let featuredProperties = [];
	let activeAuctions = [];
	let isLoadingProperties = true;
	let isLoadingAuctions = true;

	// Load data
	onMount(async () => {
		try {
			// Load featured properties
			const propertiesResponse = await propertiesService.getProperties({
				is_featured: true,
				limit: 4
			});
			featuredProperties = propertiesResponse.results || [];
			isLoadingProperties = false;

			// Load active auctions
			const auctionsResponse = await auctionsService.getAuctions({
				status: 'active',
				sort_by: 'end_date',
				order: 'asc',
				limit: 4
			});
			activeAuctions = auctionsResponse.results || [];
			isLoadingAuctions = false;
		} catch (error) {
			console.error('Error loading home page data:', error);
			isLoadingProperties = false;
			isLoadingAuctions = false;
		}
	});
</script>

<svelte:head>
	<title>منصة المزادات العقارية - الرئيسية</title>
</svelte:head>

<!-- Hero Section -->
<section class="from-primary-700 to-primary-900 bg-gradient-to-br px-4 py-16 text-black sm:py-24">
	<div class="mx-auto max-w-6xl text-center">
		<h1 class="mb-6 text-3xl font-bold md:text-5xl">المنصة الأولى للمزادات العقارية</h1>
		<p class="mx-auto mb-8 max-w-3xl text-lg md:text-xl">
			استثمر في العقار بثقة وشفافية من خلال منصتنا المتخصصة في المزادات العقارية. فرص استثمارية
			متنوعة بأسعار تنافسية.
		</p>
		<div class="flex flex-col justify-center gap-4 sm:flex-row">
			<Button href="/properties" variant="white" size="lg">تصفح العقارات</Button>
			<Button href="/auctions" variant="light" size="lg">المزادات النشطة</Button>
		</div>
	</div>
</section>

<!-- How it Works Section -->
<section class="bg-white px-4 py-12 md:py-16">
	<div class="mx-auto max-w-6xl">
		<h2 class="mb-12 text-center text-2xl font-bold md:text-3xl">كيف تعمل المنصة؟</h2>

		<div class="grid grid-cols-1 gap-8 md:grid-cols-3">
			<div class="text-center">
				<div
					class="bg-primary-100 text-primary-600 mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="h-8 w-8"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
						/>
					</svg>
				</div>
				<h3 class="mb-2 text-xl font-semibold">ابحث عن العقار المناسب</h3>
				<p class="text-gray-600">
					تصفح مجموعة متنوعة من العقارات المتاحة للمزاد واختر ما يناسب احتياجاتك واستثماراتك.
				</p>
			</div>

			<div class="text-center">
				<div
					class="bg-primary-100 text-primary-600 mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="h-8 w-8"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"
						/>
					</svg>
				</div>
				<h3 class="mb-2 text-xl font-semibold">قدم عرضك في المزاد</h3>
				<p class="text-gray-600">
					شارك في المزادات المباشرة وقدم عروضك بكل سهولة وأمان عبر المنصة الإلكترونية.
				</p>
			</div>

			<div class="text-center">
				<div
					class="bg-primary-100 text-primary-600 mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="h-8 w-8"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
				</div>
				<h3 class="mb-2 text-xl font-semibold">أتمم الصفقة بأمان</h3>
				<p class="text-gray-600">
					بعد الفوز بالمزاد، أكمل عملية الشراء بكل سهولة مع ضمان حقوقك القانونية والعقارية.
				</p>
			</div>
		</div>
	</div>
</section>

<!-- Featured Properties Section -->
<section class="bg-gray-50 px-4 py-12">
	<div class="mx-auto max-w-6xl">
		<div class="mb-8 flex items-center justify-between">
			<h2 class="text-2xl font-bold md:text-3xl">العقارات المميزة</h2>
			<Button href="/properties" variant="link">عرض المزيد</Button>
		</div>

		{#if isLoadingProperties}
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
				{#each Array(4) as _}
					<div class="h-72 animate-pulse rounded-lg bg-white shadow"></div>
				{/each}
			</div>
		{:else if featuredProperties.length > 0}
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
				{#each featuredProperties as property (property.id)}
					<PropertyCard {property} />
				{/each}
			</div>
		{:else}
			<div class="py-8 text-center">
				<p class="text-gray-500">لا توجد عقارات مميزة حالياً</p>
			</div>
		{/if}
	</div>
</section>

<!-- Active Auctions Section -->
<section class="bg-white px-4 py-12">
	<div class="mx-auto max-w-6xl">
		<div class="mb-8 flex items-center justify-between">
			<h2 class="text-2xl font-bold md:text-3xl">المزادات النشطة</h2>
			<Button href="/auctions" variant="link">عرض المزيد</Button>
		</div>

		{#if isLoadingAuctions}
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
				{#each Array(4) as _}
					<div class="h-72 animate-pulse rounded-lg bg-white shadow"></div>
				{/each}
			</div>
		{:else if activeAuctions.length > 0}
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
				{#each activeAuctions as auction (auction.id)}
					<AuctionCard {auction} />
				{/each}
			</div>
		{:else}
			<div class="py-8 text-center">
				<p class="text-gray-500">لا توجد مزادات نشطة حالياً</p>
			</div>
		{/if}
	</div>
</section>

<!-- Benefits Section -->
<section class="bg-gray-50 px-4 py-12">
	<div class="mx-auto max-w-6xl">
		<h2 class="mb-12 text-center text-2xl font-bold md:text-3xl">لماذا تختار منصتنا؟</h2>

		<div class="grid grid-cols-1 gap-8 md:grid-cols-2">
			<div class="shadow-card rounded-lg bg-white p-6">
				<div class="flex items-start">
					<div class="bg-success-100 text-success-600 ml-4 rounded-lg p-3">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="h-6 w-6"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
							/>
						</svg>
					</div>
					<div>
						<h3 class="mb-2 text-lg font-semibold">ضمان وموثوقية</h3>
						<p class="text-gray-600">
							جميع العقارات معتمدة ومفحوصة قانونياً وفنياً، مع ضمان صحة الوثائق والمستندات.
						</p>
					</div>
				</div>
			</div>

			<div class="shadow-card rounded-lg bg-white p-6">
				<div class="flex items-start">
					<div class="bg-success-100 text-success-600 ml-4 rounded-lg p-3">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="h-6 w-6"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
					</div>
					<div>
						<h3 class="mb-2 text-lg font-semibold">أسعار تنافسية</h3>
						<p class="text-gray-600">
							تتيح المزادات العلنية الحصول على أفضل الأسعار التنافسية، وفرص استثمارية حقيقية.
						</p>
					</div>
				</div>
			</div>

			<div class="shadow-card rounded-lg bg-white p-6">
				<div class="flex items-start">
					<div class="bg-success-100 text-success-600 ml-4 rounded-lg p-3">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="h-6 w-6"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"
							/>
						</svg>
					</div>
					<div>
						<h3 class="mb-2 text-lg font-semibold">دعم متكامل</h3>
						<p class="text-gray-600">
							فريق متخصص من الخبراء العقاريين والقانونيين متاح لمساعدتك في جميع مراحل عملية الشراء.
						</p>
					</div>
				</div>
			</div>

			<div class="shadow-card rounded-lg bg-white p-6">
				<div class="flex items-start">
					<div class="bg-success-100 text-success-600 ml-4 rounded-lg p-3">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="h-6 w-6"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
					</div>
					<div>
						<h3 class="mb-2 text-lg font-semibold">توفير الوقت والجهد</h3>
						<p class="text-gray-600">
							منصة إلكترونية متكاملة تتيح لك المشاركة في المزادات والمتابعة من أي مكان وفي أي وقت.
						</p>
					</div>
				</div>
			</div>
		</div>
	</div>
</section>

<!-- CTA Section -->
<section class="bg-primary-800 px-4 py-16 text-white">
	<div class="mx-auto max-w-5xl text-center">
		<h2 class="mb-4 text-2xl font-bold md:text-3xl">ابدأ الاستثمار العقاري اليوم</h2>
		<p class="mx-auto mb-8 max-w-2xl">
			انضم إلى آلاف المستثمرين والمشترين الذين يستفيدون من فرص المزادات العقارية. سجل الآن وابدأ
			رحلتك.
		</p>
		<div class="flex flex-col justify-center gap-4 sm:flex-row">
			<Button href="/register" variant="white" size="lg">إنشاء حساب جديد</Button>
			<Button href="/contact" variant="outline-white" size="lg">تواصل معنا</Button>
		</div>
	</div>
</section>
