import { z } from "zod";

const API = "https://api.deezer.com";

const trackSchema = z.object({ preview: z.string() });
const searchSchema = z.object({ data: z.array(trackSchema) });

type Query = { isrc: string | null; title: string; artist: string };

async function getJson(url: string) {
  const response = await fetch(url, { cache: "no-store" });
  return response.ok ? ((await response.json()) as unknown) : null;
}

export async function findPreviewUrl({
  isrc,
  title,
  artist,
}: Query): Promise<string | null> {
  if (isrc) {
    const byIsrc = trackSchema.safeParse(
      await getJson(`${API}/track/isrc:${encodeURIComponent(isrc)}`),
    );
    if (byIsrc.success && byIsrc.data.preview) return byIsrc.data.preview;
  }
  const search = new URLSearchParams({
    q: `${artist} ${title}`,
    limit: "1",
  });
  const bySearch = searchSchema.safeParse(
    await getJson(`${API}/search?${search}`),
  );
  return bySearch.success ? bySearch.data.data[0]?.preview || null : null;
}
