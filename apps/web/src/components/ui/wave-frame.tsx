import type { SVGProps } from "react";
import { cn } from "@/lib/utils";

export type WavePath = {
  d: string;
  strokeWidth: number;
  strokeDasharray: string;
  className: string;
};

type WaveFrameProps = SVGProps<SVGSVGElement> & {
  paths: WavePath[];
};

export function WaveFrame({ paths, className, ...svgProps }: WaveFrameProps) {
  return (
    <svg
      viewBox="0 0 400 60"
      preserveAspectRatio="none"
      className={cn("h-full w-full", className)}
      aria-hidden="true"
      {...svgProps}
    >
      {paths.map((path, index) => (
        <path
          key={index}
          data-wave-path
          d={path.d}
          stroke="currentColor"
          strokeWidth={path.strokeWidth}
          strokeDasharray={path.strokeDasharray}
          strokeLinecap="round"
          fill="none"
          className={path.className}
        />
      ))}
    </svg>
  );
}
