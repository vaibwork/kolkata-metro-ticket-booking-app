import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const rootIndexFallback = () => ({
  name: 'root-index-fallback',
  configureServer(server) {
    server.middlewares.use((req, _res, next) => {
      if (req.url === '/' || req.url === '') {
        req.url = '/index.html'
      }
      next()
    })
  },
  configurePreviewServer(server) {
    server.middlewares.use((req, _res, next) => {
      if (req.url === '/' || req.url === '') {
        req.url = '/index.html'
      }
      next()
    })
  },
})

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [rootIndexFallback(), react()],
  server: {
    port: 5173,
    host: true,
    allowedHosts: true
  },
  preview: {
    host: true,
    allowedHosts: true
  }
})
