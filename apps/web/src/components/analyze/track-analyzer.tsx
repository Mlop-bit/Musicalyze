"use client";

import { useMutation } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";
import ShinyText from "@/components/react-bits/ShinyText";
import { PreviewProvider } from "@/components/spotify/preview-player";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { TrackAnalysis } from "@/server/ml/schema";
import { useTRPC } from "@/trpc/client";
import { AnalysisResult } from "./analysis-result";
import { AnalyzerIntro } from "./analyzer-intro";
import { ExampleChips } from "./example-chips";

type Entry = { query: string; analysis: TrackAnalysis };

export function TrackAnalyzer() {
  return (
    <PreviewProvider>
      <Analyzer />
    </PreviewProvider>
  );
}

function Analyzer() {
  const trpc = useTRPC();
  const [query, setQuery] = useState("");
  const [entries, setEntries] = useState<Entry[]>([]);
  const analyze = useMutation(trpc.analyze.track.mutationOptions());

  function run(value: string) {
    const trimmed = value.trim();
    if (trimmed.length < 2 || analyze.isPending) return;
    setQuery(trimmed);
    analyze.mutate(
      { query: trimmed },
      {
        onSuccess: (analysis) =>
          setEntries((current) => [{ query: trimmed, analysis }, ...current]),
      },
    );
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    run(query);
  }

  return (
    <div className="h-full overflow-y-auto px-3 pb-6 lg:px-6">
      <div className="space-y-5 pt-2">
        <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">
          Analyse a{" "}
          <span className="font-script text-6xl font-normal text-brand sm:text-7xl">
            song
          </span>
        </h1>
        <form onSubmit={submit} className="flex flex-wrap gap-2">
          <Input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Artist and title"
            aria-label="Song to analyse"
            className="h-12 min-w-56 flex-1 text-base"
          />
          <Button
            type="submit"
            size="lg"
            disabled={analyze.isPending || query.trim().length < 2}
            className="h-12 px-7 text-base font-semibold shadow-xl shadow-brand/40"
          >
            {analyze.isPending ? (
              <ShinyText
                text="Listening…"
                color="#08130c"
                shineColor="#ffffff"
                speed={1.6}
              />
            ) : (
              "Analyse"
            )}
          </Button>
        </form>
        {analyze.error && (
          <p
            role="alert"
            className="surface rounded-2xl p-4 text-sm text-destructive"
          >
            {analyze.error.message}
          </p>
        )}
        {entries.length === 0 ? (
          <>
            <ExampleChips onPick={run} disabled={analyze.isPending} />
            <AnalyzerIntro />
          </>
        ) : (
          entries.map((entry) => (
            <AnalysisResult
              key={entry.analysis.track_id}
              title={entry.query}
              analysis={entry.analysis}
            />
          ))
        )}
      </div>
    </div>
  );
}
