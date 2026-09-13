import { useEffect, useMemo, useState } from "react";

type Phase = "typing" | "pause" | "deleting";

type UseTypewriterArgs = {
  words?: string[];
  children?: string;
  typingSpeed: number;
  deletingSpeed: number;
  pauseDelay: number;
  delay: number;
  loop: boolean;
  shouldStart: boolean;
};

export function useTypewriter({
  words,
  children,
  typingSpeed,
  deletingSpeed,
  pauseDelay,
  delay,
  loop,
  shouldStart,
}: UseTypewriterArgs) {
  const wordsToAnimate = useMemo(
    () => words ?? (children ? [children] : []),
    [words, children],
  );
  const hasMultipleWords = wordsToAnimate.length > 1;
  const animationSourceKey = useMemo(
    () => (words ? words.join("\u0000") : (children ?? "")),
    [words, children],
  );

  const [displayedText, setDisplayedText] = useState("");
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [currentCharIndex, setCurrentCharIndex] = useState(0);
  const [phase, setPhase] = useState<Phase>("typing");
  const [prevAnimationSourceKey, setPrevAnimationSourceKey] =
    useState(animationSourceKey);

  if (animationSourceKey !== prevAnimationSourceKey) {
    setPrevAnimationSourceKey(animationSourceKey);
    setDisplayedText("");
    setCurrentWordIndex(0);
    setCurrentCharIndex(0);
    setPhase("typing");
  }

  useEffect(() => {
    let timeout: ReturnType<typeof setTimeout> | null = null;

    if (shouldStart && wordsToAnimate.length > 0) {
      const timeoutDelay =
        delay > 0 && displayedText === ""
          ? delay
          : phase === "typing"
            ? typingSpeed
            : phase === "deleting"
              ? deletingSpeed
              : pauseDelay;

      timeout = setTimeout(() => {
        const currentWord = wordsToAnimate[currentWordIndex] || "";
        const graphemes = Array.from(currentWord);

        switch (phase) {
          case "typing":
            if (currentCharIndex < graphemes.length) {
              setDisplayedText(
                graphemes.slice(0, currentCharIndex + 1).join(""),
              );
              setCurrentCharIndex((prev) => prev + 1);
            } else if (hasMultipleWords || loop) {
              const isLastWord = currentWordIndex === wordsToAnimate.length - 1;
              if (!isLastWord || loop) {
                setPhase("pause");
              }
            }
            break;

          case "pause":
            setPhase("deleting");
            break;

          case "deleting":
            if (currentCharIndex > 0) {
              setDisplayedText(
                graphemes.slice(0, currentCharIndex - 1).join(""),
              );
              setCurrentCharIndex((prev) => prev - 1);
            } else {
              const nextIndex = (currentWordIndex + 1) % wordsToAnimate.length;
              setCurrentWordIndex(nextIndex);
              setPhase("typing");
            }
            break;
        }
      }, timeoutDelay);
    }

    return () => {
      if (timeout !== null) {
        clearTimeout(timeout);
      }
    };
  }, [
    shouldStart,
    phase,
    currentCharIndex,
    currentWordIndex,
    displayedText,
    wordsToAnimate,
    hasMultipleWords,
    loop,
    typingSpeed,
    deletingSpeed,
    pauseDelay,
    delay,
  ]);

  const totalChars = Array.from(wordsToAnimate[currentWordIndex] || "").length;
  const isComplete =
    !loop &&
    currentWordIndex === wordsToAnimate.length - 1 &&
    currentCharIndex >= totalChars &&
    phase !== "deleting";

  return {
    displayedText,
    isComplete,
    hasMultipleWords,
    currentCharIndex,
    totalChars,
  };
}
