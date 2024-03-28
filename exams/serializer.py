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


class ExamDocumentSerializer(serializers.Serializer):
    document = serializers.FileField()

    def create(self, validated_data):
        # This method is optional, but you can implement it if you need to perform additional actions
        # when creating an instance of the serializer.
        # For example, you can save the document to the database.
        # exam = Exam.objects.create(document=validated_data['document'])
        # return exam
        pass

    def update(self, instance, validated_data):
        # This method is optional and typically not needed for file uploads.
        pass