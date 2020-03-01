from django.contrib import admin
from .models import Specialization, CourseType, Course, Category

admin.site.register(Specialization)
admin.site.register(CourseType)
admin.site.register(Course)
admin.site.register(Category)
