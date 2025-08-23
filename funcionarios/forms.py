from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Funcionario, DocumentacaoFuncionario, DadosFuncionais, DuploVinculo,
    Habilitacao, Escolaridade, FormacaoSuperior, Disponibilidade,
    DisciplinaFuncionario, DeficienciaFuncionario, AssociacaoProfessor, AssociacaoOutrosProfissionais
)
from datetime import date

class FuncionarioForm(forms.ModelForm):
    # Campos adicionais que não estão diretamente no modelo Funcionario
    cpf = forms.CharField(max_length=14, required=True, label="CPF")
    rg = forms.CharField(max_length=20, required=False, label="RG")
    matricula = forms.CharField(max_length=20, required=True, label="Matrícula")
    funcao = forms.ChoiceField(required=True, label="Função")
    situacao_funcional = forms.ChoiceField(required=True, label="Situação Funcional")
    tipo_vinculo = forms.ChoiceField(required=True, label="Tipo de Vínculo")
    data_admissao = forms.DateField(required=True, label="Data de Admissão")
    observacoes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label="Observações")

    class Meta:
        model = Funcionario
        fields = [
            'nome', 'nome_social', 'data_nascimento', 'sexo', 'estado_civil', 'cor_raca',
            'nacionalidade', 'naturalidade', 'uf_nascimento', 'nome_mae', 'nome_pai',
            'telefone', 'celular', 'email', 'cep', 'endereco', 'numero', 'complemento',
            'bairro', 'cidade', 'uf', 'tipo_arquivo', 'foto'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'Nome completo do funcionário (obrigatório)'
            }),
            'nome_social': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nome social (opcional)'
            }),
            'data_nascimento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                    'min': '1900-01-01',
                    'max': date.today().strftime('%Y-%m-%d')
                }
            ),
            'sexo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'estado_civil': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'cor_raca': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'nacionalidade': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'naturalidade': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'Cidade de nascimento'
            }),
            'uf_nascimento': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'UF',
                'maxlength': '2'
            }),
            'nome_mae': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'Nome da mãe'
            }),
            'nome_pai': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nome do pai'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '(00) 0000-0000',
                'maxlength': '14'
            }),
            'celular': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '(00) 00000-0000',
                'maxlength': '15'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'email@exemplo.com'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '00000-000',
                'data-mask': '00000-000',
                'maxlength': '9'
            }),
            'endereco': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'Logradouro'
            }),
            'numero': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'Número',
                'pattern': '[0-9]*',
                'inputmode': 'numeric'
            }),
            'complemento': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Complemento'
            }),
            'bairro': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'Bairro'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'Cidade'
            }),
            'uf': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'UF',
                'maxlength': '2'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'accept': 'image/*'
            }),
            'tipo_arquivo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Definir choices para os campos de DadosFuncionais
        self.fields['funcao'].choices = DadosFuncionais.FUNCAO_CHOICES
        self.fields['situacao_funcional'].choices = DadosFuncionais.SITUACAO_CHOICES
        self.fields['tipo_vinculo'].choices = DadosFuncionais.TIPO_VINCULO_CHOICES
        
        # Adicionar widgets para os campos customizados
        self.fields['cpf'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
            'placeholder': '000.000.000-00',
            'data-mask': '000.000.000-00',
            'maxlength': '14'
        })
        self.fields['rg'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Número do RG'
        })
        self.fields['matricula'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
            'placeholder': 'Matrícula do funcionário',
            'pattern': '[0-9]*',
            'inputmode': 'numeric'
        })
        self.fields['funcao'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
        })
        self.fields['situacao_funcional'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
        })
        self.fields['tipo_vinculo'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
        })
        self.fields['data_admissao'].widget = forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
        })
        self.fields['observacoes'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Observações adicionais (opcional)'
        })
        
        # Preencher com dados existentes se estiver editando
        if self.instance and self.instance.pk:
            try:
                documentacao = self.instance.documentacao
                self.fields['cpf'].initial = documentacao.cpf
                self.fields['rg'].initial = documentacao.rg
            except DocumentacaoFuncionario.DoesNotExist:
                pass
            
            try:
                dados_funcionais = self.instance.dados_funcionais
                self.fields['matricula'].initial = dados_funcionais.matricula
                self.fields['funcao'].initial = dados_funcionais.funcao
                self.fields['situacao_funcional'].initial = dados_funcionais.situacao_funcional
                self.fields['tipo_vinculo'].initial = dados_funcionais.tipo_vinculo
                self.fields['data_admissao'].initial = dados_funcionais.data_admissao
                self.fields['observacoes'].initial = dados_funcionais.observacoes
            except DadosFuncionais.DoesNotExist:
                pass
    
    def clean_data_nascimento(self):
        data_nascimento = self.cleaned_data.get('data_nascimento')
        if data_nascimento:
            hoje = date.today()
            if data_nascimento > hoje:
                raise ValidationError("A data de nascimento não pode ser futura.")
            
            idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
            if idade < 16:
                raise ValidationError("O funcionário deve ter pelo menos 16 anos.")
            if idade > 100:
                raise ValidationError("A data de nascimento parece incorreta. Verifique se foi digitada corretamente.")
        
        return data_nascimento
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Remove formatação
            cpf_numeros = ''.join(filter(str.isdigit, cpf))
            if len(cpf_numeros) != 11:
                raise ValidationError("CPF deve conter 11 dígitos.")
        return cpf
    
    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            telefone_numeros = ''.join(filter(str.isdigit, telefone))
            if len(telefone_numeros) != 10:
                raise ValidationError("Telefone deve ter exatamente 10 dígitos (formato: DDD + 8 dígitos).")
        return telefone
    
    def clean_celular(self):
        celular = self.cleaned_data.get('celular')
        if celular:
            celular_numeros = ''.join(filter(str.isdigit, celular))
            if len(celular_numeros) != 11:
                raise ValidationError("Celular deve ter exatamente 11 dígitos (formato: DDD + 9 dígitos).")
        return celular
    
    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula')
        if matricula and not matricula.isdigit():
            raise ValidationError("Matrícula deve conter apenas números.")
        return matricula
    
    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        if numero and not numero.isdigit():
            raise ValidationError("Número deve conter apenas dígitos.")
        return numero
    
    def save(self, commit=True):
        funcionario = super().save(commit=False)
        
        if commit:
            funcionario.save()
            
            # Criar ou atualizar documentação
            documentacao, created = DocumentacaoFuncionario.objects.get_or_create(
                funcionario=funcionario,
                defaults={
                    'cpf': self.cleaned_data['cpf'],
                    'rg': self.cleaned_data['rg']
                }
            )
            if not created:
                documentacao.cpf = self.cleaned_data['cpf']
                documentacao.rg = self.cleaned_data['rg']
                documentacao.save()
            
            # Criar ou atualizar dados funcionais
            dados_funcionais, created = DadosFuncionais.objects.get_or_create(
                funcionario=funcionario,
                defaults={
                    'matricula': self.cleaned_data['matricula'],
                    'funcao': self.cleaned_data['funcao'],
                    'situacao_funcional': self.cleaned_data['situacao_funcional'],
                    'tipo_vinculo': self.cleaned_data['tipo_vinculo'],
                    'data_admissao': self.cleaned_data['data_admissao'],
                    'observacoes': self.cleaned_data['observacoes']
                }
            )
            if not created:
                dados_funcionais.matricula = self.cleaned_data['matricula']
                dados_funcionais.funcao = self.cleaned_data['funcao']
                dados_funcionais.situacao_funcional = self.cleaned_data['situacao_funcional']
                dados_funcionais.tipo_vinculo = self.cleaned_data['tipo_vinculo']
                dados_funcionais.data_admissao = self.cleaned_data['data_admissao']
                dados_funcionais.observacoes = self.cleaned_data['observacoes']
                dados_funcionais.save()
        
        return funcionario

