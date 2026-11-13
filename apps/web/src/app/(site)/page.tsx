import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { LandingClose } from "@/components/landing/landing-close";
import { LandingFeatures } from "@/components/landing/landing-features";
import { LandingHero } from "@/components/landing/landing-hero";
import { LandingHow } from "@/components/landing/landing-how";

export default async function Home() {
  if (process.env.NODE_ENV === "development") {
    const host = (await headers()).get("host")?.split(":")[0];
    if (host === "localhost") redirect("http://127.0.0.1:3000");
  }

  return (
    <>
      <LandingHero />
      <LandingHow />
      <LandingFeatures />
      <LandingClose />
    </>
  );
}
