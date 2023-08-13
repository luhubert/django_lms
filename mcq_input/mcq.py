class Question(models.Model):
    content = models.TextField()
    answer = models.CharField(max_length=200)
    # 其他你想要的欄位

from django import forms

class QuestionImportForm(forms.Form):
    file = forms.FileField('/Users/luchunhung/Desktop/python_test/output4.txt')

from django.shortcuts import render, redirect

def import_questions(request):
    if request.method == 'POST':
        form = QuestionImportForm(request.POST, request.FILES)
        if form.is_valid():
            # 處理檔案並匯入試題
            handle_uploaded_file(request.FILES['file'])
            return redirect('some-view-name')
    else:
        form = QuestionImportForm()
    return render(request, 'import.html', {'form': form})
