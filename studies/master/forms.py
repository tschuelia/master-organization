from django import forms
from django.urls import reverse_lazy
from django_addanother.widgets import AddAnotherWidgetWrapper

from .models import StudentCourse


class StudentCourseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_required_attribute = False

    class Meta:
        model = StudentCourse
        exclude = ["student"]
        widgets = {
            "course": AddAnotherWidgetWrapper(
                forms.Select(
                    attrs={
                        "class": "selectpicker",
                        "data-live-search": "true",
                        "data-size": "5",
                    },
                ),
                reverse_lazy("course-create"),
            ),
            "category": forms.Select(
                attrs={"class": "selectpicker", "data-live-search": "true",}
            ),
            "semester": forms.Select(
                attrs={"class": "selectpicker", "data-live-search": "true",}
            ),
        }
