<script>
	import { createEventDispatcher, onMount, tick } from 'svelte';
	import { fade, slide, scale, fly } from 'svelte/transition';
	import { t, locale } from '$lib/i18n';
	import { user as loggedInUserStore } from '$lib/stores/user.svelte.js';
	import { contactPropertyOwner, sendMessage } from '$lib/api/messages';
	import { getUserById } from '$lib/api/user';
	import Button from '$lib/components/ui/Button.svelte';

	export let property = null;
	export let recipient = ''; // User ID of the recipient, if applicable
	export let initialSubject = '';
	export let initialMessage = '';
	export let compact = false;

	const dispatch = createEventDispatcher();

	// Form state
	let formData = {
		subject: initialSubject || (property ? `${$t('messages.inquiryAbout')} ${property.title}` : ''),
		body: initialMessage || '',
		priority: 'normal'
	};

	let loading = false;
	let error = null;
	let success = false;
	let showFullForm = !compact;
	let fieldErrors = {};
	let touched = {};
	let mounted = false;
	let recipientDisplayName = '';

	// Reactive statement to update recipientDisplayName when 'recipient' prop changes
	$: if (recipient && $loggedInUserStore) {
		if (recipient === $loggedInUserStore.id) {
			recipientDisplayName = $loggedInUserStore.username || $loggedInUserStore.email;
		} else {
			// Fetch recipient's name if it's a different user
			loading = true;
			getUserById(recipient)
				.then((userProfile) => {
					if (userProfile && userProfile.username) {
						recipientDisplayName = userProfile.username;
					} else if (userProfile && userProfile.email) {
						recipientDisplayName = userProfile.email;
					} else {
						recipientDisplayName = $t('messages.unknownUser');
					}
					loading = false;
				})
				.catch((err) => {
					recipientDisplayName = $t('messages.errorFetchingUser');
					loading = false;
				});
		}
	} else if (recipient) {
		loading = true;
		getUserById(recipient)
			.then((userProfile) => {
				if (userProfile && userProfile.username) {
					recipientDisplayName = userProfile.username;
				} else if (userProfile && userProfile.email) {
					recipientDisplayName = userProfile.email;
				} else {
					recipientDisplayName = $t('messages.unknownUser');
				}
				loading = false;
			})
			.catch((err) => {
				recipientDisplayName = $t('messages.errorFetchingUser');
				loading = false;
			});
	} else {
		recipientDisplayName = '';
	}

	// Form validation
	let validationState = {
		subject: { isValid: false, message: '' },
		body: { isValid: false, message: '' }
	};

	// Computed values
	$: isRTL = $locale === 'ar';
	$: characterCount = formData.body.length;
	$: maxCharacters = 2000;
	$: subjectLength = formData.subject.length;
	$: maxSubjectLength = 255;

	// Real-time validation
	$: {
		// Subject validation
		if (formData.subject.length === 0) {
			validationState.subject = { isValid: false, message: $t('validation.subjectRequired') };
		} else if (formData.subject.length < 5) {
			validationState.subject = { isValid: false, message: $t('validation.subjectTooShort') };
		} else if (formData.subject.length > maxSubjectLength) {
			validationState.subject = { isValid: false, message: $t('validation.subjectTooLong') };
		} else {
			validationState.subject = { isValid: true, message: '' };
		}

		// Body validation
		if (formData.body.length === 0) {
			validationState.body = { isValid: false, message: $t('validation.messageRequired') };
		} else if (formData.body.length < 10) {
			validationState.body = { isValid: false, message: $t('validation.messageTooShort') };
		} else if (formData.body.length > maxCharacters) {
			validationState.body = { isValid: false, message: $t('validation.messageTooLong') };
		} else {
			validationState.body = { isValid: true, message: '' };
		}
	}

	$: canSubmit =
		validationState.subject.isValid &&
		validationState.body.isValid &&
		!loading &&
		$loggedInUserStore;

	// Priority options with enhanced design
	const priorityOptions = [
		{
			value: 'low',
			label: 'messages.priority.low',
			icon: '🔵',
			color:
				'bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-900/20 dark:border-blue-800 dark:text-blue-300',
			activeColor:
				'bg-blue-100 border-blue-400 text-blue-800 dark:bg-blue-900/40 dark:border-blue-600 dark:text-blue-200'
		},
		{
			value: 'normal',
			label: 'messages.priority.normal',
			icon: '🟢',
			color:
				'bg-green-50 border-green-200 text-green-700 dark:bg-green-900/20 dark:border-green-800 dark:text-green-300',
			activeColor:
				'bg-green-100 border-green-400 text-green-800 dark:bg-green-900/40 dark:border-green-600 dark:text-green-200'
		},
		{
			value: 'high',
			label: 'messages.priority.high',
			icon: '🟡',
			color:
				'bg-yellow-50 border-yellow-200 text-yellow-700 dark:bg-yellow-900/20 dark:border-yellow-800 dark:text-yellow-300',
			activeColor:
				'bg-yellow-100 border-yellow-400 text-yellow-800 dark:bg-yellow-900/40 dark:border-yellow-600 dark:text-yellow-200'
		},
		{
			value: 'urgent',
			label: 'messages.priority.urgent',
			icon: '🔴',
			color:
				'bg-red-50 border-red-200 text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300',
			activeColor:
				'bg-red-100 border-red-400 text-red-800 dark:bg-red-900/40 dark:border-red-600 dark:text-red-200'
		}
	];

	// Handle form submission with enhanced UX
	async function handleSubmit() {
		if (!canSubmit) return;

		loading = true;
		error = null;

		try {
			const messageData = {
				subject: formData.subject.trim(),
				body: formData.body.trim(),
				priority: formData.priority
			};

			let response;

			// FIXED: Always use contactPropertyOwner when property is provided
			if (property && property.id) {
				response = await contactPropertyOwner(property.id, messageData);
			} else if (recipient) {
				// For direct messaging (not implemented yet)
				throw new Error($t('messages.directMessagingNotAvailable'));
			} else {
				throw new Error($t('messages.directMessagingNotAvailable'));
			}

			success = true;

			// Auto-hide success message after 5 seconds
			setTimeout(() => {
				success = false;
			}, 5000);

			// Reset form after success
			setTimeout(() => {
				formData = {
					subject: property ? `${$t('messages.inquiryAbout')} ${property.title}` : '',
					body: '',
					priority: 'normal'
				};
				touched = {};
			}, 1000);

			dispatch('success', {
				message: $t('messages.messageSentSuccess'),
				data: response
			});
		} catch (err) {
			// Enhanced error handling
			if (err.response && err.response.data) {
				// Handle API validation errors
				const apiErrors = err.response.data;
				if (typeof apiErrors === 'object') {
					const errorMessages = [];
					for (const [field, messages] of Object.entries(apiErrors)) {
						if (Array.isArray(messages)) {
							errorMessages.push(...messages);
						} else {
							errorMessages.push(messages);
						}
					}
					error = errorMessages.join(', ');
				} else {
					error = apiErrors;
				}
			} else {
				error = err.message || $t('messages.sendError');
			}

			dispatch('error', { error: err.message });
		} finally {
			loading = false;
		}
	}

	// Enhanced input handling with immediate feedback
	function handleInput(field, value) {
		formData[field] = value;
		touched[field] = true;
		if (error) error = null;
		if (success) success = false;
	}

	// Toggle form with smooth animation
	function toggleFullForm() {
		showFullForm = !showFullForm;
	}

	// Focus management
	function focusFirstInput() {
		if (mounted) {
			const firstInput = document.querySelector('#contact-subject');
			if (firstInput) firstInput.focus();
		}
	}

	// Auto-resize textarea
	function autoResize(textarea) {
		textarea.style.height = 'auto';
		textarea.style.height = textarea.scrollHeight + 'px';
	}

	onMount(() => {
		mounted = true;
	});
