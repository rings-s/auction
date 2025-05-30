import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
	plugins: [tailwindcss({ config: path.resolve(__dirname, 'tailwind.config.js') }), sveltekit()],
	server: {
		host: '0.0.0.0',
		port: 5173,
		watch: {
			usePolling: true,  // Essential for Docker file watching
			interval: 1000
		}
	}
});