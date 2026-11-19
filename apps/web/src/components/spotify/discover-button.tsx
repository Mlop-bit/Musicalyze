"use client";

import { Compass } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tip } from "@/components/ui/tip";
import { buttonClass } from "./button-class";

type Props = {
  onClick: () => void;
  disabled: boolean;
  size?: "sm" | "lg";
  iconOnly?: boolean;
};

export function DiscoverButton({
  onClick,
  disabled,
  size = "lg",
  iconOnly = false,
}: Props) {
  return (
    <Tip label="Looks beyond your library: finds similar artists on Deezer and checks their best tracks. You can play the results, but not add them to Spotify.">
      <Button
        type="button"
        variant="outline"
        size={size}
        disabled={disabled}
        onClick={onClick}
        aria-label={iconOnly ? "Discover" : undefined}
        className={buttonClass(size, iconOnly)}
      >
        <Compass className="size-4" />
        {!iconOnly && "Discover"}
      </Button>
    </Tip>
  );
}
