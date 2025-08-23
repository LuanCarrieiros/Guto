from django import forms
from django.core.exceptions import ValidationError
from .models import ItinerarioFormativo, UnidadeCurricular, EnturmacaoItinerario
from alunos.models import Aluno

class ItinerarioFormativoForm(forms.ModelForm):
    class Meta:
        model = ItinerarioFormativo
        fields = ['nome', 'carga_horaria_total', 'areas_conhecimento', 'habilidades', 'vagas_disponiveis']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Nome do Itinerário Formativo'
            }),
            'carga_horaria_total': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Ex: 80',
                'min': '1'
            }),
            'areas_conhecimento': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }),
            'habilidades': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'rows': 5,
                'placeholder': 'Descreva as habilidades e competências desenvolvidas neste itinerário...'
            }),
            'vagas_disponiveis': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Ex: 30',
                'min': '1',
                'value': '30'
            }),
        }

    def clean_carga_horaria_total(self):
        carga_horaria = self.cleaned_data.get('carga_horaria_total')
        if carga_horaria and carga_horaria <= 0:
            raise ValidationError('A carga horária deve ser maior que zero.')
        return carga_horaria

    def clean_vagas_disponiveis(self):
        vagas = self.cleaned_data.get('vagas_disponiveis')
        if vagas and vagas <= 0:
            raise ValidationError('O número de vagas deve ser maior que zero.')
        return vagas

class UnidadeCurricularForm(forms.ModelForm):
    class Meta:
        model = UnidadeCurricular
        fields = ['nome', 'carga_horaria', 'ementa', 'habilidades_especificas']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Nome da Unidade Curricular'
            }),
            'carga_horaria': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Ex: 40',
                'min': '1'
            }),
            'ementa': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'rows': 5,
                'placeholder': 'Descreva a ementa da unidade curricular...'
            }),
            'habilidades_especificas': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Descreva as habilidades específicas da unidade...'
            }),
        }

    def clean_carga_horaria(self):
        carga_horaria = self.cleaned_data.get('carga_horaria')
        if carga_horaria and carga_horaria <= 0:
            raise ValidationError('A carga horária deve ser maior que zero.')
        return carga_horaria

class EnturmacaoItinerarioForm(forms.ModelForm):
    aluno = forms.ModelChoiceField(
        queryset=Aluno.objects.filter(tipo_arquivo='CORRENTE').order_by('nome'),
        empty_label="Selecione um aluno...",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
        })
    )

    class Meta:
        model = EnturmacaoItinerario
        fields = ['aluno']

    def __init__(self, *args, **kwargs):
        itinerario = kwargs.pop('itinerario', None)
        super().__init__(*args, **kwargs)
        
        # Excluir alunos já enturmados neste itinerário
        if itinerario:
            alunos_enturmados = EnturmacaoItinerario.objects.filter(
                itinerario=itinerario
            ).values_list('aluno_id', flat=True)
            
            self.fields['aluno'].queryset = self.fields['aluno'].queryset.exclude(
                pk__in=alunos_enturmados
            )