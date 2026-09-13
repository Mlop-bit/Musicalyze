"use client";

import { getSvgPath } from "figma-squircle";
import { useLayoutEffect, useRef, useState } from "react";

type UseSquircleOptions = {
  cornerRadius?: number;
  cornerSmoothing?: number;
  strokeWidth?: number;
};

export function useSquircle({
  cornerRadius = 24,
  cornerSmoothing = 0.8,
  strokeWidth = 1,
}: UseSquircleOptions = {}) {
  const ref = useRef<HTMLDivElement | null>(null);
  const [size, setSize] = useState<{ width: number; height: number } | null>(
    null,
  );

  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new ResizeObserver(([entry]) => {
      if (!entry) return;
      const box = Array.isArray(entry.borderBoxSize)
        ? entry.borderBoxSize[0]
        : entry.borderBoxSize;
      if (box) {
        setSize({ width: box.inlineSize, height: box.blockSize });
      } else {
        const rect = entry.target.getBoundingClientRect();
        setSize({ width: rect.width, height: rect.height });
      }
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const path =
    size && size.width > 0 && size.height > 0
      ? getSvgPath({
          width: Math.max(size.width - strokeWidth, 0),
          height: Math.max(size.height - strokeWidth, 0),
          cornerRadius,
          cornerSmoothing,
        })
      : null;

  return { ref, path, strokeWidth };
}
