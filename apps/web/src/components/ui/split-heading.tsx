import { Fragment } from "react";

type HeadingChar = {
  id: string;
  value: string;
};

type HeadingSegment =
  | { kind: "space"; id: string; value: string }
  | { kind: "word"; id: string; chars: HeadingChar[] };

function toSegments(text: string): HeadingSegment[] {
  let offset = 0;

  return text.split(/(\s+)/).map((value) => {
    const id = `${offset}:${value}`;

    if (value.trim() === "") {
      offset += value.length;
      return { kind: "space", id, value };
    }

    const chars = value.split("").map((char) => {
      const charId = `${offset}:${char}`;
      offset += 1;
      return { id: charId, value: char };
    });

    return { kind: "word", id, chars };
  });
}

export function splitHeading(text: string) {
  return toSegments(text).map((segment) => {
    if (segment.kind === "space") {
      return <Fragment key={segment.id}>{segment.value}</Fragment>;
    }

    return (
      <span
        key={segment.id}
        className="inline-flex overflow-hidden align-bottom"
      >
        {segment.chars.map((char) => (
          <span key={char.id} data-heading-char className="inline-block">
            {char.value}
          </span>
        ))}
      </span>
    );
  });
}
