<!-- src/lib/components/LanguageSelector.svelte -->
<script>
    import { locale, locales } from '$lib/i18n/i18n';
    
    function changeLocale(e) {
      locale.set(e.target.value);
      localStorage.setItem('locale', e.target.value);
      document.documentElement.lang = e.target.value;
      document.documentElement.dir = e.target.value === 'ar' ? 'rtl' : 'ltr';
    }
  </script>
  
  <div class="relative inline-block text-left">
    <select 
      on:change={changeLocale} 
      value={$locale}
      class="block pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
    >
      {#each Object.entries($locales) as [code, name]}
        <option value={code}>{name}</option>
      {/each}
    </select>
  </div>