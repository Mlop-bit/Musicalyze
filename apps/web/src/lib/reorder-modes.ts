import { z } from "zod";

export const REORDER_MODES = [
  { value: "similarity", label: "By similarity" },
  { value: "calm_to_energetic", label: "Calm to energetic" },
  { value: "energetic_to_calm", label: "Energetic to calm" },
] as const;

export const reorderModeSchema = z.enum(
  REORDER_MODES.map((mode) => mode.value) as [
    (typeof REORDER_MODES)[number]["value"],
    ...(typeof REORDER_MODES)[number]["value"][],
  ],
);

export type ReorderMode = z.infer<typeof reorderModeSchema>;
