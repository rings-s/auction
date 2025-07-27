<!-- src/lib/components/ui/AccessibleFormField.svelte -->
<script>
	import { createEventDispatcher } from 'svelte';
	import { t } from '$lib/i18n';

	// Props
	export let id = '';
	export let type = 'text';
	export let label = '';
	export let value = '';
	export let placeholder = '';
	export let required = false;
	export let disabled = false;
	export let error = null;
	export let helpText = null;
	export let options = []; // For select inputs
	export let rows = 3; // For textarea
	export let min = null;
	export let max = null;
	export let step = null;
	export let autocomplete = null;
	export let pattern = null;
	export let maxlength = null;
	export let readonly = false;
	export let multiple = false; // For select multiple
	export let accept = null; // For file inputs
	export let size = 'medium'; // 'small' | 'medium' | 'large'
	export let variant = 'default'; // 'default' | 'success' | 'error' | 'warning'
	export let leftIcon = null;
	export let rightIcon = null;
	export let loading = false;

	const dispatch = createEventDispatcher();

	// Generate unique IDs if not provided
	$: fieldId = id || `field-${Math.random().toString(36).substr(2, 9)}`;
	$: errorId = `${fieldId}-error`;
	$: helpId = `${fieldId}-help`;

	// Determine input classes based on size, variant, and state
	$: inputClasses = getInputClasses(size, variant, error, disabled, leftIcon, rightIcon);

	function getInputClasses(size, variant, error, disabled, leftIcon, rightIcon) {
		const baseClasses = 'block w-full border rounded-md shadow-sm transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white';
		
		// Size classes
		const sizeClasses = {
			small: 'px-2 py-1 text-sm',
			medium: 'px-3 py-2 text-sm',
			large: 'px-4 py-3 text-base'
		};

		// Variant classes
		const variantClasses = {
			default: 'border-gray-300 dark:border-gray-600',
			success: 'border-green-300 focus:border-green-500 focus:ring-green-500 dark:border-green-600',
			error: 'border-red-300 focus:border-red-500 focus:ring-red-500 dark:border-red-600',
			warning: 'border-yellow-300 focus:border-yellow-500 focus:ring-yellow-500 dark:border-yellow-600'
		};

		// State classes
		const stateClasses = error ? 'border-red-500' : disabled ? 'bg-gray-50 text-gray-500 cursor-not-allowed dark:bg-gray-800 dark:text-gray-400' : '';

		// Icon padding
		const iconClasses = leftIcon ? 'pl-10' : rightIcon ? 'pr-10' : '';

		return `${baseClasses} ${sizeClasses[size]} ${error ? variantClasses.error : variantClasses[variant]} ${stateClasses} ${iconClasses}`;
	}

	function handleInput(event) {
		value = event.target.value;
		dispatch('input', event);
	}

	function handleChange(event) {
		value = event.target.value;
		dispatch('change', event);
	}

	function handleBlur(event) {
		dispatch('blur', event);
	}

	function handleFocus(event) {
		dispatch('focus', event);
	}

	function handleKeydown(event) {
		dispatch('keydown', event);
	}
</script>

