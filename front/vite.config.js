import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
	plugins: [tailwindcss(), sveltekit()],
	server: {
		host: '0.0.0.0',
		port: 5173,
		watch: { usePolling: true, interval: 1000 },
		cors: true,
		allowedHosts: ['auction.pinealdevelopers.com'],
		fs: {
			strict: false
		}
	},
	resolve: {
		alias: {
			'plotly.js-dist-min': 'plotly.js-dist-min'
		}
	},
	build: {
		target: 'esnext',
		minify: 'esbuild',
		rollupOptions: {
			output: {
				manualChunks: {
					vendor: ['chart.js', 'date-fns', 'leaflet'],
					plotly: ['plotly.js-dist-min']
				}
			}
		}
	},
	optimizeDeps: {
		include: ['chart.js', 'date-fns', 'leaflet', 'plotly.js-dist-min'],
		force: false
	},
	clearScreen: false
});
