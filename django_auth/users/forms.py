from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm


class SignupForm(UserCreationForm):
    # email = forms.EmailField(max_length=200, help_text='Required')
    email=forms.RegexField(regex=r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$",
                                   required = True)
    class Meta(object):
        model = User  # Shows that the User fields contain the model class
        fields = ('id', 'email', 'first_name', 'last_name', 'date_joined')

        def __init__(self):
            self.cleaned_data = None

        def save(self, commit=True):
            user=super(SignupForm, self).save(commit=False)
            user.email=self.cleaned_data['email']
            if commit:
                user.save()
            return user






