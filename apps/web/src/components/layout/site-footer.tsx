import Link from "next/link";
import { GITHUB_OWNER, GITHUB_REPO } from "@/server/github/constants";

const GITHUB_URL = `https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}`;

export function SiteFooter() {
  return (
    <footer className="mx-auto flex w-full max-w-6xl flex-col gap-4 border-t border-border px-6 py-10 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between sm:px-10">
      <p>Musicalyze - signal reconstruction</p>
      <div className="flex items-center gap-6">
        <Link
          href="/changelog"
          className="transition-colors hover:text-foreground"
        >
          Changelog
        </Link>
        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noreferrer"
          className="transition-colors hover:text-foreground"
        >
          GitHub
        </a>
      </div>
    </footer>
  );
}
