import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createCallerFactory } from "../trpc";
import { appRouter } from "./_app";

vi.mock("../../github/client", () => ({
  fetchBranchCommits: vi.fn(),
}));

import { fetchBranchCommits } from "../../github/client";

const createCaller = createCallerFactory(appRouter);

beforeEach(() => {
  vi.mocked(fetchBranchCommits).mockReset();
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("changelog router", () => {
  it("getReleases reads the main branch", async () => {
    vi.mocked(fetchBranchCommits).mockResolvedValue([]);
    const caller = createCaller({});

    await caller.changelog.getReleases();

    expect(fetchBranchCommits).toHaveBeenCalledWith("main");
  });

  it("getCommits reads the development branch", async () => {
    vi.mocked(fetchBranchCommits).mockResolvedValue([]);
    const caller = createCaller({});

    await caller.changelog.getCommits();

    expect(fetchBranchCommits).toHaveBeenCalledWith("development");
  });
});
