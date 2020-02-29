from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView

from .models import Course, Category, CourseType

def overview(request):
    courses = Course.objects.all()
    variables = {
        'spec1_name' : 'Kognitive Systeme',
        'spec1' : courses
    }
    return render(request, 'master/overview.html', variables)

# Course details
def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, 'master/course_detail.html', {'course': course, 'categories': course.categories.all()})

class CourseCreateView(CreateView):
    model = Course
    fields = ['course_name', 'credit_points', 'course_type', 'categories']

class CategoryCreateView(CreateView):
    model = Category
    fields = ['category_name', 'category_abbreviation']

class CourseTypeCreateView(CreateView):
    model = CourseType
    fields = ['type_name', 'type_abbreviation']