import streamlit as st
import sqlite3
import pandas as pd

# --- 1. ALGORITHM ZA NDANI (HELPERS) KWA AJILI YA AUTOMATION ---
def calculate_standings_helpers(played_matches):
    standings = {}
    for m in played_matches:
        home, away, h_score, a_score = m[0], m[1], m[2], m[3]
        if home not in standings: standings[home] = {'Pts':0, 'GD':0, 'GF':0}
        if away not in standings: standings[away] = {'Pts':0, 'GD':0, 'GF':0}
        
        standings[home]['GF'] += h_score
        standings[home]['GD'] += (h_score - a_score)
        standings[away]['GF'] += a_score
        standings[away]['GD'] += (a_score - h_score)
        
        if h_score > a_score:
            standings[home]['Pts'] += 3
        elif h_score < a_score:
            standings[away]['Pts'] += 3
        else:
            standings[home]['Pts'] += 1
            standings[away]['Pts'] += 1
    sorted_teams = sorted(standings.items(), key=lambda x: (x[1]['Pts'], x[1]['GD'], x[1]['GF']), reverse=True)
    return [team[0] for team in sorted_teams]

def get_match_winner(league_id, stage_name):
    conn = sqlite3.connect('tinka_tech_v5.db')
    c = conn.cursor()
    c.execute("SELECT home, away, home_score, away_score FROM matches WHERE league_id=? AND stage=? AND status='Played'", (league_id, stage_name))
    res = c.fetchone()
    conn.close()
    if res:
        home, away, h_score, a_score = res
        if h_score > a_score: return home
        else: return away
    return None

# --- 2. DATABASE SETUP (V5) ---
def init_db():
    conn = sqlite3.connect('tinka_tech_v5.db')
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
st.set_page_config(page_title="Tinka Tech League", layout="wide")
st.title("🏆 TINKA TECH LEAGUE 🎮")

