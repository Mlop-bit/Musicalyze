"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { authClient } from "@/lib/auth-client";
import { GITHUB_OWNER, GITHUB_REPO } from "@/server/github/constants";

const GITHUB_URL = `https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}`;

function signInWithSpotify() {
  authClient.signIn.social({ provider: "spotify", callbackURL: "/dashboard" });
}

function AuthActions() {
  const { data: session, isPending } = authClient.useSession();

  if (isPending) {
    return <div className="h-8 w-24" aria-hidden="true" />;
  }

  if (session) {
    return (
      <Link
        href="/dashboard"
        className="rounded-full bg-signal-violet px-3.5 py-1.5 text-sm font-semibold text-background transition-colors hover:bg-signal-violet/90"
      >
        {session.user.name}
      </Link>
    );
  }

  return (
    <>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={signInWithSpotify}
        className="rounded-full text-muted-foreground"
      >
        Sign in
      </Button>
      <Button
        type="button"
        size="sm"
        onClick={signInWithSpotify}
        className="rounded-full bg-signal-violet text-background hover:bg-signal-violet/90"
      >
        Sign up
      </Button>
    </>
  );
}

export function SiteHeader() {
  return (
    <header className="fixed inset-x-0 top-4 z-50 flex justify-center px-4">
      <div className="flex items-center gap-4 rounded-full border border-border bg-background/80 px-4 py-2 shadow-[0_8px_30px_-12px_rgba(0,0,0,0.15)] backdrop-blur-md sm:gap-6 sm:px-6 sm:py-2.5">
        <Link
          href="/"
          className="text-sm font-semibold text-foreground transition-colors hover:text-signal-violet"
        >
          Musicalyze
        </Link>
        <nav className="hidden items-center gap-6 text-sm text-muted-foreground md:flex">
          <Link
            href="/changelog"
            className="transition-colors hover:text-foreground"
          >
            Changelog
          </Link>
          <Link
            href="/docs"
            className="transition-colors hover:text-foreground"
          >
            Documentation
          </Link>
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noreferrer"
            className="transition-colors hover:text-foreground"
          >
            GitHub
          </a>
        </nav>
        <div className="flex items-center gap-2 border-l border-border pl-3 sm:gap-3 sm:pl-4">
          <AuthActions />
        </div>
      </div>
    </header>
  );
}
