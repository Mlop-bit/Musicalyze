import { z } from "zod";

const GitHubCommitApiItemSchema = z.object({
  sha: z.string(),
  html_url: z.url(),
  commit: z.object({
    message: z.string(),
    author: z.object({
      name: z.string(),
      date: z.string(),
    }),
  }),
  author: z.object({ login: z.string() }).nullable(),
});

const CO_AUTHOR_TRAILER_PATTERN = /^co-authored-by:\s*(.+?)\s*<[^<>]*>\s*$/gim;

function extractCoAuthors(message: string): string[] {
  return Array.from(message.matchAll(CO_AUTHOR_TRAILER_PATTERN), (match) =>
    match[1].trim(),
  );
}

export const CommitEntrySchema = GitHubCommitApiItemSchema.transform((raw) => ({
  sha: raw.sha,
  shortSha: raw.sha.slice(0, 7),
  message: raw.commit.message.split("\n")[0],
  coAuthors: extractCoAuthors(raw.commit.message),
  author: raw.author?.login ?? raw.commit.author.name,
  date: raw.commit.author.date,
  htmlUrl: raw.html_url,
}));

export type CommitEntry = {
  sha: string;
  shortSha: string;
  message: string;
  coAuthors: string[];
  author: string;
  date: string;
  htmlUrl: string;
};

export const CommitListSchema = z.compile(z.array(CommitEntrySchema));
