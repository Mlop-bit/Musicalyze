"use client";

import { Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tip } from "@/components/ui/tip";
import { buttonClass } from "./button-class";

type Props = {
  onClick: () => void;
  disabled: boolean;
  size?: "sm" | "lg";
  iconOnly?: boolean;
};

export function FindSimilarButton({
  onClick,
  disabled,
  size = "lg",
  iconOnly = false,
}: Props) {
  return (
    <Tip label="Finds tracks in your playlists and liked songs that sound like this one. It compares the audio, not the genre or the artist.">
      <Button
        type="button"
        variant="outline"
        size={size}
        disabled={disabled}
        onClick={onClick}
        aria-label={iconOnly ? "Find similar" : undefined}
        className={buttonClass(size, iconOnly)}
      >
        <Sparkles className="size-4" />
        {!iconOnly && "Find similar"}
      </Button>
    </Tip>
  );
}
