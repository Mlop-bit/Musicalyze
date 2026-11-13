import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    env: {
      MUSICALYZE_GITHUB_TOKEN: "test-token",
      BETTER_AUTH_SECRET: "test-secret",
      BETTER_AUTH_URL: "http://127.0.0.1:3000",
      SPOTIFY_CLIENT_ID: "test-spotify-client-id",
      SPOTIFY_CLIENT_SECRET: "test-spotify-client-secret",
      MUSICALYZE_API_KEY: "test-api-key",
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
