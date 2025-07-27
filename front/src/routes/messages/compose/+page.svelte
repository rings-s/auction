<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { fade, slide, scale } from 'svelte/transition';
	import { t, locale } from '$lib/i18n';
	import { user } from '$lib/stores/user.svelte.js';
	import { sendMessage, replyToMessage, getMessage } from '$lib/api/messages';
	import { toast } from '$lib/stores/toastStore.svelte.js';
	import Button from '$lib/components/ui/Button.svelte';

	let data;

	// State management
	let replyToId = data?.replyId || null;
	let originalMessage = $state(null);
	let loading = $state(false);
	let sending = $state(false);
	let error = $state(null);
	let showPriorityFilters = $state(false);

	// Form data
	let formData = $state({
		recipient_email: '',
		subject: '',
		body: '',
		priority: 'normal'
	});

	// Field validation state
	let touched = $state({
		recipient_email: false,
		subject: false,
		body: false
	});

	// Derived values
	let isRTL = $derived($locale === 'ar');
	let isReply = $derived(!!replyToId);

	// Form validation
	let validation = $derived(
		(() => {
			const errors = {};

			if (!isReply && touched.recipient_email && !formData.recipient_email) {
				errors.recipient_email = $t('validation.recipientRequired');
			} else if (!isReply && touched.recipient_email && !isValidEmail(formData.recipient_email)) {
				errors.recipient_email = $t('validation.invalidEmail');
			}

			if (touched.subject && !formData.subject.trim()) {
				errors.subject = $t('validation.subjectRequired');
			} else if (touched.subject && formData.subject.length < 3) {
				errors.subject = $t('validation.subjectTooShort');
			}

			if (touched.body && !formData.body.trim()) {
				errors.body = $t('validation.messageRequired');
			} else if (touched.body && formData.body.length < 10) {
				errors.body = $t('validation.messageTooShort');
			}

			return errors;
		})()
	);

	let isValid = $derived(
		Object.keys(validation).length === 0 &&
			(isReply || formData.recipient_email) &&
			formData.subject.trim() &&
			formData.body.trim()
	);

	// Priority options with app CSS colors
	const priorityOptions = [
		{
			value: 'low',
			label: 'messages.priority.low',
			color:
				'bg-neutral-50 border-neutral-200 text-neutral-700 dark:bg-neutral-900/20 dark:border-neutral-700 dark:text-neutral-300',
			icon: '○',
			iconColor: 'text-neutral-600 dark:text-neutral-400'
		},
		{
			value: 'normal',
			label: 'messages.priority.normal',
			color:
				'bg-success-50 border-success-200 text-success-700 dark:bg-success-900/20 dark:border-success-700 dark:text-success-300',
			icon: '◐',
			iconColor: 'text-success-600 dark:text-success-400'
		},
		{
			value: 'high',
			label: 'messages.priority.high',
			color:
				'bg-warning-50 border-warning-200 text-warning-700 dark:bg-warning-900/20 dark:border-warning-700 dark:text-warning-300',
			icon: '◑',
			iconColor: 'text-warning-600 dark:text-warning-400'
		},
		{
			value: 'urgent',
			label: 'messages.priority.urgent',
			color:
				'bg-danger-50 border-danger-200 text-danger-700 dark:bg-danger-900/20 dark:border-danger-700 dark:text-danger-300',
			icon: '●',
			iconColor: 'text-danger-600 dark:text-danger-400'
		}
	];

	function togglePriorityFilters() {
		showPriorityFilters = !showPriorityFilters;
	}

	let initialLoadDone = false;
	$effect(() => {
		if (replyToId && !initialLoadDone) {
			loadOriginalMessage();
			initialLoadDone = true;
		} else if (!replyToId) {
			originalMessage = null;
			initialLoadDone = false;
		}
	});

	async function loadOriginalMessage() {
		loading = true;
		error = null;

		try {
			const response = await getMessage(replyToId);
			originalMessage = response.data || response;

			if (originalMessage) {
				formData.subject = `Re: ${originalMessage.subject}`;
				formData.body = `\n\n---\n${$t('messages.originalMessage')}:\n${originalMessage.body}`;
			}
		} catch (err) {
			error = err.message || $t('error.fetchFailed');
			toast.error($t('messages.couldNotLoadReplyMessage'));
		} finally {
			loading = false;
		}
	}

	function isValidEmail(email) {
		return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
	}

	async function handleSubmit() {
		touched = {
			recipient_email: true,
			subject: true,
			body: true
		};

		if (!isValid || sending) return;

		sending = true;
		error = null;

		try {
			const messagePayload = {
				subject: formData.subject.trim(),
				body: formData.body.trim(),
				priority: formData.priority
			};

			let response;
			if (isReply && originalMessage) {
				response = await replyToMessage(originalMessage.id, {
					body: messagePayload.body,
					parent_message: originalMessage.id
				});
			} else {
				messagePayload.recipient_email = formData.recipient_email;
				response = await sendMessage(messagePayload);
			}

			toast.success($t('messages.messageSentSuccess'));
			goto('/messages');
		} catch (err) {
			error = err.message || $t('messages.sendError');
			toast.error(error);
		} finally {
			sending = false;
		}
	}

	function handleCancel() {
		goto('/messages');
	}

	function autoResize(event) {
		const textarea = event.target;
		textarea.style.height = 'auto';
		textarea.style.height = `${Math.min(textarea.scrollHeight, 400)}px`;
	}
