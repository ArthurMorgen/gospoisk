import Link from "next/link";
import { Search, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-white px-6">
      <div className="relative">
        <div className="absolute -inset-4 rounded-full bg-zinc-100/50 blur-xl" />
        <div className="relative flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-zinc-100 to-zinc-200 shadow-sm">
          <Search className="h-7 w-7 text-zinc-300" />
        </div>
      </div>
      <p className="mt-6 text-6xl font-extrabold tracking-tight text-zinc-200">404</p>
      <h1 className="mt-2 text-xl font-bold text-zinc-900">Страница не найдена</h1>
      <p className="mt-2 text-sm text-zinc-400">Такой страницы нет, но тендеры точно есть</p>
      <Link href="/dashboard" className="mt-8">
        <Button variant="outline" className="gap-2 rounded-full shadow-sm transition-all hover:shadow-md">
          <ArrowLeft className="h-4 w-4" />
          К поиску тендеров
        </Button>
      </Link>
    </div>
  );
}
