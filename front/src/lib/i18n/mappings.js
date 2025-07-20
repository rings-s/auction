// lib/i18n/mappings.js

// Consolidated feature mapping with normalized keys
export const FEATURE_MAPPING = {
	// Pool variations
	'swimming pool': 'pool',
	pool: 'pool',

	// AC variations
	'air conditioning': 'airConditioning',
	ac: 'airConditioning',
	'a/c': 'airConditioning',

	// Security variations
	'security system': 'security',
	security: 'security',

	// Parking variations
	parking: 'parking',
	'car park': 'parking',
	garage: 'garage',

	// Garden & outdoor
	garden: 'garden',
	balcony: 'balcony',
	terrace: 'terrace',

	// Building features
	elevator: 'elevator',
	lift: 'elevator',
	fireplace: 'fireplace',
	'storage room': 'storage',
	storage: 'storage',

	// Property conditions
	furnished: 'furnished',
	'pets allowed': 'petsAllowed',
	'pet friendly': 'petsAllowed',
	'wheelchair access': 'wheelchairAccess',
	accessible: 'wheelchairAccess',

	// Utilities
	'fiber internet': 'fiberInternet',
	'high-speed internet': 'fiberInternet',
	'solar panels': 'solarPanels',
	solar: 'solarPanels',
	heating: 'heating'
};

export const AMENITY_MAPPING = {
	// Fitness & wellness
	gym: 'gym',
	'fitness center': 'gym',
	spa: 'spa',
	sauna: 'sauna',

	// Recreation
	playground: 'playground',
	'kids area': 'playground',
	'bbq area': 'bbqArea',
	barbecue: 'bbqArea',
	bbq: 'bbqArea',
	'tennis court': 'tennisCourtBasketball',
	'basketball court': 'tennisCourtBasketball',
	'sports court': 'tennisCourtBasketball',

	// Services
	concierge: 'concierge',
	'concierge service': 'concierge',
	'business center': 'businessCenter',
	laundry: 'laundryService',
	'laundry service': 'laundryService',

	// Amenities
	'guest parking': 'guestParking',
	'visitor parking': 'guestParking',
	rooftop: 'rooftopDeck',
	'rooftop deck': 'rooftopDeck',
	childcare: 'childcare',
	'childcare services': 'childcare',
	'pet grooming': 'petGrooming',
	'electric car charging': 'carCharging',
	'ev charging': 'carCharging',
	'bike storage': 'bikeStorage',

	// Nearby services
	schools: 'schools',
	school: 'schools',
	'shopping centers': 'shoppingCenters',
	'shopping center': 'shoppingCenters',
	'shopping mall': 'shoppingCenters',
	mall: 'shoppingCenters',
	shops: 'shoppingCenters',
	parks: 'parks',
	park: 'parks',
	'public transportation': 'publicTransportation',
	'public transport': 'publicTransportation',
	transit: 'publicTransportation',
	'bus stop': 'publicTransportation',
	metro: 'publicTransportation',
	mosque: 'mosque',
	hospitals: 'hospitals',
	restaurants: 'restaurants',
	'beach access': 'beachAccess',
	'sports facilities': 'sportsFacilities',
	university: 'university'
};

export const ROOM_TYPE_MAPPING = {
	bedroom: 'bedroom',
	'living room': 'livingRoom',
	kitchen: 'kitchen',
	bathroom: 'bathroom',
	'dining room': 'diningRoom',
	office: 'office',
	'guest room': 'guestRoom',
	'master bedroom': 'masterBedroom',
	'children room': 'childrenRoom',
	'utility room': 'utilityRoom',
	'storage room': 'storageRoom',
	garage: 'garage',
	balcony: 'balcony',
	terrace: 'terrace',
	basement: 'basement',
	attic: 'attic',
	hallway: 'hallway',
	entrance: 'entrance',
	'laundry room': 'laundryRoom'
};

// Helper functions for mapping
export function getFeatureKey(feature) {
	if (!feature) return null;
	const normalized = feature.toLowerCase().trim();
	return FEATURE_MAPPING[normalized] || null;
}

export function getAmenityKey(amenity) {
	if (!amenity) return null;
	const normalized = amenity.toLowerCase().trim();
	return AMENITY_MAPPING[normalized] || null;
}

export function getRoomTypeKey(roomType) {
	if (!roomType) return null;
	const normalized = roomType.toLowerCase().trim();
	return ROOM_TYPE_MAPPING[normalized] || null;
}
