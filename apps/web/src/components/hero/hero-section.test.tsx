import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { HERO_TAGLINE, HeroSection } from "./hero-section";

afterEach(cleanup);

describe("HeroSection", () => {
  it("renders the MUSICALYZE wordmark as a heading", () => {
    render(<HeroSection />);
    expect(
      screen.getByRole("heading", { name: /musicalyze/i }),
    ).toBeInTheDocument();
  });

  it("exports the mission-statement tagline copy", () => {
    expect(HERO_TAGLINE).toBe(
      "Tempo, key, energy, and mood - reconstructed where Spotify's API stopped.",
    );
  });

  it("renders a primary call to action once the session resolves", async () => {
    render(<HeroSection />);
    expect(
      await screen.findByRole(
        "button",
        { name: /sign up with spotify/i },
        { timeout: 3000 },
      ),
    ).toBeInTheDocument();
  });
});
