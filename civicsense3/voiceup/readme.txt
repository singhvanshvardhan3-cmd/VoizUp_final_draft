Title
VoizUp

Overview
A full‑stack Django web application for submitting, tracking, and resolving citizen complaints with role‑based tools for staff triage. Citizens can attach files and opt in for updates via email and/or SMS. Staff users can filter, assign, and update complaint status, add internal notes, and optionally notify citizens on changes.

Features

Citizen portal:

Submit complaints with title, category, description, and optional attachment.

Optional notifications via email and/or SMS on submission and updates.

Client-side and server-side validation for a smooth, safe experience.

Tracking:

Recent complaints table with ID, category, status, and timestamps.

Dashboard stats: total, active, resolved.

Staff panel:

Staff-only dashboard for filtering/searching and paginated list.

Bulk actions: assign to self, set Active/Resolved.

Detail view: update status, assignee, staff notes; optional notify by email/SMS.

Attachments:

File uploads stored in MEDIA_ROOT and served in development.

Notifications:

Email via SMTP (Gmail-compatible, App Password recommended).

SMS via Twilio (optional; supports trial and production accounts).

Tech Stack

Backend: Django (views, forms, models, auth, messages, templates)

Database: SQLite (dev default; easily switchable)

Frontend: Bootstrap 5 (CDN), custom CSS/JS for tabs, validation, tables

Email: Django send_mail with SMTP (Gmail App Password or another SMTP provider)

SMS: Twilio Python client (optional)

Storage: Django FileField to MEDIA_ROOT/attachments/

Project Structure

complaint_portal/

manage.py

complaint_portal/

settings.py, urls.py, wsgi.py, asgi.py, init.py

complaints/

models.py, forms.py, views.py, views_staff.py, services.py, urls.py, admin.py, init.py

templates/complaints/

portal.html, staff_list.html, staff_detail.html

migrations/

init.py

Quick Start

Setup

Python 3.10+ recommended

Create and activate a virtual environment

Install dependencies:

pip install django twilio

Database

python manage.py makemigrations

python manage.py migrate

Superuser (for admin/staff)

python manage.py createsuperuser

Login to /admin/ and set the is_staff flag for staff users

Development server

python manage.py runserver

Visit http://127.0.0.1:8000/

Email Configuration
Use SMTP for real emails. For Gmail, enable 2‑Step Verification and use a 16‑character App Password (not the normal password).

Example (development) settings in settings.py:

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "smtp.gmail.com"

EMAIL_PORT = 587

EMAIL_USE_TLS = True

EMAIL_HOST_USER = "your_account@gmail.com"

EMAIL_HOST_PASSWORD = "your_16_char_app_password"

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

Recommended: move secrets to environment variables in production and read them in settings.py via os.environ.get(...).

SMS Configuration (Optional)

Create a Twilio account and get:

TWILIO_ACCOUNT_SID

TWILIO_AUTH_TOKEN

TWILIO_FROM_NUMBER

In a trial account, Twilio can send only to verified recipient numbers. Upgrade or verify numbers to test unrestricted sends.

Add values as environment variables and ensure services.py can read them.

Routes

/ Portal (submit form, stats, tracking)

/test-email/ Diagnostic endpoint to test SMTP delivery

/staff/ Staff list (requires is_staff)

/staff/bulk/ Staff bulk actions (POST; requires is_staff)

/staff/<id>/ Staff detail/update page (requires is_staff)

/admin/ Django admin

Usage Flow

Citizen

Select a category, write a clear title and description (≥ 10 chars), optionally attach a file.

Add an email and/or phone to receive updates.

Submit; a confirmation email/SMS is sent if configured.

Staff

Go to /staff/ (login required; user must be is_staff).

Filter/search, select multiple complaints, use bulk actions.

Open a complaint to update status, assign to self/others, add staff notes, and optionally notify the citizen.

Development Tips

Restart the server after changing environment variables; settings are read at process start.

Test SMTP with /test-email/ to surface configuration issues (uses fail_silently=False).

Check spam/junk if messages appear to be missing.

For non-Gmail SMTP, adapt host/port/TLS and credentials per provider docs.

For production, consider:

Transactional email providers (SendGrid/Mailgun/SES) for deliverability and analytics.

Background jobs (Celery/RQ) for sending notifications asynchronously.

Proper static/media serving via a web server or object storage (S3, GCS).

Postgres/MySQL instead of SQLite.

Security Notes

CSRF protection enabled on forms.

Staff routes are restricted to authenticated users with is_staff.

Do not commit plaintext secrets; use environment variables or a secrets manager.

Validate and limit uploaded file types and sizes in production if needed.

Common Issues and Fixes

No email delivered:

Ensure SMTP credentials are correct and restart the server.

For Gmail, use an App Password and set DEFAULT_FROM_EMAIL to the same Gmail address.

Check spam/junk and provider security policies.

Twilio SMS not received:

On trial accounts, verify destination numbers or upgrade.

Confirm country support and formatting (+CCXXXXXXXXXX).

File upload errors:

Ensure the form uses enctype="multipart/form-data".

MEDIA_ROOT is writable, and MEDIA_URL is configured.

Permission denied on staff pages:

Ensure user is authenticated and has is_staff set to True.

License
Add your preferred license here (e.g., MIT, Apache-2.0), and include a LICENSE file in the project root.

Credits

Built with Django and Bootstrap.

Email via SMTP (Gmail-compatible or any SMTP provider).

Optional SMS notifications via Twilio.