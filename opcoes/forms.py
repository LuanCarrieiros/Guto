from django import forms
from datetime import date
from .models import FiltroRelatorio, CalendarioEscolar, EventoCalendario

class FiltroRelatorioForm(forms.ModelForm):
    """Form para filtros de relatórios (RF607)"""
    class Meta:
        model = FiltroRelatorio
        fields = [
            'periodo_letivo', 'tipo_ensino', 'ano_serie', 'turno', 
            'status_diario', 'situacao_turma'
        ]
        widgets = {
            'periodo_letivo': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': str(date.today().year),
                'min': '2020',
                'max': str(date.today().year + 10)
            }),
            'tipo_ensino': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'ano_serie': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Ex: 1º Ano, 5ª Série, Módulo I'
            }),
            'turno': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'status_diario': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'situacao_turma': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            })
        }

class CalendarioEscolarForm(forms.ModelForm):
    """Form para calendário escolar"""
    class Meta:
        model = CalendarioEscolar
        fields = [
            'periodo_letivo', 'tipo_ensino', 'serie', 'turno', 
            'data_inicio_letivo', 'data_fim_letivo', 'dias_letivos', 
            'dias_escolares', 'observacoes'
        ]
        widgets = {
            'periodo_letivo': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'min': '2020',
                'max': str(date.today().year + 10)
            }),
            'tipo_ensino': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'serie': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'turno': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'data_inicio_letivo': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
                }
            ),
            'data_fim_letivo': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
                }
            ),
            'dias_letivos': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'min': '100',
                'max': '250'
            }),
            'dias_escolares': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'min': '100',
                'max': '250'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Observações sobre o calendário escolar'
            })
        }

class EventoCalendarioForm(forms.ModelForm):
    """Form para eventos do calendário"""
    class Meta:
        model = EventoCalendario
        fields = [
            'data_evento', 'tipo_evento', 'nome_evento', 'descricao', 'dia_letivo'
        ]
        widgets = {
            'data_evento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
                }
            ),
            'tipo_evento': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'nome_evento': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'Nome do evento'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Descrição do evento'
            }),
            'dia_letivo': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            })
        }