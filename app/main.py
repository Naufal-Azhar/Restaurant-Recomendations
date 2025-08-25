#  app/main.py  – full file
import os
import pandas as pd
from fastapi import FastAPI
from app.engine import RestaurantCF

# ---------------------------------------------
# path ke database (selalu di data/restaurants.db)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "data", "restaurants.db")

# ---------------------------------------------
# init FastAPI & recommender engine
app = FastAPI(title="Restaurant Recommendation API")
cf = RestaurantCF(DB_PATH)

# ---------------------------------------------
# 1. Rekomendasi (hanya ID)
@app.get("/recommend/{user_id}")
def recommend(user_id: int, top_n: int = 5):
    return {"user_id": user_id, "restaurant_ids": cf.recommend(user_id, top_n)}

# ---------------------------------------------
# 2. Rekomendasi dengan nama, cuisine, dll.
@app.get("/recommend-full/{user_id}")
def recommend_full(user_id: int, limit: int = 5):
    resto_ids = cf.recommend(user_id, top_n=limit)
    if not resto_ids:
        return {"user_id": user_id, "recommendations": []}

    placeholders = ",".join("?" * len(resto_ids))
    sql = f"""
        SELECT id, name, cuisine, lat, lon
        FROM restaurants
        WHERE id IN ({placeholders})
    """
    df = pd.read_sql(sql, cf.conn, params=resto_ids)

    # urutkan sesuai urutan rekomendasi
    order_map = {rid: idx for idx, rid in enumerate(resto_ids)}
    df["order"] = df["id"].map(order_map)
    df = df.sort_values("order").drop(columns="order")

    return {"user_id": user_id, "recommendations": df.to_dict(orient="records")}

# ---------------------------------------------
# 3. Detail satu restoran berdasarkan ID
@app.get("/resto/{resto_id}")
def get_resto(resto_id: int):
    df = pd.read_sql(
        "SELECT id, name, cuisine, lat, lon FROM restaurants WHERE id = ?",
        cf.conn,
        params=(resto_id,)
    )
    if df.empty:
        return {"error": "Restoran tidak ditemukan"}
    return df.iloc[0].to_dict()

# ---------------------------------------------
# 4. Daftar semua restoran (opsional, pagination-ready)
@app.get("/restos")
def list_restos(skip: int = 0, limit: int = 50):
    df = pd.read_sql(
        "SELECT * FROM restaurants LIMIT ? OFFSET ?",
        cf.conn,
        params=(limit, skip)
    )
    return df.to_dict(orient="records")