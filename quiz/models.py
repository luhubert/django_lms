import re
import json

from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.validators import (MaxValueValidator, validate_comma_separated_integer_list,)
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.conf import settings
from django.db.models.signals import pre_save

from django.db.models import Q

from model_utils.managers import InheritanceManager
from course.models import Course
from .utils import *

# 選擇題目順序的選項
CHOICE_ORDER_OPTIONS = (
    ('content', _('內容')),
    ('random', _('隨機')),
    ('none', _('無'))
)

# 類別選項
CATEGORY_OPTIONS = (
    ('assignment', _('作業')),
    ('exam', _('考試')),
    ('practice', _('練習測驗'))
)

# 測驗管理器類別
class QuizManager(models.Manager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (Q(title__icontains=query) | 
                         Q(description__icontains=query)|
                         Q(category__icontains=query)|
                         Q(slug__icontains=query)
                        )
            qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
        return qs

# 測驗類別
class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    title = models.CharField(verbose_name=_("標題"), max_length=60, blank=False)
    slug = models.SlugField(blank=True, unique=True)
    description = models.TextField(verbose_name=_("描述"), blank=True, help_text=_("測驗的描述"))
    category = models.TextField(choices=CATEGORY_OPTIONS, blank=True)
    random_order = models.BooleanField(blank=False, default=False, verbose_name=_("隨機順序"), 
        help_text=_("是否以隨機順序顯示問題，或者按照設定的順序顯示?"))

    # max_questions = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("最大問題數"), 
    #     help_text=_("每次嘗試需要回答的問題數量."))

    answers_at_end = models.BooleanField(blank=False, default=False, verbose_name=_("最後顯示答案"),
        help_text=_("問題後不顯示正確答案。答案在最後顯示。"))

    exam_paper = models.BooleanField(blank=False, default=False, verbose_name=_("考試卷"),
        help_text=_("如果是，則每個用戶的每次嘗試的結果將被存儲。需要打分。"))

    single_attempt = models.BooleanField(blank=False, default=False, verbose_name=_("單次嘗試"), 
        help_text=_("如果是，則只允許用戶嘗試一次。"))

    pass_mark = models.SmallIntegerField(blank=True, default=50, verbose_name=_("及格分數"), validators=[MaxValueValidator(100)], 
        help_text=_("通過考試所需的百分比。"))

    draft = models.BooleanField(blank=True, default=False, verbose_name=_("草稿"),
        help_text=_("如果是，則測驗不會在測驗列表中顯示，只能由可以編輯測驗的用戶進行。"))

    timestamp = models.DateTimeField(auto_now=True)

    objects = QuizManager()

    def save(self, force_insert=False, force_update=False, *args, **kwargs):

        if self.single_attempt is True:
            self.exam_paper = True

        if self.pass_mark > 100:
            raise ValidationError('%s is above 100' % self.pass_mark)
        if self.pass_mark < 0:
            raise ValidationError('%s is below 0' % self.pass_mark)

        super(Quiz, self).save(force_insert, force_update, *args, **kwargs)

    class Meta:
        verbose_name = _("測驗")
        verbose_name_plural = _("測驗")

    def __str__(self):
        return self.title

    def get_questions(self):
        return self.question_set.all().select_subclasses()

    @property
    def get_max_score(self):
        return self.get_questions().count()

    def get_absolute_url(self):
        # return reverse('quiz_start_page', kwargs={'pk': self.pk})
        return reverse('quiz_index', kwargs={'slug': self.course.slug})

# 在保存測驗之前生成唯一的slug
def quiz_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(quiz_pre_save_receiver, sender=Quiz)

# 進度管理器類別
class ProgressManager(models.Manager):

    def new_progress(self, user):
        new_progress = self.create(user=user, score="")
        new_progress.save()
        return new_progress

# 進度類別
class Progress(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_("用戶"), on_delete=models.CASCADE)
    score = models.CharField(max_length=1024, verbose_name=_("分數"), validators=[validate_comma_separated_integer_list])

    objects = ProgressManager()

    class Meta:
        verbose_name = _("用戶進度")
        verbose_name_plural = _("用戶進度記錄")

    # @property
    def list_all_cat_scores(self):
        score_before = self.score
        output = {}

        if len(self.score) > len(score_before):
            # 如果添加了新的類別，則保存更改。
            self.save()

        return output

    def update_score(self, question, score_to_add=0, possible_to_add=0):
        # category_test = Category.objects.filter(category=question.category).exists()

        if any([item is False for item in [score_to_add, possible_to_add, isinstance(score_to_add, int), isinstance(possible_to_add, int)]]):
            return _("錯誤"), _("類別不存在或無效的分數")

        to_find = re.escape(str(question.quiz)) + r",(?P<score>\d+),(?P<possible>\d+),"

        match = re.search(to_find, self.score, re.IGNORECASE)

        if match:
            updated_score = int(match.group('score')) + abs(score_to_add)
            updated_possible = int(match.group('possible')) + abs(possible_to_add)

            new_score = ",".join([str(question.quiz), str(updated_score), str(updated_possible), ""])

            # 換掉舊的分數
            self.score = self.score.replace(match.group(), new_score)
            self.save()

        else:
            # 如果不存在但存在，則添加傳入的分數
            self.score += ",".join([str(question.quiz), str(score_to_add), str(possible_to_add), ""])
            self.save()

    def show_exams(self):
        if self.user.is_superuser:
            return Sitting.objects.filter(complete=True).order_by('-end')
        else:
            return Sitting.objects.filter(user=self.user, complete=True).order_by('-end')

# 坐下管理器類別
class SittingManager(models.Manager):

    def new_sitting(self, user, quiz, course):
        if quiz.random_order is True:
            question_set = quiz.question_set.all().select_subclasses().order_by('?')
        else:
            question_set = quiz.question_set.all().select_subclasses()

        question_set = [item.id for item in question_set]

        if len(question_set) == 0:
            raise ImproperlyConfigured('測驗的問題集是空的。請正確配置問題')

        # if quiz.max_questions and quiz.max_questions < len(question_set):
        #     question_set = question_set[:quiz.max_questions]

        questions = ",".join(map(str, question_set)) + ","

        new_sitting = self.create(
            user=user, quiz=quiz, course=course, question_order=questions, 
            question_list=questions, incorrect_questions="",
            current_score=0,
            complete=False,
            user_answers='{}'
        )
        return new_sitting

    def user_sitting(self, user, quiz, course):
        if quiz.single_attempt is True and self.filter(user=user, quiz=quiz, course=course, complete=True).exists():
            return False
        try:
            sitting = self.get(user=user, quiz=quiz, course=course, complete=False)
        except Sitting.DoesNotExist:
            sitting = self.new_sitting(user, quiz, course)
        except Sitting.MultipleObjectsReturned:
            sitting = self.filter(user=user, quiz=quiz, course=course, complete=False)[0]
        return sitting

# 坐下類別
class Sitting(models.Model):
    user_answers_correct = models.TextField(blank=True, default='{}', verbose_name=_("用戶答案是否正確"))  # 添加用戶答案是否正確的欄位
    # 原有的其他欄位
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("用戶"), on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, verbose_name=_("測驗"), on_delete=models.CASCADE)
    course = models.ForeignKey(Course, null=True, verbose_name=_("課程"), on_delete=models.CASCADE)

    question_order = models.CharField(max_length=1024, verbose_name=_("問題順序"),
        validators=[validate_comma_separated_integer_list])

    question_list = models.CharField(max_length=1024, verbose_name=_("問題列表"),
        validators=[validate_comma_separated_integer_list])

    incorrect_questions = models.CharField(max_length=1024, blank=True, verbose_name=_("不正確的問題"),
        validators=[validate_comma_separated_integer_list])

    current_score = models.IntegerField(verbose_name=_("當前分數"))
    complete = models.BooleanField(default=False, blank=False, verbose_name=_("完成"))
    user_answers = models.TextField(blank=True, default='{}', verbose_name=_("用戶答案"))
    start = models.DateTimeField(auto_now_add=True, verbose_name=_("開始"))
    end = models.DateTimeField(null=True, blank=True, verbose_name=_("結束"))

    objects = SittingManager()
    def add_user_answer(self, question, guess, correct):
        # 增加一個參數correct來記錄答案是否正確
        current = json.loads(self.user_answers)
        current[question.id] = guess
        self.user_answers = json.dumps(current)

        current_correct = json.loads(self.user_answers_correct)
        current_correct[question.id] = correct
        self.user_answers_correct = json.dumps(current_correct)

        self.save()

    class Meta:
        permissions = (("view_sittings", _("可以查看已完成的考試。")),)

    def get_first_question(self):
        if not self.question_list:
            return False

        first, _ = self.question_list.split(',', 1)
        question_id = int(first)
        return Question.objects.get_subclass(id=question_id)

    def remove_first_question(self):
        if not self.question_list:
            return

        _, others = self.question_list.split(',', 1)
        self.question_list = others
        self.save()

    def add_to_score(self, points):
        self.current_score += int(points)
        self.save()

    @property
    def get_current_score(self):
        return self.current_score

    def _question_ids(self):
        return [int(n) for n in self.question_order.split(',') if n]

    @property
    def get_percent_correct(self):
        dividend = float(self.current_score)
        divisor = len(self._question_ids())
        if divisor < 1:
            return 0            # 防止除以零錯誤

        if dividend > divisor:
            return 100

        correct = int(round((dividend / divisor) * 100))

        if correct >= 1:
            return correct
        else:
            return 0

    def mark_quiz_complete(self):
        self.complete = True
        self.end = now()
        self.save()

    def add_incorrect_question(self, question):
        if len(self.incorrect_questions) > 0:
            self.incorrect_questions += ','
        self.incorrect_questions += str(question.id) + ","
        if self.complete:
            self.add_to_score(-1)
        self.save()

    @property
    def get_incorrect_questions(self):
        return [int(q) for q in self.incorrect_questions.split(',') if q]

    def remove_incorrect_question(self, question):
        current = self.get_incorrect_questions
        current.remove(question.id)
        self.incorrect_questions = ','.join(map(str, current))
        self.add_to_score(1)
        self.save()

    @property
    def check_if_passed(self):
        return self.get_percent_correct >= self.quiz.pass_mark

    @property
    def result_message(self):
        if self.check_if_passed:
            return f"你已經通過了這個測驗，恭喜"
        else:
            return f"你沒有通過這個測驗，再給它一次機會。"

    def add_user_answer(self, question, guess):
        current = json.loads(self.user_answers)
        current[question.id] = guess
        self.user_answers = json.dumps(current)
        self.save()

    def get_questions(self, with_answers=False):
        question_ids = self._question_ids()
        questions = sorted(self.quiz.question_set.filter(id__in=question_ids).select_subclasses(), key=lambda q: question_ids.index(q.id))

        if with_answers:
            user_answers = json.loads(self.user_answers)
            for question in questions:
                question.user_answer = user_answers[str(question.id)]

        return questions

    @property
    def questions_with_user_answers(self):
        return {q: q.user_answer for q in self.get_questions(with_answers=True)}

    @property
    def get_max_score(self):
        return len(self._question_ids())

    def progress(self):
        answered = len(json.loads(self.user_answers))
        total = self.get_max_score
        return answered, total


