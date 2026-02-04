# How to Resume Work & Update Your App

## 1. Where is my project?
Your entire project is safely stored in the cloud on **GitHub**:
👉 **[https://github.com/dheerajsena/fitness-tracker](https://github.com/dheerajsena/fitness-tracker)**

This repository is the "Source of Truth". As long as this exists, your app exists.

## 2. How to work on it again (in 2 weeks, or anytime)

### Option A: You still have this computer & folder
1. Open your terminal to the project folder.
2. Run `git pull` to make sure you have the latest version.
3. Start the coding tool (like VS Code or this AI agent).
4. Run `streamlit run app.py` to test changes locally.

### Option B: You are on a NEW computer
1. Open a terminal.
2. Run: `git clone https://github.com/dheerajsena/fitness-tracker.git`
3. Enter the folder: `cd fitness-tracker`
4. Install dependencies: `pip install -r requirements.txt`
5. Start coding!

## 3. How to update the Live App
The "App" on your phone adds a magical link to the code on GitHub.
To update the app on your phone, you **DO NOT** need to touch your phone.

**Just push your code changes from your computer:**
```bash
git add .
git commit -m "Added new features"
git push
```

**That's it!**
1. GitHub receives your new code.
2. Streamlit Cloud sees the change and **automatically restarts** your app.
3. Next time you open the icon on your phone, the new features will be there!
