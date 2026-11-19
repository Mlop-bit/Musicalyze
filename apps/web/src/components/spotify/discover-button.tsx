"use client";

import { Compass } from "lucide-react";
import { Button } from "@/components/ui/button";

type Props = {
  onClick: () => void;
  disabled: boolean;
  size?: "sm" | "lg";
};

export function DiscoverButton({ onClick, disabled, size = "lg" }: Props) {
  return (
    <Button
      type="button"
      variant="outline"
      size={size}
      disabled={disabled}
      onClick={onClick}
      title="Look beyond your library, through Deezer"
      className={size === "lg" ? "h-12 gap-2 px-5" : "gap-1.5"}
    >
      <Compass className="size-4" />
      Discover
    </Button>
  );
}
