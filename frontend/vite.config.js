import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  css: {
    // Explicitly set empty PostCSS config to prevent Vite from
    // picking up postcss.config.js from parent directories
    postcss: {
      plugins: []
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/health':    'http://localhost:8000',
      '/ask':       'http://localhost:8000',
      '/anomalies': 'http://localhost:8000',
    }
  }
})
