from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home & Dashboard
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password_view, name='change_password'),
    
    # User Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/setup/', views.profile_setup_view, name='profile_setup'),
    
    # Skill URLs
    path('skills/', views.skill_list_view, name='skill_list'),
    path('skills/create/', views.skill_create_view, name='skill_create'),
    path('skills/<uuid:pk>/edit/', views.skill_edit_view, name='skill_edit'),
    path('skills/<uuid:pk>/delete/', views.skill_delete_view, name='skill_delete'),
    path('skills/bulk-import/', views.bulk_skill_import_view, name='bulk_skill_import'),
    
    # Interview Domain URLs
    path('domains/', views.domain_list_view, name='domain_list'),
    path('domains/<slug:slug>/', views.domain_detail_view, name='domain_detail'),
    path('domains/create/', views.domain_create_view, name='domain_create'),
    path('domains/<slug:slug>/edit/', views.domain_edit_view, name='domain_edit'),
    path('domains/<slug:slug>/delete/', views.domain_delete_view, name='domain_delete'),
    
    # Job Role URLs
    path('job-roles/', views.job_role_list_view, name='job_role_list'),
    path('job-roles/<slug:slug>/', views.job_role_detail_view, name='job_role_detail'),
    path('job-roles/create/', views.job_role_create_view, name='job_role_create'),
    path('job-roles/<slug:slug>/edit/', views.job_role_edit_view, name='job_role_edit'),
    path('job-roles/<slug:slug>/delete/', views.job_role_delete_view, name='job_role_delete'),
    
    # Interview Session URLs
    path('sessions/', views.interview_session_list_view, name='session_list'),
    path('sessions/create/', views.interview_session_create_view, name='session_create'),
    path('sessions/<uuid:session_id>/', views.interview_session_detail_view, name='session_detail'),
    path('sessions/<uuid:session_id>/delete/', views.interview_session_delete_view, name='session_delete'),
    path('sessions/<uuid:session_id>/generate-questions/', 
         views.interview_session_questions_generate_view, 
         name='session_questions_generate'),
    path('sessions/<uuid:session_id>/take/', 
         views.interview_session_take_view, 
         name='session_take'),
    path('sessions/<uuid:session_id>/submit/', 
         views.interview_session_submit_view, 
         name='session_submit'),
    path('sessions/<uuid:session_id>/update-status/', 
         views.session_update_status_view, 
         name='session_update_status'),
    
    # Feedback Report URLs
    path('sessions/<uuid:session_id>/feedback/', 
         views.feedback_report_view, 
         name='feedback_report'),
    path('sessions/<uuid:session_id>/feedback/generate/', 
         views.feedback_report_generate_view, 
         name='feedback_report_generate'),
    path('sessions/<uuid:session_id>/feedback/edit/', 
         views.feedback_report_edit_view, 
         name='feedback_report_edit'),
    
    # Saved Questions URLs
    path('saved-questions/', views.saved_questions_list_view, name='saved_questions_list'),
    path('questions/<uuid:question_id>/save/', 
         views.saved_question_create_view, 
         name='saved_question_create'),
    path('saved-questions/<uuid:pk>/delete/', 
         views.saved_question_delete_view, 
         name='saved_question_delete'),
    
    # Session Notes URLs
    path('sessions/<uuid:session_id>/notes/', 
         views.session_notes_list_view, 
         name='session_notes_list'),
    path('sessions/<uuid:session_id>/notes/create/', 
         views.session_note_create_view, 
         name='session_note_create'),
    path('notes/<uuid:pk>/edit/', 
         views.session_note_edit_view, 
         name='session_note_edit'),
    path('notes/<uuid:pk>/delete/', 
         views.session_note_delete_view, 
         name='session_note_delete'),
    
    # Notification URLs
    path('notifications/', views.notification_list_view, name='notification_list'),
    path('notifications/<uuid:pk>/read/', 
         views.notification_mark_read_view, 
         name='notification_mark_read'),
    path('notifications/mark-all-read/', 
         views.notification_mark_all_read_view, 
         name='notification_mark_all_read'),
    path('notifications/<uuid:pk>/delete/', 
         views.notification_delete_view, 
         name='notification_delete'),
    
    # Performance Analytics URLs
    path('performance/', views.performance_dashboard_view, name='performance_dashboard'),
    
    # Activity Log URLs (Admin only)
    path('admin/activity-logs/', views.activity_log_list_view, name='activity_log_list'),
    
    # Search URLs
    path('search/', views.global_search_view, name='global_search'),
    
    # AJAX URLs
    path('ajax/user-stats/', views.ajax_user_stats_view, name='ajax_user_stats'),
    path('ajax/skill-autocomplete/', views.ajax_skill_autocomplete_view, name='ajax_skill_autocomplete'),
    
    # Error Pages
    path('no-permission/', views.no_permission_view, name='no_permission'),
]