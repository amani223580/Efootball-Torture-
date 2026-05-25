import streamlit as st
import sqlite3
import pandas as pd
import itertools

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

# --- 2. DATABASE SETUP (V10) ---
def init_db():
    conn = sqlite3.connect('tinka_tech_v10.db')
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
st.set_page_config(page_title="Tinka Tech League V10", layout="wide")
st.title("🏆 TINKA TECH LEAGUE V10 🎮")

# Menyu zote 7 zimerudi kama zilivyokuwa awali
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
        * **Matokeo:** Hakikisha mnaingiza matokeo sahihi ili kulinda uaminifu wa ligi wetu.
        """)
    with col2:
        st.markdown("### 🏆 Mfumo wa Mashindano na Ubingwa")
        st.info("""
        * **Usajili wa Msimu:** Ligi inaruhusu idadi yoyote inayonyumbuka ya wachezaji (6, 8, 16, 20 n.k.).
        * **Ratiba Maalumu:** Mfumo unazalisha ratiba ambapo kila mtu anacheza na kila mchezaji mwingine kwenye ligi.
        * **Bingwa:** Mchezaji anayeongoza kwa pointi na magoli baada ya mechi zote kuisha anatawazwa kuwa mshindi rasmi.
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
                conn = sqlite3.connect('tinka_tech_v10.db')
                c = conn.cursor()
                c.execute("SELECT league_id FROM leagues WHERE status='Active' ORDER BY league_id DESC LIMIT 1")
                active_league_row = c.fetchone()
                
                if active_league_row:
                    current_league = active_league_row[0]
                else:
                    current_league = 1
                    c.execute("INSERT INTO leagues (league_id, winner, status) VALUES (1, '', 'Active')")
                    conn.commit()
                
                c.execute('INSERT INTO players (league_id, name, phone, payment_id, status) VALUES (?, ?, ?, ?, ?)', 
                          (current_league, name, phone, pay_id, "Pending"))
                conn.commit()
                conn.close()
                st.success(f"Hongera {name}! Ombi lako limesajiliwa kwenye **LIGI NAMBA {current_league}**. Subiri uhakiki wa Admin.")
            else:
                st.error("Tafadhali jaza nafasi zote vizuri.")

elif choice == "📅 Ratiba & Mawasiliano":
    st.subheader("Ratiba za Mechi na Mawasiliano ya Wachezaji")
    conn = sqlite3.connect('tinka_tech_v10.db')
    all_leagues = pd.read_sql("SELECT league_id FROM leagues", conn)
    if not all_leagues.empty:
        l_id = st.selectbox("Chagua Ligi kuona Ratiba", all_leagues['league_id'].tolist())
        st.markdown("### 📅 Mechi Zinazofuata (Zinajifuta Zikichezwa Zenyewe)")
        df_fixtures = pd.read_sql(f"SELECT stage AS 'Hatua/Kundi', home AS 'Nyumbani', away AS 'Ugenini' FROM matches WHERE status = 'Pending' AND league_id = {l_id}", conn)
        if not df_fixtures.empty:
            st.table(df_fixtures)
        else:
            st.info("Hakuna ratiba ya mechi zinazosubiri kuchezwa kwa sasa.")
            
        st.markdown("---")
        st.markdown("### 📞 Orodha ya Simu za Wachezaji walio-Verify")
        df_contacts = pd.read_sql(f"SELECT name AS 'Jina la Game', phone AS 'Namba ya Simu' FROM players WHERE status='Verified' AND league_id={l_id}", conn)
        if not df_contacts.empty:
            st.dataframe(df_contacts, use_container_width=True)
        else:
            st.info("Bado hakuna wachezaji waliothibitishwa katika ligi hii.")
    conn.close()

elif choice == "⚽ Tuma Matokeo":
    st.subheader("Sehemu ya Wachezaji Kuingiza Matokeo (Self-Submission)")
    conn = sqlite3.connect('tinka_tech_v10.db')
    active_leagues = pd.read_sql("SELECT league_id FROM leagues WHERE status='Playing' OR status='Active'", conn)
    
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
                    st.success("Matokeo yameingizwa na msimamo umejihuisha kwa mafanikio!")
                    st.rerun()
        else:
            st.write("Hakuna mechi zinazosubiri matokeo kwenye ligi hii kwa sasa.")
    conn.close()

