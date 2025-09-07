#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: sahildua2305
# @Date:   2016-01-06 00:11:27
# @Last Modified by:   sahildua2305
# @Last Modified time: 2016-01-12 05:51:06


from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

# Create your models here.

# Commented out since we're not using MongoDB anymore
# class codes(Document):
#     code_id = StringField(required=True)
#     code_content = StringField(required=True)
#     lang = StringField(required=True)
#     code_input = StringField(required=True)
#     compile_status= StringField(required=True)
#     run_status_status=StringField(required=True)
#     run_status_time=StringField(required=True)
#     run_status_memory=StringField(required=True)
#     run_status_output=StringField(required=True)
#     run_status_stderr=StringField(required=True)

class Contest(models.Model):
    """Coding contest model"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    first_prize = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    second_prize = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    third_prize = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Proctoring configuration
    requires_proctoring = models.BooleanField(default=True, help_text="Enable camera verification and monitoring for this contest")
    
    def __str__(self):
        return self.title
    
    @property
    def is_running(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time
    
    @property
    def prize_summary(self):
        prizes = []
        if self.first_prize:
            prizes.append(f"🥇 ₹{self.first_prize}")
        if self.second_prize:
            prizes.append(f"🥈 ₹{self.second_prize}")
        if self.third_prize:
            prizes.append(f"🥉 ₹{self.third_prize}")
        return ", ".join(prizes) or "No prizes announced"

class ContestProblem(models.Model):
    """Individual problem within a contest"""
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='problems', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=[
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
    ])
    time_limit = models.IntegerField(default=1000)  # milliseconds
    memory_limit = models.IntegerField(default=256)  # MB
    # Use TextField to store JSON for Django versions without native JSONField
    test_cases = models.TextField(default='[]')  # JSON string of input/output pairs
    points = models.IntegerField(default=100)
    is_premium = models.BooleanField(default=False)
    boilerplate_code = models.TextField(default='{}')  # JSON mapping of language -> code
    # Optional company tag for premium problems
    company_tag = models.CharField(max_length=100, blank=True)
    # Optional LeetCode-like signature schema
    signature_enabled = models.BooleanField(default=False)
    signature_name = models.CharField(max_length=100, blank=True)
    signature_params = models.TextField(default='[]', blank=True)  # JSON list of {name, type}
    signature_return = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        contest_title = self.contest.title if self.contest else 'Standalone'
        return f"{contest_title} - {self.title}"

    def _generate_stub(self, language: str) -> str:
        import json as _json
        try:
            if not self.signature_enabled or not self.signature_name:
                return ''
            params = self.signature_params
            if isinstance(params, str):
                params = _json.loads(params or '[]')
            param_names = [p.get('name', 'arg') for p in params]
            return_type = self.signature_return or ''
            lname = language.upper()
            if lname == 'PYTHON':
                args = ', '.join(param_names)
                ret = 'pass'
                return f"# Complete the function below\n\ndef {self.signature_name}({args}):\n    {ret}\n\nif __name__ == '__main__':\n    # You can test your function here\n    pass\n"
            if lname == 'JAVA':
                # crude type mapping; default to int/String
                def jtype(t):
                    t = (t or '').lower()
                    return 'int' if t in ['int','integer','number'] else ('String' if t in ['str','string','text'] else 'int')
                args = ', '.join([f"{jtype(p.get('type'))} {p.get('name','arg')}" for p in params])
                rtype = jtype(return_type)
                return (
                    "import java.util.*;\n\n" 
                    "class Solution {\n" 
                    f"    public {rtype} {self.signature_name}({args}) {{\n" 
                    "        // TODO: implement\n" 
                    "        return 0;\n" 
                    "    }\n" 
                    "}\n\n" 
                    "public class Main {\n" 
                    "    public static void main(String[] args){\n" 
                    "        // You can test Solution here\n" 
                    "    }\n" 
                    "}\n"
                )
            if lname in ['CPP','C++']:
                def ctype(t):
                    t = (t or '').lower()
                    return 'int' if t in ['int','integer','number'] else 'string'
                args = ', '.join([f"{ctype(p.get('type'))} {p.get('name','arg')}" for p in params])
                rtype = ctype(return_type)
                return (
                    "#include <bits/stdc++.h>\nusing namespace std;\n\n" 
                    f"{rtype} {self.signature_name}({args}) {{\n    // TODO: implement\n    return { '0' if rtype=='int' else '""' };\n}}\n\n" 
                    "int main(){\n    ios::sync_with_stdio(false); cin.tie(nullptr);\n    // You can test your function here\n    return 0;\n}\n"
                )
            if lname == 'C':
                def ctype(t):
                    t = (t or '').lower()
                    return 'int'
                args = ', '.join([f"{ctype(p.get('type'))} {p.get('name','arg')}" for p in params])
                rtype = ctype(return_type)
                return (
                    f"{rtype} {self.signature_name}({args}) {{\n    // TODO: implement\n    return 0;\n}}\n\n" 
                    "int main(){\n    // You can test your function here\n    return 0;\n}\n"
                )
            if lname == 'JAVASCRIPT':
                args = ', '.join(param_names)
                return (
                    f"function {self.signature_name}({args}) {{\n  // TODO: implement\n}}\n\n" 
                    "function main(){\n  // You can test your function here\n}\n\nmain();\n"
                )
            return ''
        except Exception:
            return ''

    def get_test_cases(self):
        import json as _json
        try:
            value = self.test_cases
            if isinstance(value, str):
                return _json.loads(value or '[]')
            return value or []
        except Exception:
            return []

    def get_boilerplate_code(self, language: str = 'PYTHON') -> str:
        import json as _json
        try:
            # Built-in defaults
            default_map = {
                'PYTHON': "# Write your code here\n\nimport sys\n\ndef solve():\n    # TODO: implement\n    pass\n\nif __name__ == '__main__':\n    solve()\n",
                'JAVA': "// Write your code here\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // TODO: implement\n    }\n}\n",
                'CPP': "// Write your code here\n#include <bits/stdc++.h>\nusing namespace std;\n\nint main(){\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    // TODO: implement\n    return 0;\n}\n",
                'C': "// Write your code here\n#include <stdio.h>\n\nint main(){\n    // TODO: implement\n    return 0;\n}\n",
                'JAVASCRIPT': "// Write your code here\n'use strict';\n\nfunction main(){\n  // TODO: implement\n}\n\nmain();\n",
            }
            # Prefer generated stub when signature is enabled
            generated = self._generate_stub(language)
            if generated:
                return generated
            mapping = self.boilerplate_code
            if isinstance(mapping, str):
                mapping = _json.loads(mapping or '{}')
            code = (mapping.get(language)
                    or mapping.get(language.upper())
                    or default_map.get(language.upper())
                    or '')
            return code
        except Exception:
            return ''

    def get_boilerplate_map(self) -> dict:
        import json as _json
        try:
            # Built-in defaults
            default_map = {
                'PYTHON': "# Write your code here\n\nimport sys\n\ndef solve():\n    # TODO: implement\n    pass\n\nif __name__ == '__main__':\n    solve()\n",
                'JAVA': "// Write your code here\nimport java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        // TODO: implement\n    }\n}\n",
                'CPP': "// Write your code here\n#include <bits/stdc++.h>\nusing namespace std;\n\nint main(){\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n    // TODO: implement\n    return 0;\n}\n",
                'C': "// Write your code here\n#include <stdio.h>\n\nint main(){\n    // TODO: implement\n    return 0;\n}\n",
                'JAVASCRIPT': "// Write your code here\n'use strict';\n\nfunction main(){\n  // TODO: implement\n}\n\nmain();\n",
            }
            mapping = self.boilerplate_code
            if isinstance(mapping, str):
                mapping = _json.loads(mapping or '{}')
            mapping = mapping or {}
            # Start with defaults
            merged = dict(default_map)
            # Merge explicit custom
            merged.update({k.upper(): v for k, v in mapping.items()})
            # Merge generated signatures (do not override explicit custom)
            if self.signature_enabled and self.signature_name:
                for lang in ['PYTHON','JAVA','CPP','C','JAVASCRIPT']:
                    stub = self._generate_stub(lang)
                    if stub and lang not in mapping:
                        merged[lang] = stub
            return merged
        except Exception:
            return {}

class ContestSubmission(models.Model):
    """User submission for a contest problem"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(ContestProblem, on_delete=models.CASCADE)
    language = models.CharField(max_length=20)
    source_code = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    execution_time = models.FloatField(null=True, blank=True)
    memory_used = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('WRONG_ANSWER', 'Wrong Answer'),
        ('TIME_LIMIT', 'Time Limit Exceeded'),
        ('MEMORY_LIMIT', 'Memory Limit Exceeded'),
        ('RUNTIME_ERROR', 'Runtime Error'),
        ('COMPILATION_ERROR', 'Compilation Error'),
    ], default='PENDING')
    score = models.IntegerField(default=0)
    
    # Final submission tracking
    is_final_submission = models.BooleanField(default=False)
    submission_type = models.CharField(max_length=20, choices=[
        ('TEST', 'Test Submission'),
        ('FINAL', 'Final Submission'),
        ('PRACTICE', 'Practice Submission'),  # For violated users
    ], default='TEST')
    is_practice_submission = models.BooleanField(default=False)  # Excluded from leaderboard
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.problem.title} ({'Final' if self.is_final_submission else 'Test'})"
    
    def mark_as_final(self):
        """Mark this submission as the final submission for this problem"""
        # Mark any previous final submissions as non-final
        ContestSubmission.objects.filter(
            user=self.user,
            problem=self.problem,
            is_final_submission=True
        ).update(is_final_submission=False, submission_type='TEST')
        
        # Mark this submission as final
        self.is_final_submission = True
        self.submission_type = 'FINAL'
        self.save()
    
    @staticmethod
    def get_final_submission(user, problem):
        """Get the final submission for a user and problem"""
        try:
            return ContestSubmission.objects.get(
                user=user,
                problem=problem,
                is_final_submission=True
            )
        except ContestSubmission.DoesNotExist:
            return None
    
    @staticmethod
    def has_final_submission(user, problem):
        """Check if user has made a final submission for this problem"""
        return ContestSubmission.objects.filter(
            user=user,
            problem=problem,
            is_final_submission=True
        ).exists()

