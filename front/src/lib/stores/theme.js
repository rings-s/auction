// src/lib/stores/theme.js
import { writable } from 'svelte/store';

// Initialize with 'light' or check user preference
export const theme = writable('light');