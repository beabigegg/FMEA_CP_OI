import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      // Proxying API requests to the backend server
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      // Proxying auth requests
      '/auth': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    }
  }
})
