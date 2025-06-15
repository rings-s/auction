import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit()
	],
	server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling: true,
      interval: 1000
    },
    hmr: {
      clientPort: 7500,
      host: 'localhost'
    },
    cors: true
  },
	optimizeDeps: {
		exclude: ['clsx'],
		include: ['chart.js', 'date-fns', 'leaflet']
	}
});