import type { Metadata } from "next";
import { AuthProvider } from "@/lib/auth-context";
import "./globals.css";

export const metadata: Metadata = {
  title: "ГосПоиск — поиск тендеров по ключевым словам",
  description: "Введите ключевые слова — получите актуальные тендеры и закупки со всех площадок за секунды. Бесплатно, без регистрации.",
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
