<!-- src/lib/components/property-management/workers/create/WorkerCreateTabs.svelte -->
<script>
	import { t, locale } from '$lib/i18n';
	import { fade } from 'svelte/transition';
	import MultiSelect from '$lib/components/ui/MultiSelect.svelte';
	import FileUploader from '$lib/components/ui/FileUploader.svelte';

	let {
		currentStep,
		workerData,
		validationErrors = {},
		employmentTypeOptions = [],
		statusOptions = [],
		skillLevelOptions = [],
		categoryOptions = [],
		departmentOptions = [],
		languageOptions = [],
		onChange,
		onCategoriesChange,
		onDocumentUpload,
		onProfileImageUpload
	} = $props();

	let isRTL = $derived($locale === 'ar');

	// Handle form field changes
	function handleFieldChange(field, value) {
		onChange?.(field, value);
	}

	// Handle multi-select changes
	function handleCertificationsChange(event) {
		onChange?.('certifications', event.detail);
	}

	function handleLanguagesChange(event) {
		onChange?.('languages', event.detail);
	}

	function handleSpecializationsChange(event) {
		onChange?.('specializations', event.detail);
	}

	// Format currency for display
	function formatCurrency(value) {
		if (!value) return '';
		return new Intl.NumberFormat($locale === 'ar' ? 'ar-SA' : 'en-US', {
			style: 'currency',
			currency: $locale === 'ar' ? 'SAR' : 'USD',
			minimumFractionDigits: 0
		}).format(value);
	}

	// Available certifications
	let certificationOptions = [
		'electrical_license',
		'plumbing_license',
		'hvac_certification',
		'safety_certification',
		'first_aid_certified',
		'fire_safety_certified',
		'forklift_operator',
		'crane_operator',
		'welding_certified',
		'carpentry_certified'
	].map((cert) => ({
		value: cert,
		label: $t(`worker.certification.${cert}`)
	}));

	// Available specializations
	let specializationOptions = [
		'residential_maintenance',
		'commercial_maintenance',
		'emergency_repairs',
		'preventive_maintenance',
		'equipment_installation',
		'system_diagnostics',
		'project_management',
		'customer_service',
		'training_mentoring',
		'quality_control'
	].map((spec) => ({
		value: spec,
		label: $t(`worker.specialization.${spec}`)
	}));
</script>

<div
	class="border-x border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
	dir={isRTL ? 'rtl' : 'ltr'}