elif choice == "📊 Matokeo ya Mechi":
    st.subheader("🏟️ Live Full Time Scores (Nani Kampa Kipigo Nani)")
    conn = sqlite3.connect('tinka_tech_v10.db')
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
    st.subheader("📈 Jedwali la Msimamo (League Standings Tables)")
    conn = sqlite3.connect('tinka_tech_v10.db')
    
    st.markdown("### 🏆 UKUTA WA MABINGWA (HALL OF FAME)")
    df_winners = pd.read_sql("SELECT league_id AS 'Msimu/Ligi', winner AS 'Bingwa wa Taji' FROM leagues WHERE status='Completed'", conn)
    if not df_winners.empty: 
        st.dataframe(df_winners, use_container_width=True)
    else: 
        st.write("*Bado hakuna bingwa wa kihistoria aliyepatikana.*")
    
    st.markdown("---")
    all_leagues = pd.read_sql("SELECT league_id FROM leagues", conn)
    if not all_leagues.empty:
        l_id = st.selectbox("Tazama Msimamo wa Ligi ya:", all_leagues['league_id'].tolist(), key="tables_select")
        c = conn.cursor()
        
        st.markdown(f"#### 📊 Msimamo Mkuu wa Ligi - Msimu {l_id}")
        c.execute("SELECT home, away, home_score, away_score FROM matches WHERE status = 'Played' AND league_id = ?", (l_id,))
        g_matches = c.fetchall()
        
        c.execute("SELECT DISTINCT name FROM players WHERE league_id = ? AND status = 'Verified'", (l_id,))
        g_players = [r[0] for r in c.fetchall()]
        
        if g_players:
            standings = {p: {'Pld':0, 'W':0, 'D':0, 'L':0, 'GF':0, 'GA':0, 'GD':0, 'Pts':0} for p in g_players}
            for m in g_matches:
                home, away, h_score, a_score = m[0], m[1], m[2], m[3]
                if home in standings and away in standings:
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
            df_standings.index.name = 'Mchezaji (In-Game Name)'
            df_standings = df_standings.sort_values(by=['Pts', 'GD', 'GF'], ascending=[False, False, False])
            st.dataframe(df_standings, use_container_width=True)
        else:
            st.write("*Bado hakuna wachezaji kwenye ligi hii au ratiba haijatengenezwa.*")
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
            
        # TAB SEPARATION ILIYOBORESHWA KIKAMILIFU
        tab1, tab2, tab3 = st.tabs(["✅ 1. Hakiki Usajili (Verify Players)", "🤖 2. Panga Ratiba (Auto-Pilot)", "🔒 3. Funga Ligi & Tangaza Bingwa"])
        
        with tab1:
            st.write("### 👥 Wachezaji Wote Waliojisajili na Hali zao")
            conn = sqlite3.connect('tinka_tech_v10.db')
            players_df = pd.read_sql("SELECT id, league_id, name, phone, payment_id, status FROM players ORDER BY id DESC", conn)
            
            if not players_df.empty:
                for index, row in players_df.iterrows():
                    status_color = "🟢 Verified" if row['status'] == 'Verified' else "⏳ Pending"
                    col1, col2 = st.columns([3, 1])
                    col1.markdown(f"👤 **{row['name']}** | 📞 {row['phone']} | 💵 Muamala: `{row['payment_id']}` | Ligi: {row['league_id']} | Hali: **{status_color}**")
                    
                    if row['status'] == 'Pending':
                        if col2.button("Verify", key=f"v_{row['id']}"):
                            c = conn.cursor()
                            c.execute("UPDATE players SET status = 'Verified' WHERE id = ?", (row['id'],))
                            conn.commit()
                            st.success(f"{row['name']} amethibitishwa papo hapo!")
                            st.rerun()
            else:
                st.write("Hakuna mchezaji aliyesajiliwa kwenye database kwa sasa.")
            conn.close()

        with tab2:
            st.write("### 📅 Mfumo wa Kutoa Ratiba Maalumu (Round-Robin Auto-Pilot)")
            conn = sqlite3.connect('tinka_tech_v10.db')
            c = conn.cursor()
            c.execute("SELECT league_id FROM leagues WHERE status='Active' ORDER BY league_id ASC LIMIT 1")
            active_row = c.fetchone()
            
            if active_row:
                sel_league = active_row[0]
                c.execute("SELECT COUNT(*) FROM players WHERE league_id=? AND status='Verified'", (sel_league,))
                verified_count = c.fetchone()[0]
                
                st.info(f"Msimu wa sasa unaoandaliwa: **LIGI NAMBA {sel_league}**")
                st.write(f"Idadi ya wachezaji walio-Verify kwa sasa: **{verified_count}**")
                
                if verified_count < 2:
                    st.warning("⚠️ Unahitaji angalau wachezaji 2 waliothibitishwa ili kutengeneza ratiba.")
                else:
                    st.success(f"✅ Tayari una wachezaji {verified_count}! Unaweza kuzalisha ratiba sasa.")
                    if st.button("🚀 PANGA RATIBA YA MZUNGUKO (ROUND-ROBIN)"):
                        c.execute("SELECT name FROM players WHERE league_id=? AND status='Verified'", (sel_league,))
                        players_list = [r[0] for r in c.fetchall()]
                        
                        # FLEXIBILITY ALGORITHM: Inazalisha jozi kamili za mechi kwa idadi yoyote (6, 8, 20 n.k)
                        pairs = list(itertools.combinations(players_list, 2))
                        for p in pairs:
                            c.execute("INSERT INTO matches (league_id, home, away, home_score, away_score, stage, status) VALUES (?, ?, ?, 0, 0, 'Ligi Kuu', 'Pending')",
                                      (sel_league, p[0], p[1]))
                        
                        # AUTO-SPAWN LOGIC: Inafunga hatua ya usajili ya ligi hii na kufungua mpya kiotomatiki
                        c.execute("UPDATE leagues SET status='Playing' WHERE league_id=?", (sel_league,))
                        c.execute("INSERT INTO leagues (league_id, winner, status) VALUES (?, '', 'Active')", (sel_league + 1,))
                        conn.commit()
                        st.success(f"🎉 Ratiba ya Ligi {sel_league} imepangwa na Mechi {len(pairs)} zimezalishwa! Ligi ya Usajili {sel_league + 1} imefunguliwa kiotomatiki.")
                        st.rerun()
            else:
                st.write("Hakuna ligi changamfu ya kusajili. Tafadhali anzisha kwenye mfumo.")
            conn.close()

        with tab3:
            st.write("### 🔒 Funga Msimu na Tangaza Bingwa")
            conn = sqlite3.connect('tinka_tech_v10.db')
            c = conn.cursor()
            playing_leagues = pd.read_sql("SELECT league_id FROM leagues WHERE status='Playing'", conn)
            
            if not playing_leagues.empty:
                l_to_close = st.selectbox("Chagua Ligi ya Kufunga", playing_leagues['league_id'].tolist())
                
                # Inatafuta mchezaji anayeongoza kwa kutumia helper function
                c.execute("SELECT home, away, home_score, away_score FROM matches WHERE status='Played' AND league_id=?", (l_to_close,))
                matches_played = c.fetchall()
                
                if matches_played:
                    leaderboard = calculate_standings_helpers(matches_played)
                    if leaderboard:
                        top_player = leaderboard[0]
                        st.success(f"Mchezaji anayeongoza kwa sasa na anayestahili taji: **{top_player}**")
                        
                        if st.button("🏆 Funga Ligi Rasmi na Mpe Ubingwa"):
                            c.execute("UPDATE leagues SET winner=?, status='Completed' WHERE league_id=?", (top_player, l_to_close))
                            conn.commit()
                            st.success(f"Ligi {l_to_close} imefungwa rasmi! {top_player} ameingizwa kwenye Ukuta wa Mabingwa!")
                            st.rerun()
                else:
                    st.warning("Ligi hii haina mechi hata moja iliyochezwa bado ili kupata mshindi.")
            else:
                st.write("Hakuna ligi inayochezwa kwa sasa inayoweza kufungwa.")
            conn.close()
        