class ContestParticipant(models.Model):
    """User participation in a contest"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    total_score = models.IntegerField(default=0)
    problems_solved = models.IntegerField(default=0)
    
    # Contest-wide final submission tracking
    has_final_submitted = models.BooleanField(default=False)
    final_submitted_at = models.DateTimeField(null=True, blank=True)
    final_submission_score = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'contest']
    
    def __str__(self):
        return f"{self.user.username} in {self.contest.title}"
    
    def make_final_submission(self):
        """Mark contest as finally submitted by this participant"""
        from django.utils import timezone
        
        # Mark all user's submissions in this contest as final
        final_submissions = ContestSubmission.objects.filter(
            user=self.user,
            problem__contest=self.contest,
            status='ACCEPTED'  # Only consider accepted submissions for final
        )
        
        # Calculate final score from accepted submissions
        final_score = sum(submission.score for submission in final_submissions)
        
        # Update participant status
        self.has_final_submitted = True
        self.final_submitted_at = timezone.now()
        self.final_submission_score = final_score
        self.save()
        
        # Mark qualifying submissions as final
        final_submissions.update(is_final_submission=True, submission_type='FINAL')
        
        return final_score
    
    def get_final_submission_summary(self):
        """Get summary of final submissions for this contest"""
        if not self.has_final_submitted:
            return None
            
        final_submissions = ContestSubmission.objects.filter(
            user=self.user,
            problem__contest=self.contest,
            is_final_submission=True
        ).select_related('problem')
        
        return {
            'submitted_at': self.final_submitted_at,
            'total_score': self.final_submission_score,
            'problems_count': final_submissions.count(),
            'submissions': final_submissions
        }


class SubscriptionPlan(models.Model):
    """Subscription plan like Free, Pro, Premium"""
    PLAN_CHOICES = [
        ('FREE', 'Free'),
        ('PRO', 'Pro'),
        ('PREMIUM', 'Premium'),
    ]

    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price_inr = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    duration_days = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name


class Subscription(models.Model):
    """User subscription instance"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active', 'end_date']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.plan.display_name}"

    @property
    def is_current(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    @staticmethod
    def user_has_active(user: User) -> bool:
        now = timezone.now()
        # Admins (staff/superusers) always have premium access
        if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
            return True
        return Subscription.objects.filter(user=user, is_active=True, end_date__gte=now).exists()


class ProctoringSession(models.Model):
    """Proctoring session for contest monitoring"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='proctoring/', null=True, blank=True)
    face_detected = models.BooleanField(default=False)
    faces_count = models.IntegerField(default=0)
    details = models.TextField(blank=True)
    
    # Real-time monitoring fields
    is_monitoring_active = models.BooleanField(default=False)
    violation_count = models.IntegerField(default=0)
    warning_count = models.IntegerField(default=0)
    contest_terminated = models.BooleanField(default=False)
    practice_mode = models.BooleanField(default=False)  # Allow practice without monitoring
    last_face_check = models.DateTimeField(null=True, blank=True)
    monitoring_started_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'contest']

    def __str__(self):
        return f"ProctoringSession({self.user.username}, {self.contest.title})"
    
    def can_continue_contest(self):
        """Check if user can continue the contest based on violations"""
        return not self.contest_terminated and self.violation_count < 3
    
    def can_practice(self):
        """Check if user can practice (for learning) even with violations"""
        return self.practice_mode or not self.contest_terminated
    
    def enable_practice_mode(self):
        """Enable practice mode for violated users - allows coding without monitoring"""
        self.practice_mode = True
        self.is_monitoring_active = False
        self.save()
        return True
    
    def add_violation(self, violation_type, details=""):
        """Add a violation and check if contest should be terminated"""
        self.violation_count += 1
        if self.violation_count <= 2:
            self.warning_count += 1
        if self.violation_count >= 3:
            self.contest_terminated = True
            # Automatically enable practice mode for terminated users
            self.practice_mode = True
            self.is_monitoring_active = False
        self.save()
        
        # Create violation record
        ProctoringViolation.objects.create(
            proctoring_session=self,
            violation_type=violation_type,
            details=details,
            timestamp=timezone.now()
        )
        
        return self.violation_count


class ProctoringViolation(models.Model):
    """Individual proctoring violation during contest"""
    VIOLATION_TYPES = [
        ('FACE_NOT_DETECTED', 'Face Not Detected'),
        ('MULTIPLE_FACES', 'Multiple Faces Detected'),
        ('CAMERA_BLOCKED', 'Camera Blocked'),
        ('NO_CAMERA_ACCESS', 'No Camera Access'),
    ]
    
    proctoring_session = models.ForeignKey(ProctoringSession, on_delete=models.CASCADE, related_name='violations')
    violation_type = models.CharField(max_length=30, choices=VIOLATION_TYPES)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    warning_given = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Violation: {self.get_violation_type_display()} - {self.proctoring_session.user.username}"

class StandaloneProblem(ContestProblem):
    class Meta:
        proxy = True
        verbose_name = 'Standalone Problem'
        verbose_name_plural = 'Standalone Problems'

class ContestAttachedProblem(ContestProblem):
    class Meta:
        proxy = True
        verbose_name = 'Contest Problem'
        verbose_name_plural = 'Contest Problems'

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

	def __str__(self):
		return f"Profile({self.user.username})"
