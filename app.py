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
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB_PATH = "fitness_tracker.db"
WORKOUTS_YAML = "workouts.yaml"

DAY_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

# -----------------------------
# Styling (Classy, Light, Subtle)
# -----------------------------
# -----------------------------
# Styling (Mobile-First, High Contrast)
# -----------------------------
CUSTOM_CSS = """
<style>
/* 1. FORCE LIGHT THEME BASICS */
:root {
    --primary-color: #2563eb;
    --bg-color: #f9fafb;
    --card-bg: #ffffff;
    --text-color: #1f2937;
    --text-muted: #6b7280;
    --border-color: #e5e7eb;
}

/* Force entire app to light mode colors to prevent dark mode clashes */
.stApp {
  background-color: var(--bg-color);
  color: var(--text-color);
}

/* 2. TYPOGRAPHY SCALING (Mobile Friendly) */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 16px; /* Base size larger for mobile */
}

h1 { font-size: 1.75rem !important; font-weight: 700 !important; }
h2 { font-size: 1.5rem !important; font-weight: 600 !important; }
h3 { font-size: 1.25rem !important; font-weight: 600 !important; }
p, div, label { font-size: 1rem !important; }

/* 3. BUTTONS (Fixing Black-on-Black) */
.stButton button {
  width: 100%; /* Full width on mobile feels better */
  background-color: #ffffff !important;
  color: #111827 !important; /* Solid Black/Gray */
  border: 1px solid #d1d5db !important;
  border-radius: 12px !important;
  padding: 12px 20px !important; /* Larger touch target */
  font-size: 1rem !important;
  font-weight: 600 !important;
  margin-top: 10px;
}
.stButton button:hover, .stButton button:active {
  background-color: #f3f4f6 !important;
  border-color: #9ca3af !important;
  color: #000000 !important;
}
/* Primary Action Button (Submit) - Optional: Make it blue? Keeping it clean/white for classy look, but high contrast */

/* 4. CARDS & CONTAINERS */
.block-container {
  padding-top: 2rem !important;
  padding-bottom: 5rem !important; /* Space for bottom nav feel */
}

.brand {
  background: var(--card-bg);
  padding: 16px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  margin-bottom: 24px;
}
.card {
  background: var(--card-bg);
  padding: 20px;
  border-radius: 16px; /* softer corners */
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); /* subtle lift */
  margin-bottom: 16px;
}

/* 5. METRICS GRID (Mobile optimized) */
.metric-grid {
  display: grid; 
  grid-template-columns: repeat(2, 1fr); /* 2x2 on mobile is readable */
  gap: 12px;
}
@media (min-width: 768px) {
    .metric-grid { grid-template-columns: repeat(4, 1fr); }
}

.metric-tile {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  display: flex; flex-direction: column; justify-content: center;
}
.metric-tile .label {
  font-size: 0.75rem !important; 
  font-weight: 600; 
  color: var(--text-muted); 
  text-transform: uppercase;
}
.metric-tile .value {
  font-size: 1.5rem !important; 
  font-weight: 800; 
  color: #111827;
  margin: 4px 0;
}

/* 6. INPUTS (Larger text, better touch) */
div[data-baseweb="input"] input {
    font-size: 16px !important; /* Prevents iOS zoom on focus */
    color: #111827 !important;
    padding: 10px !important;
}
div[data-baseweb="select"] div {
    font-size: 16px !important;
    color: #111827 !important;
}
label {
    color: #374151 !important;
    font-weight: 500 !important;
}

/* 7. CUSTOM MESSAGE STYLING */
.section-title {
    font-size: 1.25rem; font-weight: 700; color: #111827;
    margin: 32px 0 16px 0;
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
      <div class="pill">Classy Mode</div>
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
with tab_workout:
    schedule = data.get("schedule", {})
    day_plan = schedule.get(today_day_name, {})
    exercises = day_plan.get("exercises", [])
    
    st.markdown(f'<div class="section-title">Today: {today_day_name}</div>', unsafe_allow_html=True)
    st.info(f"**Focus:** {day_plan.get('focus','—')}  |  **Intensity:** {day_plan.get('intensity','—')}  |  **Core:** {day_plan.get('core','—')}")

    if not exercises:
        st.write("No planned exercises.")
    else:
        with st.form("log_form"):
            log_entries = []
            for i, ex in enumerate(exercises):
                st.markdown(f"**{i+1}. {ex.get('name')}**")
                st.caption(f"{ex.get('sets')} x {ex.get('reps')} | Tempo: {ex.get('tempo','—')} | {ex.get('notes','')}")
                
                cA, cB, cC, cD = st.columns([1,1,1,1])
                with cA:
                    s = st.number_input("Sets", 0, 20, 0, key=f"s{i}")
                with cB:
                    r = st.number_input("Reps", 0, 200, 0, key=f"r{i}")
                with cC:
                    w = st.number_input("Kg", 0.0, 500.0, 0.0, step=0.5, key=f"w{i}")
                with cD:
                    sk = st.checkbox("Skip", key=f"sk{i}")
                n = st.text_input("Note", key=f"n{i}", placeholder="How did it feel?")
                st.markdown("---")
                
                log_entries.append({
                    "name": ex.get("name"), "pset": str(ex.get("sets")), "prep": str(ex.get("reps")),
                    "aset": s, "arep": r, "awt": w, "skip": sk, "note": n
                })
            
            # Extras
            st.markdown("**Custom / Sport**")
            cx_name = st.text_input("Custom Exercise Name")
            c1, c2, c3 = st.columns(3)
            with c1: cx_s = st.number_input("Sets", 0, 20, 0, key="cx_s")
            with c2: cx_r = st.number_input("Reps", 0, 100, 0, key="cx_r")
            with c3: cx_w = st.number_input("Weight", 0.0, 500.0, 0.0, key="cx_w")
            
            sub = st.form_submit_button("Save Log")
            
            if sub:
                conn = connect_db()
                cur = conn.cursor()
                for e in log_entries:
                    cur.execute("INSERT INTO workout_logs (log_date, day_name, exercise_name, planned_sets, planned_reps, actual_sets, actual_reps, weight, skipped, notes) VALUES (?,?,?,?,?,?,?,?,?,?)",
                               (today.isoformat(), today_day_name, e["name"], e["pset"], e["prep"], e["aset"], e["arep"], e["awt"], 1 if e["skip"] else 0, e["note"]))
                if cx_name:
                    cur.execute("INSERT INTO custom_exercises (log_date, day_name, exercise_name, actual_sets, actual_reps, weight, notes) VALUES (?,?,?,?,?,?,?)",
                                (today.isoformat(), today_day_name, cx_name, cx_s, cx_r, cx_w, ""))
                conn.commit()
                conn.close()
                st.success("Saved!")

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
with tab_progress:
    st.markdown('<div class="section-title">Analytics</div>', unsafe_allow_html=True)
    conn = connect_db()
    logs = fetch_logs(conn)
    metrics = fetch_metrics(conn)
    conn.close()
    
    if not logs.empty:
        logs["log_date"] = pd.to_datetime(logs["log_date"]).dt.date
        daily = logs[logs["skipped"]==0].groupby("log_date").size().reset_index(name="count")
        fig = px.bar(daily, x="log_date", y="count", title="Exercises Completed per Day")
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Log some workouts to see data.")

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
