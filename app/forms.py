from django import forms
from django.db import transaction

from .models import NewsAndEvents, Session, Semester, SEMESTER

# 新聞和事件表單
class NewsAndEventsForm(forms.ModelForm):
    class Meta:
        model = NewsAndEvents
        fields = ('title', 'summary', 'posted_as',)
        labels = {
            'title': '標題',
            'summary': '摘要',
            'posted_as': '發布者',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['summary'].widget.attrs.update({'class': 'form-control'})
        self.fields['posted_as'].widget.attrs.update({'class': 'form-control'})

# 學期表單
class SessionForm(forms.ModelForm):
    next_session_begins = forms.DateTimeField(
        widget=forms.TextInput(
            attrs={
                'type': 'date',
            }
        ),
        required=True,
        label="下一學期開始時間")

    class Meta:
        model = Session
        fields = ['session', 'is_current_session', 'next_session_begins']
        labels = {
            'session': '學期',
            'is_current_session': '是否為當前學期',
            'next_session_begins': '下一學期開始時間',
        }

# 學年表單
class SemesterForm(forms.ModelForm):
    semester = forms.CharField(
        widget=forms.Select(
            choices=SEMESTER,
            attrs={
                'class': 'browser-default custom-select',
            }
        ),
        label="學年",
    )
    is_current_semester = forms.CharField(
        widget=forms.Select(
            choices=((True, '是'), (False, '否')),
            attrs={
                'class': 'browser-default custom-select',
            }
        ),
        label="是否為當前學年？",
    )
    session = forms.ModelChoiceField(
        queryset=Session.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'browser-default custom-select',
            }
        ),
        required=True,
        label="學期"
    )

    next_semester_begins = forms.DateTimeField(
        widget=forms.TextInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
            }
        ),
        required=True,
        label="下一學年開始時間")

    class Meta:
        model = Semester
        fields = ['semester', 'is_current_semester', 'session', 'next_semester_begins']
        labels = {
            'semester': '學年',
            'is_current_semester': '是否為當前學年',
            'session': '學期',
            'next_semester_begins': '下一學年開始時間',
        }
