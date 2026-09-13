"use client";

import { useEffect, useRef } from "react";
import { startSignalRing } from "./hero-gpu-scene";

export function HeroGpuCanvas({ onReady }: { onReady: () => void }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    return startSignalRing(canvas, onReady);
  }, [onReady]);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className="absolute inset-0 h-full w-full"
    />
  );
}
