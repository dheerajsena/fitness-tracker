# Personal Fitness Tracker

A clean, modern fitness tracking dashboard built with Python and Streamlit.

## Features
- **Easy Logging**: Add workouts via the sidebar with date types and duration.
- **Dynamic Config**: Workout types are loaded from `workouts.yaml`—edit this file to add your own!
- **Visual Analytics**: Interactive weekly bar chart and summary metrics.
- **Local Database**: Automatically creates and manages a local SQLite database (`fitness_tracker.db`).
- **Filtering**: Drill down into your data by workout type or date range.

## Quick Start
You need Python installed.

1.  **Install Dependencies**
    Open your terminal in this folder and run:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the App**
    ```bash
    streamlit run app.py
    ```

The app will pop up in your browser automatically!

## Customization
Edit `workouts.yaml` to change the dropdown options for exercises.
