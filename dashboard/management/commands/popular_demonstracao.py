"""
Cria dados de demonstração para os módulos complementares (transporte, AEE, itinerários,
programas, calendário e utilitários), aproveitando alunos e funcionários já cadastrados.

Uso: python manage.py popular_demonstracao
O comando é idempotente: pode ser executado várias vezes sem duplicar registros.
"""
from datetime import date, time, timedelta

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from alunos.models import Aluno, Matricula
from funcionarios.models import Funcionario


class Command(BaseCommand):
    help = 'Cria dados de demonstração para os módulos complementares do GUTO.'

    def handle(self, *args, **options):
        usuario = User.objects.filter(is_superuser=True).order_by('pk').first()
        if usuario is None:
            raise CommandError('Crie um superusuário antes (python manage.py createsuperuser).')
        alunos = list(Aluno.objects.filter(tipo_arquivo='CORRENTE').order_by('nome')[:12])
        if len(alunos) < 4:
            raise CommandError('São necessários ao menos 4 alunos cadastrados.')

        with transaction.atomic():
            self.matriculas(usuario, alunos)
            self.transporte(usuario, alunos)
            self.aee(usuario, alunos)
            self.escola(usuario, alunos)
            self.programas(usuario, alunos)
            self.calendario(usuario)
            self.utilitarios(usuario)
            self.professores(usuario)
        self.stdout.write(self.style.SUCCESS('Dados de demonstração criados/atualizados com sucesso.'))

    # ------------------------------------------------------------------
    def matriculas(self, usuario, alunos):
        ano = date.today().year
        for i, aluno in enumerate(alunos):
            Matricula.objects.get_or_create(
                aluno=aluno, ano_administrativo=ano,
                defaults={
                    'tipo_ensino': 'FUNDAMENTAL_I' if i % 2 else 'FUNDAMENTAL_II',
                    'serie_ano': f'{(i % 5) + 1}º ano', 'turno_preferencial': 'MATUTINO',
                    'data_matricula': date(ano, 2, 1), 'condicao_anterior': 'NOVATO',
                    'usuario_cadastro': usuario,
                },
            )

    def transporte(self, usuario, alunos):
        from transporte.models import AlunoTransporte, ManutencaoVeiculo, Motorista, PontoParada, RegistroViagem, Rota, Veiculo
        hoje = date.today()
        motorista, _ = Motorista.objects.get_or_create(cpf='123.456.789-09', defaults={
            'nome': 'José Ribeiro da Silva', 'data_nascimento': date(1978, 4, 12), 'celular': '(31) 98888-1234',
            'endereco': 'Rua das Acácias, 120 - Centro', 'cnh_numero': '04512378901', 'cnh_categoria': 'D',
            'cnh_validade': hoje + timedelta(days=400), 'data_inicio_contrato': date(hoje.year - 2, 2, 1),
            'salario': 3200, 'usuario_cadastro': usuario,
        })
        veiculo, _ = Veiculo.objects.get_or_create(placa='GUT2A25', defaults={
            'tipo_veiculo': 'MICRO_ONIBUS', 'marca': 'Volare', 'modelo': 'W9', 'ano_fabricacao': 2021,
            'cor': 'Amarelo', 'capacidade_passageiros': 28, 'renavam': '01234567890', 'chassi': '9BM384067KB123456',
            'km_atual': 48210, 'proxima_vistoria': hoje + timedelta(days=90), 'usuario_cadastro': usuario,
        })
        rota, _ = Rota.objects.get_or_create(nome='Rota Zona Rural Norte', defaults={
            'turno': 'MATUTINO', 'horario_saida_ida': time(6, 15), 'horario_chegada_ida': time(7, 0),
            'horario_saida_volta': time(11, 45), 'horario_chegada_volta': time(12, 30), 'km_total': 32,
            'veiculo': veiculo, 'motorista': motorista, 'usuario_cadastro': usuario,
        })
        pontos = []
        for ordem, (nome, ida, volta) in enumerate([
            ('Comunidade Boa Vista', time(6, 15), time(12, 30)),
            ('Ponte do Ribeirão', time(6, 30), time(12, 15)),
            ('Escola', time(7, 0), time(11, 45)),
        ], start=1):
            ponto, _ = PontoParada.objects.get_or_create(rota=rota, ordem=ordem, defaults={
                'nome': nome, 'endereco': nome, 'horario_ida': ida, 'horario_volta': volta,
            })
            pontos.append(ponto)
        for aluno in alunos[:4]:
            AlunoTransporte.objects.get_or_create(aluno=aluno, rota=rota, defaults={
                'ponto_embarque': pontos[0], 'ponto_desembarque': pontos[-1], 'responsavel_nome': 'Responsável',
                'responsavel_telefone': '(31) 97777-0000', 'responsavel_endereco': pontos[0].nome,
                'data_inicio': date(hoje.year, 2, 1), 'usuario_cadastro': usuario,
            })
        for dias in range(1, 4):
            dia = hoje - timedelta(days=dias)
            RegistroViagem.objects.get_or_create(rota=rota, data_viagem=dia, tipo_viagem='IDA', defaults={
                'motorista': motorista, 'veiculo': veiculo, 'km_inicial': 48100 + dias * 30,
                'km_final': 48116 + dias * 30, 'alunos_transportados': 4, 'concluida': True, 'usuario_cadastro': usuario,
            })
        ManutencaoVeiculo.objects.get_or_create(veiculo=veiculo, descricao='Troca de óleo e filtros', defaults={
            'tipo_manutencao': 'PREVENTIVA', 'data_agendamento': hoje + timedelta(days=10),
            'oficina_prestador': 'Auto Center Municipal', 'km_veiculo': veiculo.km_atual, 'usuario_cadastro': usuario,
        })

    def aee(self, usuario, alunos):
        from aee.models import EnturmacaoAEE, HistoricoEnturmacao, ProjetoPedagogico, TurmaAEE
        ano = str(date.today().year)
        projeto, _ = ProjetoPedagogico.objects.get_or_create(nome='Sala de Recursos Multifuncionais', periodo_letivo=ano, defaults={
            'tipo_projeto': 'AEE', 'carga_horaria': 10, 'usuario_criacao': usuario,
            'descricao': 'Atendimento educacional especializado no contraturno.',
        })
        turma, _ = TurmaAEE.objects.get_or_create(nome='AEE Tarde', periodo_letivo=ano, defaults={
            'turno': 'VESPERTINO', 'projeto_pedagogico': projeto, 'hora_inicio': time(13, 30), 'hora_fim': time(15, 0),
            'maximo_alunos': 8, 'segunda': True, 'quarta': True, 'local': 'Sala 4', 'usuario_criacao': usuario,
        })
        for aluno in alunos[4:6]:
            _, criada = EnturmacaoAEE.objects.get_or_create(turma=turma, aluno=aluno, ativo=True, defaults={
                'origem': 'PROPRIA_ESCOLA', 'ano_administrativo': ano, 'tipo_ensino': 'Ensino Fundamental',
                'ano_serie': '4º ano', 'usuario_enturmacao': usuario,
            })
            if criada:
                HistoricoEnturmacao.objects.create(turma=turma, aluno=aluno, acao='ADICIONAR', usuario=usuario)

    def escola(self, usuario, alunos):
        from escola.models import AssociacaoItinerarioUnidade, EnturmacaoItinerario, ItinerarioFormativo, UnidadeCurricular
        itinerario, _ = ItinerarioFormativo.objects.get_or_create(nome='Ciência de Dados e Sociedade', defaults={
            'carga_horaria_total': 240, 'areas_conhecimento': 'MATEMATICA', 'vagas_disponiveis': 30,
            'habilidades': 'Análise de dados, pensamento computacional e argumentação com evidências.',
            'usuario_cadastro': usuario,
        })
        for ordem, (nome, carga) in enumerate([('Estatística Aplicada', 80), ('Programação Básica', 80),
                                                ('Projeto Integrador', 80)], start=1):
            unidade, _ = UnidadeCurricular.objects.get_or_create(nome=nome, defaults={
                'carga_horaria': carga, 'ementa': f'Fundamentos de {nome.lower()}.',
                'habilidades_especificas': 'Resolução de problemas.', 'usuario_cadastro': usuario,
            })
            AssociacaoItinerarioUnidade.objects.get_or_create(itinerario=itinerario, unidade=unidade, defaults={'ordem': ordem})
        for aluno in alunos[6:9]:
            EnturmacaoItinerario.objects.get_or_create(aluno=aluno, itinerario=itinerario, defaults={'usuario_enturmacao': usuario})

    def programas(self, usuario, alunos):
        from programa.models import AulaPrograma, ModuloPrograma, ParticipantePrograma, ProgramaPedagogico
        ano = date.today().year
        coordenador = Funcionario.objects.filter(dados_funcionais__funcao='DOCENTE').first()
        programa, _ = ProgramaPedagogico.objects.get_or_create(nome='Reforço de Leitura e Escrita', defaults={
            'descricao': 'Acompanhamento de alunos com dificuldades de alfabetização.', 'tipo_programa': 'REFORCO',
            'status': 'ATIVO', 'data_inicio': date(ano, 3, 1), 'data_fim': date(ano, 11, 30),
            'carga_horaria_total': 60, 'vagas_disponiveis': 15, 'coordenador': coordenador,
            'objetivos_gerais': 'Desenvolver fluência leitora.', 'objetivos_especificos': 'Ler e interpretar textos curtos.',
            'competencias': 'Leitura e escrita.', 'habilidades': 'Decodificação e compreensão.',
            'publico_alvo': 'Alunos do 2º ao 5º ano.', 'usuario_cadastro': usuario,
        })
        modulo, _ = ModuloPrograma.objects.get_or_create(programa=programa, ordem=1, defaults={
            'nome': 'Consciência fonológica', 'descricao': 'Sons, sílabas e palavras.',
            'data_inicio': date(ano, 3, 1), 'data_fim': date(ano, 5, 31), 'carga_horaria': 20,
            'conteudo_programatico': 'Rimas, aliteração e segmentação.', 'metodologia': 'Jogos e leitura compartilhada.',
            'professor_responsavel': coordenador,
        })
        for numero in (1, 2):
            AulaPrograma.objects.get_or_create(modulo=modulo, numero_aula=numero, defaults={
                'titulo': f'Encontro {numero}', 'tipo_aula': 'PRATICA', 'data_planejada': date(ano, 3, numero * 7),
                'horario_inicio': time(14, 0), 'horario_fim': time(15, 30), 'carga_horaria': 1.5,
                'objetivos': 'Praticar leitura.', 'conteudo': 'Textos curtos.', 'metodologia': 'Leitura em grupo.',
                'professor': coordenador, 'usuario_cadastro': usuario,
            })
        for aluno in alunos[9:12]:
            ParticipantePrograma.objects.get_or_create(programa=programa, aluno=aluno, defaults={
                'data_inscricao': date(ano, 2, 20), 'situacao': 'ATIVO', 'usuario_cadastro': usuario,
            })

    def calendario(self, usuario):
        from opcoes.models import CalendarioEscolar, EventoCalendario
        ano = date.today().year
        calendario, _ = CalendarioEscolar.objects.get_or_create(
            periodo_letivo=str(ano), tipo_ensino='FUNDAMENTAL_I', serie='5_ANO', turno='MATUTINO',
            defaults={'data_inicio_letivo': date(ano, 2, 3), 'data_fim_letivo': date(ano, 12, 12),
                      'usuario_criacao': usuario},
        )
        for dia, tipo, nome, letivo in [
            (date(ano, 4, 21), 'FERIADO', 'Tiradentes', False),
            (date(ano, 5, 1), 'FERIADO', 'Dia do Trabalho', False),
            (date(ano, 7, 14), 'RECESSO', 'Início do recesso escolar', False),
            (date(ano, 9, 7), 'FERIADO', 'Independência do Brasil', False),
            (date(ano, 10, 15), 'EVENTO_ESPECIAL', 'Dia do Professor', False),
            (date(ano, 3, 20), 'REUNIAO_PEDAGOGICA', 'Reunião pedagógica', True),
        ]:
            EventoCalendario.objects.get_or_create(calendario=calendario, data_evento=dia, nome_evento=nome,
                                                   defaults={'tipo_evento': tipo, 'dia_letivo': letivo})

    def utilitarios(self, usuario):
        from utilitarios.models import ConfiguracaoSistema, GrupoAcesso, Instituicao, PermissaoGrupo
        for nome, descricao in [('Professor', 'Docentes: diário, turmas e consulta de alunos.'),
                                ('Secretaria', 'Secretaria escolar: cadastros e documentos.')]:
            GrupoAcesso.objects.get_or_create(nome=nome, defaults={'descricao': descricao, 'usuario_criacao': usuario})
            Group.objects.get_or_create(name=nome)
        professor = GrupoAcesso.objects.get(nome='Professor')
        for modulo in ('funcionarios', 'censo'):
            PermissaoGrupo.objects.get_or_create(grupo=professor, modulo=modulo, submenu=None, funcionalidade=None,
                                                 defaults={'visualizar': modulo == 'censo'})
        sme, _ = Instituicao.objects.get_or_create(codigo='SME01', defaults={
            'nome': 'Secretaria Municipal de Educação', 'tipo_instituicao': 'SME'})
        for codigo, nome in [('ESC01', 'Escola Municipal GUTO'), ('ESC02', 'Escola Municipal Vila Nova')]:
            Instituicao.objects.get_or_create(codigo=codigo, defaults={
                'nome': nome, 'tipo_instituicao': 'ESCOLA', 'instituicao_pai': sme})
        for chave, valor, descricao, tipo in [
            ('media_aprovacao', '6', 'Média mínima para aprovação', 'INTEGER'),
            ('frequencia_minima', '75', 'Frequência mínima (%) para aprovação', 'INTEGER'),
            ('nome_escola', 'Escola Municipal GUTO', 'Nome exibido nos documentos', 'STRING'),
        ]:
            ConfiguracaoSistema.objects.get_or_create(chave=chave, defaults={
                'valor': valor, 'descricao': descricao, 'tipo_valor': tipo, 'usuario_atualizacao': usuario})

    def professores(self, usuario):
        """Associa os docentes às disciplinas das turmas (um professor por disciplina em cada turma)."""
        from funcionarios.models import AssociacaoProfessor
        from turma.models import Turma
        docentes = list(Funcionario.objects.filter(dados_funcionais__funcao='DOCENTE', tipo_arquivo='CORRENTE').order_by('nome'))
        if not docentes:
            return
        indice = 0
        for turma in Turma.objects.order_by('nome'):
            for disciplina in turma.get_disciplinas()[:4]:
                if AssociacaoProfessor.objects.vigentes().filter(turma=turma, disciplina=disciplina).exists():
                    continue
                AssociacaoProfessor.objects.create(
                    funcionario=docentes[indice % len(docentes)], turma=turma, disciplina=disciplina,
                    tipo_associacao='DISCIPLINA', data_inicio=date(int(turma.periodo_letivo), 2, 1),
                    usuario_cadastro=usuario,
                )
                indice += 1
