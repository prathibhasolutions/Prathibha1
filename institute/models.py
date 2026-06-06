from django.db import models
from django.conf import settings


class InstituteCourse(models.Model):
    section_key = models.SlugField(max_length=120, help_text='Example: programming-languages')
    section_title = models.CharField(max_length=180, blank=True)
    section_description = models.TextField(blank=True)

    slug = models.SlugField(
        unique=True,
        max_length=180,
        help_text='Use an existing slug to open detailed course page.'
    )

    title = models.CharField(max_length=180)
    summary = models.TextField()
    overview = models.TextField(blank=True)
    syllabus = models.TextField(blank=True, help_text='Add one syllabus topic per line.')
    notes_url = models.URLField(blank=True, help_text='Optional external notes link for this course.')
    icon_sprite = models.CharField(max_length=80, default='institute')

    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('display_order', 'id')

    def __str__(self):
        return self.title


class InstituteCertificate(models.Model):
    certificate_id = models.CharField(max_length=60, unique=True)
    student_name = models.CharField(max_length=160)
    course_name = models.CharField(max_length=180)
    completed_on = models.DateField(null=True, blank=True)
    certificate_image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('certificate_id',)

    def __str__(self):
        return f'{self.certificate_id} - {self.student_name}'


class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('display_order', 'title')

    def __str__(self):
        return self.title


class ExamSection(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('display_order', 'title')

    def __str__(self):
        return f'{self.exam.title} - {self.title}'


class ExamNote(models.Model):
    section = models.ForeignKey(ExamSection, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='institute/exam_notes/', blank=True)
    external_url = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('display_order', 'title')

    def __str__(self):
        return f'{self.section.title} - {self.title}'


class ExamMock(models.Model):
    section = models.ForeignKey(ExamSection, on_delete=models.CASCADE, related_name='mocks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    test_url = models.URLField(blank=True, help_text='Optional external test URL.')
    duration_minutes = models.PositiveIntegerField(default=30)
    question_count = models.PositiveIntegerField(default=0)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('display_order', 'title')

    def __str__(self):
        return f'{self.section.title} - {self.title}'


class ExamQuestion(models.Model):
    OPTION_A = 'A'
    OPTION_B = 'B'
    OPTION_C = 'C'
    OPTION_D = 'D'
    OPTION_CHOICES = (
        (OPTION_A, 'Option A'),
        (OPTION_B, 'Option B'),
        (OPTION_C, 'Option C'),
        (OPTION_D, 'Option D'),
    )

    mock = models.ForeignKey(ExamMock, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField(help_text='Supports LaTeX. Use $...$ for inline and $$...$$ for block equations. For chemistry, use mhchem notation like \\ce{H2O}; structural diagrams such as benzene rings need an image or a chemistry-specific renderer.')
    diagram_image = models.FileField(
        upload_to='institute/question_diagrams/',
        blank=True,
        help_text='Optional chemistry/organic structure diagram image for this question.',
    )
    diagram_image_url = models.URLField(
        blank=True,
        help_text='Optional external diagram URL if you do not upload an image.',
    )
    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    explanation = models.TextField(blank=True, help_text='Optional explanation shown after submission.')
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('display_order', 'id')

    def __str__(self):
        return f'{self.mock.title} - Q{self.id}'


class ExamMockAttempt(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exam_mock_attempts')
    mock = models.ForeignKey(ExamMock, on_delete=models.CASCADE, related_name='attempts')
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    warning_count = models.PositiveIntegerField(default=0)
    auto_submitted = models.BooleanField(default=False)
    auto_submit_reason = models.CharField(max_length=120, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-submitted_at',)

    def __str__(self):
        return f'{self.student} - {self.mock.title} ({self.score}/{self.total_questions})'


class StudentAchievement(models.Model):
    EXAM_EAPCET = 'eapcet'
    EXAM_JEE_MAINS = 'jee_mains'
    EXAM_PLACEMENT = 'placement'
    EXAM_OTHER = 'other'

    EXAM_CHOICES = (
        (EXAM_EAPCET, 'EAPCET'),
        (EXAM_JEE_MAINS, 'JEE Mains'),
        (EXAM_PLACEMENT, 'Placed Students'),
        (EXAM_OTHER, 'Other Achievements'),
    )

    student_name = models.CharField(max_length=160)
    htno = models.CharField(max_length=80, blank=True, help_text='Hall ticket number or student ID')
    course_name = models.CharField(max_length=180, blank=True)
    education = models.CharField(max_length=180, blank=True, help_text='Example: B.Tech CSE, Intermediate MPC')
    exam_type = models.CharField(max_length=20, choices=EXAM_CHOICES, default=EXAM_OTHER)
    rank_label = models.CharField(max_length=120, blank=True, help_text='Examples: AIR 120, State Rank 45, Top 500')
    company_name = models.CharField(max_length=180, blank=True)
    review = models.TextField(blank=True)
    image = models.FileField(upload_to='institute/students/', blank=True)
    image_url = models.URLField(blank=True)
    show_on_home = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('exam_type', 'display_order', 'student_name')

    def __str__(self):
        return f'{self.student_name} - {self.get_exam_type_display()}'