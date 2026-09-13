import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { LogoutButton } from "@/components/dashboard/logout-button";
import {
  Card,
  CardContent,
  CardDescription,
  CardTitle,
} from "@/components/ui/card";
import { auth } from "@/server/auth/auth";

export default async function DashboardPage() {
  const session = await auth.api.getSession({ headers: await headers() });

  if (!session) {
    redirect("/");
  }

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-6 py-16 sm:px-10">
      <div className="flex items-center justify-between gap-4">
        <h1 className="font-sans text-3xl font-semibold text-foreground sm:text-4xl">
          {session.user.name}
        </h1>
        <LogoutButton />
      </div>

      <Card className="max-w-sm">
        <CardContent className="flex flex-col gap-1.5">
          <CardTitle>Account</CardTitle>
          <CardDescription>{session.user.email}</CardDescription>
        </CardContent>
      </Card>
    </main>
  );
}
