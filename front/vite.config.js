import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
	plugins: [tailwindcss({ config: path.resolve(__dirname, 'tailwind.config.js') }), sveltekit()],
	server: {
		host: '0.0.0.0',
		port: 5173,
		allowedHosts: [
			'localhost',
			'127.0.0.1',
			'auction.pinealdevelopers.com',
			'.pinealdevelopers.com',  // Allow all subdomains
			// 'all'  // Allow all hosts for development
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