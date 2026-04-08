import type { Metadata } from "next";
import Link from "next/link";
import { Search, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Footer } from "@/components/footer";

export const metadata: Metadata = {
  title: "Политика конфиденциальности",
  description: "Политика конфиденциальности сервиса ГосПоиск. Узнайте, как мы собираем, используем и защищаем ваши персональные данные.",
};

export default function PrivacyPage() {
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
        <h1 className="mb-2 text-2xl font-bold text-zinc-900 dark:text-white sm:text-3xl">Политика конфиденциальности</h1>
        <p className="mb-8 text-sm text-zinc-400">Последнее обновление: 6 апреля 2026 г.</p>

        <div className="prose-sm space-y-6 text-zinc-600 dark:text-zinc-400 [&_h2]:mb-3 [&_h2]:mt-8 [&_h2]:text-base [&_h2]:font-bold [&_h2]:text-zinc-900 dark:[&_h2]:text-white [&_li]:ml-4 [&_li]:list-disc [&_p]:leading-relaxed">
          <h2>1. Общие положения</h2>
          <p>
            Настоящая Политика конфиденциальности (далее — «Политика») определяет порядок обработки и защиты
            персональных данных пользователей сервиса «ГосПоиск» (далее — «Сервис»), расположенного по адресу
            https://apigospoisk.ru.
          </p>
          <p>
            Используя Сервис, вы соглашаетесь с условиями данной Политики. Если вы не согласны с условиями, пожалуйста,
            прекратите использование Сервиса.
          </p>

          <h2>2. Какие данные мы собираем</h2>
          <p>Мы можем собирать следующие категории данных:</p>
          <ul>
            <li>Адрес электронной почты (при регистрации)</li>
            <li>Поисковые запросы и ключевые слова</li>
            <li>IP-адрес и данные об устройстве (User-Agent)</li>
            <li>Данные об использовании Сервиса (количество поисков, посещённые страницы)</li>
          </ul>

          <h2>3. Цели обработки данных</h2>
          <p>Собранные данные используются для:</p>
          <ul>
            <li>Предоставления доступа к функциям Сервиса</li>
            <li>Идентификации пользователя и управления аккаунтом</li>
            <li>Улучшения качества Сервиса и пользовательского опыта</li>
            <li>Отправки уведомлений о новых тендерах (только с согласия пользователя)</li>
            <li>Обеспечения безопасности и предотвращения злоупотреблений</li>
          </ul>

          <h2>4. Хранение и защита данных</h2>
          <p>
            Персональные данные хранятся на защищённых серверах с использованием шифрования.
            Мы применяем организационные и технические меры для защиты данных от несанкционированного доступа,
            изменения, раскрытия или уничтожения.
          </p>
          <p>
            Аутентификация пользователей осуществляется через сервис Supabase с использованием стандартов безопасности
            (шифрование паролей, защищённые токены).
          </p>

          <h2>5. Передача данных третьим лицам</h2>
          <p>
            Мы не продаём и не передаём ваши персональные данные третьим лицам, за исключением случаев:
          </p>
          <ul>
            <li>Использования технических подрядчиков для работы Сервиса (хостинг, аутентификация)</li>
            <li>Требований законодательства Российской Федерации</li>
          </ul>

          <h2>6. Файлы cookie</h2>
          <p>
            Сервис использует localStorage для хранения данных сессии и счётчика поисков.
            Мы не используем сторонние трекеры и рекламные cookie.
          </p>

          <h2>7. Права пользователя</h2>
          <p>Вы имеете право:</p>
          <ul>
            <li>Получить информацию о хранимых данных</li>
            <li>Запросить исправление или удаление ваших данных</li>
            <li>Отозвать согласие на обработку данных</li>
            <li>Удалить аккаунт и все связанные данные</li>
          </ul>
          <p>
            Для реализации этих прав напишите на{" "}
            <a href="mailto:support@gospoisk.ru" className="text-blue-600 hover:underline">
              support@gospoisk.ru
            </a>.
          </p>

          <h2>8. Изменения Политики</h2>
          <p>
            Мы оставляем за собой право обновлять данную Политику. Актуальная версия всегда доступна на этой странице.
            Продолжая использование Сервиса после изменений, вы принимаете обновлённую Политику.
          </p>

          <h2>9. Контакты</h2>
          <p>
            По вопросам обработки персональных данных обращайтесь:{" "}
            <a href="mailto:support@gospoisk.ru" className="text-blue-600 hover:underline">
              support@gospoisk.ru
            </a>
          </p>
        </div>
      </main>

      <Footer />
    </div>
  );
}
