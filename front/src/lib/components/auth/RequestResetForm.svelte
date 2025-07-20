<script>
	import { createEventDispatcher } from 'svelte';
	import { t } from '$lib/i18n';
	import { fly } from 'svelte/transition';

	export let loading = false;
	export let email = '';
	export const success = ''; // External reference only
	export const error = ''; // External reference only

	const dispatch = createEventDispatcher();

	function validateEmail(value) {
		if (!value) return $t('validation.emailRequired');
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		if (!emailRegex.test(value)) return $t('validation.emailInvalid');
		return '';
	}

	let emailError = '';
	let emailTouched = false;

	function handleEmailBlur() {
		emailTouched = true;
		emailError = validateEmail(email);
	}

	function handleSubmit() {
		emailTouched = true;
		emailError = validateEmail(email);

		if (emailError) return;

		dispatch('submit', { email });
	}
</script>

<form class="mt-6 space-y-6" on:submit|preventDefault={handleSubmit}>
	<div>
		<label for="email" class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">
			{$t('auth.email')}
		</label>
		<div class="relative">
			<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
				<svg
					class="h-5 w-5 text-gray-400"
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 20 20"
					fill="currentColor"
				>
					<path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
					<path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
				</svg>
			</div>
			<input
				type="email"
				id="email"
				bind:value={email}
				on:blur={handleEmailBlur}
				required
				class="block w-full appearance-none border px-3 py-3 pl-10
          {emailError && emailTouched
					? 'border-red-300 dark:border-red-600'
					: 'border-gray-300 dark:border-gray-600'} 
          focus:ring-primary-500 focus:border-primary-500 rounded-lg text-gray-900
          placeholder-gray-400 shadow-sm transition-colors duration-200
          focus:ring-2 focus:outline-none dark:bg-gray-700 dark:text-white dark:placeholder-gray-500"
				placeholder="email@example.com"
			/>
		</div>
		{#if emailError && emailTouched}
			<p class="mt-1 text-sm text-red-600 dark:text-red-400" in:fly={{ y: -5, duration: 200 }}>
				{emailError}
			</p>
		{/if}
	</div>

	<div class="flex flex-col space-y-4">
		<button
			type="submit"
			disabled={loading}
			class="from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 focus:ring-primary-500 flex w-full transform items-center justify-center rounded-lg border border-transparent bg-gradient-to-br px-4 py-3 text-sm font-medium text-white shadow-lg transition-all duration-200 hover:-translate-y-0.5 hover:shadow-xl focus:ring-2 focus:ring-offset-2 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
		>
			{#if loading}
				<svg
					class="mr-3 -ml-1 h-5 w-5 animate-spin text-white"
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
				>
					<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
					></circle>
					<path
						class="opacity-75"
						fill="currentColor"
						d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
					></path>
				</svg>
			{/if}
			{$t('auth.sendResetLink')}
		</button>

		<a
			href="/login"
			class="rounded-lg border border-gray-300 bg-white px-4 py-2 text-center text-sm font-medium text-gray-700 transition-colors duration-200 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700"
		>
			{$t('auth.backToLogin')}
		</a>
	</div>
</form>
