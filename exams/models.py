from django.db import models
from django.utils import timezone

from users.models import CustomUser
from django.utils.translation import gettext_lazy as _


class Document(models.Model):
    file = models.FileField(upload_to='exam_documents/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


class Exam(models.Model):
    title = models.CharField(max_length=200, verbose_name='title')
    description = models.TextField(verbose_name='description', blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='created_by')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created_at')
    subject = models.CharField(_("subject"), max_length=100)
    date = models.DateField(_("exam date"), default=timezone.now())
    total_marks = models.IntegerField(default=0, blank=True, null=True)
    marking_scheme = models.TextField(_("marking scheme"), blank=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, blank=True, null=True)  # ForeignKey relationship

    def __str__(self):
        return self.title


class StudentExam(models.Model):
    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('completed', 'Completed'),
        ('incomplete', 'Incomplete'),
        ('withdrawn', 'Withdrawn'),
        # Add more status choices as needed
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name='exam')

    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='student')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled', verbose_name='status')

    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='score')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='start time')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='end time')
    attempts = models.PositiveIntegerField(default=0, verbose_name='attempts')
    feedback = models.TextField(blank=True, verbose_name='feedback')
    proctor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='proctoring_exams', null=True,
                                blank=True, verbose_name='proctor')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP address')
    duration = models.DurationField(null=True, blank=True, verbose_name='duration')
    submission_status = models.BooleanField(default=False, verbose_name='submission status', null=True)
    flagged_for_review = models.BooleanField(default=False, verbose_name='flagged for review')
    access_code = models.CharField(max_length=20, null=True, blank=True, verbose_name='access code')

    def __str__(self):
        return f"{self.student.username}'s attempt on {self.exam.title}"

    @classmethod
    def create_student_exam(cls, exam_id, student_id):
        exam = Exam.objects.get(id=exam_id)
        student = CustomUser.objects.get(id=student_id)
        return cls.objects.create(exam=exam, student=student)


class AnswerFile(models.Model):
    file_url = models.CharField(verbose_name='file url', blank=True, max_length=300)
    answer_text = models.TextField(verbose_name='answer', null=True, blank=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='uploaded by')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='uploaded by')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name='exam', null=True, blank=True)


class Question(models.Model):
    question_text = models.TextField(verbose_name='question', blank=False)
    question_number = models.IntegerField(verbose_name='question number', blank=True)
    description = models.TextField(verbose_name='description', blank=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name='exam')

