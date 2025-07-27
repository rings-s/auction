<!-- src/routes/property-management/workers/create/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { t, locale } from '$lib/i18n';
	import { user } from '$lib/stores/user.svelte.js';
	import { workersAPI } from '$lib/api/propertyManagement.js';

	import WorkerCreateHeader from '$lib/components/property-management/workers/create/WorkerCreateHeader.svelte';
	import WorkerCreateTabs from '$lib/components/property-management/workers/create/WorkerCreateTabs.svelte';
	import WorkerCreateFooter from '$lib/components/property-management/workers/create/WorkerCreateFooter.svelte';
	import Alert from '$lib/components/ui/Alert.svelte';

	let isRTL = $derived($locale === 'ar');

	// State
	let currentStep = 1;
	let totalSteps = 4;
	let loading = false;
	let submitting = false;
	let error = '';
	let success = false;

	// Worker data
	let workerData = {
		// Step 1: Personal Information
		full_name: '',
		email: '',
		phone: '',
		date_of_birth: '',
		national_id: '',
		emergency_contact_name: '',
		emergency_contact_phone: '',

		// Step 2: Employment Details
		employee_id: '',
		hire_date: '',
		employment_type: 'full_time',
		status: 'active',
		department: '',
		position: '',
		hourly_rate: '',

		// Step 3: Skills & Categories
		categories: [],
		skill_level: 'intermediate',
		certifications: [],
		languages: [],
		experience_years: '',
		specializations: [],

		// Step 4: Documents & Review
		profile_image: null,
		documents: [],
		notes: '',
		is_active: true
	};

	// Validation errors
	let validationErrors = {};

	// Options data
	let employmentTypeOptions = [
		{ value: 'full_time', label: $t('worker.employmentType.fullTime') },
		{ value: 'part_time', label: $t('worker.employmentType.partTime') },
		{ value: 'contract', label: $t('worker.employmentType.contract') },
		{ value: 'temporary', label: $t('worker.employmentType.temporary') }
	];

	let statusOptions = [
		{ value: 'active', label: $t('worker.status.active') },
		{ value: 'inactive', label: $t('worker.status.inactive') },
		{ value: 'on_leave', label: $t('worker.status.onLeave') }
	];

	let skillLevelOptions = [
		{ value: 'beginner', label: $t('worker.skillLevel.beginner') },
		{ value: 'intermediate', label: $t('worker.skillLevel.intermediate') },
		{ value: 'advanced', label: $t('worker.skillLevel.advanced') },
		{ value: 'expert', label: $t('worker.skillLevel.expert') }
	];

	let categoryOptions = [
		{ value: 'plumbing', label: $t('worker.category.plumbing') },
		{ value: 'electrical', label: $t('worker.category.electrical') },
		{ value: 'hvac', label: $t('worker.category.hvac') },
		{ value: 'carpentry', label: $t('worker.category.carpentry') },
		{ value: 'painting', label: $t('worker.category.painting') },
		{ value: 'landscaping', label: $t('worker.category.landscaping') },
		{ value: 'cleaning', label: $t('worker.category.cleaning') },
		{ value: 'security', label: $t('worker.category.security') },
		{ value: 'maintenance', label: $t('worker.category.maintenance') },
		{ value: 'appliance_repair', label: $t('worker.category.applianceRepair') }
	];

	let departmentOptions = [
		{ value: 'maintenance', label: $t('worker.department.maintenance') },
		{ value: 'security', label: $t('worker.department.security') },
		{ value: 'cleaning', label: $t('worker.department.cleaning') },
		{ value: 'landscaping', label: $t('worker.department.landscaping') },
		{ value: 'administration', label: $t('worker.department.administration') }
	];

	let languageOptions = [
		{ value: 'arabic', label: $t('language.arabic') },
		{ value: 'english', label: $t('language.english') },
		{ value: 'hindi', label: $t('language.hindi') },
		{ value: 'urdu', label: $t('language.urdu') },
		{ value: 'tagalog', label: $t('language.tagalog') },
		{ value: 'bengali', label: $t('language.bengali') }
	];

	// Permissions
	let canCreate = $derived(
		$user &&
			(['owner', 'appraiser', 'data_entry'].includes($user.role) ||
				$user.is_staff ||
				$user.is_superuser)
	);

	onMount(() => {
		if (!canCreate) {
			goto('/dashboard');
			return;
		}

		// Generate employee ID
		generateEmployeeId();
	});

	function generateEmployeeId() {
		const prefix = 'WKR';
		const timestamp = Date.now().toString().slice(-6);
		const random = Math.floor(Math.random() * 100)
			.toString()
			.padStart(2, '0');
		workerData.employee_id = `${prefix}-${timestamp}${random}`;
	}

	// Navigation handlers
	function handleNext() {
		if (validateCurrentStep()) {
			currentStep++;
		}
	}

	function handlePrev() {
		currentStep--;
		error = '';
	}

	// Validation
	function validateCurrentStep() {
		validationErrors = {};
		let isValid = true;

		switch (currentStep) {
			case 1: // Personal Information
				if (!workerData.full_name?.trim()) {
					validationErrors.full_name = $t('validation.required', { field: $t('worker.fullName') });
					isValid = false;
				}
				if (!workerData.email?.trim()) {
					validationErrors.email = $t('validation.required', { field: $t('worker.email') });
					isValid = false;
				} else if (!/\S+@\S+\.\S+/.test(workerData.email)) {
					validationErrors.email = $t('validation.email');
					isValid = false;
				}
				if (!workerData.phone?.trim()) {
					validationErrors.phone = $t('validation.required', { field: $t('worker.phone') });
					isValid = false;
				}
				break;

			case 2: // Employment Details
				if (!workerData.hire_date) {
					validationErrors.hire_date = $t('validation.required', { field: $t('worker.hireDate') });
					isValid = false;
				}
				if (!workerData.hourly_rate || workerData.hourly_rate <= 0) {
					validationErrors.hourly_rate = $t('validation.required', {
						field: $t('worker.hourlyRate')
					});
					isValid = false;
				}
				break;

			case 3: // Skills & Categories
				if (!workerData.categories.length) {
					validationErrors.categories = $t('validation.required', {
						field: $t('worker.categories')
					});
					isValid = false;
				}
				break;

			case 4: // Documents & Review
				// Optional validation for final step
				break;
		}

		return isValid;
	}

	// Submit handler
	async function handleSubmit() {
		if (!validateCurrentStep()) {
			return;
		}

		try {
			submitting = true;
			error = '';

			// Prepare form data
			const formData = new FormData();

			// Add all worker data
			Object.keys(workerData).forEach((key) => {
				if (
					key === 'categories' ||
					key === 'certifications' ||
					key === 'languages' ||
					key === 'specializations'
				) {
					formData.append(key, JSON.stringify(workerData[key]));
				} else if (key === 'profile_image' && workerData[key]) {
					formData.append(key, workerData[key]);
				} else if (key === 'documents' && workerData[key].length > 0) {
					workerData[key].forEach((doc, index) => {
						formData.append(`document_${index}`, doc.file);
						formData.append(`document_${index}_type`, doc.type);
					});
				} else if (workerData[key] !== null && workerData[key] !== '') {
					formData.append(key, workerData[key]);
				}
			});

			// Create worker
			const response = await workersAPI.create(formData);

			success = true;

			// Redirect to worker detail page after success
			setTimeout(() => {
				goto(`/property-management/workers/${response.data.id}`);
			}, 1500);
		} catch (err) {
			error = err.message || $t('worker.createFailed');
			console.error('Failed to create worker:', err);
		} finally {
			submitting = false;
		}
	}

	// Handle form data changes
	function handleDataChange(field, value) {
		workerData[field] = value;
		// Clear validation error for this field
		if (validationErrors[field]) {
			delete validationErrors[field];
			validationErrors = { ...validationErrors };
		}
	}

	function handleCategoriesChange(event) {
		workerData.categories = event.detail;
		if (validationErrors.categories) {
			delete validationErrors.categories;
			validationErrors = { ...validationErrors };
		}
	}

	function handleDocumentUpload(event) {
		workerData.documents = event.detail;
	}

	function handleProfileImageUpload(event) {
		workerData.profile_image = event.detail;
	}
