import type { Metadata } from "next";
import "./globals.css";
import { fontMono, fontSans } from "@/lib/fonts";

export const metadata: Metadata = {
  title: "Musicalyze",
  description: "Sign in with Spotify to browse your playlists and tracks with Musicalyze.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${fontSans.variable} ${fontMono.variable}`}>
      <body className="bg-background font-sans text-foreground antialiased">
        <main className="min-h-screen">{children}</main>
      </body>
    </html>
  );
}
