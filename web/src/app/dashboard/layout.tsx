import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Поиск тендеров — ГосПоиск",
  description: "Введите ключевые слова и найдите актуальные тендеры и закупки со всех государственных площадок.",
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
