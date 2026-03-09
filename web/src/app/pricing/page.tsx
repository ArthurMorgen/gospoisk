import Link from "next/link";
import { Search, Check, ArrowLeft, Sparkles, Crown, Building } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Footer } from "@/components/footer";

const SITE_NAME = "ГосПоиск";

const plans = [
  {
    name: "Бесплатно",
    price: "0",
    currency: "₽",
    period: "",
    description: "Попробовать сервис",
    icon: <Search className="h-4 w-4" />,
    iconBg: "bg-zinc-100 text-zinc-500",
    features: [
      "3 поиска в день",
      "Все площадки",
      "Базовая сортировка",
      "Фильтр по цене",
    ],
    cta: "Текущий план",
    disabled: true,
    highlight: false,
  },
  {
    name: "Про",
    price: "990",
    currency: "₽",
    period: "/мес",
    description: "Для активных поставщиков",
    icon: <Sparkles className="h-4 w-4" />,
    iconBg: "bg-gradient-to-br from-blue-500 to-violet-600 text-white",
    features: [
      "Безлимитные поиски",
      "Все площадки (Портал + ЕИС + ...)",
      "5 сохранённых поисков",
      "Telegram-уведомления о новых тендерах",
      "Расширенные фильтры",
      "Приоритетный парсинг",
    ],
    cta: "Скоро",
    disabled: true,
    highlight: true,
  },
  {
    name: "Бизнес",
    price: "2 990",
    currency: "₽",
    period: "/мес",
    description: "Для команд и компаний",
    icon: <Building className="h-4 w-4" />,
    iconBg: "bg-zinc-900 text-white",
    features: [
      "Всё из тарифа Про",
      "20 сохранённых поисков",
      "Экспорт в Excel / CSV",
      "Приоритетная поддержка",
      "API доступ",
      "Мульти-аккаунт (до 5 чел.)",
    ],
    cta: "Скоро",
    disabled: true,
    highlight: false,
  },
];

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-white">
      <header className="sticky top-0 z-50 border-b border-zinc-100/80 bg-white/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-zinc-800 to-zinc-950 shadow-sm">
              <Search className="h-4 w-4 text-white" />
            </div>
            <span className="text-lg font-bold tracking-tight text-zinc-900">{SITE_NAME}</span>
          </Link>
          <Link href="/dashboard">
            <Button variant="outline" size="sm" className="gap-1.5 rounded-full">
              <ArrowLeft className="h-3.5 w-3.5" />
              К поиску
            </Button>
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-12 sm:px-6 sm:py-20">
        <div className="mb-8 text-center sm:mb-14">
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-blue-600">
            Тарифы
          </p>
          <h1 className="mb-3 text-2xl font-bold text-zinc-900 sm:mb-4 sm:text-4xl">
            Простые и прозрачные цены
          </h1>
          <p className="mx-auto max-w-md text-zinc-500">
            Начните бесплатно. Обновитесь, когда вашему бизнесу потребуется больше.
          </p>
        </div>

        <div className="grid items-start gap-5 sm:grid-cols-3">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`relative rounded-2xl border p-7 transition-all ${
                plan.highlight
                  ? "border-zinc-900/20 bg-white shadow-xl shadow-zinc-200/50 sm:scale-105"
                  : "border-zinc-200/80 bg-white hover:border-zinc-300 hover:shadow-md"
              }`}
            >
              {plan.highlight && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="inline-flex items-center gap-1 rounded-full bg-gradient-to-r from-blue-600 to-violet-600 px-3 py-1 text-xs font-medium text-white shadow-sm">
                    <Crown className="h-3 w-3" /> Популярный
                  </span>
                </div>
              )}
              <div className={`mb-4 flex h-9 w-9 items-center justify-center rounded-xl ${plan.iconBg}`}>
                {plan.icon}
              </div>
              <h3 className="mb-0.5 text-lg font-bold text-zinc-900">{plan.name}</h3>
              <p className="mb-5 text-xs text-zinc-400">{plan.description}</p>
              <div className="mb-6 flex items-baseline gap-0.5">
                <span className="text-4xl font-extrabold tracking-tight text-zinc-900">{plan.price}</span>
                <span className="text-lg font-semibold text-zinc-400">{plan.currency}</span>
                {plan.period && <span className="ml-0.5 text-sm text-zinc-400">{plan.period}</span>}
              </div>
              <div className="mb-6 h-px bg-zinc-100" />
              <ul className="mb-7 space-y-2.5">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2.5 text-sm text-zinc-600">
                    <div className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-emerald-50">
                      <Check className="h-2.5 w-2.5 text-emerald-600" />
                    </div>
                    {f}
                  </li>
                ))}
              </ul>
              <Button
                className={`w-full rounded-xl ${
                  plan.highlight
                    ? "bg-zinc-900 shadow-sm shadow-zinc-900/20 hover:shadow-md"
                    : ""
                }`}
                variant={plan.highlight ? "default" : "outline"}
                disabled={plan.disabled}
              >
                {plan.cta}
              </Button>
            </div>
          ))}
        </div>

        <div className="mt-14 rounded-2xl border border-zinc-100 bg-zinc-50/50 px-6 py-5 text-center">
          <p className="text-sm text-zinc-500">
            Платные тарифы появятся в ближайшее время.
            <span className="font-medium text-zinc-700"> Сейчас все площадки доступны бесплатно</span> с лимитом 3 поиска в день.
          </p>
        </div>
      </main>

      <Footer />
    </div>
  );
}
