from .models import Profile
from django.contrib.auth.forms import UserCreationForm

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class CustomUserCreationForm(forms.Form):

    GRADES = [(str(x), x) for x in range(1, 12)]

    email = forms.EmailField()

    password1 = forms.CharField(widget=forms.PasswordInput, label="Введите пароль")

    password2 = forms.CharField(widget=forms.PasswordInput, label="Подтвердите пароль")

    sex = forms.ChoiceField(widget=forms.RadioSelect, choices=Profile.SEX, label="Укажите пол")

    grade = forms.ChoiceField(widget=forms.Select, choices=GRADES, label="Укажите класс")

    class Meta:
        model = User
        fields = ("email", "password1", "password2", "sex")

    def clean_email(self):
        # Get the email
        email = self.cleaned_data.get('email')

        # Check to see if any users already exist with this email as a username.
        try:
            match = User.objects.get(email=email)
        except:
            # Unable to find a user, this is fine
            return email

        # A user was found with this as a username, raise an error.
        raise forms.ValidationError('Этот email уже зарегистрирован')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2


    def save(self, commit=True):
        #user = super(CustomUserCreationForm, self).save(commit=False)
        email = self.cleaned_data['email']
        sex = self.cleaned_data["sex"]
        grade = self.cleaned_data["grade"]
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']


class UpdateUserProfile(forms.Form):

    current_password_flag = True

    GRADES = [(str(x), x) for x in range(1, 12)]

    sex = forms.ChoiceField(widget=forms.RadioSelect, choices=Profile.SEX, label="Укажите пол")

    grade = forms.ChoiceField(widget=forms.Select, choices=GRADES, label="Укажите класс")

    current_password = forms.CharField(widget=forms.PasswordInput, label="Введите текущий пароль", required=False)

    new_password = forms.CharField(widget=forms.PasswordInput, label="Введите новый пароль", required=False)

    confirm_new_password = forms.CharField(widget=forms.PasswordInput, label="Подтвердите новый пароль", required=False)

    class Meta:
        model = User
        fields = ("sex", "grade", "current_password", "new_password", "confirm_new_password")


    def set_current_password_flag(self):
        self.current_password_flag = False

    def clean_current_password(self):
        current_password = self.cleaned_data["current_password"]

        if self.current_password_flag == False:
            raise forms.ValidationError("Указан неправильный текущий пароль")

        return current_password

    def clean_confirm_new_password(self):
        new_password = self.cleaned_data["new_password"]
        confirm_new_password = self.cleaned_data["confirm_new_password"]

        if new_password and confirm_new_password and new_password != confirm_new_password:
            raise forms.ValidationError('Новый пароль не совпадает')

        return new_password


    def save(self):
        sex = self.cleaned_data['sex']
        grade = self.cleaned_data['grade']
        current_password = self.cleaned_data['current_password']
        new_password = self.cleaned_data["new_password"]
        confirm_new_password = self.cleaned_data["confirm_new_password"]


