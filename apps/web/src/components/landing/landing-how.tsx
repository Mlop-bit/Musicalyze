"use client";

import { m } from "motion/react";
import { ReorderDemo } from "./reorder-demo";

const STEPS = [
  {
    title: "Connect Spotify",
    text: "Sign in and we read your playlists and liked songs. A playlist changes only when you press save.",
  },
  {
    title: "We listen again",
    text: "Each track's 30-second preview becomes an audio embedding with MuQ, enriched with open AcousticBrainz data when it exists.",
  },
  {
    title: "Order by mood",
    text: "A nearest-neighbour pass over those embeddings gives a playlist that flows from one mood into the next.",
  },
];

export function LandingHow() {
  return (
    <section
      id="how"
      className="grid scroll-mt-20 gap-12 px-6 py-28 lg:grid-cols-[minmax(0,34rem)_minmax(0,1fr)] lg:px-14"
    >
      <div className="pane rounded-[2rem] p-6 sm:p-10">
        <h2 className="text-4xl font-semibold tracking-tight sm:text-6xl">
          How it{" "}
          <span className="font-script text-7xl font-normal text-brand sm:text-8xl">
            works
          </span>
        </h2>
        <ol className="mt-10 divide-y divide-border border-y border-border">
          {STEPS.map((step, index) => (
            <m.li
              key={step.title}
              initial={{ opacity: 0, x: -24 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{
                duration: 0.6,
                delay: index * 0.12,
                ease: [0.16, 1, 0.3, 1],
              }}
              className="py-5"
            >
              <h3 className="text-xl font-semibold">{step.title}</h3>
              <p className="mt-1 max-w-md text-muted-foreground">{step.text}</p>
            </m.li>
          ))}
        </ol>
      </div>
      <m.div
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-80px" }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        className="self-center"
      >
        <ReorderDemo />
      </m.div>
    </section>
  );
}
