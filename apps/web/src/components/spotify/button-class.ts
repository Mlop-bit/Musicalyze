export function buttonClass(size: "sm" | "lg", iconOnly: boolean) {
  if (size === "sm") return "gap-1.5";
  return iconOnly ? "h-12 w-12 p-0" : "h-12 gap-2 px-5";
}
