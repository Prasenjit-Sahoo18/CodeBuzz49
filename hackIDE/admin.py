#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: sahildua2305
# @Date:   2016-01-06 00:11:27
# @Last Modified by:   sahildua2305
# @Last Modified time: 2016-01-07 02:28:56


from django.contrib import admin
from .models import Contest, ContestProblem, ContestSubmission, ContestParticipant, StandaloneProblem, ContestAttachedProblem, ProctoringSession, ProctoringViolation

@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_time', 'end_time', 'is_active', 'requires_proctoring', 'created_at', 'first_prize', 'second_prize', 'third_prize']
    list_filter = ['is_active', 'requires_proctoring', 'start_time', 'end_time']
    search_fields = ['title', 'description']
    date_hierarchy = 'start_time'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'is_active')
        }),
        ('Schedule', {
            'fields': ('start_time', 'end_time')
        }),
        ('Security & Monitoring', {
            'fields': ('requires_proctoring',),
            'description': 'Enable camera verification and real-time monitoring for this contest'
        }),
        ('Prizes', {
            'fields': ('first_prize', 'second_prize', 'third_prize'),
            'classes': ('collapse',)
        }),
    )

@admin.register(StandaloneProblem)
class StandaloneProblemAdmin(admin.ModelAdmin):
    list_display = ['title', 'company_tag', 'difficulty', 'points', 'time_limit']
    list_filter = ['difficulty', 'points']
    search_fields = ['title', 'description', 'company_tag']
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'difficulty', 'points', 'is_premium', 'company_tag')
        }),
        ('Constraints', {
            'fields': ('time_limit', 'memory_limit')
        }),
        ('Function Signature (optional)', {
            'fields': ('signature_enabled', 'signature_name', 'signature_params', 'signature_return'),
        }),
        ('Evaluation', {
            'fields': ('test_cases', 'boilerplate_code'),
        }),
    )
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(contest__isnull=True)

@admin.register(ContestAttachedProblem)
class ContestAttachedProblemAdmin(admin.ModelAdmin):
    list_display = ['title', 'contest', 'difficulty', 'points', 'time_limit', 'company_tag']
    list_filter = ['contest', 'difficulty', 'points']
    search_fields = ['title', 'description', 'company_tag', 'contest__title']
    raw_id_fields = ['contest']
    fieldsets = (
        (None, {
            'fields': ('contest', 'title', 'description', 'difficulty', 'points', 'is_premium', 'company_tag')
        }),
        ('Constraints', {
            'fields': ('time_limit', 'memory_limit')
        }),
        ('Function Signature (optional)', {
            'fields': ('signature_enabled', 'signature_name', 'signature_params', 'signature_return'),
        }),
        ('Evaluation', {
            'fields': ('test_cases', 'boilerplate_code'),
        }),
    )
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(contest__isnull=False)

@admin.register(ContestSubmission)
class ContestSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'problem', 'language', 'status', 'score', 'submission_type', 'is_practice_submission', 'submitted_at']
    list_filter = ['status', 'language', 'submission_type', 'is_practice_submission', 'submitted_at']
    search_fields = ['user__username', 'problem__title']
    raw_id_fields = ['user', 'problem']
    readonly_fields = ['submitted_at']

@admin.register(ContestParticipant)
class ContestParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'contest', 'total_score', 'problems_solved', 'joined_at']
    list_filter = ['contest', 'joined_at']
    search_fields = ['user__username', 'contest__title']
    raw_id_fields = ['user', 'contest']
    readonly_fields = ['joined_at']

@admin.register(ProctoringSession)
class ProctoringSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'contest', 'face_detected', 'violation_count', 'contest_terminated', 'practice_mode', 'is_monitoring_active']
    list_filter = ['face_detected', 'contest_terminated', 'practice_mode', 'is_monitoring_active', 'contest']
    search_fields = ['user__username', 'contest__title']
    raw_id_fields = ['user', 'contest']
    readonly_fields = ['created_at', 'last_face_check', 'monitoring_started_at']
    
    actions = ['enable_practice_mode', 'disable_practice_mode', 'reset_violations']
    
    def enable_practice_mode(self, request, queryset):
        """Enable practice mode for selected users"""
        updated = 0
        for session in queryset:
            session.enable_practice_mode()
            updated += 1
        self.message_user(request, f'Practice mode enabled for {updated} users.')
    enable_practice_mode.short_description = "Enable practice mode"
    
    def disable_practice_mode(self, request, queryset):
        """Disable practice mode for selected users"""
        updated = queryset.update(practice_mode=False)
        self.message_user(request, f'Practice mode disabled for {updated} users.')
    disable_practice_mode.short_description = "Disable practice mode"
    
    def reset_violations(self, request, queryset):
        """Reset violation count for selected users"""
        updated = queryset.update(
            violation_count=0,
            warning_count=0,
            contest_terminated=False,
            practice_mode=False
        )
        self.message_user(request, f'Violations reset for {updated} users.')
    reset_violations.short_description = "Reset violations"

@admin.register(ProctoringViolation)
class ProctoringViolationAdmin(admin.ModelAdmin):
    list_display = ['proctoring_session', 'violation_type', 'warning_given', 'timestamp']
    list_filter = ['violation_type', 'warning_given', 'timestamp']
    search_fields = ['proctoring_session__user__username', 'proctoring_session__contest__title']
    raw_id_fields = ['proctoring_session']
    readonly_fields = ['timestamp']
