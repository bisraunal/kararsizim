from django import forms
from .models import Poll, Option

class PollCreateForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['question', 'description', 'category']
        widgets = {
            'question': forms.TextInput(attrs={
                'placeholder': 'Neyin arasında kararsız kaldın? (Örn: Hangi kulaklığı almalıyım?)',
                'class': 'form-input form-input-lg',
                'maxlength': '250',
                'required': True,
                'autocomplete': 'off',
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Kararınla ilgili detaylar, bütçe, kullanım amacı vb. (İsteğe bağlı)',
                'class': 'form-textarea',
                'rows': 3,
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
