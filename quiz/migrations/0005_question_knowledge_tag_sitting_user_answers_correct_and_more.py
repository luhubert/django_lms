# Generated by Django 4.2.3 on 2023-08-05 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0004_alter_mcquestion_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='knowledge_tag',
            field=models.CharField(default='unknown', max_length=100, verbose_name='知識點'),
        ),
        migrations.AddField(
            model_name='sitting',
            name='user_answers_correct',
            field=models.TextField(blank=True, default='{}', verbose_name='用戶答案是否正確'),
        ),
        migrations.AlterField(
            model_name='question',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='問題ID'),
        ),
    ]
