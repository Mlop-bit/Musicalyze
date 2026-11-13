"use client";

import { ArrowUpRight } from "lucide-react";
import { m } from "motion/react";

const FEATURES = [
  {
    title: "Order by mood",
    text: "Neighbouring tracks sound alike, optionally weighted by tempo and key.",
    ready: true,
  },
  {
    title: "Split into moods",
    text: "Long playlists become coherent sub-playlists, each named after its dominant mood.",
    ready: false,
  },
  {
    title: "Recommend by sound",
    text: "Tracks and artists that sit close to your seeds in embedding space.",
    ready: false,
  },
];

export function LandingFeatures() {
  return (
    <section className="px-6 py-28 lg:px-14">
      <div className="pane rounded-[2rem] p-6 sm:p-12">
        <h2 className="max-w-4xl text-4xl font-semibold leading-tight tracking-tight sm:text-6xl">
          Built on what the music{" "}
          <span className="font-script text-7xl font-normal text-brand sm:text-8xl">
            sounds
          </span>{" "}
          like
        </h2>
        <ul className="mt-12 space-y-2">
          {FEATURES.map((feature, index) => (
            <m.li
              key={feature.title}
              initial={{ opacity: 0, y: 28 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{
                duration: 0.6,
                delay: index * 0.1,
                ease: [0.16, 1, 0.3, 1],
              }}
              className="group grid items-center gap-2 rounded-3xl border border-transparent px-6 py-7 transition-[transform,border-color,background-color,box-shadow] duration-300 hover:-translate-y-0.5 hover:border-brand/40 hover:bg-brand/[0.07] hover:shadow-lg hover:shadow-brand/10 md:grid-cols-[minmax(0,1fr)_minmax(0,26rem)] md:gap-12"
            >
              <h3 className="text-3xl font-semibold tracking-tight transition-colors duration-300 group-hover:text-brand sm:text-5xl">
                {feature.title}
              </h3>
              <div className="space-y-3">
                <p className="text-muted-foreground">{feature.text}</p>
                <span className="flex items-center gap-2 text-sm font-medium">
                  {feature.ready ? (
                    <>
                      <span className="size-2 rounded-full bg-brand" />
                      Available
                      <ArrowUpRight className="size-4 transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
                    </>
                  ) : (
                    <span className="text-muted-foreground">Soon</span>
                  )}
                </span>
              </div>
            </m.li>
          ))}
        </ul>
      </div>
    </section>
  );
}