class DocumentacaoFuncionarioForm(forms.ModelForm):
    class Meta:
        model = DocumentacaoFuncionario
        fields = [
            'rg', 'rg_orgao_expedidor', 'rg_uf', 'rg_data_expedicao',
            'cpf', 'nis_pis_pasep', 'titulo_eleitor',
            'carteira_trabalho', 'carteira_trabalho_serie', 'carteira_trabalho_uf'
        ]
        widgets = {
            'rg': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'Número do RG'
            }),
            'rg_orgao_expedidor': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'SSP'
            }),
            'rg_uf': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'UF',
                'maxlength': '2'
            }),
            'rg_data_expedicao': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': '000.000.000-00'
            }),
            'nis_pis_pasep': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'NIS/PIS/PASEP'
            }),
            'titulo_eleitor': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Número do título'
            }),
            'carteira_trabalho': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Número da CTPS'
            }),
            'carteira_trabalho_serie': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Série'
            }),
            'carteira_trabalho_uf': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'UF',
                'maxlength': '2'
            })
        }

class DadosFuncionaisForm(forms.ModelForm):
    class Meta:
        model = DadosFuncionais
        fields = [
            'matricula', 'funcao', 'situacao_funcional', 'tipo_vinculo',
            'data_admissao', 'data_demissao', 'data_final_contrato',
            'carga_horaria_semanal', 'carga_horaria_contrato', 'observacoes'
        ]
        widgets = {
            'matricula': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'Matrícula do funcionário',
                'onblur': 'checkMatricula(this.value)'
            }),
            'funcao': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'situacao_funcional': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'tipo_vinculo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'data_admissao': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
                }
            ),
            'data_demissao': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'data_final_contrato': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'carga_horaria_semanal': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '1',
                'max': '60'
            }),
            'carga_horaria_contrato': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '1',
                'max': '60'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Observações sobre os dados funcionais'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        data_demissao = cleaned_data.get('data_demissao')
        data_final_contrato = cleaned_data.get('data_final_contrato')
        
        # RNF406: Data de demissão/final contrato não pode ser anterior à associação (validação simplificada)
        if data_demissao and data_demissao < date.today():
            if hasattr(self.instance, 'funcionario'):
                # Verificar se tem associações ativas após a data
                pass  # Implementar validação completa quando models de Turma estiverem prontos
        
        return cleaned_data

