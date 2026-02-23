"""
StudyAI Backend - Django Views (REST API)
All endpoints that communicate with the frontend
"""

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Avg, Count
import json
from datetime import date, timedelta, datetime

from .models import User, Subject, Module, TestScore, StudySession, Timetable, Notification
from .ai_engine import AISchedulingEngine, PerformanceAnalyzer, AdaptiveLearning


# ==================== AUTH VIEWS ====================

@csrf_exempt
def api_register(request):
    """POST /api/auth/register"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    university = data.get('university', '')

    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': 'Email already registered'}, status=400)

    user = User.objects.create_user(
        username=email, email=email, password=password,
        first_name=first_name, last_name=last_name,
        university=university
    )

    # Create welcome notification
    Notification.objects.create(
        user=user, title='Welcome to StudyAI! 🎉',
        message='Start by adding your subjects and let AI build your perfect timetable.',
        notification_type='ai_tip'
    )

    login(request, user)
    return JsonResponse({'success': True, 'user': _user_data(user)}, status=201)


@csrf_exempt
def api_login(request):
    """POST /api/auth/login"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')

    user = authenticate(request, username=email, password=password)
    if user:
        login(request, user)
        return JsonResponse({'success': True, 'user': _user_data(user)})
    return JsonResponse({'error': 'Invalid credentials'}, status=401)


@login_required
def api_logout(request):
    """POST /api/auth/logout"""
    logout(request)
    return JsonResponse({'success': True})


def _user_data(user):
    return {
        'id': user.id, 'email': user.email,
        'first_name': user.first_name, 'last_name': user.last_name,
        'university': user.university, 'study_goal_hours': user.study_goal_hours
    }


# ==================== SUBJECT VIEWS ====================

@csrf_exempt
@login_required
def api_subjects(request):
    """GET/POST /api/subjects"""
    if request.method == 'GET':
        subjects = Subject.objects.filter(user=request.user).prefetch_related('modules', 'scores')
        return JsonResponse({'subjects': [_subject_data(s) for s in subjects]})

    if request.method == 'POST':
        data = json.loads(request.body)
        subject = Subject.objects.create(
            user=request.user,
            name=data['name'],
            difficulty=data['difficulty'],
            exam_date=data['exam_date'],
            color=data.get('color', '#7c6aff'),
        )

        # AI: Sort and score modules by difficulty
        modules_raw = data.get('modules', [])
        if modules_raw:
            engine = AISchedulingEngine(request.user)
            sorted_modules = engine.sort_modules_by_difficulty(modules_raw)
            for i, (mod_name, ai_score) in enumerate(sorted_modules):
                Module.objects.create(
                    subject=subject, name=mod_name,
                    ai_difficulty_score=ai_score, order=i,
                    estimated_hours=max(1.0, ai_score / 3)
                )
            subject.total_modules = len(sorted_modules)
            subject.save()

        # AI: Recalculate priority scores for all subjects
        engine = AISchedulingEngine(request.user)
        engine.update_priority_scores()

        # Auto-generate deadline notification
        days_left = subject.days_until_exam()
        if days_left <= 14:
            Notification.objects.create(
                user=request.user,
                title=f'Exam Alert: {subject.name}',
                message=f'Your exam for {subject.name} is in {days_left} days! AI has prioritized it in your timetable.',
                notification_type='deadline'
            )

        return JsonResponse({'subject': _subject_data(subject)}, status=201)


@csrf_exempt
@login_required
def api_subject_detail(request, subject_id):
    """GET/PUT/DELETE /api/subjects/<id>"""
    try:
        subject = Subject.objects.get(id=subject_id, user=request.user)
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'subject': _subject_data(subject)})

    if request.method == 'PUT':
        data = json.loads(request.body)
        for field in ['name', 'difficulty', 'exam_date', 'color']:
            if field in data:
                setattr(subject, field, data[field])
        subject.save()
        return JsonResponse({'subject': _subject_data(subject)})

    if request.method == 'DELETE':
        subject.delete()
        return JsonResponse({'success': True})


