import streamlit as st
import sqlite3
import pandas as pd

# --- 1. DATABASE SETUP (V2) ---
def init_db():
    conn = sqlite3.connect('tinka_tech_v2.db')
    c = conn.cursor()
    # Table ya Wachezaji (Imeongezwa league_id)
    c.execute('''CREATE TABLE IF NOT EXISTS players 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, league_id INTEGER, name TEXT, phone TEXT, payment_id TEXT, status TEXT)''')
    # Table ya Mechi (Imeongezwa league_id)
    c.execute('''CREATE TABLE IF NOT EXISTS matches 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, league_id INTEGER, home TEXT, away TEXT, home_score INTEGER, away_score INTEGER, stage TEXT, status TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. MUONEKANO (UI LAYOUT) ---
st.set_page_config(page_title="Tinka Tech League", layout="wide")
st.title("🏆 TINKA TECH LEAGUE 🎮")

menu = ["🏠 Home & Sheria", "📝 Jisajili Hapa", "📅 Ratiba", "📊 Matokeo & Msimamo", "⚙️ Admin Hub"]
choice = st.sidebar.selectbox("Chagua Menyu", menu)

# --- 3. LOGIC YA KILA UKURASA ---

if choice == "🏠 Home & Sheria":
    st.header("Karibu Tinka Tech eFootball Hub")
    st.write("Mfumo rasmi wa kusimamia mashindano ya eFootball kuanzia makundi hadi fainali.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚙️ Sheria za Mchezo (Gameplay Rules)")
        st.warning("""
        * **Control:** Full Human Controlled (Hakuna kuachiwa AI).
        * **Smart Assist:** NO Smart Assist (Imezuiwa kabisa).
        * **Muda:** Dakika 10 kwa kila mechi.
        * **Matokeo:** Hakuna Extra Time wala Penati kwenye hatua ya makundi.
        * **Mtoano (Knockouts):** Extra Time na Penati zitaruhusiwa kuanzia hatua ya mtoano pekee.
        """)
        
    with col2:
        st.markdown("### 🏆 Mfumo wa Mashindano (Tournament Format)")
        st.info("""
        * **Idadi ya Wachezaji:** Kila Ligi/Msimu unachukua wachezaji 16. Mfumo utapanga Ligi mpya kiotomatiki ikiwa ya kwanza imejaa.
        * **Hatua ya Makundi:** Wachezaji watagawanywa kwenye makundi 4 (A, B, C, D). Kila mchezaji atacheza mechi 3 kwenye kundi lake.
        * **Kufuzu:** Wachezaji 2 wa juu kutoka kila kundi (Jumla 8) watafuzu hatua ya Robo Fainali.
        * **Vigezo vya Msimamo:** 1. Points, 2. Goal Difference (GD), 3. Goals For (GF).
        """)

    st.markdown("### 📖 Jinsi ya Kujisajili")
    st.success("Fanya malipo ya kiingilio cha **TZS 1,000** kwenda namba **0792460625**. Kisha nenda menyu ya 'Jisajili Hapa' ujaze namba ya muamala.")

elif choice == "📝 Jisajili Hapa":
    st.subheader("Fomu ya Usajili wa Ligi")
    
    with st.form("reg_form"):
        name = st.text_input("Jina lako la Kwenye Game (In-Game Name)")
        phone = st.text_input("Namba yako ya Simu")
        pay_id = st.text_input("Namba ya Muamala (Transaction ID)")
        submitted = st.form_submit_button("Tuma Maombi")
        
        if submitted:
            if name and pay_id:
                conn = sqlite3.connect('tinka_tech_v2.db')
                c = conn.cursor()
                
                # --- AUTO-LEAGUE LOGIC ---
                # Tafuta Ligi ya sasa iliyo wazi (Yenye wachezaji chini ya 16)
                c.execute("SELECT MAX(league_id) FROM players")
                max_league = c.fetchone()[0]
                
                if max_league is None:
                    current_league = 1
                else:
                    c.execute("SELECT COUNT(*) FROM players WHERE league_id=?", (max_league,))
                    count = c.fetchone()[0]
                    if count >= 16:
                        current_league = max_league + 1 # Ligi imejaa, anza mpya!
                    else:
                        current_league = max_league
                
                # Ingiza mchezaji kwenye Ligi husika
                c.execute('INSERT INTO players (league_id, name, phone, payment_id, status) VALUES (?, ?, ?, ?, ?)', 
                          (current_league, name, phone, pay_id, "Pending"))
                conn.commit()
                conn.close()
                st.success(f"Asante {name}! Umewekwa kwenye foleni ya LIGI NAMBA {current_league}. Subiri uhakiki wa Admin.")
            else:
                st.error("Tafadhali jaza Jina na Namba ya Muamala.")

elif choice == "📅 Ratiba":
    st.subheader("Ratiba ya Mechi Zijazo")
    conn = sqlite3.connect('tinka_tech_v2.db')
    
    # Select Ligi ya kuangalia
    leagues = pd.read_sql("SELECT DISTINCT league_id FROM matches", conn)
    if not leagues.empty:
        l_id = st.selectbox("Chagua Ligi", leagues['league_id'].tolist())
        df_fixtures = pd.read_sql(f"SELECT home AS 'Nyumbani', away AS 'Ugenini', stage AS 'Hatua' FROM matches WHERE status = 'Pending' AND league_id = {l_id}", conn)
        
        if not df_fixtures.empty:
            st.table(df_fixtures)
        else:
            st.info("Hakuna ratiba mpya ya ligi hii kwa sasa.")
    else:
        st.info("Hakuna ratiba zilizopangwa bado.")
    conn.close()

elif choice == "📊 Matokeo & Msimamo":
    conn = sqlite3.connect('tinka_tech_v2.db')
    leagues = pd.read_sql("SELECT DISTINCT league_id FROM matches WHERE status = 'Played'", conn)
    
    if not leagues.empty:
        l_id = st.selectbox("Tazama Msimamo wa Ligi Namba:", leagues['league_id'].tolist())
        
        st.subheader(f"Live Scores: Ligi {l_id} ⚽")
        c = conn.cursor()
        c.execute("SELECT home, away, home_score, away_score, stage FROM matches WHERE status = 'Played' AND league_id = ?", (l_id,))
        played_matches = c.fetchall()
        
        for m in played_matches:
            st.success(f"**{m[0]} ({m[2]}) - ({m[3]}) {m[1]}** | *Hatua: {m[4]}*")
            
        st.markdown("---")
        st.subheader(f"📈 Msimamo: Ligi {l_id}")
        
        # HESABU ZA MSIMAMO
        standings = {}
        for m in played_matches:
            home, away, h_score, a_score = m[0], m[1], m[2], m[3]
            
            if home not in standings: standings[home] = {'Pld':0, 'W':0, 'D':0, 'L':0, 'GF':0, 'GA':0, 'GD':0, 'Pts':0}
            if away not in standings: standings[away] = {'Pld':0, 'W':0, 'D':0, 'L':0, 'GF':0, 'GA':0, 'GD':0, 'Pts':0}
            
            standings[home]['Pld'] += 1
            standings[away]['Pld'] += 1
            standings[home]['GF'] += h_score
            standings[home]['GA'] += a_score
            standings[away]['GF'] += a_score
            standings[away]['GA'] += h_score
            
            if h_score > a_score:
                standings[home]['W'] += 1
                standings[home]['Pts'] += 3
                standings[away]['L'] += 1
            elif h_score < a_score:
                standings[away]['W'] += 1
                standings[away]['Pts'] += 3
                standings[home]['L'] += 1
            else:
                standings[home]['D'] += 1
                standings[away]['D'] += 1
                standings[home]['Pts'] += 1
                standings[away]['Pts'] += 1
                
        for team in standings:
            standings[team]['GD'] = standings[team]['GF'] - standings[team]['GA']
            
        df_standings = pd.DataFrame.from_dict(standings, orient='index')
        df_standings.index.name = 'Mchezaji'
        df_standings = df_standings.sort_values(by=['Pts', 'GD', 'GF'], ascending=[False, False, False])
        
        st.dataframe(df_standings, use_container_width=True)
    else:
        st.info("Bado hakuna matokeo yoyote kwenye mfumo.")
    conn.close()

elif choice == "⚙️ Admin Hub":
    password = st.text_input("Ingiza Password ya Tinka Tech Admin", type="password")
    
    if password == "tinka2026": 
        st.success("Karibu Msimamizi!")
        tab1, tab2, tab3 = st.tabs(["✅ Hakiki Wachezaji", "📅 Panga Ratiba", "⚽ Weka Matokeo"])
        
        with tab1:
            conn = sqlite3.connect('tinka_tech_v2.db')
            pending = pd.read_sql("SELECT * FROM players WHERE status = 'Pending'", conn)
            
            if not pending.empty:
                for index, row in pending.iterrows():
                    col1, col2 = st.columns([3, 1])
                    col1.write(f"👤 **{row['name']}** (Ligi {row['league_id']}) | 💵 Muamala: **{row['payment_id']}**")
                    if col2.button("Verify", key=f"v_{row['id']}"):
                        c = conn.cursor()
                        c.execute("UPDATE players SET status = 'Verified' WHERE id = ?", (row['id'],))
                        conn.commit()
                        st.rerun()
            else:
                st.write("Hakuna maombi mapya.")
            conn.close()

        with tab2:
            with st.form("fixture_form"):
                league_id = st.number_input("Chagua Namba ya Ligi", min_value=1, step=1)
                home_team = st.text_input("Mchezaji wa Nyumbani")
                away_team = st.text_input("Mchezaji wa Ugenini")
                stage = st.text_input("Kundi / Hatua (Mfano: Kundi A, Robo Fainali)")
                if st.form_submit_button("Hifadhi Ratiba"):
                    conn = sqlite3.connect('tinka_tech_v2.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO matches (league_id, home, away, home_score, away_score, stage, status) VALUES (?, ?, ?, 0, 0, ?, 'Pending')", 
                              (league_id, home_team, away_team, stage))
                    conn.commit()
                    conn.close()
                    st.success("Ratiba imehifadhiwa!")

        with tab3:
            conn = sqlite3.connect('tinka_tech_v2.db')
            pending_matches = pd.read_sql("SELECT id, league_id, home, away, stage FROM matches WHERE status = 'Pending'", conn)
            
            if not pending_matches.empty:
                for index, row in pending_matches.iterrows():
                    with st.expander(f"Ligi {row['league_id']} | {row['home']} VS {row['away']} ({row['stage']})"):
                        with st.form(f"result_{row['id']}"):
                            h_goals = st.number_input(f"Magoli {row['home']}", min_value=0, step=1)
                            a_goals = st.number_input(f"Magoli {row['away']}", min_value=0, step=1)
                            if st.form_submit_button("Thibitisha Matokeo"):
                                c = conn.cursor()
                                c.execute("UPDATE matches SET home_score=?, away_score=?, status='Played' WHERE id=?", 
                                          (h_goals, a_goals, row['id']))
                                conn.commit()
                                st.rerun()
            else:
                st.write("Hakuna mechi zinazosubiri matokeo.")
            conn.close()
                    
