const MIN_VISIBLE = 0.05;

export function OrderProgress({
  done,
  total,
}: {
  done: number;
  total: number;
}) {
  const fraction = total > 0 ? done / total : 0;

  return (
    <div className="absolute inset-x-0 bottom-0 h-0.5 bg-foreground/10">
      <div
        className="h-full bg-brand transition-[width] duration-700"
        style={{ width: `${Math.max(fraction, MIN_VISIBLE) * 100}%` }}
      />
    </div>
  );
}
