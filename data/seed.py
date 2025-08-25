# data/seed.py
import os
import sqlite3
import random
import itertools

# Pastikan file .db selalu dibuat di folder data/
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "restaurants.db")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Buat tabel
c.executescript("""
DROP TABLE IF EXISTS restaurants;
DROP TABLE IF EXISTS ratings;

CREATE TABLE restaurants(
    id      INTEGER PRIMARY KEY,
    name    TEXT,
    cuisine TEXT,
    lat     REAL,
    lon     REAL
);

CREATE TABLE ratings(
    user_id INTEGER,
    resto_id INTEGER,
    rating   REAL,
    PRIMARY KEY (user_id, resto_id)
);
""")

# Data dummy 50 restoran
restaurants = [
    (i, f"Resto-{i}", random.choice(["Italian", "Japanese", "Local", "Western", "Chinese"]),
     -6.2 + 0.01 * i, 106.8 + 0.01 * i)
    for i in range(1, 51)
]
c.executemany("INSERT INTO restaurants VALUES (?,?,?,?,?)", restaurants)

# Data dummy rating: 30 user, masing-masing 15 restoran acak
users = range(1, 31)
for u in users:
    sampled = random.sample(range(1, 51), 15)
    ratings = [(u, r, round(random.uniform(3.0, 5.0), 1)) for r in sampled]
    c.executemany("INSERT INTO ratings VALUES (?,?,?)", ratings)

conn.commit()
conn.close()
print("✅ Database berhasil di-seed:", DB_PATH)