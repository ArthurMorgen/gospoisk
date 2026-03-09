"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Search, Loader2, Mail, Lock as LockIcon, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";
import { Footer } from "@/components/footer";

const SITE_NAME = "ГосПоиск";

export default function AuthPage() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const { signIn, signUp } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!email || !password) {
      setError("Заполните все поля");
      return;
    }
    if (password.length < 6) {
      setError("Пароль должен быть не менее 6 символов");
      return;
    }

    setLoading(true);
    try {
      if (mode === "login") {
        const { error: err } = await signIn(email, password);
        if (err) {
          setError(translateError(err));
        } else {
          router.push("/dashboard");
        }
      } else {
        const { error: err } = await signUp(email, password);
        if (err) {
          setError(translateError(err));
        } else {
          setSuccess("Проверьте почту для подтверждения аккаунта");
        }
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
          <h1 className="mb-1 text-center text-lg font-bold text-zinc-900">
            {mode === "login" ? "Войти в аккаунт" : "Создать аккаунт"}
          </h1>
          <p className="mb-6 text-center text-sm text-zinc-400">
            {mode === "login"
              ? "Введите email и пароль"
              : "Зарегистрируйтесь для полного доступа"}
          </p>

          <form onSubmit={handleSubmit} className="space-y-3.5">
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-300" />
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl border border-zinc-200 bg-zinc-50/50 py-2.5 pl-10 pr-4 text-sm text-zinc-900 outline-none transition-colors placeholder:text-zinc-400 focus:border-zinc-400 focus:bg-white focus:ring-1 focus:ring-zinc-400/20"
                autoComplete="email"
                autoFocus
              />
            </div>
            <div className="relative">
              <LockIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-300" />
              <input
                type="password"
                placeholder="Пароль"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-xl border border-zinc-200 bg-zinc-50/50 py-2.5 pl-10 pr-4 text-sm text-zinc-900 outline-none transition-colors placeholder:text-zinc-400 focus:border-zinc-400 focus:bg-white focus:ring-1 focus:ring-zinc-400/20"
                autoComplete={mode === "login" ? "current-password" : "new-password"}
              />
            </div>

            {error && (
              <div className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-600">
                {error}
              </div>
            )}
            {success && (
              <div className="rounded-lg bg-emerald-50 px-3 py-2 text-xs text-emerald-600">
                {success}
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
                  {mode === "login" ? "Войти" : "Зарегистрироваться"}
                  <ArrowRight className="h-3.5 w-3.5" />
                </>
              )}
            </Button>
          </form>

          <div className="mt-5 text-center">
            <button
              onClick={() => {
                setMode(mode === "login" ? "register" : "login");
                setError(null);
                setSuccess(null);
              }}
              className="text-sm text-zinc-400 transition-colors hover:text-zinc-700"
            >
              {mode === "login" ? (
                <>Нет аккаунта? <span className="font-medium text-zinc-700">Создать</span></>
              ) : (
                <>Уже есть аккаунт? <span className="font-medium text-zinc-700">Войти</span></>
              )}
            </button>
          </div>
        </div>

        <p className="mt-6 text-center text-xs text-zinc-400">
          Можно пользоваться без регистрации — 3 поиска в день
        </p>
        <div className="mt-3 text-center">
          <Link href="/dashboard" className="text-xs font-medium text-zinc-500 transition-colors hover:text-zinc-900">
            Продолжить без аккаунта →
          </Link>
        </div>
      </div>
      <Footer />
    </div>
  );
}

function translateError(msg: string): string {
  if (msg.includes("Invalid login")) return "Неверный email или пароль";
  if (msg.includes("already registered")) return "Этот email уже зарегистрирован";
  if (msg.includes("valid email")) return "Введите корректный email";
  if (msg.includes("Password")) return "Пароль должен быть не менее 6 символов";
  if (msg.includes("rate limit")) return "Слишком много попыток, подождите";
  return msg;
}
