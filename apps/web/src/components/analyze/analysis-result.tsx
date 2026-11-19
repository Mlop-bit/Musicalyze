"use client";

import { ExternalLink } from "lucide-react";
import { DiscoverButton } from "@/components/spotify/discover-button";
import { FindSimilarButton } from "@/components/spotify/find-similar-button";
import { SimilarList } from "@/components/spotify/similar-list";
import { Tip } from "@/components/ui/tip";
import type { TrackAnalysis } from "@/server/ml/schema";
import { MoodBars } from "./mood-bars";
import { useAnalysisSimilar } from "./use-analysis-similar";

function Fact({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <Tip label={hint}>
      <div className="px-5 text-center">
        <dt className="text-[0.65rem] uppercase tracking-wider text-muted-foreground">
          {label}
        </dt>
        <dd className="text-lg font-semibold tabular-nums">{value}</dd>
      </div>
    </Tip>
  );
}

export function AnalysisResult({
  title,
  analysis,
}: {
  title: string;
  analysis: TrackAnalysis;
}) {
  const estimated = analysis.source !== "acousticbrainz";
  const similar = useAnalysisSimilar(analysis.track_id, title);

  return (
    <article className="surface grid gap-6 rounded-3xl p-5 md:grid-cols-[minmax(0,18rem)_minmax(0,1fr)] md:gap-8 md:p-6">
      <header className="flex flex-col gap-4">
        <div className="min-w-0">
          <h2 className="break-words font-script text-5xl leading-[1.05]">
            {title}
          </h2>
          {analysis.mood_label && (
            <p className="mt-1 text-sm text-muted-foreground">
              Sounds mostly{" "}
              <span className="font-semibold capitalize text-brand">
                {analysis.mood_label}
              </span>
            </p>
          )}
        </div>
        <dl className="flex w-fit divide-x divide-border rounded-2xl bg-foreground/[0.05] py-2 ring-1 ring-border">
          <Fact
            hint="Beats per minute. Taken from the catalogue when known, otherwise estimated from the preview."
            label="tempo"
            value={analysis.bpm ? `${Math.round(analysis.bpm)} bpm` : "n/a"}
          />
          <Fact
            hint="The musical key, estimated from the preview."
            label="key"
            value={analysis.key ?? "n/a"}
          />
        </dl>
        {estimated && (
          <p className="text-xs text-muted-foreground">
            Tempo and key are estimated from a 30 second preview.
          </p>
        )}
        {analysis.musicbrainz_id && (
          <a
            href={`https://musicbrainz.org/recording/${analysis.musicbrainz_id}`}
            target="_blank"
            rel="noreferrer"
            className="inline-flex w-fit items-center gap-1.5 text-xs text-muted-foreground transition-colors hover:text-foreground"
          >
            Matched on MusicBrainz
            <ExternalLink className="size-3" />
          </a>
        )}
      </header>
      {analysis.mood_scores ? (
        <MoodBars scores={analysis.mood_scores} />
      ) : (
        <p className="text-sm text-muted-foreground">
          No mood scores for this track.
        </p>
      )}
      <section className="space-y-2 md:col-span-2">
        <div className="flex items-center justify-between gap-3 border-t border-border pt-4">
          <p className="text-sm text-muted-foreground">
            {similar.active
              ? `Tracks that sound like ${title}`
              : "Look for tracks in your library that sound like this one."}
          </p>
          {similar.active ? (
            <button
              type="button"
              onClick={similar.reset}
              disabled={similar.running}
              className="text-xs text-muted-foreground transition-colors hover:text-foreground disabled:opacity-50"
            >
              Close
            </button>
          ) : (
            <div className="flex gap-2">
              <FindSimilarButton
                size="sm"
                onClick={() => similar.run()}
                disabled={false}
              />
              <DiscoverButton
                size="sm"
                onClick={() => similar.run("discover")}
                disabled={false}
              />
            </div>
          )}
        </div>
        {similar.active &&
          (similar.error ? (
            <p role="alert" className="text-sm text-destructive">
              {similar.error}
            </p>
          ) : (
            <SimilarList similar={similar} />
          ))}
      </section>
    </article>
  );
}
