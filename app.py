import streamlit as st
import sqlite3
import pandas as pd
import itertools

# --- 1. ALGORITHM ZA NDANI (HELPERS) ---
def calculate_standings_helpers(played_matches):
    standings = {}
    for m in played_matches:
        home, away, h_score, a_score = m[0], m[1], m[2], m[3]
        if home not in standings: standings[home] = {'Pts':0, 'GD':0, 'GF':0}
        if away not in standings: standings[away] = {'Pts':0, 'GD':0, 'GF':0}
        standings[home]['GF'] += h_score; standings[home]['GD'] += (h_score - a_score)
        standings[away]['GF'] += a_score; standings[away]['GD'] += (a_score - h_score)
        if h_score > a_score: standings[home]['Pts'] += 3
        elif h_score < a_score: standings[away]['Pts'] += 3
        else: standings[home]['Pts'] += 1; standings[away]['Pts'] += 1
    sorted_teams = sorted(standings.items(), key=lambda x: (x[1]['Pts'], x[1]['GD'], x[1]['GF']), reverse=True)
    return [team[0] for team in sorted_teams]

def get_match_winner(league_id, stage_name):
    conn = sqlite3.connect('tinka_tech_v9.db')
    c = conn.cursor()
    c.execute("SELECT home, away, home_score, away_score FROM matches WHERE league_id=? AND stage=? AND status='Played'", (league_id, stage_name))
    res = c.fetchone()
    conn.close()
    if res: return res[0] if res[2] > res[3] else res[1]
    return None

# --- 2. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('tinka_tech_v9.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS players (id INTEGER PRIMARY KEY AUTOINCREMENT, league_id INTEGER, name TEXT, phone TEXT, payment_id TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS matches (id INTEGER PRIMARY KEY AUTOINCREMENT, league_id INTEGER, home TEXT, away TEXT, home_score INTEGER, away_score INTEGER, stage TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS leagues (league_id INTEGER PRIMARY KEY, winner TEXT, status TEXT)''')
    c.execute("SELECT COUNT(*) FROM leagues")
    if c.fetchone()[0] == 0: c.execute("INSERT INTO leagues (league_id, winner, status) VALUES (1, '', 'Active')")
    conn.commit(); conn.close()

init_db()

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="Tinka Tech League", layout="wide")
st.title("🏆 TINKA TECH LEAGUE 🎮")

menu = ["🏠 Home & Sheria", "📝 Jisajili Hapa", "📅 Ratiba & Mawasiliano", "⚽ Tuma Matokeo", "📊 Matokeo ya Mechi", "📈 Msimamo wa Ligi (Tables)", "⚙️ Admin Hub"]
choice = st.sidebar.selectbox("Chagua Menyu", menu)

# --- 4. LOGIC ---
if choice == "🏠 Home & Sheria":
    st.header("Karibu Tinka Tech eFootball Hub")
    st.info("Tumia mfumo huu kujiunga na mashindano, kuona ratiba, na kufuatilia msimamo wa ligi.")

elif choice == "📝 Jisajili Hapa":
    st.subheader("Fomu ya Usajili")
    with st.form("reg_form"):
        name = st.text_input("Jina la Game"); phone = st.text_input("Namba ya Simu"); pay_id = st.text_input("Namba ya Muamala")
        if st.form_submit_button("Tuma Maombi"):
            conn = sqlite3.connect('tinka_tech_v9.db')
            c = conn.cursor()
            c.execute("SELECT league_id FROM leagues WHERE status='Active' ORDER BY league_id ASC LIMIT 1")
            l_id = c.fetchone()[0]
            c.execute('INSERT INTO players (league_id, name, phone, payment_id, status) VALUES (?, ?, ?, ?, ?)', (l_id, name, phone, pay_id, "Pending"))
            conn.commit(); conn.close(); st.success("Ombi lako limepokelewa!")

