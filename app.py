import streamlit as st
import pandas as pd
import yaml
import sqlite3
from datetime import datetime, date, timedelta
import plotly.express as px
import json
import os

# -----------------------------
# Config
# -----------------------------
st.set_page_config(
    page_title="Dheeraj's Fitness Tracker",
    page_icon="icon.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB_PATH = "fitness_tracker.db"
WORKOUTS_YAML = "workouts.yaml"

DAY_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

# -----------------------------
# Styling (Apple Health 2026 - Premium Light)
# -----------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg-color: #F2F2F7; /* iOS System Gray 6 */
    --card-bg: #FFFFFF;
    --text-primary: #000000;
    --text-secondary: #3A3A3C; /* Darker gray for better visibility */
    --accent: #007AFF; /* iOS Blue */
    --shadow: 0 4px 12px rgba(0,0,0,0.05);
}

/* GLOBAL RESET & TEXT VISIBILITY FIX */
.stApp {
    background-color: var(--bg-color);
    font-family: 'Inter', -apple-system, sans-serif;
}

/* Force ALL standard text to be dark, overriding Dark Mode defaults */
p, li, .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, label, .stDataFrame {
    color: var(--text-primary) !important;
}
.stCaption {
    color: var(--text-secondary) !important;
}

h1 { font-size: 2.2rem !important; margin-bottom: 0.5rem !important;}
h2 { font-size: 1.6rem !important; }
h3 { font-size: 1.25rem !important; }

/* NAVBAR / HEADER BRANDING */
.brand {
    background: var(--card-bg);
    padding: 24px;
    border-radius: 20px;
    box-shadow: var(--shadow);
    margin-bottom: 24px;
    border: none;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.brand h1 { margin: 0; font-size: 1.6rem !important; color: #000 !important; }
.brand .sub { color: var(--text-secondary); font-size: 0.9rem; font-weight: 500; margin-top: 4px; }
.pill {
    background: #000; color: #fff;
    padding: 6px 14px;
    border-radius: 100px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* CARDS */
.card {
    background: var(--card-bg);
    border-radius: 16px;
    padding: 24px;
    box-shadow: var(--shadow);
    border: none;
    margin-bottom: 16px;
}
.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    margin: 32px 0 16px 0;
    color: var(--text-primary);
}

/* TILES (Apple Health Summary Style) */
.metric-grid {
    display: grid; 
    grid-template-columns: repeat(2, 1fr); 
    gap: 16px;
}
@media (min-width: 768px) {
    .metric-grid { grid-template-columns: repeat(4, 1fr); }
}

.metric-tile {
    background: var(--card-bg);
    border-radius: 16px;
    padding: 20px;
    box-shadow: var(--shadow);
    display: flex; flex-direction: column;
    transition: transform 0.2s;
}
.metric-tile:hover { transform: translateY(-2px); }

.metric-tile .label {
    font-size: 0.8rem;
    font-weight: 600;
    color: #FF2D55; /* Health Pink/Red vibe */
    text-transform: uppercase;
    margin-bottom: 8px;
    display: flex; align-items: center; gap: 6px;
}
.metric-tile .value {
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--text-primary);
}
.metric-tile .hint {
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--text-secondary);
    margin-top: 4px;
}

/* BUTTONS (iOS Filled Style) */
.stButton button {
    background: #000000 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 24px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}
.stButton button:hover {
    background: #333333 !important;
    transform: scale(1.01);
}

/* INPUTS (iOS Form Style) */
/* Force input backgrounds to light gray and text to black */
input, .stNumberInput input, .stTextInput input, .stSelectbox, .stDateInput {
    color: #000000 !important;
}
div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
    background-color: #E5E5EA !important; /* iOS Input Gray */
    border: none !important;
    border-radius: 10px !important;
    color: #000 !important;
}
/* Fix the +/- buttons on number inputs to look cleaner */
button[kind="secondary"] {
    background: transparent !important;
    border: none !important;
    color: #000 !important;
}

/* TABS (Segmented Control Look) */
.stTabs [data-baseweb="tab-list"] {
    background-color: transparent;
    border-bottom: none;
    gap: 8px;
    padding-bottom: 12px;
}
.stTabs [data-baseweb="tab"] {
    background-color: var(--card-bg);
    border-radius: 20px;
    padding: 8px 16px;
    border: 1px solid rgba(0,0,0,0.05);
    font-weight: 600;
    color: var(--text-secondary);
    box-shadow: 0 2px 4px rgba(0,0,0,0.03);
}
.stTabs [aria-selected="true"] {
    background-color: #000;
}
.stTabs [aria-selected="true"] p, 
.stTabs [aria-selected="true"] span {
    color: #FFFFFF !important; /* Force inner text to white */
}

