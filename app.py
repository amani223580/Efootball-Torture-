import streamlit as st
import sqlite3
import pandas as pd

# Database Initialization
def init_db():
    conn = sqlite3.connect('tinka_tech.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS players 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, payment_id TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS matches 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, home TEXT, away TEXT, home_score INTEGER, away_score INTEGER, group_name TEXT)''')
    conn.commit()
    conn.close()

init_db()

st.title("🏆 TINKA TECH LEAGUE 🎮")

# Sidebar kwa navigation
menu = ["🏠 Home & Sheria", "📝 Jisajili", "📊 Matokeo", "⚙️ Admin"]
choice = st.sidebar.selectbox("Chagua Menyu", menu)

# 1. TAB: HOME & SHERIA
if choice == "🏠 Home & Sheria":
    st.header("Karibu Tinka Tech League")
    st.write("Mfumo rasmi wa kusimamia mashindano ya eFootball.")
    
    with st.expander("📖 Jinsi ya kutumia mfumo"):
        st.write("1. Nenda kwenye menyu ya 'Jisajili'.")
        st.write("2. Lipia ada ya 1000 TZS kupitia 0792460625.")
        st.write("3. Jaza fomu na namba ya muamala (Transaction ID).")
        st.write("4. Subiri Admin aku-verify ili uweze kushiriki.")
    
    with st.expander("⚖️ Kanuni na Sheria"):
        st.write("- Mchezaji anapaswa kuwa na mtandao mzuri.")
        st.write("- Matokeo yanayotumwa ni yale ya dakika 90.")
        st.write("- Udanganyifu wowote utapelekea kufungiwa.")

# 2. TAB: USAJILI
elif choice == "📝 Jisajili":
    st.subheader("Fomu ya Usajili")
    with st.form("reg_form"):
        name = st.text_input("Jina kamili")
        phone = st.text_input("Namba ya simu")
        pay_id = st.text_input("Namba ya Muamala")
        submitted = st.form_submit_button("Sajili")
        
        if submitted:
            conn = sqlite3.connect('tinka_tech.db')
            c = conn.cursor()
            c.execute('INSERT INTO players (name, phone, payment_id, status) VALUES (?, ?, ?, ?)', 
                      (name, phone, pay_id, "Pending"))
            conn.commit()
            conn.close()
            st.success("Usajili umepokelewa! Admin ataufanyia kazi.")

# 3. TAB: MATOKEO
elif choice == "📊 Matokeo":
    st.subheader("Msimamo na Matokeo")
    conn = sqlite3.connect('tinka_tech.db')
    df = pd.read_sql("SELECT * FROM players WHERE status = 'Verified'", conn)
    st.write("Wachezaji Walioidhinishwa:", df[['name', 'status']])
    conn.close()

# 4. TAB: ADMIN (PASSWORD PROTECTED)
elif choice == "⚙️ Admin":
    password = st.text_input("Ingiza Admin Password", type="password")
    if password == "1234": # BADILI PASSWORD HAPA
        st.subheader("Admin Dashboard")
        
        # Tab za Admin
        admin_tab1, admin_tab2 = st.tabs(["Uthibitishaji", "Weka Matokeo"])
        
        with admin_tab1:
            conn = sqlite3.connect('tinka_tech.db')
            pending_players = pd.read_sql("SELECT * FROM players WHERE status = 'Pending'", conn)
            
            if not pending_players.empty:
                for index, row in pending_players.iterrows():
                    st.write(f"Mchezaji: {row['name']} | Muamala: {row['payment_id']}")
                    if st.button(f"Verify {row['name']}", key=f"btn_{row['id']}"):
                        c = conn.cursor()
                        c.execute("UPDATE players SET status = 'Verified' WHERE id = ?", (row['id'],))
                        conn.commit()
                        st.success(f"{row['name']} amethibitishwa!")
                        st.rerun()
            else:
                st.write("Hakuna maombi mapya.")
            conn.close()

        with admin_tab2:
            with st.form("match_form"):
                h = st.text_input("Home Team")
                a = st.text_input("Away Team")
                hs = st.number_input("Goli Home", 0)
                ascore = st.number_input("Goli Away", 0)
                if st.form_submit_button("Hifadhi"):
                    conn = sqlite3.connect('tinka_tech.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO matches (home, away, home_score, away_score) VALUES (?,?,?,?)", (h,a,hs,ascore))
                    conn.commit()
                    conn.close()
                    st.success("Matokeo yameingia!")
    else:
        st.error("Password si sahihi!")
    
