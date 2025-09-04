from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Turma, Disciplina, DivisaoPeriodoLetivo, LancamentoNota, 
    Conceito, AtestadoMedico, RecuperacaoEspecial, AulaRegistrada,
    RegistroFrequencia, TipoAvaliacao, Avaliacao, NotaAvaliacao
)
from alunos.models import Aluno
from funcionarios.models import Funcionario


class TurmaForm(forms.ModelForm):
    """Formulário para criação e edição de turmas"""
    
    class Meta:
        model = Turma
        fields = ['nome', 'periodo_letivo', 'tipo_ensino', 'ano_serie', 'turno']
        
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Ex: 1º Ano A'
            }),
            'periodo_letivo': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': '2024'
            }),
            'tipo_ensino': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'ano_serie': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'turno': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Choices para tipo de ensino (atualizados sem EJA e TÉCNICO)
        self.fields['tipo_ensino'].choices = [
            ('', 'Selecione o tipo de ensino'),
            ('EDUCACAO_INFANTIL', 'Educação Infantil'),
            ('ENSINO_FUNDAMENTAL_I', 'Ensino Fundamental I'),
            ('ENSINO_FUNDAMENTAL_II', 'Ensino Fundamental II'),
            ('ENSINO_MEDIO', 'Ensino Médio'),
        ]
        
        # Choices para ano/série (atualizados com novas opções)
        self.fields['ano_serie'].choices = [
            ('', 'Selecione o ano/série'),
            # Educação Infantil
            ('BERÇARIO', 'Berçário'),
            ('MATERNAL_I', 'Maternal I'),
            ('MATERNAL_II', 'Maternal II'),
            ('PRE_I', 'Pré I'),
            ('PRE_II', 'Pré II'),
            # Ensino Fundamental I
            ('1_ANO', '1º Ano'),
            ('2_ANO', '2º Ano'),
            ('3_ANO', '3º Ano'),
            ('4_ANO', '4º Ano'),
            ('5_ANO', '5º Ano'),
            # Ensino Fundamental II
            ('6_ANO', '6º Ano'),
            ('7_ANO', '7º Ano'),
            ('8_ANO', '8º Ano'),
            ('9_ANO', '9º Ano'),
            # Ensino Médio
            ('1_ANO_EM', '1º Ano'),
            ('2_ANO_EM', '2º Ano'),
            ('3_ANO_EM', '3º Ano'),
        ]
        
        # Choices para turno
        self.fields['turno'].choices = [
            ('', 'Selecione o turno'),
            ('MATUTINO', 'Matutino'),
            ('VESPERTINO', 'Vespertino'),
            ('NOTURNO', 'Noturno'),
            ('INTEGRAL', 'Integral'),
        ]


class DisciplinaForm(forms.ModelForm):
    """Formulário para criação e edição de disciplinas"""
    
    class Meta:
        model = Disciplina
        fields = ['nome', 'codigo', 'avalia_por_conceito', 'carga_horaria']
        
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500',
                'placeholder': 'Ex: Matemática'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500',
                'placeholder': 'Ex: MAT001'
            }),
            'avalia_por_conceito': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-purple-600 bg-gray-100 border-gray-300 rounded focus:ring-purple-500'
            }),
            'carga_horaria': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500',
                'placeholder': '40'
            }),
        }


class DivisaoPeriodoLetivoForm(forms.ModelForm):
    """Formulário para criação e edição de divisões do período letivo"""
    
    class Meta:
        model = DivisaoPeriodoLetivo
        fields = ['nome', 'tipo_divisao', 'periodo_letivo', 'ordem', 'data_inicio', 'data_fim']
        
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Ex: 1º Bimestre'
            }),
            'tipo_divisao': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'periodo_letivo': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': '2024'
            }),
            'ordem': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': '1'
            }),
            'data_inicio': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'type': 'date'
            }),
            'data_fim': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'type': 'date'
            }),
        }


class EnturmacaoForm(forms.Form):
    """Formulário para enturmação de alunos"""
    
    turma = forms.ModelChoiceField(
        queryset=Turma.objects.all(),
        empty_label="Selecione uma turma",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
        })
    )
    
    alunos = forms.ModelMultipleChoiceField(
        queryset=Aluno.objects.filter(tipo_arquivo='CORRENTE'),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-checkbox text-green-600'
        }),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        turma_id = kwargs.pop('turma_id', None)
        super().__init__(*args, **kwargs)
        
        if turma_id:
            # Se uma turma específica foi selecionada, filtrar alunos disponíveis
            from .models import Enturmacao
            alunos_ja_enturmados = Enturmacao.objects.filter(
                turma_id=turma_id
            ).values_list('aluno_id', flat=True)
            
            self.fields['alunos'].queryset = Aluno.objects.filter(
                tipo_arquivo='CORRENTE'
            ).exclude(id__in=alunos_ja_enturmados)


class LancamentoNotaForm(forms.ModelForm):
    """Formulário para lançamento de notas"""
    
    class Meta:
        model = LancamentoNota
        fields = ['turma', 'disciplina', 'divisao_periodo', 'aluno', 'nota', 'conceito', 
                  'aulas_previstas', 'aulas_lecionadas', 'faltas', 'faltas_justificadas']
        
        widgets = {
            'turma': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'disciplina': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'divisao_periodo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'aluno': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'nota': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'step': '0.1',
                'min': '0',
                'max': '10'
            }),
            'conceito': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'aulas_previstas': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'aulas_lecionadas': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'faltas': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'faltas_justificadas': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
        }


