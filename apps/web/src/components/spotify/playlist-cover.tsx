import { cn } from "cn";
import { Heart } from "lucide-react";
import { RemoteImage } from "@/components/ui/remote-image";
import { LIKED_ID, type Playlist } from "@/server/spotify/schema";

export function PlaylistCover({
  playlist,
  className,
}: {
  playlist: Playlist;
  className?: string;
}) {
  if (playlist.id === LIKED_ID) {
    return (
      <div
        className={cn(
          "flex items-center justify-center bg-gradient-to-br from-brand to-emerald-900 text-white",
          className,
        )}
      >
        <Heart className="size-1/2 fill-current" />
      </div>
    );
  }
  return (
    <div className={cn("relative overflow-hidden bg-muted", className)}>
      {playlist.image && <RemoteImage src={playlist.image} />}
    </div>
  );
}
