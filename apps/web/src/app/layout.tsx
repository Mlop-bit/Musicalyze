import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";
import { AuroraBackground } from "@/components/layout/aurora-background";
import { MotionProvider } from "@/components/layout/motion-provider";
import { SiteHeader } from "@/components/layout/site-header";
import { PreferencesProvider } from "@/components/preferences/preferences-provider";
import { PREFERENCES_INIT_SCRIPT } from "@/components/preferences/preferences-script";
import { fontMono, fontSans, fontScript } from "@/lib/fonts";
import { TRPCReactProvider } from "@/trpc/client";

export const metadata: Metadata = {
  title: "Musicalyze",
  description:
    "Musicalyze reconstructs the tempo, key, energy, and mood metadata that Spotify stopped exposing, using a pretrained audio model and public acoustic datasets.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${fontSans.variable} ${fontMono.variable} ${fontScript.variable}`}
    >
      <body className="bg-background font-sans text-foreground antialiased">
        <Script id="preferences-init" strategy="beforeInteractive">
          {PREFERENCES_INIT_SCRIPT}
        </Script>
        <PreferencesProvider>
          <TRPCReactProvider>
            <MotionProvider>
              <AuroraBackground />
              <SiteHeader />
              {children}
            </MotionProvider>
          </TRPCReactProvider>
        </PreferencesProvider>
      </body>
    </html>
  );
}
