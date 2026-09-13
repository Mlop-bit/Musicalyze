import { forwardRef } from "react";

type HeroWordmarkProps = {
  text: string;
};

export const HeroWordmark = forwardRef<HTMLHeadingElement, HeroWordmarkProps>(
  function HeroWordmark({ text }, ref) {
    return (
      <h1
        ref={ref}
        className="overflow-hidden font-sans text-[clamp(1.75rem,6vw,6rem)] leading-[0.95] font-extrabold tracking-tight text-foreground"
      >
        <div className="flex flex-nowrap">
          {text.split("").map((letter) => (
            <span key={letter} data-wordmark-letter className="inline-block">
              {letter}
            </span>
          ))}
        </div>
      </h1>
    );
  },
);
