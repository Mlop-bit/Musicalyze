import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const apiUrl = process.env.MUSICALYZE_ML_API_URL ?? "http://localhost:8000";
  const apiKey = process.env.MUSICALYZE_API_KEY;
  if (!apiKey) {
    return NextResponse.json(
      { detail: "Track search is not configured. Set MUSICALYZE_API_KEY in the web environment." },
      { status: 503 },
    );
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ detail: "Invalid search request." }, { status: 400 });
  }

  try {
    const response = await fetch(`${apiUrl.replace(/\/$/, "")}/tracks/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-Key": apiKey },
      body: JSON.stringify(body),
      cache: "no-store",
    });
    const data: unknown = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json(
      { detail: "Could not reach the Musicalyze analysis service." },
      { status: 502 },
    );
  }
}
