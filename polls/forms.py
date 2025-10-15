from django import forms
from polls.models import User, Question, Choice
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.forms import inlineformset_factory


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Email:", max_length=50)
    avatar = forms.ImageField(label="Фото:")

    class Meta:
        model = User
        fields = ('username', 'email', 'avatar', 'password1', 'password2')


class ProfileUpdateForm(UserChangeForm):

    password = None

    class Meta:
        model = User
        fields = ('username', 'email', 'avatar')
        labels = {
            'username': 'Имя',
            'email': 'Email',
            'avatar': 'Аватар',
        }
        widgets = {
            'avatar': forms.FileInput(),
        }


class PollForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('question_text', 'question_description', 'picture')
        widgets = {
            'picture': forms.FileInput(),
        }


ChoiceForm = inlineformset_factory(
    Question,
    Choice,
    fields=['choice_text'],
    extra=5,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
