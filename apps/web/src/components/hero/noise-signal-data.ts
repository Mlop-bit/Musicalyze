export type NoiseDot = { x: number; y: number; r: number; chaos: number };

const VIEW_W = 1000;
const VIEW_H = 90;
const BASELINE = 45;
const WAVE_AMPLITUDE = 15;
const WAVE_CYCLES = 5.5;
const DOT_COUNT = 130;
const CLEAN_PATH_START = 0.72;

function round(value: number) {
  return Math.round(value * 1000) / 1000;
}

function pseudoRandom(seed: number) {
  const s = Math.sin(seed * 12.9898) * 43758.5453;
  return s - Math.floor(s);
}

function waveY(x: number) {
  return (
    BASELINE +
    Math.sin((x / VIEW_W) * Math.PI * 2 * WAVE_CYCLES) * WAVE_AMPLITUDE
  );
}

export const NOISE_TO_SIGNAL_DOTS: NoiseDot[] = Array.from(
  { length: DOT_COUNT },
  (_, i) => {
    const progress = i / (DOT_COUNT - 1);
    const x = progress * VIEW_W;
    const chaos = (1 - progress) ** 1.5;
    const randomY = pseudoRandom(i * 12.9898) * VIEW_H;
    const y = randomY * chaos + waveY(x) * (1 - chaos);
    const r = 1 + chaos * 1.4;
    return { x: round(x), y: round(y), r: round(r), chaos: round(chaos) };
  },
);

export const CLEAN_SIGNAL_PATH = Array.from({ length: 40 }, (_, i) => {
  const t = i / 39;
  const x = VIEW_W * (CLEAN_PATH_START + t * (1 - CLEAN_PATH_START));
  return `${i === 0 ? "M" : "L"}${round(x)},${round(waveY(x))}`;
}).join(" ");

export const NOISE_SIGNAL_VIEWBOX = `0 0 ${VIEW_W} ${VIEW_H}`;
