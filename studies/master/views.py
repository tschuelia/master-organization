from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView

from .models import Course, Specialization, CourseType, Category

def get_courses_for_category(category):
    category = get_object_or_404(Category, category_name = category)
    return category.get_courses()


def overview(request):

    params = {
        'major1' : get_object_or_404(Category, category_name='Vertiefungsfach 1'),
        'major2' : get_object_or_404(Category, category_name='Vertiefungsfach 2'),
        'minor' : get_object_or_404(Category, category_name='Ergänzungsfach'),
        'electives': get_object_or_404(Category, category_name='Wahlbereich'),
        'soft_skills': get_object_or_404(Category, category_name='Schlüsselqualifikation'),
        'internships': get_object_or_404(CourseType, type_name='Praktikum'),
        'seminars': get_object_or_404(CourseType, type_name='Seminar')
    }

    return render(request, 'master/overview.html', params)

# Course details
def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, 'master/course_detail.html', {'course': course, 'specializations': course.specializations.all()})

class CourseCreateView(CreateView):
    model = Course
    fields = ['course_name', 'credit_points', 'course_type', 'specializations', 'category']

class SpecializationCreateView(CreateView):
    model = Specialization
    fields = ['specialization_name', 'specialization_abbreviation']

class CourseTypeCreateView(CreateView):
    model = CourseType
    fields = ['type_name', 'type_abbreviation']
