from django import forms
from .models import Rat

class RatForm(forms.ModelForm):
    class Meta:
        model = Rat
        fields = '__all__'
        # Se quiser garantir ordem ou campos explícitos, pode listar todos os campos manualmente 