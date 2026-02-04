import sqlite3
import os

DB_PATH = "fitness_tracker.db"

def reset_database():
    if not os.path.exists(DB_PATH):
        print(f"Database at {DB_PATH} not found. Nothing to reset.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    tables = ["workout_logs", "custom_exercises", "sports_logs", "body_metrics"]
    
    print("Resetting database...")
    for table in tables:
        try:
            cur.execute(f"DELETE FROM {table}")
            print(f" - Cleared table: {table}")
        except sqlite3.OperationalError as e:
            print(f" - Warning: Could not clear table {table} ({e})")

    # Reset SQLite sequence to restart auto-increment IDs from 1
    try:
        cur.execute("DELETE FROM sqlite_sequence")
        print(" - Reset ID counters")
    except:
        pass

    conn.commit()
    conn.close()
    print("✅ Database completely reset. Ready for new user.")

if __name__ == "__main__":
    reset_database()