</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------
# Helpers
# -----------------------------
def load_workouts():
    if not os.path.exists(WORKOUTS_YAML):
        st.error(f"Missing {WORKOUTS_YAML}. Make sure it's in the repo root.")
        st.stop()
    with open(WORKOUTS_YAML, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_today_day_name():
    return datetime.now().strftime("%A")

def normalize_day(day):
    return day if day in DAY_ORDER else "Monday"

def connect_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def init_db():
    conn = connect_db()
    cur = conn.cursor()
    # Ensure tables
    for q in [
        "CREATE TABLE IF NOT EXISTS workout_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, log_date TEXT, day_name TEXT, exercise_name TEXT, planned_sets TEXT, planned_reps TEXT, actual_sets INTEGER, actual_reps INTEGER, weight REAL, skipped INTEGER, notes TEXT)",
        "CREATE TABLE IF NOT EXISTS custom_exercises (id INTEGER PRIMARY KEY AUTOINCREMENT, log_date TEXT, day_name TEXT, exercise_name TEXT, actual_sets INTEGER, actual_reps INTEGER, weight REAL, notes TEXT)",
        "CREATE TABLE IF NOT EXISTS sports_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, log_date TEXT, sport_name TEXT, minutes INTEGER, intensity TEXT, notes TEXT)",
        "CREATE TABLE IF NOT EXISTS body_metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, log_date TEXT, weight REAL, body_fat REAL, lean_mass REAL, muscle_mass REAL, water_mass REAL, notes TEXT)"
    ]:
        cur.execute(q)
    conn.commit()
    conn.close()

def fetch_logs(conn, start_date=None, end_date=None):
    q = "SELECT log_date, day_name, exercise_name, actual_sets, actual_reps, weight, skipped, notes FROM workout_logs"
    params = []
    if start_date and end_date:
        q += " WHERE log_date BETWEEN ? AND ?"
        params = [start_date, end_date]
    q += " ORDER BY log_date DESC"
    return pd.read_sql_query(q, conn, params=params)

def fetch_custom(conn, start_date=None, end_date=None):
    q = "SELECT log_date, day_name, exercise_name, actual_sets, actual_reps, weight, notes FROM custom_exercises"
    params = []
    if start_date and end_date:
        q += " WHERE log_date BETWEEN ? AND ?"
        params = [start_date, end_date]
    q += " ORDER BY log_date DESC"
    return pd.read_sql_query(q, conn, params=params)

def fetch_sports(conn, start_date=None, end_date=None):
    q = "SELECT log_date, sport_name, minutes, intensity, notes FROM sports_logs"
    params = []
    if start_date and end_date:
        q += " WHERE log_date BETWEEN ? AND ?"
        params = [start_date, end_date]
    q += " ORDER BY log_date DESC"
    return pd.read_sql_query(q, conn, params=params)

def fetch_metrics(conn):
    q = "SELECT log_date, weight, body_fat, lean_mass, muscle_mass, water_mass, notes FROM body_metrics ORDER BY log_date DESC"
    return pd.read_sql_query(q, conn)

def week_range(d: date):
    start = d - timedelta(days=d.weekday())
    end = start + timedelta(days=6)
    return start, end

def calc_week_score(df_logs, df_custom, df_sports, week_start, week_end):
    score = 0
    if df_logs is not None and not df_logs.empty:
        tmp = df_logs.copy()
        tmp["log_date"] = pd.to_datetime(tmp["log_date"]).dt.date
        tmp = tmp[(tmp["log_date"] >= week_start) & (tmp["log_date"] <= week_end)]
        if not tmp.empty:
            score += len(tmp[tmp["skipped"] == 0]) * 2
    if df_custom is not None and not df_custom.empty:
        tmpc = df_custom.copy()
        tmpc["log_date"] = pd.to_datetime(tmpc["log_date"]).dt.date
        tmpc = tmpc[(tmpc["log_date"] >= week_start) & (tmpc["log_date"] <= week_end)]
        score += len(tmpc)
    sport_points = 0
    if df_sports is not None and not df_sports.empty:
        tmps = df_sports.copy()
        tmps["log_date"] = pd.to_datetime(tmps["log_date"]).dt.date
        tmps = tmps[(tmps["log_date"] >= week_start) & (tmps["log_date"] <= week_end)]
        if not tmps.empty:
            total = tmps["minutes"].fillna(0).sum()
            sport_points = min(6, int(total // 20))
            score += sport_points
    return score, sport_points

# -----------------------------
# App Init
# -----------------------------
init_db()
data = load_workouts()
app_name = data.get("app", {}).get("name", "Dheeraj's Fitness Tracker")
phase = data.get("app", {}).get("phase", "")
notes = data.get("app", {}).get("notes", [])

today = date.today()
today_day_name = normalize_day(get_today_day_name())

# -----------------------------
# Header
# -----------------------------
st.markdown(
    f"""
    <div class="brand">
      <div>
        <h1>{app_name}</h1>
        <div class="sub">{phase} • {today_day_name}, {today.strftime("%d %b %Y")}</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Tabs
# -----------------------------
tabs = st.tabs(["Dashboard", "Workout", "Plan", "Progress", "Nutrition", "Recovery", "Settings"])
(tab_home, tab_workout, tab_plan, tab_progress, tab_nutrition, tab_recovery, tab_settings) = tabs

# -----------------------------
# HOME TAB
# -----------------------------
with tab_home:
    conn = connect_db()
    df_metrics = fetch_metrics(conn)
    df_logs = fetch_logs(conn)
    df_custom = fetch_custom(conn)
    df_sports = fetch_sports(conn)
    conn.close()

    week_start, week_end = week_range(today)
    score, sport_points = calc_week_score(df_logs, df_custom, df_sports, week_start, week_end)
    latest = df_metrics.iloc[0] if df_metrics is not None and not df_metrics.empty else None

    ST_Snapshot = st.container()
    
    with ST_Snapshot:
        st.markdown('<div class="section-title">Current Snapshot</div>', unsafe_allow_html=True)
        # Use python string join to avoid indentation whitespace issues
        tiles_content = ""
        tiles_data = [
             ("Weekly Score", f"{score}", f"Goal: Consistency"),
             ("Sports Points", f"{sport_points}", "Max 6/week"),
             ("Today", today_day_name, "Focus Mode"),
             ("Phase", "1", "Rebuild")
        ]
        if latest is not None:
             tiles_data = [
                 ("Weekly Score", f"{score}", f"{week_start.strftime('%d %b')} - {week_end.strftime('%d %b')}"),
                 ("Weight", f"{latest['weight']:.1f} kg" if pd.notna(latest["weight"]) else "—", "Latest reading"),
                 ("Body Fat", f"{latest['body_fat']:.1f}%" if pd.notna(latest["body_fat"]) else "—", "Target: Lean"),
                 ("Lean Mass", f"{latest['lean_mass']:.1f} kg" if pd.notna(latest["lean_mass"]) else "—", "Growth"),
             ]

        for label, val, hint in tiles_data:
            tiles_content += f'<div class="metric-tile"><div class="label">{label}</div><div class="value">{val}</div><div class="hint">{hint}</div></div>'
        
        st.markdown(f'<div class="metric-grid">{tiles_content}</div>', unsafe_allow_html=True)

    st.write("")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="section-title">Coach Notes</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if notes:
            for n in notes:
                st.write(f"• {n}")
        else:
            st.write("• Consistency eats intensity for breakfast.")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-title">Recent Activity</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if df_logs is not None and not df_logs.empty:
            # Show last 3 valid logs
            recent = df_logs[df_logs["skipped"]==0].head(3)
            if recent.empty:
                 st.write("No logs yet.")
            else:
                 for i, row in recent.iterrows():
                     st.write(f"**{row['log_date']}**: {row['exercise_name']}")
        else:
            st.write("No logs yet. Start today!")
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# WORKOUT TAB
# -----------------------------
def fetch_last_log(conn, exercise_name):
    # Fetch the most recent log for this specific exercise
    q = """
    SELECT log_date, actual_sets, actual_reps, weight, notes 
    FROM workout_logs 
    WHERE exercise_name = ? AND skipped = 0
    ORDER BY log_date DESC 
    LIMIT 1
    """
    try:
        df = pd.read_sql_query(q, conn, params=[exercise_name])
        return df.iloc[0] if not df.empty else None
    except Exception:
        return None

with tab_workout:
    # 1. Day Selection
    day_options = DAY_ORDER
    try:
        default_index = day_options.index(today_day_name)
    except ValueError:
        default_index = 0
        
    selected_day = st.selectbox("Select Workout For:", day_options, index=default_index)
    
    # Load plan for Selected Day
    schedule = data.get("schedule", {})
    day_plan = schedule.get(selected_day, {})
    exercises = day_plan.get("exercises", [])
    
    st.markdown(f'<div class="section-title">Plan: {selected_day}</div>', unsafe_allow_html=True)
    st.info(f"**Focus:** {day_plan.get('focus','—')}  |  **Intensity:** {day_plan.get('intensity','—')}  |  **Core:** {day_plan.get('core','—')}")

    conn = connect_db() # Open connection once for history lookups

    if not exercises:
        st.write("No planned exercises for this day.")
    else:
        with st.form("log_form"):
            log_entries = []
            for i, ex in enumerate(exercises):
                ex_name = ex.get('name')
                
                # History Lookup
                last_log = fetch_last_log(conn, ex_name)
                history_str = "No history yet"
                if last_log is not None:
                    # Format: 2026-02-01: 3x10 @ 50.0kg (Note: ...)
                    w_str = f"{last_log['weight']}kg" if last_log['weight'] > 0 else "BW"
                    note_str = f" | 📝 {last_log['notes']}" if last_log['notes'] else ""
                    history_str = f"⏮️ **Last ({last_log['log_date']}):** {last_log['actual_sets']} sets x {last_log['actual_reps']} reps @ **{w_str}**{note_str}"

                st.markdown(f"### {i+1}. {ex_name}")
                st.caption(f"Target: {ex.get('sets')} x {ex.get('reps')} | {ex.get('notes','')}")
                
                # Display History clearly
                if last_log is not None:
                    st.markdown(f'<div style="background-color: #E5E5EA; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; font-size: 0.85rem; color: #3A3A3C;">{history_str}</div>', unsafe_allow_html=True)
                
                cA, cB, cC, cD = st.columns([1,1,1,1])
                with cA:
                    s = st.number_input("Sets", 0, 20, 0, key=f"s{i}")
                with cB:
                    r = st.number_input("Reps", 0, 200, 0, key=f"r{i}")
                with cC:
                    w = st.number_input("Kg", 0.0, 500.0, 0.0, step=0.5, key=f"w{i}")
                with cD:
                    # Spacer to align checkbox
                    st.write("")
                    st.write("") 
                    sk = st.checkbox("Skip", key=f"sk{i}")
                n = st.text_input("Notes (e.g. '15kgx10, 12kgx8')", key=f"n{i}", placeholder="Set details or feelings...")
                st.markdown("---")
                
                log_entries.append({
                    "name": ex_name, "pset": str(ex.get("sets")), "prep": str(ex.get("reps")),
                    "aset": s, "arep": r, "awt": w, "skip": sk, "note": n
                })
            
            # Additional Workouts (Expander for clean UI)
            with st.expander("➕ Add Extra / Custom Exercise", expanded=False):
                st.markdown("**Custom Additional Log**")
                cx_name = st.text_input("Exercise Name", placeholder="e.g. Burpees")
                c1, c2, c3 = st.columns(3)
                with c1: cx_s = st.number_input("Sets", 0, 20, 0, key="cx_s")
                with c2: cx_r = st.number_input("Reps", 0, 100, 0, key="cx_r")
                with c3: cx_w = st.number_input("Weight", 0.0, 500.0, 0.0, key="cx_w")
                cx_note = st.text_input("Custom Notes", key="cx_n")
            
            sub = st.form_submit_button("Save Workout")
            
            if sub:
                cur = conn.cursor()
                # 1. Save Planned
                for e in log_entries:
                    cur.execute("INSERT INTO workout_logs (log_date, day_name, exercise_name, planned_sets, planned_reps, actual_sets, actual_reps, weight, skipped, notes) VALUES (?,?,?,?,?,?,?,?,?,?)",
                               (today.isoformat(), selected_day, e["name"], e["pset"], e["prep"], e["aset"], e["arep"], e["awt"], 1 if e["skip"] else 0, e["note"]))
                # 2. Save Custom if entered
                if cx_name:
                    cur.execute("INSERT INTO custom_exercises (log_date, day_name, exercise_name, actual_sets, actual_reps, weight, notes) VALUES (?,?,?,?,?,?,?)",
                                (today.isoformat(), selected_day, cx_name, cx_s, cx_r, cx_w, cx_note))
                conn.commit()
                st.success(f"Logged workout for {selected_day}!")
                
    conn.close()

# -----------------------------
# PLAN TAB
# -----------------------------
with tab_plan:
    st.markdown('<div class="section-title">Weekly Schedule</div>', unsafe_allow_html=True)
    schedule = data.get("schedule", {})
    for d in DAY_ORDER:
        with st.expander(f"{d}: {schedule.get(d,{}).get('focus','Rest')}", expanded=(d==today_day_name)):
            p = schedule.get(d,{})
            st.write(f"Intensity: {p.get('intensity')} | Core: {p.get('core')}")
            df = pd.DataFrame(p.get("exercises",[]))
            if not df.empty:
                st.dataframe(df[["name","sets","reps","tempo"]], hide_index=True, use_container_width=True)

# -----------------------------
# PROGRESS TAB
# -----------------------------
# -----------------------------
# PROGRESS TAB (Enterprise Analytics)
# -----------------------------
with tab_progress:
    st.markdown('<div class="section-title">Analytics</div>', unsafe_allow_html=True)
    conn = connect_db()
    logs = fetch_logs(conn)
    metrics = fetch_metrics(conn)
    conn.close()
    
    if not logs.empty:
        # Data Prep
        logs["log_date"] = pd.to_datetime(logs["log_date"])
        logs["fmt_date"] = logs["log_date"].dt.strftime("%d-%b") # "04-Feb"
        
        # Aggregation
        daily = logs[logs["skipped"]==0].groupby("fmt_date", sort=False).size().reset_index(name="count")
        
        # Enterprise Grade Chart
        fig = px.bar(daily, x="fmt_date", y="count", 
                     title="<b>Workout Consistency</b>",
                     text="count")
        
        fig.update_traces(
            marker_color="#000000", # Minimalist Black
            marker_line_width=0,
            opacity=0.9,
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Workouts: %{y}<extra></extra>'
        )
        
        fig.update_layout(
            font_family="Inter",
            font_color="#000000",
            title_font_size=18,
            title_x=0, # Left align title like enterprise dashboards
            margin=dict(l=0, r=20, t=40, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=250,
            bargap=0.3,
            xaxis=dict(
                title=None,
                showgrid=False,
                linecolor="#E5E5EA",
                tickfont=dict(size=12, color="#8E8E93"),
                tickangle=0 # Keep labels horizontal if possible
            ),
            yaxis=dict(
                title=None,
                showgrid=True,
                gridcolor="#F2F2F7", # Very subtle grid
                showticklabels=False, # Clean look, since we have value labels on bars
                zeroline=False
            )
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Enterprise Stats Row
        c1, c2, c3 = st.columns(3)
        total_workouts = len(daily)
        total_exercises = len(logs[logs["skipped"]==0])
        consistency = f"{int((len(daily)/30)*100)}%" if len(daily) > 0 else "0%"
        
        with c1: st.metric("Active Days (30d)", total_workouts)
        with c2: st.metric("Total Exercises", total_exercises)
        with c3: st.metric("Consistency", consistency)

    else:
        st.info("Log some workouts to see analytics.")

    st.markdown("### Export Data")
    if st.button("Generate Backup JSON"):
        export = {
            "logs": logs.to_dict(orient="records"),
            "metrics": metrics.to_dict(orient="records")
        }
        st.download_button("Download JSON", json.dumps(export, default=str), "backup.json")

# -----------------------------
# NUTRITION & RECOVERY (Simplified)
# -----------------------------
with tab_nutrition:
    st.markdown('<div class="section-title">Nutrition</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">Daily Targets: Protein 2g/kg | Creatine 5g | Water 3L</div>', unsafe_allow_html=True)
    with st.form("nutri_log"):
        d = st.date_input("Date", today)
        cA, cB, cC = st.columns(3)
        with cA: p = st.number_input("Protein (g)", 0, 400)
        with cB: c = st.number_input("Carbs (g)", 0, 600)
        with cC: f = st.number_input("Fats (g)", 0, 200)
        st.form_submit_button("Log Macros")

with tab_recovery:
    st.markdown('<div class="section-title">Recovery Checklist</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
    - Sleep 7.5h+ <br>
    - Sauna (2x/week) <br>
    - Mobility (Sat)
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# SETTINGS
# -----------------------------
with tab_settings:
    st.markdown('<div class="section-title">Body Metrics</div>', unsafe_allow_html=True)
    with st.form("body_metrics"):
        w = st.number_input("Weight (kg)", 0.0, 200.0, step=0.1)
        bf = st.number_input("Body Fat %", 0.0, 50.0, step=0.1)
        if st.form_submit_button("Update"):
            conn = connect_db()
            conn.execute("INSERT INTO body_metrics (log_date, weight, body_fat) VALUES (?,?,?)", 
                        (date.today().isoformat(), w, bf))
            conn.commit()
            conn.close()
            st.success("Updated")

st.markdown('<div class="footer-hint">Dheeraj\'s Fitness Tracker • Light/Classy Theme</div>', unsafe_allow_html=True)
