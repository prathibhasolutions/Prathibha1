from django.db import migrations


def create_technician_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Technician')


def remove_technician_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Technician').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_servicebooking_accepted_at_and_more'),
    ]

    operations = [
        migrations.RunPython(create_technician_group, remove_technician_group),
    ]
