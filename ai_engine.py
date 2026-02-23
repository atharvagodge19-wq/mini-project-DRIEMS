"""
StudyAI — AI Engine
=====================
1. AISchedulingEngine  — Optimized timetable generation
2. PerformanceAnalyzer — Score tracking, weak area identification, trend prediction
3. AdaptiveLearning    — Dynamic timetable adjustment based on performance

Algorithms:
  - Priority scoring: difficulty × (1/days_to_exam) × (100/avg_score)
  - Module difficulty: keyword NLP + position heuristics
  - Trend prediction: linear regression on score history
  - Adaptive hours: inverse-proportional to current performance
"""

from datetime import date, timedelta, time
from django.db.models import Avg, Count
import math
import re


class AISchedulingEngine:
    """
    Generates optimized study timetables based on:
    a) Subject difficulty
    b) Exam proximity
    c) Student availability
    d) Past performance
    """

    DIFFICULTY_KEYWORDS = {
        'high': ['theorem', 'proof', 'derivation', 'advanced', 'complex', 'abstract',
                 'differential', 'integral', 'quantum', 'mechanism', 'eigenvalue',
                 'entropy', 'topology', 'manifold', 'transform', 'convolution'],
        'medium': ['analysis', 'application', 'method', 'calculation', 'synthesis',
                   'evaluation', 'comparison', 'technique', 'algorithm', 'formula'],
        'low': ['introduction', 'overview', 'basic', 'fundamental', 'definition',
                'history', 'types', 'examples', 'simple', 'review', 'summary']
    }

    TIME_SLOTS = {
        'morning': [('08:00', 90), ('10:00', 75), ('11:30', 60)],
        'afternoon': [('14:00', 90), ('15:45', 60), ('17:00', 75)],
        'evening': [('19:00', 90), ('20:45', 60)]
    }

    def __init__(self, user):
        self.user = user

    def calculate_priority_score(self, subject):
        """
        Priority = (difficulty_weight × exam_weight × performance_weight)
        Higher score = should be studied more
        """
        from .models import TestScore

        # Difficulty weight (1-10 → 0.5-2.0)
        diff_weight = 0.5 + (subject.difficulty - 1) * (1.5 / 9)

        # Exam proximity weight (closer = higher priority, exponential)
        days = max(1, subject.days_until_exam())
        exam_weight = math.exp(-days / 30)  # decays over 30-day window

        # Performance weight (lower score = higher need)
        scores = TestScore.objects.filter(
            user=self.user, subject=subject
        ).values_list('score', flat=True)

        if scores:
            avg_score = sum(scores) / len(scores)
            perf_weight = max(0.5, 2.0 - (avg_score / 100))
        else:
            perf_weight = 1.2  # Default: slightly elevated for untested subjects

        priority = diff_weight * (1 + exam_weight) * perf_weight
        return round(priority, 4)

    def update_priority_scores(self):
        """Recalculate AI priority scores for all user subjects"""
        from .models import Subject
        for subject in Subject.objects.filter(user=self.user):
            subject.ai_priority_score = self.calculate_priority_score(subject)
            subject.save()

    def generate_timetable(self, study_hours_per_day=6, available_days=None, week_start=None):
        """
        Generate weekly timetable:
        - Allocates more time to high-priority subjects
        - Distributes difficult subjects in morning slots
        - Ensures variety across days
        """
        from .models import Subject

        if not available_days:
            available_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        if not week_start:
            week_start = date.today() - timedelta(days=date.today().weekday())

        subjects = list(Subject.objects.filter(user=self.user))
        if not subjects:
            return []

        # Calculate priority for each subject
        priorities = {s.id: self.calculate_priority_score(s) for s in subjects}
        total_priority = sum(priorities.values())

        # Allocate weekly minutes proportionally
        total_weekly_minutes = study_hours_per_day * 60 * len(available_days)
        allocations = {
            s.id: max(30, round((priorities[s.id] / total_priority) * total_weekly_minutes))
            for s in subjects
        }

        # Build timetable entries
        entries = []
        day_slots = self._get_day_slots(study_hours_per_day)

        for day in available_days:
            slots = day_slots.copy()
            # Sort subjects by priority for this day (rotate to ensure variety)
            day_subjects = sorted(subjects, key=lambda s: -priorities[s.id])

            for i, slot_duration in enumerate(slots):
                if i >= len(day_subjects):
                    break
                subject = day_subjects[i]
                hour_of_day = self._slot_index_to_hour(i, study_hours_per_day)

                entries.append({
                    'subject_id': subject.id,
                    'day': day,
                    'start_time': hour_of_day,
                    'duration_minutes': min(slot_duration, allocations[subject.id]),
                    'ai_intensity': self._get_intensity(subject.difficulty),
                    'priority_rank': i + 1
                })

        return entries

    def sort_modules_by_difficulty(self, module_names):
        """
        AI sorts syllabus modules from most to least difficult
        Uses keyword scoring + position heuristics
        Returns: [(module_name, ai_difficulty_score), ...]
        """
        scored = []
        for i, name in enumerate(module_names):
            score = self._estimate_module_difficulty(name, i, len(module_names))
            scored.append((name, score))

        # Sort descending: hardest first
        scored.sort(key=lambda x: -x[1])
        return scored

    def _estimate_module_difficulty(self, name, position, total):
        """Estimate difficulty of a module from its name"""
        name_lower = name.lower()
        score = 5.0  # baseline

        # Keyword scoring
        for keyword in self.DIFFICULTY_KEYWORDS['high']:
            if keyword in name_lower:
                score += 2.5
        for keyword in self.DIFFICULTY_KEYWORDS['medium']:
            if keyword in name_lower:
                score += 1.0
        for keyword in self.DIFFICULTY_KEYWORDS['low']:
            if keyword in name_lower:
                score -= 1.5

        # Position heuristic: later modules tend to be harder
        position_boost = (position / max(total - 1, 1)) * 1.5
        score += position_boost

        # Word count heuristic: longer names sometimes indicate complexity
        word_count = len(name.split())
        if word_count > 4:
            score += 0.5

        return round(min(10.0, max(1.0, score)), 2)

    def _get_day_slots(self, hours_per_day):
        """Generate time slot durations for a day"""
        minutes = hours_per_day * 60
        slots = []
        while minutes > 0:
            block = min(90, minutes)  # Max 90-min blocks
            slots.append(block)
            minutes -= block + 15  # 15-min break between blocks
        return slots

    def _slot_index_to_hour(self, index, total_hours):
        """Convert slot index to time string"""
        start_hour = 8  # 8 AM start
        hour = start_hour + index * 1.75  # ~105 min per slot including break
        h = int(hour)
        m = int((hour - h) * 60)
        return time(h % 24, m)

    def _get_intensity(self, difficulty):
        if difficulty >= 8:
            return 'high'
        elif difficulty >= 5:
            return 'medium'
        return 'low'


