import {
  Cpu,
  Database,
  ListMusic,
  type LucideIcon,
  RadioOff,
  Tags,
} from "lucide-react";

export const HEADING_TEXT = "How the missing metadata gets rebuilt";

export type Stage = {
  label: string;
  detail: string;
  meta: string;
  icon: LucideIcon;
};

export const STAGES: readonly Stage[] = [
  {
    label: "Spotify gap",
    detail: "Audio-feature endpoints deprecated, Nov 2024",
    meta: "GET /audio-features -> 403",
    icon: RadioOff,
  },
  {
    label: "MuQ model",
    detail: "Pretrained audio representation model",
    meta: "1024-dim embedding, self-supervised",
    icon: Cpu,
  },
  {
    label: "AcousticBrainz + Jamendo",
    detail: "Public datasets fill the label gap",
    meta: "1.2M+ tracks, CC-licensed",
    icon: Database,
  },
  {
    label: "Mood / genre classifier",
    detail: "Custom-trained on top of MuQ embeddings",
    meta: "12 mood tags, multi-label",
    icon: Tags,
  },
  {
    label: "Segmentation & recs",
    detail: "Playlist sequencing and recommendations",
    meta: "beat-aligned, cosine similarity",
    icon: ListMusic,
  },
];
