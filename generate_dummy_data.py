import sqlite3
import yaml
import random
from datetime import datetime, timedelta
import os

DB_PATH = "fitness_tracker.db"
WORKOUTS_YAML = "workouts.yaml"

def generate_data():
    if not os.path.exists(WORKOUTS_YAML):
        print(f"Error: {WORKOUTS_YAML} not found.")
        return

    with open(WORKOUTS_YAML, "r") as f:
        data = yaml.safe_load(f)

    schedule = data.get("schedule", {})
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Clear existing data for a clean slate
    print("Clearing old data...")
    cur.execute("DELETE FROM workout_logs")
    cur.execute("DELETE FROM custom_exercises")
    cur.execute("DELETE FROM sports_logs")
    cur.execute("DELETE FROM body_metrics")

    # Generate 30 days of data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print(f"Generating data from {start_date.date()} to {end_date.date()}...")

    current_date = start_date
    while current_date <= end_date:
        day_name = current_date.strftime("%A")
        
        # 1. Workout Logs
        if day_name in schedule:
            day_plan = schedule[day_name]
            exercises = day_plan.get("exercises", [])
            
            for ex in exercises:
                # 90% chance to do the workout
                if random.random() > 0.1:
                    name = ex["name"]
                    
                    # Parse target sets/reps
                    target_sets = ex.get("sets", 3)
                    if isinstance(target_sets, str): target_sets = 3
                    
                    # Simulate slight progress over time
                    # Progress factor: 0.0 to 1.0 over the 30 days
                    progress_factor = (current_date - start_date).days / 30
                    
                    # Weights vary by exercise type
                    base_weight = 0
                    if "Press" in name: base_weight = 20 + (10 * progress_factor)
                    elif "Raise" in name: base_weight = 8 + (2 * progress_factor)
                    elif "Squat" in name or "Leg" in name: base_weight = 40 + (20 * progress_factor)
                    elif "Curl" in name: base_weight = 10 + (4 * progress_factor)
                    
                    actual_weight = round(base_weight + random.uniform(-2, 2), 1)
                    if actual_weight < 0: actual_weight = 0

                    cur.execute("""
                        INSERT INTO workout_logs 
                        (log_date, day_name, exercise_name, planned_sets, planned_reps, actual_sets, actual_reps, weight, skipped, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        current_date.strftime("%Y-%m-%d"),
                        day_name,
                        name,
                        str(target_sets),
                        str(ex.get("reps", "10")),
                        target_sets, # Mostly hit target sets
                        random.randint(8, 12), # Variable reps
                        actual_weight,
                        0, # Not skipped
                        random.choice(["Felt good", "Hard", "Okay", "", "Great pump", "Heavy"])
                    ))

        # 2. Body Metrics (Logged every ~3 days)
        if random.random() < 0.3:
            # Simulate weight loss: 85kg -> 83kg
            progress_factor = (current_date - start_date).days / 30
            weight = 85.0 - (2.0 * progress_factor) + random.uniform(-0.3, 0.3)
            bf = 22.0 - (1.0 * progress_factor)
            
            cur.execute("""
                INSERT INTO body_metrics (log_date, weight, body_fat, lean_mass, muscle_mass, water_mass, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                current_date.strftime("%Y-%m-%d"),
                round(weight, 1),
                round(bf, 1),
                round(weight * (1 - bf/100), 1),
                round(weight * (1 - bf/100) * 0.95, 1), # Simplified muscle mass
                0,
                "Morning weigh-in"
            ))

        current_date += timedelta(days=1)

    conn.commit()
    conn.close()
    print("Dummy data generation complete!")

if __name__ == "__main__":
    generate_data()
