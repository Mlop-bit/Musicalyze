"use client";

import { LogOut } from "lucide-react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { authClient } from "@/lib/auth-client";

export function LogoutButton() {
  const router = useRouter();

  function handleLogout() {
    authClient.signOut({
      fetchOptions: {
        onSuccess: () => router.push("/"),
      },
    });
  }

  return (
    <Button type="button" variant="outline" size="sm" onClick={handleLogout}>
      <LogOut aria-hidden="true" className="size-4" />
      Log out
    </Button>
  );
}
