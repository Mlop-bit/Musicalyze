import type { FrameLoopHandle } from "vgpu";
import { clock, effect, frameLoop, init, surface } from "vgpu";
import signalRingShader from "./signal-ring.wgsl";

export function startSignalRing(
  canvas: HTMLCanvasElement,
  onReady: () => void,
): () => void {
  let disposed = false;
  let loop: FrameLoopHandle | undefined;
  let gpu: Awaited<ReturnType<typeof init>> | undefined;

  void (async () => {
    try {
      gpu = await init({ powerPreference: "low-power" });
    } catch {
      return;
    }
    if (disposed) {
      gpu.dispose();
      return;
    }

    const canvasSurface = surface(gpu, canvas, { dpr: [1, 2] });
    const ring = effect(gpu, signalRingShader, {
      label: "signal-ring",
      set: {
        params: {
          time: 0,
          resolution: canvasSurface.size,
        },
      },
    });

    canvasSurface.onResize(() => {
      ring.set({ params: { resolution: canvasSurface.size } });
    });

    const time = clock(gpu);
    onReady();

    loop = frameLoop(gpu, (frame) => {
      ring.set({ params: { time: time.time } });
      frame.pass(canvasSurface, ring);
    });
  })();

  return () => {
    disposed = true;
    loop?.stop();
    gpu?.dispose();
  };
}
