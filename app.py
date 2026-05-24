import streamlit as st
import sqlite3
import pandas as pd

# --- 1. DATABASE SETUP (V3) ---
def init_db():
    conn = sqlite3.connect('tinka_tech_v3.db')
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

# --- 2. MUONEKANO (UI LAYOUT) ---
st.set_page_config(page_title="Tinka Tech League", layout="wide")
st.title("🏆 TINKA TECH LEAGUE 🎮")

menu = ["🏠 Home & Sheria", "📝 Jisajili Hapa", "📅 Ratiba & Mawasiliano", "⚽ Tuma Matokeo", "📊 Matokeo & Msimamo", "⚙️ Admin Hub"]
choice = st.sidebar.selectbox("Chagua Menyu", menu)

# --- 3. LOGIC YA KILA UKURASA ---

if choice == "🏠 Home & Sheria":
    st.header("Karibu Tinka Tech eFootball Hub")
    st.write("Mfumo thabiti wa kiotomatiki unaoendesha mashindano ya eFootball kuanzia usajili hadi kutwaa taji.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚙️ Sheria za Michezo (Gameplay Rules)")
        st.warning("""
        * **Control:** Full Human Controlled (Ni marufuku kutumia AI au kuachia simu).
        * **Smart Assist:** NO Smart Assist (Imezuiwa kabisa, hakikisha imezimwa).
        * **Muda wa Mechi:** Dakika 10 (Muda rasmi wa uwanjani).
        * **Hatua ya Makundi:** Hakuna Extra Time wala Penati. Mechi inaweza kuisha kwa Droo.
        * **Hatua ya Mtoano (Knockouts):** Lazima mshindi apatikane. Extra Time na Penati zinaruhusiwa hapa tu.
        """)
        
    with col2:
        st.markdown("### 🏆 Mfumo wa Mashindano na Ubingwa")
        st.info("""
        * **Usajili wa Msimu:** Kila ligi inajaza wachezaji 16 pekee. Ikishajaa au msimu ukiisha, mfumo unafungua msimu mpya.
        * **Waliotoka/Wapya:** Ukipoteza au ukitolewa hatua za mwanzo, unaruhusiwa kulipia upya na kujisajili kwenye Ligi mpya inayofuata!
        * **Hatua ya Makundi:** Wachezaji 16 wanagawanywa kwenye makundi 4 (A, B, C, D). Kila mchezaji anacheza mechi 3 dhidi ya watu wa kundi lake.
        * **Kufuzu Robo Fainali:** Wachezaji 2 wa juu (Top 2) kila kundi wanaenda hatua ya mtoano hadi Fainali kupigania Taji.
        """)

    st.markdown("### 💵 Jinsi ya Kushiriki")
    st.success("Tuma kiingilio cha **TZS 1,000** kwenda namba **0792460625**. Baada ya hapo, nenda kwenye tab ya 'Jisajili Hapa' kukamilisha usajili wako.")

elif choice == "📝 Jisajili Hapa":
    st.subheader("Fomu ya Usajili wa Ligi ya Sasa")
    
    with st.form("reg_form"):
        name = st.text_input("Jina lako la Kwenye Game (In-Game Name)")
        phone = st.text_input("Namba yako ya Simu")
        pay_id = st.text_input("Namba ya Muamala (Transaction ID)")
        submitted = st.form_submit_button("Tuma Maombi")
        
        if submitted:
            if name and pay_id and phone:
                conn = sqlite3.connect('tinka_tech_v3.db')
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
                st.success(f"Hongera {name}! Umesajiliwa kwenye **LIGI NAMBA {current_league}**. Subiri Admin athibitishe malipo yako.")
            else:
                st.error("Tafadhali jaza nafasi zote vizuri.")

elif choice == "📅 Ratiba & Mawasiliano":
    st.subheader("Ratiba za Mechi na Mawasiliano ya Wachezaji")
    conn = sqlite3.connect('tinka_tech_v3.db')
    
    active_leagues = pd.read_sql("SELECT league_id FROM leagues WHERE status='Active'", conn)
    if not active_leagues.empty:
        l_id = st.selectbox("Chagua Ligi kuona Ratiba", active_leagues['league_id'].tolist())
        
        st.markdown("### 📅 Mechi Zinazofufuata zilizopangwa")
        df_fixtures = pd.read_sql(f"SELECT home AS 'Nyumbani', away AS 'Ugenini', stage AS 'Hatua/Kundi' FROM matches WHERE status = 'Pending' AND league_id = {l_id}", conn)
        if not df_fixtures.empty:
            st.table(df_fixtures)
        else:
            st.info("Hakuna ratiba mpya iliyopangwa kwenye ligi hii kwa sasa.")
            
        st.markdown("---")
        st.markdown("### 📞 Orodha ya Simu za Wachezaji (Tafuta mpinzani wako hapa)")
        df_contacts = pd.read_sql(f"SELECT name AS 'Jina la Game', phone AS 'Namba ya Simu' FROM players WHERE status='Verified' AND league_id={l_id}", conn)
        if not df_contacts.empty:
            st.dataframe(df_contacts, use_container_width=True)
        else:
            st.write("Bado hakuna wachezaji waliothibitishwa katika ligi hii.")
    else:
        st.info("Hakuna ligi inayoendelea kwa sasa. Subiri msimu ufunguliwe.")
    conn.close()

