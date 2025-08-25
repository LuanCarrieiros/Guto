from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from alunos.models import Aluno
from datetime import date
import random

class Command(BaseCommand):
    help = 'Popula o banco com 20 alunos fictícios brasileiros'
    
    def handle(self, *args, **options):
        # Pegar ou criar um usuário admin para as associações
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.create_superuser('admin', 'admin@escola.com', 'admin123')
        except:
            admin_user = User.objects.first()
        
        # Lista de 20 nomes únicos e realistas
        todos_nomes = [
            # Masculinos
            'João Pedro Silva Santos', 'Gabriel Costa Oliveira', 'Lucas Ferreira Lima', 
            'Matheus Alves Rodrigues', 'Rafael Santos Gomes', 'Bruno Pereira Martins',
            'Felipe Ribeiro Nascimento', 'Thiago Moreira Carvalho', 'Diego Barbosa Cruz',
            'Arthur Lima Fernandes', 'Enzo Souza Almeida', 'Davi Costa Rocha',
            
            # Femininos  
            'Maria Eduarda Santos Silva', 'Ana Clara Oliveira Costa', 'Beatriz Lima Ferreira',
            'Giovanna Silva Rodrigues', 'Isabela Pereira Santos', 'Júlia Gomes Martins',
            'Larissa Nascimento Ribeiro', 'Manuela Carvalho Santos', 'Nicole Lima Barbosa',
            'Sofia Costa Fernandes', 'Alice Souza Almeida', 'Helena Rocha Silva'
        ]
        
        nomes_maes = [
            'Maria José Silva Santos', 'Ana Paula Oliveira Costa', 'Carmen Souza Lima',
            'Rosana Ferreira Alves', 'Cleide Santos Rodrigues', 'Márcia Pereira Gomes',
            'Sandra Costa Martins', 'Vera Almeida Ribeiro', 'Lúcia Barbosa Nascimento',
            'Regina Carvalho Moreira', 'Simone Santos Cruz', 'Patrícia Lima Oliveira',
            'Cristina Souza Pereira', 'Fernanda Costa Alves', 'Adriana Silva Santos',
            'Mônica Rodrigues Lima', 'Vanessa Gomes Costa', 'Cláudia Martins Silva',
            'Denise Ribeiro Santos', 'Eliane Nascimento Lima'
        ]
        
        nomes_pais = [
            'José Carlos Silva Santos', 'Antonio Oliveira Costa', 'Francisco Souza Lima',
            'Carlos Alberto Ferreira Alves', 'João Batista Santos Rodrigues', 'Paulo César Pereira Gomes',
            'Roberto Costa Martins', 'Luiz Fernando Almeida Ribeiro', 'Marcos Antonio Barbosa Nascimento',
            'Edson Carvalho Moreira', 'Ricardo Santos Cruz', 'Fernando Lima Oliveira',
            'Alexandre Souza Pereira', 'Sergio Costa Alves', 'Rodrigo Silva Santos',
            'Anderson Rodrigues Lima', 'Leonardo Gomes Costa', 'Rafael Martins Silva',
            'Marcelo Ribeiro Santos', 'Gustavo Nascimento Lima'
        ]
        
        # Definir grupos de idade
        grupos_idade = {
            '17-18': 5,
            '15-16': 5, 
            '13-14': 5,
            '13-18': 5  # Idades aleatórias entre 13-18
        }
        
        alunos_criados = []
        contador = 0
        nomes_usados = []  # Para garantir nomes únicos
        
        for grupo, quantidade in grupos_idade.items():
            for i in range(quantidade):
                # Definir idade baseada no grupo
                if grupo == '17-18':
                    idade = random.choice([17, 18])
                elif grupo == '15-16':
                    idade = random.choice([15, 16])
                elif grupo == '13-14':
                    idade = random.choice([13, 14])
                else:  # 13-18
                    idade = random.randint(13, 18)
                
                # Calcular data de nascimento
                ano_nascimento = date.today().year - idade
                mes_nascimento = random.randint(1, 12)
                dia_nascimento = random.randint(1, 28)  # Usar 28 para evitar problemas com fevereiro
                data_nascimento = date(ano_nascimento, mes_nascimento, dia_nascimento)
                
                # Escolher nome único da lista
                nome_disponivel = [n for n in todos_nomes if n not in nomes_usados]
                if nome_disponivel:
                    nome = random.choice(nome_disponivel)
                    nomes_usados.append(nome)
                else:
                    nome = f"Aluno Exemplo {contador + 1}"
                
                # Definir sexo baseado no primeiro nome
                primeiros_nomes_femininos = ['Maria', 'Ana', 'Beatriz', 'Giovanna', 'Isabela', 'Júlia', 'Larissa', 'Manuela', 'Nicole', 'Sofia', 'Alice', 'Helena']
                primeiro_nome = nome.split()[0]
                sexo = 'F' if primeiro_nome in primeiros_nomes_femininos else 'M'
                
                # Escolher pais
                nome_mae = random.choice(nomes_maes)
                nome_pai = random.choice(nomes_pais)
                
                # Flags especiais (baixa probabilidade)
                aluno_gemeo = random.random() < 0.05  # 5% chance
                falta_historico = random.random() < 0.1  # 10% chance
                exclusivo_aee = random.random() < 0.15  # 15% chance
                
                try:
                    aluno = Aluno.objects.create(
                        nome=nome,
                        data_nascimento=data_nascimento,
                        sexo=sexo,
                        nome_mae=nome_mae,
                        nome_pai=nome_pai,
                        aluno_gemeo=aluno_gemeo,
                        falta_historico_escolar=falta_historico,
                        aluno_exclusivo_aee=exclusivo_aee,
                        usuario_cadastro=admin_user
                    )
                    alunos_criados.append(aluno)
                    contador += 1
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Aluno {contador}/20: {nome} ({idade} anos) criado com sucesso')
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Erro ao criar aluno {nome}: {str(e)}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Total: {len(alunos_criados)} alunos criados com sucesso!')
        )
        
        # Mostrar resumo por idade
        self.stdout.write(self.style.WARNING('\n📊 Resumo por faixa etária:'))
        for aluno in alunos_criados:
            idade_atual = date.today().year - aluno.data_nascimento.year
            self.stdout.write(f'• {aluno.nome}: {idade_atual} anos ({aluno.sexo})')