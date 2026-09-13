export const LINE_X = 10;

export type RailTheme = {
  label: string;
  textClass: string;
  strokeClass: string;
  dotClass: string;
  badgeClass: string;
};

export const RELEASE_THEME: RailTheme = {
  label: "Release",
  textClass: "text-signal-violet",
  strokeClass: "stroke-signal-violet",
  dotClass: "bg-signal-violet",
  badgeClass: "border-signal-violet/40 text-signal-violet",
};

export const DEVELOPMENT_THEME: RailTheme = {
  label: "Development",
  textClass: "text-signal-azure",
  strokeClass: "stroke-signal-azure",
  dotClass: "bg-signal-azure",
  badgeClass: "border-signal-azure/40 text-signal-azure",
};
