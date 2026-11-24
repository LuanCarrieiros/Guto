from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import (
    GrupoAcesso, Instituicao, PerfilUsuario, ConfiguracaoSistema, DadoAdicional,
    SolicitacaoTransferencia, BloqueioFuncionalidade,
)

# Módulos do sistema que podem receber permissões e bloqueios
# (o código corresponde ao app_name das URLs de cada módulo).
MODULOS_SISTEMA = [
    ('alunos', 'Alunos'),
    ('funcionarios', 'Funcionários'),
    ('turma', 'Turmas e Avaliações'),
    ('diario', 'Diário Eletrônico'),
    ('escola', 'Itinerários Formativos'),
    ('aee', 'AEE / Atividade Complementar'),
    ('programa', 'Programas Pedagógicos'),
    ('transporte', 'Transporte Escolar'),
    ('censo', 'Censo e Relatórios'),
    ('opcoes', 'Opções (Calendário e Documentos)'),
]


class UsuarioForm(forms.ModelForm):
    """Dados básicos do usuário. A senha é opcional na edição."""
    grupos = forms.ModelMultipleChoiceField(
        queryset=GrupoAcesso.objects.filter(ativo=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Grupos de acesso',
    )
    nova_senha = forms.CharField(
        label='Senha', required=False, strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text='Deixe em branco para manter a senha atual.',
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff']
        labels = {
            'username': 'Usuário (login)',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
            'is_active': 'Usuário ativo',
            'is_staff': 'Acesso à área administrativa (/admin)',
        }
        help_texts = {'username': '', 'is_active': '', 'is_staff': ''}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['nova_senha'].required = True
            self.fields['nova_senha'].help_text = ''
        else:
            nomes = self.instance.groups.values_list('name', flat=True)
            self.initial.setdefault('grupos', GrupoAcesso.objects.filter(nome__in=nomes))

    def clean_nova_senha(self):
        senha = self.cleaned_data.get('nova_senha')
        if senha:
            validate_password(senha, self.instance if self.instance.pk else None)
        return senha

    def save(self, commit=True):
        usuario = super().save(commit=False)
        senha = self.cleaned_data.get('nova_senha')
        if senha:
            usuario.set_password(senha)
        if commit:
            usuario.save()
            sincronizar_grupos_usuario(usuario, self.cleaned_data.get('grupos', []))
        return usuario


def sincronizar_grupos_usuario(usuario, grupos_acesso):
    """Os grupos de acesso do GUTO são espelhados em grupos do Django (auth.Group)."""
    from django.contrib.auth.models import Group
    nomes_gerenciados = set(GrupoAcesso.objects.values_list('nome', flat=True))
    # Remove grupos gerenciados pelo GUTO e reaplica os selecionados
    usuario.groups.remove(*usuario.groups.filter(name__in=nomes_gerenciados))
    for grupo in grupos_acesso:
        auth_group, _ = Group.objects.get_or_create(name=grupo.nome)
        usuario.groups.add(auth_group)


class PerfilUsuarioForm(forms.ModelForm):
    """Dados complementares do usuário (opcionais)."""

    class Meta:
        model = PerfilUsuario
        fields = ['cpf', 'telefone', 'data_nascimento']
        widgets = {
            'cpf': forms.TextInput(attrs={'placeholder': '000.000.000-00'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(00) 00000-0000'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cpf'].required = False

    def has_data(self):
        return any(self.cleaned_data.get(c) for c in self.Meta.fields)


class GrupoAcessoForm(forms.ModelForm):
    class Meta:
        model = GrupoAcesso
        fields = ['nome', 'descricao', 'ativo']
        widgets = {'descricao': forms.Textarea(attrs={'rows': 3})}


class ConfiguracaoSistemaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoSistema
        fields = ['chave', 'valor', 'tipo_valor', 'descricao']
        widgets = {'valor': forms.Textarea(attrs={'rows': 2})}

    def clean(self):
        dados = super().clean()
        tipo, valor = dados.get('tipo_valor'), (dados.get('valor') or '').strip()
        if tipo == 'INTEGER' and valor and not valor.lstrip('-').isdigit():
            self.add_error('valor', 'Informe um número inteiro.')
        elif tipo == 'BOOLEAN' and valor.lower() not in ('true', 'false', 'sim', 'não', 'nao', '1', '0'):
            self.add_error('valor', 'Use "sim" ou "não".')
        elif tipo == 'JSON' and valor:
            import json
            try:
                json.loads(valor)
            except ValueError:
                self.add_error('valor', 'JSON inválido.')
        return dados


class DadoAdicionalForm(forms.ModelForm):
    class Meta:
        model = DadoAdicional
        fields = ['rotulo', 'tipo_campo', 'opcoes', 'ordem', 'obrigatorio', 'ativo']
        widgets = {'opcoes': forms.Textarea(attrs={'rows': 2})}

    def clean(self):
        dados = super().clean()
        if dados.get('tipo_campo') == 'SELECT' and not (dados.get('opcoes') or '').strip():
            self.add_error('opcoes', 'Informe as opções da lista, separadas por vírgula.')
        return dados


class InstituicaoForm(forms.ModelForm):
    class Meta:
        model = Instituicao
        fields = ['nome', 'codigo', 'tipo_instituicao', 'cnpj', 'telefone', 'email', 'endereco', 'instituicao_pai', 'ativo']
        widgets = {'endereco': forms.Textarea(attrs={'rows': 2})}


class SolicitacaoTransferenciaForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoTransferencia
        fields = ['aluno', 'escola_origem', 'escola_destino', 'motivo', 'observacoes']
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 3}),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ativas = Instituicao.objects.filter(ativo=True)
        self.fields['escola_origem'].queryset = ativas
        self.fields['escola_destino'].queryset = ativas

    def clean(self):
        dados = super().clean()
        origem, destino, aluno = dados.get('escola_origem'), dados.get('escola_destino'), dados.get('aluno')
        if origem and destino and origem == destino:
            self.add_error('escola_destino', 'A escola de destino deve ser diferente da origem.')
        if aluno and SolicitacaoTransferencia.objects.filter(aluno=aluno, status='PENDENTE').exists():
            self.add_error('aluno', 'Já existe uma solicitação pendente para este aluno.')
        return dados


class BloqueioFuncionalidadeForm(forms.ModelForm):
    modulo = forms.ChoiceField(choices=MODULOS_SISTEMA, label='Módulo')

    class Meta:
        model = BloqueioFuncionalidade
        fields = ['modulo', 'funcionalidade', 'tipo_bloqueio', 'ano_administrativo', 'tipo_ensino',
                  'motivo', 'data_inicio', 'data_fim', 'ativo']
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 2}),
            'data_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'data_fim': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
        help_texts = {
            'ano_administrativo': 'Obrigatório para bloqueio "Por Ano Administrativo".',
            'tipo_ensino': 'Obrigatório para bloqueio "Por Tipo de Ensino".',
        }

    def clean(self):
        dados = super().clean()
        tipo = dados.get('tipo_bloqueio')
        if tipo == 'POR_ANO' and not dados.get('ano_administrativo'):
            self.add_error('ano_administrativo', 'Informe o ano administrativo.')
        if tipo == 'POR_TIPO_ENSINO' and not dados.get('tipo_ensino'):
            self.add_error('tipo_ensino', 'Informe o tipo de ensino.')
        inicio, fim = dados.get('data_inicio'), dados.get('data_fim')
        if inicio and fim and fim <= inicio:
            self.add_error('data_fim', 'A data de fim deve ser posterior ao início.')
        return dados