elif choice == "⚽ Tuma Matokeo":
    st.subheader("Sehemu ya Wachezaji Kuingiza Matokeo (Self-Submission)")
    st.info("Ilani: Ni mchezaji aliyeshinda (au aliyetoa droo nyumbani) anayepaswa kuingiza matokeo haya ili kuepuka vurugu.")
    
    conn = sqlite3.connect('tinka_tech_v3.db')
    active_leagues = pd.read_sql("SELECT league_id FROM leagues WHERE status='Active'", conn)
    
    if not active_leagues.empty:
        l_id = st.selectbox("Chagua Ligi Unayocheza", active_leagues['league_id'].tolist())
        
        c = conn.cursor()
        c.execute("SELECT id, home, away, stage FROM matches WHERE status='Pending' AND league_id=?", (l_id,))
        pending_list = c.fetchall()
        
        if pending_list:
            match_options = {f"{m[1]} VS {m[2]} ({m[3]})": m[0] for m in pending_list}
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
                    st.success(f"Matokeo ya {match_data[0]} ({h_goals}) - ({a_goals}) {match_data[1]} yameingizwa na msimamo umejihuisha!")
                    st.rerun()
        else:
            st.write("Hakuna mechi zinazosubiri matokeo kwenye ligi hii.")
    else:
        st.info("Hakuna ligi inayofanya kazi kwa sasa.")
    conn.close()

elif choice == "📊 Matokeo & Msimamo":
    conn = sqlite3.connect('tinka_tech_v3.db')
    
    st.markdown("## 🏆 UKUTA WA MABINGWA (HALL OF FAME)")
    df_winners = pd.read_sql("SELECT league_id AS 'Msimu/Ligi', winner AS 'Mfalme wa Taji/Bingwa' FROM leagues WHERE status='Completed'", conn)
    if not df_winners.empty:
        st.dataframe(df_winners, use_container_width=True)
    else:
        st.write("Msimu wa kwanza ndio unaanza, hakuna bingwa wa kihistoria bado!")
    st.markdown("---")
    
    all_leagues = pd.read_sql("SELECT league_id FROM leagues", conn)
    if not all_leagues.empty:
        l_id = st.selectbox("Tazama Msimamo na Matokeo ya Ligi ya:", all_leagues['league_id'].tolist())
        
        st.subheader(f"Live Scores: Ligi {l_id} ⚽")
        c = conn.cursor()
        c.execute("SELECT home, away, home_score, away_score, stage FROM matches WHERE status = 'Played' AND league_id = ?", (l_id,))
        played_matches = c.fetchall()
        
        if played_matches:
            for m in played_matches:
                st.success(f"**{m[0]} ({m[2]}) - ({m[3]}) {m[1]}** | *Hatua: {m[4]}*")
                
            st.markdown("---")
            st.subheader(f"📈 Msimamo wa Ligi (League Table) - Ligi {l_id}")
            
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
            st.info("Hakuna mechi zilizochezwa bado kwenye ligi hii.")
    conn.close()