</script>

<svelte:head>
	<title>{$t('worker.create')} | {$t('app.name')}</title>
	<meta name="description" content={$t('worker.createDescription')} />
</svelte:head>

<div
	class="min-h-screen bg-gradient-to-br from-slate-50 via-orange-50 to-amber-50 dark:from-gray-900 dark:via-orange-900 dark:to-amber-900"
	dir={isRTL ? 'rtl' : 'ltr'}
>
	<div class="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
		<!-- Success Message ---->
		{#if success}
			<div class="mx-auto mb-6 max-w-3xl">
				<Alert
					type="success"
					title={$t('worker.createSuccess')}
					message={$t('worker.createSuccessMessage')}
				/>
			</div>
		{/if}

		<!-- Error Message -->
		{#if error}
			<div class="mx-auto mb-6 max-w-3xl">
				<Alert type="error" message={error} />
			</div>
		{/if}

		<!-- Create Worker Form -->
		<div class="mx-auto max-w-4xl">
			<!-- Header -->
			<WorkerCreateHeader {currentStep} {totalSteps} {loading} />

			<!-- Form Content -->
			<WorkerCreateTabs
				{currentStep}
				{workerData}
				{validationErrors}
				{employmentTypeOptions}
				{statusOptions}
				{skillLevelOptions}
				{categoryOptions}
				{departmentOptions}
				{languageOptions}
				onChange={handleDataChange}
				onCategoriesChange={handleCategoriesChange}
				onDocumentUpload={handleDocumentUpload}
				onProfileImageUpload={handleProfileImageUpload}
			/>

			<!-- Footer -->
			<WorkerCreateFooter
				{currentStep}
				{totalSteps}
				loading={submitting}
				onNext={handleNext}
				onPrev={handlePrev}
				onSubmit={handleSubmit}
			/>
		</div>
	</div>
</div>

<style>
	/* Enhanced orange-amber theme for worker creation */
	:global(.worker-create-theme) {
		--primary-gradient: linear-gradient(135deg, #ea580c 0%, #f59e0b 50%, #eab308 100%);
		--accent-color: #ea580c;
		--accent-light: #fed7aa;
		--accent-dark: #c2410c;
	}

	/* Smooth transitions for better UX */
	* {
		transition: all 0.2s ease-in-out;
	}

	/* Custom gradient animations */
	@keyframes gradient-shift {
		0%,
		100% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 100% 50%;
		}
	}

	.bg-gradient-to-br {
		background-size: 200% 200%;
		animation: gradient-shift 8s ease infinite;
	}
</style>
