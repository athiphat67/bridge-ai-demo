import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// dev server :5173, proxy /api → FastAPI :8000 (เลี่ยงปัญหา CORS ตอน dev)
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_PROXY_TARGET || 'http://localhost:8000',
        changeOrigin: true,
        timeout: 120_000,       // 2 min — ONNX first-load can be slow
      },
    },
  },
})