<div class="form-field">
	<!-- Label -->
	{#if label}
		<label 
			for={fieldId}
			class="block text-sm font-medium mb-2 {required ? 'required' : ''} {
				error ? 'text-red-700 dark:text-red-400' : 'text-gray-700 dark:text-gray-300'
			}"
		>
			{label}
			{#if required}
				<span class="text-red-500 ml-1" aria-label={$t('form.required')}>*</span>
			{/if}
		</label>
	{/if}

	<!-- Input Container -->
	<div class="relative">
		<!-- Left Icon -->
		{#if leftIcon}
			<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
				<span class="text-gray-400 dark:text-gray-500">
					{@html leftIcon}
				</span>
			</div>
		{/if}

		<!-- Input Element -->
		{#if type === 'textarea'}
			<textarea
				{id}={fieldId}
				bind:value
				{placeholder}
				{required}
				{disabled}
				{readonly}
				{maxlength}
				{rows}
				{autocomplete}
				class={inputClasses}
				aria-invalid={error ? 'true' : 'false'}
				aria-describedby="{error ? errorId : ''} {helpText ? helpId : ''}".trim()
				on:input={handleInput}
				on:change={handleChange}
				on:blur={handleBlur}
				on:focus={handleFocus}
				on:keydown={handleKeydown}
			></textarea>
		{:else if type === 'select'}
			<select
				{id}={fieldId}
				bind:value
				{required}
				{disabled}
				{multiple}
				class={inputClasses}
				aria-invalid={error ? 'true' : 'false'}
				aria-describedby="{error ? errorId : ''} {helpText ? helpId : ''}".trim()
				on:change={handleChange}
				on:blur={handleBlur}
				on:focus={handleFocus}
			>
				{#if placeholder && !multiple}
					<option value="" disabled selected hidden>{placeholder}</option>
				{/if}
				{#each options as option}
					<option value={option.value} disabled={option.disabled || false}>
						{option.label}
					</option>
				{/each}
			</select>
		{:else if type === 'checkbox'}
			<div class="flex items-center">
				<input
					{id}={fieldId}
					type="checkbox"
					bind:checked={value}
					{required}
					{disabled}
					class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded {
						error ? 'border-red-500' : ''
					}"
					aria-invalid={error ? 'true' : 'false'}
					aria-describedby="{error ? errorId : ''} {helpText ? helpId : ''}".trim()
					on:change={handleChange}
					on:blur={handleBlur}
					on:focus={handleFocus}
				/>
				{#if label}
					<label for={fieldId} class="ml-2 block text-sm text-gray-900 dark:text-gray-100">
						{label}
						{#if required}
							<span class="text-red-500 ml-1" aria-label={$t('form.required')}>*</span>
						{/if}
					</label>
				{/if}
			</div>
		{:else if type === 'radio'}
			<div class="space-y-2" role="radiogroup" aria-labelledby={label ? `${fieldId}-legend` : undefined}>
				{#if label}
					<legend id="{fieldId}-legend" class="sr-only">{label}</legend>
				{/if}
				{#each options as option, index}
					<div class="flex items-center">
						<input
							id="{fieldId}-{index}"
							type="radio"
							bind:group={value}
							value={option.value}
							{required}
							{disabled}
							class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 {
								error ? 'border-red-500' : ''
							}"
							aria-invalid={error ? 'true' : 'false'}
							aria-describedby="{error ? errorId : ''} {helpText ? helpId : ''}".trim()
							on:change={handleChange}
							on:blur={handleBlur}
							on:focus={handleFocus}
						/>
						<label for="{fieldId}-{index}" class="ml-2 block text-sm text-gray-900 dark:text-gray-100">
							{option.label}
						</label>
					</div>
				{/each}
			</div>
		{:else}
			<input
				{id}={fieldId}
				{type}
				bind:value
				{placeholder}
				{required}
				{disabled}
				{readonly}
				{min}
				{max}
				{step}
				{pattern}
				{maxlength}
				{autocomplete}
				{accept}
				class={inputClasses}
				aria-invalid={error ? 'true' : 'false'}
				aria-describedby="{error ? errorId : ''} {helpText ? helpId : ''}".trim()
				on:input={handleInput}
				on:change={handleChange}
				on:blur={handleBlur}
				on:focus={handleFocus}
				on:keydown={handleKeydown}
			/>
		{/if}

		<!-- Right Icon -->
		{#if rightIcon}
			<div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
				<span class="text-gray-400 dark:text-gray-500">
					{@html rightIcon}
				</span>
			</div>
		{/if}

		<!-- Loading Spinner -->
		{#if loading}
			<div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
				<svg class="animate-spin h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24">
					<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
					<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
				</svg>
			</div>
		{/if}
	</div>

	<!-- Help Text -->
	{#if helpText}
		<p id={helpId} class="mt-1 text-xs text-gray-500 dark:text-gray-400">
			{helpText}
		</p>
	{/if}

	<!-- Error Message -->
	{#if error}
		<p id={errorId} class="mt-1 text-sm text-red-600 dark:text-red-400" role="alert" aria-live="polite">
			{error}
		</p>
	{/if}
</div>

<style>
	.required::after {
		content: " *";
		color: #ef4444;
	}

	/* Focus styles for better accessibility */
	.form-field input:focus,
	.form-field textarea:focus,
	.form-field select:focus {
		outline: 2px solid transparent;
		outline-offset: 2px;
	}

	/* High contrast mode support */
	@media (prefers-contrast: high) {
		.form-field input,
		.form-field textarea,
		.form-field select {
			border-width: 2px;
		}
	}

	/* Reduced motion support */
	@media (prefers-reduced-motion: reduce) {
		.form-field input,
		.form-field textarea,
		.form-field select {
			transition: none;
		}
	}
</style>