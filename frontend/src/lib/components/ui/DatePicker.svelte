<!-- src/lib/components/ui/DatePicker.svelte -->
<script>
    /**
     * DatePicker Component
     * A customizable date picker with calendar dropdown.
     */
    import { createEventDispatcher, onMount } from 'svelte';
    import { fade } from 'svelte/transition';
    import { language } from '$lib/i18n';
    import Button from './Button.svelte';
    import Input from './Input.svelte';
    
    const dispatch = createEventDispatcher();
    
    // Props
    export let value = ""; // ISO date string or Date object
    export let label = ""; // Input label
    export let placeholder = "Select date"; // Placeholder text
    export let format = "yyyy-MM-dd"; // Display format
    export let min = null; // Minimum selectable date
    export let max = null; // Maximum selectable date
    export let disabled = false; // Disabled state
    export let required = false; // Required state
    export let error = ""; // Error message
    export let name = ""; // Input name
    export let id = name || `date-${Math.random().toString(36).substring(2, 9)}`; // Input ID
    export let icon = true; // Show calendar icon
    export let clearable = true; // Allow clearing the date
    export let disabledDates = []; // Array of disabled dates
    export let disabledDays = []; // Array of disabled days (0-6, 0 is Sunday)
    export let size = "default"; // sm, default, lg
    
    // Local state
    let isOpen = false;
    let inputElement;
    let calendarElement;
    let currentMonth;
    let currentYear;
    let dateObject = null;
    let internalValue = "";
    let isRTL = false;
    
    // Set RTL based on language
    $: isRTL = $language === 'ar';
    
    // Day names based on locale
    const dayNames = Array.from({ length: 7 }, (_, i) => {
      const date = new Date(2021, 0, 3 + i); // Jan 3, 2021 is a Sunday
      return date.toLocaleDateString(isRTL ? 'ar' : 'en', { weekday: 'short' });
    });
    
    // Month names based on locale
    const monthNames = Array.from({ length: 12 }, (_, i) => {
      const date = new Date(2021, i, 1);
      return date.toLocaleDateString(isRTL ? 'ar' : 'en', { month: 'long' });
    });
    
    // Format date for display
    function formatDate(date) {
      if (!date) return "";
      
      try {
        if (typeof date === 'string') {
          date = new Date(date);
        }
        
        if (isNaN(date.getTime())) return "";
        
        // Simple formatter - can be enhanced with a proper formatting library
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        
        if (format === 'yyyy-MM-dd') {
          return `${year}-${month}-${day}`;
        } else if (format === 'MM/dd/yyyy') {
          return `${month}/${day}/${year}`;
        } else if (format === 'dd/MM/yyyy') {
          return `${day}/${month}/${year}`;
        }
        
        return `${year}-${month}-${day}`;
      } catch (e) {
        return "";
      }
    }
    
    // Parse string to date object
    function parseDate(dateStr) {
      if (!dateStr) return null;
      
      if (dateStr instanceof Date) {
        return isNaN(dateStr.getTime()) ? null : dateStr;
      }
      
      try {
        const date = new Date(dateStr);
        return isNaN(date.getTime()) ? null : date;
      } catch (e) {
        return null;
      }
    }
    
    // Initialize component
    onMount(() => {
      dateObject = parseDate(value);
      internalValue = formatDate(dateObject);
      
      if (dateObject) {
        currentMonth = dateObject.getMonth();
        currentYear = dateObject.getFullYear();
      } else {
        const today = new Date();
        currentMonth = today.getMonth();
        currentYear = today.getFullYear();
      }
      
      // Close calendar when clicking outside
      function handleClickOutside(event) {
        if (isOpen && 
            inputElement && 
            !inputElement.contains(event.target) && 
            calendarElement && 
            !calendarElement.contains(event.target)) {
          isOpen = false;
        }
      }
      
      document.addEventListener('mousedown', handleClickOutside);
      
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    });
    
    // Toggle calendar
    function toggleCalendar() {
      if (disabled) return;
      isOpen = !isOpen;
    }
    
    // Get days in month
    function getDaysInMonth(year, month) {
      return new Date(year, month + 1, 0).getDate();
    }
    
    // Get day of week (0-6) for first day of month
    function getFirstDayOfMonth(year, month) {
      return new Date(year, month, 1).getDay();
    }
    
    // Generate calendar days
    $: calendarDays = generateCalendarDays(currentYear, currentMonth);
    
    function generateCalendarDays(year, month) {
      const days = [];
      const firstDay = getFirstDayOfMonth(year, month);
      const daysInMonth = getDaysInMonth(year, month);
      
      // Previous month days
      const prevMonthDays = getDaysInMonth(year, month - 1);
      for (let i = firstDay - 1; i >= 0; i--) {
        days.push({
          day: prevMonthDays - i,
          month: month - 1,
          year: month === 0 ? year - 1 : year,
          currentMonth: false
        });
      }
      
      // Current month days
      for (let i = 1; i <= daysInMonth; i++) {
        days.push({
          day: i,
          month,
          year,
          currentMonth: true
        });
      }
      
      // Next month days
      const remainingCells = 42 - days.length; // 6 rows of 7 days
      for (let i = 1; i <= remainingCells; i++) {
        days.push({
          day: i,
          month: month + 1,
          year: month === 11 ? year + 1 : year,
          currentMonth: false
        });
      }
      
      return days;
    }
    
    // Navigate to previous month
    function prevMonth() {
      if (currentMonth === 0) {
        currentMonth = 11;
        currentYear--;
      } else {
        currentMonth--;
      }
    }
    
    // Navigate to next month
    function nextMonth() {
      if (currentMonth === 11) {
        currentMonth = 0;
        currentYear++;
      } else {
        currentMonth++;
      }
    }
    
    // Select date
    function selectDate(day) {
      const date = new Date(day.year, day.month, day.day);
      
      // Check if date is disabled
      if (isDateDisabled(date)) return;
      
      dateObject = date;
      internalValue = formatDate(date);
      value = date.toISOString();
      isOpen = false;
      
      dispatch('change', { value: date });
    }
    
    // Clear date
    function clearDate() {
      dateObject = null;
      internalValue = "";
      value = "";
      dispatch('change', { value: null });
    }
    
    // Check if date is today
    function isToday(day) {
      const today = new Date();
      return day.day === today.getDate() && 
             day.month === today.getMonth() && 
             day.year === today.getFullYear();
    }
    
    // Check if date is selected
    function isSelected(day) {
      if (!dateObject) return false;
      
      return day.day === dateObject.getDate() && 
             day.month === dateObject.getMonth() && 
             day.year === dateObject.getFullYear();
    }
    
    // Check if date is disabled
    function isDateDisabled(date) {
      // Check min/max constraints
      if (min && date < parseDate(min)) return true;
      if (max && date > parseDate(max)) return true;
      
      // Check disabled days of week
      if (disabledDays.includes(date.getDay())) return true;
      
      // Check specific disabled dates
      return disabledDates.some(disabledDate => {
        const disabled = parseDate(disabledDate);
        return disabled && 
               disabled.getDate() === date.getDate() && 
               disabled.getMonth() === date.getMonth() && 
               disabled.getFullYear() === date.getFullYear();
      });
    }
    
    function handleKeydown(e) {
      if (e.key === 'Escape' && isOpen) {
        isOpen = false;
      }
    }
  </script>
  
  <svelte:window on:keydown={handleKeydown} />
  
  <div class="relative" dir={isRTL ? 'rtl' : 'ltr'}>
    {#if label}
      <label 
        for={id} 
        class="block mb-1.5 text-sm font-medium text-neutral-800 dark:text-white"
      >
        {label} {#if required}<span class="text-red-500 ml-0.5">*</span>{/if}
      </label>
    {/if}
    
    <div class="relative" bind:this={inputElement}>
      <Input
        {id}
        {name}
        type="text"
        bind:value={internalValue}
        {placeholder}
        {disabled}
        readonly
        {required}
        {error}
        {size}
        on:click={toggleCalendar}
        on:focus={toggleCalendar}
        icon={icon ? 'calendar' : null}
        iconPosition="right"
      />
      
      {#if clearable && internalValue && !disabled}
        <button
          type="button"
          class="absolute inset-y-0 right-8 flex items-center pr-3 text-neutral-400 hover:text-neutral-500"
          on:click={clearDate}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      {/if}
    </div>
    
    {#if isOpen}
      <div 
        class="absolute z-10 mt-1 w-full bg-white dark:bg-neutral-800 shadow-lg rounded-lg border border-neutral-200 dark:border-neutral-700"
        bind:this={calendarElement}
        in:fade={{ duration: 150 }}
      >
        <!-- Calendar header with month/year navigation -->
        <div class="px-4 py-3 flex items-center justify-between border-b border-neutral-200 dark:border-neutral-700">
          <div>
            <span class="text-sm font-medium text-neutral-700 dark:text-neutral-300">
              {monthNames[currentMonth]} {currentYear}
            </span>
          </div>
          <div class="flex space-x-2">
            <button
              type="button"
              class="inline-flex items-center justify-center p-1 rounded-full hover:bg-neutral-100 dark:hover:bg-neutral-700"
              on:click={prevMonth}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-neutral-600 dark:text-neutral-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
            <button
              type="button"
              class="inline-flex items-center justify-center p-1 rounded-full hover:bg-neutral-100 dark:hover:bg-neutral-700"
              on:click={nextMonth}
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-neutral-600 dark:text-neutral-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Calendar days of week header -->
        <div class="grid grid-cols-7 gap-0 text-center text-xs leading-6 text-neutral-500 dark:text-neutral-400 border-b border-neutral-200 dark:border-neutral-700">
          {#each dayNames as day}
            <div class="py-2">{day}</div>
          {/each}
        </div>
        
        <!-- Calendar days grid -->
        <div class="grid grid-cols-7 gap-0 text-sm">
          {#each calendarDays as day, i}
            <div 
              class={`p-2 flex items-center justify-center cursor-pointer
                ${day.currentMonth ? 'text-neutral-900 dark:text-white' : 'text-neutral-400 dark:text-neutral-500'} 
                ${isToday(day) ? 'bg-neutral-100 dark:bg-neutral-700' : ''} 
                ${isSelected(day) ? 'bg-primary text-white hover:bg-primary-dark' : 'hover:bg-neutral-100 dark:hover:bg-neutral-700'}`}
              on:click={() => selectDate(day)}
            >
              {day.day}
            </div>
          {/each}
        </div>
        
        <!-- Calendar footer -->
        <div class="px-4 py-2 border-t border-neutral-200 dark:border-neutral-700 flex justify-between">
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => {
              const today = new Date();
              selectDate({
                day: today.getDate(),
                month: today.getMonth(),
                year: today.getFullYear(),
                currentMonth: 
                  today.getMonth() === currentMonth && 
                  today.getFullYear() === currentYear
              });
            }}
          >
            {isRTL ? 'اليوم' : 'Today'}
          </Button>
          
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => isOpen = false}
          >
            {isRTL ? 'إغلاق' : 'Close'}
          </Button>
        </div>
      </div>
    {/if}
  </div>