
from django.db import models
from django.contrib.auth.models import User
class UserProfile(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    mobile_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # store hashed password if possible

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
from django.contrib.auth import get_user_model

User = get_user_model()

class Complaint(models.Model):
    CATEGORY_CHOICES = [
        ("Road & Infrastructure", "Road & Infrastructure"),
        ("Water & Sanitation", "Water & Sanitation"),
        ("Power & Electricity", "Power & Electricity"),
        ("Public Health", "Public Health"),
        ("Law & Order", "Law & Order"),
        ("Other", "Other"),
    ]
    STATUS_CHOICES = [("Active", "Active"), ("Resolved", "Resolved")]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=64, choices=CATEGORY_CHOICES)
    description = models.TextField()
    attachment = models.FileField(upload_to="attachments/", blank=True, null=True)
    notify_email = models.EmailField(blank=True)
    notify_phone = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="Active")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.status})"

class StaffNote(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="staff_notes")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        who = self.author.get_username() if self.author else "staff"
        return f"Note by {who} on #{self.complaint_id}"
