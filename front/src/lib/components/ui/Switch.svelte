<!-- src/lib/components/Switch.svelte -->
<script>
	import { createEventDispatcher } from 'svelte';
	import { fade, fly } from 'svelte/transition';

	// Props
	export let id = crypto.randomUUID(); // Generate random ID if not provided
	export let checked = false;
	export let disabled = false;
	export let label = '';
	export let description = '';
	export let size = 'default'; // 'small', 'default', 'large'
	export let variant = 'primary'; // 'primary', 'success', 'danger', 'warning', 'custom'
	export let customColors = { bg: '', dot: '' }; // For custom variant
	export let labelPosition = 'right'; // 'right', 'left'
	export let srOnly = false; // Screen reader only label
	export let name = '';
	export let value = '';
	export let required = false;
	export let hideLabel = false; // Hide label but keep for screen readers
	export let animate = true; // Enable animations
	export let icon = null; // Optional icon for switch (SVG string)
	export let showIcons = false; // Show check/x icons in the switch

	// Event handling
	const dispatch = createEventDispatcher();

	// Size variants calculations
	$: switchHeight = size === 'small' ? 'h-5' : size === 'large' ? 'h-7' : 'h-6';
	$: switchWidth = size === 'small' ? 'w-9' : size === 'large' ? 'w-14' : 'w-11';
	$: dotSize = size === 'small' ? 'h-3.5 w-3.5' : size === 'large' ? 'h-5 w-5' : 'h-4 w-4';
	$: dotTranslate =
		size === 'small' ? 'translate-x-4' : size === 'large' ? 'translate-x-7' : 'translate-x-5';
	$: labelSize = size === 'small' ? 'text-xs' : size === 'large' ? 'text-base' : 'text-sm';
	$: descriptionSize = size === 'small' ? 'text-xs' : size === 'large' ? 'text-sm' : 'text-xs';

	// Color variants
	$: bgOn =
		variant === 'primary'
			? 'bg-primary-600 dark:bg-primary-500'
			: variant === 'success'
				? 'bg-success-600 dark:bg-success-500'
				: variant === 'danger'
					? 'bg-danger-600 dark:bg-danger-500'
					: variant === 'warning'
						? 'bg-warning-500 dark:bg-warning-400'
						: variant === 'custom'
							? customColors.bg
							: 'bg-primary-600 dark:bg-primary-500';

	$: bgOff = 'bg-gray-200 dark:bg-gray-700';

	$: dotColor =
		variant === 'primary'
			? 'bg-white'
			: variant === 'success'
				? 'bg-white'
				: variant === 'danger'
					? 'bg-white'
					: variant === 'warning'
						? 'bg-white'
						: variant === 'custom'
							? customColors.dot
							: 'bg-white';

	// Focus ring color
	$: focusRingColor =
		variant === 'primary'
			? 'focus:ring-primary-500 dark:focus:ring-primary-400'
			: variant === 'success'
				? 'focus:ring-success-500 dark:focus:ring-success-400'
				: variant === 'danger'
					? 'focus:ring-danger-500 dark:focus:ring-danger-400'
					: variant === 'warning'
						? 'focus:ring-warning-500 dark:focus:ring-warning-400'
						: 'focus:ring-primary-500 dark:focus:ring-primary-400';

	// Determine if label should be visually hidden
	$: labelClass =
		hideLabel || srOnly ? 'sr-only' : `font-medium ${labelSize} text-gray-700 dark:text-gray-300`;

	// Toggle switch state
	function toggleSwitch() {
		if (!disabled) {
			checked = !checked;
			dispatch('change', checked);
		}
	}

	// Handle keyboard interaction
	function handleKeyDown(event) {
		if (!disabled && (event.key === 'Enter' || event.key === ' ')) {
			event.preventDefault();
			toggleSwitch();
		}
	}
</script>

<div
	class="flex items-center {labelPosition === 'left'
		? 'flex-row-reverse justify-end'
		: 'justify-start'} gap-3"
