
# -----------------------------
# CLOUD DEPLOYMENT GUIDE (FREE)
# -----------------------------

You want a fitness app that works 24/7, doesn't rely on your Mac being awake, and feels like a real "App".
The best way to do this is to deploy it to the cloud.

Streamlit Community Cloud is **free** and perfect for this.

### Step 1: Create a GitHub Repository
1. Go to [GitHub.com](https://github.com) and create a new repository called `fitness-tracker`.
2. Upload these files from your `fitness_tracker` folder to it:
   - `app.py`
   - `workouts.yaml`
   - `requirements.txt`
   - `fitness_tracker.db` (Optional, if you want to keep current logs. If not, it will create a new one).

### Step 2: Deploy
1. Go to [share.streamlit.io](https://share.streamlit.io/).
2. Click **New App**.
3. Select your GitHub repository (`fitness-tracker`).
4. Select `app.py` as the main file path.
5. Click **Deploy**.

### Step 3: Use it Forever
Streamlit will give you a URL (e.g., `https://dheeraj-fitness.streamlit.app`).
1. Open this link on your iPhone.
2. Share -> Add to Home Screen.

**Now it is a real app.** It lives in the cloud. You can restart your phone, turn off your Mac, throw your Mac in the ocean — your fitness tracker will still work.

### Note on Database Persistence in Cloud
Streamlit Cloud resets the file system when the app reboots (rarely, but happens).
For **permanent** cloud storage, you should eventually connect a Google Sheet or Cloud Database.
*However*, for now, this gets you 90% of the way there for free.
