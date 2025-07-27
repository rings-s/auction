// Auctions store using Svelte 5 runes
let auctionsList = $state([]);

// Create store object that provides subscribe method for $ syntax compatibility
function createAuctionsStore() {
	const subscribers = new Set();

	function notify() {
		subscribers.forEach((fn) => fn(auctionsList));
	}

	return {
		// Subscribe method for $ syntax compatibility
		subscribe(fn) {
			subscribers.add(fn);
			fn(auctionsList); // Call immediately with current value
			return () => subscribers.delete(fn);
		},

		get value() {
			return auctionsList;
		},

		set(newAuctions) {
			auctionsList = newAuctions;
			notify();
		},

		update(updater) {
			auctionsList = updater(auctionsList);
			notify();
		},

		add(auction) {
			auctionsList = [...auctionsList, auction];
			notify();
		},

		remove(auctionId) {
			auctionsList = auctionsList.filter((a) => a.id !== auctionId);
			notify();
		},

		clear() {
			auctionsList = [];
			notify();
		}
	};
}

export const auctions = createAuctionsStore();
