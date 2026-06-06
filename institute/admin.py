from django.contrib import admin
from django.db.models import Avg, Count, Max

try:
    from unfold.admin import ModelAdmin, TabularInline, StackedInline
except Exception:  # pragma: no cover
    ModelAdmin = admin.ModelAdmin
    TabularInline = admin.TabularInline
    StackedInline = admin.StackedInline

from .models import (
    InstituteCertificate,
    InstituteCourse,
    Exam,
    ExamSection,
    ExamNote,
    ExamMock,
    ExamQuestion,
    ExamMockAttempt,
    StudentAchievement,
)


@admin.register(InstituteCourse)
class InstituteCourseAdmin(ModelAdmin):
    list_display = ('title', 'section_key', 'display_order', 'is_active')
    list_filter = ('section_key', 'is_active')
    search_fields = ('title', 'summary', 'overview', 'slug')
    prepopulated_fields = {'slug': ('title',)}


class ExamSectionInline(TabularInline):
    model = ExamSection
    extra = 0
    fields = ('title', 'display_order', 'is_active')


@admin.register(InstituteCertificate)
class InstituteCertificateAdmin(ModelAdmin):
    list_display = ('certificate_id', 'student_name', 'course_name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('certificate_id', 'student_name', 'course_name')


@admin.register(Exam)
class ExamAdmin(ModelAdmin):
    inlines = [ExamSectionInline]
    list_display = (
        'title',
        'display_order',
        'is_active',
    )
    list_filter = (
        'is_active',
    )
    search_fields = (
        'title',
        'description',
    )


class ExamNoteInline(TabularInline):
    model = ExamNote
    extra = 0
    fields = ('title', 'display_order', 'is_active')


class ExamMockInline(TabularInline):
    model = ExamMock
    extra = 0
    fields = ('title', 'duration_minutes', 'question_count', 'display_order', 'is_active')


class ExamQuestionInline(StackedInline):
    model = ExamQuestion
    extra = 0
    fields = (
        'question_text',
        ('diagram_image', 'diagram_image_url'),
        ('option_a', 'option_b'),
        ('option_c', 'option_d'),
        ('correct_option', 'display_order', 'is_active'),
        'explanation',
    )


@admin.register(ExamSection)
class ExamSectionAdmin(ModelAdmin):
    inlines = [ExamNoteInline, ExamMockInline]
    list_display = ('title', 'exam', 'display_order', 'is_active')
    list_filter = ('exam', 'is_active')
    search_fields = ('title', 'description', 'exam__title')


@admin.register(ExamNote)
class ExamNoteAdmin(ModelAdmin):
    list_display = ('title', 'section', 'display_order', 'is_active')
    list_filter = ('section__exam', 'is_active')
    search_fields = ('title', 'description', 'section__title', 'section__exam__title')


@admin.register(ExamMock)
class ExamMockAdmin(ModelAdmin):
    inlines = [ExamQuestionInline]
    list_display = ('title', 'section', 'duration_minutes', 'question_count', 'display_order', 'is_active')
    list_filter = ('section__exam', 'is_active')
    search_fields = ('title', 'description', 'section__title', 'section__exam__title')


@admin.register(ExamQuestion)
class ExamQuestionAdmin(ModelAdmin):
    list_display = ('id', 'mock', 'short_question', 'correct_option', 'display_order', 'is_active')
    list_filter = ('mock__section__exam', 'mock', 'is_active', 'correct_option')
    search_fields = ('question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'explanation', 'diagram_image_url')

    @admin.display(description='Question')
    def short_question(self, obj):
        text = (obj.question_text or '').strip().replace('\n', ' ')
        return text[:80] + ('...' if len(text) > 80 else '')


@admin.register(ExamMockAttempt)
class ExamMockAttemptAdmin(ModelAdmin):
    change_list_template = 'admin/institute/exammockattempt/change_list.html'
    list_display = (
        'student',
        'mock',
        'score',
        'total_questions',
        'percent',
        'warning_count',
        'auto_submitted',
        'submitted_at',
    )
    list_filter = ('mock__section__exam', 'mock__section', 'mock', 'student', 'auto_submitted', 'submitted_at')
    search_fields = ('student__username', 'student__email', 'mock__title', 'mock__section__title', 'mock__section__exam__title')
    date_hierarchy = 'submitted_at'

    def changelist_view(self, request, extra_context=None):
        queryset = self.get_queryset(request)
        summary = queryset.aggregate(
            attempt_count=Count('id'),
            avg_percent=Avg('percent'),
            best_percent=Max('percent'),
        )
        pass_count = queryset.filter(percent__gte=40).count()
        attempts = summary.get('attempt_count') or 0
        pass_rate = round((pass_count / attempts) * 100, 2) if attempts else 0

        topper = queryset.select_related('student', 'mock').order_by('-percent', '-score').first()
        exam_breakdowns = []
        for exam in Exam.objects.filter(is_active=True).order_by('display_order', 'title'):
            exam_attempts = ExamMockAttempt.objects.filter(mock__section__exam=exam).count()
            exam_breakdowns.append(
                {
                    'exam': exam,
                    'count': exam_attempts,
                    'url': f'?mock__section__exam__id__exact={exam.id}',
                }
            )

        extra = extra_context or {}
        extra.update(
            {
                'analytics_cards': [
                    {'label': 'Total Attempts', 'value': attempts},
                    {'label': 'Average Score %', 'value': round(float(summary.get('avg_percent') or 0), 2)},
                    {'label': 'Pass Rate %', 'value': pass_rate},
                    {'label': 'Top Score %', 'value': round(float(summary.get('best_percent') or 0), 2)},
                ],
                'topper_item': topper,
                'exam_breakdowns': exam_breakdowns,
            }
        )

        return super().changelist_view(request, extra_context=extra)


@admin.register(StudentAchievement)
class StudentAchievementAdmin(ModelAdmin):
    list_display = (
        'student_name',
        'htno',
        'exam_type',
        'rank_label',
        'education',
        'company_name',
        'show_on_home',
        'display_order',
        'is_active',
    )
    list_filter = ('exam_type', 'show_on_home', 'is_active')
    search_fields = ('student_name', 'htno', 'course_name', 'education', 'rank_label', 'company_name', 'review')