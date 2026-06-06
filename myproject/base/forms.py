from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

from .models import (
    UserProfile, Skill, InterviewDomain, JobRole,
    InterviewSession, InterviewQuestion, InterviewAnswer,
    FeedbackReport, SavedQuestion, SessionNote, Notification
)

User = get_user_model()


# ===================== Session Status Form =====================
class InterviewSessionStatusForm(forms.Form):
    """Session status update form"""
    status = forms.ChoiceField(
        choices=InterviewSession.Status.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    failure_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Reason for failure (if applicable)'}),
        help_text='Reason for failure (if status is FAILED)'
    )


# ===================== Authentication Forms =====================
class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form with improved UX"""
    
    full_name = forms.CharField(
        max_length=140,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'autocomplete': 'name'
        }),
        label='Full Name'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com',
            'autocomplete': 'email'
        }),
        label='Email Address'
    )
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username',
            'autocomplete': 'username'
        }),
        label='Username'
    )
    
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1 234 567 8900',
            'autocomplete': 'tel'
        }),
        label='Phone Number (Optional)'
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a password',
            'autocomplete': 'new-password'
        }),
        label='Password',
        help_text='At least 8 characters'
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        }),
        label='Confirm Password'
    )
    
    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'phone_number', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.full_name = self.cleaned_data['full_name']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """Custom user edit form"""
    
    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'phone_number', 'profile_image')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if hasattr(field, 'widget') and hasattr(field.widget, 'attrs'):
                field.widget.attrs['class'] = 'form-control'
        
        # Make password field not required in edit form
        self.fields['password'].required = False
        self.fields['password'].help_text = 'Leave blank to keep current password'


# ===================== User Profile Form =====================
class UserProfileForm(forms.ModelForm):
    """User profile form with improved skill selection"""
    
    class Meta:
        model = UserProfile
        fields = ('headline', 'bio', 'experience_level', 'target_role', 'skills', 'resume', 'linkedin_url', 'github_url')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Style text fields
        text_fields = ['headline', 'target_role', 'linkedin_url', 'github_url']
        for field in text_fields:
            if field in self.fields:
                self.fields[field].widget.attrs['class'] = 'form-control'
        
        # Bio textarea
        if 'bio' in self.fields:
            self.fields['bio'].widget = forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself, your experience, and career goals...'
            })
        
        # Experience level select
        if 'experience_level' in self.fields:
            self.fields['experience_level'].widget.attrs['class'] = 'form-select'
        
        # Skills - multiple select with search
        if 'skills' in self.fields:
            self.fields['skills'].widget = forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '8',
                'data-placeholder': 'Select your skills...'
            })
            self.fields['skills'].help_text = 'Hold Ctrl/Cmd to select multiple skills'
            self.fields['skills'].required = False  # Make it optional
        
        # Placeholders
        if 'headline' in self.fields:
            self.fields['headline'].widget.attrs['placeholder'] = 'e.g., Passionate Software Developer with 5 years experience'
            self.fields['headline'].required = False
        if 'target_role' in self.fields:
            self.fields['target_role'].widget.attrs['placeholder'] = 'e.g., Senior Python Developer'
            self.fields['target_role'].required = False
        if 'linkedin_url' in self.fields:
            self.fields['linkedin_url'].widget.attrs['placeholder'] = 'https://linkedin.com/in/yourprofile'
            self.fields['linkedin_url'].required = False
        if 'github_url' in self.fields:
            self.fields['github_url'].widget.attrs['placeholder'] = 'https://github.com/yourusername'
            self.fields['github_url'].required = False
        if 'resume' in self.fields:
            self.fields['resume'].widget.attrs['class'] = 'form-control'
            self.fields['resume'].required = False
            self.fields['resume'].help_text = 'Upload your resume (PDF or DOCX format)'
        
        # Help texts
        if 'headline' in self.fields:
            self.fields['headline'].help_text = 'A short professional headline (max 180 characters)'
        if 'bio' in self.fields:
            self.fields['bio'].help_text = 'Share your professional background, key achievements, and career aspirations'
        if 'target_role' in self.fields:
            self.fields['target_role'].help_text = 'What role are you currently preparing for?'
    
    def clean_skills(self):
        """Ensure skills is always a list, never None"""
        skills = self.cleaned_data.get('skills')
        if skills is None:
            return []  # Return empty list instead of None
        if isinstance(skills, str):
            return [s.strip() for s in skills.split(',') if s.strip()]
        return skills
    
    def save(self, commit=True):
        """Override save to ensure skills is never None"""
        instance = super().save(commit=False)
        
        # Ensure skills is a list
        if instance.skills is None:
            instance.skills = []
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance


# ===================== Skill Forms =====================
class SkillForm(forms.ModelForm):
    """Skill form"""
    
    class Meta:
        model = Skill
        fields = ('name', 'slug')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter skill name'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'skill-url-slug'}),
        }
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            slug = slug.lower().replace(' ', '-').replace('_', '-')
        return slug
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Auto-generate slug if not provided
            if not self.cleaned_data.get('slug'):
                self.cleaned_data['slug'] = name.lower().replace(' ', '-')
        return name


class BulkSkillForm(forms.Form):
    """Bulk skill import form"""
    
    skills = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Python\nJavaScript\nReact\nDjango\nPostgreSQL\nCommunication\nLeadership\nProblem Solving'
        }),
        help_text='Enter one skill per line'
    )
    
    def clean_skills(self):
        skills_text = self.cleaned_data.get('skills', '')
        skills_list = [s.strip() for s in skills_text.split('\n') if s.strip()]
        if not skills_list:
            raise forms.ValidationError('Please enter at least one skill.')
        return skills_list


# ===================== Domain and Job Role Forms =====================
class InterviewDomainForm(forms.ModelForm):
    """Interview domain form"""
    
    class Meta:
        model = InterviewDomain
        fields = ('title', 'slug', 'domain_type', 'description', 'icon', 'is_active')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'domain_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fa-code'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class JobRoleForm(forms.ModelForm):
    """Job role form"""
    
    class Meta:
        model = JobRole
        fields = ('domain', 'title', 'slug', 'description', 'difficulty', 'skills', 
                  'default_question_count', 'time_limit_minutes', 'is_active')
        widgets = {
            'domain': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'skills': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 6}),
            'default_question_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
            'time_limit_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 10, 'max': 180}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            slug = slug.lower().replace(' ', '-')
        return slug


# ===================== Interview Session Form =====================
class InterviewSessionForm(forms.ModelForm):
    """Interview session creation form"""
    
    class Meta:
        model = InterviewSession
        fields = ('title', 'job_role', 'question_count')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Python Developer Technical Interview',
                'autocomplete': 'off'
            }),
            'job_role': forms.Select(attrs={'class': 'form-select'}),
            'question_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 3,
                'max': 15,
                'value': 5
            }),
        }
        labels = {
            'title': 'Session Title',
            'job_role': 'Job Role',
            'question_count': 'Number of Questions',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter job roles for active ones only
        if self.user:
            self.fields['job_role'].queryset = JobRole.objects.filter(is_active=True)
            self.fields['job_role'].empty_label = "Select a job role"
        
        # Add help text
        self.fields['title'].help_text = 'Give your interview session a descriptive title'
        self.fields['question_count'].help_text = 'Choose between 3-15 questions for this interview'
        
        # Add styling
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['job_role'].widget.attrs['class'] = 'form-select'
        self.fields['question_count'].widget.attrs['class'] = 'form-control'
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title) < 5:
            raise forms.ValidationError('Title must be at least 5 characters long.')
        return title
    
    def clean_question_count(self):
        question_count = self.cleaned_data.get('question_count')
        if question_count and (question_count < 3 or question_count > 15):
            raise forms.ValidationError('Number of questions must be between 3 and 15.')
        return question_count
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set the user - CRITICAL FIX
        if self.user:
            instance.user = self.user
        
        # Set default title if not provided
        if not instance.title and instance.job_role:
            instance.title = f"{instance.job_role.title} Interview"
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance


# ===================== Question and Answer Forms =====================
class InterviewQuestionForm(forms.ModelForm):
    """Interview question form"""
    
    class Meta:
        model = InterviewQuestion
        fields = ('question_text', 'question_type', 'order', 'difficulty', 'expected_keywords')
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter the question here...'}),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'expected_keywords': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'comma, separated, keywords'}),
        }


class InterviewAnswerForm(forms.ModelForm):
    """Interview answer form"""
    
    class Meta:
        model = InterviewAnswer
        fields = ('answer_text',)
        widgets = {
            'answer_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Type your answer here...\n\nTips:\n• Take your time to think\n• Use the STAR method for behavioral questions\n• Be specific and provide examples\n• Keep your answer clear and concise'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['answer_text'].label = 'Your Answer'
        self.fields['answer_text'].help_text = 'Be thorough and specific in your response'
        self.fields['answer_text'].required = True


# ===================== Feedback Report Form =====================
class FeedbackReportForm(forms.ModelForm):
    """Feedback report form"""
    
    class Meta:
        model = FeedbackReport
        fields = ('final_score', 'report_summary', 'technical_feedback', 
                  'communication_feedback', 'improvement_plan', 'recommended_resources')
        widgets = {
            'final_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0, 'max': 100}),
            'report_summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Executive summary of the interview performance...'}),
            'technical_feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Technical aspects feedback...'}),
            'communication_feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Communication and presentation feedback...'}),
            'improvement_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Specific recommendations for improvement...'}),
            'recommended_resources': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List recommended resources, courses, or articles'}),
        }
    
    def clean_final_score(self):
        score = self.cleaned_data.get('final_score')
        if score and (score < 0 or score > 100):
            raise forms.ValidationError('Score must be between 0 and 100.')
        return score


# ===================== Saved Questions Form =====================
class SavedQuestionForm(forms.ModelForm):
    """Saved question form"""
    
    class Meta:
        model = SavedQuestion
        fields = ('note',)
        widgets = {
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add personal notes about this question (why you saved it, key points to remember, etc.)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['note'].required = False
        self.fields['note'].label = 'Personal Notes'


# ===================== Session Notes Form =====================
class SessionNoteForm(forms.ModelForm):
    """Session note form"""
    
    class Meta:
        model = SessionNote
        fields = ('note',)
        widgets = {
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your notes about this interview session...\n\n• What went well?\n• What could be improved?\n• Key takeaways\n• Questions to research further'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['note'].label = 'Note'
        self.fields['note'].required = True


# ===================== Notification Form =====================
class NotificationForm(forms.ModelForm):
    """Notification form"""
    
    class Meta:
        model = Notification
        fields = ('title', 'message', 'notification_type')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Notification title'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notification message'}),
            'notification_type': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['message'].required = True