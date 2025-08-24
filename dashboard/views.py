from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib.auth.models import User
from .models import AtividadeRecente
from alunos.models import Aluno
from funcionarios.models import Funcionario
import datetime
import locale

@login_required
def home(request):
    """
    View principal do dashboard - mostra resumo geral do sistema
    """
    # Configurar localização para português
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
        except:
            pass  # Usar padrão se não conseguir configurar
    
    # Data atual com dia da semana
    hoje = datetime.date.today()
    dias_semana = {
        0: 'Segunda-feira',
        1: 'Terça-feira', 
        2: 'Quarta-feira',
        3: 'Quinta-feira',
        4: 'Sexta-feira',
        5: 'Sábado',
        6: 'Domingo'
    }
    dia_semana = dias_semana[hoje.weekday()]
    
    # Dados reais do banco de dados
    total_alunos = Aluno.objects.count()
    total_funcionarios = Funcionario.objects.count()
    
    # Buscar atividades recentes reais
    atividades_recentes = AtividadeRecente.objects.select_related('usuario')[:10]
    
    context = {
        'total_alunos': total_alunos,
        'total_funcionarios': total_funcionarios,
        'avaliacoes_pendentes': 23,  # Será implementado quando o módulo avaliação estiver completo
        'transportes_ativos': 12,    # Será implementado quando o módulo transporte for criado
        'escola_nome': 'Sistema GUTO',
        'data_atual': hoje,
        'dia_semana': dia_semana,
        
        # Dados para gráficos (simulados - será implementado com dados reais)
        'alunos_por_serie': [
            {'serie': '1º Ano', 'quantidade': 180},
            {'serie': '2º Ano', 'quantidade': 165},
            {'serie': '3º Ano', 'quantidade': 142},
            {'serie': '4º Ano', 'quantidade': 158},
            {'serie': '5º Ano', 'quantidade': 135},
        ],
        
        # Atividades recentes reais
        'atividades_recentes': atividades_recentes,
    }
    
    return render(request, 'dashboard/home.html', context)

def estatisticas(request):
    """
    View para página de estatísticas detalhadas
    """
    context = {
        'page_title': 'Estatísticas',
    }
    return render(request, 'dashboard/estatisticas.html', context)

def configuracoes(request):
    """
    View para configurações do sistema
    """
    context = {
        'page_title': 'Configurações',
    }
    return render(request, 'dashboard/configuracoes.html', context)


def em_desenvolvimento(request):
    """
    View para páginas em desenvolvimento
    """
    # Obter parâmetros da URL
    funcionalidade = request.GET.get('funcionalidade', '')
    progresso = request.GET.get('progresso', '75')
    
    context = {
        'funcionalidade': funcionalidade,
        'progresso': progresso,
    }
    
    return render(request, 'em_desenvolvimento.html', context)
