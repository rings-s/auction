<script>
	import { t } from '$lib/i18n';
	import { theme, effectiveTheme, systemTheme } from './ThemeProvider.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import FadeInUp from '$lib/components/animations/FadeInUp.svelte';

	/** @type {'button' | 'dropdown' | 'segmented'} */
	let variant = $props('button');
	/** @type {'sm' | 'md' | 'lg'} */
	let size = $props('md');
	/** @type {boolean} */
	let showLabel = $props(false);
	/** @type {string} */
	let className = $props('');
	/** @type {boolean} */
	let animate = $props(true);


	let showDropdown = $state(false);

	let themeOptions = $derived([
		{
			value: 'light',
			label: () => t('theme.light'),
			icon: '☀️',
			description: () => t('theme.lightDescription')
		},
		{
			value: 'dark',
			label: () => t('theme.dark'),
			icon: '🌙',
			description: () => t('theme.darkDescription')
		},
		{
			value: 'system',
			label: () => t('theme.system'),
			icon: '💻',
			description: () => t('theme.systemDescription')
		}
	]);

	function setTheme(newTheme) {
		theme.set(newTheme);
		if (typeof localStorage !== 'undefined') {
			localStorage.setItem('theme', newTheme);
		}
		showDropdown = false;
	}

	function toggleTheme() {
		if ($theme === 'light') {
			setTheme('dark');
		} else if ($theme === 'dark') {
			setTheme('system');
		} else {
			setTheme('light');
		}
	}

	function getCurrentThemeOption() {
		return themeOptions.find((option) => option.value === $theme) || themeOptions[0];
	}

	function getEffectiveThemeIcon() {
		if ($theme === 'system') {
			return $systemTheme === 'dark' ? '🌙' : '☀️';
		}
		return getCurrentThemeOption().icon;
	}

	function handleClickOutside(event) {
		if (showDropdown && !event.target.closest('.theme-toggle-dropdown')) {
			showDropdown = false;
		}
	}

	function handleKeydown(event) {
		if (event.key === 'Escape') {
			showDropdown = false;
		}
	}

	$effect(() => {
		if (showDropdown) {
			document.addEventListener('click', handleClickOutside);
			document.addEventListener('keydown', handleKeydown);

			return () => {
				document.removeEventListener('click', handleClickOutside);
				document.removeEventListener('keydown', handleKeydown);
			};
		}
	});
</script>

