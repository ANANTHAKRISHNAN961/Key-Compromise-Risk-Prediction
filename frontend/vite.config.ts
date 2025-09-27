import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path' // <-- ADD THIS IMPORT

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  // ADD THIS ENTIRE 'resolve' BLOCK
  resolve: {
    alias: {
      'react': path.resolve(__dirname, './node_modules/react'),
      'react-dom': path.resolve(__dirname, './node_modules/react-dom'),
    }
  }
})