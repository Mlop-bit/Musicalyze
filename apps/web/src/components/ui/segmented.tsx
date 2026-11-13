"use client";

import { cn } from "cn";

type Option<T extends string> = {
  value: T;
  label: React.ReactNode;
  ariaLabel?: string;
};

type Props<T extends string> = {
  value: T;
  onValueChange: (value: T) => void;
  options: Option<T>[];
  label: string;
  className?: string;
};

export function Segmented<T extends string>({
  value,
  onValueChange,
  options,
  label,
  className,
}: Props<T>) {
  return (
    <div
      role="group"
      aria-label={label}
      className={cn(
        "glass-clear inline-flex rounded-full p-0.5 text-sm",
        className,
      )}
    >
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          aria-label={option.ariaLabel}
          aria-pressed={value === option.value}
          onClick={() => onValueChange(option.value)}
          className="press flex items-center justify-center gap-1.5 rounded-full px-3 py-1 text-muted-foreground aria-pressed:bg-foreground aria-pressed:text-background"
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
