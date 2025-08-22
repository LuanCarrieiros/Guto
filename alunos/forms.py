from django import forms
from django.core.exceptions import ValidationError
from .models import Aluno, DocumentacaoAluno, Responsavel, TransporteAluno, Matricula
from datetime import date

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = [
            'nome', 'nome_social', 'data_nascimento', 'sexo',
            'nome_mae', 'nome_pai', 'mae_nao_declarada', 'pai_nao_declarado',
            'aluno_gemeo', 'falta_historico_escolar', 'aluno_exclusivo_aee',
            'lembrete', 'foto'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'Nome completo do aluno (obrigatório)'
            }),
            'nome_social': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nome social (opcional)'
            }),
            'data_nascimento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
                }
            ),
            'sexo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'nome_mae': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nome da mãe'
            }),
            'nome_pai': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nome do pai'
            }),
            'mae_nao_declarada': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'pai_nao_declarado': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'aluno_gemeo': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'falta_historico_escolar': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'aluno_exclusivo_aee': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'lembrete': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Observações ou lembretes sobre o aluno'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'accept': 'image/*'
            })
        }
    
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if nome:
            # RNF101: Nome deve conter nome e sobrenome
            partes_nome = nome.strip().split()
            if len(partes_nome) < 2:
                raise ValidationError('O nome deve conter nome e sobrenome')
        return nome
    
    def clean_data_nascimento(self):
        data_nascimento = self.cleaned_data.get('data_nascimento')
        if data_nascimento:
            if data_nascimento > date.today():
                raise ValidationError('A data de nascimento não pode ser no futuro')
        return data_nascimento

class DocumentacaoAlunoForm(forms.ModelForm):
    class Meta:
        model = DocumentacaoAluno
        fields = [
            'rg', 'cpf', 'certidao_nascimento', 'titulo_eleitor',
            'aluno_nao_possui_documentos', 'escola_nao_recebeu_documentos'
        ]
        widgets = {
            'rg': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Número do RG'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'CPF (000.000.000-00)'
            }),
            'certidao_nascimento': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Número da certidão de nascimento'
            }),
            'titulo_eleitor': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Número do título de eleitor'
            }),
            'aluno_nao_possui_documentos': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'escola_nao_recebeu_documentos': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        rg = cleaned_data.get('rg')
        certidao_nascimento = cleaned_data.get('certidao_nascimento')
        aluno_nao_possui = cleaned_data.get('aluno_nao_possui_documentos')
        escola_nao_recebeu = cleaned_data.get('escola_nao_recebeu_documentos')
        
        # RNF107: É obrigatório informar pelo menos a Identidade ou a Certidão de Nascimento
        if not aluno_nao_possui and not escola_nao_recebeu:
            if not rg and not certidao_nascimento:
                raise ValidationError('É obrigatório informar pelo menos o RG ou a Certidão de Nascimento')
        
        return cleaned_data

class ResponsavelForm(forms.ModelForm):
    class Meta:
        model = Responsavel
        fields = ['nome', 'parentesco', 'telefone', 'email', 'endereco']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'Nome completo do responsável'
            }),
            'parentesco': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'Ex: Pai, Mãe, Avó, Tio, etc.'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '(00) 00000-0000'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'email@exemplo.com'
            }),
            'endereco': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Endereço completo'
            })
        }

class TransporteAlunoForm(forms.ModelForm):
    class Meta:
        model = TransporteAluno
        fields = ['utiliza_transporte', 'nome_motorista', 'placa_veiculo', 'rota']
        widgets = {
            'utiliza_transporte': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500',
                'onchange': 'toggleTransportFields(this.checked)'
            }),
            'nome_motorista': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nome do motorista'
            }),
            'placa_veiculo': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'ABC-1234'
            }),
            'rota': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nome ou número da rota'
            })
        }

class MatriculaForm(forms.ModelForm):
    class Meta:
        model = Matricula
        fields = [
            'ano_administrativo', 'tipo_ensino', 'serie_ano', 'tipo_matricula',
            'turno_preferencial', 'data_matricula', 'possui_dependencia',
            'condicao_anterior', 'escola_origem', 'tipo_rede_origem', 'pais_origem',
            'condicoes_especiais_avaliacao'
        ]
        widgets = {
            'ano_administrativo': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'min': '2020',
                'max': '2030',
                'value': date.today().year
            }),
            'tipo_ensino': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'serie_ano': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'Ex: 1º Ano, 5ª Série, Módulo I'
            }),
            'tipo_matricula': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'turno_preferencial': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'data_matricula': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'value': date.today().strftime('%Y-%m-%d')
            }),
            'possui_dependencia': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'condicao_anterior': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'onchange': 'toggleEscolaOrigem(this.value)'
            }),
            'escola_origem': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nome da escola de origem'
            }),
            'tipo_rede_origem': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Ex: Pública Municipal, Privada, etc.'
            }),
            'pais_origem': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'País de origem'
            }),
            'condicoes_especiais_avaliacao': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            })
        }
    
    def clean_ano_administrativo(self):
        ano = self.cleaned_data.get('ano_administrativo')
        if ano:
            # RNF201: Ano administrativo não pode ser alterado após criação
            if self.instance.pk and self.instance.ano_administrativo != ano:
                raise ValidationError('O ano administrativo não pode ser alterado após a criação da matrícula')
        return ano
    
    def clean(self):
        cleaned_data = super().clean()
        condicao_anterior = cleaned_data.get('condicao_anterior')
        escola_origem = cleaned_data.get('escola_origem')
        
        # RF204.5: Se novato na escola, dados da escola de origem são obrigatórios
        if condicao_anterior == 'NOVATO_ESCOLA':
            if not escola_origem:
                raise ValidationError('Para alunos novatos na escola, é obrigatório informar a escola de origem')
        
        return cleaned_data