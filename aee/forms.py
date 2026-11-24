from django import forms
from django.core.exceptions import ValidationError

from alunos.models import Aluno
from .models import EnturmacaoAEE, ProjetoPedagogico, TurmaAEE


class ProjetoPedagogicoForm(forms.ModelForm):
    class Meta:
        model = ProjetoPedagogico
        fields = ['nome', 'tipo_projeto', 'periodo_letivo', 'carga_horaria', 'descricao', 'ativo']
        widgets = {'descricao': forms.Textarea(attrs={'rows': 4})}

    def clean_carga_horaria(self):
        carga = self.cleaned_data['carga_horaria']
        if carga <= 0:
            raise ValidationError('A carga horária deve ser maior que zero.')
        return carga


class TurmaAEEForm(forms.ModelForm):
    class Meta:
        model = TurmaAEE
        fields = [
            'nome', 'projeto_pedagogico', 'periodo_letivo', 'turno', 'hora_inicio', 'hora_fim',
            'maximo_alunos', 'ordenacao', 'segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado',
            'atividade_especifica', 'local', 'material_necessario', 'situacao', 'observacoes',
        ]
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'hora_fim': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'material_necessario': forms.Textarea(attrs={'rows': 2}),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        projetos = ProjetoPedagogico.objects.filter(ativo=True)
        if self.instance.pk:
            projetos = projetos | ProjetoPedagogico.objects.filter(pk=self.instance.projeto_pedagogico_id)
        self.fields['projeto_pedagogico'].queryset = projetos.distinct()

    def clean(self):
        dados = super().clean()
        inicio, fim = dados.get('hora_inicio'), dados.get('hora_fim')
        if inicio and fim and fim <= inicio:
            self.add_error('hora_fim', 'O horário de término deve ser posterior ao de início.')
        if not any(dados.get(d) for d in ('segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado')):
            raise ValidationError('Selecione ao menos um dia da semana.')
        maximo = dados.get('maximo_alunos')
        if self.instance.pk and maximo and maximo < self.instance.get_total_alunos():
            self.add_error('maximo_alunos', 'O máximo não pode ser menor que o número de alunos já enturmados.')
        return dados


class EnturmacaoAEEForm(forms.ModelForm):
    class Meta:
        model = EnturmacaoAEE
        fields = ['turma', 'aluno', 'origem', 'escola_origem', 'codigo_escola_origem',
                  'ano_administrativo', 'tipo_ensino', 'ano_serie']
        help_texts = {
            'escola_origem': 'Obrigatório para alunos de outra escola da rede.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['turma'].queryset = TurmaAEE.objects.filter(situacao='ATIVO').order_by('nome')
        self.fields['aluno'].queryset = Aluno.objects.filter(tipo_arquivo='CORRENTE').order_by('nome')

    def clean(self):
        dados = super().clean()
        turma, aluno = dados.get('turma'), dados.get('aluno')
        if turma and not turma.tem_vaga():
            self.add_error('turma', 'Esta turma não possui vagas disponíveis.')
        if turma and aluno and EnturmacaoAEE.objects.filter(turma=turma, aluno=aluno, ativo=True).exists():
            self.add_error('aluno', 'O aluno já está enturmado nesta turma.')
        if dados.get('origem') == 'OUTRA_ESCOLA_REDE' and not dados.get('escola_origem'):
            self.add_error('escola_origem', 'Informe a escola de origem.')
        return dados
