# Generated by Django 5.0.3 on 2024-03-26 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='answerfile',
            name='answer_text',
            field=models.TextField(blank=True, null=True, verbose_name='answer'),
        ),
        migrations.AlterField(
            model_name='question',
            name='answers',
            field=models.ManyToManyField(blank=True, to='exams.answerfile', verbose_name='answers'),
        ),
        migrations.DeleteModel(
            name='Answer',
        ),
    ]