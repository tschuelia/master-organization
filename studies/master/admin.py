from django.contrib import admin
from .models import Category, CourseType, Course

admin.site.register(Category)
admin.site.register(CourseType)
admin.site.register(Course)
