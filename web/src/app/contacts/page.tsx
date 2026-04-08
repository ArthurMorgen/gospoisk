import type { Metadata } from "next";
import Link from "next/link";
import { Search, ArrowLeft, Mail, MapPin, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Footer } from "@/components/footer";

export const metadata: Metadata = {
  title: "Контакты",
  description: "Свяжитесь с командой ГосПоиск. Email, адрес и время работы поддержки.",
};

export default function ContactsPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-zinc-950">
      <header className="sticky top-0 z-50 border-b border-zinc-100/80 bg-white/70 backdrop-blur-xl dark:border-zinc-800/80 dark:bg-zinc-950/70">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-6 py-3">
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

      <main className="mx-auto max-w-3xl px-4 py-10 sm:px-6 sm:py-16">
        <h1 className="mb-2 text-2xl font-bold text-zinc-900 dark:text-white sm:text-3xl">Контакты</h1>
        <p className="mb-10 text-sm text-zinc-500">Свяжитесь с нами любым удобным способом</p>

        <div className="grid gap-5 sm:grid-cols-3">
          <div className="rounded-2xl border border-zinc-100 bg-zinc-50/50 p-6 dark:border-zinc-800 dark:bg-zinc-900/50">
            <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-950/40">
              <Mail className="h-5 w-5 text-blue-600" />
            </div>
            <h3 className="mb-1 text-sm font-bold text-zinc-900 dark:text-white">Email</h3>
            <a href="mailto:support@gospoisk.ru" className="text-sm text-blue-600 hover:underline">
              support@gospoisk.ru
            </a>
            <p className="mt-2 text-xs text-zinc-400">
              Ответим в течение 24 часов
            </p>
          </div>

          <div className="rounded-2xl border border-zinc-100 bg-zinc-50/50 p-6 dark:border-zinc-800 dark:bg-zinc-900/50">
            <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 dark:bg-emerald-950/40">
              <Clock className="h-5 w-5 text-emerald-600" />
            </div>
            <h3 className="mb-1 text-sm font-bold text-zinc-900 dark:text-white">Режим работы</h3>
            <p className="text-sm text-zinc-600 dark:text-zinc-400">Пн — Пт: 9:00 — 18:00</p>
            <p className="mt-2 text-xs text-zinc-400">
              Московское время (UTC+3)
            </p>
          </div>

          <div className="rounded-2xl border border-zinc-100 bg-zinc-50/50 p-6 dark:border-zinc-800 dark:bg-zinc-900/50">
            <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-violet-50 dark:bg-violet-950/40">
              <MapPin className="h-5 w-5 text-violet-600" />
            </div>
            <h3 className="mb-1 text-sm font-bold text-zinc-900 dark:text-white">Адрес</h3>
            <p className="text-sm text-zinc-600 dark:text-zinc-400">Российская Федерация</p>
            <p className="mt-2 text-xs text-zinc-400">
              Онлайн-сервис
            </p>
          </div>
        </div>

        <div className="mt-12 rounded-2xl border border-zinc-100 bg-zinc-50/50 p-6 dark:border-zinc-800 dark:bg-zinc-900/50 sm:p-8">
          <h2 className="mb-4 text-lg font-bold text-zinc-900 dark:text-white">Часто задаваемые вопросы</h2>
          <div className="space-y-4">
            <div>
              <h3 className="mb-1 text-sm font-semibold text-zinc-800 dark:text-zinc-200">Как связаться с технической поддержкой?</h3>
              <p className="text-sm text-zinc-500">
                Напишите на support@gospoisk.ru или используйте форму{" "}
                <Link href="/feedback" className="text-blue-600 hover:underline">обратной связи</Link>.
              </p>
            </div>
            <div>
              <h3 className="mb-1 text-sm font-semibold text-zinc-800 dark:text-zinc-200">Как удалить аккаунт и данные?</h3>
              <p className="text-sm text-zinc-500">
                Отправьте запрос на support@gospoisk.ru с темой «Удаление аккаунта» и укажите email, на который зарегистрирован аккаунт.
              </p>
            </div>
            <div>
              <h3 className="mb-1 text-sm font-semibold text-zinc-800 dark:text-zinc-200">Как оформить возврат средств?</h3>
              <p className="text-sm text-zinc-500">
                Напишите на support@gospoisk.ru в течение 14 дней с момента оплаты.
                Подробности — в{" "}
                <Link href="/terms" className="text-blue-600 hover:underline">пользовательском соглашении</Link>.
              </p>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
