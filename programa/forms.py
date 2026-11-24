from django import forms
from django.core.exceptions import ValidationError

from alunos.models import Aluno
from .models import AulaPrograma, ModuloPrograma, ParticipantePrograma, ProgramaPedagogico

DATA = {'type': 'date'}
HORA = {'type': 'time'}


class ProgramaPedagogicoForm(forms.ModelForm):
    class Meta:
        model = ProgramaPedagogico
        fields = [
            'nome', 'tipo_programa', 'modalidade', 'status', 'coordenador', 'data_inicio', 'data_fim',
            'carga_horaria_total', 'vagas_disponiveis', 'idade_minima', 'idade_maxima', 'descricao',
            'objetivos_gerais', 'objetivos_especificos', 'competencias', 'habilidades', 'publico_alvo',
            'recursos_humanos', 'recursos_materiais', 'recursos_tecnologicos',
            'metodologia_avaliacao', 'criterios_aprovacao', 'aprovado', 'data_aprovacao', 'observacoes',
        ]
        widgets = {
            'data_inicio': forms.DateInput(attrs=DATA, format='%Y-%m-%d'),
            'data_fim': forms.DateInput(attrs=DATA, format='%Y-%m-%d'),
            'data_aprovacao': forms.DateInput(attrs=DATA, format='%Y-%m-%d'),
            **{campo: forms.Textarea(attrs={'rows': 3}) for campo in (
                'descricao', 'objetivos_gerais', 'objetivos_especificos', 'competencias', 'habilidades',
                'publico_alvo', 'recursos_humanos', 'recursos_materiais', 'recursos_tecnologicos',
                'metodologia_avaliacao', 'criterios_aprovacao', 'observacoes',
            )},
        }

    def clean(self):
        dados = super().clean()
        inicio, fim = dados.get('data_inicio'), dados.get('data_fim')
        if inicio and fim and fim < inicio:
            self.add_error('data_fim', 'A data de término deve ser posterior ao início.')
        minima, maxima = dados.get('idade_minima'), dados.get('idade_maxima')
        if minima is not None and maxima is not None and maxima < minima:
            self.add_error('idade_maxima', 'A idade máxima deve ser maior que a mínima.')
        if dados.get('aprovado') and not dados.get('data_aprovacao'):
            self.add_error('data_aprovacao', 'Informe a data de aprovação.')
        vagas = dados.get('vagas_disponiveis')
        if self.instance.pk and vagas is not None and vagas < self.instance.total_participantes:
            self.add_error('vagas_disponiveis', 'Há mais participantes ativos do que vagas informadas.')
        return dados


class ModuloProgramaForm(forms.ModelForm):
    class Meta:
        model = ModuloPrograma
        fields = ['programa', 'ordem', 'nome', 'data_inicio', 'data_fim', 'carga_horaria',
                  'professor_responsavel', 'descricao', 'conteudo_programatico', 'metodologia',
                  'recursos_necessarios', 'ativo']
        widgets = {
            'data_inicio': forms.DateInput(attrs=DATA, format='%Y-%m-%d'),
            'data_fim': forms.DateInput(attrs=DATA, format='%Y-%m-%d'),
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'conteudo_programatico': forms.Textarea(attrs={'rows': 3}),
            'metodologia': forms.Textarea(attrs={'rows': 3}),
            'recursos_necessarios': forms.Textarea(attrs={'rows': 2}),
        }

    def clean(self):
        dados = super().clean()
        programa, inicio, fim = dados.get('programa'), dados.get('data_inicio'), dados.get('data_fim')
        if inicio and fim and fim < inicio:
            self.add_error('data_fim', 'A data de término deve ser posterior ao início.')
        if programa and inicio and fim and (inicio < programa.data_inicio or fim > programa.data_fim):
            raise ValidationError(
                f'O módulo deve ocorrer dentro do período do programa '
                f'({programa.data_inicio:%d/%m/%Y} a {programa.data_fim:%d/%m/%Y}).'
            )
        return dados


class ParticipanteProgramaForm(forms.ModelForm):
    class Meta:
        model = ParticipantePrograma
        fields = ['aluno', 'data_inscricao', 'data_inicio', 'situacao', 'observacoes']
        widgets = {
            'data_inscricao': forms.DateInput(attrs=DATA, format='%Y-%m-%d'),
            'data_inicio': forms.DateInput(attrs=DATA, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        self.programa = kwargs.pop('programa')
        super().__init__(*args, **kwargs)
        inscritos = self.programa.participantes.values_list('aluno_id', flat=True)
        self.fields['aluno'].queryset = Aluno.objects.filter(tipo_arquivo='CORRENTE').exclude(
            pk__in=inscritos).order_by('nome')

    def clean_aluno(self):
        aluno = self.cleaned_data['aluno']
        programa = self.programa
        if programa.vagas_restantes <= 0:
            raise ValidationError('Não há vagas disponíveis neste programa.')
        idade = aluno.idade
        if programa.idade_minima and idade < programa.idade_minima:
            raise ValidationError(f'Idade mínima para o programa: {programa.idade_minima} anos.')
        if programa.idade_maxima and idade > programa.idade_maxima:
            raise ValidationError(f'Idade máxima para o programa: {programa.idade_maxima} anos.')
        return aluno


class AulaProgramaForm(forms.ModelForm):
    class Meta:
        model = AulaPrograma
        fields = ['modulo', 'numero_aula', 'titulo', 'tipo_aula', 'data_planejada', 'horario_inicio',
                  'horario_fim', 'carga_horaria', 'professor', 'objetivos', 'conteudo', 'metodologia',
                  'recursos_utilizados', 'status', 'observacoes']
        widgets = {
            'data_planejada': forms.DateInput(attrs=DATA, format='%Y-%m-%d'),
            'horario_inicio': forms.TimeInput(attrs=HORA, format='%H:%M'),
            'horario_fim': forms.TimeInput(attrs=HORA, format='%H:%M'),
            'objetivos': forms.Textarea(attrs={'rows': 2}),
            'conteudo': forms.Textarea(attrs={'rows': 3}),
            'metodologia': forms.Textarea(attrs={'rows': 2}),
            'recursos_utilizados': forms.Textarea(attrs={'rows': 2}),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['modulo'].queryset = ModuloPrograma.objects.filter(ativo=True).select_related('programa')

    def clean(self):
        dados = super().clean()
        inicio, fim = dados.get('horario_inicio'), dados.get('horario_fim')
        if inicio and fim and fim <= inicio:
            self.add_error('horario_fim', 'O horário de término deve ser posterior ao início.')
        return dados
