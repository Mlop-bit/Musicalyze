export const FALLBACK_ARC_CIRCUMFERENCE = 2 * Math.PI * 67;

export function getArcLength(arc: SVGCircleElement) {
  try {
    return arc.getTotalLength();
  } catch {
    return FALLBACK_ARC_CIRCUMFERENCE;
  }
}