<div class="theme-toggle {className}">
	{#if variant === 'button'}
		<!-- Simple Toggle Button -->
		<Button
			variant="ghost"
			{size}
			on:click={toggleTheme}
			className="theme-toggle-button"
			aria-label={$t('theme.toggle')}
			title={$t('theme.currentTheme', { theme: getCurrentThemeOption().label() })}
		>
			<span class="theme-icon" class:animate>
				{getEffectiveThemeIcon()}
			</span>
			{#if showLabel}
				<span class="theme-label">
					{getCurrentThemeOption().label()}
				</span>
			{/if}
		</Button>
	{:else if variant === 'dropdown'}
		<!-- Dropdown Theme Selector -->
		<div class="theme-toggle-dropdown relative">
			<Button
				variant="ghost"
				{size}
				on:click={() => (showDropdown = !showDropdown)}
				className="dropdown-trigger"
				aria-label={$t('theme.selectTheme')}
				aria-expanded={showDropdown}
				aria-haspopup="menu"
			>
				<span class="theme-icon" class:animate>
					{getEffectiveThemeIcon()}
				</span>
				{#if showLabel}
					<span class="theme-label">
						{getCurrentThemeOption().label()}
					</span>
				{/if}
				<svg
					class="dropdown-arrow"
					class:open={showDropdown}
					width="12"
					height="12"
					viewBox="0 0 12 12"
					fill="none"
				>
					<path
						d="M3 4.5L6 7.5L9 4.5"
						stroke="currentColor"
						stroke-width="1.5"
						stroke-linecap="round"
						stroke-linejoin="round"
					/>
				</svg>
			</Button>

			{#if showDropdown}
				<FadeInUp delay={0}>
					<div class="dropdown-menu" role="menu" aria-label={$t('theme.themeOptions')}>
						{#each themeOptions as option}
							<button
								class="dropdown-item"
								class:active={$theme === option.value}
								on:click={() => setTheme(option.value)}
								role="menuitem"
								aria-checked={$theme === option.value}
							>
								<span class="option-icon">{option.icon}</span>
								<div class="option-content">
									<span class="option-label">{option.label()}</span>
									<span class="option-description">{option.description()}</span>
								</div>
								{#if $theme === option.value}
									<span class="check-icon">✓</span>
								{/if}
							</button>
						{/each}
					</div>
				</FadeInUp>
			{/if}
		</div>
	{:else if variant === 'segmented'}
		<!-- Segmented Control -->
		<div class="segmented-control" role="radiogroup" aria-label={$t('theme.selectTheme')}>
			{#each themeOptions as option}
				<button
					class="segment"
					class:active={$theme === option.value}
					on:click={() => setTheme(option.value)}
					role="radio"
					aria-checked={$theme === option.value}
					title={option.description()}
				>
					<span class="segment-icon" class:animate={$theme === option.value}>
						{option.icon}
					</span>
					{#if showLabel}
						<span class="segment-label">{option.label()}</span>
					{/if}
				</button>
			{/each}
		</div>
	{/if}
</div>

<style>
	.theme-toggle {
		position: relative;
	}

	.theme-icon {
		font-size: 1.25rem;
		transition: transform 300ms cubic-bezier(0.4, 0, 0.2, 1);
	}

	.theme-icon.animate {
		animation: themeChange 600ms cubic-bezier(0.4, 0, 0.2, 1);
	}

	@keyframes themeChange {
		0% {
			transform: rotate(0deg) scale(1);
		}
		50% {
			transform: rotate(180deg) scale(1.2);
		}
		100% {
			transform: rotate(360deg) scale(1);
		}
	}

	.theme-label {
		margin-left: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
	}

	/* Dropdown Styles */
	.dropdown-arrow {
		margin-left: 0.5rem;
		transition: transform 200ms ease-out;
		color: var(--color-muted-foreground);
	}

	.dropdown-arrow.open {
		transform: rotate(180deg);
	}

	.dropdown-menu {
		position: absolute;
		top: 100%;
		right: 0;
		margin-top: 0.5rem;
		background: var(--color-popover);
		border: 1px solid var(--color-border);
		border-radius: 0.75rem;
		box-shadow:
			0 10px 15px -3px rgba(0, 0, 0, 0.1),
			0 4px 6px -2px rgba(0, 0, 0, 0.05);
		min-width: 200px;
		z-index: 50;
		overflow: hidden;
	}

	.dropdown-item {
		display: flex;
		align-items: center;
		width: 100%;
		padding: 0.75rem 1rem;
		border: none;
		background: none;
		text-align: left;
		cursor: pointer;
		transition: background-color 200ms ease-out;
		color: var(--color-popover-foreground);
	}

	.dropdown-item:hover {
		background: var(--color-accent);
	}

	.dropdown-item.active {
		background: var(--color-primary);
		color: var(--color-primary-foreground);
	}

	.option-icon {
		font-size: 1.25rem;
		margin-right: 0.75rem;
		flex-shrink: 0;
	}

	.option-content {
		flex: 1;
		min-width: 0;
	}

	.option-label {
		display: block;
		font-weight: 500;
		font-size: 0.875rem;
		line-height: 1.25;
	}

	.option-description {
		display: block;
		font-size: 0.75rem;
		color: var(--color-muted-foreground);
		margin-top: 0.125rem;
		line-height: 1.2;
	}

	.dropdown-item.active .option-description {
		color: var(--color-primary-foreground);
		opacity: 0.8;
	}

	.check-icon {
		margin-left: 0.5rem;
		color: var(--color-success);
		font-weight: bold;
	}

	.dropdown-item.active .check-icon {
		color: var(--color-primary-foreground);
	}

	/* Segmented Control Styles */
	.segmented-control {
		display: flex;
		background: var(--color-muted);
		border-radius: 0.5rem;
		padding: 0.25rem;
		border: 1px solid var(--color-border);
	}

	.segment {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0.5rem 0.75rem;
		border: none;
		background: none;
		border-radius: 0.375rem;
		cursor: pointer;
		transition: all 200ms ease-out;
		color: var(--color-muted-foreground);
		font-size: 0.875rem;
		flex: 1;
	}

	.segment:hover {
		color: var(--color-foreground);
	}

	.segment.active {
		background: var(--color-background);
		color: var(--color-foreground);
		box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
	}

	.segment-icon {
		font-size: 1rem;
	}

	.segment-label {
		margin-left: 0.375rem;
		font-weight: 500;
	}

	/* Dark mode styles */
	:global([data-theme='dark']) .dropdown-menu {
		box-shadow:
			0 10px 15px -3px rgba(0, 0, 0, 0.3),
			0 4px 6px -2px rgba(0, 0, 0, 0.2);
	}

	/* High contrast mode */
	@media (prefers-contrast: high) {
		.dropdown-menu {
			border-width: 2px;
		}

		.segment {
			border: 1px solid transparent;
		}

		.segment.active {
			border-color: var(--color-foreground);
		}
	}

	/* Reduced motion */
	@media (prefers-reduced-motion: reduce) {
		.theme-icon,
		.dropdown-arrow,
		.dropdown-item,
		.segment {
			transition: none;
		}

		.theme-icon.animate {
			animation: none;
		}
	}

	/* Mobile optimizations */
	@media (max-width: 640px) {
		.dropdown-menu {
			right: auto;
			left: 0;
			width: 100vw;
			max-width: 280px;
		}

		.segment {
			padding: 0.75rem 0.5rem;
		}

		.segment-label {
			display: none;
		}
	}
</style>
