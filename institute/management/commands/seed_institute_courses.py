from django.core.management.base import BaseCommand

from institute.models import InstituteCourse
from institute.views import COURSE_CATALOG, COURSE_SECTION_ORDER


class Command(BaseCommand):
    help = 'Seed institute courses from the in-code catalog into admin-managed InstituteCourse table.'

    def handle(self, *args, **options):
        section_lookup = {item['key']: item for item in COURSE_SECTION_ORDER}
        created = 0
        updated = 0

        for index, course in enumerate(COURSE_CATALOG, start=1):
            section_key = course.get('category', 'general')
            section = section_lookup.get(section_key, {})

            defaults = {
                'section_key': section_key,
                'section_title': section.get('title', ''),
                'section_description': section.get('description', ''),
                'title': course.get('title', ''),
                'summary': course.get('summary', ''),
                'icon_sprite': course.get('icon_sprite', 'institute'),
                'display_order': index,
                'is_active': True,
            }

            _, is_created = InstituteCourse.objects.update_or_create(
                slug=course.get('slug', ''),
                defaults=defaults,
            )
            if is_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f'Seed complete. Created: {created}, Updated: {updated}'))
