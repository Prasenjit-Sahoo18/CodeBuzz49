#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: sahildua2305
# @Date:   2016-01-06 00:11:27
# @Last Modified by:   Sahil Dua
# @Last Modified time: 2016-08-10 23:58:19

from django.urls import path, re_path

from . import views

app_name = 'hackIDE'

urlpatterns = [
  # ex: /
  path('', views.index, name='index'),
  # ex: /editor/ - Code editor for authenticated users
  path('editor/', views.code_editor, name='code_editor'),
  # ex: /compile/
  path('compile/', views.compileCode, name='compile'),
  # ex: /run/
  path('run/', views.runCode, name='run'),
  # ex: /status/he_id/
  path('status/<str:he_id>/', views.getStatus, name='status'),
  # Contest URLs
  path('contests/', views.contest_list, name='contest_list'),
  path('contests/test/', views.contest_list_test, name='contest_list_test'),
  path('test/', views.test_simple, name='test_simple'),
  path('contests/<int:contest_id>/', views.contest_detail, name='contest_detail'),
  path('contests/<int:contest_id>/final-submit/', views.contest_final_submit, name='contest_final_submit'),
  path('contests/<int:contest_id>/problems/<int:problem_id>/', views.contest_problem, name='contest_problem'),
  path('contests/<int:contest_id>/leaderboard/', views.contest_leaderboard, name='contest_leaderboard'),
  path('contests/<int:contest_id>/proctor/face-check/', views.proctor_face_check, name='proctor_face_check'),
  
  # Camera test tool
  path('camera-test/', views.camera_test, name='camera_test'),
  
  # Real-time proctoring endpoints
  path('contests/<int:contest_id>/proctoring/start/', views.start_realtime_proctoring, name='start_realtime_proctoring'),
  path('contests/<int:contest_id>/proctoring/monitor/', views.realtime_face_monitor, name='realtime_face_monitor'),
  path('contests/<int:contest_id>/proctoring/status/', views.proctoring_status, name='proctoring_status'),
  path('contests/<int:contest_id>/proctoring/terminate/', views.terminate_contest, name='terminate_contest'),
  
  # Authentication URLs - MUST come before the regex pattern
  path('test-auth/', views.test_auth, name='test_auth'),
  path('login/', views.user_login, name='user_login'),
  path('signup/', views.user_signup, name='user_signup'),
  path('logout/', views.user_logout, name='user_logout'),
  path('admin-logout/', views.admin_logout, name='admin_logout'),
  path('profile/', views.user_profile, name='user_profile'),
  # Subscription URLs
  path('premium/', views.premium_plans, name='premium_plans'),
  path('premium/buy/<str:plan_name>/', views.buy_premium, name='buy_premium'),
  path('premium/problems/', views.premium_problems, name='premium_problems'),
  path('premium/callback/', views.razorpay_callback, name='razorpay_callback'),
  path('premium/problem/<int:problem_id>/', views.premium_problem_solve, name='premium_problem_solve'),
  path('premium/problem/<int:problem_id>/ai-solution/', views.get_ai_solution, name='get_ai_solution'),
  
  # ex: /code=ajSkHb/ - This must come LAST to avoid catching other URLs
  re_path(r'(?P<code_id>\w{0,50})/$', views.savedCodeView, name='saved-code'),
  
  # Test proctoring
  path('test-proctoring/', views.test_proctoring, name='test_proctoring'),
]
