import streamlit as st
import sqlite3
import pandas as pd
import os

# 1. Database Initialization - Imerekebishwa ili itengeneze file kama halipo
def get_db_connection():
    # Tunatumia file la database kwenye folder la sasa
    conn = sqlite3.connect('tinka_tech.db')
    return conn

# Unda table kama hazipo
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS players (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS matches (id INTEGER PRIMARY KEY AUTOINCREMENT, home TEXT, away TEXT, h_score INTEGER, a_score INTEGER, status TEXT)')
    conn.commit()
    conn.close()

init_db()

# 2. UI Layout
st.set_page_config(page_title="Tinka Tech League", layout="wide")
st.title("🏆 TINKA TECH LEAGUE 🎮")

# Sidebar
menu = ["🏠 Home", "📝 Jisajili", "⚽ Mechi", "📊 Msimamo"]
choice = st.sidebar.selectbox("Chagua Menyu", menu)

# 3. Logic
if choice == "🏠 Home":
    st.write("Karibu kwenye mfumo rasmi wa Tinka Tech eFootball.")

elif choice == "📝 Jisajili":
    st.subheader("Jisajili Kwenye Ligi")
    with st.form("reg_form"):
        name = st.text_input("Jina la Mchezaji")
        phone = st.text_input("Namba ya Simu")
        submitted = st.form_submit_button("Sajili")
        if submitted:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('INSERT INTO players (name, phone) VALUES (?, ?)', (name, phone))
            conn.commit()
            conn.close()
            st.success(f"Hongera {name}, umesajiliwa!")

elif choice == "⚽ Mechi":
    st.subheader("Orodha ya Mechi")
    conn = get_db_connection()
    try:
        df = pd.read_sql("SELECT * FROM matches", conn)
        if not df.empty:
            st.table(df)
        else:
            st.write("Hakuna mechi zilizopangwa bado.")
    except Exception as e:
        st.write("Database bado haijatengenezwa vizuri.")
    conn.close()

elif choice == "📊 Msimamo":
    st.subheader("Msimamo wa Ligi")
    st.write("Msimamo utaonekana hapa pindi mechi zitakapochezwa.")
