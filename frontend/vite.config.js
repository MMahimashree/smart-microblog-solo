import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Backend runs on FastAPI (uvicorn) — default dev port 8000.
// Change VITE_API_BASE_URL in .env if your backend runs elsewhere.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
});