def _subject_data(subject):
    modules = list(subject.modules.all().order_by('order').values(
        'id', 'name', 'ai_difficulty_score', 'order', 'status', 'estimated_hours'
    ))
    avg_score = subject.scores.aggregate(avg=Avg('score'))['avg'] or 0
    return {
        'id': subject.id, 'name': subject.name,
        'difficulty': subject.difficulty, 'color': subject.color,
        'exam_date': subject.exam_date.isoformat(),
        'days_until_exam': subject.days_until_exam(),
        'coverage_percent': subject.coverage_percent(),
        'total_modules': subject.total_modules,
        'completed_modules': subject.completed_modules,
        'ai_priority_score': subject.ai_priority_score,
        'avg_score': round(avg_score, 1),
        'modules': modules
    }


# ==================== SCORE VIEWS ====================

@csrf_exempt
@login_required
def api_scores(request):
    """GET/POST /api/scores"""
    if request.method == 'GET':
        subject_id = request.GET.get('subject_id')
        scores = TestScore.objects.filter(user=request.user)
        if subject_id:
            scores = scores.filter(subject_id=subject_id)
        return JsonResponse({'scores': list(scores.values())})

    if request.method == 'POST':
        data = json.loads(request.body)
        subject = Subject.objects.get(id=data['subject_id'], user=request.user)

        score = TestScore.objects.create(
            user=request.user, subject=subject,
            score=data['score'], test_type=data.get('test_type', 'quiz'),
            weak_areas=data.get('weak_areas', ''),
            date_taken=data.get('date', date.today())
        )

        # AI: Generate feedback and predict next score
        analyzer = PerformanceAnalyzer(request.user)
        feedback = analyzer.generate_feedback(subject, data['score'])
        predicted = analyzer.predict_next_score(subject)
        score.ai_feedback = feedback
        score.predicted_next_score = predicted
        score.save()

        # AI: Adaptive learning adjustments
        adaptive = AdaptiveLearning(request.user)
        adaptive.adjust_timetable(subject, data['score'])

        # Generate notification if low score
        if data['score'] < 70:
            Notification.objects.create(
                user=request.user,
                title=f'Study Alert: {subject.name}',
                message=f'Your recent score of {data["score"]}% in {subject.name} is below target. AI has increased your allocated study time.',
                notification_type='performance'
            )

        return JsonResponse({'score': {
            'id': score.id, 'score': score.score,
            'ai_feedback': feedback, 'predicted_next': predicted
        }}, status=201)


# ==================== TIMETABLE VIEWS ====================

@login_required
def api_generate_timetable(request):
    """POST /api/timetable/generate"""
    data = json.loads(request.body) if request.body else {}
    study_hours = data.get('study_hours', request.user.study_goal_hours)
    available_days = data.get('available_days', request.user.available_days.split(','))
    week_start = date.today() - timedelta(days=date.today().weekday())

    engine = AISchedulingEngine(request.user)
    timetable = engine.generate_timetable(
        study_hours_per_day=study_hours,
        available_days=available_days,
        week_start=week_start
    )

    # Clear existing and save new
    Timetable.objects.filter(user=request.user, week_start=week_start).delete()
    for entry in timetable:
        Timetable.objects.create(user=request.user, week_start=week_start, **entry)

    return JsonResponse({'timetable': timetable, 'week_start': week_start.isoformat()})


@login_required
def api_get_timetable(request):
    """GET /api/timetable"""
    week_start = date.today() - timedelta(days=date.today().weekday())
    entries = Timetable.objects.filter(
        user=request.user, week_start=week_start
    ).select_related('subject')

    return JsonResponse({'timetable': [{
        'id': e.id, 'subject_id': e.subject.id,
        'subject_name': e.subject.name, 'subject_color': e.subject.color,
        'day': e.day, 'start_time': e.start_time.strftime('%H:%M'),
        'duration_minutes': e.duration_minutes,
        'ai_intensity': e.ai_intensity, 'priority_rank': e.priority_rank
    } for e in entries]})


# ==================== PERFORMANCE VIEWS ====================

