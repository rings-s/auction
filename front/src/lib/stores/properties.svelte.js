// Properties store using Svelte 5 runes
let propertiesList = $state([]);

// Create store object that provides subscribe method for $ syntax compatibility
function createPropertiesStore() {
	const subscribers = new Set();

	function notify() {
		subscribers.forEach((fn) => fn(propertiesList));
	}

	return {
		// Subscribe method for $ syntax compatibility
		subscribe(fn) {
			subscribers.add(fn);
			fn(propertiesList); // Call immediately with current value
			return () => subscribers.delete(fn);
		},

		get value() {
			return propertiesList;
		},

		set(newProperties) {
			propertiesList = newProperties;
			notify();
		},

		update(updater) {
			propertiesList = updater(propertiesList);
			notify();
		},

		add(property) {
			propertiesList = [...propertiesList, property];
			notify();
		},

		remove(propertyId) {
			propertiesList = propertiesList.filter((p) => p.id !== propertyId);
			notify();
		},

		clear() {
			propertiesList = [];
			notify();
		}
	};
}

export const properties = createPropertiesStore();
