from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Category,
    Course,
    CourseType,
    Semester,
    Specialization,
    Student,
    StudentCourse,
)

admin.site.register(Student, UserAdmin)

admin.site.register(Specialization)
admin.site.register(CourseType)
admin.site.register(Course)
admin.site.register(StudentCourse)
admin.site.register(Category)
admin.site.register(Semester)
