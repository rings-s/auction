<!-- src/lib/components/layout/Footer.svelte -->
<script>
	import { t, language } from '$lib/i18n';

	const currentYear = new Date().getFullYear();
</script>

<footer class="mt-auto py-8" style="z-index: 10;">
	<div class="container mx-auto px-4 sm:px-6 lg:px-8">
		<div class="border-cosmos-bg-light border-t pt-8">
			<div class="flex flex-col items-center justify-between md:flex-row">
				<div class="mb-4 md:mb-0">
					<a href="/" class="text-cosmos-text text-lg font-bold">
						{$t('general.app_name')}
					</a>
					<p class="text-cosmos-text-muted mt-2 text-sm">
						© {currentYear}
						{$t('general.app_name')}. {$t('navigation.rights')}
					</p>
				</div>

				<div class="flex space-x-6 {$language === 'ar' ? 'space-x-reverse' : ''}">
					<a href="/" class="text-cosmos-text-muted hover:text-cosmos-text transition">
						{$t('navigation.home')}
					</a>
					<a href="/auctions" class="text-cosmos-text-muted hover:text-cosmos-text transition">
						{$t('navigation.auctions')}
					</a>
					<a href="/properties" class="text-cosmos-text-muted hover:text-cosmos-text transition">
						{$t('navigation.properties')}
					</a>
					<a href="/about" class="text-cosmos-text-muted hover:text-cosmos-text transition">
						{$t('navigation.about')}
					</a>
					<a href="/contact" class="text-cosmos-text-muted hover:text-cosmos-text transition">
						{$t('navigation.contact')}
					</a>
				</div>
			</div>
		</div>
	</div>
</footer>
