from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.db.models import Q, Avg, Count, Sum, Max
from django.db.models.functions import TruncDate
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from decimal import Decimal

from .models import (
    User, UserProfile, Skill, InterviewDomain, JobRole,
    InterviewSession, InterviewQuestion, InterviewAnswer,
    FeedbackReport, SavedQuestion, SessionNote, Notification,
    ActivityLog, AIProviderLog, PerformanceSnapshot
)
from .forms import (
    CustomUserCreationForm, CustomUserChangeForm, UserProfileForm,
    SkillForm, InterviewDomainForm, JobRoleForm, InterviewSessionForm,
    InterviewQuestionForm, InterviewAnswerForm, FeedbackReportForm,
    SavedQuestionForm, SessionNoteForm, NotificationForm,
    InterviewSessionStatusForm, BulkSkillForm
)

# ===================== Helper Functions =====================

def log_activity(user, action, object_type=None, object_id=None, request=None, metadata=None):
    """Helper function to log user activities"""
    try:
        ActivityLog.objects.create(
            actor=user,
            action=action,
            object_type=object_type if object_type else '',
            object_id=str(object_id) if object_id else None,
            ip_address=request.META.get('REMOTE_ADDR') if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT') if request else None,
            metadata=metadata or {}
        )
    except Exception as e:
        print(f"Failed to log activity: {e}")

def staff_required(view_func):
    """Decorator to check if user is staff"""
    decorated_func = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url='no_permission'
    )(view_func)
    return decorated_func

def generate_questions_for_session(session):
    """Generate questions for an interview session based on job role"""
    questions_data = []
    
    # Sample questions based on job role
    if session.job_role:
        role_title = session.job_role.title.lower()
        
        if "python" in role_title or "developer" in role_title:
            questions_data = [
                'Explain the difference between lists and tuples in Python.',
                'What are decorators in Python and how do you use them?',
                'Describe the concept of Object-Oriented Programming (OOP).',
                'How do you handle exceptions in Python?',
                'What is your experience with Django or Flask frameworks?',
            ]
        elif "data" in role_title or "analyst" in role_title:
            questions_data = [
                'Explain the difference between SQL and NoSQL databases.',
                'What is your experience with data visualization tools?',
                'How do you handle missing data in a dataset?',
                'Explain the difference between supervised and unsupervised learning.',
                'What metrics would you use to evaluate a machine learning model?',
            ]
        else:
            questions_data = [
                'Tell me about yourself and your professional background.',
                'Why are you interested in this role?',
                'Describe a challenging situation you faced at work and how you handled it.',
                'What are your greatest strengths and weaknesses?',
                'Where do you see yourself in 5 years?',
            ]
    else:
        questions_data = [
            'Tell me about yourself.',
            'What are your career goals?',
            'Describe a time you demonstrated leadership.',
            'How do you handle pressure and tight deadlines?',
            'What motivates you to perform well at work?',
        ]
    
    created_count = 0
    for idx, question_text in enumerate(questions_data, start=1):
        try:
            InterviewQuestion.objects.create(
                session=session,
                question_text=question_text,
                question_type='BEHAVIORAL',
                order=idx,
            )
            created_count += 1
        except Exception as e:
            print(f"Error creating question {idx}: {e}")
    
    return created_count

# ===================== Authentication Views =====================

def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created successfully.')
            log_activity(user, 'user_registered', 'User', str(user.id), request)
            return redirect('profile_setup')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            log_activity(user, 'user_login', 'User', str(user.id), request)
            
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')

@login_required
def logout_view(request):
    """Custom logout view"""
    log_activity(request.user, 'user_logout', 'User', str(request.user.id), request)
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def profile_setup_view(request):
    """Profile setup view for new users"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            log_activity(request.user, 'profile_updated', 'UserProfile', str(profile.id), request)
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'profile_setup.html', {'form': form})

@login_required
def change_password_view(request):
    """Password change view"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed successfully!')
            log_activity(request.user, 'password_changed', 'User', str(request.user.id), request)
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'change_password.html', {'form': form})

# ===================== Dashboard Views =====================

@login_required
def dashboard_view(request):
    """Main dashboard view"""
    user = request.user
    
    total_sessions = InterviewSession.objects.filter(user=user).count()
    completed_sessions = InterviewSession.objects.filter(
        user=user, status=InterviewSession.Status.COMPLETED
    ).count()
    avg_score = InterviewSession.objects.filter(
        user=user, status=InterviewSession.Status.COMPLETED
    ).aggregate(Avg('overall_score'))['overall_score__avg'] or 0
    
    recent_sessions = InterviewSession.objects.filter(user=user).order_by('-created_at')[:5]
    
    pending_notifications = Notification.objects.filter(
        recipient=user, is_read=False
    ).count()
    
    recent_notifications = Notification.objects.filter(
        recipient=user
    ).order_by('-created_at')[:5]
    
    context = {
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'avg_score': round(avg_score, 2),
        'recent_sessions': recent_sessions,
        'pending_notifications': pending_notifications,
        'notifications': recent_notifications,
    }
    
    log_activity(user, 'dashboard_viewed', 'Dashboard', None, request)
    return render(request, 'dashboard.html', context)

