"use client";

import { Popover } from "@base-ui/react/popover";
import { LogOut, Settings } from "lucide-react";
import { useRouter } from "next/navigation";
import { RemoteImage } from "@/components/ui/remote-image";
import { Segmented } from "@/components/ui/segmented";
import { Switch } from "@/components/ui/switch";
import { Tip } from "@/components/ui/tip";
import { authClient } from "@/lib/auth-client";
import { type Theme, usePreferences } from "./preferences-provider";

const THEMES: { value: Theme; label: string }[] = [
  { value: "light", label: "Light" },
  { value: "dark", label: "Dark" },
  { value: "system", label: "Auto" },
];

export function SettingsMenu() {
  const { theme, glass, setTheme, setGlass } = usePreferences();
  const router = useRouter();
  const { data: session } = authClient.useSession();

  function logOut() {
    authClient.signOut({ fetchOptions: { onSuccess: () => router.push("/") } });
  }

  return (
    <Popover.Root>
      <Tip label="Account, theme and frosted glass." side="bottom">
        <Popover.Trigger
          aria-label={session ? "Account and settings" : "Settings"}
          className="press flex size-10 items-center justify-center rounded-full text-muted-foreground outline-none hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/40"
        >
          {session ? (
            session.user.image ? (
              <span className="relative size-10 overflow-hidden rounded-full ring-2 ring-brand">
                <RemoteImage src={session.user.image} sizes="40px" />
              </span>
            ) : (
              <span className="flex size-10 items-center justify-center rounded-full bg-brand font-semibold text-brand-foreground">
                {session.user.name.slice(0, 1).toUpperCase()}
              </span>
            )
          ) : (
            <Settings className="size-5" />
          )}
        </Popover.Trigger>
      </Tip>
      <Popover.Portal>
        <Popover.Positioner sideOffset={10} align="end" className="z-50">
          <Popover.Popup className="surface w-64 space-y-4 rounded-2xl p-4 text-sm backdrop-blur-xl">
            {session && (
              <div className="min-w-0 border-b border-border pb-3">
                <p className="truncate font-semibold">{session.user.name}</p>
                <p className="truncate text-xs text-muted-foreground">
                  {session.user.email}
                </p>
              </div>
            )}
            <div className="space-y-2">
              <p className="font-medium">Theme</p>
              <Segmented
                value={theme}
                onValueChange={setTheme}
                options={THEMES}
                label="Theme"
                className="w-full [&>button]:flex-1"
              />
            </div>
            <div className="flex items-center justify-between gap-3">
              <span>
                <span className="block font-medium">Frosted glass</span>
                <span className="block text-xs text-muted-foreground">
                  Translucent panels over an aurora
                </span>
              </span>
              <Switch
                checked={glass}
                onCheckedChange={setGlass}
                aria-label="Frosted glass"
              />
            </div>
            {session && (
              <button
                type="button"
                onClick={logOut}
                className="press flex w-full items-center gap-2 border-t border-border pt-3 text-muted-foreground hover:text-foreground"
              >
                <LogOut className="size-4" />
                Log out
              </button>
            )}
          </Popover.Popup>
        </Popover.Positioner>
      </Popover.Portal>
    </Popover.Root>
  );
}