# --- ⚙️ ADMIN HUB ILYOBORESHWA (LOGIN UPDATE) ---
elif choice == "⚙️ Admin Hub":
    # 1. Hakikisha state ya login ipo
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False

    # 2. Kama haja-log in, onyesha fomu ya kuingia
    if not st.session_state.admin_logged_in:
        st.subheader("Tinka Tech Admin System")
        password = st.text_input("Ingiza Password ya Admin", type="password")
        
        if st.button("Ingia Admin Hub"):
            # .strip() inafuta space zote za makosa mwanzo au mwisho wa neno
            if password.strip() == "tinka2026": 
                st.session_state.admin_logged_in = True
                st.success("Umeingia vizuri!")
                st.rerun()
            else:
                st.error("Password si sahihi! Hakikisha herufi zote ni ndogo.")
                
    # 3. Kama amesha-log in, mfungulie panel rasmi bila mizinguo ya password
    else:
        st.success("Karibu Msimamizi Mkuu!")
        
        # Kitufe cha kutoka (Logout) kikwekwa pembeni ili kurudi uraiani
        if st.sidebar.button("🔒 Toka Admin (Logout)"):
            st.session_state.admin_logged_in = False
            st.rerun()
            
        tab1, tab2, tab3, tab4 = st.tabs(["✅ Hakiki Wachezaji", "📅 Panga Ratiba", "🔧 Lazimisha Matokeo", "🔒 Funga Ligi & Tangaza Bingwa"])
        
        # TAB 1: VERIFICATION
        with tab1:
            conn = sqlite3.connect('tinka_tech_v3.db')
            pending = pd.read_sql("SELECT * FROM players WHERE status = 'Pending'", conn)
            if not pending.empty:
                for index, row in pending.iterrows():
                    col1, col2 = st.columns([3, 1])
                    col1.write(f"👤 **{row['name']}** (Ligi {row['league_id']}) | 📞 {row['phone']} | 💵 SMS: **{row['payment_id']}**")
                    if col2.button("Verify", key=f"v_{row['id']}"):
                        c = conn.cursor()
                        c.execute("UPDATE players SET status = 'Verified' WHERE id = ?", (row['id'],))
                        conn.commit()
                        st.success(f"{row['name']} amethibitishwa!")
                        st.rerun()
            else:
                st.write("Hakuna maombi mapya ya usajili.")
            conn.close()

        # TAB 2: FIXTURES
        with tab2:
            with st.form("fixture_form"):
                league_id = st.number_input("Namba ya Ligi", min_value=1, step=1)
                home_team = st.text_input("Mchezaji wa Nyumbani")
                away_team = st.text_input("Mchezaji wa Ugenini")
                stage = st.text_input("Kundi / Hatua (Mfano: Kundi A, Fainali)")
                if st.form_submit_button("Hifadhi Ratiba"):
                    conn = sqlite3.connect('tinka_tech_v3.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO matches (league_id, home, away, home_score, away_score, stage, status) VALUES (?, ?, ?, 0, 0, ?, 'Pending')", 
                              (league_id, home_team, away_team, stage))
                    conn.commit()
                    conn.close()
                    st.success("Ratiba imepandishwa uwanjani!")

        # TAB 3: ADMIN OVERRIDE
        with tab3:
            conn = sqlite3.connect('tinka_tech_v3.db')
            pending_matches = pd.read_sql("SELECT id, league_id, home, away, stage FROM matches WHERE status = 'Pending'", conn)
            if not pending_matches.empty:
                for index, row in pending_matches.iterrows():
                    with st.expander(f"Ligi {row['league_id']} | {row['home']} VS {row['away']} ({row['stage']})"):
                        with st.form(f"admin_res_{row['id']}"):
                            h_goals = st.number_input(f"Magoli {row['home']}", min_value=0, step=1)
                            a_goals = st.number_input(f"Magoli {row['away']}", min_value=0, step=1)
                            if st.form_submit_button("Over-ride Matokeo"):
                                c = conn.cursor()
                                c.execute("UPDATE matches SET home_score=?, away_score=?, status='Played' WHERE id=?", 
                                          (h_goals, a_goals, row['id']))
                                conn.commit()
                                st.success("Matokeo yamelazimishwa vizuri!")
                                st.rerun()
            else:
                st.write("Hakuna mechi zinazosubiri matokeo.")
            conn.close()

        # TAB 4: FUNGA LIGI
        with tab4:
            st.write("### 🔒 Funga Ligi na Kuanzisha Msimu Mpya")
            st.warning("Ukifunga ligi hii, wachezaji wakijisajili upya wataingizwa kwenye ligi mpya inayofuata kiotomatiki.")
            
            conn = sqlite3.connect('tinka_tech_v3.db')
            active_leagues = pd.read_sql("SELECT league_id FROM leagues WHERE status='Active'", conn)
            
            if not active_leagues.empty:
                league_to_close = st.selectbox("Chagua Ligi ya Kufunga Rasmi", active_leagues['league_id'].tolist())
                winner_name = st.text_input("Ingiza Jina la Mchezaji Aliyetwaa Ubingwa (Winner)")
                
                if st.button("Funga Msimu na Tangaza Bingwa 🏆"):
                    if winner_name:
                        c = conn.cursor()
                        c.execute("UPDATE leagues SET winner=?, status='Completed' WHERE league_id=?", (winner_name, league_to_close))
                        next_league = league_to_close + 1
                        c.execute("INSERT INTO leagues (league_id, winner, status) VALUES (?, '', 'Active')", (next_league,))
                        conn.commit()
                        st.success(f"Ligi {league_to_close} imefungwa rasmi! {winner_name} amewekwa kwenye Ukuta wa Mabingwa. Ligi Namba {next_league} imefunguliwa kwa usajili mpya!")
                        st.rerun()
                    else:
                        st.error("Tafadhali andika jina la Bingwa kwanza kabla ya kufunga msimu.")
            else:
                st.write("Hakuna ligi inayoendelea kwa sasa.")
            conn.close()
