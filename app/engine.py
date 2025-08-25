import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import sqlite3, json

class RestaurantCF:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # 80 MB
        self._load_data()

    def _load_data(self):
        ratings = pd.read_sql("SELECT user_id,resto_id,rating FROM ratings", self.conn)
        restos = pd.read_sql("SELECT id,name,cuisine FROM restaurants", self.conn)
        self.ratings_mat = ratings.pivot(index='user_id', columns='resto_id', values='rating').fillna(0)
        self.restos = restos.set_index('id')

    def nearest_neighbors(self, user_id: int, k: int = 5):
        if user_id not in self.ratings_mat.index:
            return self._cold_start(user_id)
        vec = self.ratings_mat.loc[[user_id]]
        sims = cosine_similarity(vec, self.ratings_mat).flatten()
        top = np.argsort(-sims)[1:k+1]
        return self.ratings_mat.iloc[top].index.tolist()

    def recommend(self, user_id: int, top_n: int = 5):
        neighbors = self.nearest_neighbors(user_id)
        neighbor_ratings = self.ratings_mat.loc[neighbors].mean(axis=0)
        already = self.ratings_mat.loc[user_id]
        candidates = neighbor_ratings[already == 0]
        return candidates.sort_values(ascending=False).head(top_n).index.tolist()

    def _cold_start(self, user_id):
        # Fallback: popular in user area (simplified)
        return list(range(1,6))  # stub