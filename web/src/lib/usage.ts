const STORAGE_KEY = "gospoisk_usage";
const FREE_LIMIT = 10;
const AUTH_LIMIT = 50;

// Админские email — безлимитный доступ
const ADMIN_EMAILS = ["moshentsov2006@gmail.com"];

interface UsageData {
  date: string;
  count: number;
}

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

function getUsage(): UsageData {
  if (typeof window === "undefined") return { date: today(), count: 0 };
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { date: today(), count: 0 };
    const data: UsageData = JSON.parse(raw);
    if (data.date !== today()) return { date: today(), count: 0 };
    return data;
  } catch {
    return { date: today(), count: 0 };
  }
}

function setUsage(data: UsageData) {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

export function isAdmin(email?: string | null): boolean {
  return !!email && ADMIN_EMAILS.includes(email.toLowerCase());
}

export function getLimit(email?: string | null): number {
  if (isAdmin(email)) return 999;
  if (email) return AUTH_LIMIT;
  return FREE_LIMIT;
}

export function getSearchesLeft(email?: string | null): number {
  const limit = getLimit(email);
  if (limit >= 999) return 999;
  const usage = getUsage();
  return Math.max(0, limit - usage.count);
}

export function getSearchesUsed(): number {
  return getUsage().count;
}

export function canSearch(email?: string | null): boolean {
  return getSearchesLeft(email) > 0;
}

export function recordSearch(): void {
  const usage = getUsage();
  if (usage.date !== today()) {
    setUsage({ date: today(), count: 1 });
  } else {
    setUsage({ date: today(), count: usage.count + 1 });
  }
}

export function resetSearches(): void {
  setUsage({ date: today(), count: 0 });
}

export function isPro(email?: string | null): boolean {
  // Пока: только админ = про. Позже: проверка подписки через Supabase
  return isAdmin(email);
}

export const FREE_SEARCH_LIMIT = FREE_LIMIT;
