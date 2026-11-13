import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { LoginCard } from "@/components/auth/login-card";
import { auth } from "@/server/auth/auth";

export default async function LoginPage() {
  const session = await auth.api.getSession({ headers: await headers() });
  if (session) redirect("/dashboard");

  return <LoginCard />;
}
