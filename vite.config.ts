import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
  server: {
  host: '0.0.0.0',
  hmr: {
    host: 'rovercontrol.pagekite.me',
    port: 443,
    protocol: 'wss',
    clientPort: 443
  },
  watch: {
      usePolling: true
  }
  }
});
