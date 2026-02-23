"""
StudyAI Backend - Django Models
Database: MySQL
Tables: users, subjects, modules, test_scores, study_sessions, notifications
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import json


class User(AbstractUser):
    """Extended user model with academic profile"""
    email = models.EmailField(unique=True)
    university = models.CharField(max_length=200, blank=True)
    study_goal_hours = models.FloatField(default=6.0)  # hours per day
    available_days = models.CharField(max_length=50, default='Mon,Tue,Wed,Thu,Fri')
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    class Meta:
        db_table = 'users'


class Subject(models.Model):
    """Subject with syllabus and exam details"""
    DIFFICULTY_CHOICES = [(i, str(i)) for i in range(1, 11)]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=200)
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=5)
    color = models.CharField(max_length=10, default='#7c6aff')
    exam_date = models.DateField()
    total_modules = models.IntegerField(default=0)
    completed_modules = models.IntegerField(default=0)
    ai_priority_score = models.FloatField(default=0.0)  # Calculated by AI engine
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def coverage_percent(self):
        if self.total_modules == 0:
            return 0
        return round((self.completed_modules / self.total_modules) * 100, 1)

    def days_until_exam(self):
        delta = self.exam_date - timezone.now().date()
        return max(0, delta.days)

    def __str__(self):
        return f"{self.name} (User: {self.user.email})"

    class Meta:
        db_table = 'subjects'
        ordering = ['exam_date']


class Module(models.Model):
    """Individual module/topic within a subject"""
    DIFFICULTY_CHOICES = [(i, str(i)) for i in range(1, 11)]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='modules')
    name = models.CharField(max_length=300)
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=5)
    ai_difficulty_score = models.FloatField(default=5.0)  # AI-estimated difficulty
    order = models.IntegerField(default=0)  # AI sorted order (0 = hardest)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    estimated_hours = models.FloatField(default=2.0)
    actual_hours = models.FloatField(default=0.0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject.name} — {self.name}"

    class Meta:
        db_table = 'modules'
        ordering = ['order']


class TestScore(models.Model):
    """Quiz and test scores for performance tracking"""
    TEST_TYPES = [
        ('quiz', 'Quiz'),
        ('midterm', 'Midterm'),
        ('final', 'Final'),
        ('practice', 'Practice Test'),
        ('assignment', 'Assignment'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_scores')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='scores')
    score = models.FloatField()  # 0-100
    max_score = models.FloatField(default=100)
    test_type = models.CharField(max_length=20, choices=TEST_TYPES, default='quiz')
    weak_areas = models.TextField(blank=True)  # Notes on weak topics
    date_taken = models.DateField(default=timezone.now)
    ai_feedback = models.TextField(blank=True)  # AI-generated feedback
    predicted_next_score = models.FloatField(null=True, blank=True)

    def percentage(self):
        return round((self.score / self.max_score) * 100, 1)

    def __str__(self):
        return f"{self.subject.name}: {self.score}/{self.max_score} ({self.test_type})"

    class Meta:
        db_table = 'test_scores'
        ordering = ['-date_taken']


class StudySession(models.Model):
    """Individual study session history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='sessions')
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True, blank=True)
    duration_minutes = models.IntegerField()
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField(null=True, blank=True)
    focus_score = models.IntegerField(default=5)  # 1-10 self-reported
    notes = models.TextField(blank=True)
    ai_session_rating = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} — {self.subject.name} — {self.duration_minutes}min"

    class Meta:
        db_table = 'study_sessions'
        ordering = ['-date', '-start_time']


class Timetable(models.Model):
    """AI-generated timetable entries"""
    DAYS = [
        ('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='timetable_entries')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAYS)
    start_time = models.TimeField()
    duration_minutes = models.IntegerField()
    week_start = models.DateField()
    ai_intensity = models.CharField(max_length=10, default='medium')  # low/medium/high
    priority_rank = models.IntegerField(default=1)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} — {self.day} {self.start_time} — {self.subject.name}"

    class Meta:
        db_table = 'timetable'
        ordering = ['week_start', 'day', 'start_time']


class Notification(models.Model):
    """User notifications and reminders"""
    TYPES = [
        ('deadline', 'Deadline Alert'),
        ('reminder', 'Study Reminder'),
        ('achievement', 'Achievement'),
        ('ai_tip', 'AI Tip'),
        ('performance', 'Performance Update'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPES, default='reminder')
    is_read = models.BooleanField(default=False)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name}: {self.title}"

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
