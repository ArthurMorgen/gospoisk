import type { Metadata } from "next";
import Link from "next/link";
import { Search, ArrowRight, HelpCircle, Tag } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Footer } from "@/components/footer";
import { CATEGORIES, getCategoryBySlug } from "@/lib/categories";
import { notFound } from "next/navigation";

export function generateStaticParams() {
  return CATEGORIES.map((c) => ({ category: c.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ category: string }> }): Promise<Metadata> {
  const { category } = await params;
  const cat = getCategoryBySlug(category);
  if (!cat) return {};
  return {
    title: `Тендеры на ${cat.title} | Поиск закупок по ключевым словам`,
    description: `Ищите тендеры на ${cat.title} по 44-ФЗ и 223-ФЗ. Введите ключевые слова и получите актуальные закупки за секунды. Бесплатно.`,
    keywords: [
      `тендеры на ${cat.title}`, `закупки ${cat.title}`, `госзакупки ${cat.title}`,
      "поиск тендеров", "44-ФЗ", "223-ФЗ", "ЕИС",
    ],
  };
}

export default async function CategoryPage({ params }: { params: Promise<{ category: string }> }) {
  const { category } = await params;
  const cat = getCategoryBySlug(category);
  if (!cat) notFound();

  return (
    <div className="min-h-screen bg-white">
      <header className="sticky top-0 z-50 border-b border-zinc-100/80 bg-white/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-zinc-800 to-zinc-950 shadow-sm">
              <Search className="h-4 w-4 text-white" />
            </div>
            <span className="text-lg font-bold tracking-tight text-zinc-900">ГосПоиск</span>
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
        {/* Hero */}
        <div className="mb-10 text-center">
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-blue-600">
            Поиск тендеров
          </p>
          <h1 className="mb-4 text-2xl font-bold text-zinc-900 sm:text-4xl">
            Тендеры на {cat.title}
          </h1>
          <p className="mx-auto max-w-lg text-zinc-500">
            Найдите актуальные закупки «{cat.title}» на ЕИС и Портале поставщиков за секунды.
            Введите ключевые слова и получите результаты бесплатно.
          </p>
        </div>

        {/* CTA — поиск */}
        <div className="mb-12 flex justify-center">
          <Link href={`/dashboard?keywords=${encodeURIComponent(cat.keywords.join(","))}`}>
            <Button size="lg" className="gap-2 rounded-xl bg-zinc-900 px-8 shadow-sm shadow-zinc-900/20 transition-all hover:shadow-md">
              <Search className="h-4 w-4" />
              Искать «{cat.keywords[0]}»
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>

        {/* Примеры запросов */}
        <div className="mb-12">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-zinc-900">
            <Tag className="h-4 w-4 text-zinc-400" />
            Примеры запросов
          </h2>
          <div className="flex flex-wrap gap-2">
            {cat.examples.map((ex) => (
              <Link
                key={ex}
                href={`/dashboard?keywords=${encodeURIComponent(ex)}`}
                className="rounded-full border border-zinc-200 bg-zinc-50 px-4 py-2 text-sm text-zinc-600 transition-all hover:border-zinc-300 hover:bg-white hover:text-zinc-900 hover:shadow-sm"
              >
                {ex}
              </Link>
            ))}
          </div>
        </div>

        {/* Инфо блок */}
        <div className="mb-12 grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl border border-zinc-100 bg-zinc-50/50 p-5">
            <p className="mb-1 text-2xl font-bold text-zinc-900">2+</p>
            <p className="text-xs text-zinc-500">Площадки для поиска</p>
          </div>
          <div className="rounded-xl border border-zinc-100 bg-zinc-50/50 p-5">
            <p className="mb-1 text-2xl font-bold text-zinc-900">10</p>
            <p className="text-xs text-zinc-500">Бесплатных поисков в день</p>
          </div>
          <div className="rounded-xl border border-zinc-100 bg-zinc-50/50 p-5">
            <p className="mb-1 text-2xl font-bold text-zinc-900">~15 сек</p>
            <p className="text-xs text-zinc-500">Среднее время поиска</p>
          </div>
        </div>

        {/* Как это работает */}
        <div className="mb-12">
          <h2 className="mb-6 text-lg font-bold text-zinc-900">Как найти тендеры на {cat.title}</h2>
          <div className="space-y-4">
            {[
              { step: "1", text: `Введите ключевое слово «${cat.keywords[0]}» или выберите из примеров выше` },
              { step: "2", text: "Система найдёт актуальные тендеры на ЕИС и Портале поставщиков" },
              { step: "3", text: "Отфильтруйте по цене, региону и площадке — и переходите к участию" },
            ].map((item) => (
              <div key={item.step} className="flex items-start gap-4">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-zinc-900 text-xs font-bold text-white">
                  {item.step}
                </div>
                <p className="pt-1 text-sm text-zinc-600">{item.text}</p>
              </div>
            ))}
          </div>
        </div>

        {/* FAQ */}
        {cat.faq.length > 0 && (
          <div className="mb-12">
            <h2 className="mb-6 flex items-center gap-2 text-lg font-bold text-zinc-900">
              <HelpCircle className="h-4 w-4 text-zinc-400" />
              Частые вопросы
            </h2>
            <div className="grid gap-4 sm:grid-cols-2">
              {cat.faq.map((item) => (
                <div key={item.q} className="rounded-xl border border-zinc-100 bg-white p-5">
                  <h3 className="mb-2 text-sm font-semibold text-zinc-900">{item.q}</h3>
                  <p className="text-xs leading-relaxed text-zinc-500">{item.a}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CTA финальный */}
        <div className="rounded-2xl bg-zinc-900 p-8 text-center sm:p-10">
          <h2 className="mb-3 text-xl font-bold text-white">
            Начните искать тендеры на {cat.title}
          </h2>
          <p className="mb-6 text-sm text-zinc-400">
            10 поисков бесплатно, без регистрации. Результаты за секунды.
          </p>
          <Link href={`/dashboard?keywords=${encodeURIComponent(cat.keywords.join(","))}`}>
            <Button size="lg" className="gap-2 rounded-xl bg-white px-8 text-zinc-900 hover:bg-zinc-100">
              <Search className="h-4 w-4" />
              Начать поиск
            </Button>
          </Link>
        </div>

        {/* Другие категории */}
        <div className="mt-14">
          <h2 className="mb-4 text-center text-sm font-semibold uppercase tracking-wider text-zinc-400">
            Другие категории
          </h2>
          <div className="flex flex-wrap justify-center gap-2">
            {CATEGORIES.filter((c) => c.slug !== cat.slug)
              .slice(0, 8)
              .map((c) => (
                <Link
                  key={c.slug}
                  href={`/tenders/${c.slug}`}
                  className="rounded-full border border-zinc-200 px-3.5 py-1.5 text-xs text-zinc-500 transition-colors hover:border-zinc-300 hover:text-zinc-900"
                >
                  {c.title}
                </Link>
              ))}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
