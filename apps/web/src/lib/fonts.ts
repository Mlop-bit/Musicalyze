import { Geist, Geist_Mono, Yellowtail } from "next/font/google";

export const fontSans = Geist({ subsets: ["latin"], variable: "--font-geist" });

export const fontMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
});

export const fontScript = Yellowtail({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-yellowtail",
});
