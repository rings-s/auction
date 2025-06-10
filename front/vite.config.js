import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [tailwindcss(), sveltekit()], // Removed config reference for Tailwind v4
	server: {
		host: '0.0.0.0',
		port: 5173,
		allowedHosts: [
			'localhost',
			'127.0.0.1',
			'auction.pinealdevelopers.com',
			'.pinealdevelopers.com'
		],
		watch: {
			usePolling: true,
			interval: 1000
		}
	},
	optimizeDeps: {
		exclude: ['clsx'],
		include: ['chart.js', 'date-fns', 'leaflet'],
		force: true
	},
	build: {
		rollupOptions: {
			output: {
				manualChunks: undefined
			}
		}
	}
});