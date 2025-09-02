from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import (
    Motorista, Veiculo, Rota, PontoParada, 
    AlunoTransporte, RegistroViagem, ManutencaoVeiculo
)
from alunos.models import Aluno


class MotoristaForm(forms.ModelForm):
    class Meta:
        model = Motorista
        fields = [
            'nome', 'cpf', 'rg', 'data_nascimento', 'telefone', 'celular', 
            'endereco', 'cnh_numero', 'cnh_categoria', 'cnh_validade',
            'data_inicio_contrato', 'data_fim_contrato', 'salario', 'ativo'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-input'}),
            'cpf': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '000.000.000-00'}),
            'rg': forms.TextInput(attrs={'class': 'form-input'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'telefone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(00) 0000-0000'}),
            'celular': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(00) 00000-0000'}),
            'endereco': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'cnh_numero': forms.TextInput(attrs={'class': 'form-input'}),
            'cnh_categoria': forms.Select(attrs={'class': 'form-select'}),
            'cnh_validade': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'data_inicio_contrato': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'data_fim_contrato': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'salario': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Remove formatação
            cpf_limpo = ''.join(filter(str.isdigit, cpf))
            if len(cpf_limpo) != 11:
                raise ValidationError('CPF deve ter 11 dígitos.')
            return cpf
        return cpf

    def clean_cnh_validade(self):
        validade = self.cleaned_data.get('cnh_validade')
        if validade and validade < date.today():
            raise ValidationError('A CNH não pode estar vencida.')
        return validade

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio_contrato')
        data_fim = cleaned_data.get('data_fim_contrato')
        
        if data_inicio and data_fim and data_fim <= data_inicio:
            raise ValidationError('A data fim do contrato deve ser posterior à data de início.')
        
        return cleaned_data


