# ГосПоиск

Агрегатор тендеров с государственных площадок РФ. Единый поиск по ключевым словам — ЕИС, Портал поставщиков и другие площадки в одном окне.

## Стек

- **Frontend** — Next.js 16, React, TailwindCSS, shadcn/ui
- **Backend** — FastAPI, Python 3.11
- **Auth / DB** — Supabase
- **Хостинг** — Vercel (фронт), Render (API)

## Структура

```
├── api/              # FastAPI-сервер
│   └── main.py
├── parsers/          # Парсеры площадок
│   ├── base_parser.py
│   ├── eis_parser.py
│   └── suppliers_portal_selenium_parser.py
├── web/              # Next.js фронтенд
│   └── src/
├── config.py
└── requirements.txt
```

## Площадки

| Площадка | Метод | Статус |
|----------|-------|--------|
| ЕИС (zakupki.gov.ru) | HTML scraping | Работает |
| Портал поставщиков (zakupki.mos.ru) | REST API | Работает |

## Локальный запуск

```bash
# Backend
pip install -r requirements.txt
cd api && uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend
cd web && npm install && npm run dev
```

## API

```
POST /api/search
{ "keywords": ["грамоты", "дипломы"], "platforms": ["portal", "eis"] }
```

## Лицензия

MIT
