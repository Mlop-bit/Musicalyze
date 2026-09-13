import { HeroSection } from "@/components/hero/hero-section";
import { PipelineStrip } from "@/components/pipeline/pipeline-strip";
import { SignalStatement } from "@/components/statement/signal-statement";

export default function Home() {
  return (
    <>
      <HeroSection />
      <PipelineStrip />
      <SignalStatement />
    </>
  );
}
