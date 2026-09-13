"use client";

import {
  type DOMMotionComponents,
  domAnimation,
  type HTMLMotionProps,
  LazyMotion,
  type MotionProps,
  useInView,
} from "motion/react";
import * as m from "motion/react-m";
import {
  type ComponentType,
  type RefAttributes,
  type RefObject,
  useRef,
} from "react";

import { cn } from "@/lib/utils";
import { useTypewriter } from "./use-typewriter";

const motionElements = {
  article: m.article,
  div: m.div,
  h1: m.h1,
  h2: m.h2,
  h3: m.h3,
  h4: m.h4,
  h5: m.h5,
  h6: m.h6,
  li: m.li,
  p: m.p,
  section: m.section,
  span: m.span,
} as const;

type MotionElementType = Extract<
  keyof DOMMotionComponents,
  keyof typeof motionElements
>;
type TypingAnimationMotionComponent = ComponentType<
  Omit<HTMLMotionProps<"span">, "ref"> & RefAttributes<HTMLElement>
>;

interface TypingAnimationProps extends Omit<MotionProps, "children"> {
  children?: string;
  words?: string[];
  className?: string;
  duration?: number;
  typeSpeed?: number;
  deleteSpeed?: number;
  delay?: number;
  pauseDelay?: number;
  loop?: boolean;
  as?: MotionElementType;
  startOnView?: boolean;
  showCursor?: boolean;
  blinkCursor?: boolean;
  cursorStyle?: "line" | "block" | "underscore";
}

function getCursorChar(cursorStyle: TypingAnimationProps["cursorStyle"]) {
  switch (cursorStyle) {
    case "block":
      return "▌";
    case "underscore":
      return "_";
    case "line":
    default:
      return "|";
  }
}

export function TypingAnimation({
  children,
  words,
  className,
  duration = 100,
  typeSpeed,
  deleteSpeed,
  delay = 0,
  pauseDelay = 1000,
  loop = false,
  as: Component = "span",
  startOnView = true,
  showCursor = true,
  blinkCursor = true,
  cursorStyle = "line",
  ...props
}: TypingAnimationProps) {
  const MotionComponent = motionElements[
    Component
  ] as TypingAnimationMotionComponent;

  const elementRef = useRef<HTMLElement | null>(null);
  const isInView = useInView(elementRef as RefObject<Element>, {
    amount: 0.3,
    once: true,
  });
  const shouldStart = startOnView ? isInView : true;

  const typingSpeed = typeSpeed ?? duration;
  const deletingSpeed = deleteSpeed ?? typingSpeed / 2;

  const {
    displayedText,
    isComplete,
    hasMultipleWords,
    currentCharIndex,
    totalChars,
  } = useTypewriter({
    words,
    children,
    typingSpeed,
    deletingSpeed,
    pauseDelay,
    delay,
    loop,
    shouldStart,
  });

  const shouldShowCursor =
    showCursor &&
    !isComplete &&
    (hasMultipleWords || loop || currentCharIndex < totalChars);

  return (
    <LazyMotion features={domAnimation}>
      <MotionComponent
        ref={elementRef}
        className={cn(
          "leading-20 tracking-[-0.02em]",
          Component === "span" && "inline-block",
          className,
        )}
        {...props}
      >
        {displayedText}
        {shouldShowCursor && (
          <span
            className={cn(
              "inline-block",
              blinkCursor && "animate-blink-cursor",
            )}
          >
            {getCursorChar(cursorStyle)}
          </span>
        )}
      </MotionComponent>
    </LazyMotion>
  );
}
