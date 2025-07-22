from django import forms
from .models import AgendaDia, Visita

class AgendaDiaForm(forms.ModelForm):
    class Meta:
        model = AgendaDia
        fields = ['data', 'dia_semana']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'dia_semana': forms.TextInput(attrs={'class': 'form-input'}),
        }

class VisitaForm(forms.ModelForm):
    class Meta:
        model = Visita
        fields = ['horario', 'servico', 'cliente', 'profissional', 'observacoes']
        widgets = {
            'horario': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'servico': forms.TextInput(attrs={'class': 'form-input'}),
            'cliente': forms.TextInput(attrs={'class': 'form-input'}),
            'profissional': forms.TextInput(attrs={'class': 'form-input'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
        } 