"use client";

import { Switch as SwitchPrimitive } from "@base-ui/react/switch";
import { cn } from "cn";

export function Switch({ className, ...props }: SwitchPrimitive.Root.Props) {
  return (
    <SwitchPrimitive.Root
      className={cn(
        "inline-flex h-[22px] w-[38px] shrink-0 items-center rounded-full bg-foreground/12 p-0.5 outline-none transition-colors duration-200 focus-visible:ring-[3px] focus-visible:ring-ring/40 data-[checked]:bg-brand dark:bg-white/16",
        className,
      )}
      {...props}
    >
      <SwitchPrimitive.Thumb className="pointer-events-none block size-[18px] rounded-full bg-white shadow-[0_1px_3px_rgb(0_0_0/0.25)] transition-transform duration-400 ease-snappy data-[checked]:translate-x-4" />
    </SwitchPrimitive.Root>
  );
}
