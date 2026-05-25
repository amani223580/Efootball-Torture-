import streamlit as st
import sqlite3
import pandas as pd
import itertools

# --- 1. ALGORITHM ZA NDANI (HELPERS) KWA AJILI YA AUTOMATION ---
def calculate_standings_helpers(played_matches):
    standings = {}
    for m in played_matches:
        home, away, h_score, a_score = m[0], m[1], m[2], m[3]
        if home not in standings: standings[home] = {'Pts':0, 'GD':0, 'GF':0, 'GA':0, 'Pld':0, 'W':0, 'D':0, 'L':0}
        if away not in standings: standings[away] = {'Pts':0, 'GD':0, 'GF':0, 'GA':0, 'Pld':0, 'W':0, 'D':0, 'L':0}
        
        standings[home]['Pld'] += 1
        standings[away]['Pld'] += 1
        standings[home]['GF'] += h_score
        standings[home]['GA'] += a_score
        standings[away]['GF'] += a_score
        standings[away]['GA'] += h_score
        
        standings[home]['GD'] = standings[home]['GF'] - standings[home]['GA']
        standings[away]['GD'] = standings[away]['GF'] - standings[away]['GA']
        
        if h_score > a_score:
            standings[home]['Pts'] += 3
            standings[home]['W'] += 1
            standings[away]['L'] += 1
        elif h_score < a_score:
            standings[away]['Pts'] += 3
            standings[away]['W'] += 1
            standings[home]['L'] += 1
        else:
            standings[home]['Pts'] += 1
            standings[away]['Pts'] += 1
            standings[home]['D'] += 1
            standings[away]['D'] += 1
            
    sorted_teams = sorted(standings.items(), key=lambda x: (x[1]['Pts'], x[1]['GD'], x[1]['GF']), reverse=True)
    return sorted_teams

def get_match_winner(league_id, stage_name):
    conn = sqlite3.connect('tinka_tech_v11.db')
    c = conn.cursor()
    c.execute("SELECT home, away, home_score, away_score FROM matches WHERE league_id=? AND stage=? AND status='Played'", (league_id, stage_name))
    res = c.fetchone()
    conn.close()
    if res:
        home, away, h_score, a_score = res
        if h_score > a_score: return home
        elif h_score < a_score: return away
    return None