</script>

<svelte:head>
	<title>{isReply ? $t('messages.reply') : $t('messages.compose')} | {$t('app.name')}</title>
</svelte:head>

<div class="min-h-screen">
	<div class="mx-auto max-w-4xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
		<div class="mb-6">
			<Button
				size="small"
				on:click={handleCancel}
				class="mb-4 inline-flex items-center text-sm text-gray-500 transition-colors hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
			>
				<svg
					class="h-4 w-4 {isRTL ? 'ml-1.5' : 'mr-1.5'}"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d={isRTL ? 'M14 5l7 7m0 0l-7 7m7-7H3' : 'M10 19l-7-7m0 0l7-7m-7 7h18'}
					/>
				</svg>
				{$t('messages.backToMessages')}
			</Button>

			<h1 class="text-2xl font-semibold text-gray-900 dark:text-white">
				{isReply ? $t('messages.replyToMessage') : $t('messages.composeNewMessage')}
			</h1>
		</div>

		<div
			class="rounded-xl border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800"
		>
			{#if loading && isReply}
				<div class="p-8 text-center">
					<div
						class="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-700"
					>
						<div
							class="border-t-primary-500 h-6 w-6 animate-spin rounded-full border-2 border-gray-300 dark:border-gray-500"
						></div>
					</div>
					<p class="text-sm text-gray-500 dark:text-gray-400">{$t('common.loading')}</p>
				</div>
			{:else if error && isReply && !originalMessage}
				<div class="p-8 text-center">
					<div
						class="bg-danger-100 dark:bg-danger-900/20 mb-4 inline-flex h-12 w-12 items-center justify-center rounded-full"
					>
						<svg
							class="text-danger-600 dark:text-danger-400 h-6 w-6"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
					</div>
					<p class="mb-1 text-sm font-medium text-gray-900 dark:text-white">
						{$t('error.fetchFailed')}
					</p>
					<p class="text-sm text-gray-500 dark:text-gray-400">{error}</p>
					<Button onclick={handleCancel} variant="outline" size="sm" class="mt-4">
						{$t('common.back')}
					</Button>
				</div>
			{:else}
				<form
					class="space-y-5 p-6"
					onsubmit={(e) => {
						e.preventDefault();
						handleSubmit();
					}}
				>
					{#if isReply && originalMessage}
						<div
							class="rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-900/50"
							transition:slide
						>
							<div class="flex items-start gap-3">
								<div
									class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gray-200 dark:bg-gray-700"
								>
									<span class="text-xs font-medium text-gray-600 dark:text-gray-300">
										{originalMessage.sender_info?.name?.[0]?.toUpperCase() || '?'}
									</span>
								</div>
								<div class="min-w-0 flex-1">
									<p class="text-sm font-medium text-gray-900 dark:text-white">
										{originalMessage.sender_info?.name || $t('common.unknown')}
									</p>
									<p class="mt-0.5 text-xs text-gray-500 dark:text-gray-400">
										{new Date(originalMessage.created_at).toLocaleString($locale)}
									</p>
									<div class="mt-2 line-clamp-3 text-sm text-gray-600 dark:text-gray-300">
										{originalMessage.body}
									</div>
								</div>
							</div>
						</div>
					{/if}

					{#if !isReply}
						<div>
							<label
								for="recipient_email"
								class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('messages.to')}
								<span class="text-danger-500">*</span>
							</label>
							<input
								id="recipient_email"
								type="email"
								bind:value={formData.recipient_email}
								onfocus={() => (touched.recipient_email = true)}
								placeholder={$t('messages.recipientEmailPlaceholder')}
								class="w-full rounded-lg border px-3.5 py-2.5 text-sm transition-colors
                  {validation.recipient_email && touched.recipient_email
									? 'border-danger-300 focus:border-danger-500 focus:ring-danger-200'
									: 'focus:border-primary-500 focus:ring-primary-200 border-gray-300'}
                  focus:ring-opacity-20 focus:ring-2 focus:outline-none
                  dark:border-gray-600 dark:bg-gray-900 dark:text-white"
								aria-invalid={!!(validation.recipient_email && touched.recipient_email)}
								aria-describedby={validation.recipient_email && touched.recipient_email
									? 'recipient-error'
									: undefined}
								disabled={isReply || sending}
							/>
							{#if validation.recipient_email && touched.recipient_email}
								<p
									id="recipient-error"
									class="text-danger-600 dark:text-danger-400 mt-1 text-xs"
									transition:slide
								>
									{validation.recipient_email}
								</p>
							{/if}
						</div>
					{/if}

					<div>
						<label
							for="subject"
							class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('messages.subject')}
							<span class="text-danger-500">*</span>
						</label>
						<input
							type="text"
							id="subject"
							bind:value={formData.subject}
							onfocus={() => (touched.subject = true)}
							placeholder={$t('messages.subjectPlaceholder')}
							class="w-full rounded-lg border px-3.5 py-2.5 text-sm transition-colors
                {validation.subject && touched.subject
								? 'border-danger-300 focus:border-danger-500 focus:ring-danger-200'
								: 'focus:border-primary-500 focus:ring-primary-200 border-gray-300'}
                focus:ring-opacity-20 focus:ring-2 focus:outline-none
                dark:border-gray-600 dark:bg-gray-900 dark:text-white"
							aria-invalid={!!(validation.subject && touched.subject)}
							aria-describedby={validation.subject && touched.subject ? 'subject-error' : undefined}
						/>
						{#if validation.subject && touched.subject}
							<p
								id="subject-error"
								class="text-danger-600 dark:text-danger-400 mt-1 text-xs"
								transition:slide
							>
								{validation.subject}
							</p>
						{/if}
					</div>

					<div>
						<label
							for="priority-selector"
							class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('messages.form.priority')}
							<span class="text-danger-500">*</span>
						</label>

						<!-- Mobile Priority Toggle (xs, sm, md screens) -->
						<div class="md:hidden">
							<button
								type="button"
								id="priority-selector"
								class="priority-toggle flex w-full items-center justify-between rounded-lg border border-gray-300 bg-white px-3.5 py-2.5 text-sm transition-colors dark:border-gray-600 dark:bg-gray-800"
								aria-expanded={showPriorityFilters}
								aria-controls="priority-filters-panel"
								aria-label={$t('messages.form.priority')}
								onclick={togglePriorityFilters}
							>
								<div class="flex items-center gap-2">
									{#each priorityOptions as option}
										{#if formData.priority === option.value}
											<span class={`priority-icon text-lg leading-none ${option.iconColor}`}
												>{option.icon}</span
											>
											<span class="priority-label">{$t(option.label)}</span>
										{/if}
									{/each}
								</div>
								<svg
									class="filter-icon h-4 w-4 text-gray-400"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d={showPriorityFilters ? 'M5 15l7-7 7 7' : 'M19 9l-7 7-7-7'}
									/>
								</svg>
							</button>

							<!-- Mobile Priority Panel -->
							{#if showPriorityFilters}
								<div
									id="priority-filters-panel"
									class="priority-panel mt-2 overflow-hidden rounded-lg border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800"
									role="radiogroup"
									aria-labelledby="priority-selector"
									transition:slide={{ duration: 300, easing: (t) => 1 - Math.pow(1 - t, 3) }}
								>
									<div class="grid grid-cols-1 gap-2 p-2 sm:grid-cols-2">
										{#each priorityOptions as option}
											<button
												type="button"
												role="radio"
												aria-checked={formData.priority === option.value}
												aria-label={$t(option.label)}
												onclick={() => {
													formData.priority = option.value;
													if (window.innerWidth < 640) {
														showPriorityFilters = false;
													}
												}}
												class="priority-option flex items-center justify-between rounded-lg border px-3 py-2.5 text-sm transition-all duration-200
                          {formData.priority === option.value
													? option.color
													: 'border-gray-300 bg-white text-gray-700 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300'}
                          hover:bg-opacity-80 dark:hover:bg-opacity-80 focus:outline-none"
											>
												<div class="flex items-center gap-2">
													<span class={`text-lg leading-none ${option.iconColor}`}
														>{option.icon}</span
													>
													<span>{$t(option.label)}</span>
												</div>
												{#if formData.priority === option.value}
													<svg
														class="h-4 w-4"
														fill="none"
														stroke="currentColor"
														viewBox="0 0 24 24"
													>
														<path
															stroke-linecap="round"
															stroke-linejoin="round"
															stroke-width="2"
															d="M5 13l4 4L19 7"
														/>
													</svg>
												{/if}
											</button>
										{/each}
									</div>
								</div>
							{/if}
						</div>

						<!-- Desktop Priority Options (lg+ screens) -->
						<fieldset
							class="hidden flex-wrap gap-2.5 md:flex"
							role="radiogroup"
							aria-labelledby="priority-selector"
						>
							<legend class="sr-only">{$t('messages.form.priority')}</legend>
							{#each priorityOptions as option}
								<button
									type="button"
									role="radio"
									aria-checked={formData.priority === option.value}
									aria-label={$t(option.label)}
									onclick={() => (formData.priority = option.value)}
									class="flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-sm transition-colors
                    {formData.priority === option.value
										? option.color
										: 'border-gray-300 bg-white text-gray-700 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300'}
                    hover:bg-opacity-80 dark:hover:bg-opacity-80 focus:outline-none"
								>
									<span class="flex items-center gap-1.5">
										<span class={`text-base leading-none ${option.iconColor}`}>{option.icon}</span>
										<span>{$t(option.label)}</span>
									</span>
								</button>
							{/each}
						</fieldset>
					</div>

					<div>
						<label
							for="body"
							class="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('messages.message')}
							<span class="text-danger-500">*</span>
						</label>
						<textarea
							id="body"
							bind:value={formData.body}
							onfocus={() => (touched.body = true)}
							oninput={autoResize}
							placeholder={$t('messages.messagePlaceholder')}
							rows="6"
							class="w-full resize-none rounded-lg border px-3.5 py-2.5 text-sm transition-colors
                {validation.body && touched.body
								? 'border-danger-300 focus:border-danger-500 focus:ring-danger-200'
								: 'focus:border-primary-500 focus:ring-primary-200 border-gray-300'}
                focus:ring-opacity-20 focus:ring-2 focus:outline-none
                dark:border-gray-600 dark:bg-gray-900 dark:text-white"
							aria-invalid={!!(validation.body && touched.body)}
							aria-describedby={validation.body && touched.body ? 'body-error' : undefined}
						></textarea>
						<div class="mt-1 flex items-center justify-between">
							{#if validation.body && touched.body}
								<p
									id="body-error"
									class="text-danger-600 dark:text-danger-400 text-xs"
									transition:slide
								>
									{validation.body}
								</p>
							{:else}
								<span></span>
							{/if}
							<span class="text-xs text-gray-500 dark:text-gray-400">
								{formData.body.length} / 2000
							</span>
						</div>
					</div>

					<div class="flex flex-wrap justify-end gap-3 pt-3">
						<Button
							variant="outline"
							size="small"
							on:click={handleCancel}
							type="button"
							class="w-full sm:w-auto"
						>
							{$t('common.cancel')}
						</Button>

						<Button
							type="submit"
							variant="primary"
							size="small"
							disabled={!isValid || sending}
							loading={sending}
							class="w-full sm:w-auto"
						>
							{#if sending}
								<svg
									class="h-4 w-4 animate-spin {isRTL ? 'ml-2' : 'mr-2'}"
									xmlns="http://www.w3.org/2000/svg"
									fill="none"
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
										d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
									></path>
								</svg>
								{$t('common.sending')}
							{:else}
								<svg
									class="h-4 w-4 {isRTL ? 'ml-2' : 'mr-2'}"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
									xmlns="http://www.w3.org/2000/svg"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
									></path>
								</svg>
								{$t('messages.send')}
							{/if}
						</Button>
					</div>
				</form>
			{/if}
		</div>
	</div>
</div>

<style>
	.line-clamp-3 {
		display: -webkit-box;
		-webkit-line-clamp: 3;
		line-clamp: 3;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	button[role='radio']:focus-visible {
		outline: 2px solid var(--color-primary-500);
		outline-offset: 2px;
	}

	input:focus-visible,
	textarea:focus-visible {
		outline: 2px solid var(--color-primary-500);
		outline-offset: 1px;
	}

	.priority-toggle {
		position: relative;
		transition: all 0.2s ease;
	}

	.priority-toggle:active {
		transform: scale(0.98);
	}

	.filter-icon {
		transition: transform 0.3s ease;
	}

	.priority-toggle[aria-expanded='true'] .filter-icon {
		transform: rotate(180deg);
	}

	.priority-panel {
		transform-origin: top center;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
	}

	.priority-option {
		position: relative;
		overflow: hidden;
	}

	.priority-option:active {
		transform: translateY(1px);
	}

	.priority-option::after {
		content: '';
		position: absolute;
		top: 50%;
		left: 50%;
		width: 100%;
		height: 100%;
		background-color: currentColor;
		border-radius: 50%;
		opacity: 0;
		transform: translate(-50%, -50%) scale(0);
		transition:
			opacity 0.5s,
			transform 0.3s;
	}

	.priority-option:active::after {
		opacity: 0.1;
		transform: translate(-50%, -50%) scale(1);
		transition:
			opacity 0s,
			transform 0s;
	}

	@media (prefers-reduced-motion: reduce) {
		.priority-panel,
		.filter-icon,
		.priority-option::after {
			transition: none !important;
		}
	}
</style>
