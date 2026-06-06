import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class UUIDTimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=140, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to="users/profile_images/", blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name or self.username


class UserProfile(UUIDTimeStampedModel):
    class ExperienceLevel(models.TextChoices):
        FRESHER = "FRESHER", "Fresher"
        JUNIOR = "JUNIOR", "Junior"
        MID_LEVEL = "MID_LEVEL", "Mid Level"
        SENIOR = "SENIOR", "Senior"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    headline = models.CharField(max_length=180, blank=True, default='')
    bio = models.TextField(blank=True, default='')
    experience_level = models.CharField(
        max_length=30,
        choices=ExperienceLevel.choices,
        default=ExperienceLevel.FRESHER,
    )
    target_role = models.CharField(max_length=140, blank=True, default='')
    skills = models.JSONField(default=list, blank=True)  # Make sure default is list, not None
    resume = models.FileField(upload_to="users/resumes/", blank=True, null=True)
    linkedin_url = models.URLField(blank=True, default='')
    github_url = models.URLField(blank=True, default='')

    def __str__(self):
        return f"Profile of {self.user}"

class Skill(UUIDTimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class InterviewDomain(UUIDTimeStampedModel):
    class DomainType(models.TextChoices):
        TECHNICAL = "TECHNICAL", "Technical"
        BEHAVIORAL = "BEHAVIORAL", "Behavioral"
        HR = "HR", "HR"
        SYSTEM_DESIGN = "SYSTEM_DESIGN", "System Design"
        MIXED = "MIXED", "Mixed"

    title = models.CharField(max_length=160, unique=True)
    slug = models.SlugField(max_length=180, unique=True)
    domain_type = models.CharField(max_length=30, choices=DomainType.choices, default=DomainType.TECHNICAL)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class JobRole(UUIDTimeStampedModel):
    class Difficulty(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"

    domain = models.ForeignKey(InterviewDomain, on_delete=models.CASCADE, related_name="job_roles")
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    description = models.TextField(blank=True)
    difficulty = models.CharField(max_length=30, choices=Difficulty.choices, default=Difficulty.BEGINNER)
    skills = models.ManyToManyField(Skill, blank=True, related_name="job_roles")
    default_question_count = models.PositiveSmallIntegerField(default=5)
    time_limit_minutes = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["domain", "title"]

    def __str__(self):
        return self.title


class InterviewSession(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        CREATED = "CREATED", "Created"
        QUESTIONS_GENERATED = "QUESTIONS_GENERATED", "Questions Generated"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        SUBMITTED = "SUBMITTED", "Submitted"
        EVALUATED = "EVALUATED", "Evaluated"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="interview_sessions")
    job_role = models.ForeignKey(JobRole, on_delete=models.PROTECT, related_name="interview_sessions")
    title = models.CharField(max_length=180)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.CREATED)

    question_count = models.PositiveSmallIntegerField(default=5)
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    evaluated_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    overall_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    technical_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    communication_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    structure_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))

    ai_summary = models.TextField(blank=True)
    strengths = models.JSONField(default=list, blank=True)
    improvement_areas = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    failure_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["job_role", "created_at"]),
            models.Index(fields=["overall_score"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.title}"


class InterviewQuestion(UUIDTimeStampedModel):
    class QuestionType(models.TextChoices):
        TECHNICAL = "TECHNICAL", "Technical"
        BEHAVIORAL = "BEHAVIORAL", "Behavioral"
        HR = "HR", "HR"
        CODING = "CODING", "Coding"
        SCENARIO = "SCENARIO", "Scenario"

    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    question_type = models.CharField(max_length=30, choices=QuestionType.choices)
    skill = models.ForeignKey(Skill, on_delete=models.SET_NULL, null=True, blank=True, related_name="questions")
    order = models.PositiveSmallIntegerField(default=1)
    difficulty = models.CharField(max_length=30, choices=JobRole.Difficulty.choices, default=JobRole.Difficulty.BEGINNER)
    expected_keywords = models.JSONField(default=list, blank=True)
    ai_generation_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["session", "order"]
        constraints = [
            models.UniqueConstraint(fields=["session", "order"], name="unique_question_order_per_session")
        ]

    def __str__(self):
        return f"Question {self.order} - {self.session}"


class InterviewAnswer(UUIDTimeStampedModel):
    question = models.OneToOneField(InterviewQuestion, on_delete=models.CASCADE, related_name="answer")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="interview_answers")
    answer_text = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_spent_seconds = models.PositiveIntegerField(default=0)

    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    critique = models.TextField(blank=True)
    ideal_answer = models.TextField(blank=True)
    missing_points = models.JSONField(default=list, blank=True)
    matched_keywords = models.JSONField(default=list, blank=True)
    ai_evaluation_payload = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Answer for {self.question}"


