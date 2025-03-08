<!-- src/routes/+page.svelte -->
<script>
    import { onMount } from 'svelte';
    import ModernHero from '$lib/components/home/ModernHero.svelte';
    
    let showPage = false;
    
    onMount(() => {
      // Small delay to ensure smooth page transition
      setTimeout(() => {
        showPage = true;
      }, 100);
    });
  </script>
  
  <svelte:head>
    <title>Gudit Auction Platform | Discover Exclusive Auctions</title>
    <meta name="description" content="Gudit is the most trusted platform to bid, win, and acquire unique items with transparent, secure bidding processes, all in real-time." />
  </svelte:head>
  
  {#if showPage}
    <div class="page-transition">
      <!-- Modern Hero Section -->
      <ModernHero />
      
      <!-- Additional page content would go below -->
    </div>
  {/if}
  
  <style>
    .page-transition {
      animation: fadeIn 0.5s ease-out forwards;
    }
    
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    
    /* Ensure body styles match Gudit's design with custom cursor */
    :global(body) {
      background-color: #fff;
      margin: 0;
      padding: 0;
      overflow-x: hidden;
      font-family: 'Inter', sans-serif;
      cursor: default;
    }
    
    /* Add smooth scrolling */
    :global(html) {
      scroll-behavior: smooth;
    }
  </style>