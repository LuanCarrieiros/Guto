"""Funções auxiliares para criação de dados nos testes automatizados."""
from datetime import date, time, timedelta

from django.contrib.auth.models import User


def criar_admin(username='admin_teste'):
    return User.objects.create_superuser(username=username, password='senha-forte-123', email='')


def criar_aluno(usuario, nome='Aluno Teste', nascimento=date(2012, 5, 10)):
    from alunos.models import Aluno
    return Aluno.objects.create(nome=nome, data_nascimento=nascimento, sexo='F', usuario_cadastro=usuario)


def criar_funcionario(usuario, nome='Professora Teste', funcao='DOCENTE', matricula='M001'):
    from funcionarios.models import DadosFuncionais, Funcionario
    funcionario = Funcionario.objects.create(
        nome=nome, data_nascimento=date(1985, 3, 2), sexo='F', estado_civil='SOLTEIRO',
        cor_raca='BRANCA', naturalidade='Cidade', uf_nascimento='MG', nome_mae='Mãe',
        endereco='Rua A', numero='1', bairro='Centro', cidade='Cidade', uf='MG',
        usuario_cadastro=usuario,
    )
    DadosFuncionais.objects.create(
        funcionario=funcionario, matricula=matricula, funcao=funcao,
        situacao_funcional='ATIVO', tipo_vinculo='CONCURSADO_EFETIVO',
    )
    return funcionario


def criar_turma(usuario, nome='5º Ano A', periodo=None):
    from turma.models import Turma
    return Turma.objects.create(
        nome=nome, periodo_letivo=periodo or str(date.today().year), tipo_ensino='ENSINO_FUNDAMENTAL_I',
        ano_serie='5_ANO', turno='MATUTINO', usuario_criacao=usuario,
    )


def criar_rota_completa(usuario):
    """Cria motorista, veículo, rota e um ponto de parada."""
    from transporte.models import Motorista, PontoParada, Rota, Veiculo
    motorista = Motorista.objects.create(
        nome='Motorista Teste', cpf='111.222.333-44', data_nascimento=date(1980, 1, 1),
        celular='(31) 99999-0000', endereco='Rua B', cnh_numero='123456', cnh_categoria='D', salario=3000,
        cnh_validade=date.today() + timedelta(days=365), data_inicio_contrato=date(2024, 1, 1),
        usuario_cadastro=usuario,
    )
    veiculo = Veiculo.objects.create(
        placa='ABC1D23', tipo_veiculo='ONIBUS', marca='Marca', modelo='Modelo', ano_fabricacao=2020,
        cor='Amarelo', capacidade_passageiros=40, renavam='12345678901', chassi='9BWZZZ377VT004251',
        usuario_cadastro=usuario,
    )
    rota = Rota.objects.create(
        nome='Rota Centro', turno='MATUTINO', horario_saida_ida=time(6, 30), horario_chegada_ida=time(7, 15),
        horario_saida_volta=time(12, 0), horario_chegada_volta=time(12, 45),
        veiculo=veiculo, motorista=motorista, usuario_cadastro=usuario,
    )
    ponto = PontoParada.objects.create(rota=rota, nome='Praça', endereco='Praça Central', ordem=1,
                                       horario_ida=time(6, 40), horario_volta=time(12, 30))
    return motorista, veiculo, rota, ponto
