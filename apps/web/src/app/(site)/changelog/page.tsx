import { ChangelogFeed } from "@/components/changelog/changelog-feed";
import { createServerCaller } from "@/server/trpc/caller";

export const revalidate = 3600;

export default async function ChangelogPage() {
  const caller = createServerCaller();
  const [releases, commits] = await Promise.all([
    caller.changelog.getReleases(),
    caller.changelog.getCommits(),
  ]);

  return (
    <main className="px-6 pb-20 pt-32 lg:px-14">
      <h1 className="text-5xl font-semibold tracking-tight sm:text-7xl">
        What{" "}
        <span className="font-script text-7xl font-normal text-brand sm:text-9xl">
          shipped
        </span>
      </h1>
      <p className="mb-12 mt-4 max-w-2xl text-muted-foreground">
        Every commit on the project repository. Development is day-to-day work;
        Release is what reached main.
      </p>
      <ChangelogFeed releases={releases} commits={commits} />
    </main>
  );
}
