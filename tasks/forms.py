# forms.py
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Task, Course, Explanation, Explain, UserTaskStatus, ComputerScienceTask, ComputerScienceTask, ComputerScienceTaskDetail

class RegisterForm(UserCreationForm):
    usable_password = None
    
    username = forms.CharField(
        max_length=100,
        label='Имя пользователя',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Пожалуйста, введите имя пользователя.',
            'unique': 'Имя пользователя уже занято.',
        }
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Пожалуйста, введите email.',
            'invalid': 'Введите корректный email адрес.',
        }
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Пожалуйста, введите пароль.',
        }
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Пожалуйста, подтвердите пароль.',
        }
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError(
                _("Пароли не совпадают."),
                code='password_mismatch',
            )

        if password1:
            if len(password1) < 8:
                raise ValidationError(
                    _("Пароль слишком короткий. Минимальная длина пароля - 8 символов."),
                    code='password_too_short',
                )
            if password1.isdigit():
                raise ValidationError(
                    _("Пароль не может состоять только из цифр."),
                    code='password_entirely_numeric',
                )
            username = self.cleaned_data.get("username")
            if username and password1.lower() == username.lower():
                raise ValidationError(
                    _("Пароль слишком похож на имя пользователя."),
                    code='password_too_similar',
                )
        
        return password2

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = _('Имя пользователя')
        self.fields['password'].label = _('Пароль')
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'style': 'width: 100%; margin-right: 80px;',
        })
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'style': 'width: 100%; margin-right: 80px;',
        })

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    _('Неправильное имя пользователя или пароль.'),
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

class ComputerScienceTaskForm(forms.ModelForm):
    class Meta:
        model = ComputerScienceTask
        fields = ['title']

class ComputerScienceTaskDetailForm(forms.ModelForm):
    class Meta:
        model = ComputerScienceTaskDetail
        fields = ['description', 'image', 'video']

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'grade']

class ExplanationTitleForm(forms.ModelForm):
    class Meta:
        model = Explain
        fields = ['title']

class ExplainForm(forms.ModelForm):
    description = forms.CharField(required=False)
    image = forms.ImageField(required=False)
    video = forms.FileField(required=False)

    class Meta:
        model = Explanation
        fields = ['description', 'image', 'video']

class TaskForm(forms.ModelForm):
    description = forms.CharField(required=False)
    correct_answer = forms.CharField(required=False)
    image = forms.ImageField(required=False)
    video = forms.FileField(required=False)
    is_theory = forms.BooleanField(required=False, label="Это теоретическое задание") 
    
    expl = forms.CharField(required=False)
    expl_img = forms.ImageField(required=False)
    expl_video = forms.FileField(required=False)
    
    file = forms.FileField(required=False)
    file_link_text = forms.CharField(required=False)

    class Meta:
        model = Task
        fields = ['description', 'correct_answer', 'image', 'video', 'is_theory', 'expl', 'expl_img', 'expl_video','file','file_link_text'] 

class AnswerForm(forms.ModelForm):
    class Meta:
        model = UserTaskStatus
        fields = ['answer']