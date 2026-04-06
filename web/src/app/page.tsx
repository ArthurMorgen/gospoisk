import Link from "next/link";
import { Footer } from "@/components/footer";
import {
  Search,
  Zap,
  Shield,
  Clock,
  ArrowRight,
  Layers,
  TrendingUp,
  Target,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { CATEGORIES } from "@/lib/categories";
import { ThemeToggle } from "@/components/theme-toggle";

const SITE_NAME = "ГосПоиск";

const DEMO_KEYWORDS = ["мебель", "канцтовары", "IT-оборудование", "стройматериалы", "медицина", "продукты"];

export default function Home() {
  return (
    <div className="min-h-screen bg-white dark:bg-zinc-950">
      {/* Header */}
      <header className="fixed top-0 z-50 w-full border-b border-zinc-100/80 bg-white/70 backdrop-blur-xl dark:border-zinc-800/80 dark:bg-zinc-950/70">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-zinc-800 to-zinc-950 shadow-sm">
              <Search className="h-4 w-4 text-white" />
            </div>
            <span className="text-lg font-bold tracking-tight text-zinc-900 dark:text-white">{SITE_NAME}</span>
          </Link>
          <div className="flex items-center gap-3 sm:gap-4">
            <Link href="/pricing" className="hidden text-sm text-zinc-500 transition-colors hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white sm:block">
              Тарифы
            </Link>
            <Link href="/feedback" className="hidden text-sm text-zinc-500 transition-colors hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white md:block">
              Обратная связь
            </Link>
            <Link href="/auth" className="text-sm text-zinc-500 transition-colors hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white">
              Войти
            </Link>
            <ThemeToggle />
            <Link href="/dashboard">
              <Button size="sm" className="rounded-full bg-zinc-900 px-4 text-xs shadow-sm shadow-zinc-900/20 transition-all hover:shadow-md hover:shadow-zinc-900/20 sm:px-5 sm:text-sm">
                Начать поиск
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute -right-40 -top-40 h-[500px] w-[500px] rounded-full bg-blue-100/40 blur-3xl dark:bg-blue-900/20" />
          <div className="absolute -left-40 top-20 h-[400px] w-[400px] rounded-full bg-violet-100/30 blur-3xl dark:bg-violet-900/15" />
        </div>
        <div className="relative mx-auto max-w-6xl px-4 pb-16 pt-28 text-center sm:px-6 sm:pb-24 sm:pt-36">
          <div className="mx-auto max-w-2xl">
            <div className="mb-6 inline-flex items-center gap-1.5 rounded-full border border-zinc-200 bg-white px-3 py-1 text-xs font-medium text-zinc-600 shadow-sm dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300">
              <Sparkles className="h-3 w-3 text-amber-500" />
              Портал поставщиков + ЕИС — уже работает
            </div>
            <h1 className="mb-5 text-3xl font-extrabold leading-[1.1] tracking-tight text-zinc-900 dark:text-white sm:mb-6 sm:text-5xl md:text-6xl">
              Все тендеры по вашему
              <br />
              <span className="bg-gradient-to-r from-blue-600 via-violet-600 to-purple-600 bg-clip-text text-transparent">
                запросу за секунды
              </span>
            </h1>
            <p className="mx-auto mb-6 max-w-md text-sm leading-relaxed text-zinc-500 dark:text-zinc-400 sm:mb-8 sm:text-[1.1rem]">
              Введите ключевые слова — получите актуальные закупки
              со всех площадок в одном окне.
            </p>
            <Link href="/dashboard">
              <Button size="lg" className="h-12 gap-2 rounded-full bg-zinc-900 px-8 text-base shadow-xl shadow-zinc-900/15 transition-all hover:scale-[1.02] hover:shadow-2xl hover:shadow-zinc-900/20">
                Найти тендеры <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <p className="mt-4 text-sm text-zinc-400">Бесплатно. Без регистрации. 10 поисков в день.</p>

            {/* Floating keywords */}
            <div className="mt-10 flex flex-wrap justify-center gap-2">
              {DEMO_KEYWORDS.map((kw) => (
                <span
                  key={kw}
                  className="rounded-full border border-zinc-200/80 bg-white/80 px-3 py-1 text-xs text-zinc-400 shadow-sm backdrop-blur-sm dark:border-zinc-700/80 dark:bg-zinc-900/80 dark:text-zinc-500"
                >
                  {kw}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Площадки — social proof */}
      <section className="border-b border-zinc-100 bg-white py-8 dark:border-zinc-800 dark:bg-zinc-950">
        <div className="mx-auto max-w-4xl px-4 sm:px-6">
          <p className="mb-5 text-center text-xs font-medium uppercase tracking-widest text-zinc-300">
            Ищем на официальных площадках
          </p>
          <div className="flex flex-wrap items-center justify-center gap-8 sm:gap-14">
            <a href="https://zakupki.gov.ru" target="_blank" rel="noopener noreferrer" className="group flex items-center gap-2 text-zinc-300 transition-colors hover:text-zinc-600">
              <Shield className="h-5 w-5" />
              <span className="text-sm font-semibold tracking-tight">ЕИС (zakupki.gov.ru)</span>
            </a>
            <a href="https://zakupki.mos.ru" target="_blank" rel="noopener noreferrer" className="group flex items-center gap-2 text-zinc-300 transition-colors hover:text-zinc-600">
              <Layers className="h-5 w-5" />
              <span className="text-sm font-semibold tracking-tight">Портал поставщиков</span>
            </a>
          </div>
        </div>
      </section>

      {/* Как это работает — 3 шага */}
      <section className="border-y border-zinc-100 bg-zinc-50/50 py-14 dark:border-zinc-800 dark:bg-zinc-900/50 sm:py-24">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <p className="mb-2 text-center text-xs font-semibold uppercase tracking-[0.2em] text-blue-600">
            Как это работает
          </p>
          <h2 className="mb-8 text-center text-xl font-bold text-zinc-900 dark:text-white sm:mb-14 sm:text-3xl">
            Три шага до нужного тендера
          </h2>
          <div className="grid gap-6 sm:grid-cols-3">
            {[
              {
                step: "01",
                icon: <Target className="h-5 w-5" />,
                color: "from-blue-500 to-blue-700",
                title: "Введите ключевые слова",
                desc: "Что угодно: мебель, IT, стройматериалы, продукты, медицина — без ограничений.",
              },
              {
                step: "02",
                icon: <Zap className="h-5 w-5" />,
                color: "from-violet-500 to-violet-700",
                title: "Система ищет по площадкам",
                desc: "Параллельный поиск по ЕИС, Порталу поставщиков и другим площадкам.",
              },
              {
                step: "03",
                icon: <TrendingUp className="h-5 w-5" />,
                color: "from-emerald-500 to-emerald-700",
                title: "Получите результат",
                desc: "Список тендеров с ценами, заказчиками, сроками и прямыми ссылками.",
              },
            ].map((item) => (
              <div key={item.step} className="group relative rounded-2xl border border-zinc-200/60 bg-white p-7 transition-all hover:border-zinc-300 hover:shadow-lg hover:shadow-zinc-200/50">
                <div className={`mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br ${item.color} text-white shadow-sm`}>
                  {item.icon}
                </div>
                <span className="absolute right-6 top-6 text-5xl font-black text-zinc-100/70 transition-colors group-hover:text-zinc-200">
                  {item.step}
                </span>
                <h3 className="mb-2 text-base font-semibold text-zinc-900">{item.title}</h3>
                <p className="text-sm leading-relaxed text-zinc-500">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Преимущества */}
      <section className="py-14 sm:py-24">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <p className="mb-2 text-center text-xs font-semibold uppercase tracking-[0.2em] text-blue-600">
            Преимущества
          </p>
          <h2 className="mb-8 text-center text-xl font-bold text-zinc-900 sm:mb-14 sm:text-3xl">
            Экономьте время, зарабатывайте больше
          </h2>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {[
              {
                icon: <Search className="h-5 w-5 text-blue-600" />,
                bg: "bg-blue-50",
                border: "hover:border-blue-200",
                title: "Любые запросы",
                desc: "Ищите по любым ключевым словам — без ограничений по категориям.",
              },
              {
                icon: <Layers className="h-5 w-5 text-violet-600" />,
                bg: "bg-violet-50",
                border: "hover:border-violet-200",
                title: "Несколько площадок",
                desc: "ЕИС, Портал поставщиков — и список растёт каждую неделю.",
              },
              {
                icon: <Shield className="h-5 w-5 text-emerald-600" />,
                bg: "bg-emerald-50",
                border: "hover:border-emerald-200",
                title: "Только актуальное",
                desc: "Просроченные тендеры автоматически убираются из выдачи.",
              },
              {
                icon: <Clock className="h-5 w-5 text-amber-600" />,
                bg: "bg-amber-50",
                border: "hover:border-amber-200",
                title: "Мгновенный кеш",
                desc: "Повторный поиск по тем же словам — результат за миллисекунды.",
              },
            ].map((item) => (
              <div key={item.title} className={`rounded-2xl border border-zinc-100 p-6 transition-all dark:border-zinc-800 ${item.border} hover:shadow-md`}>
                <div className={`mb-3.5 flex h-10 w-10 items-center justify-center rounded-xl ${item.bg}`}>
                  {item.icon}
                </div>
                <h3 className="mb-1.5 font-semibold text-zinc-900 dark:text-white">{item.title}</h3>
                <p className="text-sm leading-relaxed text-zinc-500 dark:text-zinc-400">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Популярные категории */}
      <section className="border-t border-zinc-100 bg-zinc-50/50 py-14 dark:border-zinc-800 dark:bg-zinc-900/50 sm:py-20">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <p className="mb-2 text-center text-xs font-semibold uppercase tracking-[0.2em] text-blue-600">
            Категории
          </p>
          <h2 className="mb-8 text-center text-xl font-bold text-zinc-900 dark:text-white sm:text-3xl">
            Популярные направления поиска
          </h2>
          <div className="flex flex-wrap justify-center gap-2.5">
            {CATEGORIES.map((cat) => (
              <Link
                key={cat.slug}
                href={`/tenders/${cat.slug}`}
                className="rounded-full border border-zinc-200 bg-white px-4 py-2 text-sm text-zinc-600 transition-all hover:border-zinc-300 hover:shadow-sm hover:text-zinc-900 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-400 dark:hover:border-zinc-600 dark:hover:text-white"
              >
                {cat.title}
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative overflow-hidden bg-zinc-900 py-14 text-center sm:py-24">
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute -left-20 top-0 h-[300px] w-[300px] rounded-full bg-blue-500/10 blur-3xl" />
          <div className="absolute -right-20 bottom-0 h-[300px] w-[300px] rounded-full bg-violet-500/10 blur-3xl" />
        </div>
        <div className="relative mx-auto max-w-lg px-6">
          <h2 className="mb-4 text-2xl font-bold text-white sm:text-3xl">
            Попробуйте прямо сейчас
          </h2>
          <p className="mb-8 text-zinc-400">
            Введите ключевые слова и получите список актуальных тендеров. Бесплатно.
          </p>
          <Link href="/dashboard">
            <Button
              size="lg"
              className="h-12 gap-2 rounded-full bg-white px-8 text-base text-zinc-900 shadow-xl transition-all hover:scale-[1.02] hover:bg-zinc-50"
            >
              Начать поиск <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  );
}