# Hapa tumetenganisha kabisa Matokeo na Msimamo kuwa menu tofauti kama ulivyoomba
menu = [
    "🏠 Home & Sheria", 
    "📝 Jisajili Hapa", 
    "📅 Ratiba & Mawasiliano", 
    "⚽ Tuma Matokeo", 
    "📊 Matokeo ya Mechi", 
    "📈 Msimamo wa Ligi (Tables)", 
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
        * **Usajili wa Msimu:** Kila ligi inajaza wachezaji 16 pekee.
        * **Hatua ya Makundi:** Wachezaji 16 wanagawanywa kwenye makundi 4 (A, B, C, D) kiotomatiki.
        * **Kufuzu Robo Fainali:** Wachezaji 2 wa juu (Top 2) kila kundi wanaenda hatua ya mtoano hadi Fainali.
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
                conn = sqlite3.connect('tinka_tech_v5.db')
                c = conn.cursor()
                c.execute("SELECT league_id, status FROM leagues ORDER BY league_id DESC LIMIT 1")
                last_league = c.fetchone()
                
                if last_league:
                    l_id, l_status = last_league[0], last_league[1]
                    c.execute("SELECT COUNT(*) FROM players WHERE league_id=?", (l_id,))
                    player_count = c.fetchone()[0]
                    if l_status == 'Completed' or player_count >= 16:
                        current_league = l_id + 1
                        c.execute("INSERT INTO leagues (league_id, winner, status) VALUES (?, '', 'Active')", (current_league,))
                        conn.commit()
                    else:
                        current_league = l_id
                else:
                    current_league = 1
                    c.execute("INSERT INTO leagues (league_id, winner, status) VALUES (1, '', 'Active')")
                    conn.commit()
                
                c.execute('INSERT INTO players (league_id, name, phone, payment_id, status) VALUES (?, ?, ?, ?, ?)', 
                          (current_league, name, phone, pay_id, "Pending"))
                conn.commit()
                conn.close()
                st.success(f"Hongera {name}! Umesajiliwa kwenye **LIGI NAMBA {current_league}**.")
            else:
                st.error("Tafadhali jaza nafasi zote vizuri.")

elif choice == "📅 Ratiba & Mawasiliano":
    st.subheader("Ratiba za Mechi na Mawasiliano ya Wachezaji")
    conn = sqlite3.connect('tinka_tech_v5.db')
    active_leagues = pd.read_sql("SELECT league_id FROM leagues WHERE status='Active'", conn)
    if not active_leagues.empty:
        l_id = st.selectbox("Chagua Ligi kuona Ratiba", active_leagues['league_id'].tolist())
        st.markdown("### 📅 Mechi Zinazofuata (Zinajifuta Zikichezwa Zenyewe)")
        df_fixtures = pd.read_sql(f"SELECT stage AS 'Hatua/Kundi', home AS 'Nyumbani', away AS 'Ugenini' FROM matches WHERE status = 'Pending' AND league_id = {l_id}", conn)
        if not df_fixtures.empty:
            st.table(df_fixtures)
        else:
            st.info("Hakuna ratiba ya mechi zinazosubiri kuchezwa kwa sasa.")
            
        st.markdown("---")
        st.markdown("### 📞 Orodha ya Simu za Wachezaji")
        df_contacts = pd.read_sql(f"SELECT name AS 'Jina la Game', phone AS 'Namba ya Simu' FROM players WHERE status='Verified' AND league_id={l_id}", conn)
        if not df_contacts.empty:
            st.dataframe(df_contacts, use_container_width=True)
    conn.close()

elif choice == "⚽ Tuma Matokeo":
    st.subheader("Sehemu ya Wachezaji Kuingiza Matokeo (Self-Submission)")
    conn = sqlite3.connect('tinka_tech_v5.db')
    active_leagues = pd.read_sql("SELECT league_id FROM leagues WHERE status='Active'", conn)
    
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
                    st.success("Matokeo yameingizwa na msimamo umejihuisha!")
                    st.rerun()
        else:
            st.write("Hakuna mechi zinazosubiri matokeo kwenye ligi hii.")
    conn.close()

elif choice == "📊 Matokeo ya Mechi":
    # MENU HII NI KWA AJILI YA KUONYESHA FULL TIME SCORES TU KAMA ULIVYOOMBA
    st.subheader("🏟️ Live Full Time Scores (Nani Kampa Kipigo Nani)")
    conn = sqlite3.connect('tinka_tech_v5.db')
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
    # MENU MAALUMU YA RATING TABLES INAYOFANYA KAZI AUTOMATICALLY
    st.subheader("📈 Jedwali la Msimamo (League Standings Tables)")
    conn = sqlite3.connect('tinka_tech_v5.db')
    
    st.markdown("### 🏆 UKUTA WA MABINGWA (HALL OF FAME)")
    df_winners = pd.read_sql("SELECT league_id AS 'Msimu/Ligi', winner AS 'Bingwa wa Taji' FROM leagues WHERE status='Completed'", conn)
    if not df_winners.empty: st.dataframe(df_winners, use_container_width=True)
    else: st.write("*Bado hakuna bingwa wa kihistoria aliyepatikana.*")
    
    st.markdown("---")
    all_leagues = pd.read_sql("SELECT league_id FROM leagues", conn)
    if not all_leagues.empty:
        l_id = st.selectbox("Tazama Msimamo wa Ligi ya:", all_leagues['league_id'].tolist(), key="tables_select")
        c = conn.cursor()
        
        for g_name in ["Kundi A", "Kundi B", "Kundi C", "Kundi D"]:
            st.markdown(f"#### 📊 {g_name}")
            c.execute("SELECT home, away, home_score, away_score FROM matches WHERE status = 'Played' AND league_id = ? AND stage = ?", (l_id, g_name))
            g_matches = c.fetchall()
            
            c.execute("SELECT DISTINCT home FROM matches WHERE league_id = ? AND stage = ?", (l_id, g_name))
            g_players_home = [r[0] for r in c.fetchall()]
            c.execute("SELECT DISTINCT away FROM matches WHERE league_id = ? AND stage = ?", (l_id, g_name))
            g_players_away = [r[0] for r in c.fetchall()]
            g_players = list(set(g_players_home + g_players_away))
            
            if g_players:
                standings = {p: {'Pld':0, 'W':0, 'D':0, 'L':0, 'GF':0, 'GA':0, 'GD':0, 'Pts':0} for p in g_players}
                for m in g_matches:
                    home, away, h_score, a_score = m[0], m[1], m[2], m[3]
                    standings[home]['Pld'] += 1
                    standings[away]['Pld'] += 1
                    standings[home]['GF'] += h_score
                    standings[home]['GA'] += a_score
                    standings[away]['GF'] += a_score
                    standings[away]['GA'] += h_score
                    
                    if h_score > a_score:
                        standings[home]['W'] += 1; standings[home]['Pts'] += 3; standings[away]['L'] += 1
                    elif h_score < a_score:
                        standings[away]['W'] += 1; standings[away]['Pts'] += 3; standings[home]['L'] += 1
                    else:
                        standings[home]['D'] += 1; standings[away]['D'] += 1; standings[home]['Pts'] += 1; standings[away]['Pts'] += 1
                        
                for team in standings:
                    standings[team]['GD'] = standings[team]['GF'] - standings[team]['GA']
                    
                df_standings = pd.DataFrame.from_dict(standings, orient='index')
                df_standings.index.name = 'Mchezaji'
                df_standings = df_standings.sort_values(by=['Pts', 'GD', 'GF'], ascending=[False, False, False])
                st.dataframe(df_standings, use_container_width=True)
            else:
                st.write("*Ratiba ya kundi hili bado haijazalishwa na Admin.*")
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
        st.success("Karibu Kwenye Control Panel, Msimamizi!")
        if st.sidebar.button("🔒 Toka Admin (Logout)"):
            st.session_state.admin_logged_in = False
            st.rerun()
            
        tab1, tab2, tab3, tab4 = st.tabs(["✅ Hakiki Wachezaji", "🤖 Kusimamia Ratiba (Auto-Pilot)", "🔧 Lazimisha Matokeo", "🔒 Funga Ligi & Tangaza Bingwa"])
        
        with tab1:
            conn = sqlite3.connect('tinka_tech_v5.db')
            pending = pd.read_sql("SELECT * FROM players WHERE status = 'Pending'", conn)
            if not pending.empty:
                for index, row in pending.iterrows():
                    col1, col2 = st.columns([3, 1])
                    col1.write(f"👤 **{row['name']}** (Ligi {row['league_id']}) | 📞 {row['phone']} | 💵 Muamala: **{row['payment_id']}**")
                    if col2.button("Verify", key=f"v_{row['id']}"):
                        c = conn.cursor()
                        c.execute("UPDATE players SET status = 'Verified' WHERE id = ?", (row['id'],))
                        conn.commit(); st.success(f"{row['name']} amethibitishwa!"); st.rerun()
            else: st.write("Hakuna maombi mapya yanayosubiri uhakiki.")
            conn.close()

        with tab2:
            st.write("### 📅 Mfumo wa Kutoa Ratiba Kiotomatiki (Auto-Pilot)")
            conn = sqlite3.connect('tinka_tech_v5.db')
            c = conn.cursor()
            leagues_df = pd.read_sql("SELECT league_id, status FROM leagues", conn)
            if not leagues_df.empty:
                sel_league = st.selectbox("Chagua Ligi ya Kusimamia Ratiba", leagues_df['league_id'].tolist())
                c.execute("SELECT COUNT(*) FROM players WHERE league_id=? AND status='Verified'", (sel_league,))
                verified_count = c.fetchone()[0]
                st.info(f"Wachezaji waliothibitishwa Ligi {sel_league}: **{verified_count} / 16**")
                
                c.execute("SELECT COUNT(*) FROM matches WHERE league_id=?", (sel_league,))
                total_matches = c.fetchone()[0]
                
                if total_matches == 0:
                    if verified_count < 16: st.warning("⚠️ Ratiba haiwezi kupangwa hadi watu 16 wathibitishwe.")
                    else:
                        st.success("✅ Wachezaji 16 wamekamilika!")
                        if st.button("🚀 Panga Ratiba ya Makundi Kiotomatiki"):
                            c.execute("SELECT name FROM players WHERE league_id=? AND status='Verified'", (sel_league,))
                            players = [r[0] for r in c.fetchall()]
                            groups = {"Kundi A": players[0:4], "Kundi B": players[4:8], "Kundi C": players[8:12], "Kundi D": players[12:16]}
                            for g_name, g_players in groups.items():
                                pairs = [(0,1), (2,3), (0,2), (1,3), (0,3), (1,2)]
                                for p in pairs:
                                    c.execute("INSERT INTO matches (league_id, home, away, home_score, away_score, stage, status) VALUES (?, ?, ?, 0, 0, ?, 'Pending')",
                                              (sel_league, g_players[p[0]], g_players[p[1]], g_name))
                            conn.commit(); st.success("Ratiba ya Makundi imepangwa!"); st.rerun()
                else:
                    c.execute("SELECT COUNT(*) FROM matches WHERE league_id=? AND stage LIKE 'Kundi %' AND status='Pending'", (sel_league,))
                    pending_groups = c.fetchone()[0]
                    c.execute("SELECT COUNT(*) FROM matches WHERE league_id=? AND stage LIKE 'Robo Fainali %'", (sel_league,))
                    robo_exists = c.fetchone()[0]
                    
                    if pending_groups > 0: st.warning(f"⏳ Hatua ya Makundi inaendelea. Mechi {pending_groups} bado hazijachezwa.")
                    elif pending_groups == 0 and robo_exists == 0:
                        st.success("🎉 Mechi zote za Makundi zimeisha!")
                        if st.button("🚀 Panga Mechi za Robo Fainali"):
                            def get_top_2(g_name):
                                c.execute("SELECT home, away, home_score, away_score FROM matches WHERE league_id=? AND stage=? AND status='Played'", (sel_league, g_name))
                                return calculate_standings_helpers(c.fetchall())
                            top_A, top_B, top_C, top_D = get_top_2("Kundi A"), get_top_2("Kundi B"), get_top_2("Kundi C"), get_top_2("Kundi D")
                            if len(top_A)>=2 and len(top_B)>=2 and len(top_C)>=2 and len(top_D)>=2:
                                c.execute("INSERT INTO matches (league_id, home, away, home_score, away_score, stage, status) VALUES (?, ?, ?, 0, 0, 'Robo Fainali 1', 'Pending')", (sel_league, top_A[0], top_B[1]))
                                c.execute("INSERT INTO matches (league_id, home, away, home_score, away_score, stage, status) VALUES (?, ?, ?, 0, 0, 'Robo Fainali 2', 'Pending')", (sel_league, top_B[0], top_A[1]))
                                c.execute("INSERT INTO matches (league_id, home, away, home_score, away_score, stage, status) VALUES (?, ?, ?, 0, 0, 'Robo Fainali 3', 'Pending')", (sel_league, top_C[0], top_D[1]))
                                c.execute("INSERT INTO matches (league_id, home, away, home_score, away_score, stage, status) VALUES (?, ?, ?, 0, 0, 'Robo Fainali 4', 'Pending')", (sel_league, top_D[0], top_C[1]))
                                conn.commit(); st.success("Robo Fainali imepangwa!"); st.rerun()
                    else:
                        c.execute("SELECT COUNT(*) FROM matches WHERE league_id=? AND stage LIKE 'Robo Fainali %' AND status='Pending'", (sel_league,))
                        pending_robo = c.fetchone()[0]
                        c.execute("SELECT COUNT(*) FROM matches WHERE league_id=? AND stage LIKE 'Nusu Fainali %'", (sel_league,))
                        nusu_exists = c.fetchone()[0]
                        
                        if pending_robo > 0: st.warning(f"⏳ Robo Fainali inaendelea. Mechi {pending_robo} bado hazijachezwa.")
                        elif pending_robo == 0 and nusu_exists == 0:
                            if st.button("🚀 Panga Mechi za Nusu Fainali"):
                                w1, w2, w3, w4 = get_match_winner(sel_league, "Robo Fainali 1"), get_match_winner(sel_league, "Robo Fainali 2"), get_match_winner(sel_league, "Robo Fainali 3"), get_match_winner(sel_league, "Robo Fainali 4")
                                if w1 and w2 and w3 and w4:
                                    c.execute("INSERT INTO matches (league_id, home, away, home_score, away_score, stage, status) VALUES (?, ?, ?, 0, 0, 'Nusu Fainali 1', 'Pending')", (sel_league, w1, w3))
                                    c.execute("INSERT INTO matches (league_id, home, away, home_score, away_score, stage, status) VALUES (?, ?, ?, 0, 0, 'Nusu Fainali 2', 'Pending')", (sel_league, w2, w4))
                                    conn.commit(); st.success("Nusu Fainali imepangwa!"); st.rerun()
                        else:
                            c.execute("SELECT COUNT(*) FROM matches WHERE league_id=? AND stage LIKE 'Nusu Fainali %' AND status='Pending'", (sel_league,))
                            pending_nusu = c.fetchone()[0]
                            c.execute("SELECT COUNT(*) FROM matches WHERE league_id=? AND stage='Fainali'", (sel_league,))
                            fainali_exists = c.fetchone()[0]
                            
                            if pending_nusu > 0: st.warning(f"⏳ Nusu Fainali inaendelea. Mechi {pending_nusu} bado hazijachezwa.")
                            elif pending_nusu == 0 and fainali_exists == 0:
                                if st.button("🚀 Panga Mechi ya Fainali"):
                                    wn1, wn2 = get_match_winner(sel_league, "Nusu Fainali 1"), get_match_winner(sel_league, "Nusu Fainali 2")
                                    if wn1 and wn2:
                                        c.execute("INSERT INTO matches (league_id, home, away, home_score, away_score, stage, status) VALUES (?, ?, ?, 0, 0, 'Fainali', 'Pending')", (sel_league, wn1, wn2))
                                        conn.commit(); st.success("Fainali Kuu imepangwa!"); st.rerun()
                            else:
                                c.execute("SELECT COUNT(*) FROM matches WHERE league_id=? AND stage='Fainali' AND status='Played'", (sel_league,))
                                if c.fetchone()[0] > 0:
                                    st.balloons(); st.success(f"🏆 Ligi {sel_league} imekamilika! Bingwa: **{get_match_winner(sel_league, 'Fainali')}**")
            conn.close()

        with tab3:
            conn = sqlite3.connect('tinka_tech_v5.db')
            pending_matches = pd.read_sql("SELECT id, league_id, home, away, stage FROM matches WHERE status = 'Pending'", conn)
            if not pending_matches.empty:
                for index, row in pending_matches.iterrows():
                    with st.expander(f"Ligi {row['league_id']} | {row['home']} VS {row['away']} ({row['stage']})"):
                        with st.form(f"admin_res_{row['id']}"):
                            h_goals = st.number_input(f"Magoli {row['home']}", min_value=0, step=1)
                            a_goals = st.number_input(f"Magoli {row['away']}", min_value=0, step=1)
                            if st.form_submit_button("Over-ride Matokeo"):
                                c = conn.cursor()
                                c.execute("UPDATE matches SET home_score=?, away_score=?, status='Played' WHERE id=?", (h_goals, a_goals, row['id']))
                                conn.commit(); st.success("Matokeo yamelazimishwa!"); st.rerun()
            else: st.write("Hakuna mechi zinazosubiri matokeo.")
            conn.close()

        with tab4:
            st.write("### 🔒 Funga Ligi na Kuanzisha Msimu Mpya")
            conn = sqlite3.connect('tinka_tech_v5.db')
            active_leagues = pd.read_sql("SELECT league_id FROM leagues WHERE status='Active'", conn)
            if not active_leagues.empty:
                league_to_close = st.selectbox("Chagua Ligi ya Kufunga Rasmi", active_leagues['league_id'].tolist())
                winner_name = st.text_input("Ingiza Jina la Bingwa (Winner)")
                if st.button("Funga Msimu 🏆"):
                    if winner_name:
                        c = conn.cursor()
                        c.execute("UPDATE leagues SET winner=?, status='Completed' WHERE league_id=?", (winner_name, league_to_close))
                        c.execute("INSERT INTO leagues (league_id, winner, status) VALUES (?, '', 'Active')", (league_to_close + 1,))
                        conn.commit(); st.success("Ligi imefungwa!"); st.rerun()
                    else: st.error("Andika jina la Bingwa kwanza.")
            conn.close()
