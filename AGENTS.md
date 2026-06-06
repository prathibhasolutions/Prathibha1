# AI Agent Instructions for Prathibha Project

## Purpose
This file helps AI coding agents like GitHub Copilot understand the repository structure, conventions, and how to work safely in this Django website project.

## Project overview
- Django website with five main apps: `core`, `services`, `technologies`, `institute`, and `solutions`.
- Uses SQLite locally (`db.sqlite3`), WhiteNoise for static file serving, and TinyMCE in the admin.
- Includes admin-editable content models, contact form handling, search, and seeded branch/content data.

## How to run locally
1. Create and activate a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Run `python manage.py migrate`.
4. Run `python manage.py seed_branches` and `python manage.py seed_content`.
5. Start the server with `python manage.py runserver`.
6. Use `/admin/` to manage content.

## Key files and architecture
- `manage.py` — Django command entry point.
- `config/settings.py` — project settings, including database, static files, and email config.
- `config/urls.py` — root URL routes.
- `template/` — main template directory used by all apps.
- `static/` — project static assets.
- `core/views_search.py` — search endpoint used at `/search/`.
- `accounts/` — contains auth-related app (if present in future work).
- `services/`, `technologies/`, `institute/`, `solutions/` — app-specific models, views, URLs, and templates.

## Conventions
- Keep content and layout changes within app templates under `template/<app>/`.
- App URL namespaces are flat and mapped in `config/urls.py`:
  - `/` → `core`
  - `/services/` → `services`
  - `/technologies/` → `technologies`
  - `/institute/` → `institute`
  - `/solutions/` → `solutions`
- Use the admin for content data changes rather than hardcoding content where possible.
- The project uses Django 6.x syntax and settings.

## Environment and deployment notes
- `.env.example` defines environment variables: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, email settings.
- In production, set `DJANGO_DEBUG=False`, configure `ALLOWED_HOSTS`, and use Gunicorn.
- Static files are collected to `staticfiles` using WhiteNoise.

## What to avoid
- Do not modify the virtual environment directories (`.venv` or `venv`) or `db.sqlite3` unless explicitly working on schema/data.
- Avoid adding unrelated third-party apps without checking the existing app structure first.
- Do not assume there are automated tests; add tests if implementing new behavior.

## Suggested next agent customizations
- Create a dedicated skill for Django app scaffolding and template updates.
- Add a hook for ensuring content model changes are reflected in the admin and front-end templates.
