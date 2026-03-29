import type { Metadata } from "next";
import { AuthProvider } from "@/lib/auth-context";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "ГосПоиск — поиск тендеров по ключевым словам",
    template: "%s | ГосПоиск",
  },
  description: "Введите ключевые слова — получите актуальные тендеры и закупки со всех площадок. Бесплатно, без регистрации.",
  keywords: ["тендеры", "закупки", "поиск тендеров", "госзакупки", "ЕИС", "портал поставщиков", "44-ФЗ", "223-ФЗ"],
  openGraph: {
    title: "ГосПоиск — поиск тендеров по ключевым словам",
    description: "Все тендеры по вашему запросу за секунды. ЕИС, Портал поставщиков и другие площадки.",
    type: "website",
    locale: "ru_RU",
    siteName: "ГосПоиск",
  },
  twitter: {
    card: "summary",
    title: "ГосПоиск — поиск тендеров",
    description: "Все тендеры по вашему запросу за секунды.",
  },
  metadataBase: new URL("https://gospoisk.vercel.app"),
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body className="antialiased">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