class DuploVinculoForm(forms.ModelForm):
    class Meta:
        model = DuploVinculo
        fields = [
            'matricula_secundaria', 'funcao_secundaria', 'situacao_secundaria',
            'tipo_vinculo_secundario', 'data_admissao_secundaria', 
            'data_demissao_secundaria', 'carga_horaria_secundaria'
        ]
        widgets = {
            'matricula_secundaria': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'Matrícula secundária'
            }),
            'funcao_secundaria': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'situacao_secundaria': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'tipo_vinculo_secundario': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'data_admissao_secundaria': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
                }
            ),
            'data_demissao_secundaria': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'carga_horaria_secundaria': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '1',
                'max': '40'
            })
        }

class HabilitacaoForm(forms.ModelForm):
    class Meta:
        model = Habilitacao
        fields = ['tipo_habilitacao', 'area_conhecimento', 'instituicao', 'ano_conclusao']
        widgets = {
            'tipo_habilitacao': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'area_conhecimento': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Ex: Matemática, Português, Pedagogia'
            }),
            'instituicao': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nome da instituição'
            }),
            'ano_conclusao': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '1960',
                'max': date.today().year + 10
            })
        }

class EscolaridadeForm(forms.ModelForm):
    class Meta:
        model = Escolaridade
        fields = ['nivel', 'curso', 'instituicao', 'ano_conclusao']
        widgets = {
            'nivel': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'curso': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nome do curso'
            }),
            'instituicao': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nome da instituição'
            }),
            'ano_conclusao': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '1960',
                'max': date.today().year + 10
            })
        }

