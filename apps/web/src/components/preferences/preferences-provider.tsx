"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { z } from "zod";

const themeSchema = z.enum(["light", "dark", "system"]);
export type Theme = z.infer<typeof themeSchema>;

type Preferences = {
  theme: Theme;
  glass: boolean;
  dark: boolean;
  setTheme: (theme: Theme) => void;
  setGlass: (glass: boolean) => void;
};

const PreferencesContext = createContext<Preferences | null>(null);

function readStorage(key: string) {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function writeStorage(key: string, value: string) {
  try {
    localStorage.setItem(key, value);
  } catch {}
}

function applyTheme(theme: Theme) {
  const dark =
    theme === "dark" ||
    (theme === "system" && matchMedia("(prefers-color-scheme: dark)").matches);
  document.documentElement.classList.toggle("dark", dark);
  return dark;
}

export function PreferencesProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [theme, setThemeState] = useState<Theme>("system");
  const [glass, setGlassState] = useState(false);
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const stored = themeSchema.catch("system").parse(readStorage("theme"));
    setThemeState(stored);
    setDark(applyTheme(stored));
    setGlassState(readStorage("glass") === "on");
  }, []);

  useEffect(() => {
    if (theme !== "system") return;
    const query = matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => setDark(applyTheme("system"));
    query.addEventListener("change", onChange);
    return () => query.removeEventListener("change", onChange);
  }, [theme]);

  const setTheme = useCallback((next: Theme) => {
    setThemeState(next);
    writeStorage("theme", next);
    setDark(applyTheme(next));
  }, []);

  const setGlass = useCallback((next: boolean) => {
    setGlassState(next);
    writeStorage("glass", next ? "on" : "off");
    document.documentElement.dataset.glass = next ? "on" : "off";
  }, []);

  const value = useMemo(
    () => ({ theme, glass, dark, setTheme, setGlass }),
    [theme, glass, dark, setTheme, setGlass],
  );

  return <PreferencesContext value={value}>{children}</PreferencesContext>;
}

export function usePreferences() {
  const context = useContext(PreferencesContext);
  if (!context)
    throw new Error("usePreferences must be used inside PreferencesProvider");
  return context;
}
