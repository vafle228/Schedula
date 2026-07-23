import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  // Dev-only: forward the real API to the Python backend (server/main.py on
  // :8000). Active only once src/api/client.js sets USE_MOCK = false.
  server: {
    proxy: {
      '/api/v1': 'http://127.0.0.1:8000',
    },
  },
})
