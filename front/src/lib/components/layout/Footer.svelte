<!-- src/lib/components/layout/Footer.svelte -->
<script>
	import { t, locale } from '$lib/i18n';
	import { onMount } from 'svelte';

	let currentYear = new Date().getFullYear();
	let mounted = false;

	onMount(() => {
		mounted = true;
	});

	// Quick links organized by category
	const quickLinks = [
		{ name: $t('nav.home'), href: '/' },
		{ name: $t('nav.properties'), href: '/properties' },
		{ name: $t('nav.auctions'), href: '/auctions' },
		{ name: $t('nav.about'), href: '/about' }
	];

	const supportLinks = [
		{ name: $t('footer.help'), href: '/help' },
		{ name: $t('nav.contact'), href: '/contact' },
		{ name: $t('footer.faq'), href: '/faq' },
		{ name: $t('footer.support'), href: '/support' }
	];

	const legalLinks = [
		{ name: $t('footer.privacy'), href: '/privacy' },
		{ name: $t('footer.terms'), href: '/terms' },
		{ name: $t('footer.cookies'), href: '/cookies' }
	];
</script>

<footer
	class="relative border-t border-gray-200/50 bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:border-gray-700/50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900"
>
	<!-- Decorative background elements -->
	<div class="pointer-events-none absolute inset-0 overflow-hidden">
		<div
			class="from-primary-100/30 to-secondary-100/30 dark:from-primary-900/20 dark:to-secondary-900/20 absolute -top-40 -right-40 h-80 w-80 rounded-full bg-gradient-to-br blur-3xl"
		></div>
		<div
			class="from-success-100/30 to-primary-100/30 dark:from-success-900/20 dark:to-primary-900/20 absolute -bottom-40 -left-40 h-80 w-80 rounded-full bg-gradient-to-tr blur-3xl"
		></div>
	</div>

	<div class="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
		<!-- Main footer content -->
		<div class="py-16 lg:py-20">
			<div class="grid grid-cols-1 gap-12 lg:grid-cols-12 lg:gap-8">
				<!-- Brand section -->
				<div class="space-y-6 lg:col-span-4">
					<div class="space-y-4">
						<a href="/" class="group inline-block">
							<h2
								class="from-primary-600 via-secondary-600 to-success-600 bg-gradient-to-r bg-clip-text text-3xl font-bold text-transparent transition-transform duration-300 group-hover:scale-105"
							>
								RealEstate
							</h2>
						</a>
						<p class="max-w-md text-lg leading-relaxed text-gray-600 dark:text-gray-300">
							{$t('footer.aboutText')}
						</p>
					</div>

					<!-- Contact info with enhanced styling -->
					<div class="space-y-4">
						<div class="group flex items-start space-x-3">
							<div
								class="from-primary-500 to-secondary-500 flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br transition-transform duration-300 group-hover:scale-105"
							>
								<svg
									class="h-5 w-5 text-white"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
									/>
								</svg>
							</div>
							<div>
								<p class="text-sm font-medium text-gray-500 dark:text-gray-400">Email</p>
								<a
									href="mailto:info@realestate.com"
									class="hover:text-primary-600 dark:hover:text-primary-400 text-gray-700 transition-colors duration-300 dark:text-gray-300"
								>
									info@realestate.com
								</a>
							</div>
						</div>

						<div class="group flex items-start space-x-3">
							<div
								class="from-secondary-500 to-success-500 flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br transition-transform duration-300 group-hover:scale-105"
							>
								<svg
									class="h-5 w-5 text-white"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
									/>
								</svg>
							</div>
							<div>
								<p class="text-sm font-medium text-gray-500 dark:text-gray-400">Phone</p>
								<a
									href="tel:+15551234567"
									class="hover:text-primary-600 dark:hover:text-primary-400 text-gray-700 transition-colors duration-300 dark:text-gray-300"
								>
									+1 (555) 123-4567
								</a>
							</div>
						</div>

						<div class="group flex items-start space-x-3">
							<div
								class="from-success-500 to-primary-500 flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br transition-transform duration-300 group-hover:scale-105"
							>
								<svg
									class="h-5 w-5 text-white"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
									/>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
									/>
								</svg>
							</div>
							<div>
								<p class="text-sm font-medium text-gray-500 dark:text-gray-400">Address</p>
								<address class="text-gray-700 not-italic dark:text-gray-300">
									123 Main Street<br />
									New York, NY 10001<br />
									United States
								</address>
							</div>
						</div>
					</div>
				</div>

				<!-- Links sections -->
				<div class="lg:col-span-8">
					<div class="grid grid-cols-1 gap-8 sm:grid-cols-3 lg:gap-12">
						<!-- Quick Links -->
						<div class="space-y-6">
							<h3 class="relative text-lg font-bold text-gray-900 dark:text-white">
								{$t('footer.quickLinks')}
								<span
									class="from-primary-500 to-secondary-500 absolute -bottom-2 left-0 h-0.5 w-12 rounded-full bg-gradient-to-r"
								></span>
							</h3>
							<ul class="space-y-3">
								{#each quickLinks as link}
									<li>
										<a
											href={link.href}
											class="hover:text-primary-600 dark:hover:text-primary-400 group flex items-center text-gray-600 transition-all duration-300 dark:text-gray-400"
										>
											<span
												class="bg-primary-500 mr-0 h-0.5 w-0 rounded-full transition-all duration-300 group-hover:mr-2 group-hover:w-2"
											></span>
											{link.name}
										</a>
									</li>
								{/each}
							</ul>
						</div>

						<!-- Support -->
						<div class="space-y-6">
							<h3 class="relative text-lg font-bold text-gray-900 dark:text-white">
								{$t('footer.support')}
								<span
									class="from-secondary-500 to-success-500 absolute -bottom-2 left-0 h-0.5 w-12 rounded-full bg-gradient-to-r"
								></span>
							</h3>
							<ul class="space-y-3">
								{#each supportLinks as link}
									<li>
										<a
											href={link.href}
											class="hover:text-secondary-600 dark:hover:text-secondary-400 group flex items-center text-gray-600 transition-all duration-300 dark:text-gray-400"
										>
											<span
												class="bg-secondary-500 mr-0 h-0.5 w-0 rounded-full transition-all duration-300 group-hover:mr-2 group-hover:w-2"
											></span>
											{link.name}
										</a>
									</li>
								{/each}
							</ul>
						</div>

						<!-- Legal -->
						<div class="space-y-6">
							<h3 class="relative text-lg font-bold text-gray-900 dark:text-white">
								{$t('footer.legal')}
								<span
									class="from-success-500 to-primary-500 absolute -bottom-2 left-0 h-0.5 w-12 rounded-full bg-gradient-to-r"
								></span>
							</h3>
							<ul class="space-y-3">
								{#each legalLinks as link}
									<li>
										<a
											href={link.href}
											class="hover:text-success-600 dark:hover:text-success-400 group flex items-center text-gray-600 transition-all duration-300 dark:text-gray-400"
										>
											<span
												class="bg-success-500 mr-0 h-0.5 w-0 rounded-full transition-all duration-300 group-hover:mr-2 group-hover:w-2"
											></span>
											{link.name}
										</a>
									</li>
								{/each}
							</ul>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Newsletter section -->
		<div class="border-t border-gray-200/50 py-8 dark:border-gray-700/50">
			<div class="mx-auto max-w-4xl space-y-6 text-center">
				<div class="space-y-2">
					<h3 class="text-2xl font-bold text-gray-900 dark:text-white">
						{$t('footer.newsletter.title')}
					</h3>
					<p class="mx-auto max-w-2xl text-gray-600 dark:text-gray-400">
						{$t('footer.newsletter.description')}
					</p>
				</div>

				<form class="mx-auto flex max-w-md flex-col gap-3 sm:flex-row">
					<input
						type="email"
						placeholder={$t('footer.newsletter.placeholder')}
						class="focus:ring-primary-500 flex-1 rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 placeholder-gray-500 transition-all duration-300 focus:border-transparent focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder-gray-400"
						required
					/>
					<button
						type="submit"
						class="from-primary-600 to-secondary-600 hover:from-primary-700 hover:to-secondary-700 focus:ring-primary-500 rounded-lg bg-gradient-to-r px-6 py-3 font-medium text-white transition-all duration-300 hover:scale-105 hover:shadow-lg focus:ring-2 focus:ring-offset-2"
					>
						{$t('footer.newsletter.subscribe')}
					</button>
				</form>
			</div>
		</div>

		<!-- Bottom section -->
		<div class="border-t border-gray-200/50 py-8 dark:border-gray-700/50">
			<div class="flex flex-col items-center justify-between space-y-6 lg:flex-row lg:space-y-0">
				<!-- Copyright -->
				<div class="flex flex-col items-center space-y-2 sm:flex-row sm:space-y-0 sm:space-x-6">
					<p class="text-sm text-gray-500 dark:text-gray-400">
						&copy; {currentYear} RealEstate. {$t('footer.rights')}
					</p>
					<p class="text-sm text-gray-500 dark:text-gray-400">
						{$t('footer.madeBy')}
						<span class="font-medium text-gray-700 dark:text-gray-300">Ahmed Bashir Ali</span>
					</p>
				</div>

				<!-- Social links -->
				<div class="flex items-center space-x-4">
					<p class="mr-2 text-sm text-gray-500 dark:text-gray-400">
						{$t('footer.followUs')}
					</p>

					<!-- Facebook -->
					<a
						href="/"
						class="group rounded-lg bg-gray-100 p-2 transition-all duration-300 hover:bg-blue-50 dark:bg-gray-800 dark:hover:bg-blue-900/30"
						aria-label="Facebook"
					>
						<svg
							class="h-5 w-5 text-gray-600 transition-colors duration-300 group-hover:text-blue-600 dark:text-gray-400 dark:group-hover:text-blue-400"
							fill="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"
							/>
						</svg>
					</a>

					<!-- Twitter -->
					<a
						href="/"
						class="group rounded-lg bg-gray-100 p-2 transition-all duration-300 hover:bg-blue-50 dark:bg-gray-800 dark:hover:bg-blue-900/30"
						aria-label="Twitter"
					>
						<svg
							class="h-5 w-5 text-gray-600 transition-colors duration-300 group-hover:text-blue-500 dark:text-gray-400 dark:group-hover:text-blue-400"
							fill="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"
							/>
						</svg>
					</a>

					<!-- Instagram -->
					<a
						href="/"
						class="group rounded-lg bg-gray-100 p-2 transition-all duration-300 hover:bg-pink-50 dark:bg-gray-800 dark:hover:bg-pink-900/30"
						aria-label="Instagram"
					>
						<svg
							class="h-5 w-5 text-gray-600 transition-colors duration-300 group-hover:text-pink-600 dark:text-gray-400 dark:group-hover:text-pink-400"
							fill="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 6.62 5.367 11.987 11.988 11.987 6.62 0 11.987-5.367 11.987-11.987C24.014 5.367 18.637.001 12.017.001zM8.449 16.988c-1.297 0-2.448-.49-3.323-1.297C4.198 14.895 3.708 13.744 3.708 12.447s.49-2.448 1.418-3.323C6.001 8.198 7.152 7.708 8.449 7.708s2.448.49 3.323 1.416c.875.926 1.365 2.077 1.365 3.374s-.49 2.448-1.365 3.323c-.875.807-2.026 1.167-3.323 1.167zm7.718 0c-1.297 0-2.448-.49-3.323-1.297-.875-.926-1.365-2.077-1.365-3.374s.49-2.448 1.365-3.323c.875-.926 2.026-1.416 3.323-1.416s2.448.49 3.323 1.416c.875.875 1.365 2.026 1.365 3.323s-.49 2.448-1.365 3.374c-.875.807-2.026 1.297-3.323 1.297z"
							/>
						</svg>
					</a>

					<!-- LinkedIn -->
					<a
						href="/"
						class="group rounded-lg bg-gray-100 p-2 transition-all duration-300 hover:bg-blue-50 dark:bg-gray-800 dark:hover:bg-blue-900/30"
						aria-label="LinkedIn"
					>
						<svg
							class="h-5 w-5 text-gray-600 transition-colors duration-300 group-hover:text-blue-700 dark:text-gray-400 dark:group-hover:text-blue-400"
							fill="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"
							/>
						</svg>
					</a>

					<!-- YouTube -->
					<a
						href="/"
						class="group rounded-lg bg-gray-100 p-2 transition-all duration-300 hover:bg-red-50 dark:bg-gray-800 dark:hover:bg-red-900/30"
						aria-label="YouTube"
					>
						<svg
							class="h-5 w-5 text-gray-600 transition-colors duration-300 group-hover:text-red-600 dark:text-gray-400 dark:group-hover:text-red-400"
							fill="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"
							/>
						</svg>
					</a>
				</div>
			</div>
		</div>
	</div>
</footer>
