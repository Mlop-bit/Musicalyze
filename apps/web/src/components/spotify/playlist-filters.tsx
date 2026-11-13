"use client";

import { LayoutGrid, Rows3 } from "lucide-react";
import { useMemo, useState } from "react";
import { Input } from "@/components/ui/input";
import { Segmented } from "@/components/ui/segmented";
import { Select } from "@/components/ui/select";
import { LIKED_ID, type Playlist } from "@/server/spotify/schema";

export type Sort = "name" | "most" | "fewest";
export type Scope = "all" | "mine";
export type View = "grid" | "deck";

const SORTS: { value: Sort; label: string }[] = [
  { value: "name", label: "Name" },
  { value: "most", label: "Most tracks" },
  { value: "fewest", label: "Fewest tracks" },
];

const SCOPES: { value: Scope; label: string }[] = [
  { value: "all", label: "All" },
  { value: "mine", label: "Mine" },
];

const VIEWS: { value: View; label: React.ReactNode; ariaLabel: string }[] = [
  {
    value: "grid",
    label: <LayoutGrid className="size-4" />,
    ariaLabel: "Grid view",
  },
  {
    value: "deck",
    label: <Rows3 className="size-4" />,
    ariaLabel: "List view",
  },
];

export function usePlaylistFilters(
  playlists: Playlist[],
  ownerName: string | undefined,
) {
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState<Sort>("name");
  const [scope, setScope] = useState<Scope>("all");

  const visible = useMemo(() => {
    const term = search.trim().toLowerCase();
    const filtered = playlists
      .filter((playlist) => playlist.name.toLowerCase().includes(term))
      .filter(
        (playlist) =>
          scope === "all" ||
          playlist.owner === ownerName ||
          playlist.id === LIKED_ID,
      )
      .sort((a, b) =>
        sort === "name"
          ? a.name.localeCompare(b.name)
          : sort === "most"
            ? b.trackCount - a.trackCount
            : a.trackCount - b.trackCount,
      );
    return [
      ...filtered.filter((playlist) => playlist.id === LIKED_ID),
      ...filtered.filter((playlist) => playlist.id !== LIKED_ID),
    ];
  }, [playlists, search, sort, scope, ownerName]);

  return { visible, search, setSearch, sort, setSort, scope, setScope };
}

type Filters = ReturnType<typeof usePlaylistFilters>;

export function ViewToggle({
  view,
  onViewChange,
}: {
  view: View;
  onViewChange: (view: View) => void;
}) {
  return (
    <Segmented
      value={view}
      onValueChange={onViewChange}
      options={VIEWS}
      label="View"
    />
  );
}

export function PlaylistFilters({ filters }: { filters: Filters }) {
  return (
    <div className="@container flex flex-wrap items-center gap-2">
      <Input
        type="search"
        value={filters.search}
        onChange={(event) => filters.setSearch(event.target.value)}
        placeholder="Search playlists"
        aria-label="Search playlists"
        className="basis-full @lg:min-w-48 @lg:flex-1 @lg:basis-0"
      />
      <Select
        value={filters.sort}
        onValueChange={filters.setSort}
        options={SORTS}
        label="Sort playlists"
        className="min-w-0 flex-1 @lg:flex-none @lg:min-w-40"
      />
      <Segmented
        value={filters.scope}
        onValueChange={filters.setScope}
        options={SCOPES}
        label="Playlist owner"
      />
    </div>
  );
}
