from django import forms
from django.contrib.auth.models import User
from .models import Post, Comments


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class PostCreateForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = (
            'title', 'text', 'pub_date',
            'location', 'category', 'image',
            'is_published')
        widgets = {'pub_date': forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'datetime-input'})}


class CommentsForm(forms.ModelForm):

    class Meta:
        model = Comments
        fields = ('text',)
