import base64
import json
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.db import close_pool, get_pool, init_pool

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_pool()
    yield
    await close_pool()


app = FastAPI(title="CodeVector Products API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def encode_cursor(created_at: datetime, product_id: UUID) -> str:
    payload = {"created_at": created_at.isoformat(), "id": str(product_id)}
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()


def decode_cursor(cursor: str) -> tuple[datetime, UUID]:
    try:
        raw = base64.urlsafe_b64decode(cursor.encode())
        data = json.loads(raw)
        return datetime.fromisoformat(data["created_at"]), UUID(data["id"])
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid cursor") from exc


def row_to_dict(row: Any) -> dict:
    return {
        "id": str(row["id"]),
        "name": row["name"],
        "category": row["category"],
        "price": float(row["price"]),
        "created_at": row["created_at"].isoformat(),
        "updated_at": row["updated_at"].isoformat(),
    }


@app.get("/health")
async def health() -> dict:
    pool = get_pool()
    async with pool.acquire() as conn:
        count = await conn.fetchval("SELECT COUNT(*) FROM products")
    return {"status": "ok", "product_count": count}


@app.get("/categories")
async def categories() -> dict:
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT category, COUNT(*) AS count
            FROM products
            GROUP BY category
            ORDER BY category
            """
        )
    return {
        "items": [{"category": row["category"], "count": row["count"]} for row in rows]
    }


@app.get("/products")
async def list_products(
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = None,
    category: str | None = None,
) -> dict:
    pool = get_pool()
    clauses: list[str] = []
    params: list[Any] = []
    param_index = 1

    if category:
        clauses.append(f"category = ${param_index}")
        params.append(category)
        param_index += 1

    if cursor:
        cursor_created_at, cursor_id = decode_cursor(cursor)
        clauses.append(f"(created_at, id) < (${param_index}, ${param_index + 1})")
        params.extend([cursor_created_at, cursor_id])
        param_index += 2

    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    params.append(limit + 1)
    sql = f"""
        SELECT id, name, category, price, created_at, updated_at
        FROM products
        {where_sql}
        ORDER BY created_at DESC, id DESC
        LIMIT ${param_index}
    """

    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, *params)

    has_more = len(rows) > limit
    rows = rows[:limit]

    next_cursor = None
    if has_more and rows:
        last = rows[-1]
        next_cursor = encode_cursor(last["created_at"], last["id"])

    return {
        "items": [row_to_dict(row) for row in rows],
        "next_cursor": next_cursor,
        "has_more": has_more,
    }


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def ui() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
