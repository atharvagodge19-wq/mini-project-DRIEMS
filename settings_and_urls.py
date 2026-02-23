"""
StudyAI — Django Settings + URL Configuration
"""

# ==================== settings.py ====================
"""
Django Settings for StudyAI Project
"""

SECRET_KEY = 'django-insecure-change-this-in-production-use-env-variable'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',          # pip install django-cors-headers
    'rest_framework',       # pip install djangorestframework
    'studyai',              # your app
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'studyai.urls'

# ==================== MySQL Database ====================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'studyai_db',
        'USER': 'studyai_user',
        'PASSWORD': 'your_secure_password_here',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

AUTH_USER_MODEL = 'studyai.User'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = 'media/'

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:5500",  # VS Code Live Server
]
CORS_ALLOW_CREDENTIALS = True

SESSION_COOKIE_AGE = 86400 * 7  # 7 days
SESSION_SAVE_EVERY_REQUEST = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


# ==================== urls.py ====================
"""
URL Configuration for StudyAI API
All frontend requests go through /api/ prefix
"""

# studyai/urls.py
URLPATTERNS_CODE = """
from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('api/auth/register', views.api_register, name='register'),
    path('api/auth/login', views.api_login, name='login'),
    path('api/auth/logout', views.api_logout, name='logout'),

    # Subjects & Syllabus
    path('api/subjects', views.api_subjects, name='subjects'),
    path('api/subjects/<int:subject_id>', views.api_subject_detail, name='subject_detail'),

    # Scores & Performance
    path('api/scores', views.api_scores, name='scores'),
    path('api/performance/summary', views.api_performance_summary, name='performance_summary'),

    # Timetable
    path('api/timetable', views.api_get_timetable, name='timetable'),
    path('api/timetable/generate', views.api_generate_timetable, name='gen_timetable'),

    # Notifications
    path('api/notifications', views.api_notifications, name='notifications'),
    path('api/notifications/<int:notif_id>/read', views.api_mark_read, name='mark_read'),

    # Chatbot
    path('api/chatbot', views.api_chatbot, name='chatbot'),
]
"""


# ==================== MySQL Setup SQL ====================
MYSQL_SETUP_SQL = """
-- Run this SQL to create the MySQL database for StudyAI

CREATE DATABASE IF NOT EXISTS studyai_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'studyai_user'@'localhost' IDENTIFIED BY 'your_secure_password_here';
GRANT ALL PRIVILEGES ON studyai_db.* TO 'studyai_user'@'localhost';
FLUSH PRIVILEGES;

-- Django will create the tables automatically via migrations
-- python manage.py makemigrations
-- python manage.py migrate

-- Verify tables created:
USE studyai_db;
SHOW TABLES;

/*
Expected tables after migration:
- users                (user accounts, auth)
- subjects             (subject name, difficulty, exam_date)
- modules              (syllabus modules, AI-sorted by difficulty)
- test_scores          (quiz/test scores, weak areas, AI feedback)
- study_sessions       (study history: subject, duration, date)
- timetable            (AI-generated weekly schedule)
- notifications        (reminders, deadline alerts, AI tips)

Plus Django system tables:
- django_migrations, auth_*, django_content_type, django_session
*/

-- Sample query to see student performance dashboard
SELECT
    u.first_name, u.last_name,
    s.name AS subject,
    AVG(ts.score) AS avg_score,
    COUNT(ts.id) AS tests_taken,
    s.exam_date,
    DATEDIFF(s.exam_date, CURDATE()) AS days_until_exam,
    s.difficulty
FROM users u
JOIN subjects s ON s.user_id = u.id
LEFT JOIN test_scores ts ON ts.subject_id = s.id
GROUP BY u.id, s.id
ORDER BY avg_score ASC;

-- Query to get weak subjects (avg score < 70)
SELECT s.name, AVG(ts.score) as avg, u.email
FROM subjects s
JOIN test_scores ts ON ts.subject_id = s.id
JOIN users u ON u.id = s.user_id
GROUP BY s.id
HAVING avg < 70
ORDER BY avg ASC;

-- Study history per week
SELECT
    WEEK(ss.date) AS week_number,
    s.name AS subject,
    SUM(ss.duration_minutes) / 60 AS total_hours
FROM study_sessions ss
JOIN subjects s ON s.id = ss.subject_id
WHERE ss.user_id = 1
GROUP BY week_number, s.id
ORDER BY week_number, total_hours DESC;
"""
