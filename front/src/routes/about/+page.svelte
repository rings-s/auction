<!-- src/routes/about/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { locale } from '$lib/i18n';
	import Button from '$lib/components/ui/Button.svelte';

	let mounted = false;
	let scrollY = 0;
	let prefersReducedMotion = false;

	// RTL support
	$: isRTL = $locale === 'ar';

	// Content structure
	const content = {
		en: {
			hero: {
				title: "We're building the future of real estate",
				description:
					'Our platform transforms how people buy, sell, and invest in properties through transparent auctions and cutting-edge technology.',
				stats: [
					{ number: '50K+', label: 'Properties Listed' },
					{ number: '98%', label: 'Success Rate' },
					{ number: '15', label: 'Countries' }
				]
			},
			story: {
				title: 'Our Story',
				content:
					'Born from a vision to democratize real estate investing, we started with a simple belief: everyone should have access to transparent property transactions. What began as a small team in 2019 has grown into a global platform serving thousands of satisfied customers.',
				highlight:
					'We believe in transparency, innovation, and building trust through every interaction.'
			},
			values: {
				title: 'What drives us',
				items: [
					{
						icon: 'transparency',
						title: 'Transparency First',
						description: 'Every bid, every transaction, every detail - open and verifiable.'
					},
					{
						icon: 'innovation',
						title: 'Innovation Always',
						description: 'Pushing boundaries with technology to simplify complex processes.'
					},
					{
						icon: 'trust',
						title: 'Trust Through Action',
						description: 'Building lasting relationships by delivering on our promises.'
					}
				]
			},
			team: {
				title: 'Leadership',
				subtitle: 'Guided by experience, driven by purpose',
				members: [
					{
						name: 'Sarah Chen',
						role: 'CEO & Co-founder',
						bio: '20+ years in proptech',
						image: 'sarah'
					},
					{
						name: 'Marcus Johnson',
						role: 'CTO & Co-founder',
						bio: 'Former Google engineer',
						image: 'marcus'
					},
					{
						name: 'Elena Rodriguez',
						role: 'Head of Operations',
						bio: 'Real estate veteran',
						image: 'elena'
					}
				]
			},
			cta: {
				title: 'Ready to join our journey?',
				description: 'Experience the future of real estate auctions today.',
				primaryBtn: 'Get Started',
				secondaryBtn: 'Talk to Sales'
			}
		},
		ar: {
			hero: {
				title: 'نبني مستقبل العقارات',
				description:
					'منصتنا تحول كيفية شراء وبيع والاستثمار في العقارات من خلال المزادات الشفافة والتكنولوجيا المتطورة.',
				stats: [
					{ number: '+50ألف', label: 'عقار مدرج' },
					{ number: '98%', label: 'معدل النجاح' },
					{ number: '15', label: 'دولة' }
				]
			},
			story: {
				title: 'قصتنا',
				content:
					'وُلدت من رؤية لإضفاء الطابع الديمقراطي على الاستثمار العقاري، بدأنا بإيمان بسيط: يجب أن يتمتع الجميع بإمكانية الوصول إلى معاملات عقارية شفافة. ما بدأ كفريق صغير في 2019 نما إلى منصة عالمية تخدم آلاف العملاء الراضين.',
				highlight: 'نؤمن بالشفافية والابتكار وبناء الثقة من خلال كل تفاعل.'
			},
			values: {
				title: 'ما يحركنا',
				items: [
					{
						icon: 'transparency',
						title: 'الشفافية أولاً',
						description: 'كل عرض، كل معاملة، كل تفصيل - مفتوح وقابل للتحقق.'
					},
					{
						icon: 'innovation',
						title: 'الابتكار دائماً',
						description: 'دفع الحدود بالتكنولوجيا لتبسيط العمليات المعقدة.'
					},
					{
						icon: 'trust',
						title: 'الثقة من خلال العمل',
						description: 'بناء علاقات دائمة من خلال الوفاء بوعودنا.'
					}
				]
			},
			team: {
				title: 'القيادة',
				subtitle: 'موجهون بالخبرة، مدفوعون بالهدف',
				members: [
					{
						name: 'سارة تشين',
						role: 'الرئيس التنفيذي والمؤسس المشارك',
						bio: '20+ سنة في تقنية العقارات',
						image: 'sarah'
					},
					{
						name: 'ماركوس جونسون',
						role: 'المدير التقني والمؤسس المشارك',
						bio: 'مهندس سابق في جوجل',
						image: 'marcus'
					},
					{ name: 'إيلينا رودريغيز', role: 'رئيس العمليات', bio: 'خبيرة عقارات', image: 'elena' }
				]
			},
			cta: {
				title: 'مستعد للانضمام إلى رحلتنا؟',
				description: 'جرب مستقبل مزادات العقارات اليوم.',
				primaryBtn: 'ابدأ الآن',
				secondaryBtn: 'تحدث إلى المبيعات'
			}
		}
	};

	function getText(path) {
		const lang = $locale || 'en';
		const keys = path.split('.');
		let value = content[lang] || content.en;

		for (const key of keys) {
			value = value?.[key];
			if (!value) return path;
		}
		return value;
	}

	onMount(() => {
		mounted = true;

		if (typeof window !== 'undefined') {
			const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
			prefersReducedMotion = mediaQuery.matches;

			mediaQuery.addEventListener('change', (e) => {
				prefersReducedMotion = e.matches;
			});
		}
	});
