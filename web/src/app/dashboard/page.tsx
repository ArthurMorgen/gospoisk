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
  ArrowDown,
  ArrowDownUp,
  Zap,
  Lock,
  User,
  LogOut,
  Bookmark,
  BookmarkCheck,
  Download,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { searchTenders, predictBatch, fetchRegions, type Tender, type SortOption, type PredictionResult } from "@/lib/api";
import { canSearch, recordSearch, getSearchesLeft, getLimit, isAdmin, isPro, FREE_SEARCH_LIMIT } from "@/lib/usage";
import { useAuth } from "@/lib/auth-context";
import { saveSearch } from "@/lib/saved-searches";
import { ThemeToggle } from "@/components/theme-toggle";

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

function TenderCard({ tender, index, prediction, showPrediction }: { tender: Tender; index: number; prediction?: PredictionResult | null; showPrediction?: boolean }) {
  const displayPlatform = getPlatformName(tender.platform);
  const platformColor = PLATFORM_COLORS[displayPlatform] || "bg-zinc-400";

  return (
    <a
      href={tender.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block"
    >
      <Card className="group cursor-pointer border-zinc-200/60 bg-white transition-all hover:border-zinc-300 hover:shadow-lg hover:shadow-zinc-200/50 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-zinc-700 dark:hover:shadow-zinc-900/50">
        <CardContent className="p-4 sm:p-5">
          <div className="flex items-start gap-3">
            <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-zinc-100 text-[11px] font-bold tabular-nums text-zinc-400 transition-all group-hover:bg-zinc-900 group-hover:text-white group-hover:shadow-sm dark:bg-zinc-800 dark:text-zinc-500">
              {index}
            </span>
            <div className="min-w-0 flex-1">
              <div className="mb-2.5 flex items-start justify-between gap-2">
                <h3 className="text-[13px] font-semibold leading-snug text-zinc-900 transition-colors group-hover:text-blue-700 dark:text-zinc-100">
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
                  <span className="flex items-center gap-1 rounded-md bg-zinc-50 px-1.5 py-0.5 text-xs font-semibold text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
                    <Banknote className="h-3 w-3 text-zinc-400" />
                    {formatPrice(tender.price)}
                  </span>
                )}
                {prediction && prediction.drop_pct > 0 && showPrediction && (
                  <span className={`flex items-center gap-1 rounded-md px-1.5 py-0.5 text-xs font-semibold ${
                    prediction.confidence === 'high' ? 'bg-green-50 text-green-700' :
                    prediction.confidence === 'medium' ? 'bg-amber-50 text-amber-700' :
                    'bg-zinc-50 text-zinc-500'
                  }`}>
                    <ArrowDown className="h-3 w-3" />
                    ~{prediction.drop_pct}%
                  </span>
                )}
                {prediction && prediction.drop_pct > 0 && !showPrediction && (
                  <span className="flex items-center gap-1 rounded-md bg-zinc-100 px-1.5 py-0.5 text-xs font-semibold text-zinc-400 blur-[3px] select-none">
                    <ArrowDown className="h-3 w-3" />
                    ~{prediction.drop_pct}%
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
  const [predictions, setPredictions] = useState<(PredictionResult | null)[]>([]);
  const [saving, setSaving] = useState(false);
  const [region, setRegion] = useState("");
  const [regions, setRegions] = useState<string[]>([]);
  const [showPromo, setShowPromo] = useState(false);
  const promoTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const [elapsed, setElapsed] = useState(0);

  const searchParams = useSearchParams();

  useEffect(() => {
    inputRef.current?.focus();
    setSearchesLeft(getSearchesLeft(userEmail));
    fetchRegions().then(setRegions);

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

  const exportCSV = () => {
    if (tenders.length === 0) return;
    const header = "Название;Заказчик;Цена (₽);Площадка;Дедлайн;Ссылка";
    const rows = tenders.map((t) => {
      const title = (t.title || "").replace(/;/g, ",").replace(/\n/g, " ");
      const customer = (t.customer || "").replace(/;/g, ",").replace(/\n/g, " ");
      const price = t.price ? t.price.toLocaleString("ru-RU") : "—";
      const platform = t.platform.includes("suppliers_portal") ? "Портал поставщиков" : t.platform === "ЕИС" ? "ЕИС" : t.platform;
      const deadline = t.deadline || "—";
      const url = t.url || "";
      return `${title};${customer};${price};${platform};${deadline};${url}`;
    });
    const csv = "\uFEFF" + [header, ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `gospoisk_${activeKeywords.join("_")}_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

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
        region: region || undefined,
        signal: controller.signal,
      });
      setTenders(data.tenders);
      setTotal(data.total);
      setTotalPages(data.total_pages);
      setPage(pg);
      setSearchTime(data.search_time_ms);
      setWasCached(data.cached);
      // Прогноз снижения цены (в фоне)
      if (data.tenders.length > 0) {
        predictBatch(data.tenders.map(t => ({ title: t.title, price: t.price }))).then(setPredictions).catch(() => {});
      } else {
        setPredictions([]);
      }
      if (pg === 1) {
        recordSearch();
        setSearchesLeft(getSearchesLeft(userEmail));
        resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
        // Промо-модалка через 15 сек (только для незалогиненных, один раз за сессию)
        if (!userEmail && !sessionStorage.getItem("promo_shown")) {
          if (promoTimerRef.current) clearTimeout(promoTimerRef.current);
          promoTimerRef.current = setTimeout(() => {
            setShowPromo(true);
            sessionStorage.setItem("promo_shown", "1");
          }, 15000);
        }
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
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-zinc-100/80 bg-white/70 backdrop-blur-xl dark:border-zinc-800/80 dark:bg-zinc-950/70">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-2.5">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-zinc-800 to-zinc-950 shadow-sm">
              <Search className="h-3.5 w-3.5 text-white" />
            </div>
            <span className="text-base font-bold tracking-tight text-zinc-900 dark:text-white">{SITE_NAME}</span>
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
            <ThemeToggle />
            {user ? (
              <div className="flex items-center gap-1.5">
                <Link
                  href="/saved"
                  className="flex h-7 w-7 items-center justify-center rounded-lg text-zinc-400 transition-colors hover:bg-zinc-100 hover:text-zinc-700 dark:hover:bg-zinc-800 dark:hover:text-zinc-300"
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
            <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-amber-50 to-amber-100">
              <Lock className="h-6 w-6 text-amber-600" />
            </div>
            <h3 className="mb-2 text-center text-lg font-bold text-zinc-900">
              {userEmail ? "Дневной лимит исчерпан" : "Бесплатные поиски закончились"}
            </h3>
            <p className="mb-4 text-center text-sm leading-relaxed text-zinc-500">
              {userEmail
                ? `Вы использовали все ${getLimit(userEmail)} поисков на сегодня. Оформите подписку для безлимитного доступа.`
                : `Вы использовали ${FREE_SEARCH_LIMIT} бесплатных поисков. Зарегистрируйтесь — получите ${getLimit("user@")} поисков в день бесплатно.`}
            </p>
            {!userEmail && (
              <div className="mb-4 rounded-xl bg-emerald-50 px-4 py-3">
                <p className="text-center text-xs font-medium text-emerald-700">
                  Регистрация бесплатна — {getLimit("user@")} поисков/день вместо {FREE_SEARCH_LIMIT}
                </p>
              </div>
            )}
            <div className="mb-3 rounded-xl bg-zinc-50 p-3">
              <p className="mb-2 text-xs font-semibold text-zinc-700">С подпиской Про вы получите:</p>
              <ul className="space-y-1">
                {["Безлимитные поиски", "AI-прогноз снижения цены", "Telegram-уведомления"].map((f) => (
                  <li key={f} className="flex items-center gap-2 text-xs text-zinc-500">
                    <span className="h-1 w-1 rounded-full bg-blue-500" />
                    {f}
                  </li>
                ))}
              </ul>
            </div>
            <div className="flex flex-col gap-2.5">
              {!userEmail ? (
                <Link href="/auth">
                  <Button className="w-full rounded-xl bg-zinc-900 shadow-sm shadow-zinc-900/20 transition-all hover:shadow-md">
                    Зарегистрироваться бесплатно
                  </Button>
                </Link>
              ) : (
                <Link href="/pricing">
                  <Button className="w-full rounded-xl bg-zinc-900 shadow-sm shadow-zinc-900/20 transition-all hover:shadow-md">
                    Смотреть тарифы
                  </Button>
                </Link>
              )}
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

      {/* Promo Modal — после поиска для незалогиненных */}
      {showPromo && (
        <div className="fixed inset-0 z-[100] flex items-end justify-center sm:items-center" onClick={() => setShowPromo(false)}>
          <div className="absolute inset-0 bg-black/20 backdrop-blur-sm" />
          <div className="relative mx-4 mb-4 w-full max-w-sm rounded-2xl border border-zinc-200/50 bg-white p-6 shadow-2xl sm:mb-0" onClick={(e) => e.stopPropagation()}>
            <button onClick={() => setShowPromo(false)} className="absolute right-3 top-3 rounded-full p-1 text-zinc-300 hover:text-zinc-500">
              <X className="h-4 w-4" />
            </button>
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-50 to-violet-50">
              <Sparkles className="h-5 w-5 text-blue-600" />
            </div>
            <h3 className="mb-2 text-center text-base font-bold text-zinc-900">
              Хотите получать больше?
            </h3>
            <p className="mb-5 text-center text-xs leading-relaxed text-zinc-500">
              Зарегистрируйтесь бесплатно и получите {getLimit("user@")} поисков в день вместо {FREE_SEARCH_LIMIT}.
              Плюс возможность сохранять поиски и экспортировать результаты.
            </p>
            <Link href="/auth">
              <Button className="w-full rounded-xl bg-zinc-900 shadow-sm shadow-zinc-900/20">
                Зарегистрироваться бесплатно
              </Button>
            </Link>
            <p className="mt-3 text-center text-[10px] text-zinc-300">
              Без спама. Только поиск тендеров.
            </p>
          </div>
        </div>
      )}

      <main className="mx-auto max-w-3xl px-4 py-6">
        {/* Search Form */}
        <div className="mb-6 rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900 sm:p-5">
          <form onSubmit={handleSearch}>
            {/* Chips + Input in one row */}
            <div className="mb-3 flex flex-wrap items-center gap-1.5 rounded-lg border border-zinc-200 bg-zinc-50/50 px-2.5 py-2 focus-within:border-zinc-400 focus-within:ring-1 focus-within:ring-zinc-400/20 dark:border-zinc-700 dark:bg-zinc-800/50">
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
                className="min-w-[120px] flex-1 bg-transparent py-0.5 text-sm outline-none placeholder:text-zinc-400 dark:text-white dark:placeholder:text-zinc-500"
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
                <div className="relative">
                  <input
                    type="text"
                    value={region}
                    onChange={(e) => setRegion(e.target.value)}
                    placeholder="Регион"
                    list="region-list"
                    className="h-7 w-28 rounded-md border border-zinc-200 bg-white px-2 text-xs text-zinc-600 outline-none focus:border-zinc-400 focus:ring-1 focus:ring-zinc-400/20 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-300 sm:w-40"
                  />
                  <datalist id="region-list">
                    {regions.map((r) => (
                      <option key={r} value={r} />
                    ))}
                  </datalist>
                  {region && (
                    <button
                      type="button"
                      onClick={() => setRegion("")}
                      className="absolute right-1 top-1/2 -translate-y-1/2 rounded p-0.5 text-zinc-300 hover:text-zinc-500"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  )}
                </div>
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
            <div className="mt-4 border-t border-zinc-100 pt-4 dark:border-zinc-800">
              <p className="mb-2.5 text-xs font-medium text-zinc-400">Попробуйте готовые запросы:</p>
              <div className="flex flex-wrap gap-1.5">
                {EXAMPLE_KEYWORDS.map((ex) => (
                  <button
                    key={ex.join(",")}
                    onClick={() => useExample(ex)}
                    className="flex items-center gap-1 rounded-lg border border-zinc-200 px-2.5 py-1.5 text-xs text-zinc-500 transition-all hover:border-zinc-400 hover:bg-zinc-50 hover:text-zinc-800 dark:border-zinc-700 dark:text-zinc-400 dark:hover:border-zinc-600 dark:hover:bg-zinc-800 dark:hover:text-white"
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
                  <span className="font-semibold text-zinc-700 dark:text-zinc-300">{total}</span> тендеров
                  <span className="ml-1.5 inline-flex items-center gap-1 text-zinc-300">
                    <Zap className="h-3 w-3" />
                    {searchTime < 1000
                      ? `${searchTime} мс`
                      : `${(searchTime / 1000).toFixed(1)} с`}
                    {wasCached && " (кеш)"}
                  </span>
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={exportCSV}
                    className="flex items-center gap-1 rounded-full bg-zinc-100 px-2.5 py-1 text-xs font-medium text-zinc-500 transition-all hover:bg-zinc-200 hover:text-zinc-700 dark:bg-zinc-800 dark:text-zinc-400 dark:hover:bg-zinc-700 dark:hover:text-white"
                  >
                    <Download className="h-3 w-3" /> CSV
                  </button>
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
                        : "text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800"
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
                    <p className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
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
                  prediction={predictions[i]}
                  showPrediction={isPro(userEmail)}
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
