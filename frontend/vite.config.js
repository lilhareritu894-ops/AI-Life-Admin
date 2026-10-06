import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true, // Local network / IP testing ke liye
    open: true, // Server start hote hi browser auto-open karne ke liye
  },
  resolve: {
    alias: {
      '@': '/src', // Clean imports ke liye (e.g. import Button from '@/components/Button')
    },
  },
})