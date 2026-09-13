import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { fetchBranchCommits } from "./client";

const fetchMock = vi.fn();

const SAMPLE_COMMIT = {
  sha: "abcdef1234567890",
  html_url: "https://github.com/Mlop-bit/AIProject/commit/abcdef1234567890",
  commit: {
    message: "fix: reduce cache ttl\n\nlonger body here",
    author: { name: "Stefano Marocco", date: "2026-09-01T10:00:00Z" },
  },
  author: { login: "fapakslapa" },
};

const SAMPLE_COMMIT_WITH_COAUTHORS = {
  sha: "1122334455667788",
  html_url: "https://github.com/Mlop-bit/AIProject/commit/1122334455667788",
  commit: {
    message:
      "feat: pair on changelog page\n\nWorked through the layout together.\n\nCo-authored-by: Ada Lovelace <ada@example.com>\nCo-Authored-By: Grace Hopper <grace@example.com>",
    author: { name: "Stefano Marocco", date: "2026-09-02T10:00:00Z" },
  },
  author: { login: "fapakslapa" },
};

beforeEach(() => {
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  vi.unstubAllGlobals();
  fetchMock.mockReset();
});

describe("fetchBranchCommits", () => {
  it("requests the given branch with an auth header and parses commits", async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => [SAMPLE_COMMIT],
    });

    const result = await fetchBranchCommits("development");

    expect(fetchMock).toHaveBeenCalledWith(
      "https://api.github.com/repos/Mlop-bit/AIProject/commits?sha=development&per_page=30",
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer test-token",
        }),
      }),
    );
    expect(result).toEqual([
      {
        sha: "abcdef1234567890",
        shortSha: "abcdef1",
        message: "fix: reduce cache ttl",
        coAuthors: [],
        author: "fapakslapa",
        date: "2026-09-01T10:00:00Z",
        htmlUrl:
          "https://github.com/Mlop-bit/AIProject/commit/abcdef1234567890",
      },
    ]);
  });

  it("extracts Co-authored-by trailers into coAuthors while keeping message to the first line", async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => [SAMPLE_COMMIT_WITH_COAUTHORS],
    });

    const result = await fetchBranchCommits("development");

    expect(result).toEqual([
      {
        sha: "1122334455667788",
        shortSha: "1122334",
        message: "feat: pair on changelog page",
        coAuthors: ["Ada Lovelace", "Grace Hopper"],
        author: "fapakslapa",
        date: "2026-09-02T10:00:00Z",
        htmlUrl:
          "https://github.com/Mlop-bit/AIProject/commit/1122334455667788",
      },
    ]);
  });

  it("throws when the GitHub API responds with an error status", async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "Not Found",
      json: async () => ({}),
    });

    await expect(fetchBranchCommits("main")).rejects.toThrow(/404/);
  });
});
