# CodeVector Products API

Backend to browse ~200,000 products with fast, stable pagination.

## Stack

- **FastAPI** + **asyncpg** (API)
- **PostgreSQL** (Neon / Supabase)
- **Render** (hosting)

## Pagination approach

Uses **keyset (cursor) pagination** on `(created_at DESC, id DESC)`.

**Why not OFFSET?** New inserts at the top cause duplicates and skipped rows with `OFFSET` pagination. Cursor pagination anchors to the last seen row, so browsing stays correct while data changes.

**Why `created_at` + `id`?** `created_at` is immutable, so updates to name/price don't reshuffle the list. `id` breaks ties when timestamps match.

## Setup

### 1. Database

Create a Postgres database (Neon or Supabase), then run `scripts/schema.sql` in the SQL editor.

### 2. Environment

```bash
cp .env.example .env
# paste your DATABASE_URL
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Seed 200,000 products

```bash
python scripts/seed.py
```

Uses PostgreSQL `COPY` for bulk load (seconds, not minutes).

### 5. Run locally

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

## API

### `GET /products`

| Param      | Description                          |
|------------|--------------------------------------|
| `limit`    | Page size (default 20, max 100)      |
| `cursor`   | Opaque cursor from previous response |
| `category` | Optional category filter             |

### `GET /categories`

Returns categories with product counts.

### `GET /health`

Health check and total product count.

## Deploy (Render)

1. Push this repo to GitHub
2. Create a **Web Service** on [Render](https://render.com)
3. Set `DATABASE_URL` in environment variables
4. Build: `pip install -r requirements.txt`
5. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Run `python scripts/seed.py` once against your production database

## What I'd improve with more time

- Automated tests for cursor edge cases (invalid cursor, last page, category filter)
- `EXPLAIN ANALYZE` examples in docs
- Rate limiting and structured logging
- CI pipeline for lint + tests

## AI usage

- AI helped scaffold FastAPI boilerplate, seed script, and bonus UI
- Core design choices (cursor pagination, indexes, `COPY` seeding) were intentional
- Verified AI did not use OFFSET pagination
