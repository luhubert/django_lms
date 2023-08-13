from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.views.generic import CreateView, ListView
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm

from .decorators import lecturer_required, student_required, admin_required
from course.models import Course
from result.models import TakenCourse
from app.models import Session, Semester
from .forms import StaffAddForm, StudentAddForm, ProfileUpdateForm
from .models import User, Student

# 驗證使用者名稱是否已被使用
def validate_username(request):
    username = request.GET.get("username", None)
    data = {
        "is_taken": User.objects.filter(username__iexact = username).exists()
    }
    return JsonResponse (data)

# 註冊新的學生帳號
def register(request):
    if request.method == 'POST':
        form = StudentAddForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'帳號建立成功。')
        else:
            messages.error(request, f'有些東西不對，請正確填寫所有欄位。')
    else:
        form = StudentAddForm(request.POST)
    return render(request, "registration/register.html", {'form': form})

# 顯示使用者的個人資料
@login_required
def profile(request):
    try:
        current_session = get_object_or_404(Session, is_current_session=True)
        current_semester = get_object_or_404(Semester, is_current_semester=True, session=current_session)
        
    except Semester.MultipleObjectsReturned and Semester.DoesNotExist and Session.DoesNotExist:
        raise Http404

    if request.user.is_lecturer:
        courses = Course.objects.filter(allocated_course__lecturer__pk=request.user.id).filter(
            semester=current_semester)
        return render(request, 'accounts/profile.html', {
            'title': request.user.get_full_name,
            "courses": courses,
            'current_session': current_session,
            'current_semester': current_semester,
        })
    elif request.user.is_student:
        level = Student.objects.get(student__pk=request.user.id)
        courses = TakenCourse.objects.filter(student__student__id=request.user.id, course__level=level.level)
        context = {
            'title': request.user.get_full_name,
            'courses': courses,
            'level': level,
            'current_session': current_session,
            'current_semester': current_semester,
        }
        return render(request, 'accounts/profile.html', context)
    else:
        staff = User.objects.filter(is_lecturer=True)
        return render(request, 'accounts/profile.html', {
            'title': request.user.get_full_name,
            "staff": staff,
            'current_session': current_session,
            'current_semester': current_semester,
        })

# 顯示選定使用者的個人資料
@login_required
@admin_required
def profile_single(request, id):
    if request.user.id == id:
        return redirect("/profile/")

    current_session = get_object_or_404(Session, is_current_session=True)
    current_semester = get_object_or_404(Semester, is_current_semester=True, session=current_session)
    user = User.objects.get(pk=id)
    if user.is_lecturer:
        courses = Course.objects.filter(allocated_course__lecturer__pk=id).filter(semester=current_semester)
        context = {
            'title': user.get_full_name,
            "user": user,
            "user_type": "講師",
            "courses": courses,
            'current_session': current_session,
            'current_semester': current_semester,
        }
        return render(request, 'accounts/profile_single.html', context)
    elif user.is_student:
        student = Student.objects.get(student__pk=id)
        courses = TakenCourse.objects.filter(student__student__id=id, course__level=student.level)
        context = {
            'title': user.get_full_name,
            'user': user,
            "user_type": "學生",
            'courses': courses,
            'student': student,
            'current_session': current_session,
            'current_semester': current_semester,
        }
        return render(request, 'accounts/profile_single.html', context)
    else:
        context = {
            'title': user.get_full_name,
            "user": user,
            "user_type": "超級使用者",
            'current_session': current_session,
            'current_semester': current_semester,
        }
        return render(request, 'accounts/profile_single.html', context)

# 顯示管理員面板
@login_required
@admin_required
def admin_panel(request):
    return render(request, 'setting/admin_panel.html', {})

# 設定視圖
@login_required
def profile_update(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '您的個人資料已成功更新。')
            return redirect('profile')
        else:
            messages.error(request, '請修正以下的錯誤。')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'setting/profile_info_change.html', {
        'title': '設定 | DjangoSMS',
        'form': form,
    })

# 更改密碼
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '您的密碼已成功更新！')
            return redirect('profile')
        else:
            messages.error(request, '請修正以下的錯誤。')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'setting/password_change.html', {
        'form': form,
    })

# 新增教職員工
@login_required
@admin_required
def staff_add_view(request):
    if request.method == 'POST':
        form = StaffAddForm(request.POST)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        if form.is_valid():
            form.save()
            messages.success(request, "講師 " + first_name + ' ' + last_name + " 的帳號已建立。")
            return redirect("lecturer_list")
    else:
        form = StaffAddForm()

    context = {
        'title': '新增講師 | DjangoSMS',
        'form': form,
    }

    return render(request, 'accounts/add_staff.html', context)

# 編輯教職員工
@login_required
@admin_required
def edit_staff(request, pk):
    instance = get_object_or_404(User, is_lecturer=True, pk=pk)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=instance)
        full_name = instance.get_full_name
        if form.is_valid():
            form.save()

            messages.success(request, '講師 ' + full_name + ' 已被更新。')
            return redirect('lecturer_list')
        else:
            messages.error(request, '請修正以下的錯誤。')
    else:
        form = ProfileUpdateForm(instance=instance)
    return render(request, 'accounts/edit_lecturer.html', {
        'title': '編輯講師 | DjangoSMS',
        'form': form,
    })

# 列出所有講師
@method_decorator([login_required, admin_required], name='dispatch')
class LecturerListView(ListView):
    queryset = User.objects.filter(is_lecturer=True)
    template_name = "accounts/lecturer_list.html"
    paginate_by = 10  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "講師 | DjangoSMS"
        return context

# 刪除教職員工
@login_required
@admin_required
def delete_staff(request, pk):
    lecturer = get_object_or_404(User, pk=pk)
    full_name = lecturer.get_full_name
    lecturer.delete()
    messages.success(request, '講師 ' + full_name + ' 已被刪除。')
    return redirect('lecturer_list')

# 新增學生
@login_required
@admin_required
def student_add_view(request):
    if request.method == 'POST':
        form = StudentAddForm(request.POST)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        if form.is_valid():
            form.save()
            messages.success(request, first_name + ' ' + last_name + ' 的帳號已建立。')
            return redirect('student_list')
        else:
            messages.error(request, '請修正以下的錯誤。')
    else:
        form = StudentAddForm()

    return render(request, 'accounts/add_student.html', {
        'title': "新增學生 | DjangoSMS",
        'form': form
    })

# 編輯學生
@login_required
@admin_required
def edit_student(request, pk):
    instance = get_object_or_404(User, is_student=True, pk=pk)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=instance)
        full_name = instance.get_full_name
        if form.is_valid():
            form.save()

            messages.success(request, ('學生 ' + full_name + ' 已被更新。'))
            return redirect('student_list')
        else:
            messages.error(request, '請修正以下的錯誤。')
    else:
        form = ProfileUpdateForm(instance=instance)
    return render(request, 'accounts/edit_student.html', {
        'title': '編輯個人資料 | DjangoSMS',
        'form': form,
    })

# 列出所有學生
@method_decorator([login_required, admin_required], name='dispatch')
class StudentListView(ListView):
    template_name = "accounts/student_list.html"
    paginate_by = 10  # if pagination is desired

    def get_queryset(self):
        queryset = Student.objects.all()
        query = self.request.GET.get('student_id')
        if query is not None:
            queryset = queryset.filter(Q(department=query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "學生 | DjangoSMS"
        return context

# 刪除學生
@login_required
@admin_required
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    messages.success(request, '學生已被刪除。')
    return redirect('student_list')
