"""Seed the demo SQLite database for the e-commerce quick start.

Usage:
    python examples/ecommerce/seed_db.py [path]   (default: examples/ecommerce/shop.db)
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path


def seed(database: str | Path) -> None:
    connection = sqlite3.connect(database)
    connection.executescript(
        """
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            activity_score REAL
        );
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL REFERENCES customers(id),
            status TEXT NOT NULL,
            total REAL NOT NULL
        );
        CREATE TABLE payments (
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL REFERENCES orders(id),
            status TEXT NOT NULL,
            amount REAL NOT NULL
        );
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL
        );
        """
    )
    connection.executemany(
        "INSERT INTO customers (id, name, activity_score) VALUES (?, ?, ?)",
        [(1, "Alice", 0.9), (2, "Bob", 0.4), (3, "Carol", 0.2)],
    )
    connection.executemany(
        "INSERT INTO orders (id, customer_id, status, total) VALUES (?, ?, ?, ?)",
        [(1, 1, "completed", 120.0), (2, 1, "completed", 80.0), (3, 2, "refunded", 40.0), (4, 3, "completed", 15.0)],
    )
    connection.executemany(
        "INSERT INTO payments (id, order_id, status, amount) VALUES (?, ?, ?, ?)",
        [(1, 1, "completed", 120.0), (2, 2, "completed", 80.0), (3, 3, "failed", 40.0), (4, 4, "completed", 15.0)],
    )
    connection.executemany(
        "INSERT INTO products (id, name, price) VALUES (?, ?, ?)",
        [(1, "Widget", 30.0), (2, "Gadget", 50.0)],
    )
    connection.commit()
    connection.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed the e-commerce demo database")
    parser.add_argument("path", nargs="?", default=str(Path(__file__).with_name("shop.db")))
    args = parser.parse_args(argv)

    seed(args.path)
    print(f"seeded demo database at {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