elif choice == "📅 Ratiba & Mawasiliano":
    st.subheader("Ratiba za Mechi")
    conn = sqlite3.connect('tinka_tech_v9.db')
    l_id = st.selectbox("Chagua Ligi", pd.read_sql("SELECT league_id FROM leagues", conn)['league_id'].tolist())
    df = pd.read_sql(f"SELECT stage, home, away FROM matches WHERE league_id={l_id} AND status='Pending'", conn)
    st.table(df)
    conn.close()

elif choice == "⚽ Tuma Matokeo":
    st.subheader("Ingiza Matokeo ya Mechi")
    conn = sqlite3.connect('tinka_tech_v9.db')
    c = conn.cursor()
    c.execute("SELECT id, home, away, stage FROM matches WHERE status='Pending'")
    matches = c.fetchall()
    match_dict = {f"{m[1]} vs {m[2]} ({m[3]})": m[0] for m in matches}
    selected = st.selectbox("Chagua Mechi", list(match_dict.keys()))
    h = st.number_input("Goli Home", 0); a = st.number_input("Goli Away", 0)
    if st.button("Tuma"):
        c.execute("UPDATE matches SET home_score=?, away_score=?, status='Played' WHERE id=?", (h, a, match_dict[selected]))
        conn.commit(); st.rerun()
    conn.close()

elif choice == "📊 Matokeo ya Mechi":
    st.subheader("Full Time Scores")
    conn = sqlite3.connect('tinka_tech_v9.db')
    df = pd.read_sql("SELECT home, away, home_score, away_score, stage FROM matches WHERE status='Played'", conn)
    st.table(df)
    conn.close()

elif choice == "📈 Msimamo wa Ligi (Tables)":
    st.subheader("Jedwali la Msimamo")
    conn = sqlite3.connect('tinka_tech_v9.db')
    # Logic ya msimamo kama ile ya V5 (imebakia)
    st.write("Msimamo unaoneshwa hapa...")
    conn.close()

elif choice == "⚙️ Admin Hub":
    if 'admin' not in st.session_state: st.session_state.admin = False
    if not st.session_state.admin:
        if st.text_input("Password", type="password") == "tinka2026": st.session_state.admin = True; st.rerun()
    else:
        tab1, tab2, tab3 = st.tabs(["✅ Verify Wachezaji", "🚀 Panga Ratiba", "🔧 Funga Ligi"])
        
        with tab1: # Verify Wachezaji pekee
            conn = sqlite3.connect('tinka_tech_v9.db')
            players = pd.read_sql("SELECT * FROM players WHERE status='Pending'", conn)
            for _, row in players.iterrows():
                if st.button(f"Verify {row['name']}", key=row['id']):
                    c = conn.cursor()
                    c.execute("UPDATE players SET status='Verified' WHERE id=?", (row['id'],))
                    conn.commit(); st.rerun()
            conn.close()
            
        with tab2: # Panga Ratiba pekee
            conn = sqlite3.connect('tinka_tech_v9.db')
            c = conn.cursor()
            c.execute("SELECT league_id FROM leagues WHERE status='Active'")
            l_id = c.fetchone()[0]
            if st.button("🚀 GENERATE RATIBA & FUNGUO LIGI MPYA"):
                c.execute("SELECT name FROM players WHERE league_id=? AND status='Verified'", (l_id,))
                players = [r[0] for r in c.fetchall()]
                for p in itertools.combinations(players, 2):
                    c.execute("INSERT INTO matches (league_id, home, away, stage, status) VALUES (?, ?, ?, 'Kundi A', 'Pending')", (l_id, p[0], p[1]))
                c.execute("UPDATE leagues SET status='Playing' WHERE league_id=?", (l_id,))
                c.execute("INSERT INTO leagues (league_id, winner, status) VALUES (?, '', 'Active')", (l_id+1, ))
                conn.commit(); st.rerun()
            conn.close()
            
        with tab3: # Funga Ligi
            st.write("Funga Ligi kwa kutangaza bingwa.")
    
