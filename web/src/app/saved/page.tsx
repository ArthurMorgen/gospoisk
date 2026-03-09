"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Search,
  Trash2,
  Play,
  Clock,
  Bookmark,
  ArrowLeft,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/lib/auth-context";
import { Footer } from "@/components/footer";
import {
  getSavedSearches,
  deleteSavedSearch,
  type SavedSearch,
} from "@/lib/saved-searches";

const SITE_NAME = "ГосПоиск";

export default function SavedPage() {
  const { user, loading: authLoading } = useAuth();
  const [searches, setSearches] = useState<SavedSearch[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.push("/auth");
      return;
    }
    loadSearches();
  }, [user, authLoading]);

  const loadSearches = async () => {
    setLoading(true);
    const data = await getSavedSearches();
    setSearches(data);
    setLoading(false);
  };

  const handleDelete = async (id: string) => {
    await deleteSavedSearch(id);
    setSearches(searches.filter((s) => s.id !== id));
  };

  const handleRun = (search: SavedSearch) => {
    const params = new URLSearchParams();
    params.set("keywords", search.keywords.join(","));
    if (search.platforms?.length) params.set("platforms", search.platforms.join(","));
    router.push(`/dashboard?${params.toString()}`);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("ru-RU", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (authLoading || (!user && !authLoading)) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-zinc-400" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50">
      <header className="sticky top-0 z-50 border-b border-zinc-100/80 bg-white/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-2.5">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-zinc-800 to-zinc-950 shadow-sm">
              <Search className="h-3.5 w-3.5 text-white" />
            </div>
            <span className="text-base font-bold tracking-tight text-zinc-900">{SITE_NAME}</span>
          </Link>
          <Link href="/dashboard">
            <Button variant="outline" size="sm" className="gap-1.5 rounded-full text-xs">
              <ArrowLeft className="h-3 w-3" />
              К поиску
            </Button>
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-4 py-8">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-zinc-100">
            <Bookmark className="h-5 w-5 text-zinc-500" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-zinc-900">Сохранённые поиски</h1>
            <p className="text-xs text-zinc-400">
              {searches.length > 0
                ? `${searches.length} ${searches.length === 1 ? "поиск" : "поисков"}`
                : "Пока пусто"}
            </p>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-5 w-5 animate-spin text-zinc-400" />
          </div>
        ) : searches.length === 0 ? (
          <div className="rounded-2xl border border-zinc-200/60 bg-white px-6 py-16 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-zinc-100">
              <Bookmark className="h-5 w-5 text-zinc-300" />
            </div>
            <p className="mb-1 font-semibold text-zinc-900">Нет сохранённых поисков</p>
            <p className="mb-5 text-sm text-zinc-400">
              Выполните поиск на дашборде и нажмите «Сохранить»
            </p>
            <Link href="/dashboard">
              <Button variant="outline" className="gap-2 rounded-full">
                <Search className="h-3.5 w-3.5" />
                Перейти к поиску
              </Button>
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {searches.map((search) => (
              <Card
                key={search.id}
                className="group border-zinc-200/60 bg-white transition-all hover:border-zinc-300 hover:shadow-md"
              >
                <CardContent className="flex items-center gap-4 p-4">
                  <div className="min-w-0 flex-1">
                    <div className="mb-2 flex flex-wrap gap-1.5">
                      {search.keywords.map((kw) => (
                        <Badge key={kw} variant="secondary" className="rounded-md text-xs">
                          {kw}
                        </Badge>
                      ))}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-zinc-400">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatDate(search.created_at)}
                      </span>
                      {search.platforms?.length > 0 && (
                        <span>{search.platforms.map((p) => p === "eis" ? "ЕИС" : "Портал").join(", ")}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex shrink-0 items-center gap-1.5">
                    <button
                      onClick={() => handleRun(search)}
                      className="flex h-8 w-8 items-center justify-center rounded-lg bg-zinc-900 text-white shadow-sm transition-all hover:shadow-md"
                      title="Запустить поиск"
                    >
                      <Play className="h-3.5 w-3.5" />
                    </button>
                    <button
                      onClick={() => handleDelete(search.id)}
                      className="flex h-8 w-8 items-center justify-center rounded-lg text-zinc-300 transition-colors hover:bg-red-50 hover:text-red-500"
                      title="Удалить"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}
