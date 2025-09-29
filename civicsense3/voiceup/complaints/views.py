from django.shortcuts import render, redirect
from .forms import UserProfileForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm
from django.contrib.auth.hashers import check_password
from .models import UserProfile
from django.urls import reverse_lazy

def signup_view(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST)
        if form.is_valid():
            # save without confirm_password
            user = form.save(commit=False)
            # ⚠️ Hash password instead of storing plain text
            from django.contrib.auth.hashers import make_password
            user.password = make_password(form.cleaned_data["password"])
            user.save()
            return redirect("complaints:login")
    else:
        form = UserProfileForm()

    return render(request, "complaints/signup.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = UserProfile.objects.get(email=email)
                # If password stored as plain text (not recommended):
                # if user.password == password:
                # If password hashed:
                if check_password(password, user.password):
                    request.session['user_id'] = user.id  # create session
                    messages.success(request, f"Welcome, {user.first_name}!")
                    return redirect("complaints:portal")  # change to your home/dashboard page
                else:
                    messages.error(request, "Invalid password")
            except UserProfile.DoesNotExist:
                messages.error(request, "User does not exist")
    else:
        form = LoginForm()

    return render(request, "complaints/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")
# complaints/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q

from .forms import ComplaintForm, StaffUpdateForm, StaffNoteForm
from .models import Complaint, StaffNote
from .services import send_email_notification, send_sms_notification

def _stats():
    return {
        "total": Complaint.objects.count(),
        "active": Complaint.objects.filter(status="Active").count(),
        "resolved": Complaint.objects.filter(status="Resolved").count(),
    }

@require_http_methods(["GET", "POST"])
def portal_view(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user if request.user.is_authenticated else None
            obj.save()

            subject = f"Complaint submitted: {obj.title}"
            body = (
                f"Thank you for your submission. your complaint has been registered and you will get a mail when your problem is being looked at and is solved\n"
                f"Title: {obj.title}\n"
                f"Category: {obj.category}\n"
                f"Description:{obj.description}\n"
                f"Status: {obj.status}\n"
                f"ID: {obj.id}\n"
            )
            email_ok = send_email_notification(obj.notify_email, subject, body) if obj.notify_email else False
            sms_ok = send_sms_notification(obj.notify_phone, f"{subject}\nStatus: {obj.status}, ID: {obj.id}") if obj.notify_phone else False

            if email_ok or sms_ok:
                messages.success(request, "Complaint submitted. Notification sent.")
            else:
                messages.success(request, "Complaint submitted.")
            return redirect("complaints:portal")
    else:
        form = ComplaintForm()

    if request.user.is_authenticated:
        track_list = Complaint.objects.filter(created_by=request.user).order_by("-created_at")[:10]
    else:
        track_list = Complaint.objects.order_by("-created_at")[:10]

    return render(request, "complaints/portal.html", {
        "form": form,
        "stats": _stats(),
        "track_list": track_list,
    })

# ---------- STAFF PANEL VIEWS ----------

def _staff_required(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(_staff_required)
def staff_list_view(request):
    """
    List complaints with filters: status, category, search query (title/description/id).
    """
    qs = Complaint.objects.all().order_by("-created_at")

    status = request.GET.get("status", "").strip()
    category = request.GET.get("category", "").strip()
    q = request.GET.get("q", "").strip()

    if status in ("Active", "Resolved"):
        qs = qs.filter(status=status)
    if category:
        qs = qs.filter(category=category)
    if q:
        q_int = None
        try:
            q_int = int(q)
        except Exception:
            pass
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            (Q(id=q_int) if q_int else Q(pk__isnull=True))
        )

    context = {
        "objects": qs[:200],
        "status": status,
        "category": category,
        "q": q,
        "stats": _stats(),
        "categories": [c[0] for c in Complaint.CATEGORY_CHOICES],
    }
    return render(request, "complaints/staff_list.html", context)

@login_required
@user_passes_test(_staff_required)
def staff_detail_view(request, pk: int):
    """
    Show a single complaint with metadata, notes, and quick status control.
    """
    obj = get_object_or_404(Complaint, pk=pk)
    notes = obj.staff_notes.all()
    form = StaffUpdateForm(initial={"status": obj.status})
    note_form = StaffNoteForm()
    return render(request, "complaints/staff_detail.html", {
        "obj": obj,
        "notes": notes,
        "form": form,
        "note_form": note_form,
    })

@login_required
@user_passes_test(_staff_required)
@require_http_methods(["POST"])
def staff_update_view(request, pk: int):
    """
    Handle status change and optional note creation. If send_notification checked,
    email/SMS are sent to the complainant if contact is provided.
    """
    obj = get_object_or_404(Complaint, pk=pk)
    form = StaffUpdateForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Invalid input.")
        return redirect("complaints:staff_detail", pk=obj.pk)

    new_status = form.cleaned_data["status"]
    note_text = form.cleaned_data["note"]
    send_notif = form.cleaned_data["send_notification"]

    changed = False
    if new_status and new_status != obj.status:
        obj.status = new_status
        obj.save(update_fields=["status"])
        changed = True

    if note_text:
        StaffNote.objects.create(
            complaint=obj,
            author=request.user if request.user.is_authenticated else None,
            note=note_text,
        )
        changed = True

    notif_sent = False
    if send_notif:
        subject = f"Complaint update: {obj.title} (ID #{obj.id})"
        body_lines = [
            f"Your complaint status has been updated.",
            f"Title: {obj.title}",
            f"Category: {obj.category}",
            f"New Status: {obj.status}",
            f"ID: {obj.id}",
        ]
        if note_text:
            body_lines.append(f"Staff note: {note_text}")
        body = "\n".join(body_lines)

        email_ok = send_email_notification(obj.notify_email, subject, body) if obj.notify_email else False
        sms_ok = send_sms_notification(obj.notify_phone, f"{subject}\nStatus: {obj.status}, ID: {obj.id}") if obj.notify_phone else False
        notif_sent = bool(email_ok or sms_ok)

    if changed and notif_sent:
        messages.success(request, "Updated. Notification sent to complainant.")
    elif changed:
        messages.success(request, "Updated.")
    else:
        messages.info(request, "No changes detected.")

    return redirect("complaints:staff_detail", pk=obj.pk)