class FormacaoSuperiorForm(forms.ModelForm):
    class Meta:
        model = FormacaoSuperior
        fields = ['curso', 'instituicao', 'ano_conclusao', 'tipo_curso']
        widgets = {
            'curso': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nome do curso'
            }),
            'instituicao': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nome da instituição'
            }),
            'ano_conclusao': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '1960',
                'max': date.today().year + 10
            }),
            'tipo_curso': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            })
        }

class DisponibilidadeForm(forms.ModelForm):
    class Meta:
        model = Disponibilidade
        fields = ['matutino', 'vespertino', 'noturno']
        widgets = {
            'matutino': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'vespertino': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            }),
            'noturno': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            })
        }

class DisciplinaFuncionarioForm(forms.ModelForm):
    class Meta:
        model = DisciplinaFuncionario
        fields = ['disciplina', 'habilitado']
        widgets = {
            'disciplina': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nome da disciplina'
            }),
            'habilitado': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            })
        }

class DeficienciaFuncionarioForm(forms.ModelForm):
    class Meta:
        model = DeficienciaFuncionario
        fields = ['tipo_deficiencia', 'descricao']
        widgets = {
            'tipo_deficiencia': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'onchange': 'checkDeficienciaMultipla()'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Descrição da deficiência'
            })
        }

class AssociacaoProfessorForm(forms.ModelForm):
    class Meta:
        model = AssociacaoProfessor
        fields = [
            'funcionario', 'turma', 'disciplina', 'tipo_associacao',
            'data_inicio', 'data_termino', 'sem_docente'
        ]
        widgets = {
            'funcionario': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'turma': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'Nome da turma'
            }),
            'disciplina': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'Nome da disciplina'
            }),
            'tipo_associacao': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'data_inicio': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'data_termino': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'sem_docente': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # RNF501: Apenas docentes na lista
        self.fields['funcionario'].queryset = Funcionario.objects.filter(
            dados_funcionais__funcao='DOCENTE',
            tipo_arquivo='CORRENTE'
        )

class AssociacaoOutrosProfissionaisForm(forms.ModelForm):
    class Meta:
        model = AssociacaoOutrosProfissionais
        fields = [
            'funcionario', 'turma', 'tipo_profissional', 
            'data_inicio', 'data_termino'
        ]
        widgets = {
            'funcionario': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'turma': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50',
                'placeholder': 'Nome da turma'
            }),
            'tipo_profissional': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'data_inicio': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-green-50'
            }),
            'data_termino': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # RNF502: Filtrar funcionários por função correspondente
        if self.data and 'tipo_profissional' in self.data:
            tipo = self.data['tipo_profissional']
            if tipo == 'AUXILIAR_EDUCACIONAL':
                self.fields['funcionario'].queryset = Funcionario.objects.filter(
                    dados_funcionais__funcao='AUXILIAR_EDUCACIONAL',
                    tipo_arquivo='CORRENTE'
                )
            elif tipo == 'MONITOR_ATIVIDADE':
                self.fields['funcionario'].queryset = Funcionario.objects.filter(
                    dados_funcionais__funcao='PROFISSIONAL_MONITOR',
                    tipo_arquivo='CORRENTE'
                )
            elif tipo == 'TRADUTOR_LIBRAS':
                self.fields['funcionario'].queryset = Funcionario.objects.filter(
                    dados_funcionais__funcao='TRADUTOR_LIBRAS',
                    tipo_arquivo='CORRENTE'
                )

class BuscaRedeForm(forms.Form):
    TIPO_BUSCA_CHOICES = [
        ('nome', 'Nome'),
        ('cpf', 'CPF'),
        ('matricula', 'Matrícula'),
    ]
    
    busca = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Digite o termo de busca'
        })
    )
    
    tipo_busca = forms.ChoiceField(
        choices=TIPO_BUSCA_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )