<!-- src/lib/components/ui/DateRangePicker.svelte -->
<script>
    import { createEventDispatcher, onMount, onDestroy } from 'svelte';
    import { fade } from 'svelte/transition';
    
    // Props
    export let startDate = null; // Start date (Date object or ISO string)
    export let endDate = null; // End date (Date object or ISO string)
    export let minDate = null; // Minimum selectable date
    export let maxDate = null; // Maximum selectable date
    export let placeholder = 'Select date range'; // Placeholder text
    export let format = 'yyyy-MM-dd'; // Date format
    export let label = ''; // Label for the input
    export let name = ''; // Name for form fields
    export let disabled = false; // Whether the picker is disabled
    export let required = false; // Whether the picker is required
    export let error = ''; // Error message
    export let allowSingleDate = false; // Whether to allow selecting just a start date with no end date
    export let singlePicker = false; // Show only one month at a time (for mobile)
    export let disabledDates = []; // Array of dates to disable
    export let customClass = ''; // Additional custom class
    export let fullWidth = false; // Whether to take full width
    export let locale = 'en-US'; // Locale for date formatting
    export let showWeekNumbers = false; // Whether to show week numbers
    export let firstDayOfWeek = 0; // 0 = Sunday, 1 = Monday, etc.
    export let startDatePlaceholder = 'Start date'; // Placeholder for start date
    export let endDatePlaceholder = 'End date'; // Placeholder for end date
    export let clearable = true; // Whether dates can be cleared
    
    // Internal state
    let isOpen = false;
    let selecting = 'start'; // 'start' or 'end'
    let calendarDate = new Date(); // Currently displayed month
    let hoverDate = null; // Date being hovered for preview
    let pickerRef;
    let inputRef;
    let startInputRef;
    let endInputRef;
    
    // Event dispatcher
    const dispatch = createEventDispatcher();
    
    // Parse dates on initial load
    onMount(() => {
      // Parse the initial dates if they're strings
      if (startDate && typeof startDate === 'string') {
        startDate = new Date(startDate);
      }
      
      if (endDate && typeof endDate === 'string') {
        endDate = new Date(endDate);
      }
      
      // If we have a start date, set the calendar to that month
      if (startDate) {
        calendarDate = new Date(startDate);
      }
      
      // Set up click outside listener
      document.addEventListener('click', handleClickOutside);
      
      return () => {
        document.removeEventListener('click', handleClickOutside);
      };
    });
    
    // Clean up event listeners
    onDestroy(() => {
      document.removeEventListener('click', handleClickOutside);
    });
    
    // Format a date according to the format string
    function formatDate(date, formatStr = format) {
      if (!date) return '';
      
      // Handle invalid dates
      if (!(date instanceof Date) || isNaN(date.getTime())) {
        return '';
      }
      
      // Use Intl.DateTimeFormat for localized date formatting
      try {
        if (formatStr === 'yyyy-MM-dd') {
          // ISO format
          return date.toISOString().split('T')[0];
        } else {
          // Localized format
          const options = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
          };
          return new Intl.DateTimeFormat(locale, options).format(date);
        }
      } catch (e) {
        console.error('Error formatting date:', e);
        return date.toDateString();
      }
    }
    
    // Parse user input
    function parseDate(dateStr) {
      if (!dateStr) return null;
      
      // Try to parse the date string
      try {
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) {
          return null;
        }
        return date;
      } catch (e) {
        return null;
      }
    }
    
    // Generate days for calendar display
    function generateCalendarDays(year, month) {
      const daysInMonth = new Date(year, month + 1, 0).getDate();
      const firstDayOfMonth = new Date(year, month, 1).getDay();
      const days = [];
      
      // Adjust for first day of week
      const adjustedFirstDay = (firstDayOfMonth - firstDayOfWeek + 7) % 7;
      
      // Add previous month's days
      for (let i = adjustedFirstDay - 1; i >= 0; i--) {
        const date = new Date(year, month, -i);
        days.push({
          date,
          day: date.getDate(),
          isCurrentMonth: false,
          isToday: isToday(date),
          isDisabled: isDateDisabled(date),
          inRange: isInRange(date),
          isStart: isStartDate(date),
          isEnd: isEndDate(date)
        });
      }
      
      // Add current month's days
      for (let i = 1; i <= daysInMonth; i++) {
        const date = new Date(year, month, i);
        days.push({
          date,
          day: i,
          isCurrentMonth: true,
          isToday: isToday(date),
          isDisabled: isDateDisabled(date),
          inRange: isInRange(date),
          isStart: isStartDate(date),
          isEnd: isEndDate(date)
        });
      }
      
      // Add next month's days to make sure we have a complete grid
      const totalDaysSoFar = days.length;
      const remainder = totalDaysSoFar % 7;
      const daysToAdd = remainder ? 7 - remainder : 0;
      
      for (let i = 1; i <= daysToAdd; i++) {
        const date = new Date(year, month + 1, i);
        days.push({
          date,
          day: i,
          isCurrentMonth: false,
          isToday: isToday(date),
          isDisabled: isDateDisabled(date),
          inRange: isInRange(date),
          isStart: isStartDate(date),
          isEnd: isEndDate(date)
        });
      }
      
      return days;
    }
    
    // Get the current visible months
    function getVisibleMonths() {
      const months = [];
      
      // Get first month
      const firstMonth = new Date(calendarDate);
      firstMonth.setDate(1);
      
      // If singlePicker, return just the current month
      if (singlePicker) {
        return [
          {
            date: firstMonth,
            year: firstMonth.getFullYear(),
            month: firstMonth.getMonth(),
            monthName: getMonthName(firstMonth),
            days: generateCalendarDays(firstMonth.getFullYear(), firstMonth.getMonth())
          }
        ];
      }
      
      // Add current month
      months.push({
        date: firstMonth,
        year: firstMonth.getFullYear(),
        month: firstMonth.getMonth(),
        monthName: getMonthName(firstMonth),
        days: generateCalendarDays(firstMonth.getFullYear(), firstMonth.getMonth())
      });
      
      // Add next month
      const secondMonth = new Date(firstMonth);
      secondMonth.setMonth(secondMonth.getMonth() + 1);
      
      months.push({
        date: secondMonth,
        year: secondMonth.getFullYear(),
        month: secondMonth.getMonth(),
        monthName: getMonthName(secondMonth),
        days: generateCalendarDays(secondMonth.getFullYear(), secondMonth.getMonth())
      });
      
      return months;
    }
    
    // Get days of the week
    function getDaysOfWeek() {
      const daysOfWeek = [];
      const baseDate = new Date(2023, 0, 1); // January 1st, 2023 was a Sunday
      
      // Adjust for first day of the week
      for (let i = 0; i < 7; i++) {
        const dayIndex = (i + firstDayOfWeek) % 7;
        baseDate.setDate(dayIndex + 1);
        
        daysOfWeek.push({
          short: baseDate.toLocaleDateString(locale, { weekday: 'short' }).slice(0, 2),
          long: baseDate.toLocaleDateString(locale, { weekday: 'long' })
        });
      }
      
      return daysOfWeek;
    }
    
    // Get month name
    function getMonthName(date) {
      return date.toLocaleDateString(locale, { month: 'long', year: 'numeric' });
    }
    
    // Check if a date is today
    function isToday(date) {
      const today = new Date();
      return date.getDate() === today.getDate() &&
             date.getMonth() === today.getMonth() &&
             date.getFullYear() === today.getFullYear();
    }
    
    // Check if a date is disabled
    function isDateDisabled(date) {
      // Check min date
      if (minDate && date < new Date(minDate)) {
        return true;
      }
      
      // Check max date
      if (maxDate && date > new Date(maxDate)) {
        return true;
      }
      
      // Check disabled dates
      if (disabledDates.length > 0) {
        return disabledDates.some(disabledDate => {
          const disabled = new Date(disabledDate);
          return date.getDate() === disabled.getDate() &&
                 date.getMonth() === disabled.getMonth() &&
                 date.getFullYear() === disabled.getFullYear();
        });
      }
      
      return false;
    }
    
    // Check if a date is the start date
    function isStartDate(date) {
      if (!startDate) return false;
      
      const start = new Date(startDate);
      return date.getDate() === start.getDate() &&
             date.getMonth() === start.getMonth() &&
             date.getFullYear() === start.getFullYear();
    }
    
    // Check if a date is the end date
    function isEndDate(date) {
      if (!endDate) return false;
      
      const end = new Date(endDate);
      return date.getDate() === end.getDate() &&
             date.getMonth() === end.getMonth() &&
             date.getFullYear() === end.getFullYear();
    }
    
    // Check if a date is in the selected range
    function isInRange(date) {
      if (!startDate || !endDate) {
        // If we're hovering while selecting the end date, show the preview range
        if (startDate && hoverDate && selecting === 'end') {
          const start = new Date(startDate);
          const hover = new Date(hoverDate);
          
          // Handle hover date before start date
          if (hover < start) {
            return date > hover && date < start;
          }
          
          return date > start && date < hover;
        }
        
        return false;
      }
      
      const start = new Date(startDate);
      const end = new Date(endDate);
      
      // Check if the date is in the range
      return date > start && date < end;
    }
    
    // Handle day click
    function handleDayClick(day) {
      if (day.isDisabled) return;
      
      if (selecting === 'start') {
        // Update start date
        startDate = day.date;
        
        // If we already have an end date and it's before the new start date,
        // clear the end date
        if (endDate && endDate < startDate) {
          endDate = null;
        }
        
        // Move to selecting end date
        selecting = 'end';
        
        // If single date selection is allowed, notify changes
        if (allowSingleDate) {
          dispatch('change', { startDate, endDate });
        }
        
      } else {
        // Selecting end date
        
        // If clicking before start date, swap them
        if (day.date < startDate) {
          endDate = new Date(startDate);
          startDate = day.date;
        } else {
          endDate = day.date;
        }
        
        // Reset selecting to start for next time
        selecting = 'start';
        
        // Notify changes
        dispatch('change', { startDate, endDate });
        
        // Close the picker if a complete range is selected
        if (!allowSingleDate || (allowSingleDate && endDate)) {
          isOpen = false;
        }
      }
    }
    
    // Handle day mouse enter for preview
    function handleDayHover(day) {
      if (!day.isDisabled) {
        hoverDate = day.date;
      }
    }
    
    // Go to previous month
    function prevMonth() {
      calendarDate.setMonth(calendarDate.getMonth() - 1);
      calendarDate = new Date(calendarDate);
    }
    
    // Go to next month
    function nextMonth() {
      calendarDate.setMonth(calendarDate.getMonth() + 1);
      calendarDate = new Date(calendarDate);
    }
    
    // Open the date picker
    function openPicker(focusStart = true) {
      if (disabled) return;
      
      isOpen = true;
      
      // Focus the appropriate input
      setTimeout(() => {
        if (focusStart && startInputRef) {
          startInputRef.focus();
        } else if (!focusStart && endInputRef) {
          endInputRef.focus();
        }
      }, 0);
    }
    
    // Handle click outside to close picker
    function handleClickOutside(event) {
      if (pickerRef && !pickerRef.contains(event.target)) {
        isOpen = false;
      }
    }
    
    // Handle input change for start date
    function handleStartDateInput(event) {
      const dateStr = event.target.value;
      const parsed = parseDate(dateStr);
      
      if (parsed) {
        startDate = parsed;
        calendarDate = new Date(parsed);
        selecting = 'end';
        
        // If single date selection is allowed, notify changes
        if (allowSingleDate) {
          dispatch('change', { startDate, endDate });
        }
      }
    }
    
    // Handle input change for end date
    function handleEndDateInput(event) {
      const dateStr = event.target.value;
      const parsed = parseDate(dateStr);
      
      if (parsed) {
        // Ensure end date is not before start date
        if (startDate && parsed < startDate) {
          endDate = null;
          event.target.value = '';
          return;
        }
        
        endDate = parsed;
        dispatch('change', { startDate, endDate });
      }
    }
    
    // Clear dates
    function clearDates() {
      startDate = null;
      endDate = null;
      selecting = 'start';
      
      dispatch('change', { startDate, endDate });
      dispatch('clear');
    }
    
    // Create display text for input
    $: displayText = startDate || endDate ? 
      `${startDate ? formatDate(startDate) : ''}${endDate ? ' - ' + formatDate(endDate) : ''}` : 
      placeholder;
    
    // Compute visible months
    $: visibleMonths = getVisibleMonths();
    
    // Compute days of week
    $: daysOfWeek = getDaysOfWeek();
    
    // Determine if a valid range is selected
    $: hasValidRange = startDate && (allowSingleDate || endDate);
  </script>
  
  <div class="date-range-picker {fullWidth ? 'w-full' : ''} {customClass}" bind:this={pickerRef}>
    <!-- Label if provided -->
    {#if label}
      <label class="block text-sm font-medium text-text-dark mb-1">
        {label}
        {#if required}
          <span class="text-red-500 ml-1">*</span>
        {/if}
      </label>
    {/if}
    
    <!-- Input field(s) -->
    <div class="relative {fullWidth ? 'w-full' : ''}">
      <!-- Combined input display (when closed) -->
      <div 
        class="flex items-center w-full px-4 py-2 bg-white border rounded-md transition-colors
          {error ? 'border-red-500 focus-within:ring-red-200' : 'border-primary-blue-200 focus-within:ring-primary-blue-200'}
          focus-within:ring-2 focus-within:border-primary-blue
          {disabled ? 'bg-gray-100 opacity-60 cursor-not-allowed' : 'cursor-pointer hover:bg-gray-50'}"
        on:click={() => openPicker()}
        on:keydown={e => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            openPicker();
          }
        }}
        tabindex={disabled ? -1 : 0}
        role="button"
        aria-haspopup="dialog"
        aria-expanded={isOpen}
      >
        <!-- Calendar icon -->
        <svg class="w-5 h-5 mr-2 text-primary-blue" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
        </svg>
        
        <!-- Display text -->
        <span class="flex-grow text-sm {!startDate && !endDate ? 'text-gray-500' : 'text-gray-900'}">
          {displayText}
        </span>
        
        <!-- Clear button (if clearable and dates selected) -->
        {#if clearable && (startDate || endDate) && !disabled}
          <button 
            type="button"
            class="ml-2 text-gray-400 hover:text-gray-600"
            on:click|stopPropagation={clearDates}
            aria-label="Clear dates"
          >
            <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        {/if}
      </div>
      
      <!-- Error message -->
      {#if error}
        <p class="mt-1 text-sm text-red-600">{error}</p>
      {/if}
      
      <!-- Hidden form inputs for forms -->
      {#if name}
        <input type="hidden" name="{name}_start" value={startDate ? formatDate(startDate, 'yyyy-MM-dd') : ''} {required} />
        <input type="hidden" name="{name}_end" value={endDate ? formatDate(endDate, 'yyyy-MM-dd') : ''} {required} />
      {/if}
      
      <!-- Date picker dropdown -->
      {#if isOpen}
        <div 
          class="absolute z-50 mt-1 bg-white rounded-md shadow-lg border border-primary-blue-200 {singlePicker ? 'w-80' : 'w-auto'}"
          transition:fade={{ duration: 150 }}
          role="dialog"
          aria-modal="true"
          aria-label="Date range picker"
        >
          <!-- Inputs for direct date entry -->
          <div class="p-3 border-b border-primary-blue-100">
            <div class="flex space-x-2">
              <!-- Start date input -->
              <div class="flex-1">
                <label for="date-start" class="block text-xs font-medium text-gray-700 mb-1">Start Date</label>
                <input
                  type="date"
                  id="date-start"
                  name="date-start"
                  class="block w-full px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-primary-blue focus:border-primary-blue"
                  bind:this={startInputRef}
                  value={startDate ? formatDate(startDate, 'yyyy-MM-dd') : ''}
                  min={minDate ? formatDate(new Date(minDate), 'yyyy-MM-dd') : ''}
                  max={maxDate ? formatDate(new Date(maxDate), 'yyyy-MM-dd') : ''}
                  on:change={handleStartDateInput}
                  placeholder={startDatePlaceholder}
                />
              </div>
              
              <!-- End date input -->
              <div class="flex-1">
                <label for="date-end" class="block text-xs font-medium text-gray-700 mb-1">End Date</label>
                <input
                  type="date"
                  id="date-end"
                  name="date-end"
                  class="block w-full px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-primary-blue focus:border-primary-blue"
                  bind:this={endInputRef}
                  value={endDate ? formatDate(endDate, 'yyyy-MM-dd') : ''}
                  min={startDate ? formatDate(startDate, 'yyyy-MM-dd') : (minDate ? formatDate(new Date(minDate), 'yyyy-MM-dd') : '')}
                  max={maxDate ? formatDate(new Date(maxDate), 'yyyy-MM-dd') : ''}
                  on:change={handleEndDateInput}
                  placeholder={endDatePlaceholder}
                />
              </div>
            </div>
          </div>
          
          <!-- Calendars -->
          <div class="{singlePicker ? 'flex-col' : 'flex'} p-2 px-1">
            {#each visibleMonths as monthData}
              <div class="calendar p-2 {singlePicker ? 'w-full' : 'w-72'}">
                <!-- Month header with navigation -->
                <div class="flex items-center justify-between mb-2">
                  <!-- Previous month button -->
                  <button
                    type="button"
                    on:click={prevMonth}
                    class="p-1 text-gray-600 hover:text-gray-900 rounded-full hover:bg-gray-100"
                    aria-label="Previous month"
                    disabled={monthData.month === 0 && monthData.year === (minDate ? new Date(minDate).getFullYear() : 0)}
                  >
                    <svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                  </button>
                  
                  <!-- Month/year display -->
                  <h3 class="font-medium text-gray-900 whitespace-nowrap">
                    {monthData.monthName}
                  </h3>
                  
                  <!-- Next month button -->
                  <button
                    type="button"
                    on:click={nextMonth}
                    class="p-1 text-gray-600 hover:text-gray-900 rounded-full hover:bg-gray-100"
                    aria-label="Next month"
                    disabled={monthData.month === 11 && monthData.year === (maxDate ? new Date(maxDate).getFullYear() : 9999)}
                  >
                    <svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                    </svg>
                  </button>
                </div>
                
                <!-- Days of week header -->
                <div class="grid grid-cols-7 mb-1 text-center">
                  {#each daysOfWeek as day}
                    <div class="text-xs font-medium text-gray-500 py-1">
                      {day.short}
                    </div>
                  {/each}
                </div>
                
                <!-- Calendar days -->
                <div class="grid grid-cols-7">
                  {#each monthData.days as day}
                    <!-- svelte-ignore a11y-click-events-have-key-events -->
                    <div
                      class="relative p-1 text-center"
                      on:click={() => handleDayClick(day)}
                      on:mouseenter={() => handleDayHover(day)}
                      role="button"
                      tabindex="0"
                      aria-label="{day.date.toLocaleDateString(locale, { year: 'numeric', month: 'long', day: 'numeric' })}{day.isStart ? ' (start date)' : ''}{day.isEnd ? ' (end date)' : ''}"
                      aria-disabled={day.isDisabled}
                      aria-selected={day.isStart || day.isEnd}
                    >
                      <div
                        class="w-8 h-8 mx-auto flex items-center justify-center rounded-full text-sm
                          {day.isStart ? 'bg-primary-blue text-white' : ''}
                          {day.isEnd ? 'bg-primary-blue text-white' : ''}
                          {day.isToday && !day.isStart && !day.isEnd ? 'border border-primary-blue-400 font-bold' : ''}
                          {day.inRange ? 'bg-primary-blue-100' : ''}
                          {!day.isCurrentMonth ? 'text-gray-400' : 'text-gray-900'}
                          {day.isDisabled ? 'text-gray-300 cursor-not-allowed' : 'cursor-pointer hover:bg-primary-blue-50'}
                        "
                      >
                        {day.day}
                      </div>
                      
                      <!-- Show start indicator -->
                      {#if day.isStart}
                        <span class="absolute bottom-0 left-1/2 transform -translate-x-1/2 text-xs text-primary-blue font-medium">
                          Start
                        </span>
                      {/if}
                      
                      <!-- Show end indicator -->
                      {#if day.isEnd}
                        <span class="absolute bottom-0 left-1/2 transform -translate-x-1/2 text-xs text-primary-blue font-medium">
                          End
                        </span>
                      {/if}
                    </div>
                  {/each}
                </div>
              </div>
            {/each}
          </div>
          
          <!-- Footer with actions -->
          <div class="p-3 border-t border-primary-blue-100 flex justify-between">
            <!-- Selected range text -->
            <div class="text-sm text-gray-700">
              {#if startDate && endDate}
                <span class="font-medium">{formatDate(startDate)} — {formatDate(endDate)}</span>
              {:else if startDate}
                <span class="font-medium">{formatDate(startDate)}</span>
                {#if !allowSingleDate}
                  <span> — Select end date</span>
                {/if}
              {:else}
                <span>Select dates</span>
              {/if}
            </div>
            
            <!-- Action buttons -->
            <div class="space-x-2">
              {#if clearable && (startDate || endDate)}
                <button
                  type="button"
                  class="px-3 py-1 text-sm text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md"
                  on:click={clearDates}
                >
                  Clear
                </button>
              {/if}
              
              <button
                type="button"
                class="px-3 py-1 text-sm text-white bg-primary-blue hover:bg-primary-blue-600 rounded-md"
                on:click={() => isOpen = false}
                disabled={!allowSingleDate && (!startDate || !endDate)}
              >
                {hasValidRange ? 'Apply' : 'Cancel'}
              </button>
            </div>
          </div>
        </div>
      {/if}
    </div>
  </div>
  
  <style>
    /* Range selection styles */
    .calendar .grid-cols-7 > div[aria-selected="true"] {
      position: relative;
      z-index: 1;
    }
    
    /* Hover effect on days */
    .calendar .grid-cols-7 > div:not([aria-disabled="true"]):hover {
      z-index: 2;
    }
    
    /* Ensure the picker has proper z-index */
    .date-range-picker {
      position: relative;
      z-index: 10;
    }
    
    /* Make sure dropdown has high z-index */
    .date-range-picker div[role="dialog"] {
      z-index: 50;
    }
  </style>