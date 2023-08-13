# Generated by Django 4.2.3 on 2023-08-05 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0003_alter_choice_options_alter_essay_question_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mcquestion',
            options={'verbose_name': '選擇題', 'verbose_name_plural': '選擇題'},
        ),
        migrations.AlterField(
            model_name='mcquestion',
            name='choice_order',
            field=models.CharField(blank=True, choices=[('content', '內容'), ('random', '隨機'), ('none', '無')], help_text='選擇題選項對使用者顯示的順序', max_length=30, null=True, verbose_name='選項順序'),
        ),
    ]