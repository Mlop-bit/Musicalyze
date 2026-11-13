import { cn } from "cn";
import Link from "next/link";
import { buttonVariants } from "@/components/ui/button-variants";

export function LandingClose() {
  return (
    <section className="flex min-h-[70dvh] flex-col items-center justify-center px-6 py-24 text-center lg:px-14">
      <p className="font-script text-7xl leading-none sm:text-[9rem]">
        Drop the needle.
      </p>
      <Link
        href="/login"
        className={cn(
          buttonVariants({ size: "lg" }),
          "mt-10 px-8 font-semibold shadow-lg shadow-brand/30",
        )}
      >
        Continue with Spotify
      </Link>
    </section>
  );
}
