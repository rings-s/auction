<!-- src/lib/components/auth/VerifyEmailForm.svelte -->
<script>
	import { createEventDispatcher, onMount } from 'svelte';
	import { t } from '$lib/i18n';
	import { fly } from 'svelte/transition';

	export let loading = false;
	export let email = '';
	// Remove the unused autoVerify prop since it's not being used
	// export let autoVerify = false; // REMOVED

	const dispatch = createEventDispatcher();

	let verificationCode = '';
	let codeError = '';
	let codeTouched = false;

	// Auto-focus on first input
	let firstInput;

	onMount(() => {
		if (firstInput) {
			// Add a small delay to ensure the component is fully mounted
			setTimeout(() => firstInput.focus(), 100);
		}
	});

	// Validation
	function validateCode(value) {
		if (!value) return $t('auth.validation.codeRequired');
		if (!/^\d{6}$/.test(value)) return $t('auth.validation.codeInvalid');
		return '';
	}

	$: if (codeTouched) codeError = validateCode(verificationCode);

	// Handle paste event for verification code
	function handlePaste(e) {
		e.preventDefault();
		const paste = e.clipboardData.getData('text');
		if (/^\d{6}$/.test(paste)) {
			verificationCode = paste;
			handleSubmit();
		}
	}

	async function handleSubmit() {
		codeTouched = true;
		codeError = validateCode(verificationCode);

		if (codeError) return;

		dispatch('submit', { email, verificationCode });
	}

	function handleResend() {
		dispatch('resend', { email });
	}
</script>

<div class="space-y-6">
	<!-- Email field (read-only) -->
	<div class="space-y-1">
		<label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
			{$t('auth.email')}
		</label>
		<div class="relative">
			<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
				<svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
					/>
				</svg>
			</div>
			<input
				id="email"
				type="email"
				bind:value={email}
				readonly
				class="
          block w-full cursor-not-allowed appearance-none rounded-lg border
          border-gray-300 bg-gray-50 py-3
          pr-3 pl-10
          text-gray-500 shadow-sm
          dark:border-gray-600 dark:bg-gray-900
          dark:text-gray-400
        "
			/>
		</div>
	</div>

	<!-- Verification Code -->
	<div class="space-y-1">
		<label
			for="verification_code"
			class="block text-sm font-medium text-gray-700 dark:text-gray-300"
		>
			{$t('auth.verificationCode')}
		</label>
		<div class="relative">
			<div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
				<svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
					/>
				</svg>
			</div>
			<input
				bind:this={firstInput}
				id="verification_code"
				type="text"
				bind:value={verificationCode}
				on:blur={() => (codeTouched = true)}
				on:paste={handlePaste}
				maxlength="6"
				placeholder="123456"
				class="
          block w-full appearance-none border py-3 pr-3
          pl-10 {codeError && codeTouched
					? 'border-red-300 dark:border-red-600'
					: 'border-gray-300 dark:border-gray-600'}
          focus:ring-primary-500 focus:border-primary-500 rounded-lg placeholder-gray-400
          shadow-sm focus:ring-2 focus:outline-none dark:placeholder-gray-500
          {codeError && codeTouched
					? 'text-red-900 dark:text-red-300'
					: 'text-gray-900 dark:text-white'}
          bg-white text-center
          font-mono text-2xl
          tracking-widest transition-all duration-200 dark:bg-gray-800
        "
			/>
		</div>
		{#if codeError && codeTouched}
			<p class="text-sm text-red-600 dark:text-red-400" in:fly={{ y: -5, duration: 200 }}>
				{codeError}
			</p>
		{/if}
		<p class="text-sm text-gray-500 dark:text-gray-400">
			{$t('auth.verifyInstructions')}
		</p>
	</div>

	<!-- Submit Button -->
	<button
		type="button"
		on:click={handleSubmit}
		disabled={loading || !verificationCode}
		class="
      bg-primary-600 hover:bg-primary-700 focus:ring-primary-500 relative flex w-full
      transform justify-center rounded-lg border border-transparent
      px-4 py-3 text-sm
      font-medium text-white transition-all duration-200
      hover:scale-[1.02] focus:ring-2
      focus:ring-offset-2 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50
    "
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
		{$t('auth.verifyAccount')}
	</button>

	<!-- Resend Code -->
	<div class="text-center">
		<button
			type="button"
			on:click={handleResend}
			disabled={loading}
			class="text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300 text-sm font-medium transition-colors duration-200 disabled:opacity-50"
		>
			{$t('auth.resendCode')}
		</button>
	</div>
</div>
