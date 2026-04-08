import type { Metadata } from "next";
import Link from "next/link";
import { Search, ArrowRight, BookOpen, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Footer } from "@/components/footer";
import { BLOG_POSTS } from "@/lib/blog";

export const metadata: Metadata = {
  title: "Блог | Статьи о поиске тендеров и госзакупках",
  description: "Полезные статьи о поиске тендеров, госзакупках, стратегиях участия и инструментах для поставщиков. Пошаговые инструкции и практические кейсы.",
  keywords: [
    "блог о тендерах", "статьи о госзакупках", "как найти тендер",
    "поиск тендеров инструкция", "44-ФЗ", "223-ФЗ",
  ],
};

export default function BlogPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-zinc-950">
      <header className="sticky top-0 z-50 border-b border-zinc-100/80 bg-white/70 backdrop-blur-xl dark:border-zinc-800/80 dark:bg-zinc-950/70">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-zinc-800 to-zinc-950 shadow-sm">
              <Search className="h-4 w-4 text-white" />
            </div>
            <span className="text-lg font-bold tracking-tight text-zinc-900 dark:text-white">ГосПоиск</span>
          </Link>
          <Link href="/dashboard">
            <Button variant="outline" size="sm" className="gap-1.5 rounded-full">
              <Search className="h-3.5 w-3.5" />
              К поиску
            </Button>
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-10 sm:px-6 sm:py-16">
        <div className="mb-10 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-zinc-100 dark:bg-zinc-800">
            <BookOpen className="h-5 w-5 text-zinc-600 dark:text-zinc-400" />
          </div>
          <h1 className="mb-3 text-2xl font-bold text-zinc-900 dark:text-white sm:text-3xl">Блог ГосПоиск</h1>
          <p className="mx-auto max-w-md text-sm text-zinc-500">
            Статьи о поиске тендеров, стратегиях участия в госзакупках и инструментах для поставщиков
          </p>
        </div>

        <div className="space-y-5">
          {BLOG_POSTS.map((post) => (
            <Link
              key={post.slug}
              href={`/blog/${post.slug}`}
              className="group block rounded-2xl border border-zinc-100 bg-white p-6 transition-all hover:border-zinc-200 hover:shadow-lg hover:shadow-zinc-100/80 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-zinc-700 dark:hover:shadow-zinc-900/50 sm:p-8"
            >
              <div className="mb-3 flex flex-wrap items-center gap-2">
                {post.tags.map((tag) => (
                  <span
                    key={tag}
                    className="rounded-full bg-zinc-100 px-2.5 py-0.5 text-[10px] font-medium uppercase tracking-wider text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400"
                  >
                    {tag}
                  </span>
                ))}
              </div>
              <h2 className="mb-2 text-lg font-bold text-zinc-900 transition-colors group-hover:text-blue-600 dark:text-white sm:text-xl">
                {post.title}
              </h2>
              <p className="mb-4 text-sm leading-relaxed text-zinc-500">{post.description}</p>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 text-xs text-zinc-400">
                  <span>{new Date(post.date).toLocaleDateString("ru-RU", { day: "numeric", month: "long", year: "numeric" })}</span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {post.readTime}
                  </span>
                </div>
                <span className="flex items-center gap-1 text-xs font-medium text-blue-600 opacity-0 transition-opacity group-hover:opacity-100">
                  Читать <ArrowRight className="h-3 w-3" />
                </span>
              </div>
            </Link>
          ))}
        </div>
      </main>

      <Footer />
    </div>
  );
}
