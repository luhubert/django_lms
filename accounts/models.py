from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings

from django.db.models import Q
from PIL import Image

from course.models import Program
from .validators import ASCIIUsernameValidator

# 定義學位等級
BACHLOAR_DEGREE = "Bachloar"
MASTER_DEGREE = "Master"

LEVEL = (
    (BACHLOAR_DEGREE, "學士學位"),
    (MASTER_DEGREE, "碩士學位"),
)

# # 定義親屬關係
# FATHER = "Father"
# MOTHER = "Mother"
# BROTHER = "Brother"
# SISTER = "Sister"
# GRAND_MOTHER = "Grand mother"
# GRAND_FATHER = "Grand father"
# OTHER = "Other"

# RELATION_SHIP  = (
#     (FATHER, "父親"),
#     (MOTHER, "母親"),
#     (BROTHER, "兄弟"),
#     (SISTER, "姐妹"),
#     (GRAND_MOTHER, "祖母"),
#     (GRAND_FATHER, "祖父"),
#     (OTHER, "其他"),
# )

# 自定義的 UserManager，增加了一個搜尋方法
class UserManager(UserManager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (Q(username__icontains=query) | 
                         Q(first_name__icontains=query)| 
                         Q(last_name__icontains=query)| 
                         Q(email__icontains=query)
                        )
            qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
        return qs

# 自定義的 User 模型，繼承了 Django 的 AbstractUser
class User(AbstractUser):
    is_student = models.BooleanField(default=False)  # 是否為學生
    is_lecturer = models.BooleanField(default=False)  # 是否為講師
    # is_parent = models.BooleanField(default=False)  # 是否為家長
    # is_dep_head = models.BooleanField(default=False)  # 是否為部門主管
    phone = models.CharField(max_length=60, blank=True, null=True)  # 電話號碼
    address = models.CharField(max_length=60, blank=True, null=True)  # 地址
    picture = models.ImageField(upload_to='profile_pictures/%y/%m/%d/', default='default.png', null=True)  # 頭像
    email = models.EmailField(blank=True, null=True)  # 電子郵件

    username_validator = ASCIIUsernameValidator()

    objects = UserManager()

    @property
    def get_full_name(self):
        full_name = self.username
        if self.first_name and self.last_name:
            full_name = self.first_name + " " + self.last_name
        return full_name

    def __str__(self):
        return '{} ({})'.format(self.username, self.get_full_name)

    @property
    def get_user_role(self):
        if self.is_superuser:
            return "管理員"
        elif self.is_student:
            return "學生"
        elif self.is_lecturer:
            return "講師"

    def get_picture(self):
        try:
            return self.picture.url
        except:
            no_picture = settings.MEDIA_URL + 'default.png'
            return no_picture

    def get_absolute_url(self):
        return reverse('profile_single', kwargs={'id': self.id})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.picture.path)
        except:
            pass

    def delete(self, *args, **kwargs):
        if self.picture.url != settings.MEDIA_URL + 'default.png':
            self.picture.delete()
        super().delete(*args, **kwargs)

# 學生模型的管理器，增加了一個搜尋方法
class StudentManager(models.Manager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (Q(level__icontains=query) | 
                         Q(department__icontains=query)
                        )
            qs = qs.filter(or_lookup).distinct() # distinct() is often necessary with Q lookups
        return qs

# 學生模型
class Student(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE)  # 關聯 User 模型
    level = models.CharField(max_length=25, choices=LEVEL, null=True)  # 學位等級
    department = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)  # 所屬學系

    objects = StudentManager()

    def __str__(self):
        return self.student.get_full_name

    def get_absolute_url(self):
        return reverse('profile_single', kwargs={'id': self.id})

    def delete(self, *args, **kwargs):
        self.student.delete()
        super().delete(*args, **kwargs)

# # 家長模型
# class Parent(models.Model):
#     """
#     將學生與其家長連接起來，家長只能查看與他們連接的學生的信息
#     """
#     user = models.OneToOneField(User, on_delete=models.CASCADE)  # 關聯 User 模型
#     student = models.OneToOneField(Student, null=True, on_delete=models.SET_NULL)  # 關聯 Student 模型
#     first_name = models.CharField(max_length=120)  # 名字
#     last_name = models.CharField(max_length=120)  # 姓氏
#     phone = models.CharField(max_length=60, blank=True, null=True)  # 電話號碼
#     email = models.EmailField(blank=True, null=True)  # 電子郵件

#     # 學生與家長之間的關係（例如：父親、母親、兄弟、姐妹）
#     relation_ship = models.TextField(choices=RELATION_SHIP, blank=True)

#     def __str__(self):
#         return self.user.username

# 部門主管模型
class DepartmentHead(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # 關聯 User 模型
    department = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "{}".format(self.user)
