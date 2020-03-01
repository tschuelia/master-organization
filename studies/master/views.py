from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import (
    get_total_credits,
    get_total_average,
    Course, 
    Specialization, 
    CourseType, 
    Category, 
    Semester
)
from django.urls import reverse_lazy

def get_courses_for_category(category):
    category = get_object_or_404(Category, category_name = category)
    return category.get_courses()

def get_credits_sem_int():
    internship = get_object_or_404(CourseType, type_name='Praktikum')
    seminar = get_object_or_404(CourseType, type_name='Seminar')
    return internship.get_sum_of_credits() + seminar.get_sum_of_credits()

def overview(request):
    internship = get_object_or_404(CourseType, type_name='Praktikum')
    seminar = get_object_or_404(CourseType, type_name='Seminar')

    sum_credits_int_sem = get_credits_sem_int()
    missing_int_sem = max(0, 12 - sum_credits_int_sem)

    seminars_and_internships_valid = missing_int_sem == 0
    
    params = {
        'total_credits': get_total_credits(),
        'total_missing_credits': 90 - get_total_credits(),
        'total_average': get_total_average(),
        'major1' : get_object_or_404(Category, category_name='Vertiefungsfach 1'),
        'major2' : get_object_or_404(Category, category_name='Vertiefungsfach 2'),
        'minor' : get_object_or_404(Category, category_name='Ergänzungsfach'),
        'electives': get_object_or_404(Category, category_name='Wahlbereich'),
        'soft_skills': get_object_or_404(Category, category_name='Schlüsselqualifikation'),
        'internships': internship,
        'seminars': seminar,
        'sum_credits_int_sem': sum_credits_int_sem,
        'missing_int_sem': missing_int_sem,
        'seminars_and_internships_valid': seminars_and_internships_valid,
        'base_modules': get_object_or_404(CourseType, type_name='Stammmodul')
    }

    return render(request, 'master/overview.html', params)

def semesters(request):
    semesters = Semester.objects.all()
    semesters.order_by('year')
    return render(request, 'master/semester_view.html', {'semesters': semesters})

# Course details
def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, 'master/course_detail.html', {'course': course, 'specializations': course.specializations.all()})

def confirm_course(request, course_id):
    if request.method == 'GET':
        course = get_object_or_404(Course, pk=course_id)
        return render(request, 'master/confirm_course.html', {'course': course})
    else:
        course = get_object_or_404(Course, pk=course_id)
        course.included = False
        course.save()
        return redirect('course-detail', course_id=course.pk)

class CourseCreateView(CreateView):
    model = Course
    fields = '__all__'

    def form_valid(self, form):
        self.object = form.save()
        if (self.object.course_type.type_name == 'Praktikum' \
            or self.object.course_type.type_name == 'Seminar') \
            and self.object.included \
            and get_credits_sem_int() >= 18:
                # no more seminars/internships creditable
                return redirect('course-confirm', course_id=self.object.pk)
                
        return redirect('course-detail', course_id=self.object.pk)

class CourseUpdateView(UpdateView):
    model = Course
    fields = '__all__'

    def form_valid(self, form):
        self.object = form.save()
        if (self.object.course_type.type_name == 'Praktikum' \
            or self.object.course_type.type_name == 'Seminar') \
            and self.object.included \
            and get_credits_sem_int() >= 18:
                # no more seminars/internships creditable
                return redirect('course-confirm', course_id=self.object.pk)
                
        return redirect('course-detail', course_id=self.object.pk)

class CourseDeleteView(DeleteView):
    model = Course
    success_url = '/master/'

class SpecializationCreateView(CreateView):
    model = Specialization
    fields = '__all__'

class CourseTypeCreateView(CreateView):
    model = CourseType
    fields = '__all__'
