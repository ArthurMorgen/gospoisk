const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://apigospoisk.ru";

export interface Tender {
  tender_id: string;
  platform: string;
  title: string;
  price: number;
  customer: string;
  deadline: string;
  status: string;
  url: string;
  tender_type: string;
  parsed_at: string;
}

export type SortOption = "relevance" | "price_asc" | "price_desc" | "deadline";

export interface TendersResponse {
  tenders: Tender[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  keywords: string[];
  search_time_ms: number;
  cached: boolean;
}

export interface PredictionResult {
  drop_pct: number;
  category: string;
  confidence: 'high' | 'medium' | 'low';
}

export async function predictBatch(tenders: { title: string; price: number }[]): Promise<(PredictionResult | null)[]> {
  try {
    const res = await fetch(`${API_BASE}/api/predict/batch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(tenders),
    });
    if (!res.ok) return tenders.map(() => null);
    const data = await res.json();
    return data.predictions;
  } catch {
    return tenders.map(() => null);
  }
}

export async function fetchRegions(): Promise<string[]> {
  try {
    const res = await fetch(`${API_BASE}/api/regions`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.regions || [];
  } catch {
    return [];
  }
}

export async function searchTenders(params: {
  keywords: string[];
  platforms?: string[];
  page?: number;
  per_page?: number;
  filter?: string;
  sort?: SortOption;
  min_price?: number;
  max_price?: number;
  region?: string;
  signal?: AbortSignal;
}): Promise<TendersResponse> {
  const searchParams = new URLSearchParams();
  if (params.page) searchParams.set("page", String(params.page));
  if (params.per_page) searchParams.set("per_page", String(params.per_page));
  if (params.filter) searchParams.set("filter", params.filter);

  const body: Record<string, unknown> = { keywords: params.keywords };
  if (params.platforms && params.platforms.length > 0) body.platforms = params.platforms;
  if (params.sort && params.sort !== "relevance") body.sort = params.sort;
  if (params.min_price) body.min_price = params.min_price;
  if (params.max_price) body.max_price = params.max_price;
  if (params.region) body.region = params.region;

  const controller = params.signal ? undefined : new AbortController();
  const signal = params.signal || controller?.signal;
  const timeout = setTimeout(() => controller?.abort(), 120_000);

  try {
    const res = await fetch(`${API_BASE}/api/search?${searchParams.toString()}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Ошибка сервера" }));
      throw new Error(err.detail || "Ошибка поиска");
    }
    return res.json();
  } catch (e: unknown) {
    if (e instanceof DOMException && e.name === "AbortError") {
      throw new Error("Поиск отменён");
    }
    if (e instanceof TypeError && (e.message.includes("fetch") || e.message.includes("network") || e.message.includes("Failed"))) {
      throw new Error("Нет связи с сервером. Проверьте интернет и попробуйте снова.");
    }
    throw e;
  } finally {
    clearTimeout(timeout);
  }
}
