from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'E-posta adresiniz (gizli tutulur)',
            'class': 'form-input',
            'autocomplete': 'email'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Kullanıcı adı (ör. kararsiz_biri)',
                'class': 'form-input',
                'autocomplete': 'username'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = "Sadece harf, rakam ve @/./+/-/_ karakterleri."
        for field_name, field in self.fields.items():
            if field_name not in ['username', 'email']:
                field.widget.attrs.update({'class': 'form-input'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Bu e-posta adresi ile zaten bir hesap kayıtlı.")
        return email


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Kullanıcı adınız',
            'class': 'form-input',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Parolanız',
            'class': 'form-input',
            'autocomplete': 'current-password'
        })
    )
