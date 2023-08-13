from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _

from .models import Quiz, Progress, Question, MCQuestion, Choice, Essay_Question, Sitting


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1


class QuizAdminForm(forms.ModelForm):

    class Meta:
        model = Quiz
        exclude = []

    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all().select_subclasses(),
        required=False,
        label=_("Questions"),
        widget=FilteredSelectMultiple(
            verbose_name=_("Questions"),
            is_stacked=False))

    def __init__(self, *args, **kwargs):
        super(QuizAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['questions'].initial = self.instance.question_set.all().select_subclasses()

    def save(self, commit=True):
        quiz = super(QuizAdminForm, self).save(commit=False)
        quiz.save()
        quiz.question_set.set(self.cleaned_data['questions'])
        self.save_m2m()
        return quiz


class QuizAdmin(admin.ModelAdmin):
    form = QuizAdminForm

    list_display = ('title', 'category', 'random_order', 'single_attempt', 'pass_mark', 'draft')
    search_fields = ('title', 'description', 'category')


class MCQuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'knowledge_tag','knowledge_tag1', 'knowledge_tag2')
    # list_filter = ('category',)
    fields = ('content', 'figure', 'quiz', 'explanation', 'knowledge_tag', 'knowledge_tag1', 'knowledge_tag2','choice_order')

    search_fields = ('content', 'explanation')
    filter_horizontal = ('quiz',)

    inlines = [ChoiceInline]
    search_fields = ('content', 'knowledge_tag','knowledge_tag1', 'knowledge_tag2')


class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user', 'score', )
    


class EssayQuestionAdmin(admin.ModelAdmin):
    list_display = ('content','knowledge_tag' )
    # list_filter = ('category',)
    fields = ('content', 'quiz', 'explanation', )
    search_fields = ('content', 'explanation','knowledge_tag')
    filter_horizontal = ('quiz',)

class SittingAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'course', 'current_score', 'complete', 'start', 'end')
    search_fields = ('user', 'quiz', 'course')

admin.site.register(Quiz, QuizAdmin)
admin.site.register(MCQuestion, MCQuestionAdmin)
admin.site.register(Progress, ProgressAdmin)
admin.site.register(Essay_Question, EssayQuestionAdmin)
admin.site.register(Sitting, SittingAdmin)
