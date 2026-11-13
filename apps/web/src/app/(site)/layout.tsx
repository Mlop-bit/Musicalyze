import { SiteFooter } from "@/components/layout/site-footer";
import { SmoothScrollProvider } from "@/components/layout/smooth-scroll-provider";

export default function SiteLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <SmoothScrollProvider>
      <div className="flex min-h-screen flex-col">
        <main className="flex-1">{children}</main>
        <SiteFooter />
      </div>
    </SmoothScrollProvider>
  );
}
