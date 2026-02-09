import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    // Enable CORS for local development
    proxy: {
      // Optional: proxy API calls to avoid CORS in development
      // Uncomment if you want /api/* to proxy to backend
      // '/api': {
      //   target: 'http://localhost:8000',
      //   changeOrigin: true,
      //   rewrite: (path) => path.replace(/^\/api/, '')
      // }
    },
  },
});
