"""
ГосПоиск API — поиск тендеров по ключевым словам
"""

import sys
import os
import logging
import hashlib
import time
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Добавляем корневую папку проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from concurrent.futures import ThreadPoolExecutor

from config import PLATFORMS
from parsers.suppliers_portal_selenium_parser import SuppliersPortalSeleniumParser
from parsers.eis_parser import EISParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Инициализация парсеров ===
portal_parser = SuppliersPortalSeleniumParser(PLATFORMS['suppliers_portal_new'])
eis_parser = EISParser(PLATFORMS['eis'])

PARSERS = {
    "portal": {"parser": portal_parser, "name": "Портал поставщиков"},
    "eis": {"parser": eis_parser, "name": "ЕИС"},
}

# === FastAPI app ===
app = FastAPI(
    title="ГосПоиск API",
    description="Поиск тендеров по ключевым словам",
    version="1.0.0"
)

# CORS обрабатывается nginx
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# === Модели ===
class Tender(BaseModel):
    tender_id: str
    platform: str = ""
    title: str = ""
    price: float = 0.0
    customer: str = ""
    deadline: str = ""
    status: str = ""
    url: str = ""
    tender_type: str = ""
    parsed_at: str = ""


def normalize_tender(t: dict) -> dict:
    """Ensure all string fields are strings, not None"""
    return {
        'tender_id': str(t.get('tender_id') or ''),
        'platform': str(t.get('platform') or ''),
        'title': str(t.get('title') or ''),
        'price': float(t.get('price') or 0),
        'customer': str(t.get('customer') or ''),
        'deadline': str(t.get('deadline') or ''),
        'status': str(t.get('status') or ''),
        'url': str(t.get('url') or ''),
        'tender_type': str(t.get('tender_type') or ''),
        'parsed_at': str(t.get('parsed_at') or ''),
    }


class TendersResponse(BaseModel):
    tenders: List[Tender]
    total: int
    page: int
    per_page: int
    total_pages: int
    keywords: List[str]
    search_time_ms: int = 0
    cached: bool = False


class SearchRequest(BaseModel):
    keywords: List[str]
    platforms: Optional[List[str]] = None
    sort: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None


# === Кеш по ключевым словам ===
# Ключ = хеш от отсортированных keywords, значение = {tenders, updated_at}
tender_cache: dict = {}
CACHE_TTL_SECONDS = 300  # 5 минут


def cache_key(keywords: List[str], platforms: List[str] = None) -> str:
    normalized = sorted([k.strip().lower() for k in keywords if k.strip()])
    plat = sorted(platforms) if platforms else ["all"]
    raw = "|".join(normalized) + "::" + ",".join(plat)
    return hashlib.md5(raw.encode()).hexdigest()


def is_cache_valid(key: str) -> bool:
    entry = tender_cache.get(key)
    if not entry or not entry.get("updated_at"):
        return False
    elapsed = (datetime.now() - entry["updated_at"]).total_seconds()
    return elapsed < CACHE_TTL_SECONDS


def _search_portal(keywords: List[str]) -> List[dict]:
    """Поиск по Порталу поставщиков (API)"""
    results = []
    seen = set()
    for kw in keywords:
        try:
            tenders = portal_parser._search_api(kw)
            for t in tenders:
                if t['tender_id'] not in seen:
                    seen.add(t['tender_id'])
                    results.append(t)
        except Exception as e:
            logger.warning(f"Portal ошибка для '{kw}': {e}")
    return results


def _search_eis(keywords: List[str]) -> List[dict]:
    """Поиск по ЕИС (HTML scraping)"""
    results = []
    seen = set()
    try:
        raw = eis_parser.search_tenders(keywords=keywords)
        for t in raw:
            tid = t.get('tender_id', '')
            if tid and tid not in seen:
                seen.add(tid)
                results.append({
                    'tender_id': tid,
                    'platform': t.get('platform', 'ЕИС'),
                    'title': t.get('title', ''),
                    'price': float(t.get('price', 0) or 0),
                    'customer': t.get('customer', ''),
                    'deadline': t.get('deadline', ''),
                    'status': t.get('status', ''),
                    'url': t.get('url', ''),
                    'tender_type': '',
                    'parsed_at': '',
                })
    except Exception as e:
        logger.warning(f"EIS ошибка: {e}")
    return results


