from django import forms
from django.core.exceptions import ValidationError

from .models import Post

from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group

class PostForm(forms.ModelForm):
    # description = forms.CharField(min_length=20)
    class Meta:
       model = Post
       fields = [
           'author',
           'type',
           'header',
           'category',
           'content',
       ]

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get("content")
        header = cleaned_data.get("header")

        if header == content:
            raise ValidationError(
                "Описание не может быть индентично названию."
            )

        return cleaned_data

