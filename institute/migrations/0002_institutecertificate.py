from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('institute', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstituteCertificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('certificate_id', models.CharField(max_length=60, unique=True)),
                ('student_name', models.CharField(max_length=160)),
                ('course_name', models.CharField(max_length=180)),
                ('completed_on', models.DateField(blank=True, null=True)),
                ('certificate_image_url', models.URLField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('certificate_id',),
            },
        ),
    ]