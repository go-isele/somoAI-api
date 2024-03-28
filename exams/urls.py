from django.urls import path

from exams.views import ExamView, TakeStudentExamAPIView, AnswerFileAPIView, MarkingAPIView, ManagementExamInfoView, \
    StudentExamInfoView, ExamDocumentUploadView

urlpatterns = [
    path('upload-exam-document/', ExamDocumentUploadView.as_view(), name='upload_exam_document'),
    path('exam/take/<int:exam_id>/', TakeStudentExamAPIView.as_view(), name='take-exam'),
    path('student/exam-info/', StudentExamInfoView.as_view(), name='student-exam-info'),

    path('exam/', ExamView.as_view(), name='exam'),
    path('answer/file/', AnswerFileAPIView.as_view(), name='answer-file-api'),
    path('exam/mark/', MarkingAPIView.as_view(), name='marking_api'),

    path('management/exam-info/', ManagementExamInfoView.as_view(), name='management-exam-info'),
]