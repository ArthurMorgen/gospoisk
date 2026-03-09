"use client";

import { useState } from "react";
import Link from "next/link";
import { Search, Send, MessageSquare, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Footer } from "@/components/footer";

const SITE_NAME = "ГосПоиск";

export default function FeedbackPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [type, setType] = useState<"feedback" | "bug" | "feature">("feedback");
  const [sent, setSent] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: отправка через Supabase или email API
    setSent(true);
  };

  const types = [
    { value: "feedback", label: "Отзыв" },
    { value: "bug", label: "Ошибка" },
    { value: "feature", label: "Идея" },
  ] as const;

  return (
    <div className="flex min-h-screen flex-col bg-zinc-50">
      <header className="border-b border-zinc-100/80 bg-white/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-2.5">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-zinc-800 to-zinc-950 shadow-sm">
              <Search className="h-3.5 w-3.5 text-white" />
            </div>
            <span className="text-base font-bold tracking-tight text-zinc-900">{SITE_NAME}</span>
          </Link>
          <Link href="/dashboard">
            <Button variant="outline" size="sm" className="rounded-full text-xs">
              К поиску
            </Button>
          </Link>
        </div>
      </header>

      <main className="mx-auto w-full max-w-lg flex-1 px-4 py-12">
        {sent ? (
          <div className="rounded-2xl border border-zinc-200/60 bg-white px-6 py-16 text-center">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-50">
              <CheckCircle2 className="h-7 w-7 text-emerald-500" />
            </div>
            <h2 className="mb-2 text-lg font-bold text-zinc-900">Спасибо за обращение!</h2>
            <p className="mb-6 text-sm text-zinc-400">
              Мы получили ваше сообщение и ответим в ближайшее время.
            </p>
            <Link href="/dashboard">
              <Button variant="outline" className="rounded-full">
                Вернуться к поиску
              </Button>
            </Link>
          </div>
        ) : (
          <>
            <div className="mb-8 text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-zinc-100">
                <MessageSquare className="h-5 w-5 text-zinc-500" />
              </div>
              <h1 className="text-xl font-bold text-zinc-900">Обратная связь</h1>
              <p className="mt-1.5 text-sm text-zinc-400">
                Нашли ошибку? Есть идея? Напишите нам
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="flex gap-2">
                {types.map((t) => (
                  <button
                    key={t.value}
                    type="button"
                    onClick={() => setType(t.value)}
                    className={`flex-1 rounded-xl border px-3 py-2.5 text-xs font-medium transition-all ${
                      type === t.value
                        ? "border-zinc-900 bg-zinc-900 text-white shadow-sm"
                        : "border-zinc-200 bg-white text-zinc-500 hover:border-zinc-300"
                    }`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>

              <div>
                <input
                  type="text"
                  placeholder="Ваше имя"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full rounded-xl border border-zinc-200 bg-white px-4 py-3 text-sm text-zinc-900 placeholder:text-zinc-300 focus:border-zinc-400 focus:outline-none focus:ring-0"
                />
              </div>

              <div>
                <input
                  type="email"
                  placeholder="Email для ответа"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-xl border border-zinc-200 bg-white px-4 py-3 text-sm text-zinc-900 placeholder:text-zinc-300 focus:border-zinc-400 focus:outline-none focus:ring-0"
                />
              </div>

              <div>
                <textarea
                  placeholder="Ваше сообщение..."
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  rows={5}
                  required
                  className="w-full resize-none rounded-xl border border-zinc-200 bg-white px-4 py-3 text-sm text-zinc-900 placeholder:text-zinc-300 focus:border-zinc-400 focus:outline-none focus:ring-0"
                />
              </div>

              <Button
                type="submit"
                disabled={!message.trim()}
                className="w-full gap-2 rounded-xl bg-zinc-900 py-6 text-sm font-semibold shadow-sm"
              >
                <Send className="h-4 w-4" />
                Отправить
              </Button>
            </form>
          </>
        )}
      </main>

      <Footer />
    </div>
  );
}
