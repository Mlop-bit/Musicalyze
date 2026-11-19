import { EXAMPLE_QUERIES } from "./examples";

type Props = { onPick: (query: string) => void; disabled: boolean };

export function ExampleChips({ onPick, disabled }: Props) {
  return (
    <div className="space-y-2">
      <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
        Try one
      </p>
      <ul className="flex flex-wrap gap-2">
        {EXAMPLE_QUERIES.map((query) => (
          <li key={query}>
            <button
              type="button"
              disabled={disabled}
              onClick={() => onPick(query)}
              className="glass-clear press rounded-full px-4 py-1.5 text-sm hover:text-brand disabled:opacity-50"
            >
              {query}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
