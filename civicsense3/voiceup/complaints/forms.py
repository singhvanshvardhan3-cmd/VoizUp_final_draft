from django import forms
from .models import UserProfile
from django.core.exceptions import ValidationError


class UserProfileForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input-field", "placeholder": "Confirm Password"}),
        label=""
    )

    class Meta:
        model = UserProfile
        fields = ["first_name", "last_name", "mobile_number", "email", "password"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "input-field", "placeholder": "First Name"}),
            "last_name": forms.TextInput(attrs={"class": "input-field", "placeholder": "Last Name"}),
            "mobile_number": forms.TextInput(attrs={"class": "input-field", "placeholder": "Mobile Number"}),
            "email": forms.EmailInput(attrs={"class": "input-field", "placeholder": "Email ID"}),
            "password": forms.PasswordInput(attrs={"class": "input-field", "placeholder": "Password"}),
        }
        def clean(self):
            cleaned_data = super().clean()
            password = cleaned_data.get("password")
            confirm_password = cleaned_data.get("confirm_password")

            if password != confirm_password:
                raise ValidationError("Passwords do not match")

            return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'}))
from .models import Complaint, StaffNote

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["title", "category", "description", "attachment", "notify_email", "notify_phone"]
        widgets = {
            "title": forms.TextInput(attrs={"class":"input", "id":"title", "placeholder":"Brief title", "aria-describedby":"titleHelp"}),
            "category": forms.Select(attrs={"class":"select", "id":"category", "aria-label":"Complaint category"}),
            "description": forms.Textarea(attrs={"class":"textarea", "id":"desc", "placeholder":"Describe the issue with location, time, and details", "aria-describedby":"descHelp"}),
            "notify_email": forms.EmailInput(attrs={"class":"input", "id":"email", "placeholder":"you@example.com", "aria-describedby":"emailHelp"}),
            "notify_phone": forms.TextInput(attrs={"class":"input", "id":"phone", "placeholder":"+1 555 000 1111", "aria-describedby":"phoneHelp"}),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError("Please enter a title.")
        return title

    def clean_description(self):
        desc = self.cleaned_data.get("description", "").strip()
        if len(desc) < 10:
            raise forms.ValidationError("Please provide at least 10 characters.")
        return desc

class StaffUpdateForm(forms.Form):
    status = forms.ChoiceField(choices=Complaint.STATUS_CHOICES, widget=forms.Select(attrs={"class":"select"}))
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class":"textarea", "rows":4, "placeholder":"Add an internal note (optional)"}),
    )
    send_notification = forms.BooleanField(required=False, initial=False)

    def clean_note(self):
        note = self.cleaned_data.get("note", "")
        return note.strip()

class StaffNoteForm(forms.ModelForm):
    class Meta:
        model = StaffNote
        fields = ["note"]
        widgets = {
            "note": forms.Textarea(attrs={"class":"textarea", "rows":3, "placeholder":"Add an internal note"}),
        }
