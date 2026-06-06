from django.urls import path
from .views import (
    institute_home,
    institute_courses,
    course_detail,
    course_test,
    institute_certificates,
    institute_gallery,
    exam_home,
    exam_detail,
    exam_section_detail,
    exam_mock_test,
    exam_attempt_history,
    institute_about,
    institute_contact,
    institute_students,
)

app_name = 'institute'

urlpatterns = [
    path('', institute_home, name='home'),
    path('about/', institute_about, name='about'),
    path('contact/', institute_contact, name='contact'),
    path('courses/', institute_courses, name='courses'),
    path('exams/', exam_home, name='exam_home'),
    path('exams/history/', exam_attempt_history, name='exam_attempt_history'),
    path('exams/<int:exam_id>/', exam_detail, name='exam_detail'),
    path('exams/section/<int:section_id>/', exam_section_detail, name='exam_section_detail'),
    path('exams/section/<int:section_id>/mock/<int:mock_id>/test/', exam_mock_test, name='exam_mock_test'),
    path('students/', institute_students, name='students'),
    path('certificates/', institute_certificates, name='certificates'),
    path('gallery/', institute_gallery, name='gallery'),
    path('course/<slug:slug>/', course_detail, name='course_detail'),
    path('course/<slug:slug>/test/', course_test, name='course_test'),
]