from django import forms
from .models import (
    Conceito,
    Turma, Disciplina, DivisaoPeriodoLetivo, TipoAvaliacao, 
    Avaliacao
)


def mesmo_nome(nome, queryset, campo='nome'):
    """Verifica nomes iguais ignorando maiúsculas, acentuação de caixa e espaços extras.
    (Feito em Python porque o SQLite só compara maiúsculas/minúsculas de letras sem acento.)"""
    alvo = ' '.join(nome.split()).casefold()
    return any(' '.join(valor.split()).casefold() == alvo for valor in queryset.values_list(campo, flat=True))


class TurmaForm(forms.ModelForm):
    def clean(self):
        dados = super().clean()
        nome, periodo = dados.get('nome'), dados.get('periodo_letivo')
        if nome and periodo and mesmo_nome(nome, Turma.objects.filter(periodo_letivo=periodo).exclude(pk=self.instance.pk)):
            self.add_error('nome', f'Já existe uma turma com este nome em {periodo}.')
        if nome:
            dados['nome'] = ' '.join(nome.split())
        return dados

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

    def clean_nome(self):
        nome = ' '.join(self.cleaned_data['nome'].split())
        if mesmo_nome(nome, Disciplina.objects.exclude(pk=self.instance.pk)):
            raise forms.ValidationError(
                'Já existe uma disciplina com este nome. Uma disciplina (ex.: Matemática) é cadastrada '
                'uma única vez e vinculada a várias turmas, cada uma com seu professor.'
            )
        return nome
    
    class Meta:
        model = Disciplina
        fields = ['nome', 'codigo', 'avalia_por_conceito', 'carga_horaria']
        
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500',
                'placeholder': 'Ex: Matemática',
                'id': 'id_nome'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500',
                'placeholder': 'Deixe vazio para gerar automaticamente',
                'id': 'id_codigo'
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
            }, format='%Y-%m-%d'),
        }

    def clean(self):
        dados = super().clean()
        inicio, fim = dados.get('data_inicio'), dados.get('data_fim')
        if inicio and fim and fim < inicio:
            self.add_error('data_fim', 'A data de fim deve ser posterior ao início.')
        periodo, ordem = dados.get('periodo_letivo'), dados.get('ordem')
        if periodo and ordem and DivisaoPeriodoLetivo.objects.filter(
                periodo_letivo=periodo, ordem=ordem).exclude(pk=self.instance.pk).exists():
            self.add_error('ordem', f'Já existe uma divisão com a ordem {ordem} em {periodo}.')
        return dados


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
        self.user = user
        super().__init__(*args, **kwargs)
        
        if user is not None:
            # Professores veem apenas as turmas em que estão associados
            from diario.acesso import filtrar_turmas
            self.fields['turma'].queryset = filtrar_turmas(user, Turma.objects.order_by('-periodo_letivo', 'nome'))
        self.fields['disciplina'].queryset = Disciplina.objects.filter(ativo=True).order_by('nome')

    def clean(self):
        dados = super().clean()
        turma, divisao, user = dados.get('turma'), dados.get('divisao_periodo'), self.user
        if turma and divisao and divisao.periodo_letivo != turma.periodo_letivo:
            self.add_error('divisao_periodo', f'O período deve ser do ano letivo da turma ({turma.periodo_letivo}).')
        if turma and dados.get('disciplina') and user is not None:
            from diario.acesso import pode_acessar
            if not pode_acessar(user, turma, dados['disciplina']):
                self.add_error('disciplina', 'Você não é o professor desta disciplina nesta turma.')
        return dados


class AvaliacaoDiarioForm(forms.ModelForm):
    """Validação das avaliações criadas/editadas pelo diário (turma, disciplina e período vêm da URL)."""

    class Meta:
        model = Avaliacao
        fields = ['nome', 'tipo_avaliacao', 'peso', 'data_aplicacao', 'descricao']

    def clean_peso(self):
        peso = self.cleaned_data['peso']
        if peso is None or peso <= 0:
            raise forms.ValidationError('O peso deve ser maior que zero.')
        return peso


class ConceitoForm(forms.ModelForm):
    class Meta:
        model = Conceito
        fields = ['nome', 'descricao', 'valor_numerico', 'cor_display', 'ativo']
        widgets = {'cor_display': forms.TextInput(attrs={'type': 'color'})}
        help_texts = {'valor_numerico': 'Nota equivalente (0 a 10) usada no cálculo das médias.'}

    def clean_nome(self):
        nome = self.cleaned_data['nome'].strip().upper()
        if mesmo_nome(nome, Conceito.objects.exclude(pk=self.instance.pk)):
            raise forms.ValidationError('Já existe um conceito com este nome.')
        return nome
