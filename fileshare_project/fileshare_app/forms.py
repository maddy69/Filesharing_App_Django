from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from .models import UploadedFile

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    user_type = forms.ChoiceField(choices=UserProfile.USER_TYPE_CHOICES)

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']