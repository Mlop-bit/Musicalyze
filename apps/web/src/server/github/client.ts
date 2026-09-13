import { cache } from "react";
import { env } from "@/env";
import { COMMITS_PER_PAGE, GITHUB_OWNER, GITHUB_REPO } from "./constants";
import { type CommitEntry, CommitListSchema } from "./schema";

const GITHUB_API_BASE = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}`;

export const fetchBranchCommits = cache(
  async (branch: "main" | "development"): Promise<CommitEntry[]> => {
    const url = `${GITHUB_API_BASE}/commits?sha=${branch}&per_page=${COMMITS_PER_PAGE}`;
    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${env.MUSICALYZE_GITHUB_TOKEN}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
      },
      next: { revalidate: 3600 },
    });

    if (!response.ok) {
      throw new Error(
        `GitHub API request failed for branch "${branch}": ${response.status} ${response.statusText}`,
      );
    }

    const raw = await response.json();
    return CommitListSchema.parse(raw);
  },
);
