from django import forms
from .models import UserResume

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = UserResume
        fields = ['resume_file']
        widgets = {
            'resume_file': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }
