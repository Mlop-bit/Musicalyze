"use client";

import { Select as SelectPrimitive } from "@base-ui/react/select";
import { cn } from "cn";
import { Check, ChevronDown } from "lucide-react";

type Option<T extends string> = { value: T; label: string };

type Props<T extends string> = {
  value: T;
  onValueChange: (value: T) => void;
  options: Option<T>[];
  label: string;
  disabled?: boolean;
  className?: string;
};

export function Select<T extends string>({
  value,
  onValueChange,
  options,
  label,
  disabled,
  className,
}: Props<T>) {
  return (
    <SelectPrimitive.Root
      value={value}
      onValueChange={(next) => next !== null && onValueChange(next as T)}
      items={options}
      disabled={disabled}
    >
      <SelectPrimitive.Trigger
        aria-label={label}
        className={cn(
          "glass-clear press flex h-8 items-center justify-between gap-2 rounded-full px-3 text-sm outline-none focus-visible:ring-[3px] focus-visible:ring-ring/40",
          className,
        )}
      >
        <SelectPrimitive.Value />
        <SelectPrimitive.Icon>
          <ChevronDown className="size-3.5 text-muted-foreground" />
        </SelectPrimitive.Icon>
      </SelectPrimitive.Trigger>
      <SelectPrimitive.Portal>
        <SelectPrimitive.Positioner sideOffset={6} className="z-50">
          <SelectPrimitive.Popup className="surface min-w-[var(--anchor-width)] rounded-2xl p-1 text-sm backdrop-blur-xl">
            {options.map((option) => (
              <SelectPrimitive.Item
                key={option.value}
                value={option.value}
                className="flex cursor-default items-center justify-between gap-3 rounded-xl px-3 py-1.5 outline-none data-[highlighted]:bg-accent"
              >
                <SelectPrimitive.ItemText>
                  {option.label}
                </SelectPrimitive.ItemText>
                <SelectPrimitive.ItemIndicator>
                  <Check className="size-3.5 text-brand" />
                </SelectPrimitive.ItemIndicator>
              </SelectPrimitive.Item>
            ))}
          </SelectPrimitive.Popup>
        </SelectPrimitive.Positioner>
      </SelectPrimitive.Portal>
    </SelectPrimitive.Root>
  );
}
