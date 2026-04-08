"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { User } from "lucide-react";

export function AuthNav() {
  const { user } = useAuth();

  if (user) {
    return (
      <Link
        href="/dashboard"
        className="hidden items-center gap-1.5 text-sm text-zinc-500 transition-colors hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white sm:flex"
      >
        <User className="h-3.5 w-3.5" />
        {user.email?.split("@")[0]}
      </Link>
    );
  }

  return (
    <Link
      href="/auth"
      className="hidden text-sm text-zinc-500 transition-colors hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white sm:block"
    >
      Войти
    </Link>
  );
}
