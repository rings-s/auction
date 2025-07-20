<script>
	import { fade, fly, scale } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';
	import { locale } from '$lib/i18n/config.js';

	let mounted = $state(false);
	let scrollY = $state(0);
	let prefersReducedMotion = $state(false);

	// RTL support
	let isRTL = $derived($locale === 'ar');

	// Content structure with translations
	const content = {
		en: {
			hero: {
				badge: 'Trusted by 50K+ Users',
				title: {
					line1: 'Find Your Dream',
					line2: 'Property'
				},
				subtitle:
					'Explore premium real estate opportunities through transparent auctions and direct listings. Your perfect property is just a click away.',
				cta: {
					primary: 'Browse Properties',
					secondary: 'View Auctions'
				},
				stats: [
					{ value: '2.5K+', label: 'Properties' },
					{ value: '847M', label: 'Total Value' },
					{ value: '98%', label: 'Success Rate' },
					{ value: '45+', label: 'Cities' }
				],
				features: {
					verified: 'Verified',
					secure: 'Secure',
					instant: 'Instant'
				}
			}
		},
		ar: {
			hero: {
				badge: 'موثوق من 50ألف+ مستخدم',
				title: {
					line1: 'اعثر على',
					line2: 'عقار أحلامك'
				},
				subtitle:
					'استكشف فرص العقارات المميزة من خلال المزادات الشفافة والقوائم المباشرة. عقارك المثالي على بعد نقرة واحدة.',
				cta: {
					primary: 'تصفح العقارات',
					secondary: 'عرض المزادات'
				},
				stats: [
					{ value: '2.5ألف+', label: 'عقار' },
					{ value: '847م', label: 'القيمة الكلية' },
					{ value: '98%', label: 'معدل النجاح' },
					{ value: '45+', label: 'مدينة' }
				],
				features: {
					verified: 'موثق',
					secure: 'آمن',
					instant: 'فوري'
				}
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

	$effect(() => {
		mounted = true;

		if (typeof window !== 'undefined') {
			const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
			prefersReducedMotion = mediaQuery.matches;

			const handleChange = (e) => {
				prefersReducedMotion = e.matches;
			};

			mediaQuery.addEventListener('change', handleChange);

			return () => {
				mediaQuery.removeEventListener('change', handleChange);
			};
		}
	});
</script>

<svelte:head>
	<title>{isRTL ? 'منصة العقارات المتميزة' : 'Premium Real Estate Platform'}</title>
	<meta name="description" content={getText('hero.subtitle')} />
</svelte:head>

<svelte:window bind:scrollY />

<div class="min-h-screen overflow-hidden bg-gray-50 dark:bg-gray-950" dir={isRTL ? 'rtl' : 'ltr'}>
	{#if mounted}
		<!-- Hero Section -->
		<section class="relative flex min-h-screen items-center">
			<!-- Enhanced Background with Better Dark Mode -->
			<div class="absolute inset-0">
				<div
					class="background-div absolute inset-0"
					style="background: linear-gradient(135deg, 
                 var(--color-neutral-50) 0%, 
                 var(--color-primary-50) 25%, 
                 var(--color-secondary-50) 50%, 
                 var(--color-neutral-50) 100%);"
				></div>
				<div class="absolute inset-0 overflow-hidden">
					<!-- Enhanced Floating Shapes -->
					<div
						class="shape-1 absolute -top-1/3 -left-1/3 h-[80%] w-[80%] rounded-full"
						style="background: radial-gradient(circle at center, 
                   var(--color-primary-300) 0%, 
                   var(--color-primary-500) 50%, 
                   transparent 70%);
                   transform: rotate({scrollY * 0.02}deg) scale(1.2);
                   filter: blur(120px);"
					></div>
					<div
						class="shape-3 absolute -right-1/3 -bottom-1/3 h-[70%] w-[70%] rounded-full"
						style="background: radial-gradient(circle at center, 
                   var(--color-secondary-300) 0%, 
                   var(--color-secondary-500) 50%, 
                   transparent 70%);
                   transform: rotate({-scrollY * 0.02}deg) scale(1.1);
                   filter: blur(100px);"
					></div>
					<!-- Additional shape for depth -->
					<div
						class="shape-2 absolute top-1/2 left-1/2 h-[60%] w-[60%] -translate-x-1/2 -translate-y-1/2 rounded-full"
						style="background: radial-gradient(circle at center, 
                   var(--color-accent-200) 0%, 
                   var(--color-accent-400) 50%, 
                   transparent 70%);
                   transform: rotate({scrollY * 0.01}deg);
                   filter: blur(150px);"
					></div>
				</div>
			</div>

			<!-- Content Container -->
			<div class="relative mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
				<div class="grid grid-cols-1 items-center gap-8 lg:grid-cols-12 lg:gap-12">
					<!-- Left Content - 40% -->
					<div class="space-y-6 lg:col-span-5 lg:space-y-8">
						<!-- Enhanced Trust Badge -->
						<div
							in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 600, delay: 200 }}
							class="from-secondary-100 to-secondary-50 dark:from-secondary-900/30 dark:to-secondary-800/20 border-secondary-300 dark:border-secondary-700 inline-flex items-center gap-2 rounded-full border bg-gradient-to-r px-4 py-2.5 shadow-sm backdrop-blur-sm"
						>
							<div class="bg-secondary-500 h-2 w-2 animate-pulse rounded-full"></div>
							<span class="text-secondary-700 dark:text-secondary-300 text-xs font-semibold">
								{getText('hero.badge')}
							</span>
						</div>

						<!-- Title with Brown Accent -->
						<div class="space-y-2">
							<h1
								in:fly={{ y: prefersReducedMotion ? 0 : 30, duration: 800, delay: 300 }}
								class="text-5xl leading-[0.9] font-black tracking-tight sm:text-6xl lg:text-7xl xl:text-8xl"
							>
								<span class="block text-gray-900 dark:text-white">
									{getText('hero.title.line1')}
								</span>
								<span class="text-secondary-600 dark:text-secondary-400 mt-2 block">
									{getText('hero.title.line2')}
								</span>
							</h1>
						</div>

						<!-- Subtitle -->
						<p
							in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 800, delay: 400 }}
							class="max-w-xl text-base leading-relaxed text-gray-600 lg:text-lg dark:text-gray-300"
						>
							{getText('hero.subtitle')}
						</p>

						<!-- CTA Buttons -->
						<div
							in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 800, delay: 500 }}
							class="flex flex-col gap-3 sm:flex-row"
						>
							<a
								href="/properties"
								class="bg-primary-600 hover:bg-primary-700 inline-flex transform items-center justify-center rounded-xl px-6 py-3 font-medium text-white shadow-lg transition-all duration-200 hover:-translate-y-0.5 hover:shadow-xl"
							>
								{getText('hero.cta.primary')}
								<svg
									class="h-4 w-4 {isRTL ? 'mr-2' : 'ml-2'}"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d={isRTL ? 'M11 19l-7-7 7-7m8 14l-7-7 7-7' : 'M13 5l7 7-7 7M5 12h14'}
									/>
								</svg>
							</a>

							<a
								href="/auctions"
								class="inline-flex transform items-center justify-center rounded-xl border border-gray-200 bg-white px-6 py-3 font-medium text-gray-700 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
							>
								{getText('hero.cta.secondary')}
							</a>
						</div>

						<!-- Stats Grid with Brown Accents -->
						<div
							in:fly={{ y: prefersReducedMotion ? 0 : 20, duration: 800, delay: 600 }}
							class="grid grid-cols-4 gap-4 pt-6"
						>
							{#each getText('hero.stats') as stat, i}
								<div class="text-center">
									<div
										class="text-secondary-600 dark:text-secondary-400 text-xl font-bold sm:text-2xl"
									>
										{stat.value}
									</div>
									<div class="mt-0.5 text-xs text-gray-500 dark:text-gray-400">
										{stat.label}
									</div>
								</div>
							{/each}
						</div>
					</div>

					<!-- Right SVG Animation - 60% -->
					<div class="relative lg:col-span-7">
						<div
							in:scale={{ duration: 1000, delay: 300, easing: cubicOut }}
							class="relative w-full"
						>
							<svg viewBox="0 0 900 800" class="mx-auto h-full w-full max-w-[1000px]">
								<defs>
									<!-- Enhanced Gradients -->
									<linearGradient id="primaryGradient" x1="0%" y1="0%" x2="100%" y2="100%">
										<stop offset="0%" style="stop-color:var(--color-primary-400);stop-opacity:1" />
										<stop
											offset="100%"
											style="stop-color:var(--color-primary-600);stop-opacity:1"
										/>
									</linearGradient>

									<linearGradient id="secondaryGradient" x1="0%" y1="0%" x2="100%" y2="100%">
										<stop
											offset="0%"
											style="stop-color:var(--color-secondary-400);stop-opacity:1"
										/>
										<stop
											offset="100%"
											style="stop-color:var(--color-secondary-600);stop-opacity:1"
										/>
									</linearGradient>

									<linearGradient id="successGradient" x1="0%" y1="0%" x2="100%" y2="100%">
										<stop offset="0%" style="stop-color:var(--color-success-400);stop-opacity:1" />
										<stop
											offset="100%"
											style="stop-color:var(--color-success-600);stop-opacity:1"
										/>
									</linearGradient>

									<linearGradient id="windowGradient" x1="0%" y1="0%" x2="0%" y2="100%">
										<stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.9" />
										<stop offset="100%" style="stop-color:#ffffff;stop-opacity:0.4" />
									</linearGradient>

									<!-- Enhanced Filters -->
									<filter id="softShadow">
										<feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="rgba(0,0,0,0.15)" />
									</filter>

									<filter id="glow">
										<feGaussianBlur stdDeviation="4" result="coloredBlur" />
										<feMerge>
											<feMergeNode in="coloredBlur" />
											<feMergeNode in="SourceGraphic" />
										</feMerge>
									</filter>
								</defs>

								<!-- City Skyline Group -->
								<g transform="translate(450, 400)">
									<!-- Background Buildings -->
									<g opacity="0.15">
										<rect
											x="-380"
											y="-100"
											width="60"
											height="200"
											fill="var(--color-neutral-400)"
										/>
										<rect
											x="-300"
											y="-140"
											width="80"
											height="240"
											fill="var(--color-neutral-400)"
										/>
										<rect
											x="280"
											y="-120"
											width="70"
											height="220"
											fill="var(--color-neutral-400)"
										/>
									</g>

									<!-- Left Office Building -->
									<g filter="url(#softShadow)" transform="translate(-200, 0)">
										<rect
											x="-70"
											y="-160"
											width="140"
											height="310"
											rx="4"
											fill="url(#secondaryGradient)"
										>
											<animateTransform
												attributeName="transform"
												type="translate"
												values="0,0; 0,-8; 0,0"
												dur="8s"
												repeatCount="indefinite"
											/>
										</rect>
										<!-- Windows Grid -->
										<g opacity="0.8">
											{#each Array(15) as _, i}
												<rect
													x={-60 + (i % 3) * 45}
													y={-150 + Math.floor(i / 3) * 55}
													width="35"
													height="45"
													fill="url(#windowGradient)"
													rx="2"
												>
													<animate
														attributeName="opacity"
														values="0.4;0.9;0.6;0.9;0.4"
														dur="6s"
														begin="{i * 0.3}s"
														repeatCount="indefinite"
													/>
												</rect>
											{/each}
										</g>
									</g>

									<!-- Central Tower -->
									<g filter="url(#softShadow)">
										<rect
											x="-80"
											y="-200"
											width="160"
											height="350"
											rx="4"
											fill="url(#primaryGradient)"
										>
											<animateTransform
												attributeName="transform"
												type="translate"
												values="0,0; 0,-10; 0,0"
												dur="7s"
												repeatCount="indefinite"
											/>
										</rect>
										<!-- Window Pattern -->
										<g opacity="0.8">
											{#each Array(18) as _, i}
												<rect
													x={-70 + (i % 3) * 50}
													y={-190 + Math.floor(i / 3) * 55}
													width="40"
													height="45"
													fill="url(#windowGradient)"
													rx="2"
												>
													<animate
														attributeName="opacity"
														values="0.5;1;0.7;1;0.5"
														dur="5s"
														begin="{i * 0.2}s"
														repeatCount="indefinite"
													/>
												</rect>
											{/each}
										</g>
										<!-- Rooftop -->
										<rect
											x="-40"
											y="-210"
											width="80"
											height="10"
											rx="5"
											fill="var(--color-primary-700)"
										/>
										<circle cx="0" cy="-215" r="3" fill="var(--color-danger-500)">
											<animate
												attributeName="opacity"
												values="1;0.2;1"
												dur="2s"
												repeatCount="indefinite"
											/>
										</circle>
									</g>

									<!-- Right Residential Building -->
									<g filter="url(#softShadow)" transform="translate(200, 20)">
										<rect
											x="-60"
											y="-140"
											width="120"
											height="290"
											rx="4"
											fill="url(#successGradient)"
										>
											<animateTransform
												attributeName="transform"
												type="translate"
												values="0,0; 0,-6; 0,0"
												dur="7.5s"
												repeatCount="indefinite"
											/>
										</rect>
										<!-- Balconies and Windows -->
										{#each Array(5) as _, i}
											<g transform="translate(0, {-120 + i * 50})">
												<rect
													x="-50"
													y="0"
													width="100"
													height="3"
													fill="var(--color-success-700)"
													rx="1"
												/>
												<rect
													x="-45"
													y="5"
													width="40"
													height="35"
													fill="url(#windowGradient)"
													rx="2"
													opacity="0.8"
												/>
												<rect
													x="5"
													y="5"
													width="40"
													height="35"
													fill="url(#windowGradient)"
													rx="2"
													opacity="0.8"
												/>
											</g>
										{/each}
									</g>

									<!-- Enhanced Modern Villa (Left Foreground) -->
									<g filter="url(#softShadow)" transform="translate(-320, 100)">
										<!-- Main Structure -->
										<rect
											x="-55"
											y="-35"
											width="110"
											height="75"
											fill="var(--color-neutral-100)"
											rx="4"
										/>
										<!-- Large Glass Windows -->
										<rect
											x="-50"
											y="-30"
											width="45"
											height="55"
											fill="url(#windowGradient)"
											rx="2"
											opacity="0.8"
										/>
										<rect
											x="5"
											y="-30"
											width="45"
											height="55"
											fill="url(#windowGradient)"
											rx="2"
											opacity="0.8"
										/>
										<!-- Modern Flat Roof -->
										<rect x="-55" y="-40" width="110" height="5" fill="var(--color-neutral-700)" />
										<!-- Roof Garden -->
										<rect
											x="-30"
											y="-38"
											width="20"
											height="3"
											fill="var(--color-success-500)"
											rx="1"
										/>
										<rect
											x="10"
											y="-38"
											width="20"
											height="3"
											fill="var(--color-success-500)"
											rx="1"
										/>
										<!-- Entry Door -->
										<rect
											x="-12"
											y="10"
											width="24"
											height="30"
											fill="var(--color-secondary-700)"
											rx="2"
										/>
										<!-- Door Handle -->
										<circle cx="5" cy="25" r="1.5" fill="var(--color-secondary-400)" />
										<!-- Driveway -->
										<rect
											x="-40"
											y="40"
											width="80"
											height="5"
											fill="var(--color-neutral-400)"
											opacity="0.5"
										/>
										<!-- Garden -->
										<ellipse
											cx="-35"
											cy="45"
											rx="15"
											ry="8"
											fill="var(--color-success-300)"
											opacity="0.4"
										/>
										<ellipse
											cx="35"
											cy="45"
											rx="15"
											ry="8"
											fill="var(--color-success-300)"
											opacity="0.4"
										/>
										<!-- Small Trees -->
										<circle cx="-35" cy="40" r="5" fill="var(--color-success-500)" opacity="0.6" />
										<circle cx="35" cy="40" r="5" fill="var(--color-success-500)" opacity="0.6" />
									</g>

									<!-- Enhanced Modern House (Right Foreground) -->
									<g filter="url(#softShadow)" transform="translate(320, 90)">
										<!-- House Base with Pitched Roof -->
										<path
											d="M -60 40 L -60 -20 L 0 -50 L 60 -20 L 60 40 Z"
											fill="url(#secondaryGradient)"
										/>
										<!-- Roof Ridge -->
										<line
											x1="-60"
											y1="-20"
											x2="0"
											y2="-50"
											stroke="var(--color-secondary-700)"
											stroke-width="2"
										/>
										<line
											x1="0"
											y1="-50"
											x2="60"
											y2="-20"
											stroke="var(--color-secondary-700)"
											stroke-width="2"
										/>
										<!-- Chimney -->
										<rect
											x="25"
											y="-40"
											width="15"
											height="25"
											fill="var(--color-secondary-600)"
											rx="1"
										/>
										<!-- Large Windows -->
										<rect
											x="-45"
											y="-10"
											width="35"
											height="40"
											fill="url(#windowGradient)"
											rx="2"
											opacity="0.8"
										/>
										<rect
											x="10"
											y="-10"
											width="35"
											height="40"
											fill="url(#windowGradient)"
											rx="2"
											opacity="0.8"
										/>
										<!-- Window Frames -->
										<line
											x1="-45"
											y1="10"
											x2="-10"
											y2="10"
											stroke="var(--color-secondary-700)"
											stroke-width="1"
										/>
										<line
											x1="10"
											y1="10"
											x2="45"
											y2="10"
											stroke="var(--color-secondary-700)"
											stroke-width="1"
										/>
										<line
											x1="-27.5"
											y1="-10"
											x2="-27.5"
											y2="30"
											stroke="var(--color-secondary-700)"
											stroke-width="1"
										/>
										<line
											x1="27.5"
											y1="-10"
											x2="27.5"
											y2="30"
											stroke="var(--color-secondary-700)"
											stroke-width="1"
										/>
										<!-- Entry Door -->
										<rect
											x="-12"
											y="5"
											width="24"
											height="35"
											fill="var(--color-secondary-800)"
											rx="2"
										/>
										<!-- Door Details -->
										<rect
											x="-10"
											y="10"
											width="20"
											height="15"
											fill="var(--color-secondary-700)"
											rx="1"
											opacity="0.5"
										/>
										<circle cx="6" cy="22" r="1" fill="var(--color-secondary-400)" />
										<!-- Porch -->
										<rect x="-20" y="40" width="40" height="3" fill="var(--color-secondary-600)" />
										<!-- Front Garden -->
										<ellipse
											cx="0"
											cy="48"
											rx="50"
											ry="10"
											fill="var(--color-success-300)"
											opacity="0.3"
										/>
										<!-- Bushes -->
										<ellipse
											cx="-30"
											cy="42"
											rx="8"
											ry="4"
											fill="var(--color-success-500)"
											opacity="0.5"
										/>
										<ellipse
											cx="30"
											cy="42"
											rx="8"
											ry="4"
											fill="var(--color-success-500)"
											opacity="0.5"
										/>
									</g>
								</g>

								<!-- Enhanced Property Info Cards -->
								{#each [{ x: 280, y: 220, price: '$450K', type: 'Villa', delay: '0s' }, { x: 620, y: 200, price: '$2.8M', type: 'Luxury', delay: '1s' }, { x: 400, y: 520, price: '$320K', type: 'Condo', delay: '2s' }, { x: 520, y: 420, price: '$1.2M', type: 'Office', delay: '3s' }] as tag}
									<g transform="translate({tag.x}, {tag.y})">
										<rect
											x="-52"
											y="-18"
											width="104"
											height="36"
											rx="18"
											fill="white"
											stroke="var(--color-gray-200)"
											stroke-width="1"
											filter="url(#softShadow)"
										>
											<animate
												attributeName="y"
												values="-18;-24;-18"
												dur="4s"
												begin={tag.delay}
												repeatCount="indefinite"
											/>
										</rect>
										<text
											x="-35"
											y="6"
											text-anchor="start"
											fill="var(--color-secondary-700)"
											font-size="15"
											font-weight="700"
											font-family="Inter, sans-serif"
										>
											{tag.price}
										</text>
										<text
											x="35"
											y="6"
											text-anchor="end"
											fill="var(--color-gray-600)"
											font-size="13"
											font-weight="500"
											font-family="Inter, sans-serif"
										>
											{tag.type}
										</text>
									</g>
								{/each}

								<!-- Enhanced Feature Badges -->
								<g transform="translate(450, 700)">
									{#each [{ x: -150, feature: 'verified', icon: '✓', color: 'success' }, { x: 0, feature: 'secure', icon: '🔒', color: 'primary' }, { x: 150, feature: 'instant', icon: '⚡', color: 'warning' }] as item, i}
										<g transform="translate({item.x}, 0)">
											<rect
												x="-50"
												y="-16"
												width="100"
												height="32"
												rx="16"
												fill="white"
												stroke="var(--color-{item.color}-300)"
												stroke-width="1.5"
												filter="url(#softShadow)"
											>
												<animate
													attributeName="opacity"
													values="0.9;1;0.9"
													dur="3s"
													begin="{i * 0.5}s"
													repeatCount="indefinite"
												/>
											</rect>
											<!-- Badge Background -->
											<circle cx="-30" cy="0" r="10" fill="var(--color-{item.color}-100)" />
											<text
												x="-30"
												y="6"
												text-anchor="middle"
												font-size="16"
												fill="var(--color-{item.color}-600)"
											>
												{item.icon}
											</text>
											<text
												x="5"
												y="6"
												text-anchor="middle"
												font-size="13"
												fill="var(--color-{item.color}-700)"
												font-weight="600"
												font-family="Inter, sans-serif"
											>
												{getText(`hero.features.${item.feature}`)}
											</text>
										</g>
									{/each}
								</g>

								<!-- Subtle Animated Particles -->
								<g opacity="0.3">
									{#each Array(20) as _, i}
										<circle
											cx={150 + Math.random() * 600}
											cy={100 + Math.random() * 500}
											r={0.5 + Math.random() * 0.5}
											fill="var(--color-primary-400)"
										>
											<animate
												attributeName="opacity"
												values="0;0.8;0"
												dur="{4 + Math.random() * 3}s"
												begin="{Math.random() * 3}s"
												repeatCount="indefinite"
											/>
											<animateTransform
												attributeName="transform"
												type="translate"
												values="0,0; {Math.random() * 20 - 10},{-Math.random() * 30}; 0,0"
												dur="{4 + Math.random() * 3}s"
												begin="{Math.random() * 3}s"
												repeatCount="indefinite"
											/>
										</circle>
									{/each}
								</g>
							</svg>
						</div>
					</div>
				</div>
			</div>
		</section>
	{/if}
</div>

<style>
	.background-div {
		opacity: 0.3;
	}
	:global(.dark) .background-div {
		opacity: 0.05;
	}

	.shape-1 {
		opacity: 0.2;
	}
	:global(.dark) .shape-1 {
		opacity: 0.1;
	}

	.shape-2 {
		opacity: 0.1;
	}
	:global(.dark) .shape-2 {
		opacity: 0.05;
	}

	.shape-3 {
		opacity: 0.2;
	}
	:global(.dark) .shape-3 {
		opacity: 0.1;
	}

	/* Ensure badge text stays within containers */
	text {
		dominant-baseline: middle;
	}

	/* Transform origin for rotation animations */
	:global(.origin-center) {
		transform-origin: center;
	}

	/* Gradient text for secondary color */
	.text-secondary-600 {
		background: linear-gradient(
			135deg,
			var(--color-secondary-500) 0%,
			var(--color-secondary-700) 100%
		);
		background-clip: text;
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
	}

	/* Respect reduced motion */
	@media (prefers-reduced-motion: reduce) {
		.animate-pulse {
			animation: none;
		}
	}

	/* Ensure proper height on mobile */
	@media (max-width: 1024px) {
		section {
			min-height: auto;
			padding-top: 4rem;
			padding-bottom: 4rem;
		}
	}
</style>