class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = [
            'placa', 'tipo_veiculo', 'marca', 'modelo', 'ano_fabricacao', 'cor',
            'capacidade_passageiros', 'renavam', 'chassi', 'status', 'km_atual',
            'data_ultima_vistoria', 'proxima_vistoria', 'seguradora', 
            'numero_apolice', 'validade_seguro'
        ]
        widgets = {
            'placa': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ABC1234'}),
            'tipo_veiculo': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.TextInput(attrs={'class': 'form-input'}),
            'modelo': forms.TextInput(attrs={'class': 'form-input'}),
            'ano_fabricacao': forms.NumberInput(attrs={'class': 'form-input', 'min': '1990', 'max': '2030'}),
            'cor': forms.TextInput(attrs={'class': 'form-input'}),
            'capacidade_passageiros': forms.NumberInput(attrs={'class': 'form-input', 'min': '1'}),
            'renavam': forms.TextInput(attrs={'class': 'form-input'}),
            'chassi': forms.TextInput(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'km_atual': forms.NumberInput(attrs={'class': 'form-input', 'min': '0'}),
            'data_ultima_vistoria': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'proxima_vistoria': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'seguradora': forms.TextInput(attrs={'class': 'form-input'}),
            'numero_apolice': forms.TextInput(attrs={'class': 'form-input'}),
            'validade_seguro': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        }

    def clean_placa(self):
        placa = self.cleaned_data.get('placa', '').upper()
        if placa:
            # Remove espaços e hífens
            placa = placa.replace(' ', '').replace('-', '')
            if len(placa) not in [7, 8]:  # Formato antigo e novo
                raise ValidationError('Placa deve ter formato válido (ABC1234 ou ABC1A23).')
        return placa

    def clean_chassi(self):
        chassi = self.cleaned_data.get('chassi', '').upper()
        if chassi and len(chassi) != 17:
            raise ValidationError('Chassi deve ter exatamente 17 caracteres.')
        return chassi


class RotaForm(forms.ModelForm):
    class Meta:
        model = Rota
        fields = [
            'nome', 'descricao', 'turno', 'horario_saida_ida', 'horario_chegada_ida',
            'horario_saida_volta', 'horario_chegada_volta', 'veiculo', 'motorista',
            'ativa', 'km_total'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-input'}),
            'descricao': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'turno': forms.Select(attrs={'class': 'form-select'}),
            'horario_saida_ida': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'horario_chegada_ida': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'horario_saida_volta': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'horario_chegada_volta': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'veiculo': forms.Select(attrs={'class': 'form-select'}),
            'motorista': forms.Select(attrs={'class': 'form-select'}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'km_total': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['veiculo'].queryset = Veiculo.objects.filter(status='ATIVO')
        self.fields['motorista'].queryset = Motorista.objects.filter(ativo=True)


class PontoParadaForm(forms.ModelForm):
    class Meta:
        model = PontoParada
        fields = [
            'rota', 'nome', 'endereco', 'referencia', 'latitude', 'longitude',
            'horario_ida', 'horario_volta', 'ordem', 'ativo'
        ]
        widgets = {
            'rota': forms.Select(attrs={'class': 'form-select'}),
            'nome': forms.TextInput(attrs={'class': 'form-input'}),
            'endereco': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'referencia': forms.TextInput(attrs={'class': 'form-input'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.0000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.0000001'}),
            'horario_ida': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'horario_volta': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-input', 'min': '1'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rota'].queryset = Rota.objects.filter(ativa=True)


class AlunoTransporteForm(forms.ModelForm):
    class Meta:
        model = AlunoTransporte
        fields = [
            'aluno', 'rota', 'ponto_embarque', 'ponto_desembarque',
            'responsavel_nome', 'responsavel_telefone', 'responsavel_endereco',
            'data_inicio', 'data_fim', 'situacao', 'observacoes', 'ativo'
        ]
        widgets = {
            'aluno': forms.Select(attrs={'class': 'form-select'}),
            'rota': forms.Select(attrs={'class': 'form-select'}),
            'ponto_embarque': forms.Select(attrs={'class': 'form-select'}),
            'ponto_desembarque': forms.Select(attrs={'class': 'form-select'}),
            'responsavel_nome': forms.TextInput(attrs={'class': 'form-input'}),
            'responsavel_telefone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(00) 00000-0000'}),
            'responsavel_endereco': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'situacao': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['aluno'].queryset = Aluno.objects.filter(ativo=True)
        self.fields['rota'].queryset = Rota.objects.filter(ativa=True)
        
        if self.instance.pk and self.instance.rota:
            self.fields['ponto_embarque'].queryset = PontoParada.objects.filter(
                rota=self.instance.rota, ativo=True
            )
            self.fields['ponto_desembarque'].queryset = PontoParada.objects.filter(
                rota=self.instance.rota, ativo=True
            )
        else:
            self.fields['ponto_embarque'].queryset = PontoParada.objects.none()
            self.fields['ponto_desembarque'].queryset = PontoParada.objects.none()


class RegistroViagemForm(forms.ModelForm):
    class Meta:
        model = RegistroViagem
        fields = [
            'rota', 'motorista', 'veiculo', 'data_viagem', 'tipo_viagem',
            'horario_saida_real', 'horario_chegada_real', 'km_inicial', 'km_final',
            'alunos_transportados', 'concluida', 'observacoes'
        ]
        widgets = {
            'rota': forms.Select(attrs={'class': 'form-select'}),
            'motorista': forms.Select(attrs={'class': 'form-select'}),
            'veiculo': forms.Select(attrs={'class': 'form-select'}),
            'data_viagem': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'tipo_viagem': forms.Select(attrs={'class': 'form-select'}),
            'horario_saida_real': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'horario_chegada_real': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'km_inicial': forms.NumberInput(attrs={'class': 'form-input', 'min': '0'}),
            'km_final': forms.NumberInput(attrs={'class': 'form-input', 'min': '0'}),
            'alunos_transportados': forms.NumberInput(attrs={'class': 'form-input', 'min': '0'}),
            'concluida': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rota'].queryset = Rota.objects.filter(ativa=True)
        self.fields['motorista'].queryset = Motorista.objects.filter(ativo=True)
        self.fields['veiculo'].queryset = Veiculo.objects.filter(status='ATIVO')

    def clean(self):
        cleaned_data = super().clean()
        km_inicial = cleaned_data.get('km_inicial')
        km_final = cleaned_data.get('km_final')
        
        if km_inicial and km_final and km_final < km_inicial:
            raise ValidationError('KM final deve ser maior que KM inicial.')
        
        return cleaned_data


class ManutencaoVeiculoForm(forms.ModelForm):
    class Meta:
        model = ManutencaoVeiculo
        fields = [
            'veiculo', 'tipo_manutencao', 'descricao', 'data_agendamento',
            'data_inicio', 'data_conclusao', 'oficina_prestador', 'telefone_prestador',
            'valor_orcamento', 'valor_final', 'status', 'km_veiculo', 'observacoes'
        ]
        widgets = {
            'veiculo': forms.Select(attrs={'class': 'form-select'}),
            'tipo_manutencao': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'data_agendamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'data_conclusao': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'oficina_prestador': forms.TextInput(attrs={'class': 'form-input'}),
            'telefone_prestador': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(00) 0000-0000'}),
            'valor_orcamento': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
            'valor_final': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'km_veiculo': forms.NumberInput(attrs={'class': 'form-input', 'min': '0'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        data_agendamento = cleaned_data.get('data_agendamento')
        data_inicio = cleaned_data.get('data_inicio')
        data_conclusao = cleaned_data.get('data_conclusao')
        
        if data_inicio and data_agendamento and data_inicio < data_agendamento:
            raise ValidationError('Data de início não pode ser anterior ao agendamento.')
        
        if data_conclusao and data_inicio and data_conclusao < data_inicio:
            raise ValidationError('Data de conclusão deve ser posterior ao início.')
        
        return cleaned_data