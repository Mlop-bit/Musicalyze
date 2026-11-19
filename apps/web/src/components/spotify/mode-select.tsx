"use client";

import { Select } from "@/components/ui/select";
import { Tip } from "@/components/ui/tip";
import { REORDER_MODES, type ReorderMode } from "@/lib/reorder-modes";

type Props = {
  value: ReorderMode;
  onValueChange: (value: ReorderMode) => void;
  disabled?: boolean;
};

export function ModeSelect({ value, onValueChange, disabled }: Props) {
  return (
    <Tip label="How to order: by how alike the tracks sound, or as a ramp from calm to energetic (or the other way round).">
      <Select
        value={value}
        onValueChange={onValueChange}
        options={[...REORDER_MODES]}
        label="Ordering style"
        disabled={disabled}
        className="h-10 min-w-44"
      />
    </Tip>
  );
}
