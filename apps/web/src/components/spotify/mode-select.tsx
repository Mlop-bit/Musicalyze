"use client";

import { Select } from "@/components/ui/select";
import { REORDER_MODES, type ReorderMode } from "@/lib/reorder-modes";

type Props = {
  value: ReorderMode;
  onValueChange: (value: ReorderMode) => void;
  disabled?: boolean;
};

export function ModeSelect({ value, onValueChange, disabled }: Props) {
  return (
    <Select
      value={value}
      onValueChange={onValueChange}
      options={[...REORDER_MODES]}
      label="Ordering style"
      disabled={disabled}
      className="h-10 min-w-44"
    />
  );
}