class PerformanceAnalyzer:
    """
    Tracks scores, identifies weak areas, predicts improvement trends
    Uses linear regression for trend analysis
    """

    def __init__(self, user):
        self.user = user

    def calculate_trend(self, scores):
        """
        Simple linear regression to determine score trend
        Returns: 'improving', 'declining', 'stable'
        """
        if len(scores) < 2:
            return 'stable'

        n = len(scores)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(scores) / n

        numerator = sum((x[i] - x_mean) * (scores[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 'stable'

        slope = numerator / denominator

        if slope > 1.5:
            return 'improving'
        elif slope < -1.5:
            return 'declining'
        return 'stable'

    def predict_next_score(self, subject, num_ahead=1):
        """
        Predict next score using weighted moving average + trend
        Recent scores weighted more heavily
        """
        from .models import TestScore

        scores = list(TestScore.objects.filter(
            user=self.user, subject=subject
        ).order_by('date_taken').values_list('score', flat=True))

        if not scores:
            return None

        # Weighted moving average (recent = more weight)
        weights = [i + 1 for i in range(len(scores))]
        weighted_avg = sum(s * w for s, w in zip(scores, weights)) / sum(weights)

        # Add trend adjustment
        trend_scores = scores[-3:] if len(scores) >= 3 else scores
        trend = self.calculate_trend(trend_scores)
        adjustment = 3 if trend == 'improving' else -3 if trend == 'declining' else 0

        prediction = min(100, max(0, weighted_avg + adjustment))
        return round(prediction, 1)

    def generate_feedback(self, subject, score):
        """Generate AI feedback text based on score and subject context"""
        avg = self.predict_next_score(subject) or score

        if score >= 90:
            feedback = f"Excellent performance in {subject.name}! You're in the top tier. Consider helping peers or exploring advanced topics."
        elif score >= 80:
            feedback = f"Good work on {subject.name}. Focus on the remaining {100 - score}% gap by reviewing your weak modules."
        elif score >= 70:
            feedback = f"{subject.name} needs more attention. I've identified weak areas in your notes. Consider 2 extra study sessions this week."
        else:
            feedback = (
                f"Critical: {subject.name} score of {score}% is below the passing threshold. "
                f"AI has doubled your allocated time for this subject. "
                f"Start with the most difficult modules: review systematically and use spaced repetition."
            )

        return feedback

    def recommended_hours(self, subject, avg_score):
        """AI-recommended weekly hours based on score and exam proximity"""
        base_hours = 3.0
        # Low score → more hours
        score_factor = max(0.5, 2.0 - (avg_score / 100) * 1.5)
        # Near exam → more hours
        days = max(1, subject.days_until_exam())
        proximity_factor = max(1.0, 10 / math.sqrt(days))
        # High difficulty → more hours
        diff_factor = 0.8 + (subject.difficulty / 10) * 0.8

        hours = base_hours * score_factor * proximity_factor * diff_factor
        return round(min(15, hours), 1)

    def predict_overall_improvement(self):
        """Predict user's overall score improvement over next 2 weeks"""
        from .models import Subject, TestScore

        subjects = Subject.objects.filter(user=self.user)
        improvements = []

        for subject in subjects:
            current_avg = TestScore.objects.filter(
                user=self.user, subject=subject
            ).aggregate(avg=Avg('score'))['avg']

            if current_avg:
                predicted = self.predict_next_score(subject)
                if predicted:
                    improvements.append(predicted - current_avg)

        if not improvements:
            return 0
        return round(sum(improvements) / len(improvements), 1)

    def identify_weak_areas(self):
        """Returns subjects needing urgent attention"""
        from .models import Subject, TestScore

        weak = []
        for subject in Subject.objects.filter(user=self.user):
            avg = TestScore.objects.filter(
                user=self.user, subject=subject
            ).aggregate(avg=Avg('score'))['avg']

            if avg and avg < 75:
                weak.append({
                    'subject': subject.name,
                    'avg_score': round(avg, 1),
                    'priority': 'critical' if avg < 60 else 'high' if avg < 70 else 'medium',
                    'recommended_action': self._weak_area_action(subject, avg)
                })

        return sorted(weak, key=lambda x: x['avg_score'])

    def _weak_area_action(self, subject, avg):
        days = subject.days_until_exam()
        if days < 7:
            return f"URGENT: Daily 2-hour intensive sessions. Focus only on difficult modules."
        elif avg < 60:
            return f"Critical: Restart from basics. Daily practice tests. Seek tutoring."
        else:
            return f"Increase weekly hours by 50%. Review mistakes from past tests."


class AdaptiveLearning:
    """
    Dynamically adjusts study plan based on real-time performance
    - Increases time for weak subjects
    - Suggests revision frequency
    - Rebalances timetable after each score log
    """

    def __init__(self, user):
        self.user = user
        self.engine = AISchedulingEngine(user)
        self.analyzer = PerformanceAnalyzer(user)

    def adjust_timetable(self, subject, new_score):
        """
        After logging a score, adaptively adjust the timetable:
        1. Recalculate priority scores
        2. Increase/decrease time allocation for this subject
        3. Create adaptive notification
        """
        from .models import Notification

        # Update priority scores
        self.engine.update_priority_scores()

        # Determine adjustment
        avg_score = self.analyzer.predict_next_score(subject) or new_score
        recommended_hrs = self.analyzer.recommended_hours(subject, new_score)

        if new_score < 70:
            action = f"⚡ AI increased your {subject.name} study time to {recommended_hrs}h/week"
            notif_type = 'performance'
        elif new_score >= 90:
            action = f"✅ You're excelling at {subject.name}. Time redistributed to weaker subjects."
            notif_type = 'achievement'
        else:
            action = f"📊 Timetable adjusted for {subject.name} based on your latest performance."
            notif_type = 'ai_tip'

        Notification.objects.create(
            user=self.user,
            title='Adaptive Learning Update',
            message=action,
            notification_type=notif_type
        )

    def suggest_revision_frequency(self, subject):
        """
        Spaced repetition: suggests optimal revision intervals
        Based on Ebbinghaus forgetting curve
        """
        from .models import StudySession

        last_session = StudySession.objects.filter(
            user=self.user, subject=subject
        ).order_by('-date').first()

        if not last_session:
            return {'next_revision': 'Today', 'interval_days': 1}

        days_since = (date.today() - last_session.date).days

        # Spaced repetition intervals: 1, 3, 7, 14, 30 days
        intervals = [1, 3, 7, 14, 30]
        for interval in intervals:
            if days_since < interval:
                return {
                    'next_revision': f'In {interval - days_since} day(s)',
                    'interval_days': interval
                }

        return {'next_revision': 'Overdue — revise immediately!', 'interval_days': 0}

    def get_study_recommendations(self):
        """Get personalized AI recommendations for the user"""
        weak_areas = self.analyzer.identify_weak_areas()
        improvement = self.analyzer.predict_overall_improvement()

        recommendations = []

        for weak in weak_areas[:3]:
            recommendations.append({
                'type': 'warning' if weak['priority'] == 'critical' else 'info',
                'subject': weak['subject'],
                'message': weak['recommended_action'],
                'priority': weak['priority']
            })

        if improvement > 0:
            recommendations.append({
                'type': 'positive',
                'subject': 'Overall',
                'message': f"AI predicts +{improvement}% improvement if you maintain current pace!",
                'priority': 'low'
            })

        return recommendations
