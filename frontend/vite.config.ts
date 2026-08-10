import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  return {
    plugins: [react()],
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'https://traffic-twinflow-ai.onrender.com',
          changeOrigin: true,
        },
        '/ws': {
          target: env.VITE_WS_URL || 'wss://twinflow-backend.onrender.com/ws',
          ws: true,
        },
      },
    },
    define: {
      'process.env.VITE_MAPBOX_TOKEN': JSON.stringify(env.VITE_MAPBOX_TOKEN),
    },
  };
});