import { TRPCError } from "@trpc/server";
import type { z } from "zod";
import { env } from "@/env";

export async function callMl<S extends z.ZodType>(
  path: string,
  schema: S,
  body?: unknown,
): Promise<z.infer<S>> {
  const response = await fetch(`${env.MUSICALYZE_ML_API_URL}${path}`, {
    method: body === undefined ? "GET" : "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": env.MUSICALYZE_API_KEY,
    },
    body: body === undefined ? undefined : JSON.stringify(body),
    cache: "no-store",
  }).catch(() => {
    throw new TRPCError({
      code: "BAD_GATEWAY",
      message: "The analysis service is unreachable.",
    });
  });
  if (!response.ok) {
    const failure = (await response.json().catch(() => null)) as {
      detail?: unknown;
    } | null;
    const userFacing = response.status === 404 || response.status === 422;
    throw new TRPCError({
      code: userFacing ? "NOT_FOUND" : "BAD_GATEWAY",
      message:
        userFacing && typeof failure?.detail === "string"
          ? failure.detail
          : `The analysis service answered HTTP ${response.status}.`,
    });
  }
  return schema.parse(await response.json());
}
