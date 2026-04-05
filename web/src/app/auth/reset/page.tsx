"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Search, Loader2, Lock as LockIcon, ArrowRight, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";
import { Footer } from "@/components/footer";

const SITE_NAME = "ГосПоиск";

export default function ResetPasswordPage() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const { updatePassword, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (done) {
      const timer = setTimeout(() => router.push("/dashboard"), 2000);
      return () => clearTimeout(timer);
    }
  }, [done, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!password || password.length < 6) {
      setError("Пароль должен быть не менее 6 символов");
      return;
    }
    if (password !== confirmPassword) {
      setError("Пароли не совпадают");
      return;
    }

    setLoading(true);
    try {
      const { error: err } = await updatePassword(password);
      if (err) {
        setError(err);
      } else {
        setDone(true);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-white px-4">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -right-60 -top-60 h-[500px] w-[500px] rounded-full bg-blue-50/60 blur-3xl" />
        <div className="absolute -left-60 bottom-0 h-[400px] w-[400px] rounded-full bg-violet-50/40 blur-3xl" />
      </div>

      <div className="relative w-full max-w-sm">
        <Link href="/" className="mb-8 flex items-center justify-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-zinc-800 to-zinc-950 shadow-sm">
            <Search className="h-4 w-4 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight text-zinc-900">{SITE_NAME}</span>
        </Link>

        <div className="rounded-2xl border border-zinc-200/60 bg-white p-7 shadow-xl shadow-zinc-100/50">
          {done ? (
            <div className="flex flex-col items-center gap-3 py-4">
              <CheckCircle className="h-10 w-10 text-emerald-500" />
              <h1 className="text-lg font-bold text-zinc-900">Пароль изменён</h1>
              <p className="text-sm text-zinc-400">Перенаправляем в дашборд...</p>
            </div>
          ) : (
            <>
              <h1 className="mb-1 text-center text-lg font-bold text-zinc-900">
                Новый пароль
              </h1>
              <p className="mb-6 text-center text-sm text-zinc-400">
                Введите новый пароль для вашего аккаунта
              </p>

              <form onSubmit={handleSubmit} className="space-y-3.5">
                <div className="relative">
                  <LockIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-300" />
                  <input
                    type="password"
                    placeholder="Новый пароль"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full rounded-xl border border-zinc-200 bg-zinc-50/50 py-2.5 pl-10 pr-4 text-sm text-zinc-900 outline-none transition-colors placeholder:text-zinc-400 focus:border-zinc-400 focus:bg-white focus:ring-1 focus:ring-zinc-400/20"
                    autoComplete="new-password"
                    autoFocus
                  />
                </div>
                <div className="relative">
                  <LockIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-300" />
                  <input
                    type="password"
                    placeholder="Повторите пароль"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full rounded-xl border border-zinc-200 bg-zinc-50/50 py-2.5 pl-10 pr-4 text-sm text-zinc-900 outline-none transition-colors placeholder:text-zinc-400 focus:border-zinc-400 focus:bg-white focus:ring-1 focus:ring-zinc-400/20"
                    autoComplete="new-password"
                  />
                </div>

                {error && (
                  <div className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-600">
                    {error}
                  </div>
                )}

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full gap-2 rounded-xl bg-zinc-900 py-2.5 shadow-sm shadow-zinc-900/20 transition-all hover:shadow-md"
                >
                  {loading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <>
                      Сохранить пароль
                      <ArrowRight className="h-3.5 w-3.5" />
                    </>
                  )}
                </Button>
              </form>
            </>
          )}
        </div>
      </div>
      <Footer />
    </div>
  );
}
