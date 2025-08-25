# app_ui.py  (root project)
import streamlit as st
import httpx
import os

st.set_page_config(page_title="🍽️ Resto Recommender", layout="centered")

# --- Section 1: Rekomendasi berdasarkan User ID ---
st.title("🍽️ Restaurant Recommendation Demo")
user_id = st.number_input("Masukkan User ID", min_value=1, max_value=30, value=1)

if st.button("Rekomendasikan"):
    with st.spinner("Memuat rekomendasi..."):
        try:
            r = httpx.get(f"http://localhost:8000/recommend-full/{user_id}")
            r.raise_for_status()
            recs = r.json()["recommendations"]
            st.success(f"Rekomendasi untuk user {user_id}")
            st.table(recs)
        except Exception as e:
            st.error(f"Gagal memuat rekomendasi: {e}")

st.markdown("---")  # garis pemisah

# --- Section 2: Lihat detail restoran berdasarkan ID ---
st.subheader("🔍 Detail Restoran")
resto_id = st.number_input("Masukkan ID Restoran", min_value=1, max_value=50, value=15)

if st.button("Tampilkan Detail"):
    with st.spinner("Loading detail..."):
        try:
            r = httpx.get(f"http://localhost:8000/resto/{resto_id}")
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                st.error(data["error"])
            else:
                st.subheader(f"{data['name']} ({data['cuisine']})")
                st.write(f"ID      : {data['id']}")
                st.write(f"Latitude: {data['lat']}")
                st.write(f"Longitude: {data['lon']}")
        except Exception as e:
            st.error(f"Gagal memuat detail: {e}")