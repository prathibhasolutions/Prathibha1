from django.db import migrations


def seed_exam_structure(apps, schema_editor):
    Exam = apps.get_model('institute', 'Exam')
    ExamSection = apps.get_model('institute', 'ExamSection')
    ExamMock = apps.get_model('institute', 'ExamMock')

    structure = [
        {
            'title': 'EAPCET 2026 Test Series',
            'description': 'A crucial entrance exam for engineering and medical streams.',
            'display_order': 1,
            'sections': [
                'Full Test',
                'Mathematics',
                'Physics',
                'Chemistry',
            ],
        },
        {
            'title': 'JEE Mains',
            'description': "One of India's most important engineering entrance exams.",
            'display_order': 2,
            'sections': [
                'Full Test',
                'Mathematics',
                'Physics',
                'Chemistry',
            ],
        },
        {
            'title': 'Programming Challenges',
            'description': 'Test your coding skills with competitive programming contests.',
            'display_order': 3,
            'sections': [
                'C Language',
                'Python',
                'Java',
                'HTML CSS JavaScript',
            ],
        },
        {
            'title': 'Aptitude Tests',
            'description': 'Prepare for top recruitment exams with challenging aptitude tests.',
            'display_order': 4,
            'sections': [
                'General Test',
                'Quantitative Aptitude',
                'Logical Reasoning',
                'Verbal Ability',
            ],
        },
    ]

    for exam_data in structure:
        exam, _ = Exam.objects.get_or_create(
            title=exam_data['title'],
            defaults={
                'description': exam_data['description'],
                'display_order': exam_data['display_order'],
                'is_active': True,
            },
        )

        if not exam.description:
            exam.description = exam_data['description']
            exam.display_order = exam_data['display_order']
            exam.is_active = True
            exam.save(update_fields=['description', 'display_order', 'is_active'])

        for index, section_title in enumerate(exam_data['sections'], start=1):
            section, _ = ExamSection.objects.get_or_create(
                exam=exam,
                title=section_title,
                defaults={
                    'description': f'{section_title} tests for {exam.title}.',
                    'display_order': index,
                    'is_active': True,
                },
            )

            for mock_number in range(1, 4):
                ExamMock.objects.get_or_create(
                    section=section,
                    title=f'Mock {mock_number}',
                    defaults={
                        'description': f'Mock {mock_number} for {section.title}. Admin can add a live test link later.',
                        'duration_minutes': 30,
                        'question_count': 25,
                        'display_order': mock_number,
                        'is_active': True,
                    },
                )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('institute', '0004_institutecourse_notes_url_institutecourse_overview_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_exam_structure, noop_reverse),
    ]