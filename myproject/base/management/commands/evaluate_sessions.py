from django.core.management.base import BaseCommand
from django.utils import timezone
from base.models import InterviewSession, InterviewAnswer, FeedbackReport
from decimal import Decimal

class Command(BaseCommand):
    help = 'Evaluate all submitted sessions and generate scores'

    def handle(self, *args, **options):
        # Get sessions that are SUBMITTED or IN_PROGRESS with all questions answered
        sessions = InterviewSession.objects.filter(status__in=['SUBMITTED', 'IN_PROGRESS'])
        
        if not sessions.exists():
            self.stdout.write(self.style.WARNING('No submitted or in-progress sessions found'))
            return
        
        evaluated_count = 0
        for session in sessions:
            self.stdout.write(f'Processing: {session.title}')
            
            answers = InterviewAnswer.objects.filter(question__session=session, user=session.user)
            
            if not answers.exists():
                self.stdout.write(self.style.WARNING(f'  No answers found for {session.title}'))
                continue
            
            total_score = Decimal('0.00')
            answer_count = answers.count()
            
            for answer in answers:
                # Simple scoring logic based on answer length
                answer_text = answer.answer_text or ""
                answer_length = len(answer_text)
                
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
                self.stdout.write(f'  Question {answer.question.order}: {score}%')
            
            overall_score = (total_score / answer_count).quantize(Decimal('0.01'))
            
            # Update session
            session.overall_score = overall_score
            session.technical_score = overall_score
            session.communication_score = overall_score
            session.structure_score = overall_score
            session.confidence_score = overall_score
            session.status = 'EVALUATED'
            session.evaluated_at = timezone.now()
            session.save()
            
            # Create or update feedback report - FIX: Set final_score before saving
            try:
                report = FeedbackReport.objects.get(session=session)
                # Update existing report
                report.generated_by_model = "Batch Evaluation"
                report.final_score = overall_score
                report.report_summary = f"Overall score: {overall_score}% based on {answer_count} questions."
                report.save()
                self.stdout.write(self.style.SUCCESS(f'  Updated existing report! Score: {overall_score}%'))
            except FeedbackReport.DoesNotExist:
                # Create new report with all required fields
                report = FeedbackReport.objects.create(
                    session=session,
                    generated_by_model="Batch Evaluation",
                    final_score=overall_score,
                    report_summary=f"Overall score: {overall_score}% based on {answer_count} questions.",
                    technical_feedback="Your technical answers demonstrated good knowledge.",
                    communication_feedback="Your communication was clear and well-structured.",
                    improvement_plan="Practice more to improve your scores.",
                    recommended_resources=[]  # Empty list as default
                )
                self.stdout.write(self.style.SUCCESS(f'  Created new report! Score: {overall_score}%'))
            
            evaluated_count += 1
            self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS(f'\nTotal sessions evaluated: {evaluated_count}'))