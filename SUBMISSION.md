# Submission Note

## Live URL

`https://codevector-products-umh6.onrender.com`

## GitHub

`https://github.com/rudraprakashnayak/codevector-products`

## What I chose and why

- **FastAPI + PostgreSQL (Neon/Supabase) + Render** — simple, fast to deploy, strong Postgres indexing
- **Keyset pagination** on `(created_at DESC, id DESC)` — stable while new products are inserted; no duplicates or gaps
- **Composite indexes** — one for full browse, one for category + browse
- **COPY-based seed** — loads 200k rows in seconds instead of row-by-row inserts

## What I'd improve with more time

- Unit/integration tests for pagination correctness
- Performance benchmarks with `EXPLAIN ANALYZE`
- Rate limiting and observability (structured logs, metrics)
- Admin endpoint to simulate live inserts for demo purposes

## How I used AI

- Scaffolded project structure, FastAPI routes, seed script, and bonus UI
- AI initially suggested OFFSET pagination in some examples — I rejected that and used cursor pagination
- I verified index design and cursor encoding/decoding myself so I can explain and change it live
