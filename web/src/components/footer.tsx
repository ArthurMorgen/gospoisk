import Link from "next/link";
import { Search } from "lucide-react";

const SITE_NAME = "ГосПоиск";

export function Footer() {
  return (
    <footer className="border-t border-zinc-100 bg-white dark:border-zinc-800 dark:bg-zinc-950">
      <div className="mx-auto max-w-5xl px-4 py-8 sm:py-10">
        <div className="grid grid-cols-2 gap-6 sm:grid-cols-4 sm:gap-8">
          <div className="col-span-2 sm:col-span-1">
            <Link href="/" className="flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-zinc-800 to-zinc-950 shadow-sm">
                <Search className="h-3.5 w-3.5 text-white" />
              </div>
              <span className="text-sm font-bold text-zinc-900 dark:text-white">{SITE_NAME}</span>
            </Link>
            <p className="mt-2.5 text-xs leading-relaxed text-zinc-400">
              Поиск тендеров по ключевым словам на государственных площадках РФ
            </p>
          </div>

          <div>
            <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-zinc-400">
              Сервис
            </h4>
            <ul className="space-y-2">
              <li>
                <Link href="/dashboard" className="text-sm text-zinc-500 transition-colors hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white">
                  Поиск тендеров
                </Link>
              </li>
              <li>
                <Link href="/pricing" className="text-sm text-zinc-500 transition-colors hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white">
                  Тарифы
                </Link>
              </li>
              <li>
                <Link href="/saved" className="text-sm text-zinc-500 transition-colors hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white">
                  Сохранённые поиски
                </Link>
              </li>
              <li>
                <Link href="/blog" className="text-sm text-zinc-500 transition-colors hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white">
                  Блог
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-zinc-400">
              Площадки
            </h4>
            <ul className="space-y-2">
              <li>
                <a href="https://zakupki.gov.ru" target="_blank" rel="noopener noreferrer" className="text-sm text-zinc-500 transition-colors hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white">
                  ЕИС (zakupki.gov.ru)
                </a>
              </li>
              <li>
                <a href="https://zakupki.mos.ru" target="_blank" rel="noopener noreferrer" className="text-sm text-zinc-500 transition-colors hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white">
                  Портал поставщиков
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-zinc-400">
              Поддержка
            </h4>
            <ul className="space-y-2">
              <li>
                <Link href="/feedback" className="text-sm text-zinc-500 transition-colors hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white">
                  Обратная связь
                </Link>
              </li>
              <li>
                <Link href="/contacts" className="text-sm text-zinc-500 transition-colors hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white">
                  Контакты
                </Link>
              </li>
              <li>
                <a href="mailto:support@gospoisk.ru" className="text-sm text-zinc-500 transition-colors hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white">
                  support@gospoisk.ru
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 flex flex-col items-center justify-between gap-3 border-t border-zinc-100 pt-6 dark:border-zinc-800 sm:flex-row">
          <p className="text-xs text-zinc-300">
            © {new Date().getFullYear()} {SITE_NAME}. Все права защищены.
          </p>
          <div className="flex items-center gap-4">
            <Link href="/privacy" className="text-xs text-zinc-300 transition-colors hover:text-zinc-500">
              Политика конфиденциальности
            </Link>
            <Link href="/terms" className="text-xs text-zinc-300 transition-colors hover:text-zinc-500">
              Пользовательское соглашение
            </Link>
          </div>
          <p className="text-xs text-zinc-300">
            Не является государственным ресурсом
          </p>
        </div>
      </div>
    </footer>
  );
}
