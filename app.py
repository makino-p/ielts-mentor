from flask import Flask, render_template, request, jsonify, session
import json
import os
import random
from datetime import datetime, timedelta
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ielts-mentor-secret-2024")

# ── Load curriculum data ──────────────────────────────────────────────────────

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

CURRICULUM = load_json("data/curriculum.json")
EXERCISES  = load_json("data/exercises.json")
VOCABULARY = load_json("data/vocabulary.json")

# ── Anthropic Claude API (free tier via user's key or env) ────────────────────

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

def ask_claude(system_prompt, user_message, max_tokens=800):
    """Call Claude API for AI-powered feedback."""
    if not ANTHROPIC_API_KEY:
        return None
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_message}],
            },
            timeout=30,
        )
        data = resp.json()
        return data["content"][0]["text"] if resp.status_code == 200 else None
    except Exception:
        return None

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_progress():
    return session.get("progress", {
        "completed_lessons": [],
        "quiz_scores": {},
        "vocabulary_known": [],
        "writing_submissions": [],
        "total_xp": 0,
        "streak": 0,
        "last_study_date": None,
        "started_date": datetime.now().strftime("%Y-%m-%d"),
        "band_estimate": 3.5,
    })

def save_progress(p):
    session["progress"] = p
    session.modified = True

def update_streak(p):
    today = datetime.now().strftime("%Y-%m-%d")
    if p["last_study_date"] == today:
        return p
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    if p["last_study_date"] == yesterday:
        p["streak"] += 1
    else:
        p["streak"] = 1
    p["last_study_date"] = today
    return p

def estimate_band(p):
    completed = len(p["completed_lessons"])
    scores = list(p["quiz_scores"].values())
    avg_score = sum(scores) / len(scores) if scores else 0
    base = 3.5 + (completed * 0.05) + (avg_score / 100 * 1.5)
    return round(min(base, 9.0) * 2) / 2  # round to nearest 0.5

def build_schedule(p):
    """Generate a 12-week study schedule."""
    weeks = []
    lesson_index = 0
    lessons_flat = []
    for module in CURRICULUM["modules"]:
        for lesson in module["lessons"]:
            lessons_flat.append({"module": module["title"], "lesson": lesson})

    for week in range(1, 13):
        days = []
        for day_num in range(1, 6):  # Mon-Fri
            tasks = []
            if lesson_index < len(lessons_flat):
                l = lessons_flat[lesson_index]
                tasks.append({"type": "lesson", "title": l["lesson"]["title"], "module": l["module"], "id": l["lesson"]["id"]})
                lesson_index += 1
            # Add vocab or practice based on day
            if day_num % 2 == 0:
                tasks.append({"type": "vocabulary", "title": "Vocabulary Practice (20 words)"})
            else:
                tasks.append({"type": "exercise", "title": "Skills Practice"})
            days.append({"day": day_num, "tasks": tasks})
        weeks.append({"week": week, "days": days})
    return weeks

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    p = get_progress()
    p = update_streak(p)
    p["band_estimate"] = estimate_band(p)
    save_progress(p)
    schedule = build_schedule(p)
    current_week = min(
        max(1, len(p["completed_lessons"]) // 5 + 1), 12
    )
    return render_template(
        "index.html",
        progress=p,
        curriculum=CURRICULUM,
        schedule=schedule,
        current_week=current_week,
    )

@app.route("/lesson/<lesson_id>")
def lesson(lesson_id):
    p = get_progress()
    # Find lesson in curriculum
    found = None
    for module in CURRICULUM["modules"]:
        for les in module["lessons"]:
            if les["id"] == lesson_id:
                found = {"lesson": les, "module": module["title"]}
                break
    if not found:
        return "Lesson not found", 404
    return render_template("lesson.html", data=found, progress=p)

@app.route("/api/complete-lesson", methods=["POST"])
def complete_lesson():
    data = request.json
    p = get_progress()
    lid = data.get("lesson_id")
    if lid and lid not in p["completed_lessons"]:
        p["completed_lessons"].append(lid)
        p["total_xp"] += 50
    p = update_streak(p)
    p["band_estimate"] = estimate_band(p)
    save_progress(p)
    return jsonify({"xp": p["total_xp"], "band": p["band_estimate"], "streak": p["streak"]})

@app.route("/exercise/<skill>")
def exercise(skill):
    p = get_progress()
    exercises = EXERCISES.get(skill, [])
    ex = random.choice(exercises) if exercises else None
    return render_template("exercise.html", exercise=ex, skill=skill, progress=p)

@app.route("/api/check-answer", methods=["POST"])
def check_answer():
    data = request.json
    skill     = data.get("skill")
    ex_id     = data.get("exercise_id")
    answer    = data.get("answer", "")
    correct   = data.get("correct_answer", "")
    ex_type   = data.get("type", "mcq")

    p = get_progress()

    if ex_type == "writing":
        # Use Claude for writing feedback
        sys_prompt = (
            "You are an expert IELTS examiner. Give concise, encouraging feedback "
            "for a pre-intermediate student. Score the writing out of 9 for: "
            "Task Achievement, Coherence, Vocabulary, Grammar. Be specific and helpful. "
            "Response in 150-200 words max."
        )
        user_msg = f"IELTS Task prompt: {correct}\n\nStudent's answer:\n{answer}"
        feedback = ask_claude(sys_prompt, user_msg, max_tokens=300)
        if not feedback:
            feedback = evaluate_writing_offline(answer)
        score = estimate_writing_score(answer)
        p["writing_submissions"].append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "score": score,
            "feedback": feedback[:200],
        })
        p["total_xp"] += 30
        save_progress(p)
        return jsonify({"correct": True, "score": score, "feedback": feedback, "xp_earned": 30})

    # MCQ / fill-in-the-blank
    is_correct = answer.strip().lower() == correct.strip().lower()
    xp = 10 if is_correct else 0
    p["total_xp"] += xp
    if skill not in p["quiz_scores"]:
        p["quiz_scores"][skill] = []
    p["quiz_scores"][skill].append(100 if is_correct else 0)
    save_progress(p)
    return jsonify({
        "correct": is_correct,
        "correct_answer": correct,
        "explanation": data.get("explanation", ""),
        "xp_earned": xp,
    })

