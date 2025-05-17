<script>
  import { onMount } from 'svelte';
  import { auctions } from '$lib/stores/auctions.js';
  import { fetchAuctions } from '$lib/api/auction.js';

  let loading = true;
  let error = '';
  let data = [];

  onMount(async () => {
    try {
      loading = true;
      error = '';
      data = await fetchAuctions();
      auctions.set(data);
    } catch (e) {
      error = e.message || 'Error loading auctions';
    } finally {
      loading = false;
    }
  });
</script>

<main class="min-h-screen bg-gray-50 py-8 px-4">
  <h1 class="text-3xl font-bold mb-8 text-center text-gray-800">Auctions</h1>

  {#if loading}
    <div class="flex justify-center items-center h-40">
      <span class="text-gray-500 animate-pulse">Loading auctions...</span>
    </div>
  {:else if error}
    <div class="flex justify-center items-center h-40">
      <span class="text-red-600">{error}</span>
    </div>
  {:else if data.length === 0}
    <div class="flex justify-center items-center h-40">
      <span class="text-gray-500">No auctions found.</span>
    </div>
  {:else}
    <section class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {#each data as auction}
        <article class="bg-white rounded-lg shadow hover:shadow-lg transition-shadow border border-gray-100 p-6 flex flex-col justify-between">
          <div>
            <h2 class="text-xl font-semibold text-blue-700 mb-2 truncate" title={auction.title}>{auction.title}</h2>
            <p class="text-gray-600 text-sm mb-4 line-clamp-2">{auction.description}</p>
            <div class="flex flex-wrap gap-2 mb-2">
              <span class="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">{auction.status}</span>
              <span class="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded">{auction.auction_type}</span>
            </div>
            <div class="text-gray-500 text-xs mb-2">
              Start: {auction.start_date?.slice(0, 10)}<br>
              End: {auction.end_date?.slice(0, 10)}
            </div>
          </div>
          <a class="mt-4 inline-block text-center bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2 px-4 rounded transition-colors" href={"/auctions/" + auction.slug}>
            View Auction
          </a>
        </article>
      {/each}
    </section>
  {/if}
</main>