from django.contrib import admin
from .models import Specialization, CourseType, Course, Category, Semester, UserCourse

admin.site.register(Specialization)
admin.site.register(CourseType)
admin.site.register(Course)
admin.site.register(UserCourse)
admin.site.register(Category)
admin.site.register(Semester)
