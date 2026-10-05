from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("shopbot.db")

CUSTOMERS = [
    (1001, "Alice Chen", "alice@example.test"),
    (1002, "Ben Ortiz", "ben@example.test"),
    (1003, "Carla Singh", "carla@example.test"),
    (1004, "Devon Brooks", "devon@example.test"),
    (1005, "Elena Rossi", "elena@example.test"),
    (1006, "Farid Hassan", "farid@example.test"),
]

PURCHASES = [
    (1001, "2026-08-19", "Noise-canceling headphones", 129.99, "delivered"),
    (1001, "2026-09-03", "USB-C travel charger", 39.95, "delivered"),
    (1001, "2026-09-18", "Laptop sleeve", 24.50, "delivered"),
    (1002, "2026-07-22", "Running shoes", 89.00, "delivered"),
    (1002, "2026-09-11", "Fitness watch", 179.00, "delivered"),
    (1002, "2026-09-27", "Water bottle", 22.00, "processing"),
    (1003, "2026-08-02", "Espresso grinder", 119.00, "delivered"),
    (1003, "2026-08-28", "Coffee filters", 14.75, "delivered"),
    (1003, "2026-09-30", "Glass dripper", 31.25, "shipped"),
    (1004, "2026-06-15", "Camping lantern", 44.95, "delivered"),
    (1004, "2026-08-12", "Hiking daypack", 76.00, "delivered"),
    (1004, "2026-09-25", "Trail map set", 18.50, "delivered"),
    (1005, "2026-07-06", "Chef knife", 94.00, "delivered"),
    (1005, "2026-09-01", "Cutting board", 47.50, "delivered"),
    (1005, "2026-09-29", "Digital kitchen scale", 29.99, "shipped"),
    (1006, "2026-08-09", "Mechanical keyboard", 109.00, "delivered"),
    (1006, "2026-09-14", "Wireless mouse", 54.99, "delivered"),
    (1006, "2026-10-01", "Desk mat", 27.00, "processing"),
]


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_database() -> None:
    """Create and seed the synthetic database if it does not already exist."""
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS purchases (
                purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                purchase_date TEXT NOT NULL,
                item TEXT NOT NULL,
                price REAL NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            );
            """
        )
        if conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO customers(customer_id, name, email) VALUES (?, ?, ?)",
                CUSTOMERS,
            )
        if conn.execute("SELECT COUNT(*) FROM purchases").fetchone()[0] == 0:
            conn.executemany(
                """
                INSERT INTO purchases(customer_id, purchase_date, item, price, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                PURCHASES,
            )


def list_customers() -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT customer_id, name, email FROM customers ORDER BY customer_id"
        ).fetchall()
    return [dict(row) for row in rows]


def purchase_history(customer_id: int) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT purchase_id, purchase_date, item, price, status
            FROM purchases
            WHERE customer_id = ?
            ORDER BY purchase_date DESC
            """,
            (customer_id,),
        ).fetchall()
    return [dict(row) for row in rows]
