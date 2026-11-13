"use client";

import Link from "next/link";
import { SettingsMenu } from "@/components/preferences/settings-menu";
import { buttonVariants } from "@/components/ui/button-variants";
import { authClient } from "@/lib/auth-client";
import { GITHUB_OWNER, GITHUB_REPO } from "@/server/github/constants";

const GITHUB_URL = `https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}`;
const NAV_LINK =
  "text-muted-foreground transition-colors hover:text-foreground";

function AuthActions() {
  const { data: session, isPending } = authClient.useSession();

  if (isPending || session) return null;

  return (
    <>
      <Link href="/login" className={buttonVariants({ variant: "outline" })}>
        Sign in
      </Link>
      <Link href="/login" className={buttonVariants()}>
        Sign up
      </Link>
    </>
  );
}

export function SiteHeader() {
  return (
    <header className="surface fixed left-1/2 top-4 z-50 grid h-14 w-[min(52rem,calc(100%-2rem))] -translate-x-1/2 grid-cols-[1fr_auto_1fr] items-center rounded-full pl-6 pr-2 text-[0.95rem] shadow-xl">
      <Link
        href="/"
        className="justify-self-start font-script text-3xl leading-none text-foreground"
      >
        Musicalyze
      </Link>
      <nav className="hidden items-center gap-8 sm:flex">
        <Link href="/dashboard" className={NAV_LINK}>
          Dashboard
        </Link>
        <Link href="/changelog" className={NAV_LINK}>
          Changelog
        </Link>
        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noreferrer"
          className={NAV_LINK}
        >
          GitHub
        </a>
      </nav>
      <div className="flex items-center justify-self-end gap-2">
        <AuthActions />
        <SettingsMenu />
      </div>
    </header>
  );
}