# --- 2. DATABASE SETUP (V11) ---
def init_db():
    conn = sqlite3.connect('tinka_tech_v11.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS players 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, league_id INTEGER, name TEXT, phone TEXT, payment_id TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS matches 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, league_id INTEGER, home TEXT, away TEXT, home_score INTEGER, away_score INTEGER, stage TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS leagues 
                 (league_id INTEGER PRIMARY KEY, winner TEXT, status TEXT)''')
    
    c.execute("SELECT COUNT(*) FROM leagues")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO leagues (league_id, winner, status) VALUES (1, '', 'Active')")
        
    conn.commit()
    conn.close()

init_db()

# --- 3. MUONEKANO WA MFUMO (UI LAYOUT) ---
st.set_page_config(page_title="Tinka Tech League V11", layout="wide")
st.title("🏆 TINKA TECH LEAGUE V11 🎮")

# Orodha kamili ya Menyu 9 bila kupoteza hata moja
menu = [
    "🏠 Home & Sheria", 
    "📝 Jisajili Hapa", 
    "📅 Ratiba & Mawasiliano", 
    "⚽ Tuma Matokeo", 
    "📊 Matokeo ya Mechi", 
    "📈 Msimamo wa Ligi (Tables)", 
    "🏆 Msimamo wa Knockouts & Waliofuzu",  # Menyu Mpya 1
    "🗓️ Ratiba Kamili ya Hatua (Fixtures)",  # Menyu Mpya 2
    "⚙️ Admin Hub"
]
choice = st.sidebar.selectbox("Chagua Menyu", menu)

# --- 4. LOGIC YA KILA UKURASA ---

if choice == "🏠 Home & Sheria":
    st.header("Karibu Tinka Tech eFootball Hub")
    st.write("Mfumo thabiti wa kiotomatiki unaoendesha mashindano ya eFootball kuanzia usajili hadi kutwaa taji.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ⚙️ Sheria za Michezo (Gameplay Rules)")
        st.warning("""
        * **Control:** Full Human Controlled (Ni marufuku kutumia AI au kuachia simu).
        * **Smart Assist:** NO Smart Assist (Imezuiwa kabisa).
        * **Muda wa Mechi:** Dakika 10 (Muda rasmi wa uwanjani).
        * **Hatua ya Makundi:** Hakuna Extra Time wala Penati. Mechi inaweza kuisha kwa Droo.
        * **Hatua ya Mtoano (Knockouts):** Lazima mshindi apatikane (Extra Time & Penati).
        """)
    with col2:
        st.markdown("### 🏆 Mfumo wa Mashindano na Ubingwa")
        st.info("""
        * **Usajili wa Msimu:** Ligi inajaza wachezaji 16 kiwango cha juu, lakini mfumo unanyumbuka kwa idadi yoyote.
        * **Hatua ya Makundi:** Wachezaji wanagawanywa kwenye makundi (A, B, C, D) kiotomatiki kama wamefika 16.
        * **Kufuzu Knockouts:** Viongozi wa makundi wanaenda Robo Fainali, Nusu Fainali hadi Fainali kuu.
        """)
    st.success("Tuma kiingilio cha **TZS 1,000** kwenda namba **0792460625** kisha ujisajili.")

elif choice == "📝 Jisajili Hapa":
    st.subheader("Fomu ya Usajili wa Ligi ya Sasa")
    with st.form("reg_form"):
        name = st.text_input("Jina lako la Kwenye Game (In-Game Name)")
        phone = st.text_input("Namba yako ya Simu")
        pay_id = st.text_input("Namba ya Muamala (Transaction ID)")
        submitted = st.form_submit_button("Tuma Maombi")
        
        if submitted:
            if name and pay_id and phone:
                conn = sqlite3.connect('tinka_tech_v11.db')
                c = conn.cursor()
                c.execute("SELECT league_id FROM leagues WHERE status='Active' ORDER BY league_id DESC LIMIT 1")
                active_row = c.fetchone()
                current_league = active_row[0] if active_row else 1
                
                c.execute('INSERT INTO players (league_id, name, phone, payment_id, status) VALUES (?, ?, ?, ?, ?)', 
                          (current_league, name, phone, pay_id, "Pending"))
                conn.commit()
                conn.close()
                st.success(f"Hongera {name}! Umesajiliwa kwenye **LIGI NAMBA {current_league}**. Subiri Admin aku-verify.")
            else:
                st.error("Tafadhali jaza nafasi zote vizuri.")

elif choice == "📅 Ratiba & Mawasiliano":
    st.subheader("Mawasiliano na Simu za Wachezaji walio-Verify")
    conn = sqlite3.connect('tinka_tech_v11.db')
    all_leagues = pd.read_sql("SELECT league_id FROM leagues", conn)
    if not all_leagues.empty:
        l_id = st.selectbox("Chagua Ligi kuona Wachezaji", all_leagues['league_id'].tolist(), key="contacts_lg")
        df_contacts = pd.read_sql(f"SELECT name AS 'Jina la Game', phone AS 'Namba ya Simu', status AS 'Hali' FROM players WHERE league_id={l_id}", conn)
        if not df_contacts.empty:
            st.dataframe(df_contacts, use_container_width=True)
        else:
            st.info("Hakuna wachezaji waliosajiliwa kwenye ligi hii.")
    conn.close()

elif choice == "⚽ Tuma Matokeo":
    st.subheader("Sehemu ya Wachezaji Kuingiza Matokeo (Self-Submission)")
    conn = sqlite3.connect('tinka_tech_v11.db')
    active_leagues = pd.read_sql("SELECT league_id FROM leagues WHERE status='Playing'", conn)
    
    if not active_leagues.empty:
        l_id = st.selectbox("Chagua Ligi Unayocheza", active_leagues['league_id'].tolist())
        c = conn.cursor()
        c.execute("SELECT id, home, away, stage FROM matches WHERE status='Pending' AND league_id=?", (l_id,))
        pending_list = c.fetchall()
        
        if pending_list:
            match_options = {f"[{m[3]}] {m[1]} VS {m[2]}": m[0] for m in pending_list}
            selected_match_text = st.selectbox("Chagua Mechi Yako", list(match_options.keys()))
            match_id = match_options[selected_match_text]
            c.execute("SELECT home, away FROM matches WHERE id=?", (match_id,))
            match_data = c.fetchone()
            
            with st.form("player_res_form"):
                col1, col2 = st.columns(2)
                h_goals = col1.number_input(f"Magoli ya {match_data[0]}", min_value=0, step=1)
                a_goals = col2.number_input(f"Magoli ya {match_data[1]}", min_value=0, step=1)
                if st.form_submit_button("Tuma Matokeo"):
                    c.execute("UPDATE matches SET home_score=?, away_score=?, status='Played' WHERE id=?", 
                              (h_goals, a_goals, match_id))
                    conn.commit()
                    st.success("Matokeo yameingizwa kwa ufanisi!")
                    st.rerun()
        else:
            st.write("Hakuna mechi zinazosubiri matokeo kwenye ligi hii.")
    conn.close()

elif choice == "📊 Matokeo ya Mechi":
    st.subheader("🏟️ Live Full Time Scores (Nani Kampa Kipigo Nani)")
    conn = sqlite3.connect('tinka_tech_v11.db')
    all_leagues = pd.read_sql("SELECT league_id FROM leagues", conn)
    
    if not all_leagues.empty:
        l_id = st.selectbox("Tazama Matokeo ya Ligi ya:", all_leagues['league_id'].tolist(), key="scores_select")
        c = conn.cursor()
        c.execute("SELECT home, away, home_score, away_score, stage FROM matches WHERE status = 'Played' AND league_id = ? ORDER BY id DESC", (l_id,))
        played_matches = c.fetchall()
        
        if played_matches:
            for m in played_matches:
                st.success(f"📌 **{m[4]}** ｜ {m[0]} **({m[2]})** — **({m[3]})** {m[1]}")
        else:
            st.info("Bado hakuna mechi zilizochezwa kwenye ligi hii.")
    conn.close()

elif choice == "📈 Msimamo wa Ligi (Tables)":
    st.subheader("📈 Jedwali la Msimamo wa Hatua ya Makundi")
    conn = sqlite3.connect('tinka_tech_v11.db')
    all_leagues = pd.read_sql("SELECT league_id FROM leagues", conn)
    
    if not all_leagues.empty:
        l_id = st.selectbox("Tazama Msimamo wa Ligi ya:", all_leagues['league_id'].tolist(), key="tables_select")
        c = conn.cursor()
        
        for g_name in ["Kundi A", "Kundi B", "Kundi C", "Kundi D"]:
            c.execute("SELECT home, away, home_score, away_score FROM matches WHERE status = 'Played' AND league_id = ? AND stage = ?", (l_id, g_name))
            g_matches = c.fetchall()
            
            c.execute("SELECT DISTINCT home FROM matches WHERE league_id = ? AND stage = ?", (l_id, g_name))
            g_players_home = [r[0] for r in c.fetchall()]
            c.execute("SELECT DISTINCT away FROM matches WHERE league_id = ? AND stage = ?", (l_id, g_name))
            g_players_away = [r[0] for r in c.fetchall()]
            g_players = list(set(g_players_home + g_players_away))
            
            if g_players:
                st.markdown(f"#### 📊 {g_name}")
                sorted_standings = calculate_standings_helpers(g_matches)
                
                res_dict = {}
                for name, stats in sorted_standings:
                    res_dict[name] = stats
                    
                df_standings = pd.DataFrame.from_dict(res_dict, orient='index')
                st.dataframe(df_standings[['Pld', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']], use_container_width=True)
    conn.close()

# --- MENYU MPYA 1: MSIMAMO WA KNOCKOUTS & WALIOFUZU ---
elif choice == "🏆 Msimamo wa Knockouts & Waliofuzu":
    st.subheader("🏆 Uchambuzi wa Waliofuzu Hatua za Mtoano (Knockouts Progression)")
    conn = sqlite3.connect('tinka_tech_v11.db')
    all_leagues = pd.read_sql("SELECT league_id FROM leagues", conn)
    
    if not all_leagues.empty:
        l_id = st.selectbox("Chagua Msimu kuona Waliofuzu", all_leagues['league_id'].tolist(), key="knock_select")
        c = conn.cursor()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🚪 Kutoka Makundi kwenda Robo")
            for g in ["Kundi A", "Kundi B", "Kundi C", "Kundi D"]:
                c.execute("SELECT home, away, home_score, away_score FROM matches WHERE league_id=? AND stage=? AND status='Played'", (l_id, g))
                matches = c.fetchall()
                res = calculate_standings_helpers(matches)
                if len(res) >= 2:
                    st.write(f"**{g}:** 1. {res[0][0]} ✅ | 2. {res[1][0]} ✅")
                else:
                    st.write(f"**{g}:** *Inasubiri mechi ziishe...*")
                    
        with col2:
            st.markdown("### ⚡ Waliofuzu Nusu Fainali")
            w1 = get_match_winner(l_id, "Robo Fainali 1")
            w2 = get_match_winner(l_id, "Robo Fainali 2")
            w3 = get_match_winner(l_id, "Robo Fainali 3")
            w4 = get_match_winner(l_id, "Robo Fainali 4")
            if w1: st.success(f"Mshindi Robo 1: **{w1}** ➡️ Semi")
            if w2: st.success(f"Mshindi Robo 2: **{w2}** ➡️ Semi")
            if w3: st.success(f"Mshindi Robo 3: **{w3}** ➡️ Semi")
            if w4: st.success(f"Mshindi Robo 4: **{w4}** ➡️ Semi")
            
        with col3:
            st.markdown("### 👑 Fainali na Bingwa")
            f1 = get_match_winner(l_id, "Nusu Fainali 1")
            f2 = get_match_winner(l_id, "Nusu Fainali 2")
            champion = get_match_winner(l_id, "Fainali")
            if f1: st.info(f"Mshindi Semi 1: **{f1}** ➡️ Final")
            if f2: st.info(f"Mshindi Semi 2: **{f2}** ➡️ Final")
            if champion: st.balloons(); st.header(f"👑 BINGWA: {champion} 🏆")
    conn.close()

# --- MENYU MPYA 2: RATIBA KAMILI YA HATUA (FIXTURES WITH AUTOMATIC LABELS) ---
elif choice == "🗓️ Ratiba Kamili ya Hatua (Fixtures)":
    st.subheader("🗓️ Ratiba Zote za Mashindano na Hali ya Sasa")
    conn = sqlite3.connect('tinka_tech_v11.db')
    all_leagues = pd.read_sql("SELECT league_id FROM leagues", conn)
    
    if not all_leagues.empty:
        l_id = st.selectbox("Chagua Ligi kuona Ratiba", all_leagues['league_id'].tolist(), key="fixtures_page_select")
        c = conn.cursor()
        
        # Kugundua hatua ya sasa kiotomatiki
        c.execute("SELECT stage FROM matches WHERE league_id=? AND status='Pending' ORDER BY id ASC LIMIT 1", (l_id,))
        current_stage_row = c.fetchone()
        
        if current_stage_row:
            current_stage = current_stage_row[0]
            st.metric(label="🚨 HATUA INAYOENDELEA SASA", value=f"{current_stage.upper()}")
        else:
            st.info("Ligi hii haina mechi zinazosubiri kuchezwa kwa sasa au haijaanza.")
            
        st.markdown("---")
        # Kuonesha ratiba zilizogawanywa kwa makundi au hatua husika
        stages_in_db = ["Kundi A", "Kundi B", "Kundi C", "Kundi D", "Robo Fainali 1", "Robo Fainali 2", "Robo Fainali 3", "Robo Fainali 4", "Nusu Fainali 1", "Nusu Fainali 2", "Fainali"]
        for stg in stages_in_db:
            df_stg = pd.read_sql(f"SELECT home AS 'Nyumbani', away AS 'Ugenini', status AS 'Hali ya Mechi' FROM matches WHERE league_id={l_id} AND stage='{stg}'", conn)
            if not df_stg.empty:
                st.markdown(f"#### 🏟️ Ratiba ya - **{stg}**")
                st.table(df_stg)
    conn.close()

elif choice == "⚙️ Admin Hub":
    if 'admin_logged_in' not in st.session_state: st.session_state.admin_logged_in = False
    if not st.session_state.admin_logged_in:
        st.subheader("Tinka Tech Admin System")
        password = st.text_input("Ingiza Password ya Admin", type="password")
        if st.button("Ingia Admin Hub"):
            if password.strip() == "tinka2026": 
                st.session_state.admin_logged_in = True
                st.rerun()
            else: st.error("Password si sahihi!")
    else:
        st.success("Karibu Kwenye Control Panel, Msimamizi Mkuu!")
        if st.sidebar.button("🔒 Toka Admin (Logout)"):
            st.session_state.admin_logged_in = False
            st.rerun()
            
        # TAB SEPARATION ILIYOOMBEWA NA USER
        tab1, tab2, tab3 = st.tabs(["✅ 1. Hakiki Usajili (Verify)", "🤖 2. Panga Ratiba (Auto-Pilot)", "🔧 3. Lazimisha Matokeo & Funga"])
        
        with tab1:
            st.write("### Orodha ya Wachezaji wote waliojisajili (Verify Hub)")
            conn = sqlite3.connect('tinka_tech_v11.db')
            players_df = pd.read_sql("SELECT id, name, phone, payment_id, status, league_id FROM players ORDER BY id DESC", conn)
            if not players_df.empty:
                for idx, row in players_df.iterrows():
                    status_lbl = "🟢 Verified" if row['status'] == 'Verified' else "⏳ Pending"
                    col1, col2 = st.columns([3, 1])
                    col1.write(f"👤 **{row['name']}** | {row['phone']} | Ligi: {row['league_id']} | Hali: {status_lbl}")
                    if row['status'] == 'Pending':
                        if col2.button("Verify", key=f"v_hub_{row['id']}"):
                            c = conn.cursor()
                            c.execute("UPDATE players SET status='Verified' WHERE id=?", (row['id'],))
                            conn.commit()
                            st.rerun()
            conn.close()
            
        with tab2:
            st.write("### 🤖 Panga Ratiba Kiotomatiki (Flexibility & Auto-spawn)")
            conn = sqlite3.connect('tinka_tech_v11.db')
            c = conn.cursor()
            c.execute("SELECT league_id FROM leagues WHERE status='Active'")
            active_row = c.fetchone()
            
            if active_row:
                sel_league = active_row[0]
                c.execute("SELECT COUNT(*) FROM players WHERE league_id=? AND status='Verified'", (sel_league,))
                v_count = c.fetchone()[0]
                st.info(f"Ligi inayosajili sasa: Ligi {sel_league} | Wachezaji walio-Verify: {v_count}")
                
                c.execute("SELECT COUNT(*) FROM matches WHERE league_id=?", (sel_league,))
                has_matches = c.fetchone()[0]
                
                if has_matches == 0:
                    if st.button("🚀 PANGA RATIBA YA MAKUNDI (ROUND-ROBIN FLEX)"):
                        c.execute("SELECT name FROM players WHERE league_id=? AND status='Verified'", (sel_league,))
                        p_list = [r[0] for r in c.fetchall()]
                        
                        # Inatengeneza makundi kiotomatiki kutokana na idadi yoyote ile iliyopo
                        if len(p_list) >= 16:
                            groups = {"Kundi A": p_list[0:4], "Kundi B": p_list[4:8], "Kundi C": p_list[8:12], "Kundi D": p_list[12:16]}
                            for g_name, g_players in groups.items():
                                for p in itertools.combinations(g_players, 2):
                                    c.execute("INSERT INTO matches (league_id, home, away, home_score, away_score, stage, status) VALUES (?, ?, ?, 0, 0, ?, 'Pending')", (sel_league, p[0], p[1], g_name))
                        else:
                            # Kama wachezaji ni wachache kuliko 16, wanacheza wote kundi moja la Round-Robin flex!
                            for p in itertools.combinations(p_list, 2):
                                c.execute("INSERT INTO matches (league_id, home, away, home_score, away_score, stage, status) VALUES (?, ?, ?, 0, 0, 'Kundi A', 'Pending')", (sel_league, p[0], p[1]))
                        
                        # AUTO-SPAWN LOGIC
                        c.execute("UPDATE leagues SET status='Playing' WHERE league_id=?", (sel_league,))
                        c.execute("INSERT INTO leagues (league_id, winner, status) VALUES (?, '', 'Active')", (sel_league + 1,))
                        conn.commit()
                        st.success("Ratiba imezalishwa na Ligi Mpya ya usajili imefunguliwa!")
                        st.rerun()
                else:
                    # Logic ya kuendeleza Hatua za Mtoano (Knockouts generation)
                    c.execute("SELECT COUNT(*) FROM matches WHERE league_id=? AND stage LIKE 'Kundi %' AND status='Pending'", (sel_league,))
                    pending_g = c.fetchone()[0]
                    c.execute("SELECT COUNT(*) FROM matches WHERE league_id=? AND stage LIKE 'Robo %'", (sel_league,))
                    robo_ex = c.fetchone()[0]
                    
                    if pending_g == 0 and robo_ex == 0:
                     