def estimate_writing_score(text):
    words = len(text.split())
    sentences = text.count(".") + text.count("!") + text.count("?")
    if words < 50:   return 3.5
    if words < 100:  return 4.0
    if words < 150:  return 4.5
    if words < 200:  return 5.0
    return 5.5

def evaluate_writing_offline(text):
    words = len(text.split())
    score = estimate_writing_score(text)
    return (
        f"Good effort! Your response has {words} words. "
        f"Estimated band: {score}. "
        "Focus on: using linking words (however, therefore, in addition), "
        "varying your sentence structure, and checking subject-verb agreement. "
        "Keep practicing — consistency is key for IELTS success!"
    )

@app.route("/vocabulary")
def vocabulary():
    p = get_progress()
    level = "pre_intermediate"
    words = VOCABULARY.get(level, [])
    known = p.get("vocabulary_known", [])
    unknown = [w for w in words if w["word"] not in known]
    random.shuffle(unknown)
    batch = unknown[:20]
    return render_template("vocabulary.html", words=batch, known_count=len(known), total=len(words), progress=p)

@app.route("/api/mark-word", methods=["POST"])
def mark_word():
    data = request.json
    word = data.get("word")
    p = get_progress()
    if word and word not in p["vocabulary_known"]:
        p["vocabulary_known"].append(word)
        p["total_xp"] += 2
    save_progress(p)
    return jsonify({"known_count": len(p["vocabulary_known"]), "xp": p["total_xp"]})

@app.route("/schedule")
def schedule_page():
    p = get_progress()
    schedule = build_schedule(p)
    current_week = min(max(1, len(p["completed_lessons"]) // 5 + 1), 12)
    return render_template("schedule.html", schedule=schedule, current_week=current_week, progress=p)

@app.route("/api/ai-chat", methods=["POST"])
def ai_chat():
    data = request.json
    message = data.get("message", "")
    context = data.get("context", "general")
    p = get_progress()

    sys_prompt = (
        "You are an expert, warm and encouraging IELTS tutor. "
        f"The student is at pre-intermediate level (estimated band {p['band_estimate']}). "
        "Answer questions about IELTS clearly and practically. "
        "Give examples. Keep responses under 150 words. Be friendly."
    )
    response = ask_claude(sys_prompt, message)
    if not response:
        response = get_offline_response(message, context)
    return jsonify({"response": response})

def get_offline_response(message, context):
    msg = message.lower()
    if "writing" in msg:
        return ("For IELTS Writing Task 1, describe graphs/charts in 150+ words. "
                "Task 2 needs an essay of 250+ words. Use linking words: "
                "Furthermore, However, In conclusion. Practice daily!")
    if "reading" in msg:
        return ("IELTS Reading has 40 questions in 60 minutes. "
                "Skim first for the main idea, then scan for specific answers. "
                "Don't spend more than 2 minutes per question!")
    if "listening" in msg:
        return ("For IELTS Listening: read questions BEFORE the audio plays. "
                "Underline keywords. Write exactly what you hear. "
                "Practice with BBC Learning English podcasts daily!")
    if "speaking" in msg:
        return ("In Speaking Part 2, use the 1-minute prep time to make notes. "
                "Structure: Past→Present→Future. Use fillers: 'That's a good point...', "
                "'What I mean is...' — they buy you thinking time!")
    return ("Great question! The key to IELTS success is consistent daily practice. "
            "Focus on one skill per day, review vocabulary every morning, "
            "and use BBC Learning English for free audio practice. You've got this! 🎯")

@app.route("/api/reset-progress", methods=["POST"])
def reset_progress():
    session.clear()
    return jsonify({"ok": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
