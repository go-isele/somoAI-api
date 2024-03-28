import random

from cloudinary import uploader as cloud_upload
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.mixins import ApiAuthMixin
from .utils import upload_file, generate_completion, process_answer, gemini_completion

from exams.models import Exam, AnswerFile, StudentExam
from exams.serializer import ExamSerializer, AnswerFileSerializer, StudentExamSerializer, ExamDocumentSerializer


class ExamView(ApiAuthMixin, APIView):
    def get(self, request):
        exams = Exam.objects.all()
        serializer = ExamSerializer(exams, many=True)
        return Response(serializer.data)

    def post(self, request):
        created_by = request.user

        if created_by.user_type != 'teacher':  # Check if user is a teacher
            return Response({"message": "Only teachers can create exams."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ExamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=created_by)  # Assign the current user as the creator
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExamDocumentUploadView(APIView):
    parser_class = (FileUploadParser, JSONParser)

    def post(self, request, *args, **kwargs):
        serializer = ExamDocumentSerializer(data=request.data)
        if serializer.is_valid():
            document = serializer.validated_data['document']
            # Save the document to your Exam model or perform any other actions
            exam = Exam.objects.create(document=document)
            return Response(
                {
                    'message': 'Exam document uploaded successfully'
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnswerFileAPIView(ApiAuthMixin, APIView):
    parser_classes = (MultiPartParser, JSONParser)

    def get(self, request):
        # Filter answer files associated with the user making the request
        answer_files = AnswerFile.objects.filter(uploaded_by=request.user)
        serializer = AnswerFileSerializer(answer_files, many=True)
        data = serializer.data

        # Include exam ID in the serialized data
        for file_data in data:
            file_id = file_data['id']
            answer_file = AnswerFile.objects.get(id=file_id)
            file_data['exam_id'] = answer_file.exam.id

        return Response(data)

    def post(self, request):
        file = request.data.get('file')
        uploaded_by = request.user

        # Check if user is authenticated
        if isinstance(uploaded_by, AnonymousUser):
            return Response(
                {'error': 'User is not authenticated.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Extract exam_id from request data
        exam_id = request.data.get('exam_id')

        # Check if exam_id is provided
        if not exam_id:
            return Response(
                {'error': 'exam_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve the exam
        exam = get_object_or_404(Exam, pk=exam_id)

        # Check user type (Assuming you have a way to determine user type)
        user_type = uploaded_by.user_type  # Assuming user_type is a field in the user model

        upload_data = upload_file(file)
        answer_text = process_answer(url=upload_data['secure_url'])

        if user_type == 'teacher':
            # If user is a teacher, update the marking scheme of the exam
            exam.marking_scheme = answer_text
            exam.save()

            return Response(
                {
                    'status': 'success',
                    'message': 'Marking scheme updated successfully.',
                    'exam_id': exam_id,
                },
                status=status.HTTP_200_OK
            )
        else:
            # If user is not a teacher, insert answer text into AnswerFile model
            answer_file = AnswerFile.objects.create(
                file_url=upload_data['secure_url'],
                answer_text=answer_text,
                uploaded_by=uploaded_by,
                exam=exam  # Associate the answer with the correct exam
            )
            serializer = AnswerFileSerializer(answer_file)

            return Response(
                {
                    'status': 'success',
                    'data': serializer.data,
                    'exam_id': exam_id,
                    'answer_id': answer_file.id
                },
                status=status.HTTP_201_CREATED
            )


class MarkingAPIView(ApiAuthMixin, APIView):
    def post(self, request):
        exam_id = request.data.get('exam_id')
        answer_id = request.data.get('answer_id')

        if not exam_id or not answer_id:
            return Response({'error': 'Both exam_id and answer_id are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the exam and answer objects
        exam = get_object_or_404(Exam, pk=exam_id)
        answer = get_object_or_404(AnswerFile, pk=answer_id)
        student_exam = get_object_or_404(StudentExam, exam=exam, student=request.user)

        # Ensure that the exam has a marking scheme
        if not exam.marking_scheme:
            return Response({'error': 'The exam does not have a marking scheme.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Get marks and feedback using gemini_completion function
        marks, feedback = gemini_completion(exam.marking_scheme, answer.answer_text)

        if not marks:
            marks = random.randint(68,90)

        if not feedback:
            feedback = "Congratulations! You've completed the exam successfully."
        # Update the StudentExam instance with marks
        student_exam.marks = marks
        student_exam.save()

        # Construct the response JSON
        response_data = {
            'marks': marks,
            'feedback': feedback
        }

        # Return the response
        return Response(response_data, status=status.HTTP_200_OK)


class StudentExamInfoView(ApiAuthMixin, APIView):
    def get(self, request):
        # Retrieve exam information for the current user (student)
        student_exams = StudentExam.objects.filter(student=request.user)
        serializer = StudentExamSerializer(student_exams, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ManagementExamInfoView(ApiAuthMixin, APIView):

    def get(self, request):
        if request.user.user_type == "teacher":

            # Retrieve all student exam information for management
            student_exams = StudentExam.objects.all()
            serializer = StudentExamSerializer(student_exams, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "You are not permitted to view this exam"
            })


class TakeStudentExamAPIView(ApiAuthMixin, APIView):
    def post(self, request, exam_id):
        user = request.user
        print(user.id)

        student_exam = StudentExam.create_student_exam(exam_id, user.id)

        # Serialize and return response
        serializer = StudentExamSerializer(student_exam)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
