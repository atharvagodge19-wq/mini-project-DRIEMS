# ⚡ StudyAI — Intelligent Study Planner

> AI-powered academic companion that generates personalized timetables, tracks performance, and adapts to your learning needs.

---

## 📁 Project Structure

```
study_planner/
├── frontend/
│   ├── index.html        ← Main SPA with all pages (Login + Dashboard)
│   ├── styles.css        ← Complete dark theme UI styles
│   └── app.js            ← Frontend logic, charts, AI simulation
│
└── backend/
    ├── models.py          ← Django ORM models (MySQL schema)
    ├── views.py           ← REST API endpoints (auth, subjects, timetable, etc.)
    ├── ai_engine.py       ← AI modules (scheduler, performance analyzer, adaptive learning)
    └── settings_and_urls.py ← Django config + MySQL setup SQL
```

---

## 🚀 Quick Start

### 1. Open Frontend (Standalone Demo)
```bash
# Simply open in browser — works without backend
open frontend/index.html
# Or use VS Code Live Server
```

### 2. Full Stack Setup

#### Prerequisites
```bash
pip install django djangorestframework django-cors-headers mysqlclient
```

#### MySQL Database Setup
```sql
CREATE DATABASE studyai_db CHARACTER SET utf8mb4;
CREATE USER 'studyai_user'@'localhost' IDENTIFIED BY 'yourpassword';
GRANT ALL PRIVILEGES ON studyai_db.* TO 'studyai_user'@'localhost';
```

#### Django Setup
```bash
# Create project
django-admin startproject studyai_project .
python manage.py startapp studyai

# Copy models.py, views.py, ai_engine.py into the studyai/ app
# Update settings.py with MySQL credentials from settings_and_urls.py

# Run migrations
python manage.py makemigrations studyai
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

---

## 🧠 AI Features

### 1. AI Scheduling Engine
- **Priority Score** = `difficulty_weight × exam_proximity_weight × performance_weight`  
- Harder subjects in morning time slots (peak focus hours)
- Subjects with closer exams get proportionally more time
- Low-scoring subjects get time boost automatically

### 2. Performance Analyzer
- Tracks quiz/test scores per subject over time
- Linear regression trend detection (improving / stable / declining)
- Weighted moving average score prediction
- Identifies critical weak areas (< 70% threshold)

### 3. Adaptive Learning Module
- After every score entry: recalculates timetable priorities
- Spaced repetition revision frequency suggestions (Ebbinghaus curve)
- Increases study hours for weak subjects inversely to score
- Generates personalized action recommendations

### 4. Module Difficulty Sorter
- NLP keyword scoring (theorem/proof = high difficulty)
- Position heuristics (later modules tend to be harder)
- Outputs sorted syllabus: most difficult → easiest

### 5. AI Chatbot
- Contextual responses using live user data
- Knows your weakest subjects, closest exam, study history
- Can explain concepts, give study strategies, motivate
- **Production**: Replace `generate_contextual_response()` with OpenAI/Claude API call

---

## 📊 MySQL Schema

| Table | Key Columns |
|-------|-------------|
| `users` | id, email, first_name, university, study_goal_hours |
| `subjects` | id, user_id, name, difficulty, exam_date, ai_priority_score |
| `modules` | id, subject_id, name, ai_difficulty_score, order, status |
| `test_scores` | id, user_id, subject_id, score, test_type, ai_feedback, predicted_next_score |
| `study_sessions` | id, user_id, subject_id, duration_minutes, date, focus_score |
| `timetable` | id, user_id, subject_id, day, start_time, duration_minutes, ai_intensity |
| `notifications` | id, user_id, title, message, notification_type, is_read |

---

## 🖥️ Frontend Features

| Section | Features |
|---------|----------|
| **Login/Register** | Email auth, JWT sessions |
| **Dashboard** | Stats grid, today's schedule, AI tips, strength chart |
| **Timetable** | Weekly view, AI regeneration, hour/day controls |
| **Subjects** | Add subjects + modules, AI difficulty sorting display |
| **Performance** | Score logging, trend charts, weak area cards |
| **Notifications** | Deadline alerts, custom reminders, AI notifications |
| **Progress** | Weekly hours bar chart, subject coverage donut, timeline with AI prediction |
| **AI Chatbot** | Floating assistant with context-aware responses |

---

## 🔌 API Endpoints

```
POST  /api/auth/register          Register new user
POST  /api/auth/login             Login with email + password
POST  /api/auth/logout            Logout

GET   /api/subjects               List all subjects
POST  /api/subjects               Add subject (AI sorts modules)
GET   /api/subjects/:id           Get subject details
PUT   /api/subjects/:id           Update subject
DELETE /api/subjects/:id          Delete subject

GET   /api/scores                 List scores (optional ?subject_id)
POST  /api/scores                 Log new score (AI feedback generated)
GET   /api/performance/summary    AI performance summary + trends

GET   /api/timetable              Current week timetable
POST  /api/timetable/generate     Generate new AI timetable

GET   /api/notifications          All notifications
POST  /api/notifications/:id/read Mark as read

POST  /api/chatbot                AI assistant message
```

---

## 🎨 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Charts | Chart.js 4.x |
| Backend | Python 3.11+ / Django 4.x |
| Database | MySQL 8.0 |
| Auth | Django Session Auth (extendable to JWT) |
| AI/ML | Custom algorithms (extendable to OpenAI API) |

---

## 🔮 Extend to Full AI

To connect the chatbot to a real LLM, update `views.py`:

```python
import openai

def api_chatbot(request):
    ...
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": f"You are StudyAI. User context: {json.dumps(context)}"},
            {"role": "user", "content": user_message}
        ]
    )
    return JsonResponse({'response': response.choices[0].message.content})
```

Or use Claude API:
```python
import anthropic
client = anthropic.Anthropic(api_key="your-key")
msg = client.messages.create(model="claude-opus-4-6", max_tokens=500, messages=[...])
```
