"use client";

import { Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

type Props = {
  onClick: () => void;
  disabled: boolean;
  size?: "sm" | "lg";
};

export function FindSimilarButton({ onClick, disabled, size = "lg" }: Props) {
  return (
    <Button
      type="button"
      variant="outline"
      size={size}
      disabled={disabled}
      onClick={onClick}
      className={size === "lg" ? "h-12 gap-2 px-5" : "gap-1.5"}
    >
      <Sparkles className="size-4" />
      Find similar
    </Button>
  );
}