class FeedbackReport(UUIDTimeStampedModel):
    session = models.OneToOneField(InterviewSession, on_delete=models.CASCADE, related_name="feedback_report")
    generated_by_model = models.CharField(max_length=120, blank=True, default='')
    final_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,  # Allow null temporarily
        blank=True,  # Allow blank
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    report_summary = models.TextField(blank=True, default='')  # Allow blank
    technical_feedback = models.TextField(blank=True, default='')
    communication_feedback = models.TextField(blank=True, default='')
    improvement_plan = models.TextField(blank=True, default='')
    recommended_resources = models.JSONField(default=list, blank=True)
    report_json = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Report for {self.session}"


class AIProviderLog(UUIDTimeStampedModel):
    class Provider(models.TextChoices):
        OPENAI = "OPENAI", "OpenAI"
        GEMINI = "GEMINI", "Gemini"
        OLLAMA = "OLLAMA", "Ollama"
        CUSTOM = "CUSTOM", "Custom"

    class Purpose(models.TextChoices):
        QUESTION_GENERATION = "QUESTION_GENERATION", "Question Generation"
        ANSWER_EVALUATION = "ANSWER_EVALUATION", "Answer Evaluation"
        REPORT_GENERATION = "REPORT_GENERATION", "Report Generation"

    class Status(models.TextChoices):
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    session = models.ForeignKey(InterviewSession, on_delete=models.SET_NULL, null=True, blank=True, related_name="ai_logs")
    provider = models.CharField(max_length=30, choices=Provider.choices)
    purpose = models.CharField(max_length=40, choices=Purpose.choices)
    model_name = models.CharField(max_length=120, blank=True)
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
    latency_ms = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices)
    request_payload = models.JSONField(default=dict, blank=True)
    response_payload = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.total_tokens = self.prompt_tokens + self.completion_tokens
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.provider} - {self.purpose} - {self.status}"


class SavedQuestion(UUIDTimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_questions")
    question = models.ForeignKey(InterviewQuestion, on_delete=models.CASCADE, related_name="saved_by")
    note = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "question"], name="unique_saved_question_per_user")
        ]

    def __str__(self):
        return f"{self.user} saved question"


class SessionNote(UUIDTimeStampedModel):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name="notes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="interview_notes")
    note = models.TextField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note for {self.session}"


class PerformanceSnapshot(UUIDTimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="performance_snapshots")
    snapshot_date = models.DateField(default=timezone.localdate)
    total_sessions = models.PositiveIntegerField(default=0)
    completed_sessions = models.PositiveIntegerField(default=0)
    average_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    best_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    weakest_skills = models.JSONField(default=list, blank=True)
    strongest_skills = models.JSONField(default=list, blank=True)
    analytics_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-snapshot_date"]
        constraints = [
            models.UniqueConstraint(fields=["user", "snapshot_date"], name="unique_user_performance_snapshot_per_day")
        ]

    def __str__(self):
        return f"{self.user} performance - {self.snapshot_date}"


class Notification(UUIDTimeStampedModel):
    class Type(models.TextChoices):
        SESSION_STARTED = "SESSION_STARTED", "Session Started"
        QUESTIONS_READY = "QUESTIONS_READY", "Questions Ready"
        REPORT_READY = "REPORT_READY", "Report Ready"
        PRACTICE_REMINDER = "PRACTICE_REMINDER", "Practice Reminder"
        SYSTEM = "SYSTEM", "System"

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=40, choices=Type.choices)
    title = models.CharField(max_length=180)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["recipient", "is_read"])]

    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=["is_read", "read_at", "updated_at"])

    def __str__(self):
        return self.title


# In your models.py, update the ActivityLog model:

class ActivityLog(models.Model):
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=100, blank=True, null=True)  # Allow null/blank
    object_id = models.CharField(max_length=100, blank=True, null=True)   # Allow null/blank
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.action 