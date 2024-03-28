# Generated by Django 5.0.3 on 2024-03-26 09:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0002_answerfile_answer_text_alter_question_answers_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='answers',
        ),
        migrations.AddField(
            model_name='answerfile',
            name='exam',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='exams.exam', verbose_name='exam'),
        ),
        migrations.AddField(
            model_name='exam',
            name='marking_scheme',
            field=models.TextField(blank=True, verbose_name='marking scheme'),
        ),
    ]