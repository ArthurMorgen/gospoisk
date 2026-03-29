"use client";

import { useState, useRef, useEffect, useCallback, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  Search,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  Building2,
  Clock,
  Banknote,
  Loader2,
  X,
  Sparkles,
  ArrowUp,
  ArrowDownUp,
  Zap,
  Lock,
  User,
  LogOut,
  Bookmark,
  BookmarkCheck,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { searchTenders, type Tender, type SortOption } from "@/lib/api";
import { canSearch, recordSearch, getSearchesLeft, getLimit, isAdmin, FREE_SEARCH_LIMIT } from "@/lib/usage";
import { useAuth } from "@/lib/auth-context";
import { saveSearch } from "@/lib/saved-searches";

const SITE_NAME = "ГосПоиск";
const ITEMS_PER_PAGE = 10;

const EXAMPLE_KEYWORDS = [
  ["грамоты", "дипломы", "бланки"],
  ["канцтовары", "бумага"],
  ["мебель офисная"],
  ["компьютеры", "ноутбуки"],
  ["продукты питания"],
  ["строительные работы"],
];

const PLATFORM_NAMES: Record<string, string> = {
  suppliers_portal: "Портал поставщиков",
  suppliers_portal_new: "Портал поставщиков",
  portal: "Портал поставщиков",
  eis: "ЕИС",
  "Единая информационная система": "ЕИС",
  "ЕИС": "ЕИС",
};

const PLATFORM_COLORS: Record<string, string> = {
  "ЕИС": "bg-blue-500",
  "Портал поставщиков": "bg-emerald-500",
};

function getPlatformName(raw: string): string {
  return PLATFORM_NAMES[raw] || raw;
}

function formatPrice(price: number): string {
  if (!price || price === 0) return "";
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(price);
}

function TenderCard({ tender, index }: { tender: Tender; index: number }) {
  const displayPlatform = getPlatformName(tender.platform);
  const platformColor = PLATFORM_COLORS[displayPlatform] || "bg-zinc-400";

  return (
    <a
      href={tender.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block"
    >
      <Card className="group cursor-pointer border-zinc-200/60 bg-white transition-all hover:border-zinc-300 hover:shadow-lg hover:shadow-zinc-200/50">
        <CardContent className="p-4 sm:p-5">
          <div className="flex items-start gap-3">
            <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-zinc-100 text-[11px] font-bold tabular-nums text-zinc-400 transition-all group-hover:bg-zinc-900 group-hover:text-white group-hover:shadow-sm">
              {index}
            </span>
            <div className="min-w-0 flex-1">
              <div className="mb-2.5 flex items-start justify-between gap-2">
                <h3 className="text-[13px] font-semibold leading-snug text-zinc-900 transition-colors group-hover:text-blue-700">
                  {tender.title}
                </h3>
                <ExternalLink className="mt-0.5 h-3.5 w-3.5 shrink-0 text-zinc-200 transition-colors group-hover:text-blue-500" />
              </div>
              <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5">
                {tender.platform && (
                  <span className="flex items-center gap-1.5 text-xs text-zinc-400">
                    <span className={`inline-block h-1.5 w-1.5 rounded-full ${platformColor}`} />
                    {displayPlatform}
                  </span>
                )}
                {tender.price > 0 && (
                  <span className="flex items-center gap-1 rounded-md bg-zinc-50 px-1.5 py-0.5 text-xs font-semibold text-zinc-700">
                    <Banknote className="h-3 w-3 text-zinc-400" />
                    {formatPrice(tender.price)}
                  </span>
                )}
                {tender.deadline && (
                  <span className="flex items-center gap-1 text-xs text-zinc-400">
                    <Clock className="h-3 w-3" />
                    {tender.deadline}
                  </span>
                )}
                {tender.customer && (
                  <span className="flex items-center gap-1 text-xs text-zinc-400">
                    <Building2 className="h-3 w-3 shrink-0" />
                    <span className="max-w-[180px] truncate sm:max-w-[240px]">{tender.customer}</span>
                  </span>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </a>
  );
}

function TenderSkeleton() {
  return (
    <Card className="border-zinc-200/60">
      <CardContent className="p-4 sm:p-5">
        <div className="flex items-start gap-3">
          <Skeleton className="h-7 w-7 rounded-lg" />
          <div className="flex-1 space-y-3">
            <Skeleton className="h-4 w-4/5" />
            <div className="flex gap-3">
              <Skeleton className="h-3.5 w-16" />
              <Skeleton className="h-3.5 w-24" />
              <Skeleton className="h-3.5 w-20" />
              <Skeleton className="h-3.5 w-32" />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function DashboardPageWrapper() {
  return (
    <Suspense>
      <DashboardPage />
    </Suspense>
  );
}

function DashboardPage() {
  const { user, signOut } = useAuth();
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [keywords, setKeywords] = useState<string[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeKeywords, setActiveKeywords] = useState<string[]>([]);
  const [sort, setSort] = useState<SortOption>("relevance");
  const [searchTime, setSearchTime] = useState(0);
  const [wasCached, setWasCached] = useState(false);
  const [platforms, setPlatforms] = useState<string[]>(["portal", "eis"]);
  const [showPaywall, setShowPaywall] = useState(false);
  const [searchesLeft, setSearchesLeft] = useState(FREE_SEARCH_LIMIT);
  const userEmail = user?.email;
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const [elapsed, setElapsed] = useState(0);

  const searchParams = useSearchParams();

  useEffect(() => {
    inputRef.current?.focus();
    setSearchesLeft(getSearchesLeft(userEmail));

    const kwParam = searchParams.get("keywords");
    if (kwParam) {
      const kws = kwParam.split(",").map((k) => k.trim()).filter(Boolean);
      if (kws.length > 0) {
        setKeywords(kws);
        doSearch(kws, 1);
      }
    }
  }, []);

  const addKeyword = () => {
    const raw = inputValue.trim();
    if (!raw) return;
    const words = raw.split(",").map((w) => w.trim()).filter(Boolean);
    const newKw = [...keywords];
    for (const w of words) {
      if (!newKw.includes(w)) newKw.push(w);
    }
    setKeywords(newKw);
    setInputValue("");
    inputRef.current?.focus();
  };

  const removeKeyword = (kw: string) => {
    setKeywords(keywords.filter((k) => k !== kw));
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      if (inputValue.trim()) {
        addKeyword();
      } else if (keywords.length > 0) {
        doSearch(keywords, 1);
      }
    }
    if (e.key === "Backspace" && !inputValue && keywords.length > 0) {
      setKeywords(keywords.slice(0, -1));
    }
  };

  const cancelSearch = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setLoading(false);
  }, []);

  const doSearch = async (kws: string[], pg: number = 1, sortOpt?: SortOption) => {
    if (kws.length === 0) return;
    if (pg === 1 && !canSearch(userEmail)) {
      setShowPaywall(true);
      return;
    }
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setLoading(true);
    setError(null);
    setSearched(true);
    setActiveKeywords(kws);
    setElapsed(0);

    const timer = setInterval(() => setElapsed((e) => e + 1), 1000);

    try {
      const data = await searchTenders({
        keywords: kws,
        platforms,
        page: pg,
        per_page: ITEMS_PER_PAGE,
        sort: sortOpt || sort,
        signal: controller.signal,
      });
      setTenders(data.tenders);
      setTotal(data.total);
      setTotalPages(data.total_pages);
      setPage(pg);
      setSearchTime(data.search_time_ms);
      setWasCached(data.cached);
      if (pg === 1) {
        recordSearch();
        setSearchesLeft(getSearchesLeft(userEmail));
        resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Ошибка поиска";
      if (msg !== "Поиск отменён") setError(msg);
    } finally {
      clearInterval(timer);
      setLoading(false);
      abortRef.current = null;
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) addKeyword();
    const allKw = inputValue.trim()
      ? [...new Set([...keywords, ...inputValue.trim().split(",").map((w) => w.trim()).filter(Boolean)])]
      : keywords;
    if (allKw.length === 0) return;
    setKeywords(allKw);
    doSearch(allKw, 1);
  };

  const handlePageChange = (newPage: number) => {
    doSearch(activeKeywords, newPage);
  };

  const handleSort = (s: SortOption) => {
    setSort(s);
    if (activeKeywords.length > 0) doSearch(activeKeywords, 1, s);
  };

  const useExample = (ex: string[]) => {
    setKeywords(ex);
    doSearch(ex, 1);
  };

  const clearAll = () => {
    setKeywords([]);
    setTenders([]);
    setSearched(false);
    setError(null);
    setTotal(0);
    setSaved(false);
    inputRef.current?.focus();
  };

  const handleSave = async () => {
    if (!user || saving || saved || activeKeywords.length === 0) return;
    setSaving(true);
    const result = await saveSearch(activeKeywords, platforms);
    if (result) setSaved(true);
    setSaving(false);
  };

  return (
    <div className="min-h-screen bg-zinc-50">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-zinc-100/80 bg-white/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-2.5">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-zinc-800 to-zinc-950 shadow-sm">
              <Search className="h-3.5 w-3.5 text-white" />
            </div>
            <span className="text-base font-bold tracking-tight text-zinc-900">{SITE_NAME}</span>
          </Link>
          <div className="flex items-center gap-2.5">
            {searched && (
              <button
                onClick={clearAll}
                className="text-xs font-medium text-zinc-400 transition-colors hover:text-zinc-700"
              >
                Новый поиск
              </button>
            )}
            <Link
              href="/pricing"
              className={`rounded-full px-2.5 py-1 text-xs font-medium tabular-nums ${
                searchesLeft === 0
                  ? "bg-red-50 text-red-600"
                  : "bg-zinc-100 text-zinc-500"
              }`}
            >
              {isAdmin(userEmail) ? "∞" : `${searchesLeft}/${getLimit(userEmail)}`}
            </Link>
            {user ? (
              <div className="flex items-center gap-1.5">
                <Link
                  href="/saved"
                  className="flex h-7 w-7 items-center justify-center rounded-lg text-zinc-400 transition-colors hover:bg-zinc-100 hover:text-zinc-700"
                  title="Сохранённые поиски"
                >
                  <Bookmark className="h-3.5 w-3.5" />
                </Link>
                <span className="hidden text-xs text-zinc-400 sm:block">{user.email?.split("@")[0]}</span>
                <button
                  onClick={() => signOut()}
                  className="flex h-7 w-7 items-center justify-center rounded-lg text-zinc-400 transition-colors hover:bg-zinc-100 hover:text-zinc-700"
                  title="Выйти"
                >
                  <LogOut className="h-3.5 w-3.5" />
                </button>
              </div>
            ) : (
              <Link href="/auth">
                <button className="flex h-7 w-7 items-center justify-center rounded-lg bg-zinc-100 text-zinc-500 transition-colors hover:bg-zinc-200 hover:text-zinc-700">
                  <User className="h-3.5 w-3.5" />
                </button>
              </Link>
            )}
          </div>
        </div>
      </header>

      {/* Paywall Modal */}
      {showPaywall && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-md" onClick={() => setShowPaywall(false)}>
          <div className="mx-4 w-full max-w-sm rounded-2xl border border-zinc-200/50 bg-white p-7 shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-zinc-100 to-zinc-200">
              <Lock className="h-6 w-6 text-zinc-500" />
            </div>
            <h3 className="mb-2 text-center text-lg font-bold text-zinc-900">
              Лимит исчерпан
            </h3>
            <p className="mb-6 text-center text-sm leading-relaxed text-zinc-500">
              Вы использовали {FREE_SEARCH_LIMIT} бесплатных поиска на сегодня.
              Оформите подписку для безлимитного доступа.
            </p>
            <div className="flex flex-col gap-2.5">
              <Link href="/pricing">
                <Button className="w-full rounded-xl bg-zinc-900 shadow-sm shadow-zinc-900/20 transition-all hover:shadow-md">Смотреть тарифы</Button>
              </Link>
              <Button
                variant="ghost"
                className="w-full rounded-xl text-zinc-400 hover:text-zinc-600"
                onClick={() => setShowPaywall(false)}
              >
                Закрыть
              </Button>
            </div>
          </div>
        </div>
      )}

      <main className="mx-auto max-w-3xl px-4 py-6">
        {/* Search Form */}
        <div className="mb-6 rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm sm:p-5">
          <form onSubmit={handleSearch}>
            {/* Chips + Input in one row */}
            <div className="mb-3 flex flex-wrap items-center gap-1.5 rounded-lg border border-zinc-200 bg-zinc-50/50 px-2.5 py-2 focus-within:border-zinc-400 focus-within:ring-1 focus-within:ring-zinc-400/20">
              {keywords.map((kw) => (
                <Badge
                  key={kw}
                  variant="secondary"
                  className="gap-1 rounded-md py-0.5 pl-2 pr-1 text-xs"
                >
                  {kw}
                  <button
                    type="button"
                    onClick={() => removeKeyword(kw)}
                    className="rounded p-0.5 hover:bg-zinc-300"
                  >
                    <X className="h-2.5 w-2.5" />
                  </button>
                </Badge>
              ))}
              <input
                ref={inputRef}
                type="text"
                placeholder={keywords.length === 0 ? "Введите ключевые слова через запятую..." : "Ещё..."}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                className="min-w-[120px] flex-1 bg-transparent py-0.5 text-sm outline-none placeholder:text-zinc-400"
              />
            </div>

            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2 sm:gap-3">
                <p className="hidden text-xs text-zinc-400 sm:block">Enter — добавить, повторный — искать</p>
                <span className="hidden text-zinc-200 sm:block">|</span>
                {(["portal", "eis"] as const).map((p) => (
                  <label key={p} className="flex cursor-pointer items-center gap-1 text-xs">
                    <input
                      type="checkbox"
                      checked={platforms.includes(p)}
                      onChange={(e) => {
                        if (e.target.checked) setPlatforms([...platforms, p]);
                        else setPlatforms(platforms.filter((x) => x !== p));
                      }}
                      className="h-3 w-3 rounded accent-zinc-900"
                    />
                    <span className="text-zinc-500">{p === "portal" ? "Портал" : "ЕИС"}</span>
                  </label>
                ))}
              </div>
              <Button
                type="submit"
                disabled={(keywords.length === 0 && !inputValue.trim()) || loading}
                className="ml-auto gap-1.5 rounded-lg"
                size="sm"
              >
                {loading ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Search className="h-3.5 w-3.5" />
                )}
                Найти тендеры
              </Button>
            </div>
          </form>

          {/* Examples */}
          {!searched && (
            <div className="mt-4 border-t border-zinc-100 pt-4">
              <p className="mb-2.5 text-xs font-medium text-zinc-400">Попробуйте готовые запросы:</p>
              <div className="flex flex-wrap gap-1.5">
                {EXAMPLE_KEYWORDS.map((ex) => (
                  <button
                    key={ex.join(",")}
                    onClick={() => useExample(ex)}
                    className="flex items-center gap-1 rounded-lg border border-zinc-200 px-2.5 py-1.5 text-xs text-zinc-500 transition-all hover:border-zinc-400 hover:bg-zinc-50 hover:text-zinc-800"
                  >
                    <Sparkles className="h-3 w-3 text-zinc-300" />
                    {ex.join(", ")}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Results area */}
        <div ref={resultsRef}>
          {/* Stats + Sort */}
          {searched && !loading && tenders.length > 0 && (
            <div className="mb-3 space-y-2">
              <div className="flex items-center justify-between">
                <p className="text-xs text-zinc-400">
                  <span className="font-semibold text-zinc-700">{total}</span> тендеров
                  <span className="ml-1.5 inline-flex items-center gap-1 text-zinc-300">
                    <Zap className="h-3 w-3" />
                    {searchTime < 1000
                      ? `${searchTime} мс`
                      : `${(searchTime / 1000).toFixed(1)} с`}
                    {wasCached && " (кеш)"}
                  </span>
                </p>
                <div className="flex items-center gap-2">
                  {user && (
                    <button
                      onClick={handleSave}
                      disabled={saving || saved}
                      className={`flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium transition-all ${
                        saved
                          ? "bg-emerald-50 text-emerald-600"
                          : "bg-zinc-100 text-zinc-500 hover:bg-zinc-200 hover:text-zinc-700"
                      }`}
                    >
                      {saved ? (
                        <><BookmarkCheck className="h-3 w-3" /> Сохранено</>
                      ) : saving ? (
                        <><Loader2 className="h-3 w-3 animate-spin" /> ...</>
                      ) : (
                        <><Bookmark className="h-3 w-3" /> Сохранить</>
                      )}
                    </button>
                  )}
                  <p className="text-xs tabular-nums text-zinc-400">
                    Стр. {page}/{totalPages}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-1.5">
                <ArrowDownUp className="h-3 w-3 text-zinc-400" />
                {([
                  ["relevance", "По умолчанию"],
                  ["price_asc", "Цена ↑"],
                  ["price_desc", "Цена ↓"],
                  ["deadline", "Дедлайн"],
                ] as [SortOption, string][]).map(([value, label]) => (
                  <button
                    key={value}
                    onClick={() => handleSort(value)}
                    className={`rounded-md px-2 py-0.5 text-xs transition-colors ${
                      sort === value
                        ? "bg-zinc-900 text-white"
                        : "text-zinc-500 hover:bg-zinc-100"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="mb-4 flex items-center justify-between rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-600">
              <span>{error}</span>
              <button
                onClick={() => doSearch(activeKeywords, page)}
                className="shrink-0 rounded-lg bg-red-100 px-3 py-1 text-xs font-medium text-red-700 transition-colors hover:bg-red-200"
              >
                Повторить
              </button>
            </div>
          )}

          {/* Tenders List */}
          <div className="space-y-2">
            {loading ? (
              <>
                <div className="flex flex-col items-center gap-4 py-16">
                  <div className="relative flex h-14 w-14 items-center justify-center">
                    <div className="absolute inset-0 animate-spin rounded-full border-2 border-zinc-200 border-t-zinc-900" />
                    <Search className="h-5 w-5 text-zinc-400" />
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-medium text-zinc-700">
                      {elapsed < 5 ? "Подключаемся к площадкам..." : elapsed < 20 ? "Ищем по площадкам..." : elapsed < 40 ? "Парсим результаты..." : "Почти готово..."}
                    </p>
                    <p className="mt-1 tabular-nums text-xs text-zinc-400">{elapsed} сек</p>
                  </div>
                  <button
                    onClick={cancelSearch}
                    className="mt-1 rounded-full border border-zinc-200 px-4 py-1.5 text-xs font-medium text-zinc-500 transition-all hover:border-zinc-400 hover:text-zinc-700"
                  >
                    Отменить
                  </button>
                </div>
                <div className="space-y-2">
                  {Array.from({ length: 3 }).map((_, i) => <TenderSkeleton key={i} />)}
                </div>
              </>
            ) : searched && tenders.length === 0 ? (
              <div className="py-20 text-center">
                <Search className="mx-auto mb-3 h-10 w-10 text-zinc-200" />
                <p className="font-medium text-zinc-400">Ничего не нашлось</p>
                <p className="mt-1 text-sm text-zinc-300">Попробуйте другие ключевые слова</p>
              </div>
            ) : !searched ? (
              <div className="py-24 text-center">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-zinc-100">
                  <ArrowUp className="h-7 w-7 text-zinc-300" />
                </div>
                <p className="font-medium text-zinc-400">
                  Введите запрос выше
                </p>
                <p className="mt-1 text-sm text-zinc-300">
                  Или выберите один из готовых примеров
                </p>
              </div>
            ) : (
              tenders.map((tender, i) => (
                <TenderCard
                  key={tender.tender_id}
                  tender={tender}
                  index={(page - 1) * ITEMS_PER_PAGE + i + 1}
                />
              ))
            )}
          </div>

          {/* Pagination */}
          {searched && !loading && totalPages > 1 && (
            <div className="mt-5 flex items-center justify-center gap-2">
              <Button
                variant="outline"
                size="sm"
                className="h-8 w-8 rounded-lg p-0"
                onClick={() => handlePageChange(Math.max(1, page - 1))}
                disabled={page <= 1}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                let pageNum: number;
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (page <= 3) {
                  pageNum = i + 1;
                } else if (page >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = page - 2 + i;
                }
                return (
                  <Button
                    key={pageNum}
                    variant={pageNum === page ? "default" : "ghost"}
                    size="sm"
                    className="h-8 w-8 rounded-lg p-0 text-xs"
                    onClick={() => handlePageChange(pageNum)}
                  >
                    {pageNum}
                  </Button>
                );
              })}
              <Button
                variant="outline"
                size="sm"
                className="h-8 w-8 rounded-lg p-0"
                onClick={() => handlePageChange(Math.min(totalPages, page + 1))}
                disabled={page >= totalPages}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
