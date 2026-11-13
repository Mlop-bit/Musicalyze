"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { authClient } from "@/lib/auth-client";

const FALLBACK_MESSAGE = "Spotify sign-in could not start.";

export function LoginCard() {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");

  async function signIn() {
    setError("");
    setPending(true);
    try {
      const result = await authClient.signIn.social({
        provider: "spotify",
        callbackURL: "/dashboard",
      });
      if (result.error) {
        setError(result.error.message ?? FALLBACK_MESSAGE);
        setPending(false);
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : FALLBACK_MESSAGE);
      setPending(false);
    }
  }

  return (
    <section className="mx-auto flex min-h-[80vh] max-w-lg flex-col items-center justify-center px-5 pt-20 text-center">
      <div className="mb-5 flex size-14 items-center justify-center rounded-full bg-[#1ed760] text-2xl font-bold text-black">
        ♪
      </div>
      <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">
        Your music, in one place.
      </h1>
      <p className="mt-3 max-w-sm text-muted-foreground">
        Connect Spotify to browse your playlists and order them by mood.
      </p>
      <Button
        type="button"
        onClick={() => void signIn()}
        disabled={pending}
        className="mt-7 h-11 rounded-full bg-[#1ed760] px-7 font-semibold text-black hover:bg-[#1ed760]/90"
      >
        {pending ? "Connecting…" : "Continue with Spotify"}
      </Button>
      {error && (
        <p role="alert" className="mt-4 max-w-md text-sm text-destructive">
          {error}
        </p>
      )}
    </section>
  );
}
