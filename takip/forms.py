from django import forms
from django.contrib.auth.forms import AuthenticationForm
from takip.models import Student

class OgrenciGirisForm(forms.Form):
    sinif = forms.ChoiceField(label='Sınıf', choices=[])
    numara = forms.CharField(label='Numara', max_length=10)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        siniflar = Student.objects.values_list('classroom', flat=True).distinct().order_by('classroom')
        self.fields['sinif'].choices = [(sinif, sinif) for sinif in siniflar]

class OgretmenGirisForm(AuthenticationForm):
    """Standart Django giriş formu, sadece görünüm için"""
    pass