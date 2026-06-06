from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='InstituteCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section_key', models.SlugField(help_text='Example: programming-languages', max_length=120)),
                ('section_title', models.CharField(blank=True, max_length=180)),
                ('section_description', models.TextField(blank=True)),
                ('slug', models.SlugField(help_text='Use an existing slug to open detailed course page.', max_length=180, unique=True)),
                ('title', models.CharField(max_length=180)),
                ('summary', models.TextField()),
                ('icon_sprite', models.CharField(default='institute', max_length=80)),
                ('display_order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('display_order', 'id'),
            },
        ),
    ]