</script>

<!-- Rest of the template remains the same -->
<div
	class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-xl backdrop-blur-sm dark:border-gray-700 dark:bg-gray-800"
>
	<!-- Enhanced Header with Property Context -->
	<div
		class="bg-gradient-to-r from-blue-50 via-white to-green-50 px-6 py-5 dark:from-blue-900/10 dark:via-gray-800 dark:to-green-900/10"
	>
		<div class="flex items-start justify-between">
			<div class="flex-1">
				<div class="mb-2 flex items-center gap-3">
					<div class="rounded-xl bg-blue-100 p-2 dark:bg-blue-900/30">
						<svg
							class="h-5 w-5 text-blue-600 dark:text-blue-400"
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
						<h3 class="text-xl font-bold text-gray-900 dark:text-white">
							{$t('property.contactOwner')}
						</h3>
						<p class="text-sm text-gray-600 dark:text-gray-400">
							{$t('messages.getInTouch')}
						</p>
					</div>
				</div>

				{#if property}
					<div
						class="rounded-lg border border-gray-200/50 bg-white/50 p-3 dark:border-gray-600/50 dark:bg-gray-700/30"
					>
						<div class="flex items-center gap-3">
							{#if property.images && property.images[0]}
								<img
									src={property.images[0].image_url}
									alt={property.title}
									class="h-12 w-12 rounded-lg object-cover"
								/>
							{:else}
								<div
									class="flex h-12 w-12 items-center justify-center rounded-lg bg-gray-200 dark:bg-gray-600"
								>
									<svg
										class="h-6 w-6 text-gray-400"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
										/>
									</svg>
								</div>
							{/if}
							<div class="min-w-0 flex-1">
								<p class="truncate font-semibold text-gray-900 dark:text-white">
									{property.title}
								</p>
								<p class="text-sm text-gray-600 dark:text-gray-400">
									{property.location?.city || ''} • ${property.market_value?.toLocaleString() ||
										'N/A'}
								</p>
							</div>
						</div>
					</div>
				{/if}
			</div>

			{#if compact}
				<Button
					type="button"
					size="small"
					on:click={toggleFullForm}
					class="group rounded-xl p-2 transition-all duration-200 hover:bg-white/60 dark:hover:bg-gray-700/50"
					aria-label={showFullForm ? $t('common.collapse') : $t('common.expand')}
				>
					<svg
						class="h-5 w-5 text-gray-600 transition-all duration-300 group-hover:text-blue-600 dark:text-gray-400 dark:group-hover:text-blue-400 {showFullForm
							? 'rotate-180'
							: ''}"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M19 9l-7 7-7-7"
						/>
					</svg>
				</Button>
			{/if}
		</div>
	</div>

	<!-- Enhanced Form Content -->
	{#if showFullForm}
		<div class="p-6" transition:slide={{ duration: 400, easing: (t) => t * (2 - t) }}>
			{#if !$loggedInUserStore && !recipient}
				<!-- Enhanced Login Required State -->
				<div class="py-12 text-center" in:fade={{ duration: 300 }}>
					<div
						class="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-blue-100 dark:bg-blue-900/30"
					>
						<svg
							class="h-10 w-10 text-blue-600 dark:text-blue-400"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
							/>
						</svg>
					</div>
					<h4 class="mb-3 text-2xl font-bold text-gray-900 dark:text-white">
						{$t('messages.loginRequired')}
					</h4>
					<p class="mx-auto mb-8 max-w-md text-gray-600 dark:text-gray-400">
						{$t('property.loginToContact')}
					</p>
					<div class="flex flex-col justify-center gap-3 sm:flex-row">
						<Button
							href="/login"
							variant="primary"
							size="large"
							rounded="full"
							class="inline-flex items-center shadow-lg transition-all hover:shadow-xl"
						>
							<svg
								class="h-5 w-5 {isRTL ? 'ml-3' : 'mr-3'}"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"
								/>
							</svg>
							{$t('nav.login')}
						</Button>
						<Button
							href="/register"
							variant="outline"
							size="small"
							rounded="full"
							class="inline-flex items-center"
						>
							<svg
								class="h-5 w-5 {isRTL ? 'ml-3' : 'mr-3'}"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
								/>
							</svg>
							{$t('nav.register')}
						</Button>
					</div>
				</div>
			{:else}
				<!-- Enhanced Message Form -->
				<form on:submit|preventDefault={handleSubmit} class="space-y-8">
					<!-- Enhanced Success/Error Messages -->
					{#if success}
						<div
							class="rounded-xl border-l-4 border-green-400 bg-gradient-to-r from-green-50 to-emerald-50 p-6 shadow-sm dark:from-green-900/20 dark:to-emerald-900/20"
							transition:fly={{ y: -20, duration: 400 }}
						>
							<div class="flex items-start">
								<div class="flex-shrink-0">
									<div
										class="flex h-8 w-8 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/40"
									>
										<svg
											class="h-5 w-5 text-green-600 dark:text-green-400"
											fill="none"
											stroke="currentColor"
											viewBox="0 0 24 24"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
											/>
										</svg>
									</div>
								</div>
								<div class={isRTL ? 'mr-4' : 'ml-4'}>
									<h4 class="mb-1 text-lg font-semibold text-green-800 dark:text-green-200">
										{$t('messages.messageSentSuccess')}
									</h4>
									<p class="text-green-700 dark:text-green-300">
										{$t('messages.messageDelivered')}
									</p>
								</div>
							</div>
						</div>
					{/if}

					{#if error}
						<div
							class="rounded-xl border-l-4 border-red-400 bg-gradient-to-r from-red-50 to-pink-50 p-6 shadow-sm dark:from-red-900/20 dark:to-pink-900/20"
							transition:fly={{ y: -20, duration: 400 }}
						>
							<div class="flex items-start">
								<div class="flex-shrink-0">
									<div
										class="flex h-8 w-8 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/40"
									>
										<svg
											class="h-5 w-5 text-red-600 dark:text-red-400"
											fill="none"
											stroke="currentColor"
											viewBox="0 0 24 24"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
											/>
										</svg>
									</div>
								</div>
								<div class={isRTL ? 'mr-4' : 'ml-4'}>
									<h4 class="mb-1 text-lg font-semibold text-red-800 dark:text-red-200">
										{$t('error.sendingFailed')}
									</h4>
									<p class="text-red-700 dark:text-red-300">{error}</p>
								</div>
							</div>
						</div>
					{/if}

					<!-- Enhanced Sender Info -->
					<div
						class="rounded-2xl border border-gray-200 bg-gradient-to-r from-gray-50 to-blue-50 p-6 dark:border-gray-700 dark:from-gray-800 dark:to-blue-900/20"
					>
						<div class="flex items-center">
							<div class="relative">
								<div
									class="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-green-500 text-lg font-bold text-white shadow-lg"
								>
									{$loggedInUserStore.first_name?.charAt(0)}{$loggedInUserStore.last_name?.charAt(
										0
									)}
								</div>
								<div
									class="absolute -right-1 -bottom-1 h-5 w-5 rounded-full border-2 border-white bg-green-400 dark:border-gray-800"
								></div>
							</div>
							<div class="{isRTL ? 'mr-4' : 'ml-4'} flex-1">
								<p class="text-lg font-bold text-gray-900 dark:text-white">
									{$loggedInUserStore.first_name}
									{$loggedInUserStore.last_name}
								</p>
								<p class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
										/>
									</svg>
									{$loggedInUserStore.email}
								</p>
							</div>
							<div
								class="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-300"
							>
								{$t('messages.sender')}
							</div>
						</div>
					</div>

					<!-- Display Recipient Name if available -->
					{#if recipientDisplayName}
						<div
							class="mb-4 rounded-lg border border-blue-200 bg-blue-50 p-3 dark:border-blue-800 dark:bg-blue-900/20"
						>
							<p class="text-sm font-medium text-blue-700 dark:text-blue-300">
								{$t('messages.to', { values: { name: recipientDisplayName } })}
							</p>
						</div>
					{/if}

					<!-- Enhanced Subject Field -->
					<div class="space-y-2">
						<label
							for="contact-subject"
							class="flex items-center justify-between text-sm font-semibold text-gray-700 dark:text-gray-300"
						>
							<span class="flex items-center gap-2">
								{$t('messages.subject')}
								<span class="text-base text-red-500">*</span>
							</span>
							<span class="text-xs text-gray-500 dark:text-gray-400">
								{subjectLength}/{maxSubjectLength}
							</span>
						</label>
						<div class="relative">
							<input
								id="contact-subject"
								type="text"
								bind:value={formData.subject}
								on:input={(e) => handleInput('subject', e.target.value)}
								on:focus={() => (touched.subject = true)}
								placeholder={$t('messages.subjectPlaceholder')}
								class="block w-full rounded-2xl border-2 px-6 py-4 text-base shadow-sm transition-all duration-200
                  {validationState.subject.isValid && touched.subject
									? 'border-green-300 bg-green-50/30 focus:border-green-400 focus:ring-green-200 dark:border-green-600 dark:bg-green-900/10'
									: !validationState.subject.isValid && touched.subject
										? 'border-red-300 bg-red-50/30 focus:border-red-400 focus:ring-red-200 dark:border-red-600 dark:bg-red-900/10'
										: 'border-gray-300 focus:border-blue-400 focus:ring-blue-200 dark:border-gray-600'}
                  focus:ring-opacity-20 placeholder-gray-400 focus:ring-4 dark:bg-gray-700 dark:text-white"
								required
								maxlength={maxSubjectLength}
							/>
							{#if validationState.subject.isValid && touched.subject}
								<div
									class="absolute top-1/2 -translate-y-1/2 transform {isRTL ? 'left-4' : 'right-4'}"
								>
									<svg
										class="h-5 w-5 text-green-500"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
										/>
									</svg>
								</div>
							{/if}
						</div>
						{#if !validationState.subject.isValid && touched.subject}
							<p
								class="flex items-center gap-2 text-sm text-red-600 dark:text-red-400"
								transition:slide={{ duration: 200 }}
							>
								<svg
									class="h-4 w-4 flex-shrink-0"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
									/>
								</svg>
								{validationState.subject.message}
							</p>
						{/if}
					</div>

					<!-- Enhanced Priority Selection -->
					<fieldset class="space-y-3">
						<legend class="block text-sm font-semibold text-gray-700 dark:text-gray-300">
							{$t('messages.form.priority')}
							<span class="text-base text-red-500 {isRTL ? 'mr-1' : 'ml-1'}">*</span>
						</legend>
						<div class="grid grid-cols-2 gap-3 lg:grid-cols-4">
							{#each priorityOptions as option (option.value)}
								<button
									type="button"
									class="group relative rounded-2xl border-2 p-4 text-sm font-medium transition-all duration-300 hover:scale-105 hover:shadow-lg {formData.priority ===
									option.value
										? option.activeColor + ' scale-105 transform shadow-md'
										: option.color + ' hover:shadow-md'}"
									on:click={() => handleInput('priority', option.value)}
									in:scale={{ duration: 200, delay: priorityOptions.indexOf(option) * 50 }}
								>
									<div class="text-center">
										<span
											class="mb-2 block text-2xl transition-transform duration-200 group-hover:scale-110"
											>{option.icon}</span
										>
										<span class="block text-xs font-semibold">{$t(option.label)}</span>
									</div>
									{#if formData.priority === option.value}
										<div
											class="absolute top-2 {isRTL ? 'left-2' : 'right-2'}"
											transition:scale={{ duration: 200 }}
										>
											<svg
												class="h-4 w-4 text-current"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
												/>
											</svg>
										</div>
									{/if}
								</button>
							{/each}
						</div>
					</fieldset>

					<!-- Enhanced Message Body -->
					<div class="space-y-2">
						<label
							for="contact-message"
							class="flex items-center justify-between text-sm font-semibold text-gray-700 dark:text-gray-300"
						>
							<span class="flex items-center gap-2">
								{$t('property.message')}
								<span class="text-base text-red-500">*</span>
							</span>
							<span
								class="text-xs text-gray-500 dark:text-gray-400 {characterCount >
								maxCharacters * 0.9
									? 'text-orange-500'
									: ''}"
							>
								{characterCount}/{maxCharacters}
							</span>
						</label>
						<div class="relative">
							<textarea
								id="contact-message"
								bind:value={formData.body}
								on:input={(e) => {
									handleInput('body', e.target.value);
									autoResize(e.target);
								}}
								on:focus={() => (touched.body = true)}
								placeholder={$t('property.messagePlaceholder')}
								rows="6"
								maxlength={maxCharacters}
								class="block w-full resize-none rounded-2xl border-2 px-6 py-4 text-base shadow-sm transition-all duration-200
                  {validationState.body.isValid && touched.body
									? 'border-green-300 bg-green-50/30 focus:border-green-400 focus:ring-green-200 dark:border-green-600 dark:bg-green-900/10'
									: !validationState.body.isValid && touched.body
										? 'border-red-300 bg-red-50/30 focus:border-red-400 focus:ring-red-200 dark:border-red-600 dark:bg-red-900/10'
										: 'border-gray-300 focus:border-blue-400 focus:ring-blue-200 dark:border-gray-600'}
                  focus:ring-opacity-20 placeholder-gray-400 focus:ring-4 dark:bg-gray-700 dark:text-white"
								required
							></textarea>
							{#if validationState.body.isValid && touched.body}
								<div class="absolute top-4 {isRTL ? 'left-4' : 'right-4'}">
									<svg
										class="h-5 w-5 text-green-500"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
										/>
									</svg>
								</div>
							{/if}
						</div>
						{#if !validationState.body.isValid && touched.body}
							<p
								class="flex items-center gap-2 text-sm text-red-600 dark:text-red-400"
								transition:slide={{ duration: 200 }}
							>
								<svg
									class="h-4 w-4 flex-shrink-0"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
									/>
								</svg>
								{validationState.body.message}
							</p>
						{/if}
					</div>

					<!-- Enhanced Submit Section -->
					<div
						class="flex flex-col items-start justify-between gap-4 border-t-2 border-gray-100 pt-6 sm:flex-row sm:items-center dark:border-gray-700"
					>
						<div class="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400">
							<svg
								class="mt-0.5 h-4 w-4 flex-shrink-0 text-blue-500"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M13 16h-1v-4h-1m1-4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
								/>
							</svg>
							<span>{$t('messages.messageDisclaimer')}</span>
						</div>

						<Button
							type="submit"
							variant="primary"
							size="large"
							disabled={!canSubmit}
							{loading}
							rounded="full"
							class="min-w-[160px] shadow-lg transition-all duration-300 hover:shadow-xl {canSubmit
								? 'hover:scale-105'
								: ''}"
						>
							{#if loading}
								<svg
									class="h-5 w-5 {isRTL ? 'ml-3' : 'mr-3'} animate-spin"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<circle
										class="opacity-25"
										cx="12"
										cy="12"
										r="10"
										stroke="currentColor"
										stroke-width="4"
									></circle>
									<path
										class="opacity-75"
										fill="currentColor"
										d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
									></path>
								</svg>
								{$t('common.sending')}
							{:else}
								<svg
									class="h-5 w-5 {isRTL ? 'ml-3' : 'mr-3'}"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
									/>
								</svg>
								{$t('property.sendMessage')}
							{/if}
						</Button>
					</div>
				</form>
			{/if}
		</div>
	{/if}
</div>

<!-- Rest of the styles remain the same -->
<style>
	/* Enhanced animations */
	@keyframes shake {
		0%,
		100% {
			transform: translateX(0);
		}
		25% {
			transform: translateX(-4px);
		}
		75% {
			transform: translateX(4px);
		}
	}

	/* Auto-resize textarea */
	textarea {
		transition: height 0.2s ease;
	}

	/* Enhanced focus styles */
	input:focus,
	textarea:focus {
		transform: translateY(-1px);
	}

	/* Priority button animations */
	.priority-option:hover {
		animation: subtle-bounce 0.4s ease;
	}

	@keyframes subtle-bounce {
		0%,
		100% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.05);
		}
	}

	/* Character counter color transitions */
	.character-counter {
		transition: color 0.3s ease;
	}

	/* Validation state transitions */
	.validation-enter {
		animation: slideDown 0.2s ease;
	}

	@keyframes slideDown {
		from {
			opacity: 0;
			transform: translateY(-8px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	/* RTL-specific adjustments */
	:global(.rtl) .character-counter {
		left: 1rem;
		right: auto;
	}

	/* High contrast mode */
	@media (prefers-contrast: high) {
		input,
		textarea {
			border-width: 3px;
		}
	}

	/* Reduced motion */
	@media (prefers-reduced-motion: reduce) {
		* {
			animation: none !important;
			transition: none !important;
		}
	}
</style>
