from rest_framework import serializers

from .models import Exam, AnswerFile, Question, StudentExam


class ExamSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'created_by', 'subject', 'date', 'score']


class AnswerFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerFile
        fields = ['id', 'file_url', 'uploaded_by', 'uploaded_at']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class StudentExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentExam
        fields = '__all__'