>
	<!-- Step 1: Personal Information -->
	{#if currentStep === 1}
		<div class="step-content p-8" transition:fade={{ duration: 300 }}>
			<div class="space-y-6">
				<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
					<!-- Full Name -->
					<div class="lg:col-span-2">
						<label
							for="full_name"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('worker.fullName')} <span class="text-red-500">*</span>
						</label>
						<input
							type="text"
							id="full_name"
							bind:value={workerData.full_name}
							on:input={(e) => handleFieldChange('full_name', e.target.value)}
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 placeholder-gray-500 transition-all duration-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
							placeholder={$t('worker.fullNamePlaceholder')}
							class:border-red-500={validationErrors.full_name}
							class:ring-red-500={validationErrors.full_name}
						/>
						{#if validationErrors.full_name}
							<p class="mt-1 text-sm text-red-600 dark:text-red-400">
								{validationErrors.full_name}
							</p>
						{/if}
					</div>

					<!-- Email -->
					<div>
						<label
							for="email"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('worker.email')} <span class="text-red-500">*</span>
						</label>
						<input
							type="email"
							id="email"
							bind:value={workerData.email}
							on:input={(e) => handleFieldChange('email', e.target.value)}
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 placeholder-gray-500 transition-all duration-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
							placeholder={$t('worker.emailPlaceholder')}
							class:border-red-500={validationErrors.email}
						/>
						{#if validationErrors.email}
							<p class="mt-1 text-sm text-red-600 dark:text-red-400">{validationErrors.email}</p>
						{/if}
					</div>

					<!-- Phone -->
					<div>
						<label
							for="phone"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('worker.phone')} <span class="text-red-500">*</span>
						</label>
						<input
							type="tel"
							id="phone"
							bind:value={workerData.phone}
							on:input={(e) => handleFieldChange('phone', e.target.value)}
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 placeholder-gray-500 transition-all duration-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
							placeholder={$t('worker.phonePlaceholder')}
							class:border-red-500={validationErrors.phone}
						/>
						{#if validationErrors.phone}
							<p class="mt-1 text-sm text-red-600 dark:text-red-400">{validationErrors.phone}</p>
						{/if}
					</div>

					<!-- Date of Birth -->
					<div>
						<label
							for="date_of_birth"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('worker.dateOfBirth')}
						</label>
						<input
							type="date"
							id="date_of_birth"
							bind:value={workerData.date_of_birth}
							on:change={(e) => handleFieldChange('date_of_birth', e.target.value)}
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
						/>
					</div>

					<!-- National ID -->
					<div>
						<label
							for="national_id"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('worker.nationalId')}
						</label>
						<input
							type="text"
							id="national_id"
							bind:value={workerData.national_id}
							on:input={(e) => handleFieldChange('national_id', e.target.value)}
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 placeholder-gray-500 transition-all duration-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
							placeholder={$t('worker.nationalIdPlaceholder')}
						/>
					</div>
				</div>

				<!-- Emergency Contact Section -->
				<div>
					<h3 class="mb-4 flex items-center text-lg font-semibold text-gray-900 dark:text-white">
						<svg
							class="mr-2 h-5 w-5 text-red-500"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"
							/>
						</svg>
						{$t('worker.emergencyContact')}
					</h3>
					<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
						<!-- Emergency Contact Name -->
						<div>
							<label
								for="emergency_contact_name"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('worker.emergencyContactName')}
							</label>
							<input
								type="text"
								id="emergency_contact_name"
								bind:value={workerData.emergency_contact_name}
								on:input={(e) => handleFieldChange('emergency_contact_name', e.target.value)}
								class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 placeholder-gray-500 transition-all duration-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
								placeholder={$t('worker.emergencyContactNamePlaceholder')}
							/>
						</div>

						<!-- Emergency Contact Phone -->
						<div>
							<label
								for="emergency_contact_phone"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('worker.emergencyContactPhone')}
							</label>
							<input
								type="tel"
								id="emergency_contact_phone"
								bind:value={workerData.emergency_contact_phone}
								on:input={(e) => handleFieldChange('emergency_contact_phone', e.target.value)}
								class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 placeholder-gray-500 transition-all duration-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
								placeholder={$t('worker.emergencyContactPhonePlaceholder')}
							/>
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}

	<!-- Step 2: Employment Details -->
	{#if currentStep === 2}
		<div class="step-content p-8" transition:fade={{ duration: 300 }}>
			<div class="space-y-6">
				<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
					<!-- Employee ID -->
					<div>
						<label
							for="employee_id"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('worker.employeeId')}
						</label>
						<input
							type="text"
							id="employee_id"
							bind:value={workerData.employee_id}
							disabled
							class="w-full cursor-not-allowed rounded-lg border border-gray-300 bg-gray-100 px-4 py-3 text-gray-900 dark:border-gray-600 dark:bg-gray-600 dark:text-white"
						/>
						<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
							{$t('worker.employeeIdHelp')}
						</p>
					</div>

					<!-- Hire Date -->
					<div>
						<label
							for="hire_date"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('worker.hireDate')} <span class="text-red-500">*</span>
						</label>
						<input
							type="date"
							id="hire_date"
							bind:value={workerData.hire_date}
							on:change={(e) => handleFieldChange('hire_date', e.target.value)}
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
							class:border-red-500={validationErrors.hire_date}
						/>
						{#if validationErrors.hire_date}
							<p class="mt-1 text-sm text-red-600 dark:text-red-400">
								{validationErrors.hire_date}
							</p>
						{/if}
					</div>

					<!-- Employment Type -->
					<div>
						<label
							for="employment_type"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('worker.employmentType')}
						</label>
						<select
							id="employment_type"
							bind:value={workerData.employment_type}
							on:change={(e) => handleFieldChange('employment_type', e.target.value)}
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
						>
							{#each employmentTypeOptions as option}
								<option value={option.value}>{option.label}</option>
							{/each}
						</select>
					</div>

					<!-- Status -->
					<div>
						<label
							for="status"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('common.status')}
						</label>
						<select
							id="status"
							bind:value={workerData.status}
							on:change={(e) => handleFieldChange('status', e.target.value)}
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
						>
							{#each statusOptions as option}
								<option value={option.value}>{option.label}</option>
							{/each}
						</select>
					</div>

					<!-- Department -->
					<div>
						<label
							for="department"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('worker.department')}
						</label>
						<select
							id="department"
							bind:value={workerData.department}
							on:change={(e) => handleFieldChange('department', e.target.value)}
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
						>
							<option value="">{$t('worker.selectDepartment')}</option>
							{#each departmentOptions as option}
								<option value={option.value}>{option.label}</option>
							{/each}
						</select>
					</div>

					<!-- Position -->
					<div>
						<label
							for="position"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('worker.position')}
						</label>
						<input
							type="text"
							id="position"
							bind:value={workerData.position}
							on:input={(e) => handleFieldChange('position', e.target.value)}
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 placeholder-gray-500 transition-all duration-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
							placeholder={$t('worker.positionPlaceholder')}
						/>
					</div>

					<!-- Hourly Rate -->
					<div>
						<label
							for="hourly_rate"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('worker.hourlyRate')} <span class="text-red-500">*</span>
						</label>
						<input
							type="number"
							id="hourly_rate"
							bind:value={workerData.hourly_rate}
							on:input={(e) => handleFieldChange('hourly_rate', parseFloat(e.target.value))}
							min="0"
							step="0.01"
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
							placeholder="50.00"
							class:border-red-500={validationErrors.hourly_rate}
						/>
						{#if validationErrors.hourly_rate}
							<p class="mt-1 text-sm text-red-600 dark:text-red-400">
								{validationErrors.hourly_rate}
							</p>
						{/if}
					</div>

					<!-- Experience Years -->
					<div>
						<label
							for="experience_years"
							class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{$t('worker.experienceYears')}
						</label>
						<input
							type="number"
							id="experience_years"
							bind:value={workerData.experience_years}
							on:input={(e) => handleFieldChange('experience_years', parseInt(e.target.value))}
							min="0"
							max="50"
							class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
							placeholder="5"
						/>
					</div>
				</div>
			</div>
		</div>
	{/if}

	<!-- Step 3: Skills & Categories -->
	{#if currentStep === 3}
		<div class="step-content p-8" transition:fade={{ duration: 300 }}>
			<div class="space-y-6">
				<!-- Skills Section -->
				<div>
					<h3 class="mb-4 flex items-center text-lg font-semibold text-gray-900 dark:text-white">
						<svg
							class="mr-2 h-5 w-5 text-blue-500"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
							/>
						</svg>
						{$t('worker.skillsAndExpertise')}
					</h3>
					<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
						<!-- Categories -->
						<div>
							<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
								{$t('worker.categories')} <span class="text-red-500">*</span>
							</label>
							<MultiSelect
								options={categoryOptions}
								selected={workerData.categories}
								placeholder={$t('worker.selectCategories')}
								onChange={onCategoriesChange}
								error={validationErrors.categories}
							/>
							{#if validationErrors.categories}
								<p class="mt-1 text-sm text-red-600 dark:text-red-400">
									{validationErrors.categories}
								</p>
							{/if}
						</div>

						<!-- Skill Level -->
						<div>
							<label
								for="skill_level"
								class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
							>
								{$t('worker.skillLevel.title')}
							</label>
							<select
								id="skill_level"
								bind:value={workerData.skill_level}
								on:change={(e) => handleFieldChange('skill_level', e.target.value)}
								class="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all duration-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
							>
								{#each skillLevelOptions as option}
									<option value={option.value}>{option.label}</option>
								{/each}
							</select>
						</div>

						<!-- Certifications -->
						<div>
							<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
								{$t('worker.certifications')}
							</label>
							<MultiSelect
								options={certificationOptions}
								selected={workerData.certifications}
								placeholder={$t('worker.selectCertifications')}
								onChange={handleCertificationsChange}
							/>
						</div>

						<!-- Languages -->
						<div>
							<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
								{$t('worker.languages')}
							</label>
							<MultiSelect
								options={languageOptions}
								selected={workerData.languages}
								placeholder={$t('worker.selectLanguages')}
								onChange={handleLanguagesChange}
							/>
						</div>

						<!-- Specializations -->
						<div class="lg:col-span-2">
							<label class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
								{$t('worker.specializations')}
							</label>
							<MultiSelect
								options={specializationOptions}
								selected={workerData.specializations}
								placeholder={$t('worker.selectSpecializations')}
								onChange={handleSpecializationsChange}
							/>
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}

	<!-- Step 4: Documents & Review -->
	{#if currentStep === 4}
		<div class="step-content p-8" transition:fade={{ duration: 300 }}>
			<div class="space-y-8">
				<!-- Profile Image -->
				<div>
					<h3 class="mb-4 flex items-center text-lg font-semibold text-gray-900 dark:text-white">
						<svg
							class="mr-2 h-5 w-5 text-indigo-500"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
							/>
						</svg>
						{$t('worker.profileImage')}
					</h3>
					<FileUploader
						files={workerData.profile_image ? [workerData.profile_image] : []}
						onChange={onProfileImageUpload}
						acceptedTypes="image/*"
						maxFiles={1}
						maxSize={5 * 1024 * 1024}
						preview={true}
					/>
				</div>

				<!-- Documents -->
				<div>
					<h3 class="mb-4 flex items-center text-lg font-semibold text-gray-900 dark:text-white">
						<svg
							class="mr-2 h-5 w-5 text-green-500"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
							/>
						</svg>
						{$t('worker.documents')}
					</h3>
					<FileUploader
						files={workerData.documents}
						onChange={onDocumentUpload}
						acceptedTypes="application/pdf,image/*"
						maxFiles={10}
						maxSize={10 * 1024 * 1024}
						multiple={true}
					/>
				</div>

				<!-- Notes -->
				<div>
					<label
						for="notes"
						class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
					>
						{$t('worker.notes')}
					</label>
					<textarea
						id="notes"
						bind:value={workerData.notes}
						on:input={(e) => handleFieldChange('notes', e.target.value)}
						rows="4"
						class="w-full resize-none rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 placeholder-gray-500 transition-all duration-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
						placeholder={$t('worker.notesPlaceholder')}
					></textarea>
				</div>

				<!-- Worker Summary -->
				<div>
					<h3 class="mb-4 flex items-center text-lg font-semibold text-gray-900 dark:text-white">
						<svg
							class="mr-2 h-5 w-5 text-orange-500"
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
						{$t('worker.summary')}
					</h3>
					<div
						class="rounded-xl border border-gray-200 bg-gradient-to-r from-gray-50 to-orange-50 p-6 dark:border-gray-600 dark:from-gray-700 dark:to-orange-900/20"
					>
						<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
							<div>
								<h4 class="mb-3 font-medium text-gray-900 dark:text-white">
									{$t('worker.personalInfo')}
								</h4>
								<dl class="space-y-2 text-sm">
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">{$t('worker.fullName')}:</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{workerData.full_name || '-'}
										</dd>
									</div>
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">{$t('worker.email')}:</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{workerData.email || '-'}
										</dd>
									</div>
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">{$t('worker.phone')}:</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{workerData.phone || '-'}
										</dd>
									</div>
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">{$t('worker.department')}:</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{departmentOptions.find((d) => d.value === workerData.department)?.label ||
												'-'}
										</dd>
									</div>
								</dl>
							</div>
							<div>
								<h4 class="mb-3 font-medium text-gray-900 dark:text-white">
									{$t('worker.employmentInfo')}
								</h4>
								<dl class="space-y-2 text-sm">
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">{$t('worker.employeeId')}:</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{workerData.employee_id || '-'}
										</dd>
									</div>
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">{$t('worker.hireDate')}:</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{workerData.hire_date || '-'}
										</dd>
									</div>
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">{$t('worker.hourlyRate')}:</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{formatCurrency(workerData.hourly_rate) || '-'}
										</dd>
									</div>
									<div class="flex justify-between">
										<dt class="text-gray-500 dark:text-gray-400">
											{$t('worker.skillLevel.title')}:
										</dt>
										<dd class="font-medium text-gray-900 dark:text-white">
											{skillLevelOptions.find((s) => s.value === workerData.skill_level)?.label ||
												'-'}
										</dd>
									</div>
								</dl>
							</div>
						</div>
					</div>
				</div>

				<!-- Status Toggle -->
				<div class="flex items-center justify-between rounded-lg bg-gray-50 p-4 dark:bg-gray-700">
					<div>
						<label for="is_active" class="text-sm font-medium text-gray-700 dark:text-gray-300">
							{$t('worker.activeStatus')}
						</label>
						<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
							{$t('worker.activeStatusDescription')}
						</p>
					</div>
					<label class="relative inline-flex cursor-pointer items-center">
						<input
							type="checkbox"
							id="is_active"
							bind:checked={workerData.is_active}
							on:change={(e) => handleFieldChange('is_active', e.target.checked)}
							class="peer sr-only"
						/>
						<div
							class="peer h-6 w-11 rounded-full bg-gray-200 peer-checked:bg-orange-600 peer-focus:ring-4 peer-focus:ring-orange-300 peer-focus:outline-none after:absolute after:top-[2px] after:left-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:after:translate-x-full peer-checked:after:border-white dark:border-gray-600 dark:bg-gray-700 dark:peer-focus:ring-orange-800"
						></div>
					</label>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	/* Step content animations */
	.step-content {
		animation: slide-up 0.3s ease-out;
	}

	@keyframes slide-up {
		from {
			opacity: 0;
			transform: translateY(20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	/* Custom toggle switch animations */
	input[type='checkbox']:checked + div {
		background: linear-gradient(135deg, #ea580c 0%, #f59e0b 100%);
	}

	/* Enhanced form field focus states */
	input:focus,
	select:focus,
	textarea:focus {
		box-shadow: 0 0 0 3px rgba(234, 88, 12, 0.1);
		border-color: #ea580c;
	}
</style>
