import type { Metadata } from "next";
import { AuthProvider } from "@/lib/auth-context";
import { ThemeProvider } from "@/lib/theme-context";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Поиск тендеров по ключевым словам | Бесплатно и без регистрации | ГосПоиск",
    template: "%s | ГосПоиск",
  },
  description: "Мгновенный поиск тендеров по любым ключевым словам на ЕИС, Портале поставщиков и других площадках. 10 поисков бесплатно. Без регистрации. Попробуйте прямо сейчас.",
  keywords: [
    "поиск тендеров", "тендеры по ключевым словам", "агрегатор тендеров",
    "найти тендер", "госзакупки", "поиск по 44-ФЗ", "223-ФЗ",
    "ЕИС", "портал поставщиков", "закупки", "тендеры бесплатно",
    "поиск закупок", "государственные закупки",
  ],
  openGraph: {
    title: "ГосПоиск — мгновенный поиск тендеров по ключевым словам",
    description: "Все тендеры по вашему запросу за секунды. ЕИС, Портал поставщиков и другие площадки. Бесплатно.",
    type: "website",
    locale: "ru_RU",
    siteName: "ГосПоиск",
    url: "https://apigospoisk.ru",
  },
  twitter: {
    card: "summary",
    title: "ГосПоиск — поиск тендеров по ключевым словам",
    description: "Мгновенный поиск тендеров на ЕИС и Портале поставщиков. Бесплатно.",
  },
  robots: {
    index: true,
    follow: true,
  },
  metadataBase: new URL("https://apigospoisk.ru"),
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <body className="antialiased bg-white text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100 transition-colors">
        <ThemeProvider>
          <AuthProvider>{children}</AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
