import "dotenv/config";
import { defineConfig, env } from "prisma/config";

export default defineConfig({
  schema: "prisma/schema.prisma",
  migrations: {
    path: "prisma/migrations",
  },
  datasource: {
    url: env("DATABASE_URL"),
  },
  experimental: {
    externalTables: true,
  },
  tables: {
    external: [
      "public.track_features",
      "public.alembic_version",
      "public.jobs",
    ],
  },
});