@login_required
def api_performance_summary(request):
    """GET /api/performance/summary"""
    user = request.user
    analyzer = PerformanceAnalyzer(user)

    subjects = Subject.objects.filter(user=user)
    summary = []
    for subject in subjects:
        scores = TestScore.objects.filter(user=user, subject=subject).order_by('date_taken')
        if scores.exists():
            avg = scores.aggregate(avg=Avg('score'))['avg']
            trend = analyzer.calculate_trend(list(scores.values_list('score', flat=True)))
            summary.append({
                'subject_id': subject.id, 'subject_name': subject.name,
                'avg_score': round(avg, 1), 'trend': trend,
                'is_weak': avg < 70,
                'recommended_hours': analyzer.recommended_hours(subject, avg)
            })

    # Weekly study hours
    week_ago = date.today() - timedelta(days=7)
    weekly_sessions = StudySession.objects.filter(
        user=user, date__gte=week_ago
    ).values('date').annotate(
        total_minutes=models.Sum('duration_minutes')
    )

    return JsonResponse({
        'subject_summary': summary,
        'weekly_study_hours': [
            {'date': s['date'].isoformat(), 'hours': round(s['total_minutes'] / 60, 1)}
            for s in weekly_sessions
        ],
        'total_study_hours_week': sum(s['total_minutes'] for s in weekly_sessions) / 60,
        'improvement_prediction': analyzer.predict_overall_improvement()
    })


# ==================== NOTIFICATION VIEWS ====================

@login_required
def api_notifications(request):
    """GET /api/notifications"""
    notifs = Notification.objects.filter(user=request.user)
    return JsonResponse({'notifications': list(notifs.values())})


@csrf_exempt
@login_required
def api_mark_read(request, notif_id):
    """POST /api/notifications/<id>/read"""
    Notification.objects.filter(id=notif_id, user=request.user).update(is_read=True)
    return JsonResponse({'success': True})


# ==================== CHATBOT VIEW ====================

@csrf_exempt
@login_required
def api_chatbot(request):
    """POST /api/chatbot — AI assistant endpoint"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    data = json.loads(request.body)
    user_message = data.get('message', '')
    conversation_history = data.get('history', [])

    # Build context from user's data
    user = request.user
    subjects = Subject.objects.filter(user=user).prefetch_related('scores')
    weak_subjects = [s for s in subjects if s.scores.aggregate(avg=Avg('score'))['avg'] or 75 < 70]
    closest_exam = subjects.filter(exam_date__gte=date.today()).first()

    context = {
        'user_name': user.first_name,
        'subjects': [{'name': s.name, 'difficulty': s.difficulty, 'days_left': s.days_until_exam()} for s in subjects],
        'weak_subjects': [s.name for s in weak_subjects],
        'closest_exam': closest_exam.name if closest_exam else None,
        'closest_exam_days': closest_exam.days_until_exam() if closest_exam else None,
    }

    # In production: integrate with OpenAI/Claude API here
    # response = openai.chat.completions.create(
    #     model="gpt-4",
    #     messages=[
    #         {"role": "system", "content": f"You are StudyAI, an academic assistant. User context: {json.dumps(context)}"},
    #         *conversation_history,
    #         {"role": "user", "content": user_message}
    #     ]
    # )
    # bot_response = response.choices[0].message.content

    # Simplified response for demo
    bot_response = generate_contextual_response(user_message, context)

    return JsonResponse({
        'response': bot_response,
        'context_used': context
    })


def generate_contextual_response(message, context):
    """Simple rule-based response (replace with LLM in production)"""
    lower = message.lower()
    if 'weak' in lower or 'struggling' in lower:
        if context['weak_subjects']:
            return f"Based on your scores, you should focus on: {', '.join(context['weak_subjects'])}. I've flagged these for extra time in your timetable."
        return "Your scores look solid! Keep up the consistent study schedule."
    if 'exam' in lower:
        if context['closest_exam']:
            return f"Your nearest exam is {context['closest_exam']} in {context['closest_exam_days']} days. Review your AI-sorted modules starting from the most difficult ones."
        return "No upcoming exams found. Add your exam dates in the Subjects section!"
    return f"I'm here to help, {context['user_name']}! Ask me about your subjects, study strategies, or exam preparation."
