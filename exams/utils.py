import json
import re

import cloudinary.uploader
from django.conf import settings
import requests

from openai import OpenAI
import google.generativeai as genai

from exams.models import Exam, StudentExam

genai.configure(api_key=settings.GOOGLE_API_KEY)

ai_client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


def parse_marks_and_feedback(text):
    marks = None
    feedback = ""

    # Extract marks
    match_marks = re.search(r'Score:\D*(\d+)', text)
    if match_marks:
        marks = int(match_marks.group(1))

    # Extract feedback
    match_feedback = re.search(r'Feedback:\s*(.*)', text)
    if match_feedback:
        feedback = match_feedback.group(1).strip()

    return marks, feedback


def gemini_completion(teacher_answer, student_answer):
    prompt = f"Can you evaluate the following student answer based on the teacher's provided answer? \n Teacher Answer: {teacher_answer} \n Student Answer: {student_answer} \n What score would you give the student's answer (out of 100)?\n What specific feedback can you provide on the student's answer?"

    # Initialize generative model
    model = genai.GenerativeModel("gemini-pro")

    # Generate response
    response = model.generate_content(
        prompt,
        stream=True,
        generation_config=genai.types.GenerationConfig(
            candidate_count=1,
            stop_sequences=['x'],
            temperature=1.0)
    )

    # Concatenate chunks of response into a single string
    response_text = "".join(chunk.text for chunk in response)

    print("Generated response text:", response_text)

    # Parse marks and feedback
    marks, feedback = parse_marks_and_feedback(response_text)

    print("Parsed marks:", marks)
    print("Parsed feedback:", feedback)

    return marks, feedback




def generate_completion(teacher_answer, student_answer):
    # Define the context and marking criteria
    prompts = [
        {"role": "system", "content": "You are a High School Teacher assistant, skilled in administering and "
                                      "marking of student answers. Given the following marking scheme:"},
        {"role": "user", "content": f"Teacher's Answer: {teacher_answer}\nStudent's Answer: {student_answer}\n"
                                    "Please provide marks or feedback based on the comparison of ideas."}
    ]

    # Call OpenAI API to generate completion
    completion = ai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=prompts
    )

    # Extract marks or feedback from the completion
    if completion.choices:
        return completion.choices[0].message['content']
    else:
        return "Failed to generate marks or feedback."


def upload_file(file):
    """
  Uploads a file to Cloudinary and returns the public URL.

  Args:
      file: The uploaded file object from the serializer's validated data.

  Returns:
      The public URL of the uploaded file on Cloudinary.

  Raises:
      Exception: If there's an error uploading the file.
  """

    # Configure Cloudinary using your Cloudinary account details
    cloudinary.config(
        cloud_name="dov23ufag",
        api_key="158384229493682",
        api_secret="wK1MEGj5nI5z9dh3qENPJTmyR90"
    )

    # Upload the file to Cloudinary
    try:
        result = cloudinary.uploader.upload(file)
        return result
    except Exception as e:
        raise Exception(f"Error uploading file to Cloudinary: {e}")


def process_answer(url, overlay=False, api_key='helloworld', language='eng'):
    """ OCR.space API request with remote file.
        Python3.5 - not tested on 2.7
    :param url: Image url.
    :param overlay: Is OCR.space overlay required in your response.
                    Defaults to False.
    :param api_key: OCR.space API key.
                    Defaults to 'helloworld'.
    :param language: Language code to be used in OCR.
                    List of available language codes can be found on https://ocr.space/OCRAPI
                    Defaults to 'en'.
    :return: Result in JSON format.
    """

    payload = {'url': url,
               'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language,
               }
    r = requests.post('https://api.ocr.space/parse/image', data=payload)
    return r.content.decode()


def get_students_in_exam(exam_id):
    try:
        students = StudentExam.objects.filter(exam_id=exam_id).select_related('student')
        return students
    except StudentExam.DoesNotExist:
        return None


def get_student_attempts(student_id):
    try:
        attempts = StudentExam.objects.filter(student_id=student_id).select_related('exam')
        return attempts
    except StudentExam.DoesNotExist:
        return None


def get_exam_attempts_with_scores(exam_id):
    try:
        attempts = StudentExam.objects.filter(exam_id=exam_id, score__isnull=False).select_related('student')
        return attempts
    except StudentExam.DoesNotExist:
        return None