# ===================== User Profile Views =====================

@login_required
def profile_view(request):
    """View user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'profile': profile})

@login_required
def profile_edit_view(request):
    """Edit user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Save user form
            user_form.save()
            
            # Save profile form
            profile_instance = profile_form.save(commit=False)
            
            # Ensure skills is a list (not None)
            if profile_instance.skills is None:
                profile_instance.skills = []
            
            profile_instance.save()
            profile_form.save_m2m()  # Save many-to-many relationships
            
            messages.success(request, 'Your profile has been updated successfully!')
            log_activity(request.user, 'profile_updated', 'UserProfile', str(profile.id), request)
            return redirect('profile')
        else:
            # Print form errors for debugging
            if user_form.errors:
                print("User form errors:", user_form.errors)
            if profile_form.errors:
                print("Profile form errors:", profile_form.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = CustomUserChangeForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    return render(request, 'profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

# ===================== Skill Views =====================

@login_required
@staff_required
def skill_list_view(request):
    """List all skills with search functionality"""
    skills = Skill.objects.all().order_by('name')
    
    search_query = request.GET.get('search', '')
    if search_query:
        skills = skills.filter(Q(name__icontains=search_query) | Q(slug__icontains=search_query))
    
    paginator = Paginator(skills, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'skills/list.html', {'page_obj': page_obj, 'search_query': search_query})

@login_required
@staff_required
def skill_create_view(request):
    """Create a new skill"""
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save()
            messages.success(request, f'Skill "{skill.name}" has been created.')
            log_activity(request.user, 'skill_created', 'Skill', str(skill.id), request)
            return redirect('skill_list')
    else:
        form = SkillForm()
    
    return render(request, 'skills/form.html', {'form': form, 'title': 'Create Skill'})

@login_required
@staff_required
def skill_edit_view(request, pk):
    """Edit an existing skill"""
    skill = get_object_or_404(Skill, pk=pk)
    
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            skill = form.save()
            messages.success(request, f'Skill "{skill.name}" has been updated.')
            log_activity(request.user, 'skill_updated', 'Skill', str(skill.id), request)
            return redirect('skill_list')
    else:
        form = SkillForm(instance=skill)
    
    return render(request, 'skills/form.html', {'form': form, 'title': 'Edit Skill', 'skill': skill})

@login_required
@staff_required
def skill_delete_view(request, pk):
    """Delete a skill"""
    skill = get_object_or_404(Skill, pk=pk)
    
    if request.method == 'POST':
        skill_name = skill.name
        skill.delete()
        messages.success(request, f'Skill "{skill_name}" has been deleted.')
        log_activity(request.user, 'skill_deleted', 'Skill', str(pk), request)
        return redirect('skill_list')
    
    return render(request, 'skills/delete.html', {'skill': skill})

@login_required
@staff_required
def bulk_skill_import_view(request):
    """Bulk import skills"""
    if request.method == 'POST':
        form = BulkSkillForm(request.POST)
        if form.is_valid():
            skills_data = form.cleaned_data['skills']
            created_count = 0
            existing_count = 0
            
            for skill_name in skills_data:
                skill, created = Skill.objects.get_or_create(
                    name=skill_name,
                    defaults={'slug': skill_name.lower().replace(' ', '-')}
                )
                if created:
                    created_count += 1
                else:
                    existing_count += 1
            
            messages.success(request, f'Imported {created_count} new skills. {existing_count} already existed.')
            log_activity(request.user, 'bulk_skill_import', 'Skill', None, request, {'created': created_count, 'existing': existing_count})
            return redirect('skill_list')
    else:
        form = BulkSkillForm()
    
    return render(request, 'skills/bulk_import.html', {'form': form})

# ===================== Interview Domain Views =====================

@login_required
def domain_list_view(request):
    """List interview domains with filtering"""
    domains = InterviewDomain.objects.filter(is_active=True)
    
    domain_type = request.GET.get('type')
    if domain_type:
        domains = domains.filter(domain_type=domain_type)
    
    search_query = request.GET.get('search')
    if search_query:
        domains = domains.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
    
    paginator = Paginator(domains, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'domains/list.html', {'page_obj': page_obj, 'search_query': search_query})

@login_required
def domain_detail_view(request, slug):
    """Domain detail view with job roles"""
    domain = get_object_or_404(InterviewDomain, slug=slug, is_active=True)
    job_roles = domain.job_roles.filter(is_active=True)
    
    difficulty = request.GET.get('difficulty')
    if difficulty:
        job_roles = job_roles.filter(difficulty=difficulty)
    
    return render(request, 'domains/detail.html', {
        'domain': domain,
        'job_roles': job_roles
    })

@login_required
@staff_required
def domain_create_view(request):
    """Create a new interview domain"""
    if request.method == 'POST':
        form = InterviewDomainForm(request.POST)
        if form.is_valid():
            domain = form.save()
            messages.success(request, f'Domain "{domain.title}" has been created.')
            log_activity(request.user, 'domain_created', 'InterviewDomain', str(domain.id), request)
            return redirect('domain_list')
    else:
        form = InterviewDomainForm()
    
    return render(request, 'domains/form.html', {'form': form, 'title': 'Create Domain'})

@login_required
@staff_required
def domain_edit_view(request, slug):
    """Edit an interview domain"""
    domain = get_object_or_404(InterviewDomain, slug=slug)
    
    if request.method == 'POST':
        form = InterviewDomainForm(request.POST, instance=domain)
        if form.is_valid():
            domain = form.save()
            messages.success(request, f'Domain "{domain.title}" has been updated.')
            log_activity(request.user, 'domain_updated', 'InterviewDomain', str(domain.id), request)
            return redirect('domain_list')
    else:
        form = InterviewDomainForm(instance=domain)
    
    return render(request, 'domains/form.html', {'form': form, 'title': 'Edit Domain', 'domain': domain})

@login_required
@staff_required
def domain_delete_view(request, slug):
    """Delete an interview domain"""
    domain = get_object_or_404(InterviewDomain, slug=slug)
    
    if request.method == 'POST':
        domain_title = domain.title
        domain.delete()
        messages.success(request, f'Domain "{domain_title}" has been deleted.')
        log_activity(request.user, 'domain_deleted', 'InterviewDomain', None, request)
        return redirect('domain_list')
    
    return render(request, 'domains/delete.html', {'domain': domain})

# ===================== Job Role Views =====================

@login_required
def job_role_list_view(request):
    """List all job roles with filtering"""
    job_roles = JobRole.objects.filter(is_active=True).select_related('domain')
    
    domain_id = request.GET.get('domain')
    if domain_id:
        job_roles = job_roles.filter(domain_id=domain_id)
    
    difficulty = request.GET.get('difficulty')
    if difficulty:
        job_roles = job_roles.filter(difficulty=difficulty)
    
    search_query = request.GET.get('search')
    if search_query:
        job_roles = job_roles.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
    
    paginator = Paginator(job_roles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    domains = InterviewDomain.objects.filter(is_active=True)
    
    return render(request, 'job_roles/list.html', {
        'page_obj': page_obj,
        'domains': domains,
        'search_query': search_query
    })

@login_required
def job_role_detail_view(request, slug):
    """Job role detail view"""
    job_role = get_object_or_404(JobRole, slug=slug, is_active=True)
    return render(request, 'job_roles/detail.html', {'job_role': job_role})

@login_required
@staff_required
def job_role_create_view(request):
    """Create a new job role"""
    if request.method == 'POST':
        form = JobRoleForm(request.POST)
        if form.is_valid():
            job_role = form.save()
            messages.success(request, f'Job role "{job_role.title}" has been created.')
            log_activity(request.user, 'job_role_created', 'JobRole', str(job_role.id), request)
            return redirect('job_role_list')
    else:
        form = JobRoleForm()
    
    return render(request, 'job_roles/form.html', {'form': form, 'title': 'Create Job Role'})

@login_required
@staff_required
def job_role_edit_view(request, slug):
    """Edit a job role"""
    job_role = get_object_or_404(JobRole, slug=slug)
    
    if request.method == 'POST':
        form = JobRoleForm(request.POST, instance=job_role)
        if form.is_valid():
            job_role = form.save()
            messages.success(request, f'Job role "{job_role.title}" has been updated.')
            log_activity(request.user, 'job_role_updated', 'JobRole', str(job_role.id), request)
            return redirect('job_role_list')
    else:
        form = JobRoleForm(instance=job_role)
    
    return render(request, 'job_roles/form.html', {'form': form, 'title': 'Edit Job Role', 'job_role': job_role})

@login_required
@staff_required
def job_role_delete_view(request, slug):
    """Delete a job role"""
    job_role = get_object_or_404(JobRole, slug=slug)
    
    if request.method == 'POST':
        job_role_title = job_role.title
        job_role.delete()
        messages.success(request, f'Job role "{job_role_title}" has been deleted.')
        log_activity(request.user, 'job_role_deleted', 'JobRole', None, request)
        return redirect('job_role_list')
    
    return render(request, 'job_roles/delete.html', {'job_role': job_role})

# ===================== Interview Session Views =====================

@login_required
def interview_session_list_view(request):
    """List all interview sessions for the user"""
    sessions = InterviewSession.objects.filter(user=request.user)
    
    status_filter = request.GET.get('status')
    if status_filter:
        sessions = sessions.filter(status=status_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        sessions = sessions.filter(title__icontains=search_query)
    
    paginator = Paginator(sessions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'sessions/list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query
    })

@login_required
def interview_session_create_view(request):
    """Create a new interview session"""
    if request.method == 'POST':
        form = InterviewSessionForm(request.POST, user=request.user)
        if form.is_valid():
            session = form.save()
            messages.success(request, f'Interview session "{session.title}" has been created.')
            log_activity(request.user, 'session_created', 'InterviewSession', str(session.id), request)
            
            question_count = generate_questions_for_session(session)
            
            if question_count > 0:
                session.status = InterviewSession.Status.QUESTIONS_GENERATED
                session.save()
                messages.success(request, f'{question_count} questions have been generated for this session.')
                return redirect('session_take', session_id=session.id)
            else:
                messages.warning(request, 'No questions were generated. Please try again.')
                return redirect('session_detail', session_id=session.id)
    else:
        form = InterviewSessionForm(user=request.user)
    
    return render(request, 'sessions/create.html', {'form': form})

@login_required
def interview_session_detail_view(request, session_id):
    """Interview session detail view"""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    questions = session.questions.all().order_by('order')
    
    # Fix: Get answers for this specific session
    answers = InterviewAnswer.objects.filter(
        question__session=session, 
        user=request.user
    )
    
    # Create a dictionary of answered question IDs for quick lookup
    answered_question_ids = set(answers.values_list('question_id', flat=True))
    
    # Add answered status to each question
    questions_with_status = []
    for question in questions:
        questions_with_status.append({
            'question': question,
            'is_answered': question.id in answered_question_ids,
            'answer': answers.filter(question=question).first()
        })
    
    total_questions = questions.count()
    answered_count = len(answered_question_ids)
    progress = (answered_count / total_questions * 100) if total_questions > 0 else 0
    
    # Get session status display
    status_display = dict(InterviewSession.Status.choices).get(session.status, session.status)
    
    context = {
        'session': session,
        'questions_with_status': questions_with_status,
        'questions': questions,
        'answers': answers,
        'progress': round(progress, 1),
        'total_questions': total_questions,
        'answered_count': answered_count,
        'status_display': status_display,
        'unanswered_count': total_questions - answered_count,
    }
    
    return render(request, 'sessions/detail.html', context)
@login_required
def interview_session_questions_generate_view(request, session_id):
    """Generate questions for the interview session"""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    
    if session.status != InterviewSession.Status.CREATED:
        messages.warning(request, 'Questions have already been generated for this session.')
        return redirect('session_detail', session_id=session.id)
    
    question_count = generate_questions_for_session(session)
    
    if question_count > 0:
        session.status = InterviewSession.Status.QUESTIONS_GENERATED
        session.save()
        messages.success(request, f'{question_count} questions have been generated successfully!')
        log_activity(request.user, 'questions_generated', 'InterviewSession', str(session.id), request)
    else:
        messages.error(request, 'Failed to generate questions. Please try again.')
        return redirect('session_detail', session_id=session.id)
    
    return redirect('session_take', session_id=session.id)

@login_required
def interview_session_take_view(request, session_id):
    """Take the interview session"""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    
    questions = session.questions.all().order_by('order')
    
    if not questions.exists():
        messages.warning(request, 'No questions available for this session. Please generate questions first.')
        return redirect('session_questions_generate', session_id=session.id)
    
    # Get answered questions for this session
    answered_questions = InterviewAnswer.objects.filter(
        question__session=session, 
        user=request.user
    )
    answered_question_ids = set(answered_questions.values_list('question_id', flat=True))
    
    # Find current question (first unanswered)
    current_question = None
    current_index = 0
    
    for idx, q in enumerate(questions):
        if q.id not in answered_question_ids:
            current_question = q
            current_index = idx + 1
            break
    
    # If all questions answered, go to submit page
    if not current_question:
        if session.status != InterviewSession.Status.SUBMITTED:
            return redirect('session_submit', session_id=session.id)
        else:
            messages.info(request, 'This session has already been submitted.')
            return redirect('session_detail', session_id=session.id)
    
    # Start the session if not already started
    if not session.started_at:
        session.started_at = timezone.now()
        session.status = InterviewSession.Status.IN_PROGRESS
        session.save()
        log_activity(request.user, 'session_started', 'InterviewSession', str(session.id), request)
        messages.info(request, 'Interview started! Answer each question to the best of your ability.')
    
    # Get existing answer for current question if any
    existing_answer = InterviewAnswer.objects.filter(
        question=current_question, 
        user=request.user
    ).first()
    
    if request.method == 'POST':
        form = InterviewAnswerForm(request.POST, instance=existing_answer)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = current_question
            answer.user = request.user
            answer.submitted_at = timezone.now()
            answer.save()
            
            messages.success(request, f'Answer saved for Question {current_index}!')
            log_activity(request.user, 'answer_submitted', 'InterviewAnswer', str(answer.id), request)
            
            # Check if this was the last question
            total_answered = answered_questions.count() + 1
            if total_answered == questions.count():
                messages.info(request, 'Congratulations! You have answered all questions. Please submit your interview.')
                return redirect('session_submit', session_id=session.id)
            
            # Redirect to the same session to show next question
            return redirect('session_take', session_id=session.id)
    else:
        form = InterviewAnswerForm(instance=existing_answer)
    
    total_questions = questions.count()
    answered_count = len(answered_question_ids)
    progress = (answered_count / total_questions * 100) if total_questions > 0 else 0
    is_last_question = (answered_count + 1) == total_questions
    
    context = {
        'session': session,
        'question': current_question,
        'form': form,
        'progress': round(progress, 1),
        'question_number': current_index,
        'total_questions': total_questions,
        'answered_count': answered_count,
        'is_last_question': is_last_question,
    }
    
    return render(request, 'sessions/take.html', context)

@login_required
def interview_session_submit_view(request, session_id):
    """Submit the interview session for evaluation"""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    
    # Check if already submitted
    if session.status == InterviewSession.Status.SUBMITTED:
        messages.warning(request, 'This session has already been submitted.')
        return redirect('session_detail', session_id=session.id)
    
    # Check if session is in progress
    if session.status != InterviewSession.Status.IN_PROGRESS:
        messages.warning(request, 'This session cannot be submitted.')
        return redirect('session_detail', session_id=session.id)
    
    # Check if all questions are answered
    total_questions = session.questions.count()
    answers = InterviewAnswer.objects.filter(
        question__session=session, 
        user=request.user
    )
    answered_count = answers.count()
    
    if answered_count < total_questions:
        messages.error(
            request, 
            f'Please answer all questions before submitting. ({answered_count}/{total_questions} completed)'
        )
        return redirect('session_take', session_id=session.id)
    
    if request.method == 'POST':
        # Auto-evaluate answers
        from decimal import Decimal
        
        total_score = Decimal('0.00')
        for answer in answers:
            answer_text = answer.answer_text or ""
            answer_length = len(answer_text)
            
            # Simple scoring logic
            if answer_length == 0:
                score = Decimal('0.00')
            elif answer_length < 50:
                score = Decimal('40.00')
            elif answer_length < 100:
                score = Decimal('60.00')
            elif answer_length < 200:
                score = Decimal('75.00')
            elif answer_length < 300:
                score = Decimal('85.00')
            else:
                score = Decimal('90.00')
            
            answer.score = score
            answer.save()
            total_score += score
        
        overall_score = (total_score / answered_count).quantize(Decimal('0.01'))
        
        # Update session
        session.submitted_at = timezone.now()
        session.completed_at = timezone.now()
        session.overall_score = overall_score
        session.status = InterviewSession.Status.EVALUATED
        session.evaluated_at = timezone.now()
        session.save()
        
        # Create feedback report
        from .models import FeedbackReport
        report, created = FeedbackReport.objects.get_or_create(session=session)
        report.generated_by_model = "Auto Evaluation"
        report.final_score = overall_score
        report.report_summary = f"You scored {overall_score}% on this interview based on {answered_count} questions."
        report.technical_feedback = "Your answers demonstrate good understanding of the topics."
        report.communication_feedback = "Your responses are clear and well-structured."
        report.improvement_plan = "Continue practicing with more questions to improve your score."
        report.recommended_resources = [
            "Practice more interview questions",
            "Review common interview topics",
            "Record yourself answering questions"
        ]
        report.save()
        
        messages.success(
            request, 
            f'Your interview has been submitted and evaluated! Score: {overall_score}%'
        )
        log_activity(request.user, 'session_submitted', 'InterviewSession', str(session.id), request)
        
        # Create notification
        Notification.objects.create(
            recipient=request.user,
            notification_type=Notification.Type.REPORT_READY,
            title='Interview Report Ready!',
            message=f'Your interview "{session.title}" scored {overall_score}%. Check your feedback report!'
        )
        
        return redirect('feedback_report', session_id=session.id)
    
    # For GET request - show confirmation page
    answered_ids = answers.values_list('question_id', flat=True)
    unanswered_questions = session.questions.exclude(id__in=answered_ids)
    
    context = {
        'session': session,
        'total_questions': total_questions,
        'answered_count': answered_count,
        'unanswered_count': unanswered_questions.count(),
        'unanswered_questions': unanswered_questions,
    }
    
    return render(request, 'sessions/submit.html', context)

@login_required
def interview_session_delete_view(request, session_id):
    """Delete an interview session"""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    
    if request.method == 'POST':
        session_title = session.title
        session.delete()
        messages.success(request, f'Interview session "{session_title}" has been deleted.')
        log_activity(request.user, 'session_deleted', 'InterviewSession', str(session_id), request)
        return redirect('session_list')
    
    return render(request, 'sessions/delete.html', {'session': session})

@login_required
def session_update_status_view(request, session_id):
    """Update session status (AJAX or form)"""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    
    if request.method == 'POST':
        form = InterviewSessionStatusForm(request.POST)
        if form.is_valid():
            session.status = form.cleaned_data['status']
            session.failure_reason = form.cleaned_data.get('failure_reason', '')
            
            if session.status == InterviewSession.Status.COMPLETED:
                session.completed_at = timezone.now()
            elif session.status == InterviewSession.Status.EVALUATED:
                session.evaluated_at = timezone.now()
            
            session.save()
            messages.success(request, f'Session status updated to {session.get_status_display()}')
            log_activity(request.user, 'session_status_updated', 'InterviewSession', str(session.id), request, {'status': session.status})
    
    return redirect('session_detail', session_id=session.id)

# ===================== Feedback Report Views =====================

@login_required
def feedback_report_view(request, session_id):
    """View feedback report for a session"""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    
    try:
        report = FeedbackReport.objects.get(session=session)
    except FeedbackReport.DoesNotExist:
        messages.warning(request, 'Feedback report is not yet available. Please check back later.')
        return redirect('session_detail', session_id=session.id)
    
    return render(request, 'feedback/report.html', {
        'session': session,
        'report': report
    })

@login_required
def feedback_report_generate_view(request, session_id):
    """Generate feedback report with scores"""
    session = get_object_or_404(InterviewSession, id=session_id)
    
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to generate reports.')
        return redirect('session_detail', session_id=session.id)
    
    answers = InterviewAnswer.objects.filter(question__session=session, user=session.user)
    
    if not answers.exists():
        messages.error(request, 'No answers found for this session.')
        return redirect('session_detail', session_id=session.id)
    
    # Calculate scores for each answer
    total_score = Decimal('0.00')
    
    for answer in answers:
        # Simple scoring logic based on answer length and keywords
        # In production, this would call an AI service
        answer_text = answer.answer_text or ""
        answer_length = len(answer_text)
        
        # Base score on length (minimum 40, maximum 95)
        if answer_length == 0:
            score = Decimal('0.00')
        elif answer_length < 50:
            score = Decimal('40.00')
        elif answer_length < 100:
            score = Decimal('60.00')
        elif answer_length < 200:
            score = Decimal('75.00')
        elif answer_length < 300:
            score = Decimal('85.00')
        else:
            score = Decimal('90.00')
        
        # Add bonus for good keywords (simple check)
        good_keywords = ['experience', 'project', 'team', 'learn', 'achieve', 'solve', 'develop']
        keyword_count = sum(1 for kw in good_keywords if kw in answer_text.lower())
        score += Decimal(keyword_count * 2)
        
        # Cap at 95
        if score > 95:
            score = Decimal('95.00')
        
        answer.score = score
        answer.save()
        total_score += score
    
    # Calculate overall session score
    overall_score = (total_score / answers.count()).quantize(Decimal('0.01'))
    
    # Create or update feedback report
    report, created = FeedbackReport.objects.get_or_create(session=session)
    report.generated_by_model = "AI Evaluation v1.0"
    report.final_score = overall_score
    report.report_summary = f"""
You completed {answers.count()} questions with an overall score of {overall_score}%.

Score Breakdown:
- Average score per question: {overall_score}%
- Total questions answered: {answers.count()}

Your responses show good understanding of the topics. Continue practicing to improve your interview skills.
    """
    
    report.technical_feedback = "Your technical answers demonstrated good knowledge. Consider providing more specific examples from your experience."
    report.communication_feedback = "Your communication was clear and well-structured. Keep practicing to sound more confident."
    report.improvement_plan = """
1. Practice answering questions within time limits
2. Use more specific examples from your experience
3. Research common interview questions for your role
4. Record yourself answering questions to identify areas for improvement
    """
    report.recommended_resources = [
        "https://www.interviewbit.com/",
        "https://leetcode.com/",
        "https://www.pramp.com/",
        "Cracking the Coding Interview book"
    ]
    
    report.save()
    
    # Update session with scores
    session.overall_score = overall_score
    session.technical_score = overall_score
    session.communication_score = overall_score
    session.structure_score = overall_score
    session.confidence_score = overall_score
    session.status = InterviewSession.Status.EVALUATED
    session.evaluated_at = timezone.now()
    session.save()
    
    messages.success(request, f'Feedback report has been generated! Overall score: {overall_score}%')
    log_activity(request.user, 'report_generated', 'FeedbackReport', str(report.id), request)
    
    # Create notification for user
    Notification.objects.create(
        recipient=session.user,
        notification_type=Notification.Type.REPORT_READY,
        title='Your interview report is ready!',
        message=f'Your interview "{session.title}" scored {overall_score}%. Check the detailed feedback!'
    )
    
    return redirect('feedback_report', session_id=session.id)

@login_required
def feedback_report_edit_view(request, session_id):
    """Edit feedback report (admin/staff only)"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit reports.')
        return redirect('session_detail', session_id=session.id)
    
    session = get_object_or_404(InterviewSession, id=session_id)
    report = get_object_or_404(FeedbackReport, session=session)
    
    if request.method == 'POST':
        form = FeedbackReportForm(request.POST, instance=report)
        if form.is_valid():
            report = form.save()
            messages.success(request, 'Feedback report has been updated!')
            log_activity(request.user, 'report_updated', 'FeedbackReport', str(report.id), request)
            return redirect('feedback_report', session_id=session.id)
    else:
        form = FeedbackReportForm(instance=report)
    
    return render(request, 'feedback/edit.html', {
        'session': session,
        'form': form
    })

# ===================== Saved Questions Views =====================

@login_required
def saved_questions_list_view(request):
    """List saved questions for the user"""
    saved_questions = SavedQuestion.objects.filter(user=request.user).select_related('question__session')
    
    paginator = Paginator(saved_questions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'saved_questions/list.html', {'page_obj': page_obj})

@login_required
def saved_question_create_view(request, question_id):
    """Save a question"""
    question = get_object_or_404(InterviewQuestion, id=question_id)
    
    if SavedQuestion.objects.filter(user=request.user, question=question).exists():
        messages.warning(request, 'This question is already in your saved list.')
        return redirect(request.META.get('HTTP_REFERER', 'saved_questions_list'))
    
    if request.method == 'POST':
        form = SavedQuestionForm(request.POST)
        if form.is_valid():
            saved = form.save(commit=False)
            saved.user = request.user
            saved.question = question
            saved.save()
            
            messages.success(request, 'Question saved successfully!')
            log_activity(request.user, 'question_saved', 'SavedQuestion', str(saved.id), request)
            return redirect('saved_questions_list')
    else:
        form = SavedQuestionForm()
    
    return render(request, 'saved_questions/save.html', {
        'form': form,
        'question': question
    })

@login_required
def saved_question_delete_view(request, pk):
    """Remove a saved question"""
    saved_question = get_object_or_404(SavedQuestion, id=pk, user=request.user)
    
    if request.method == 'POST':
        saved_question.delete()
        messages.success(request, 'Question removed from saved list.')
        log_activity(request.user, 'question_unsaved', 'SavedQuestion', str(pk), request)
        return redirect('saved_questions_list')
    
    return render(request, 'saved_questions/delete.html', {'saved_question': saved_question})

# ===================== Session Notes Views =====================

@login_required
def session_notes_list_view(request, session_id):
    """List notes for a session"""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    notes = session.notes.all()
    
    return render(request, 'notes/list.html', {
        'session': session,
        'notes': notes
    })

@login_required
def session_note_create_view(request, session_id):
    """Create a note for a session"""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    
    if request.method == 'POST':
        form = SessionNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.session = session
            note.save()
            
            messages.success(request, 'Note added successfully!')
            log_activity(request.user, 'note_created', 'SessionNote', str(note.id), request)
            return redirect('session_detail', session_id=session.id)
    else:
        form = SessionNoteForm()
    
    return render(request, 'notes/create.html', {
        'form': form,
        'session': session
    })

@login_required
def session_note_edit_view(request, pk):
    """Edit a session note"""
    note = get_object_or_404(SessionNote, id=pk, user=request.user)
    
    if request.method == 'POST':
        form = SessionNoteForm(request.POST, instance=note)
        if form.is_valid():
            note = form.save()
            messages.success(request, 'Note updated successfully!')
            log_activity(request.user, 'note_updated', 'SessionNote', str(note.id), request)
            return redirect('session_detail', session_id=note.session.id)
    else:
        form = SessionNoteForm(instance=note)
    
    return render(request, 'notes/edit.html', {
        'form': form,
        'note': note
    })

@login_required
def session_note_delete_view(request, pk):
    """Delete a session note"""
    note = get_object_or_404(SessionNote, id=pk, user=request.user)
    
    if request.method == 'POST':
        session_id = note.session.id
        note.delete()
        messages.success(request, 'Note deleted successfully!')
        log_activity(request.user, 'note_deleted', 'SessionNote', str(pk), request)
        return redirect('session_detail', session_id=session_id)
    
    return render(request, 'notes/delete.html', {'note': note})

# ===================== Notification Views =====================

@login_required
def notification_list_view(request):
    """List notifications for the user"""
    notifications = Notification.objects.filter(recipient=request.user)
    
    unread_only = request.GET.get('unread', False)
    if unread_only:
        notifications = notifications.filter(is_read=False)
    
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'notifications/list.html', {
        'page_obj': page_obj,
        'unread_only': unread_only
    })

@login_required
def notification_mark_read_view(request, pk):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=pk, recipient=request.user)
    notification.mark_as_read()
    
    messages.success(request, 'Notification marked as read.')
    return redirect('notification_list')

@login_required
def notification_mark_all_read_view(request):
    """Mark all notifications as read"""
    count = Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True, read_at=timezone.now())
    
    messages.success(request, f'{count} notification(s) marked as read.')
    return redirect('notification_list')

@login_required
def notification_delete_view(request, pk):
    """Delete a notification"""
    notification = get_object_or_404(Notification, id=pk, recipient=request.user)
    
    if request.method == 'POST':
        notification.delete()
        messages.success(request, 'Notification deleted.')
        return redirect('notification_list')
    
    return render(request, 'notifications/delete.html', {'notification': notification})

# ===================== Performance Analytics Views =====================

@login_required
def performance_dashboard_view(request):
    """Performance analytics dashboard"""
    user = request.user
    
    # Get performance statistics
    total_sessions = InterviewSession.objects.filter(user=user, status=InterviewSession.Status.COMPLETED)
    
    if not total_sessions.exists():
        messages.info(request, 'Complete some interviews to see your performance analytics.')
        return render(request, 'performance/dashboard.html', {'has_data': False})
    
    # Overall statistics
    avg_score = total_sessions.aggregate(Avg('overall_score'))['overall_score__avg']
    best_score = total_sessions.aggregate(Max('overall_score'))['overall_score__max']
    
    # Score distribution over time
    sessions_over_time = total_sessions.annotate(
        date=TruncDate('completed_at')
    ).values('date').annotate(
        avg_score=Avg('overall_score'),
        count=Count('id')
    ).order_by('date')
    
    # Convert to lists for JavaScript
    dates = []
    scores = []
    counts = []
    
    for item in sessions_over_time:
        if item['date']:
            dates.append(item['date'].strftime('%Y-%m-%d'))
            scores.append(float(item['avg_score']) if item['avg_score'] else 0)
            counts.append(item['count'])
    
    # Performance by domain
    domain_performance = {}
    for session in total_sessions:
        if session.job_role and session.job_role.domain:
            domain_name = session.job_role.domain.title
            if domain_name not in domain_performance:
                domain_performance[domain_name] = {'total_score': 0, 'count': 0}
            domain_performance[domain_name]['total_score'] += float(session.overall_score) if session.overall_score else 0
            domain_performance[domain_name]['count'] += 1
    
    domain_names = list(domain_performance.keys())
    domain_scores = [
        domain_performance[name]['total_score'] / domain_performance[name]['count'] 
        if domain_performance[name]['count'] > 0 else 0 
        for name in domain_names
    ]
    
    # Recent performance snapshot
    latest_snapshot = PerformanceSnapshot.objects.filter(user=user).order_by('-snapshot_date').first()
    
    context = {
        'has_data': True,
        'avg_score': round(avg_score, 2) if avg_score else 0,
        'best_score': round(best_score, 2) if best_score else 0,
        'total_sessions': total_sessions.count(),
        'dates': dates,  # Pass as list instead of using map filter
        'scores': scores,  # Pass as list instead of using map filter
        'domain_names': domain_names,  # Pass as list instead of using map filter
        'domain_scores': domain_scores,  # Pass as list instead of using map filter
        'latest_snapshot': latest_snapshot,
    }
    
    log_activity(user, 'performance_viewed', 'Performance', None, request)
    return render(request, 'performance/dashboard.html', context)

# ===================== Activity Log Views (Admin Only) =====================

@login_required
@staff_required
def activity_log_list_view(request):
    """List activity logs (admin only)"""
    logs = ActivityLog.objects.all().select_related('actor')
    
    user_id = request.GET.get('user')
    if user_id:
        logs = logs.filter(actor_id=user_id)
    
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action__icontains=action)
    
    object_type = request.GET.get('object_type')
    if object_type:
        logs = logs.filter(object_type__icontains=object_type)
    
    date_from = request.GET.get('date_from')
    if date_from:
        logs = logs.filter(created_at__date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        logs = logs.filter(created_at__date__lte=date_to)
    
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    users = User.objects.all()
    
    return render(request, 'admin/activity_logs.html', {
        'page_obj': page_obj,
        'users': users,
        'filters': {
            'user_id': user_id,
            'action': action,
            'object_type': object_type,
            'date_from': date_from,
            'date_to': date_to,
        }
    })

# ===================== Search Views =====================

@login_required
def global_search_view(request):
    """Global search across multiple models"""
    query = request.GET.get('q', '')
    
    if not query:
        return render(request, 'search/results.html', {'query': query})
    
    results = {
        'job_roles': JobRole.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            is_active=True
        )[:5],
        'domains': InterviewDomain.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            is_active=True
        )[:5],
        'sessions': InterviewSession.objects.filter(
            Q(title__icontains=query),
            user=request.user
        )[:5],
        'skills': Skill.objects.filter(name__icontains=query)[:5],
    }
    
    log_activity(request.user, 'global_search', 'Search', None, request, {'query': query})
    
    return render(request, 'search/results.html', {
        'query': query,
        'results': results
    })

# ===================== API-style AJAX Views =====================

@login_required
def ajax_user_stats_view(request):
    """Return user statistics as JSON"""
    user = request.user
    
    stats = {
        'total_sessions': InterviewSession.objects.filter(user=user).count(),
        'completed_sessions': InterviewSession.objects.filter(user=user, status=InterviewSession.Status.COMPLETED).count(),
        'average_score': InterviewSession.objects.filter(
            user=user, status=InterviewSession.Status.COMPLETED
        ).aggregate(Avg('overall_score'))['overall_score__avg'],
        'unread_notifications': Notification.objects.filter(recipient=user, is_read=False).count(),
    }
    
    return JsonResponse(stats)

@login_required
def ajax_skill_autocomplete_view(request):
    """Autocomplete skills for form inputs"""
    term = request.GET.get('term', '')
    skills = Skill.objects.filter(name__icontains=term)[:10]
    
    results = [{'id': skill.id, 'label': skill.name, 'value': skill.name} for skill in skills]
    
    return JsonResponse(results, safe=False)

# ===================== Error Views =====================

def no_permission_view(request):
    """View for permission denied"""
    return render(request, 'errors/no_permission.html', status=403)

def custom_404_view(request, exception):
    """Custom 404 error view"""
    return render(request, 'errors/404.html', status=404)

def custom_500_view(request):
    """Custom 500 error view"""
    return render(request, 'errors/500.html', status=500)

# ===================== Home View =====================

def home_view(request):
    """Landing page view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    featured_domains = InterviewDomain.objects.filter(is_active=True)[:6]
    
    # Use annotate with Count for ordering
    popular_roles = JobRole.objects.filter(
        is_active=True
    ).annotate(
        session_count=Count('interview_sessions')
    ).order_by('-session_count')[:6]
    
    return render(request, 'home.html', {
        'featured_domains': featured_domains,
        'popular_roles': popular_roles,
    })