class Question(models.Model):
    id = models.AutoField(primary_key=True, verbose_name=_("問題ID"))  # 添加問題ID
    knowledge_tag = models.CharField(max_length=100, blank=False ,default='', verbose_name=_("知識點1"))  # 添加知識點
    knowledge_tag1 = models.CharField(max_length=100, blank=True ,default='', verbose_name=_("知識點2"))  # 添加知識點
    knowledge_tag2 = models.CharField(max_length=100, blank=True ,default='', verbose_name=_("知識點3"))  # 添加知識點
    quiz = models.ManyToManyField(Quiz, verbose_name=_("測驗"), blank=True)
    figure = models.ImageField(upload_to='uploads/%Y/%m/%d', blank=True, null=True, verbose_name=_("圖片"))
    content = models.CharField(max_length=1000, blank=False, 
        help_text=_("輸入你想要顯示的問題文字"), verbose_name=_('問題'))
    explanation = models.TextField(max_length=2000, blank=True,
        help_text=_("問題回答後顯示的解釋"),
        verbose_name=_('解釋'))

    objects = InheritanceManager()

    class Meta:
        verbose_name = _("問題")
        verbose_name_plural = _("問題")

    def __str__(self):
        return self.content

#選擇題
class MCQuestion(Question):

    choice_order = models.CharField(
        max_length=30, null=True, blank=True,
        choices=CHOICE_ORDER_OPTIONS,
        help_text=_("選擇題選項對使用者顯示的順序"),
        verbose_name=_("選項順序"))

    def check_if_correct(self, guess):
        answer = Choice.objects.get(id=guess)
        correct = answer.correct is True
        # 儲存用戶的答案和答案是否正確
        Sitting.objects.filter(user=self.user, quiz=self.quiz, complete=False).update_user_answer(self, guess, correct)
        return correct
    
    
    def order_choices(self, queryset):
        if self.choice_order == 'content':
            return queryset.order_by('choice')
        if self.choice_order == 'random':
            return queryset.order_by('?')
        if self.choice_order == 'none':
            return queryset.order_by()
        return queryset

    def get_choices(self):
        return self.order_choices(Choice.objects.filter(question=self))

    def get_choices_list(self):
        return [(choice.id, choice.choice) for choice in
                self.order_choices(Choice.objects.filter(question=self))]

    def answer_choice_to_string(self, guess):
        return Choice.objects.get(id=guess).choice

    class Meta:
        verbose_name = _("選擇題")
        verbose_name_plural = _("選擇題")


class Choice(models.Model):
    question = models.ForeignKey(MCQuestion, verbose_name=_("問題"), on_delete=models.CASCADE)

    choice = models.CharField(max_length=1000, blank=False,
        help_text=_("輸入你想要顯示的選項文字"), 
        verbose_name=_("內容"))

    correct = models.BooleanField(blank=False, default=False, 
        help_text=_("這是正確答案嗎？"), 
        verbose_name=_("正確"))

    def __str__(self):
        return self.choice

    class Meta:
        verbose_name = _("選項")
        verbose_name_plural = _("選項")


class Essay_Question(Question):

    def check_if_correct(self, guess):
        # 儲存用戶的答案，由於問答題無法自動判斷答案是否正確，所以此處暫時將答案是否正確設為False
        Sitting.objects.filter(user=self.user, quiz=self.quiz, complete=False).update_user_answer(self, guess, False)

        return False

    def get_answers(self):
        return False

    def get_answers_list(self):
        return False

    def answer_choice_to_string(self, guess):
        return str(guess)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = _("問答題")
        verbose_name_plural = _("問答題")


