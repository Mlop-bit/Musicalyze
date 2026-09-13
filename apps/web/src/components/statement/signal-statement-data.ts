import type { WavePath } from "@/components/ui/wave-frame";

export const RAW_SIGNAL_PATH =
  "M0,30 L15,8 L30,52 L45,14 L60,46 L75,20 L90,42 L105,24 L120,38 L135,28 L150,30";
export const WAVEFORM_PATH =
  "M0,30 C15,10 30,50 45,30 C60,10 75,50 90,30 C105,10 120,50 135,30 C142,20 150,30 150,30";

export const HEADING_TEXT = "The signal never stopped.";

export const SENTENCES = [
  "In November 2024, Spotify shut off the endpoints that exposed tempo, key, energy, and danceability to third-party developers.",
  "Musicalyze rebuilds that layer independently, analyzing the audio itself instead of a metadata API that no longer exists.",
] as const;

export const AMBIENT_WAVE_PATHS: WavePath[] = [
  {
    d: "M0,30 C25,8 50,52 75,30 C100,8 125,52 150,30 C175,8 200,52 225,30 C250,8 275,52 300,30 C325,8 350,52 375,30 C387,20 400,30 400,30",
    strokeWidth: 1.25,
    strokeDasharray: "8 12",
    className: "text-signal-violet",
  },
  {
    d: "M0,33 C25,48 50,20 75,33 C100,48 125,20 150,33 C175,48 200,20 225,33 C250,48 275,20 300,33 C325,48 350,20 375,33 C387,40 400,33 400,33",
    strokeWidth: 1,
    strokeDasharray: "4 9",
    className: "text-muted-foreground opacity-60",
  },
  {
    d: "M0,27 C25,15 50,42 75,27 C100,15 125,42 150,27 C175,15 200,42 225,27 C250,15 275,42 300,27 C325,15 350,42 375,27 C387,22 400,27 400,27",
    strokeWidth: 0.75,
    strokeDasharray: "3 7",
    className: "text-signal-violet opacity-40",
  },
];

export const WAVE_DASH_DELTAS = [-200, 195, -180] as const;
export const WAVE_DURATIONS = [10, 14, 18] as const;
