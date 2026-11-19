"use client";

import { Tooltip } from "@base-ui/react/tooltip";

type Props = {
  label: string;
  children: React.ReactNode;
  side?: "top" | "bottom";
};

export function Tip({ label, children, side = "bottom" }: Props) {
  return (
    <Tooltip.Root>
      <Tooltip.Trigger render={<span className="inline-flex" />}>
        {children}
      </Tooltip.Trigger>
      <Tooltip.Portal>
        <Tooltip.Positioner side={side} sideOffset={8} className="z-[60]">
          <Tooltip.Popup className="surface max-w-64 rounded-xl px-3 py-2 text-xs leading-snug text-foreground shadow-lg backdrop-blur-xl">
            {label}
          </Tooltip.Popup>
        </Tooltip.Positioner>
      </Tooltip.Portal>
    </Tooltip.Root>
  );
}
