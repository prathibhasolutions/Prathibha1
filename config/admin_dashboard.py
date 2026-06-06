from services.models import ServiceBooking
from technologies.models import TechnologyBooking
from solutions.models import SolutionBooking
from institute.models import InstituteCourse, Exam, ExamSection, ExamMock


def dashboard_callback(request, context):
    total_service = ServiceBooking.objects.count()
    total_tech = TechnologyBooking.objects.count()
    total_solution = SolutionBooking.objects.count()
    total_courses = InstituteCourse.objects.filter(is_active=True).count()
    total_exams = Exam.objects.filter(is_active=True).count()
    total_sections = ExamSection.objects.filter(is_active=True).count()
    total_mocks = ExamMock.objects.filter(is_active=True).count()

    context['dashboard_cards'] = [
        {
            'title': 'Service Bookings',
            'value': total_service,
            'subtitle': 'Repair and support requests',
            'url': '/admin/services/servicebooking/',
            'accent': 'sky',
        },
        {
            'title': 'Technology Bookings',
            'value': total_tech,
            'subtitle': 'Tech visit and diagnostics',
            'url': '/admin/technologies/technologybooking/',
            'accent': 'cyan',
        },
        {
            'title': 'Solution Bookings',
            'value': total_solution,
            'subtitle': 'Website and app projects',
            'url': '/admin/solutions/solutionbooking/',
            'accent': 'blue',
        },
        {
            'title': 'Active Courses',
            'value': total_courses,
            'subtitle': 'Institute course catalog',
            'url': '/admin/institute/institutecourse/',
            'accent': 'violet',
        },
        {
            'title': 'Exam Categories',
            'value': total_exams,
            'subtitle': 'Exam groups configured',
            'url': '/admin/institute/exam/',
            'accent': 'emerald',
        },
        {
            'title': 'Exam Sections',
            'value': total_sections,
            'subtitle': 'Subject/section breakdown',
            'url': '/admin/institute/examsection/',
            'accent': 'amber',
        },
        {
            'title': 'Mock Tests',
            'value': total_mocks,
            'subtitle': 'Mock sets available',
            'url': '/admin/institute/exammock/',
            'accent': 'rose',
        },
    ]

    return context
