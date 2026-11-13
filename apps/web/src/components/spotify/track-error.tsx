import { Lock, TriangleAlert } from "lucide-react";

export function TrackError({ message }: { message: string }) {
  const restricted = message.includes("only lets this app");

  return (
    <div
      role="alert"
      className="mx-auto my-6 flex max-w-md flex-col items-center gap-3 rounded-3xl glass-clear p-6 text-center"
    >
      <span
        className={`flex size-12 items-center justify-center rounded-full ${restricted ? "bg-brand/15 text-brand" : "bg-destructive/15 text-destructive"}`}
      >
        {restricted ? (
          <Lock className="size-5" />
        ) : (
          <TriangleAlert className="size-5" />
        )}
      </span>
      <div className="space-y-1">
        <p className="font-semibold">
          {restricted
            ? "Spotify keeps this playlist private"
            : "Could not load the tracks"}
        </p>
        <p className="text-sm text-muted-foreground">
          {restricted
            ? "Spotify only lets this app read playlists you own or collaborate on. Your own playlists and Liked Songs work as usual."
            : message}
        </p>
      </div>
    </div>
  );
}
