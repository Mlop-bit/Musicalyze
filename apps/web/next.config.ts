import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@musicalyze/db"],
  allowedDevOrigins: ["127.0.0.1"],
};

export default nextConfig;