>
	<!-- Switch Control -->
	<button
		type="button"
		role="switch"
		{id}
		aria-checked={checked}
		aria-disabled={disabled}
		tabindex={disabled ? '-1' : '0'}
		class="{switchWidth} {switchHeight} relative inline-flex flex-shrink-0 rounded-full border-2 border-transparent
             transition-colors duration-200 ease-in-out
             {checked ? bgOn : bgOff}
             {disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}
             focus:outline-none {focusRingColor} focus:ring-2 focus:ring-offset-2"
		on:click={toggleSwitch}
		on:keydown={handleKeyDown}
	>
		<span class="sr-only">{label || 'Toggle'}</span>

		<!-- Animated Dot -->
		<span
			aria-hidden="true"
			class="{dotSize} rounded-full {dotColor} transform shadow ring-0 transition duration-200 ease-in-out
               {checked ? dotTranslate : 'translate-x-0'}
               flex items-center justify-center"
		>
			{#if checked && showIcons}
				<svg
					class={`${size === 'small' ? 'h-2 w-2' : size === 'large' ? 'h-3 w-3' : 'h-2.5 w-2.5'} text-primary-600`}
					fill="currentColor"
					viewBox="0 0 20 20"
				>
					<path
						fill-rule="evenodd"
						d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
						clip-rule="evenodd"
					></path>
				</svg>
			{:else if !checked && showIcons}
				<svg
					class={`${size === 'small' ? 'h-2 w-2' : size === 'large' ? 'h-3 w-3' : 'h-2.5 w-2.5'} text-gray-600`}
					fill="currentColor"
					viewBox="0 0 20 20"
				>
					<path
						fill-rule="evenodd"
						d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
						clip-rule="evenodd"
					></path>
				</svg>
			{:else if icon}
				<span
					class={`${size === 'small' ? 'h-2 w-2' : size === 'large' ? 'h-3 w-3' : 'h-2.5 w-2.5'}`}
				>
					{@html icon}
				</span>
			{/if}
		</span>

		<!-- Background Icons -->
		{#if showIcons}
			<span
				class="pointer-events-none absolute inset-0 flex items-center justify-between p-1 opacity-70"
			>
				<span class={`${size === 'small' ? 'ml-0.5' : size === 'large' ? 'ml-1.5' : 'ml-1'}`}>
					<svg
						class={`${size === 'small' ? 'h-2 w-2' : size === 'large' ? 'h-3 w-3' : 'h-2.5 w-2.5'} text-white`}
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 20 20"
						fill="currentColor"
					>
						<path
							fill-rule="evenodd"
							d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
							clip-rule="evenodd"
						/>
					</svg>
				</span>
				<span class={`${size === 'small' ? 'mr-0.5' : size === 'large' ? 'mr-1.5' : 'mr-1'}`}>
					<svg
						class={`${size === 'small' ? 'h-2 w-2' : size === 'large' ? 'h-3 w-3' : 'h-2.5 w-2.5'} text-gray-300 dark:text-gray-600`}
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 20 20"
						fill="currentColor"
					>
						<path
							fill-rule="evenodd"
							d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
							clip-rule="evenodd"
						/>
					</svg>
				</span>
			</span>
		{/if}
	</button>

	<!-- Label and Description -->
	{#if label || description}
		<div
			class={`flex flex-col ${labelPosition === 'left' ? 'mr-2 items-end' : 'ml-0 items-start'}`}
		>
			{#if label}
				<span class={labelClass}>
					{label}
					{#if required}
						<span class="text-danger-500 dark:text-danger-400 ml-0.5">*</span>
					{/if}
				</span>
			{/if}

			{#if description}
				<span
					class="text-gray-500 dark:text-gray-400 {descriptionSize} {hideLabel || srOnly
						? 'mt-0'
						: 'mt-0.5'}"
					id={`${id}-description`}
				>
					{description}
				</span>
			{/if}
		</div>
	{/if}

	<!-- Hidden real input for form submission -->
	{#if name}
		<input type="checkbox" {name} {value} {required} {checked} {disabled} class="sr-only" />
	{/if}
</div>

<style>
	/* Custom transition utility classes */
	button[role='switch'] {
		transition-property:
			background-color, border-color, color, fill, stroke, opacity, box-shadow, transform;
		will-change: transform;
	}

	/* Improved focus styles for Windows High Contrast mode */
	@media (forced-colors: active) {
		button[role='switch']:focus {
			outline: 2px solid transparent;
			outline-offset: 2px;
		}
	}
</style>