class AulaRegistradaForm(forms.ModelForm):
    """Formulário para registro de aulas"""
    
    class Meta:
        model = AulaRegistrada
        fields = ['turma', 'disciplina', 'data_aula', 'horario_inicio', 'horario_fim', 
                  'conteudo_programatico', 'observacoes']
        
        widgets = {
            'turma': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
            }),
            'disciplina': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
            }),
            'data_aula': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
            }),
            'horario_inicio': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
            }),
            'horario_fim': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
            }),
            'conteudo_programatico': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'rows': 4,
                'placeholder': 'Descreva o conteúdo que será ministrado na aula...'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'rows': 2,
                'placeholder': 'Observações adicionais (opcional)...'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        horario_inicio = cleaned_data.get('horario_inicio')
        horario_fim = cleaned_data.get('horario_fim')
        
        if horario_inicio and horario_fim and horario_fim <= horario_inicio:
            raise ValidationError('O horário de fim deve ser posterior ao horário de início.')
        
        return cleaned_data


class RegistroFrequenciaForm(forms.ModelForm):
    """Formulário para registro de frequência"""
    
    class Meta:
        model = RegistroFrequencia
        fields = ['situacao', 'observacoes']
        
        widgets = {
            'situacao': forms.Select(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'observacoes': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Observações...'
            }),
        }


class TipoAvaliacaoForm(forms.ModelForm):
    """Formulário para tipos de avaliação"""
    
    class Meta:
        model = TipoAvaliacao
        fields = ['nome', 'descricao', 'peso_default', 'cor_display', 'ativo']
        
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500',
                'placeholder': 'Ex: Prova Bimestral'
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500',
                'placeholder': 'Descrição do tipo de avaliação...'
            }),
            'peso_default': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500',
                'step': '0.1',
                'min': '0.1',
                'max': '10.0'
            }),
            'cor_display': forms.TextInput(attrs={
                'type': 'color',
                'class': 'w-16 h-10 border border-gray-300 rounded cursor-pointer'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-purple-600 bg-gray-100 border-gray-300 rounded focus:ring-purple-500'
            }),
        }


class AvaliacaoForm(forms.ModelForm):
    """Formulário para criar avaliações"""
    
    class Meta:
        model = Avaliacao
        fields = ['turma', 'disciplina', 'divisao_periodo', 'tipo_avaliacao', 'nome', 
                  'descricao', 'data_aplicacao', 'valor_maximo', 'peso']
        
        widgets = {
            'turma': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'disciplina': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'divisao_periodo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'tipo_avaliacao': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'nome': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Ex: Prova de Matemática - 1º Bimestre'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 3,
                'placeholder': 'Descrição da avaliação, conteúdo abordado, etc...'
            }),
            'data_aplicacao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'valor_maximo': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'step': '0.01',
                'min': '0.01'
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'step': '0.1',
                'min': '0.1'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.groups.filter(name='Professor').exists():
            # Filtrar apenas turmas do professor
            turmas_ids = AulaRegistrada.objects.filter(
                professor=user
            ).values_list('turma', flat=True).distinct()
            self.fields['turma'].queryset = Turma.objects.filter(id__in=turmas_ids)


class NotaAvaliacaoForm(forms.ModelForm):
    """Formulário para lançamento de notas individuais"""
    
    class Meta:
        model = NotaAvaliacao
        fields = ['nota', 'conceito', 'observacoes', 'ausente', 'dispensado']
        
        widgets = {
            'nota': forms.NumberInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'step': '0.01',
                'min': '0'
            }),
            'conceito': forms.Select(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'observacoes': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Observações...'
            }),
            'ausente': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'dispensado': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        nota = cleaned_data.get('nota')
        conceito = cleaned_data.get('conceito')
        ausente = cleaned_data.get('ausente')
        dispensado = cleaned_data.get('dispensado')
        
        if not ausente and not dispensado and not nota and not conceito:
            raise ValidationError('Informe uma nota ou conceito, ou marque como ausente/dispensado.')
        
        if nota and conceito:
            raise ValidationError('Informe apenas nota OU conceito, não ambos.')
        
        return cleaned_data


class FiltroRelatorioForm(forms.Form):
    """Formulário para filtros de relatórios"""
    
    turma = forms.ModelChoiceField(
        queryset=Turma.objects.all(),
        required=False,
        empty_label="Todas as turmas",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-gray-500'
        })
    )
    
    disciplina = forms.ModelChoiceField(
        queryset=Disciplina.objects.all(),
        required=False,
        empty_label="Todas as disciplinas",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-gray-500'
        })
    )
    
    periodo = forms.ModelChoiceField(
        queryset=DivisaoPeriodoLetivo.objects.filter(ativo=True),
        required=False,
        empty_label="Todos os períodos",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-gray-500'
        })
    )
    
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-gray-500'
        })
    )
    
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-gray-500'
        })
    )