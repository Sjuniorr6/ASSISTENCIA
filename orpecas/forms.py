from django import forms
from .models import Orpecas

class OrpecasForm(forms.ModelForm):
    class Meta:
        model = Orpecas
        exclude = ['valor_total', 'valor_total_com_desconto'] 