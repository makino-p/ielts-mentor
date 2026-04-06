# 🎯 IELTS Mentor — AI-Powered IELTS Preparation Website

A full-featured IELTS preparation platform built with Flask (Python). Designed for pre-intermediate students targeting Band 6+.

## ✨ Features

- 📊 **Personal Dashboard** — band score estimate, XP system, streak tracker
- 📅 **12-Week Study Schedule** — structured day-by-day lesson plan
- 📚 **6 Course Modules** — 20+ lessons covering all 4 IELTS skills
- ✏️ **Practice Exercises** — Grammar, Listening, Reading, Writing, Vocabulary
- 🤖 **AI Tutor Chat** — ask questions anytime (uses Claude AI)
- ✍️ **Writing Feedback** — AI analyses your essays and gives band scores
- 💬 **Vocabulary Builder** — 40+ essential IELTS words with examples
- 📱 **Fully Responsive** — works on phone, tablet, and laptop

---

## 🚀 STEP-BY-STEP: Upload to GitHub & Deploy for FREE

### STEP 1: Install Git (if not installed)
- Windows: Download from https://git-scm.com
- Mac: Run `xcode-select --install` in Terminal
- Linux: `sudo apt install git`

---

### STEP 2: Create a GitHub Account & Repository
1. Go to https://github.com and create a free account
2. Click the **"+"** button → **"New repository"**
3. Repository name: `ielts-mentor`
4. Set to **Public** (required for free hosting)
5. Click **"Create repository"**

---

### STEP 3: Upload Files to GitHub

Open your terminal (Command Prompt / Terminal / PowerShell) in the `ielts-mentor` folder:

```bash
# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit: IELTS Mentor app"

# Connect to your GitHub repository (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/ielts-mentor.git

# Push to GitHub
git branch -M main
git push -u origin main
```

✅ Your code is now on GitHub!

---

### STEP 4: Deploy for FREE on Render.com

**Render** gives you a free Python web server — perfect for Flask apps.

1. Go to https://render.com and sign up (use your GitHub account)
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect a repository"** → select `ielts-mentor`
4. Fill in the settings:
   - **Name:** `ielts-mentor` (or any name you like)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free ✅
5. Click **"Create Web Service"**
6. Wait 2-3 minutes for deployment
7. Your website URL will be: `https://ielts-mentor.onrender.com`

---

### STEP 5: (Optional) Add AI Features with Claude API

To enable the AI tutor chat and writing feedback:

1. Go to https://console.anthropic.com
2. Create a free account
3. Go to **API Keys** → Create a new key
4. In Render dashboard → Your Service → **Environment Variables**
5. Add: `ANTHROPIC_API_KEY` = your API key

> **Note:** Without an API key, the app still works fully — it uses smart pre-written responses for the chat and offline writing feedback.

---

## 🖥️ Run Locally (on your own computer)

```bash
# 1. Install Python 3.11+ from https://python.org

# 2. Open terminal in the ielts-mentor folder

# 3. Create a virtual environment
python -m venv venv

# 4. Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Run the app
python app.py

# 7. Open in browser:
# http://localhost:5000
```

---

## 📁 Project Structure

```
ielts-mentor/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── Procfile               # For Render/Heroku deployment
├── render.yaml            # Render configuration
├── runtime.txt            # Python version
├── data/
│   ├── curriculum.json    # All lessons and modules
│   ├── exercises.json     # Practice exercises
│   └── vocabulary.json    # IELTS vocabulary list
├── templates/
│   ├── base.html          # Base layout
│   ├── index.html         # Dashboard
│   ├── lesson.html        # Lesson page
│   ├── exercise.html      # Practice exercises
│   ├── vocabulary.html    # Vocabulary builder
│   └── schedule.html      # Study schedule
└── static/
    ├── css/main.css        # All styles
    └── js/main.js         # Interactive features
```

---

## 🆓 Free Resources Used

The app recommends and links to these completely free resources:
- **BBC Learning English** — bbc.co.uk/learningenglish
- **British Council LearnEnglish** — learnenglish.britishcouncil.org
- **IELTS Liz** — ieltsliz.com
- **IELTS Simon** — ielts-simon.com
- **TED Talks** — ted.com/talks
- **Duolingo** — duolingo.com

---

## 🔧 Customization

### Add More Exercises
Edit `data/exercises.json` — add objects to any skill array (grammar, listening, reading, writing, vocabulary).

### Add More Lessons
Edit `data/curriculum.json` — add lesson objects to any module's `lessons` array.

### Add More Vocabulary
Edit `data/vocabulary.json` — add word objects to the `pre_intermediate` array.

---

## 🌟 IELTS Band Score Targets

| Starting Level | Target Band | Estimated Time |
|---------------|-------------|----------------|
| Pre-intermediate (3.5) | Band 5.0 | 6-8 weeks |
| Pre-intermediate (3.5) | Band 5.5 | 10-12 weeks |
| Pre-intermediate (3.5) | Band 6.0 | 4-6 months |

---

## 📞 Support

If you have problems with deployment:
1. Check Render logs in the dashboard
2. Make sure `requirements.txt` is in the root folder
3. Make sure `Procfile` contains exactly: `web: gunicorn app:app`

---

*Built with ❤️ for IELTS students. Good luck with your exam! 🎯*
