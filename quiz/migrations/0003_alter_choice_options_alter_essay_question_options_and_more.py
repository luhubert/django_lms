# Generated by Django 4.2.3 on 2023-08-05 05:57

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0006_courseoffer'),
        ('quiz', '0002_alter_choice_id_alter_progress_id_alter_question_id_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='choice',
            options={'verbose_name': '選項', 'verbose_name_plural': '選項'},
        ),
        migrations.AlterModelOptions(
            name='essay_question',
            options={'verbose_name': '問答題', 'verbose_name_plural': '問答題'},
        ),
        migrations.AlterModelOptions(
            name='mcquestion',
            options={'verbose_name': '多選題', 'verbose_name_plural': '多選題'},
        ),
        migrations.AlterModelOptions(
            name='progress',
            options={'verbose_name': '用戶進度', 'verbose_name_plural': '用戶進度記錄'},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'verbose_name': '問題', 'verbose_name_plural': '問題'},
        ),
        migrations.AlterModelOptions(
            name='quiz',
            options={'verbose_name': '測驗', 'verbose_name_plural': '測驗'},
        ),
        migrations.AlterModelOptions(
            name='sitting',
            options={'permissions': (('view_sittings', '可以查看已完成的考試。'),)},
        ),
        migrations.AlterField(
            model_name='choice',
            name='choice',
            field=models.CharField(help_text='輸入你想要顯示的選項文字', max_length=1000, verbose_name='內容'),
        ),
        migrations.AlterField(
            model_name='choice',
            name='correct',
            field=models.BooleanField(default=False, help_text='這是正確答案嗎？', verbose_name='正確'),
        ),
        migrations.AlterField(
            model_name='choice',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.mcquestion', verbose_name='問題'),
        ),
        migrations.AlterField(
            model_name='mcquestion',
            name='choice_order',
            field=models.CharField(blank=True, choices=[('content', '內容'), ('random', '隨機'), ('none', '無')], help_text='多選題選項對使用者顯示的順序', max_length=30, null=True, verbose_name='選項順序'),
        ),
        migrations.AlterField(
            model_name='progress',
            name='score',
            field=models.CharField(max_length=1024, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')], verbose_name='分數'),
        ),
        migrations.AlterField(
            model_name='progress',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用戶'),
        ),
        migrations.AlterField(
            model_name='question',
            name='content',
            field=models.CharField(help_text='輸入你想要顯示的問題文字', max_length=1000, verbose_name='問題'),
        ),
        migrations.AlterField(
            model_name='question',
            name='explanation',
            field=models.TextField(blank=True, help_text='問題回答後顯示的解釋', max_length=2000, verbose_name='解釋'),
        ),
        migrations.AlterField(
            model_name='question',
            name='figure',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/%Y/%m/%d', verbose_name='圖片'),
        ),
        migrations.AlterField(
            model_name='question',
            name='quiz',
            field=models.ManyToManyField(blank=True, to='quiz.quiz', verbose_name='測驗'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='answers_at_end',
            field=models.BooleanField(default=False, help_text='問題後不顯示正確答案。答案在最後顯示。', verbose_name='最後顯示答案'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='category',
            field=models.TextField(blank=True, choices=[('assignment', '作業'), ('exam', '考試'), ('practice', '練習測驗')]),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='description',
            field=models.TextField(blank=True, help_text='測驗的描述', verbose_name='描述'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='draft',
            field=models.BooleanField(blank=True, default=False, help_text='如果是，則測驗不會在測驗列表中顯示，只能由可以編輯測驗的用戶進行。', verbose_name='草稿'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='exam_paper',
            field=models.BooleanField(default=False, help_text='如果是，則每個用戶的每次嘗試的結果將被存儲。需要打分。', verbose_name='考試卷'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='pass_mark',
            field=models.SmallIntegerField(blank=True, default=50, help_text='通過考試所需的百分比。', validators=[django.core.validators.MaxValueValidator(100)], verbose_name='及格分數'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='random_order',
            field=models.BooleanField(default=False, help_text='是否以隨機順序顯示問題，或者按照設定的順序顯示?', verbose_name='隨機順序'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='single_attempt',
            field=models.BooleanField(default=False, help_text='如果是，則只允許用戶嘗試一次。', verbose_name='單次嘗試'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='title',
            field=models.CharField(max_length=60, verbose_name='標題'),
        ),
        migrations.AlterField(
            model_name='sitting',
            name='complete',
            field=models.BooleanField(default=False, verbose_name='完成'),
        ),
        migrations.AlterField(
            model_name='sitting',
            name='course',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='course.course', verbose_name='課程'),
        ),
        migrations.AlterField(
            model_name='sitting',
            name='current_score',
            field=models.IntegerField(verbose_name='當前分數'),
        ),
        migrations.AlterField(
            model_name='sitting',
            name='end',
            field=models.DateTimeField(blank=True, null=True, verbose_name='結束'),
        ),
        migrations.AlterField(
            model_name='sitting',
            name='incorrect_questions',
            field=models.CharField(blank=True, max_length=1024, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')], verbose_name='不正確的問題'),
        ),
        migrations.AlterField(
            model_name='sitting',
            name='question_list',
            field=models.CharField(max_length=1024, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')], verbose_name='問題列表'),
        ),
        migrations.AlterField(
            model_name='sitting',
            name='question_order',
            field=models.CharField(max_length=1024, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')], verbose_name='問題順序'),
        ),
        migrations.AlterField(
            model_name='sitting',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.quiz', verbose_name='測驗'),
        ),
        migrations.AlterField(
            model_name='sitting',
            name='start',
            field=models.DateTimeField(auto_now_add=True, verbose_name='開始'),
        ),
        migrations.AlterField(
            model_name='sitting',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用戶'),
        ),
        migrations.AlterField(
            model_name='sitting',
            name='user_answers',
            field=models.TextField(blank=True, default='{}', verbose_name='用戶答案'),
        ),
    ]