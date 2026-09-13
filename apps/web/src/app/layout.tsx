import type { Metadata } from "next";
import "./globals.css";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { SmoothScrollProvider } from "@/components/layout/smooth-scroll-provider";
import { fontMono, fontSans } from "@/lib/fonts";

export const metadata: Metadata = {
  title: "Musicalyze",
  description:
    "Musicalyze reconstructs the tempo, key, energy, and mood metadata that Spotify stopped exposing, using a pretrained audio model and public acoustic datasets.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${fontSans.variable} ${fontMono.variable}`}>
      <body className="bg-background font-sans text-foreground antialiased">
        <SiteHeader />
        <SmoothScrollProvider>
          <div className="flex min-h-screen flex-col">
            <main className="flex-1">{children}</main>
            <SiteFooter />
          </div>
        </SmoothScrollProvider>
      </body>
    </html>
  );
}