</script>

<svelte:head>
	<title>About Us | Transforming Real Estate Through Innovation</title>
	<meta
		name="description"
		content="Learn about our mission to democratize real estate through transparent auctions and innovative technology."
	/>
</svelte:head>

<svelte:window bind:scrollY />

<div
	class="relative overflow-hidden bg-gradient-to-b from-white via-purple-50/20 to-white dark:from-gray-900 dark:via-purple-950/20 dark:to-gray-900"
	dir={isRTL ? 'rtl' : 'ltr'}
>
	{#if mounted}
		<!-- Hero Section with Modern Design -->
		<section class="relative flex min-h-screen items-center py-20 sm:py-24 lg:py-32">
			<!-- Background Decoration -->
			<div class="pointer-events-none absolute inset-0 overflow-hidden">
				<div
					class="absolute top-20 left-0 h-96 w-96 rounded-full bg-purple-200/30 blur-3xl dark:bg-purple-800/20"
				></div>
				<div
					class="absolute right-0 bottom-20 h-96 w-96 rounded-full bg-blue-200/30 blur-3xl dark:bg-blue-800/20"
				></div>
			</div>

			<div class="relative z-10 mx-auto w-full max-w-7xl px-6 sm:px-8 lg:px-12">
				<div class="grid grid-cols-1 items-center gap-12 lg:grid-cols-12 lg:gap-16">
					<!-- Left Content -->
					<div class="space-y-8 lg:col-span-5">
						<h1
							in:fly={{ y: prefersReducedMotion ? 0 : 30, duration: 800, delay: 200 }}
							class="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-5xl leading-[0.95] font-black tracking-tight text-transparent sm:text-6xl lg:text-7xl"
						>
							{getText('hero.title')}
						</h1>

						<p
							in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 800, delay: 300 }}
							class="max-w-md text-lg leading-relaxed text-gray-600 dark:text-gray-300"
						>
							{getText('hero.description')}
						</p>

						<!-- Stats with Modern Cards -->
						<div
							in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 800, delay: 400 }}
							class="grid grid-cols-3 gap-4"
						>
							{#each getText('hero.stats') as stat, i}
								<div
									class="rounded-2xl border border-purple-200/50 bg-white/80 p-4 text-center shadow-lg backdrop-blur-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl dark:border-purple-700/50 dark:bg-gray-800/80"
								>
									<div
										class="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-2xl font-black text-transparent lg:text-3xl"
									>
										{stat.number}
									</div>
									<div class="mt-1 text-xs text-gray-600 lg:text-sm dark:text-gray-400">
										{stat.label}
									</div>
								</div>
							{/each}
						</div>
					</div>

					<!-- Right Visual - Modern Property Illustration -->
					<div class="relative lg:col-span-7">
						<div
							in:scale={{ duration: 1000, delay: 500, easing: 'cubicOut' }}
							class="relative mx-auto aspect-square w-full max-w-lg"
						>
							<svg viewBox="0 0 400 400" class="h-full w-full">
								<defs>
									<linearGradient id="purpleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
										<stop
											offset="0%"
											class="text-purple-400"
											stop-color="currentColor"
											stop-opacity="0.8"
										/>
										<stop
											offset="100%"
											class="text-blue-500"
											stop-color="currentColor"
											stop-opacity="0.6"
										/>
									</linearGradient>
									<linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="100%">
										<stop offset="0%" class="text-purple-600" stop-color="currentColor" />
										<stop offset="100%" class="text-blue-600" stop-color="currentColor" />
									</linearGradient>
									<filter id="glow">
										<feGaussianBlur stdDeviation="4" result="coloredBlur" />
										<feMerge>
											<feMergeNode in="coloredBlur" />
											<feMergeNode in="SourceGraphic" />
										</feMerge>
									</filter>
								</defs>

								<!-- Modern Building Complex -->
								<g
									stroke="url(#purpleGrad)"
									stroke-width="2"
									fill="none"
									stroke-linecap="round"
									stroke-linejoin="round"
									filter="url(#glow)"
								>
									<!-- Main Building -->
									<path d="M150 350 L150 150 Q200 120 250 150 L250 350" class="animate-draw" />

									<!-- Windows -->
									{#each Array(4) as _, i}
										<rect
											x={170 + (i % 2) * 40}
											y={180 + Math.floor(i / 2) * 50}
											width="20"
											height="30"
											class="animate-draw"
											style="animation-delay: {0.5 + i * 0.1}s"
										/>
									{/each}

									<!-- Side Building -->
									<path
										d="M100 350 L100 200 L150 180 L150 350"
										class="animate-draw"
										style="animation-delay: 0.8s"
									/>

									<!-- Auction Gavel -->
									<g stroke="url(#accentGrad)" stroke-width="3">
										<line
											x1="280"
											y1="120"
											x2="320"
											y2="80"
											class="animate-draw"
											style="animation-delay: 1.2s"
										/>
										<rect
											x="270"
											y="115"
											width="20"
											height="10"
											rx="2"
											class="animate-draw"
											style="animation-delay: 1.3s"
										/>
									</g>

									<!-- Floating Elements -->
									<circle
										cx="320"
										cy="200"
										r="30"
										stroke="url(#accentGrad)"
										fill="url(#accentGrad)"
										fill-opacity="0.1"
										class="animate-pulse"
									/>
									<circle
										cx="80"
										cy="150"
										r="20"
										stroke="url(#accentGrad)"
										fill="url(#accentGrad)"
										fill-opacity="0.1"
										class="animate-pulse"
										style="animation-delay: 0.5s"
									/>
								</g>
							</svg>
						</div>
					</div>
				</div>
			</div>
		</section>

		<!-- Story Section with Timeline -->
		<section class="relative overflow-hidden py-24 lg:py-32">
			<div
				class="absolute inset-0 bg-gradient-to-b from-purple-50/30 via-transparent to-blue-50/30 dark:from-purple-950/20 dark:via-transparent dark:to-blue-950/20"
			></div>

			<div class="relative mx-auto max-w-7xl px-6 sm:px-8 lg:px-12">
				<!-- Section Header -->
				<div class="mb-16 text-center">
					<h2
						in:fly={{ y: prefersReducedMotion ? 0 : -20, duration: 800, delay: 100 }}
						class="mb-4 text-4xl font-black text-gray-900 md:text-5xl dark:text-white"
					>
						{getText('story.title')}
					</h2>
					<div
						class="mx-auto h-1 w-24 rounded-full bg-gradient-to-r from-purple-500 to-blue-500"
					></div>
				</div>

				<!-- Story Content -->
				<div class="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
					<!-- Timeline -->
					<div
						in:fly={{ x: prefersReducedMotion ? 0 : -30, duration: 800, delay: 200 }}
						class="space-y-8"
					>
						<!-- Timeline Items -->
						<div class="relative border-l-2 border-purple-300 pl-8 dark:border-purple-700">
							{#each [{ year: '2019', text: 'Founded with a vision' }, { year: '2021', text: 'Global expansion' }, { year: 'Today', text: 'Industry leader' }] as item, i}
								<div class="relative mb-8 last:mb-0">
									<div class="absolute top-0 -left-[9px] h-4 w-4 rounded-full bg-purple-500"></div>
									<h3 class="mb-2 text-xl font-bold text-purple-600 dark:text-purple-400">
										{item.year}
									</h3>
									<p class="text-gray-600 dark:text-gray-300">{item.text}</p>
								</div>
							{/each}
						</div>
					</div>

					<!-- Content Card -->
					<div
						in:fly={{ x: prefersReducedMotion ? 0 : 30, duration: 800, delay: 300 }}
						class="rounded-3xl border border-purple-200/50 bg-white p-8 shadow-2xl backdrop-blur-sm lg:p-10 dark:border-purple-700/50 dark:bg-gray-800"
					>
						<p class="mb-6 text-lg leading-relaxed text-gray-700 dark:text-gray-300">
							{getText('story.content')}
						</p>

						<blockquote
							class="rounded-2xl border-l-4 border-purple-500 bg-gradient-to-r from-purple-50 to-blue-50 p-6 dark:from-purple-900/20 dark:to-blue-900/20"
						>
							<p class="text-lg text-gray-800 italic dark:text-gray-200">
								{getText('story.highlight')}
							</p>
						</blockquote>
					</div>
				</div>
			</div>
		</section>

		<!-- Values Section -->
		<section class="relative py-24 lg:py-32">
			<div class="mx-auto max-w-7xl px-6 sm:px-8 lg:px-12">
				<div class="mb-16 text-center">
					<h2
						in:fly={{ y: prefersReducedMotion ? 0 : -20, duration: 800, delay: 100 }}
						class="mb-4 text-4xl font-black text-gray-900 md:text-5xl dark:text-white"
					>
						{getText('values.title')}
					</h2>
					<div
						class="mx-auto h-1 w-24 rounded-full bg-gradient-to-r from-purple-500 to-blue-500"
					></div>
				</div>

				<div class="grid grid-cols-1 gap-8 md:grid-cols-3">
					{#each getText('values.items') as value, i}
						<div
							in:scale={{ duration: 600, delay: 200 + i * 100, easing: 'cubicOut' }}
							class="group relative rounded-3xl border border-purple-200/50 bg-white p-8 shadow-xl transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl dark:border-purple-700/50 dark:bg-gray-800"
						>
							<!-- Icon -->
							<div
								class="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-purple-500 to-blue-500 text-white"
							>
								{#if value.icon === 'transparency'}
									<svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
										/>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
										/>
									</svg>
								{:else if value.icon === 'innovation'}
									<svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M13 10V3L4 14h7v7l9-11h-7z"
										/>
									</svg>
								{:else}
									<svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
										/>
									</svg>
								{/if}
							</div>

							<h3 class="mb-3 text-xl font-bold text-gray-900 dark:text-white">
								{value.title}
							</h3>

							<p class="text-gray-600 dark:text-gray-300">
								{value.description}
							</p>

							<!-- Decorative gradient line -->
							<div
								class="absolute right-0 bottom-0 left-0 h-1 rounded-b-3xl bg-gradient-to-r from-purple-500 to-blue-500 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
							></div>
						</div>
					{/each}
				</div>
			</div>
		</section>

		<!-- Team Section -->
		<section
			class="relative bg-gradient-to-b from-purple-50/30 to-transparent py-24 lg:py-32 dark:from-purple-950/20 dark:to-transparent"
		>
			<div class="mx-auto max-w-7xl px-6 sm:px-8 lg:px-12">
				<div class="mb-16 text-center">
					<h2
						in:fly={{ y: prefersReducedMotion ? 0 : -20, duration: 800, delay: 100 }}
						class="mb-2 text-4xl font-black text-gray-900 md:text-5xl dark:text-white"
					>
						{getText('team.title')}
					</h2>
					<p class="text-lg text-gray-600 dark:text-gray-400">
						{getText('team.subtitle')}
					</p>
				</div>

				<div class="grid grid-cols-1 gap-8 md:grid-cols-3">
					{#each getText('team.members') as member, i}
						<div
							in:scale={{ duration: 600, delay: 200 + i * 100, easing: 'cubicOut' }}
							class="text-center"
						>
							<div class="relative mx-auto mb-6 h-40 w-40">
								<div
									class="flex h-full w-full items-center justify-center rounded-full bg-gradient-to-br from-purple-400 to-blue-500 text-4xl font-bold text-white"
								>
									{member.name
										.split(' ')
										.map((n) => n[0])
										.join('')}
								</div>
							</div>

							<h3 class="mb-1 text-xl font-bold text-gray-900 dark:text-white">
								{member.name}
							</h3>
							<p class="mb-2 font-medium text-purple-600 dark:text-purple-400">
								{member.role}
							</p>
							<p class="text-gray-600 dark:text-gray-400">
								{member.bio}
							</p>
						</div>
					{/each}
				</div>
			</div>
		</section>

		<!-- CTA Section -->
		<section class="relative py-24 lg:py-32">
			<div class="mx-auto max-w-4xl px-6 sm:px-8 lg:px-12">
				<div
					in:scale={{ duration: 800, delay: 100, easing: 'cubicOut' }}
					class="relative overflow-hidden rounded-3xl bg-gradient-to-br from-purple-600 to-blue-600 p-12 text-center lg:p-16"
				>
					<!-- Background Pattern -->
					<div class="absolute inset-0 opacity-10">
						<svg class="h-full w-full" viewBox="0 0 400 400">
							<pattern id="dots" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
								<circle cx="20" cy="20" r="2" fill="currentColor" />
							</pattern>
							<rect width="100%" height="100%" fill="url(#dots)" />
						</svg>
					</div>

					<div class="relative z-10">
						<h2 class="mb-6 text-3xl font-black text-white sm:text-4xl lg:text-5xl">
							{getText('cta.title')}
						</h2>

						<p class="mx-auto mb-10 max-w-2xl text-lg text-white/90 lg:text-xl">
							{getText('cta.description')}
						</p>

						<div class="flex flex-col justify-center gap-4 sm:flex-row">
							<Button
								variant="primary"
								size="large"
								href="/register"
								class="rounded-xl bg-white px-8 py-4 font-bold text-purple-600 shadow-xl transition-all duration-300 hover:bg-gray-100 hover:shadow-2xl"
							>
								{getText('cta.primaryBtn')}
							</Button>

							<Button
								variant="outline"
								size="large"
								href="/contact"
								class="rounded-xl border-2 border-white px-8 py-4 font-bold text-white transition-all duration-300 hover:bg-white hover:text-purple-600"
							>
								{getText('cta.secondaryBtn')}
							</Button>
						</div>
					</div>
				</div>
			</div>
		</section>
	{/if}
</div>

<style>
	@keyframes draw {
		from {
			stroke-dasharray: 1000;
			stroke-dashoffset: 1000;
			opacity: 0;
		}
		to {
			stroke-dasharray: 1000;
			stroke-dashoffset: 0;
			opacity: 1;
		}
	}

	.animate-draw {
		animation: draw 2s ease-out forwards;
		stroke-dasharray: 1000;
		stroke-dashoffset: 1000;
		opacity: 0;
	}

	.animate-pulse {
		animation: pulse 3s ease-in-out infinite;
	}

	@keyframes pulse {
		0%,
		100% {
			opacity: 0.1;
			transform: scale(1);
		}
		50% {
			opacity: 0.3;
			transform: scale(1.05);
		}
	}

	/* Respect reduced motion */
	@media (prefers-reduced-motion: reduce) {
		.animate-draw {
			animation: none;
			stroke-dasharray: none;
			stroke-dashoffset: 0;
			opacity: 1;
		}

		.animate-pulse {
			animation: none;
		}
	}
</style>