def do_search(keywords: List[str], platforms: List[str] = None) -> List[dict]:
    """Поиск по всем площадкам параллельно"""
    clean = [k.strip() for k in keywords if k.strip()]
    if not clean:
        return []

    use_portal = not platforms or "portal" in platforms
    use_eis = not platforms or "eis" in platforms

    all_tenders = []

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = []
        if use_portal:
            futures.append(pool.submit(_search_portal, clean))
        if use_eis:
            futures.append(pool.submit(_search_eis, clean))

        for f in futures:
            try:
                all_tenders.extend(f.result(timeout=60))
            except Exception as e:
                logger.error(f"Ошибка парсера: {e}")

    # Дедупликация по tender_id
    seen = set()
    unique = []
    for t in all_tenders:
        if t['tender_id'] not in seen:
            seen.add(t['tender_id'])
            unique.append(t)

    logger.info(f"Всего: {len(unique)} уникальных тендеров с {len(futures)} площадок")
    return unique


# === Эндпоинты ===

@app.get("/")
async def root():
    return {"status": "ok", "service": "ГосПоиск API", "version": "1.0.0"}


@app.post("/api/search", response_model=TendersResponse)
async def search_tenders(
    body: SearchRequest,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    filter: Optional[str] = Query(None, description="Дополнительный фильтр по названию"),
):
    """Поиск тендеров по ключевым словам пользователя"""
    t_start = time.time()

    keywords = [k.strip() for k in body.keywords if k.strip()]
    if not keywords:
        raise HTTPException(status_code=400, detail="Введите хотя бы одно ключевое слово")
    if len(keywords) > 20:
        raise HTTPException(status_code=400, detail="Максимум 20 ключевых слов")

    key = cache_key(keywords, body.platforms)
    was_cached = is_cache_valid(key)

    if not was_cached:
        logger.info(f"Парсю по: {keywords}")
        try:
            tenders = do_search(keywords, body.platforms)
            tender_cache[key] = {
                "tenders": tenders,
                "keywords": keywords,
                "updated_at": datetime.now(),
            }
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            if key not in tender_cache:
                raise HTTPException(status_code=503, detail="Парсер временно недоступен")

    all_tenders = list(tender_cache[key]["tenders"])

    # Доп. фильтр по названию
    if filter:
        fl = filter.lower()
        all_tenders = [t for t in all_tenders if fl in t.get('title', '').lower()]

    # Фильтр по цене
    if body.min_price is not None:
        all_tenders = [t for t in all_tenders if t.get('price', 0) >= body.min_price]
    if body.max_price is not None:
        all_tenders = [t for t in all_tenders if 0 < t.get('price', 0) <= body.max_price]

    # Сортировка
    if body.sort == "price_asc":
        with_price = [t for t in all_tenders if t.get('price', 0) and t['price'] > 0]
        no_price = [t for t in all_tenders if not t.get('price', 0) or t['price'] <= 0]
        with_price.sort(key=lambda t: t['price'])
        all_tenders = with_price + no_price
    elif body.sort == "price_desc":
        with_price = [t for t in all_tenders if t.get('price', 0) and t['price'] > 0]
        no_price = [t for t in all_tenders if not t.get('price', 0) or t['price'] <= 0]
        with_price.sort(key=lambda t: t['price'], reverse=True)
        all_tenders = with_price + no_price
    elif body.sort == "deadline":
        with_deadline = [t for t in all_tenders if (t.get('deadline') or '').strip()]
        no_deadline = [t for t in all_tenders if not (t.get('deadline') or '').strip()]
        with_deadline.sort(key=lambda t: t['deadline'])
        all_tenders = with_deadline + no_deadline

    # Пагинация
    total = len(all_tenders)
    total_pages = max(1, (total + per_page - 1) // per_page)
    start = (page - 1) * per_page
    end = start + per_page

    elapsed = int((time.time() - t_start) * 1000)

    return TendersResponse(
        tenders=[Tender(**normalize_tender(t)) for t in all_tenders[start:end]],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        keywords=keywords,
        search_time_ms=elapsed,
        cached=was_cached,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
