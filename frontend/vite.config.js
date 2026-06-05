import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 8861,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:8860',
        changeOrigin: true
      },
      '/avatars': {
        target: 'http://localhost:8860',
        changeOrigin: true
      }
    }
  }
})
