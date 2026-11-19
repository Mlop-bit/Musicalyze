import { AudioWaveform, Gauge, Tags } from "lucide-react";

const POINTS = [
  {
    icon: AudioWaveform,
    title: "Listens to a preview",
    text: "A 30 second clip is turned into an audio fingerprint.",
  },
  {
    icon: Gauge,
    title: "Tempo and key",
    text: "Taken from the catalogue when known, estimated from the sound otherwise.",
  },
  {
    icon: Tags,
    title: "Mood tags",
    text: "Fifty-odd tags such as energetic, melodic or love, ranked by strength.",
  },
];

export function AnalyzerIntro() {
  return (
    <ul className="grid gap-3 sm:grid-cols-3">
      {POINTS.map(({ icon: Icon, title, text }) => (
        <li key={title} className="surface flex gap-3 rounded-2xl p-4">
          <span className="glass-clear flex size-9 shrink-0 items-center justify-center rounded-full text-brand">
            <Icon className="size-4" />
          </span>
          <span>
            <span className="block text-sm font-semibold">{title}</span>
            <span className="mt-0.5 block text-xs text-muted-foreground">
              {text}
            </span>
          </span>
        </li>
      ))}
    </ul>
  );
}
