import csv
import io
import os
import random
import uuid
from datetime import datetime, timedelta, timezone

import psycopg2
from dotenv import load_dotenv

load_dotenv()

CATEGORIES = ["electronics", "clothing", "home", "books", "sports", "toys", "garden"]
NAME_PREFIXES = ["Pro", "Ultra", "Basic", "Max", "Mini", "Super", "Eco"]
NAME_TYPES = ["Widget", "Gadget", "Chair", "Lamp", "Bag", "Shoe", "Book", "Ball"]

BATCH_SIZE = 200_000


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("Set DATABASE_URL in .env or environment")

    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    print("Clearing existing products...")
    cur.execute("TRUNCATE TABLE products")

    print(f"Generating {BATCH_SIZE:,} products...")
    buf = io.StringIO()
    writer = csv.writer(buf)
    base_time = datetime.now(timezone.utc)

    for i in range(BATCH_SIZE):
        created = base_time - timedelta(seconds=i)
        name = f"{random.choice(NAME_PREFIXES)} {random.choice(NAME_TYPES)} {i % 10000}"
        writer.writerow(
            [
                str(uuid.uuid4()),
                name,
                random.choice(CATEGORIES),
                round(random.uniform(4.99, 999.99), 2),
                created.isoformat(),
                created.isoformat(),
            ]
        )

    buf.seek(0)
    print("Bulk loading via COPY...")
    cur.copy_expert(
        """
        COPY products (id, name, category, price, created_at, updated_at)
        FROM STDIN WITH (FORMAT CSV)
        """,
        buf,
    )

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM products")
    count = cur.fetchone()[0]
    print(f"Done. {count:,} products in database.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
