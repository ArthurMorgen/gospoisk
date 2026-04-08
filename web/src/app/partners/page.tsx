import type { Metadata } from "next";
import Link from "next/link";
import { Search, ArrowLeft, Users, Percent, Gift, Zap, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Footer } from "@/components/footer";

export const metadata: Metadata = {
  title: "Партнёрская программа | Зарабатывайте с ГосПоиск",
  description: "Станьте партнёром ГосПоиск и получайте до 30% от каждого привлечённого клиента. Для тендерных специалистов, бухгалтеров, юристов и консультантов.",
};

const STEPS = [
  {
    icon: <Users className="h-5 w-5" />,
    color: "bg-blue-50 text-blue-600",
    title: "Зарегистрируйтесь как партнёр",
    desc: "Оставьте заявку — мы свяжемся и выдадим персональную реферальную ссылку или промокод.",
  },
  {
    icon: <Gift className="h-5 w-5" />,
    color: "bg-violet-50 text-violet-600",
    title: "Рекомендуйте клиентам",
    desc: "Поделитесь ссылкой с коллегами, клиентами, подписчиками — всеми, кто работает с тендерами.",
  },
  {
    icon: <Percent className="h-5 w-5" />,
    color: "bg-emerald-50 text-emerald-600",
    title: "Получайте вознаграждение",
    desc: "Когда привлечённый клиент оформляет подписку, вы получаете процент от его платежа.",
  },
];

const CONDITIONS = [
  { label: "Тариф Про (990 ₽/мес)", reward: "297 ₽", percent: "30%" },
  { label: "Тариф Бизнес (2 990 ₽/мес)", reward: "897 ₽", percent: "30%" },
];

export default function PartnersPage() {
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
          <Link href="/">
            <Button variant="outline" size="sm" className="gap-1.5 rounded-full">
              <ArrowLeft className="h-3.5 w-3.5" />
              На главную
            </Button>
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-10 sm:px-6 sm:py-16">
        {/* Hero */}
        <div className="mb-12 text-center">
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-blue-600">
            Партнёрская программа
          </p>
          <h1 className="mb-4 text-2xl font-bold text-zinc-900 dark:text-white sm:text-4xl">
            Зарабатывайте, рекомендуя ГосПоиск
          </h1>
          <p className="mx-auto max-w-lg text-zinc-500">
            Получайте до 30% от каждого привлечённого клиента. Подходит для тендерных специалистов,
            бухгалтеров, юристов и всех, кто работает с поставщиками.
          </p>
        </div>

        {/* Как это работает */}
        <div className="mb-14">
          <h2 className="mb-8 text-center text-lg font-bold text-zinc-900 dark:text-white">Как это работает</h2>
          <div className="grid gap-5 sm:grid-cols-3">
            {STEPS.map((step, i) => (
              <div key={i} className="rounded-2xl border border-zinc-100 p-6 transition-all hover:border-zinc-200 hover:shadow-md dark:border-zinc-800 dark:hover:border-zinc-700">
                <div className={`mb-4 flex h-10 w-10 items-center justify-center rounded-xl ${step.color}`}>
                  {step.icon}
                </div>
                <h3 className="mb-2 text-sm font-bold text-zinc-900 dark:text-white">{step.title}</h3>
                <p className="text-xs leading-relaxed text-zinc-500">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Условия */}
        <div className="mb-14">
          <h2 className="mb-6 text-center text-lg font-bold text-zinc-900 dark:text-white">Сколько можно заработать</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {CONDITIONS.map((c) => (
              <div key={c.label} className="rounded-2xl border border-zinc-100 bg-zinc-50/50 p-6 dark:border-zinc-800 dark:bg-zinc-900/50">
                <p className="mb-1 text-sm text-zinc-500">{c.label}</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-extrabold text-zinc-900 dark:text-white">{c.reward}</span>
                  <span className="text-sm text-zinc-400">с каждого платежа</span>
                </div>
                <p className="mt-2 text-xs text-emerald-600 font-medium">{c.percent} от суммы</p>
              </div>
            ))}
          </div>
          <div className="mt-6 rounded-xl bg-amber-50 p-4 text-center dark:bg-amber-950/30">
            <p className="text-xs text-amber-800 dark:text-amber-300">
              <strong>Пример:</strong> Вы привлекли 10 клиентов на тариф Про → <strong>2 970 ₽/мес</strong> пассивного дохода.
              За год — <strong>35 640 ₽</strong>.
            </p>
          </div>
        </div>

        {/* Кто может стать партнёром */}
        <div className="mb-14">
          <h2 className="mb-6 text-center text-lg font-bold text-zinc-900 dark:text-white">Кто может стать партнёром</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {[
              "Тендерные специалисты и консультанты",
              "Бухгалтеры и юристы, работающие с поставщиками",
              "Бизнес-тренеры и авторы курсов по госзакупкам",
              "Telegram-каналы и блогеры в нише B2B/закупок",
              "Торгово-промышленные палаты и бизнес-объединения",
              "Все, кто знает людей, участвующих в тендерах",
            ].map((item) => (
              <div key={item} className="flex items-start gap-3 rounded-xl border border-zinc-100 p-4 dark:border-zinc-800">
                <Zap className="mt-0.5 h-4 w-4 shrink-0 text-blue-500" />
                <p className="text-sm text-zinc-600 dark:text-zinc-400">{item}</p>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="rounded-2xl bg-zinc-900 p-8 text-center sm:p-10">
          <h2 className="mb-3 text-xl font-bold text-white">
            Хотите стать партнёром?
          </h2>
          <p className="mb-6 text-sm text-zinc-400">
            Напишите нам — мы расскажем подробности и выдадим реферальную ссылку.
          </p>
          <a href="mailto:support@gospoisk.ru?subject=Партнёрская программа">
            <Button size="lg" className="gap-2 rounded-xl bg-white px-8 text-zinc-900 hover:bg-zinc-100">
              <Mail className="h-4 w-4" />
              Написать на support@gospoisk.ru
            </Button>
          </a>
        </div>
      </main>

      <Footer />
    </div>
  );
}
