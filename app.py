import sqlite3
import itertools

# --- 1. INITIALIZATION ---
def init_db():
    conn = sqlite3.connect('tinka_tech.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS leagues (id INTEGER PRIMARY KEY, status TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS players (id INTEGER PRIMARY KEY, league_id INTEGER, name TEXT, phone TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS matches (
                      match_id INTEGER PRIMARY KEY, 
                      league_id INTEGER, 
                      group_name TEXT, 
                      stage TEXT,
                      home_player_id INTEGER, 
                      away_player_id INTEGER, 
                      home_score INTEGER DEFAULT 0, 
                      away_score INTEGER DEFAULT 0, 
                      status TEXT DEFAULT 'Pending')''')
    conn.commit()
    conn.close()

# --- 2. LOGIC: Kupanga Mechi ---
def generate_fixtures(league_id):
    conn = sqlite3.connect('tinka_tech.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM players WHERE league_id = ?", (league_id,))
    players = [row[0] for row in cursor.fetchall()]
    
    groups = ['A', 'B', 'C', 'D']
    for i in range(0, 16, 4):
        group_players = players[i:i+4]
        group_name = groups[i//4]
        matches = list(itertools.combinations(group_players, 2))
        for p1, p2 in matches:
            cursor.execute('''INSERT INTO matches (league_id, group_name, stage, home_player_id, away_player_id, status) 
                              VALUES (?, ?, ?, ?, ?, ?)''', (league_id, group_name, 'Groups', p1, p2, 'Pending'))
    conn.commit()
    conn.close()

# --- 3. LOGIC: Usajili ---
def register_player(name, phone):
    conn = sqlite3.connect('tinka_tech.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM leagues ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    league_id = row[0] if row else 1

    cursor.execute("SELECT COUNT(*) FROM players WHERE league_id = ?", (league_id,))
    count = cursor.fetchone()[0]

    if count >= 16:
        league_id += 1
        cursor.execute("INSERT INTO leagues (id, status) VALUES (?, ?)", (league_id, 'Open'))
    
    cursor.execute("INSERT INTO players (league_id, name, phone) VALUES (?, ?, ?)", (league_id, name, phone))
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM players WHERE league_id = ?", (league_id,))
    if cursor.fetchone()[0] == 16:
        generate_fixtures(league_id)
        print(f"Ligi {league_id} imetimia! Mechi zimepangwa.")
    else:
        print(f"Mchezaji {name} amesajiliwa League {league_id}.")
            
    conn.close()

# --- 4. EXECUTION ---
if __name__ == "__main__":
    init_db()
    # Hapa ndipo unaweza kuongeza wachezaji wako
    # register_player("Juma", "0712345678")
def submit_result(match_id, home_score, away_score):
    conn = sqlite3.connect('tinka_tech.db')
    cursor = conn.cursor()
    
    # 1. Update matokeo kwenye mechi husika
    cursor.execute('''UPDATE matches 
                      SET home_score = ?, away_score = ?, status = 'Played' 
                      WHERE match_id = ?''', 
                   (home_score, away_score, match_id))
    
    conn.commit()
    conn.close()
    print(f"Matokeo ya mechi {match_id} yamesajiliwa: {home_score}-{away_score}! ✅")
def view_pending_matches():
    conn = sqlite3.connect('tinka_tech.db')
    cursor = conn.cursor()
    cursor.execute("SELECT match_id, home_player_id, away_player_id FROM matches WHERE status = 'Pending'")
    matches = cursor.fetchall()
    
    print("\n--- MECHI ZILIZOBAKI (Pending) ---")
    for m in matches:
        print(f"Match ID: {m[0]} | Mchezaji {m[1]} vs {m[2]}")
    conn.close()
# Hii ni sehemu ya test
# view_pending_matches()
# submit_result(1, 5, 2) # Mfano: mechi ya kwanza imetoka 5-2
def get_standings(league_id):
    conn = sqlite3.connect('tinka_tech.db')
    cursor = conn.cursor()
    
    # 1. Pata wachezaji wote wa hiyo ligi
    cursor.execute("SELECT id, name FROM players WHERE league_id = ?", (league_id,))
    players_db = cursor.fetchall()
    
    # 2. Tengeneza dictionary ya kuhifadhi stats
    stats = {p[0]: {'name': p[1], 'pts': 0, 'played': 0, 'won': 0, 'drawn': 0, 'lost': 0, 'gf': 0, 'ga': 0} for p in players_db}
    
    # 3. Pata mechi zote zilizochezwa
    cursor.execute("SELECT home_player_id, away_player_id, home_score, away_score FROM matches WHERE league_id = ? AND status = 'Played'", (league_id,))
    matches = cursor.fetchall()
    
    for h_id, a_id, h_score, a_score in matches:
        # Update stats kwa wachezaji wawili
        for p_id in [h_id, a_id]:
            stats[p_id]['played'] += 1
            stats[p_id]['gf'] += h_score if p_id == h_id else a_score
            stats[p_id]['ga'] += a_score if p_id == h_id else h_score
        
        # Calculate Points
        if h_score > a_score: # Home wins
            stats[h_id]['pts'] += 3
            stats[h_id]['won'] += 1
            stats[a_id]['lost'] += 1
        elif a_score > h_score: # Away wins
            stats[a_id]['pts'] += 3
            stats[a_id]['won'] += 1
            stats[h_id]['lost'] += 1
        else: # Draw
            stats[h_id]['pts'] += 1
            stats[a_id]['pts'] += 1
            stats[h_id]['drawn'] += 1
            stats[a_id]['drawn'] += 1
            
    conn.close()
    
    # 4. Badilisha iwe list na u-sort (Points, kisha Goal Diff)
    final_table = []
    for p_id, data in stats.items():
        data['gd'] = data['gf'] - data['ga']
        data['id'] = p_id
        final_table.append(data)
        
    return sorted(final_table, key=lambda x: (x['pts'], x['gd']), reverse=True)

# --- Jinsi ya ku-display matokeo ---
def print_table(league_id):
    standings = get_standings(league_id)
    print(f"\n--- MSIMAMO LIGI {league_id} ---")
    print(f"{'Jina':<15} | {'P':<3} | {'W':<3} | {'D':<3} | {'L':<3} | {'GF':<3} | {'GA':<3} | {'GD':<3} | {'PTS':<3}")
    for p in standings:
        print(f"{p['name']:<15} | {p['played']:<3} | {p['won']:<3} | {p['drawn']:<3} | {p['lost']:<3} | {p['gf']:<3} | {p['ga']:<3} | {p['gd']:<3} | {p['pts']:<3}")
if __name__ == "__main__":
    init_db()
    
    # Mfano: Kuonyesha msimamo wa League 1
    print_table(1)
    # Efootball-Torture-
The high cup
